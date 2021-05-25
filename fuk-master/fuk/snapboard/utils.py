import time
import urllib

from django.conf import settings
from django.core.cache import cache
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from django.core.paginator import Paginator

# Subclass paginator so we can pass a post count on init and save an expensive query.

class SBPaginator(Paginator):
    def __init__(self, **kwargs):
        self.object_count = kwargs.pop('object_count', 0)
        Paginator.__init__(self, **kwargs)

    def _get_count(self):
        "Override method to use passed-in value."
        return self.object_count
    count = property(_get_count)

def thread_paginator(request, qs, ct):
    """ Create a threads paginator object for the right page. Takes request, query set and a count. """
        # Make sure page request is an int. If not, deliver first page.
    paginator = Paginator(qs, ct)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
      threads = paginator.page(page)
    except (EmptyPage, InvalidPage):
      threads = paginator.page(paginator.num_pages)
    return threads

# Forms ########################################################################

class RequestFormMixin(object):
    def __init__(self, data=None, files=None, request=None, *args, **kwargs):
        super(RequestFormMixin, self).__init__(data=data, files=files, *args, **kwargs)
        self.request = request
    
class RequestForm(RequestFormMixin, forms.Form):
    pass
    
class RequestModelForm(RequestFormMixin, forms.ModelForm):
    pass  

# Models  ######################################################################

def toggle_boolean_field(obj, field):
    # Toggles and returns a boolean field of a model instance.
    setattr(obj, field, (not getattr(obj, field)))
    obj.save()
    return getattr(obj, field)


# Rendering ####################################################################



def renders(template_name, context):
    return render_to_string(template_name, context)

def JSONResponse(o):
    from snapboard.json import dumps
    return HttpResponse(dumps(o), mimetype='application/javascript')

def json_response(view):
    def wrapper(*args, **kwargs):
        return JSONResponse(view(*args, **kwargs))
    return wrapper

def sanitize(s):
    from templatetags.bbcode import bb2xhtml
    return bb2xhtml(s)


# Caching ######################################################################




# Mail #########################################################################

def bcc_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    from django.core.mail import SMTPConnection, EmailMessage
    # Send mail with recipient_list BCC'ed.
    connection = SMTPConnection(username=auth_user, password=auth_password,
                               fail_silently=fail_silently)
    return EmailMessage(subject, message, from_email, None, recipient_list, 
       connection).send()

       
# Helpers ######################################################################

def safe_int(s, default=None):
    try:
        return int(s)
    except ValueError:
        return default
        
        
def post_offset(postcount, unread, perpage):
  """Get the page to point to for a given unread postcount."""
  pos=postcount-unread
  if pos % perpage > 0: # is there a remainder from read_posts/posts_per_page?
    pg=(pos/perpage)+1
  else:
    pg=pos/perpage
  return pg
    



def SlugifyUniquely(value, model, slugfield="slug"):
        """Returns a slug on a name which is unique within a model's table

        This code suffers a race condition between when a unique
        slug is determined and when the object with that slug is saved.
        It's also not exactly database friendly if there is a high
        likelyhood of common slugs being attempted.

        A good usage pattern for this code would be to add a custom save()
        method to a model with a slug field along the lines of:

                from django.template.defaultfilters import slugify

                def save(self):
                    if not self.id:
                        # replace self.name with your prepopulate_from field
                        self.slug = SlugifyUniquely(self.name, self.__class__)
                super(self.__class__, self).save()

        Original pattern discussed at
        http://www.b-list.org/weblog/2006/11/02/django-tips-auto-populated-fields
        https://code.djangoproject.com/wiki/SlugifyUniquely
        """
        from django.template.defaultfilters import slugify
        suffix = 0
        potential = base = slugify(value)
        while True:
                if suffix:
                        potential = "-".join([base, str(suffix)])
                if not model.objects.filter(**{slugfield: potential}).count():
                        return potential
                # we hit a conflicting slug, so bump the suffix & try again
                suffix += 1

  