# Logging, signals and other utils
# This stuff is all imported in the top level module file 
# __init__.py, so that we can be sure it is available
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from smileys.models import Smiley
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
import logging
try:
  from statsd import statsd
except:
  pass # statsd optional
  
logger = logging.getLogger('fukapp.utils')

def log_to_amon():
  pass

# cache smileys.
# Cut down on endless db requests for something that
# very rarely changes.

def cache_smileys():
  smiles = Smiley.objects.filter(is_active=True)
  cached_smiles = []
  for smiley in smiles:
    # store image data on cached object
    smiley.img = '<img class="smiley" src="%s" alt="%s" height="%i" width="%i" />' % (smiley.image.url, smiley.description, smiley.image.height, smiley.image.width)
    if smiley.default == '' and not smiley.is_regex:
      smiley.default = smiley.pattern
    cached_smiles.append(smiley)
  # cache for a day
  cache.set('stored_smileys', cached_smiles, 24*60*60)
  # pass through
  # logger.info('smiley cache updated')
  return cached_smiles 
  
# Signals
@receiver(post_save, sender=Smiley, weak=False)
def cache_smileys_on_signal(sender, **kwargs):
  return cache_smileys()
  
# Log creation of objects. Include the username and URL of the item 
# if available. Also send to statsd, if there is a STATSD_PREFIX set.
@receiver(post_save)
def item_was_created(sender, **kwargs):
  obj_list=['Post', 'Thread', 'Photo']
  cl = sender.__name__
  if cl in obj_list and kwargs['created']:
    item = kwargs['instance']
    username = url = ''
    if hasattr(item, 'user'):
      username = item.user.username
    if hasattr(item, 'get_absolute_url'):
      url = item.get_absolute_url()
    d = {'type': cl, 'id': item.pk, 'user': username, 'url': url}
    logger.info("%(type)s created by %(user)s %(url)s ", d, extra=d)
    if getattr(settings, 'STATSD_HOST', ''):
      try:
        statsd.incr(cl)
      except:
        pass
      
    
class FukappFormatter(logging.Formatter):
  def format(self, record):
    import pprint
    return pprint.pprint(record.__dict__)
    
def notify_pm_recipients(message):
  """ Send an email notification"""
  recips = message.recipients.all()
  subject = "You have received a new private message at fuk.co.uk"
  from_email = settings.DEFAULT_FROM_EMAIL
  for r in recips:
    p = r.get_profile()
    if p.messagenotify=="i":
      ctx = {'user': r, 'site': Site.objects.get_current()}
      message = render_to_string('umessages/pm_notification.txt', ctx)
      r.email_user(subject, message)
      
      