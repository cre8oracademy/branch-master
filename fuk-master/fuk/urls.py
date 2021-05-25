import os
from django.conf.urls import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from django.views.generic.base import TemplateView, RedirectView

from fprofiles.forms import UserProfileForm
from fukapp.models import ShoppingItem
from fukapp.views import ShoppingListView
admin.autodiscover()
# also need to autodiscover oembed urls
# import oembed
# oembed.autodiscover()


urlpatterns = patterns('',
    # Example:
     url(r'^$', TemplateView.as_view(template_name='index.html'), name='home_page'),
     (r'^about/', TemplateView.as_view(template_name='about.html')),
     (r'^oldsub/', TemplateView.as_view(template_name='oldsub.html')),
     (r'^elite_thanks/', TemplateView.as_view(template_name='elite_thanks.html')),
     (r'^advertise/', TemplateView.as_view(template_name='advertise.html')),
      (r'^privacy/', TemplateView.as_view(template_name='privacy.html')),
      (r'^help/', TemplateView.as_view(template_name='help.html')),
      (r'^elite/', TemplateView.as_view(template_name='elite.html')),
     # (r'^contact/', TemplateView.as_view(template_name='contact.html')),
     (r'^contact/', include('envelope.urls')),
     (r'^threads/', include('snapboard.urls')),
     # Accounts managed by our wrapped version of django-registration
     (r'^accounts/', include('registration_app.urls')),
     # Uncomment this for admin:
     url(r'^admin/', include(admin.site.urls)),
     # anchoring profile stuff at 'profiles', rather than 'user'. Does this matter for redirects from old site? Could implement them in apache.
     (r'^profile/', include('fprofiles.urls')),
     # (r'^avatar/', include('avatar.urls')),
     # (r'^photos/', include('fukphotos.urls')),
     (r'^comments/', include('django.contrib.comments.urls')),
     url(r'^shopping/$', ShoppingListView.as_view(), name='shopping_listing'),
     (r'^competitions/', include('fukapp.urls')), 
     # archive content
     # url(r'node/(?P<nid>[0-9]+)$', 'fukapp.views.view_archive_item', name='archive_item'),
      (r'^pm/', include('fukapp.pm_urls')),
      # subscriptions
      url(r'subs/', include('subscription.urls')),
      # direct link to standard fuk sub
      url(r'^subscribe/$', 'subscription.views.subscription_detail', {'object_id': 1}, name='fuk_subscription'),
      # search
      url(r'^search/results/$', TemplateView.as_view(template_name='gcse-results.html')),

)

# General redirects
# 
urlpatterns += patterns('',
    # redirect old user pages
    (r'^user/(?P<user_id>[0-9]+)$', RedirectView.as_view(url='/profile/%(user_id)s')),
    # fashion feed has gone
    (r'^fashion_feed$', RedirectView.as_view(url=None)),
    # track pages have gone
    (r'^user/.+/track', RedirectView.as_view(url=None)),
    # SEO, baby!
    (r'^node/47742$', RedirectView.as_view(url='/threads/what-to-write-in-the-girlfriends-christmas-card/')),
)

# urls for which we want to skip the lastactivity settings

skip_last_activity_date = [
  r'^admin/.*',
  r'^media/.*',
  r'^static/.*',
]

# # serve media dir in development 
# if settings.DEBUG:
#   urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
