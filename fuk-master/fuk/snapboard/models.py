from datetime import datetime, timedelta
import time

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F

from django.contrib.auth.models import User, Group
from snapboard.managers import ThreadManager, PostManager, CategoryManager

#we need the profiles model to check for mailing prefs
from fprofiles.models import UserProfile, N_CHOICES


# note, these 2 need to be hooked in to the django-pagination settings.
THREADS_PER_PAGE = getattr(settings, "SB_THREADS_PER_PAGE", 20)
POSTS_PER_PAGE = getattr(settings, "SB_POSTS_PER_PAGE",20)

NOTIFY = getattr(settings, 'use_notification', False)
MEDIA_PREFIX = getattr(settings, 'SNAP_MEDIA_PREFIX')
READ_TIMEOUT = getattr(settings, "READ_TIMEOUT", 3600 * 24 * 7)
GROUPS_LIST=('All', 'Newbies', 'Basics', 'Elite')


class Category(models.Model):
  """Using django's built-in groups for the category perms, instead of Snapboard's original native system.
   The reason for this is that we want groups to be site wide, not app specific. The groups do not necessarily
   define all the permissions required, we just check for membership - the All group is just a proxy for anon users."""
  
  name = models.CharField(max_length=64, verbose_name='name')
  description = models.CharField(max_length=255, blank=True, verbose_name='description')
  order = models.IntegerField(default=0, help_text="The display order for categories. Lower numbers appear higher up the list.")
  read_group = models.ForeignKey("auth.Group", verbose_name='Read group', related_name='sb_cat_read')
  post_group = models.ForeignKey("auth.Group", verbose_name='Post group', related_name='sb_cat_post')
  new_thread_group= models.ForeignKey("auth.Group", verbose_name='New thread group', related_name='sb_cat_new_thread')
  slug = models.SlugField(unique=True)
  
  def can_read(self, user):
      flag = False
      if self.read_group.name == 'All':
          flag = True
      else:
          #TODO should we be looking up the groups each time, or is there somewhere we could cache/load this info?
          # would be cached in MySQL query cache, so not a huge deal.
          flag = user.is_superuser or (user.is_authenticated() and self.read_group.name in user.groups.values_list('name', flat=True)
          )
      return flag

  def can_post(self, user):
      """Only authenticated users can post, so the 'All' post group excludes anonymous."""
      flag = False
      if user.is_authenticated() and self.post_group.name == 'All':
          flag = True
      else:
          flag = user.is_superuser or (user.is_authenticated() and self.post_group.name in user.groups.values_list('name', flat=True)
      )
      return flag

  def can_create_thread(self, user):
      flag = False
      if user.is_authenticated() and self.post_group.name == 'All':
          flag = True
      else:
          flag = user.is_superuser or (user.is_authenticated() and self.new_thread_group.name in user.groups.values_list('name', flat=True)
      )
      return flag
  
  def topic_count(self):
      return self.thread_set.count()
      
  def last_post(self):
      """ Returns thread object (NOT post object) for most recently updated thread."""
      try:
        lp = self.thread_set.latest('updated')
        return lp
      except Thread.DoesNotExist:
        return None
      
  def get_latest_data(self):
      """ Get the latest data to display on category listing page."""
      data =  {'name': self.name,
              'description': self.description,
              'url': self.get_absolute_url(),
              'count': self.topic_count(),
              }
      lp = self.last_post()
      if lp is not None:
       data['updated']= lp.updated
       data['last_poster'] = lp.last_poster
      return data
      
  objects = CategoryManager()
  class Meta:
      verbose_name = 'category'
      verbose_name_plural = 'categories'
  
  def __unicode__(self):
      return self.name
      
  def get_absolute_url(self):
      return reverse('sb_category', kwargs={'slug': self.slug})
      

class Thread(models.Model):
    user = models.ForeignKey("auth.User", verbose_name='user', null=True,
            on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, verbose_name='subject')
    slug = models.SlugField(max_length=255)
    category = models.ForeignKey('Category', verbose_name='category')
    private = models.BooleanField(default=False, verbose_name='private')
    closed = models.BooleanField(default=False, verbose_name='closed')
    sticky = models.BooleanField(default=False, verbose_name='sticky')
    created = models.DateTimeField(verbose_name='created', editable=False)
    updated = models.DateTimeField(verbose_name='updated', editable=False)
    last_poster = models.ForeignKey('auth.User', verbose_name='last poster', related_name='sb_last_poster', null=True)
    post_count = models.IntegerField(verbose_name='post count', null=True, default=0)
    show_og = models.BooleanField(default=False, verbose_name="show original post", help_text="If checked, the original post will always be visible on multi-page threads.")
    popular = models.BooleanField(default=False, help_text="Add to the popular threads curated list.")
    
    objects = ThreadManager()
    
    class Meta:
        verbose_name = 'thread'
        verbose_name_plural = 'threads'
    
    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.id is None:
            self.created = self.updated = datetime.now()
        return super(Thread, self).save(force_insert, force_update, *args, **kwargs)
    
    def is_fav(self, user):
        # True if user is watching this thread.
        return user.is_authenticated() and self.watchlist_set.filter(user=user).count() != 0

    def get_notify_recipients(self, postnotify='i'):
        # Returns a set of emails watching this thread, either immediate (i) or digest (d) from profile prefs
        mail_dict = dict(self.watchlist_set.values_list("user__id", "user__email"))
        
        dont_mail_pks = UserProfile.objects.filter(user__id__in=mail_dict.keys()).exclude(postnotify=postnotify)
        dont_mail_pks = dont_mail_pks.values_list("user__id", flat=True)
        for pk in dont_mail_pks:
            mail_dict.pop(pk)
        
        #recipients = set(mail_dict.values())
        return mail_dict
    
    def get_post_count(self):
        """ Get the number of available posts by querying the db. This number is also stored on the thread when changes are made to posts (creation, moderation etc)"""
        return self.post_set.moderated().count()
        
    def update_post_count(self):
        """ Update the stored post count on the thread object."""
        self.post_count = self.get_post_count()
        self.save()
        
    def thread_unread_count(self, user):
        """If we have read this thread, then find the number of new posts. If we've never read it, or it was longer ago
        than READ_TIMEOUT, """
        now=datetime.today()
        t=Read.objects.filter(thread=self.id, user=user)
        if t: # we have viewed this thread
          stamp=t[0].time
        else:
          stamp=now-timedelta(seconds=READ_TIMEOUT)
        return self.post_set.moderated().filter(date__gt=stamp).count()
    
    def get_last_post(self): 
        return self.post_set.moderated().order_by('-date')[0]

    def get_first_post(self):
        """ Get the first post of the thread, may be in moderated
        status""" 
        return self.post_set.order_by('date')[0]
        
        
    def update_read(self, user):
        read, new = Read.objects.get_or_create(user=user, thread=self)
        if not new:
            read.time = datetime.now()
            read.save()
   
    def get_url(self):
        return reverse('sb_thread', args=(self.slug,))
    get_absolute_url = get_url
    
    def get_paged_url(self, user):
      """get a correctly paged url for this thread, based on the user's read history."""
      pg=self.get_user_page(user)
      if pg==0:
        return self.get_absolute_url()
      else:
        return reverse('sb_paged_thread', args=(self.slug, pg))
      
    def get_user_page(self, user):
      """ Get the current page in the thread based on the user's unread history. Otherwise return the last page.""" 
      ct=self.post_count
      if ct % POSTS_PER_PAGE > 0:
        last=(ct/POSTS_PER_PAGE)+1
      else:
        last=ct/POSTS_PER_PAGE
      if not user.is_authenticated():
        return last
      # see if we've got any unreads for this thread
      un=self.thread_unread_count(user)
      if un==0:
        # no unreads, return the default - (possibly modify if there is eg less than 5 pages, go to first page?)
        return last
      pos=ct-un # subtract unreads from total posts
      if pos % POSTS_PER_PAGE > 0: # is there a remainder from read_posts/posts_per_page?
        pg=(pos/POSTS_PER_PAGE)+1
      else:
        pg=pos/POSTS_PER_PAGE
      return pg
      
    def update_active_threads_list(self):
      """ Update the active threads list in the cache. all_threads is the list for all users, elite_threads contains
      threads posted in the elite forum(s). Threads are stored as 3 item tuples with id, title, url."""
      ct = getattr(settings, "ACTIVE_THREAD_COUNT", 20)
      all_threads = cache.get('active_threads', [])
      elite_threads = cache.get('active_threads_elite', [])
      # reorder the thread list and trim if needed
      def rejig(item, l):
        if item in l:
          l.remove(item)
        l.insert(0, item)
        if len(l) > ct:
          return l[0:ct]
        return l
      if self.category.read_group == 'All':
        all_threads = rejig(self.id, all_threads)
      elite_threads = rejig(self.id, elite_threads)
      # cached for 24 hours for safety, but will be updated more frequently.
      cache.set('active_threads', all_threads, 3600 * 24)
      cache.set('active_threads_elite', elite_threads, 3600 * 24)
      cache.set('thread-%d' % self.id, (self.id, self.name, self.get_absolute_url()), 3600 * 24)

STATUS_CHOICES = (
      ('a', 'Approved'),
      ('p', 'Pending'),
      ('r', 'Rejected'),
      )
class Post(models.Model):
    """ The basic post object."""
    user = models.ForeignKey("auth.User", verbose_name='user', null=True,
            on_delete=models.SET_NULL)
    thread = models.ForeignKey('Thread', verbose_name='thread')
    text = models.TextField(verbose_name='text')
    # private = models.BooleanField(default=False, verbose_name='private')
    status = models.CharField(verbose_name='status', max_length=1, choices=STATUS_CHOICES, default='a', db_index=True)
    date = models.DateTimeField(verbose_name='date', null=True, db_index=True)
    edited = models.DateTimeField(verbose_name='edited', null=True)
    ip = models.IPAddressField(verbose_name='ip address', blank=True, null=True)
    
    objects = PostManager()
    
    
    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        permissions = (
          ("post_unmoderated", "Can post unmoderated",),
          ("moderate_posts", "Can moderate posts",),
        )
        ordering = ['date']
    
    def __unicode__(self):
        # return the first x characters of the post.
        return self.text[0:40]
    

    def moderate(self, status, moduser):
        """Moderate a post, updating the post status, and the thread status if applicable. If called
        from a request, send the user along (may be called externally eg managemnent command instead)."""
        oldstatus = self.status
        if status != oldstatus: #someone else may have modded this one while we were looking at it.
          self.status = status
          self.save(tstamp=False)
          thread=self.thread
          if self.id == thread.get_first_post().id:
              # update thread status if it is the first post in a new thread
              if thread.private and status=='a':
                  thread.private = False
                  thread.save()
          # update the users moderation count, will change their group status if they are eligible.
          # TODO update last poster value on thread if it hasn't been updated since
          up = self.user.get_profile()
          up.change_mod_posts(status)
          m = Moderation(mod=moduser, oldstatus=oldstatus, newstatus=status, post=self, author=self.user)
          m.save()




        
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """ Save method. Pass tstamp=false to prevent 'edited' attr being updated with current time. (for instance, in moderation actions)"""
        tstamp = kwargs.pop('tstamp', True)
        if tstamp:
            # existing post has been edited
            self.edited = datetime.now()
        thread = self.thread
        if self.id is None:
            # it's a new post, increment user's post count, add last poster info to thread
            # unmoderated posts will still increment user post count, which can be decremented if post rejected by mod
            self.date = self.edited
            pc = self.user.get_profile()
            pc.postcount += 1
            pc.save()
            if self.status == 'a': #post was not moderated, so update the thread time
              thread.updated = self.date
              thread.last_poster = self.user
        super(Post, self).save(force_insert, force_update, *args, **kwargs)
        # delete post from cache
        cache.delete('post-'+str(self.id))
        # update active_thread list if post is not in moderation
        if self.status == 'a':
          thread.update_active_threads_list()
        thread.update_post_count()
        thread.save()
        
        
    def get_url(self):
        """ Work out a page and fragment for this thread. TODO would this be quicker doing an SQL count?"""
        posts = list(self.thread.post_set.values_list("pk", flat=True))
        total = len(posts)
        preceding_count = posts.index(self.pk)
        page=0
        query = "#post%i" % self.pk
        if total > POSTS_PER_PAGE:
            page = preceding_count // POSTS_PER_PAGE + 1
            # query = "?page=%s%s" % (page, query)
        
        if page:
            path = reverse('sb_paged_thread', args=[self.thread.slug, page])
        else:
            path = reverse('sb_thread', args=[self.thread.slug])
        next = "%s%s" % (path, query)
        return next
    get_absolute_url = get_url
    
    

class Read(models.Model):
    """
    For each topic that user has entered the time 
    is logged to this model.
    
    Borrowed from pyBB.
    """

    user = models.ForeignKey("auth.User", verbose_name='User')
    thread = models.ForeignKey(Thread, verbose_name='Thread')
    time = models.DateTimeField('Time', blank=True)

    class Meta:
        unique_together = [('user', 'thread')]
        verbose_name = 'Read'
        verbose_name_plural = 'Reads'

    def save(self, *args, **kwargs):
        if self.time is None:
            self.time = datetime.now()
        super(Read, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'T[%d], U[%d]: %s' % (self.thread.id, self.user.id, unicode(self.time))



# Fav
class WatchList(models.Model):
    user = models.ForeignKey("auth.User", verbose_name='user', related_name='sb_watchlist')
    thread = models.ForeignKey(Thread, verbose_name='thread')


# A run of the notification system

class NotifyRun(models.Model):
    starttime=models.DateTimeField()
    elapsed=models.IntegerField()
    threadcount=models.IntegerField()
    usercount=models.IntegerField()
    notifytype=models.CharField(max_length=1, choices=N_CHOICES)
    class Meta:
        get_latest_by = 'starttime'



# moderation

class Moderation(models.Model):
    """Moderation objects record status changes in posts."""
    mod = models.ForeignKey("auth.User", verbose_name='Moderator', related_name='sb_moderator')
    oldstatus = models.CharField(verbose_name='Old status', max_length=1, choices=STATUS_CHOICES)
    newstatus = models.CharField(verbose_name='New status', max_length=1, choices=STATUS_CHOICES)
    author = models.ForeignKey("auth.User", related_name='sb_mod_author')
    post = models.ForeignKey('Post', related_name='sb_mod_post')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    



