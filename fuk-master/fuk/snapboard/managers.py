from django.db import models
from django.db.models import Q, F
from django.template.defaultfilters import slugify


class ThreadManager(models.Manager):
    def get_user_query_set(self, user):
        """Return a query set with 'private' threads filtered out (filter now applies to staff as well, as moderated
        posts in their own section."""
        qs = self.get_query_set().order_by("-sticky", "-updated").select_related('last_poster')
        return qs.filter(private=False)
        
    def create_thread(self, *args, **kwargs):
        kwargs['slug'] = self.get_slug(kwargs['name'])
        return self.create(**kwargs)
    
    def get_slug(self, slug):
        """Returns a unique slug."""
        get = lambda: self.filter(slug=slug)
        slug = s = slugify(slug)
        if slug == "": # at this point slug could be blank if all illegal chars, give me something to work with.
          slug = "xxx"
        counter = 1
        while get():
            slug = "%s-%s" % (s, counter)
            counter += 1
        return slug
    
    def favorites(self, user):
        """Returns threads watched by user. TODO can't this be done with a related query? Haven't been able to figure it out so far .... :-("""
        
        watch_pks = user.sb_watchlist.values_list("thread_id", flat=True)
        return self.filter(pk__in=watch_pks).order_by("-updated")

    def popular(self):
        """ Returns a list of popular threads. 'Popularity' is currently an admin-defined quality! Does no checks on 
        visibility apart from published status."""
        qs = self.filter(popular=True).exclude(closed=True)
        return qs

 
    def active_threads(self, user):
        """ Return the required number of recently updated threads, with their category details.""" 
        from snapboard.models import Category    
        viewcats=Category.objects.get_user_view_cats(user).values_list("id", flat=True)
        qs = self.get_user_query_set(user).order_by("-updated")
        restricted=qs.filter(Q(category__in=viewcats))
        return restricted
         
    def filter_active_threads(self, excludes=None, includes=None):
        """ Return a list of threads, excluding any category number in the 
        exclusions var, or only returning those in the includes. 
        
        This should be as efficient a query as possible, as it is called
        frequently for the sidebar. Notably, we do not use the individual user id here, but 
        pass categories to include and exclude instead. """
        qs = self.filter(private=False).exclude(closed=True).order_by("-updated")
        if includes is not None:
          # if there are includes, only return those items
          qs = qs.filter(category__in=includes)
        elif excludes is not None:
          qs = qs.exclude(category__in=excludes)
        return qs
          
          
        
          
       
class PostManager(models.Manager):
    
    def moderated(self):
        """Default query set to use, has moderated posts filtered out."""
        return self.get_query_set().filter(status='a')
        
    def get_user_query_set(self, user):
        """Query set for user edits."""
        qs = self.moderated()
        if user.is_staff:
            return qs
        if user.is_authenticated():
            return qs.filter(user=user)
        return qs.none()
        
    def get_recent_by_user(self, user, curruser):
        """ Get the recent posts by a particular user. We pass the current user, and the user whose posts we want to retrieve. """
        posts = self.moderated().order_by('-date').filter(user=user.id).select_related('thread')
        if user != curruser:
          # filter according to viewing users permissions.
          from snapboard.models import Category    
          viewcats=Category.objects.get_user_view_cats(curruser).values_list("id", flat=True)
          filtered = posts.filter(Q(thread__category__in=viewcats))
          return filtered
        return posts
          
          
          

    def create_and_notify(self, thread, user, **kwargs):
        """Using a create method here, rather than a save() override on the model,
        lets us do the various other bits and pieces related to post creation, without
        running in to related field problems."""
        if user.has_perm("snapboard.post_unmoderated"): 
          status = 'a'
        else:
          status = 'p'
        # create a post, with appropriate moderation status.
        post = self.create(thread=thread, user=user, status=status, **kwargs)
        
        # Auto-watch the threads you post in.
        user.sb_watchlist.get_or_create(thread=thread)
        
        
        # # update the thread info if the post is not moderated:
        # if status == 'a':
        #   thread.updated = post.date
        #   thread.post_count=thread.get_post_count()
        #   thread.last_poster = user
        #   thread.save()
        # 
        return post


# class ModeratedPostManager(models.Manager):
#       """Custom manager for posts in all moderation states."""
#       def get_query_set(self):
#           return super(ModeratedPostManager, self).get_query_set()

class CategoryManager(models.Manager):
    def get_query_set(self):
      """ Use ordering by default"""
      return super(CategoryManager, self).get_query_set().order_by('order')
         
    def get_user_view_cats(self, user):
      """A list of categories that the user is allowed to view. 'All' group id is 4.
      TODO: Cache this result, so that users in the same group can re-use. query will be re-executed each time for individual user id."""
      if not user.is_authenticated():
        return self.filter(read_group=4)
      if user.is_staff: # staff can view everything
        return self.get_query_set()
      groups=user.groups.values_list("id", flat=True)
      return self.filter(Q(read_group__in=groups) | Q(read_group__exact=4))

    def get_user_post_cats(self,user):
      """Categories that the user can post in, for the edit thread form. 'All' group id is 4."""      
      if user.is_staff:
         return self
      groups=user.groups.values_list("id", flat=True)
      return self.filter(Q(post_group__in=groups) | Q(post_group__exact=4))