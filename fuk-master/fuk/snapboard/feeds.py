from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed


from snapboard.models import Post


class LatestPosts(Feed):
    title = 'fuk.co.uk recent posts'
    link = "/threads"
    description = "The latest posts from the Threads forum at fuk.co.uk."

    title_template = "snapboard/feeds/latest_title.html"
    description_template = "snapboard/feeds/latest_description.html"

    def items(self):
        # select_related_user?
        return Post.objects.filter(thread__private=False).order_by('-date')[:10]
        
    def item_pubdate(self, obj):
        return obj.date
        
    def item_author_name(self, obj):
        return obj.user.username