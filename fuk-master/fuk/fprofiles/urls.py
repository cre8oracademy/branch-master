from django.conf.urls import *

"""We are rejigging the profiles urls a bit, as some of them are from profiles app, and some are our own in fprofiles app. Using the same named views as profiles apps to allow redirects that use reverse() to work. For the detail view, we use a user id rather than username in the url, as our legacy user names are not all URL friendly."""

urlpatterns = patterns('',
   url(r'(?P<uid>\d+)/$', 'fprofiles.views.view_profile', name='fprofiles_profile_detail'),
   url(r'edit/$', 'fprofiles.views.edit_profile', name='fprofiles_edit_profile'),
   url(r'change_av/$', 'fprofiles.views.change_av', name='fprofiles_change_av'),
   ) 