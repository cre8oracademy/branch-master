from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.core.paginator import InvalidPage, EmptyPage, PageNotAnInteger

from fprofiles.models import UserProfile, get_user_info
from snapboard.forms import *
from snapboard.models import *
from snapboard.utils import *
from snapboard.templatetags.sb_tags import process_text

# Ajax #########################################################################

@json_response
def preview(request):
    return {'preview': process_text(request.raw_post_data)}

@staff_member_required
@json_response
def sticky(request):
    thread = get_object_or_404(Thread, pk=request.POST.get("id"))
    if toggle_boolean_field(thread, 'sticky'):
        return {'link':_('Unset sticky'), 'msg':_('This topic is sticky')}
    else:
        return {'link':_('Set sticky'), 'msg':_('This topic is not sticky.')}

@staff_member_required
@json_response
def close(request):
    thread = get_object_or_404(Thread, pk=request.POST.get("id"))
    if toggle_boolean_field(thread, 'closed'):
        return {'link':_('Open thread'), 'msg':_('This topic is closed.')}
    else:
        return {'link':_('Close thread'), 'msg':_('This topic is open.')}

@staff_member_required
@json_response
def private(request):
    thread = get_object_or_404(Thread, pk=request.POST.get("id"))
    if toggle_boolean_field(thread, 'private'):
        return {'link':_('Publish thread'), 'msg':_('This topic has been unpublished.')}
    else:
        return {'link':_('Unpublish thread'), 'msg':_('This topic has been published.')}

@login_required
@json_response
def watch(request):
    thread = get_object_or_404(Thread, pk=request.POST.get("id"))
    try:
        WatchList.objects.get(user=request.user, thread=thread).delete()
        return {
            'link': _('Watch thread'), 
            'msg': _('This topic has been removed from your favorites.')
        }
    except WatchList.DoesNotExist:
        WatchList.objects.create(user=request.user, thread=thread)
        return {
            'link': _('Stop watching'), 
            'msg': _('This topic has been added to your favorites.')
        }

# Ajax post editing, not currently implemented for fuk.co.uk
@login_required
@json_response
def edit(request):
    pk = request.POST.get("id")
    post = get_object_or_404(Post.objects.get_user_query_set(request.user), pk=pk)
    form = PostForm(request.POST, request=request, instance=post)
    if form.is_valid():
        post = form.save()
        return {'preview': sanitize(post.text)}
    return form.errors

# display original post in thread on subsequent pages.
@json_response
def ogpost(request):
  from django.template.loader import render_to_string
  pk=request.POST.get("id")
  thread = get_object_or_404(Thread, pk=pk)
  post = thread.get_first_post()
  # check post is not in moderation.
  if post.status == 'a':
    post.user_info = get_user_info(post.user_id)
    rendered = renders('snapboard/include/post.html', {'post': post})
    return {'post': rendered}
  else:
    return False
  
# fetch a post's content so that it can be displayed as a quote block in the editing form.
@json_response
def quote(request):
  pk=request.POST.get("id")
  post=get_object_or_404(Post, pk=pk)
  s="[quote=%s]%s[/quote]" % (post.user.username, post.text)
  return {'post': s}


# moderation

@json_response
@permission_required('snapboard.moderate_posts')
def moderate(request):
  pk = request.POST.get("id")
  status = request.POST.get("status")
  post = get_object_or_404(Post, pk=pk)
  post.moderate(status, request.user)
  return {'updated': 1}
  

  
  
  
# Views ########################################################################

# TODO: Sticky ordering on pages.
# TODO: Caching of admin / private views
@permission_required('snapboard.post_unmoderated')
def edit_post(request, post_id, template="snapboard/edit_post.html"):
    """ Edit interface for staff and op. Permission check is in get_user_query_set """
    post = get_object_or_404(Post.objects.get_user_query_set(request.user), pk=post_id)
    thread = post.thread
    if post.id == thread.get_first_post().id:
      # it's the first post in the thread, so use ThreadEditForm and pass in the Post object.
      form = ThreadEditForm(request.POST or None, request=request, instance=thread, thepost=post)
      redir = thread.get_url()
    else:
      form = PostForm(request.POST or None, request=request, instance=post)
      redir = post.get_url()
    if request.method == 'POST':
        if form.is_valid():
          post=form.save()
          return HttpResponseRedirect(redir)

    ctx={'form': form}
    return render(request, template, ctx)
    
def category_list(request, template="snapboard/category_list.html"):
    """ Display the category listing page. This is a very high traffic page, so queries are optimised as much as poss. This means a bit 
    more logic and database activity in the view, even though you could just pass the queryset to the template and let all the db lookups
    happen there."""
    categories = Category.objects.get_user_view_cats(request.user)
    catdetails = [x.get_latest_data() for x in categories]
    ctx = {"categories": catdetails}    
    return render(request, template, ctx)

def category(request, slug, template="snapboard/thread_list.html"):
    category = get_object_or_404(Category, slug=slug)
    if not category.can_read(request.user):
      return HttpResponseForbidden("you can't see this, sorry.")
    threads = thread_paginator(request, category.thread_set.get_user_query_set(request.user), 20)
    ctx = {'display_cats': False, 'threads': threads, 'title': category}
    return render(request, template, ctx)
    

def thread_list(request, template="snapboard/thread_list.html"):
    """ The 'latest' view. We add the category to the thread listing entry via display_cats variable."""
    thread_list = Thread.objects.active_threads(request.user)
    threads = thread_paginator(request, thread_list, 25)
    return render(request, template, {'title': 'Latest', 'threads': threads, 'display_cats': True})

def thread_paged(request, tslug, current_page=0, template="snapboard/paged_thread.html"):
    """Return a paged post. Go to oldest unread post if we have been reading this thread."""

    thread = get_object_or_404(Thread.objects.all(), slug=tslug)
    # can this user read this thread?
    if not thread.category.can_read(request.user):
      return HttpResponseForbidden("you can't see this, sorry.")
    if 'page' in request.GET:
      # old style page link, redirect
      try:
        p = int(request.GET.get('page'))
      except ValueError: # not a number
        pass
      else:
        p = p+1 # one-based index for threads
        dest = reverse('sb_paged_thread', kwargs={'tslug': tslug, 'current_page': p})
        return HttpResponsePermanentRedirect(dest) # 301 to correct url
    # captured current page is a string, make it an int.
    current_page=int(current_page)
    if current_page !=0: # we've got a paged url, calculate the base url
       # TODO: shouldn't these be captured as named params in the url conf?
       import re
       regex=re.compile(r'/\d+/$')
       base_url=regex.split(request.path)[0]
    else:
      base_url=request.path[:-1] # lop the trailing slash.
    # is there a new post? process and redirect
    form = PostForm(request.POST or None, request=request)
    if form.is_valid() and request.user.is_authenticated(): 
      post = form.save(thread)
      if post.status == 'p': # post in moderation, let the user know.
        return HttpResponseRedirect(reverse('sb_moderated'))
      return HttpResponseRedirect(post.get_url())
    if thread.private and not request.user.is_staff:
      #TODO might need to check on mod not staff status
      raise Http404
    # can the user post in this thread?
    can_post=False
    if request.user.is_authenticated():
      can_post=thread.category.can_post(request.user)
      thread.update_read(request.user)

    if current_page==0:
      # if we are not going to a specific page, check the user's read history
      # For anons, this will be the default page
      current_page=thread.get_user_page(request.user)
    post_set=thread.post_set.moderated()
    per_page=POSTS_PER_PAGE
    # user our sub-classed Paginator, passing in the thread's post count.
    paginator = SBPaginator(object_list=post_set, per_page=per_page, object_count=thread.post_count)
    try:
      posts = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
      posts = paginator.page(paginator.num_pages)
    # get info for users.
    userinfo = {}
    for post in posts.object_list:
      if not post.user_id in userinfo.keys():
        userinfo[post.user_id] = get_user_info(post.user_id)
      post.user_info = userinfo[post.user_id]
    ctx = {
        'is_fav': thread.is_fav(request.user),
        'posts': posts,
        'paginator': paginator,
        'thread': thread,
        'form': form,
        'category': thread.category,
        'current_page': current_page,
        'base_url': base_url,
        'can_post': can_post,
        'og_post': None,  
    }
    # are we also displaying the original post? Update the context.
    if current_page != 1 and thread.show_og:
      p = thread.get_first_post()
      p.user_info = get_user_info(p.user_id)
      ctx['og_post'] = p  
    return render(request, template, ctx)

def paged_thread_from_post(request, post_id):
    """ A short url to a post. Find the correct paged thread and redirect.
    Calculating paged posts is very db intensive, so we only do it when we 
    actually need to visit the page. """
    post = get_object_or_404(Post.objects.moderated(), pk=post_id)
    return HttpResponseRedirect(post.get_url())




# moderation views

@permission_required('snapboard.moderate_posts')
def moderation_queue(request, status="p", template="snapboard/moderation.html"):
    from snapboard.models import STATUS_CHOICES
    # limit to 20 posts so we don't kill the whole page if
    # there are hundreds.
    posts = Post.objects.filter(status=status)[:20]
    # get info for users. This is copied from main post displays,
    # but should probably be factored out somehow. 
    userinfo = {}
    for post in posts:
      if not post.user_id in userinfo.keys():
        userinfo[post.user_id] = get_user_info(post.user_id)
      post.user_info = userinfo[post.user_id]

    cx = [ch[1] for ch in STATUS_CHOICES if ch[0]==status] #nb returns a list
    if len(cx)==0: # invalid status id
      raise Http404
    ctx = {'status': cx[0], 'posts': posts }
    return render(request, template, ctx)

@login_required
def new_thread(request, slug=None, template="snapboard/new_thread.html"):
    category = None
    if request.POST:
       form = ThreadForm(request.POST, request=request)
       if form.is_valid():
         thread = form.save()
         if not request.user.has_perm('snapboard.post_unmoderated'):
             return HttpResponseRedirect(reverse('sb_moderated'))
         return HttpResponseRedirect(thread.get_url())
    else:
      if slug is not None:
          category = get_object_or_404(Category, slug=slug)
          # modelChoiceField needs an id when passing an initial value.
          # we will check later for valid cats for this user.
          form = ThreadForm(initial={'category': category.id}, request=request)
      else:
          form = ThreadForm(request=request)
    return render(request, template, {"form": form, "category": category})

@login_required
def favorites(request, template="snapboard/thread_list.html"):
    thread_list = Thread.objects.favorites(request.user)
    threads = thread_paginator(request, thread_list, 20)
    title = "Watch list for %s" % request.user.username
    return render(request, template, {'title': title, 'threads': threads, 'display_cats': True})

    
    


