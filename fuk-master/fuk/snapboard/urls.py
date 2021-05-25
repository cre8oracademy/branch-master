from django.conf.urls import *
#from snapboard.feeds import LatestPosts
from django.conf import settings
from snapboard.forms import PostForm
from django.views.generic import TemplateView

# Previous feed support removed, not sure anyone uses the category
# feeds, and we might do something better with Twitter instead.
# feeds = {
#     'latest': LatestPosts
# }
# 
# urlpatterns = patterns('django.contrib.syndication.views',
#     (r'^feeds/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}, 'sb_feeds'),
# )

urlpatterns = patterns('snapboard.views',
    # Forum
    (r'^new/$', 'new_thread', {}, 'sb_new_thread_nocat'),
    (r'^post/(?P<post_id>\d+)/$', 'paged_thread_from_post', {}, 'sb_paged_thread_from_post'), 
    url(r'^post/moderated', TemplateView.as_view(template_name='snapboard/post_moderated.html'), name='sb_moderated'),
    (r'^(?P<slug>[-_\w]+)/new/$', 'new_thread', {}, 'sb_new_thread'),
    (r'^$', 'category_list', {}, 'sb_category_list'),
    (r'^latest/$', 'thread_list', {}, 'sb_thread_list'),
    # (r'^search/$', 'search', {}, 'sb_search'),
    (r'^watching/$', 'favorites', {}, 'sb_favorites'),
    (r'^post/edit/(?P<post_id>\d+)/', 'edit_post', {}, 'sb_edit_post'),
    (r'^moderation/(?P<status>\w)/', 'moderation_queue', {}, 'sb_moderation_queue'),

    # Ajax
    (r'^rpc/edit/$', 'edit', {}, 'sb_edit'),
    (r'^rpc/preview/$', 'preview', {}, 'sb_preview'),
    (r'^rpc/sticky/$', 'sticky', {}, 'sb_sticky'),
    (r'^rpc/close/$', 'close', {}, 'sb_close'),
    (r'^rpc/watch/$', 'watch', {}, 'sb_watch'),
    (r'^rpc/private/$', 'private', {}, 'sb_private'),
    (r'^rpc/ogpost/$', 'ogpost', {}, 'sb_ogpost'),
    (r'^rpc/quote/$', 'quote', {}, 'sb_quote'),
    (r'^rpc/moderate', 'moderate', {}, 'sb_moderate'),

    
    # Categories / Threads
    (r'^forums/(?P<slug>[-_\w]+)/$', 'category', {}, 'sb_category'),
    (r'^(?P<tslug>[-_\w]+)/$', 'thread_paged', {}, 'sb_thread'),
    (r'^(?P<tslug>[-_\w]+)/(?P<current_page>\d+)/$', 'thread_paged', {}, 'sb_paged_thread'),
   
)
