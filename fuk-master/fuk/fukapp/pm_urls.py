# wrapper url conf for private message system. We mostly use the userena.umessages views directly, but
# for those that require a username in the url, we wrap it so we can use the user id instead (because of our legacy usernames)

from django.conf.urls import *
from userena.contrib.umessages import views as messages_views
from fukapp.pm_views import pm_message_compose, PmMessageDetailListView
from fukapp.views import autocomplete_user
from fukapp.forms import PmComposeForm
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^compose/$',
        pm_message_compose,
        {'compose_form': PmComposeForm},
        name='userena_umessages_compose'),

    url(r'^compose/(?P<recipients>[\+\d]+)/$',
        pm_message_compose,
        name='userena_umessages_compose_to'),

    url(r'^reply/(?P<parent_id>[\d]+)/$',
        messages_views.message_compose,
        name='userena_umessages_reply'),

    url(r'^view/(?P<user_id>[\d]+)/(?P<page>[\d]+)?$',
        PmMessageDetailListView.as_view(),
        name='userena_umessages_detail'),

    url(r'^remove/$',
        messages_views.message_remove,
        name='userena_umessages_remove'),

    url(r'^unremove/$',
        messages_views.message_remove,
        {'undo': True},
        name='userena_umessages_unremove'),

    url(r'^(?P<page>[\d]+)?$',
    login_required(messages_views.MessageListView.as_view()),
    name='userena_umessages_list'),
        
    url(r'usercomplete.json', 
        autocomplete_user,
        name='userena_user_autocomplete'),
)
