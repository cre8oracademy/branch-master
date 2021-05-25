# -*- coding: utf-8 -*-
import os
import re
from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.importlib import import_module

# from snapboard.templatetags import bbcode
from snapboard.unread import cache_unreads
from snapboard.models import Thread, Read, Post, Category
from micawber.parsers import parse_html

from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.template.defaultfilters import urlize
from django.core.cache import cache
from django.core.urlresolvers import reverse
from fukapp.models import affiliate_replace
from fprofiles.models import get_avatar, get_user_info


from datetime import datetime, timedelta

bad_words_list = []
# https://github.com/ReconCubed/django-profanity-filter/blob/master/wordlist.txt
bad_words_file = os.path.normpath(
  os.path.join(settings.SITE_ROOT, '../badwords.txt'))

if os.path.exists(bad_words_file):
    with open(bad_words_file, 'r') as f:
        bad_words_list = [line.strip() for line in f.readlines()]


LATEST_POSTS = getattr(settings, "SB_LATEST_POSTS", 6)

register = template.Library()

# some oembed bits we have imported from mcdjango
def _load_from_module(path):
    package, attr = path.rsplit('.', 1)
    module = import_module(package)
    return getattr(module, attr)


PROVIDERS = getattr(settings, 'MICAWBER_PROVIDERS', 'micawber.contrib.mcdjango.providers.bootstrap_basic')

providers = _load_from_module(PROVIDERS)
if callable(providers):
    providers = providers()

def fuk_inline_handler(url, response_data, **params):
  """ Deal with missing title errors in default micawber setup """
  if not 'title' in response_data:
    response_data['title']=''
  return '<a href="%(url)s" title="%(title)s">%(title)s</a>' % response_data

def fuk_full_handler(url, response_data, **params):
    # sometimes, we get a broken but still valid
    # embed response, in which case just make it a
    # normal URL link.
    if not 'type' in response_data:
        response_data['type'] = 'link'
        response_data['title'] = url
    if not 'title' in response_data:
      response_data['title']=''
    if response_data['type'] == 'link':
        return '<a href="%(url)s" title="%(title)s">%(title)s</a>' % response_data
    elif response_data['type'] == 'photo':
        return '<a href="%(url)s" title="%(title)s"><img alt="%(title)s" src="%(url)s" /></a>' % response_data
    else:
        return response_data['html']

@register.filter
def truncate(text, chars=200):
  if len(text) < chars:
    return text
  try:
    last_space = text.rindex(' ', 0, chars)
    if last_space < chars // 5:
      raise ValueError
  except ValueError:
    return text[:chars - 1] + u'…'
  else:
    return text[:last_space] + u'…'

# def markdown(value, arg=''):
#     import markdown
#     return markdown.markdown(value, safe_mode=False)
# register.filter('markdown', markdown)

# def bbcode_filter(value, arg=''):
#     # value=urlize(value)
#     return bbcode.bb2xhtml(value, True)
# register.filter('bbcode', bbcode_filter)

# the main post filter. Return post if in cache, if not run it through the processor and cache it.
@register.filter
def postfilter(text, post_id, autoescape=None):
  key = "post-%d" % post_id
  cached_post = cache.get(key)
  if cached_post:
    return cached_post
  post_text =  process_text(text)
  cache.set(key, post_text)
  return post_text
postfilter.needs_autoescape=True


def process_text(text):
  from fukapp import bbcoder
  # from fukapp import postmarkup
  post_text = text
  # are there any old youtube embeds? replace them with the plain url link.
  # An expensive operation, so check if there is an embed first.
  if post_text.find('<object') > -1:
    post_text = replace_youtube_embed(post_text)
  # Once we have manually replaced any HTML tags, we need to blitz
  # the rest.
  post_text = strip_tags(post_text)
  # Then run the post through postmarkup. This is to do legacy bbcode conversions, 
  # and to maintain capability for quoting posts. It is really important that 
  # postmarkup does not linkify anything, or wrap stuff in paragraphs, as these
  # mess up oembed.
  # post_text = postmarkup.render_bbcode(post_text, paragraphs=False, auto_urls=False)
  post_text = bbcoder.fukparser.format(post_text)
  # Next, run the oembed parser. This can activate all links, whether oembedded or not.
  post_text = parse_html(post_text, providers, "600x600", block_handler=fuk_inline_handler, handler=fuk_full_handler)  
  # run the affiliate link replacements
  post_text = affiliate_replace(post_text)
  # convert smilies to their image equivalents.
  post_text = gen_smileys(post_text, 'html')
  return mark_safe(post_text)

@register.filter
def gen_smileys(text, format="html"):
  """ Dropin replacement for django-smileys function, but 
  uses more sane caching and image building."""
  smileys = cache.get('stored_smileys')
  if not smileys:
   from fukapp.utils import cache_smileys
   smileys = cache_smileys()
  for s in smileys:
    if s.is_regex:
      # test that the regex will compile, don't want template errors
      try:
        patt=re.compile(s.pattern)
        text = patt.sub(s.img, text)
      except:
        # if it's an invalid regex, just leave the string
        pass
    else:
      text = text.replace(s.pattern, s.img)
  return text
  
@register.simple_tag  
def list_smileys():
    """Create a json list of smileys, to be used in a post editing form."""
    from django.utils import simplejson as json
    smileys = cache.get('stored_smileys')
    if not smileys:
      from fukapp.utils import cache_smileys
      smileys = cache_smileys()
    slist = [{'img':k.image.url, 'title':k.description, 'alt':k.default} for k in smileys]
    return json.dumps(slist)
    
  
def replace_youtube_embed(t):
  """ Use BeautifulSoup to replace old YouTube and Sound Cloud embeds"""
  try:
    from BeautifulSoup import BeautifulSoup as bs
  except ImportError: 
    return t
  from urlparse import urlparse
  soup = bs(t)
  # print soup.prettify()
  yts = soup.findAll('object')
  for y in yts:
    mv = y.find('param', attrs={'name': 'movie'})
    if mv:
      if mv['value'].find('youtube') > -1:
        o = urlparse(mv['value'])
        # youtube paths are in the format '/v/dkjrnb3', so strip out the leading /v/
        y.replaceWith("http://www.youtube.com/watch?v=" + o.path[3:])
      elif mv['value'].find('soundcloud.com') > -1:
        y.replaceWith("") #replace the embed with nothing.
        spans = soup('span') # get the href from the span
        for s in spans:
          if s.find('a') and 'href' in s.find('a'):
            # sometimes we have an <a> with no href
            k = s.find('a')['href']
            # allow for missing parent node http://stackoverflow.com/a/3461905
            if s.parent is not None:
                s.replaceWith(k) # replace whole span with just url

  return unicode(soup)



# private messages are not cached, so have their own filter. Separated out so that we can have different
# processors on posts and PMs.
@register.filter
def pmfilter(text):
  return process_text(text)
  

  
@register.filter
def dateisoformat(dt):
    return hasattr(dt, "isoformat") and dt.isoformat() or ""
    
    
@register.filter
def timeago(dt):
    if not hasattr(dt, "strftime"):
      return ""
    d1=dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    d2=dt.strftime("%a, %d %b %Y %H:%M")
    
    return mark_safe('<abbr class="timeago" title="%s">%s</abbr>' % (d1, d2))


# Paged url template tag. Adds paging according to user's unread thread setting.

@register.simple_tag
def paged_url(thread, user):
    if has_unreads(thread, user):
       return thread.get_paged_url(user)
    else:
       return thread.get_absolute_url()


@register.simple_tag
def active_threads(user, trunc=40, ct=20):
    """ Get the active threads, according to user privileges.

    This is the new version of the sidebar, which excludes the classifieds, 
    now in their own area.

    For better efficiency on this query, we now specify the categories to 
    exclude or include as numbers. This means that any change to privileged
    forum accesses (ie a new elite forum) must be accounted for here in the 
    access control switching.

    Formatting moved in to a separate function format_thread_list().

    """
    elite_cat = 4
    classified_cat = 3
    excludes = [classified_cat]
    if user.is_anonymous():
        excludes.append(elite_cat)
    else:
        info = get_user_info(user)
        if not info['is_elite']:
            excludes.append(elite_cat)
    threads = Thread.objects.filter_active_threads(excludes=excludes)[:ct]
    return format_thread_list(threads, trunc)


@register.simple_tag
def active_classifieds(trunc=40, ct=20):
    """ Get the latest classifeds threads """    
    threads = Thread.objects.filter_active_threads(includes=[3])[:ct]
    return format_thread_list(threads, trunc)


@register.simple_tag
def popular_threads(trunc=40, ct=20):
    """ Get the popular threads list"""
    op = ''
    tlist = [(a.id, a.name, a.get_absolute_url()) for a in Thread.objects.popular()[:ct]]
    for t in tlist:
      title = t[1]
      if len(title) > trunc:
        title = title[0:trunc] + "..."
      op += '<li><a href="%s">%s</a></li>' % (t[2], title)
    return op
    

def format_thread_list(threads, trunc=40):
    """Format a list of threads for the right sidebar"""
    op = ''
    tlist = [(a.id, a.name, a.get_absolute_url()) for a in threads]
    for t in tlist:
      title = t[1]
      if len(title) > trunc:
        title = title[0:trunc] + "..."
      op += '<li><a href="%s">%s</a></li>' % (t[2], title)
    return op


@register.simple_tag
def users_online(online_now_ids, online_now_users):
    """ Using the online now info created from our middelware, this tag
    returns a formatted list of links to users profile page"""
    l = []
    for uid in online_now_ids:
      if uid in online_now_users:
        link = reverse('fprofiles_profile_detail', args=[uid])
        l.append('<a href="%s">%s</a>' % (link, online_now_users[uid]))
    return ', '.join(l)


# get the current moderation queue count, to display in a moderator's user block
@register.simple_tag
def moderation_count():
    ct = Post.objects.filter(status='p').count()
    if ct:
      return '(%d)' % ct
    else:
      return ''


@register.simple_tag
def category_links(user):
    s = ""
    cats = Category.objects.get_user_view_cats(user)
    for cat in cats:
      s += '<li><a href="%s">%s</a></li>' % (cat.get_absolute_url(), cat.name)
    return s

# Unreads code. Borrowed from djangoBB/pyBB
# When displaying a list of topics, we first filter the topics through forum_unreads(). This
# checks for reads and adds a _read attribute


@register.filter
def forum_unreads(qs, user):
    return cache_unreads(qs, user)


@register.filter
def has_unreads(thread, user):
    """
    Check if thread has unread posts for this user. Should have been added by cache_unreads(), do a lookup if it hasn't.
    """
    now = datetime.now()
    delta = timedelta(seconds=settings.READ_TIMEOUT)
    if not user.is_authenticated():
        return False
    else:
        if isinstance(thread, Thread):
            if (now - delta > thread.updated):
                return False
            else:
                if hasattr(thread, '_read'):
                    read = thread._read
                else:
                    try:
                        read = Read.objects.get(user=user, thread=thread)
                    except Read.DoesNotExist:
                        read = None

                if read is None:
                    return True
                else:
                    return thread.updated > read.time
        else:
            raise Exception('Object should be a thread')


def avatar(user, size='standard'):
    """ Calls the get_avatar function in fpofiles to get an avatar SRC"""
    avpath = get_avatar(user, size)
    return """<img src="%s" alt="%s avatar" class="avatar">""" % (avpath, user)

register.simple_tag(avatar)

def profile_link(user):
    """ Return a link to the user's profile page, or not if they have been 
    deleted or blocked. """
    # deleted user, return word [deleted]
    if user == 0:
        return "[deleted]" 
    info = get_user_info(user)
    if not info:
        return "[deleted]"
    # active user, return profile link
    if info['active']:
        return '<a href="%s">%s</a>' % (info['profile_link'], info['name'])
    # blocked user, return name only
    return info['name']
    
register.simple_tag(profile_link)

# Copyright 2009, EveryBlock
# This code is released under the GPL.
@register.tag
def raw(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = 'endraw'
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)


@register.filter
def profanity_filter(value):
    """
    Ugly but quick way to do it for now
    """
    for word in bad_words_list:
        word = r'\b%s\b' % word  # Apply word boundaries to the bad word
        regex = re.compile(word, re.IGNORECASE)
        value = regex.sub('*' * (len(word) - 4), value)
    return value
profanity_filter.is_safe = True
