import logging
import sys
from django.db import models
# from imagekit.models import ImageSpec
# from imagekit.processors import resize, Adjust
# from easy_thumbnails.fields import ThumbnailerImageField

from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.utils import safestring
from easy_thumbnails.files import get_thumbnailer

def profile_handler(sender, **kwargs):
  """create a profile record for new users. Listen to the post_save signal from User create.
  Reset user info if this is a save on an existing user."""
  if kwargs['created']:
      u = UserProfile(user=kwargs['instance'])
      u.save()
  else:
      u = kwargs['instance']
      ckey = 'uinfo-%d' % u.id
      cache.delete(ckey)


post_save.connect(profile_handler, sender=User)

logger = logging.getLogger('fukapp.models')

# site-wide profile model

# Post notification preferences
N_CHOICES = (
 ('i', 'Immediately'),
 ('d', 'Daily'),
 ('n', 'Never'),
)
# message notification preferences, the same for now.
M_CHOICES = N_CHOICES

# moderated post threshold - once you have reached this we upgrade your account
M_THRESHOLD = settings.MODERATED_POST_COUNT

# groups settings
POSTGROUPS = {"Basics": 1, "Elite": 2, "Newbies": 3}


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name='user', related_name='userprofile')
    location = models.CharField(verbose_name='location', max_length=128, null=True, blank=True, help_text="Where are you?")
    website = models.CharField(verbose_name='website', max_length=128, null=True, blank=True, help_text="Blog, Facebook profile or whatever public web presence you have.")
    twitter = models.CharField(verbose_name='twitter', max_length=128, null=True, blank=True, help_text="On Twitter? Stick your username in here.")
    postnotify = models.CharField(verbose_name='post notification', max_length=1, choices=N_CHOICES, default='d', help_text="When shall we email you about new posts in threads you are watching?")
    messagenotify = models.CharField(verbose_name='message notification', max_length=1, choices=M_CHOICES, default='d', help_text="When shall we email you about new private messages?")
    postcount = models.IntegerField(verbose_name='post count', default=0)
    lastactive = models.DateTimeField(verbose_name='last activity', null=True, db_index=True)
    moderated_posts = models.IntegerField(verbose_name='moderated_posts', default=0)

    def joined(self):
      return self.user.date_joined

    def badge(self, elite=False):
      """ Return the correct badge for this user. Staff or Mod if they are one, then GJ or nothing.
      Can pass in the 'is_elite' property if it's already available."""
      imgref = ''
      if self.user.is_staff:
        imgref = 'admin_av.gif'
      elif self.user.has_perm("snapboard.moderate_posts"):
        imgref = "mod_av.gif"
      elif elite or self.is_elite():
        imgref = "jimmy_av.gif"
      if imgref:
        return safestring.mark_safe('<img src="%sbank/%s">' % (settings.STATIC_URL, imgref))
      else:
        return ''

    def is_elite(self):
      """ Is this user in the elite group"""
      groups = self.user.groups.values_list("id", flat=True)
      if 2 in groups:
        return True
      else:
        return False

    def get_absolute_url(self):
          return ('profiles_profile_detail', (), {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)

    def change_mod_posts(self, status):
        if status == 'a':
            mps = self.moderated_posts + 1
            if mps >= M_THRESHOLD:
                # if we've passed the mod threshold, add us to the basics group
                basics = Group.objects.get(pk=1)
                if not basics in self.user.groups.all():
                    self.user.groups.add(basics)
            self.moderated_posts = mps
            self.save()
        return

    def __unicode__(self):
      return self.user.username


def get_user_info(user, updatecache=False):
      """ Takes a user object or user id.
      Returns a dict with a full set of user info. Avoids hitting db if possible.
      Check cache and update if not available
      The dict contains: username, is_elite, badge, avatar, joined, postcount, profile_link, blocked
      Call with updatecache if we know something has changed."""
      allinfo = {}
      u = None
      if hasattr(user, 'username'):
        u = user
        uid = user.id
      else:
        uid = user
      ckey = 'uinfo-%d' % uid
      if not updatecache:
          allinfo = cache.get(ckey)
      if allinfo:
          return allinfo
      else:
          if not u:
            try:
                u = User.objects.get(pk=uid)
            except User.DoesNotExist:
                return {}
          p = u.get_profile()
          e = p.is_elite()
          allinfo = {
          'name': u.username,
          'active': u.is_active,
          'is_elite': e,
          'badge': p.badge(e),
          'joined': u.date_joined,
          'postcount': p.postcount,
          'profile_link': reverse_lazy('fprofiles_profile_detail', kwargs={'uid': uid}),
          'avatar_standard': get_avatar(u, 'standard'),
          'avatar_small': get_avatar(u, 'small'), 
                }
          cache.set(ckey, allinfo, 300)
          return allinfo




def avatar_path(instance=None, filename=None, user=None):
  user = user or instance.user
  p = 0
  if user:
    p = user.id
  return "uploads/avatars/%d-%s" % (p, filename)


class Avatar(models.Model):
    user = models.OneToOneField(User, verbose_name='user', related_name='useravatar', editable=False)
    avatar = models.ImageField(upload_to=avatar_path)

    def __unicode__(self):
      return self.avatar.name
      
    def save(self, *args, **kwargs):
      # save the avatar, then flush the userinfo data from the cache.
      super(Avatar, self).save(*args, **kwargs)
      get_user_info(self.user, True)
    
    
def get_avatar(user, size='standard'):
    """ Get a user's avatar, or the default av if they don't have one.
    Takes a user object or username. Return path, width and height. """
    avconf=getattr(settings, 'AVATAR_'+size.upper(), None)
    if avconf is None:
      return ''
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:#handle deleted users
            avpath = avconf['default']
            user = ''
    if isinstance(user, User):
        try:
          avatar = user.useravatar
          thumbnailer = get_thumbnailer(avatar.avatar)
          thumbnail_opts = dict(size=(avconf['width'], avconf['height']), crop=True)
          # can't use Thumbnailer's .tag() method, because we need to put a class in the url
          # and that's a python syntax error when passed as an argument.
          avpath = thumbnailer.get_thumbnail(thumbnail_opts).url
          
        except Avatar.DoesNotExist:
          avpath = avconf['default']

        except:
          """ catch other errors that might 500 the page and log"""
          logger.error("Invalid image format for %s avatar %s" % (user.username, sys.exc_info()[0]))
          avpath = avconf['default']

    return avpath




