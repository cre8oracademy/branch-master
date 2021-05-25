from userena.contrib.umessages.models import Message, MessageRecipient
from django.core.management.base import BaseCommand, CommandError
from django.template import Context
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail import send_mass_mail
from datetime import datetime, timedelta

# Notify any users with unread pms that have 
# been received in the last 24 hours

PM_OFFSET = timedelta(hours=24)

class Command(BaseCommand):
  help = "Send email notifications to users with new private messages"
  
  def handle(self, *args, **options):
    subject = "You have new private messages at fuk.co.uk"
    from_email = settings.DEFAULT_FROM_EMAIL
    interval = datetime.now() - PM_OFFSET
    recips = MessageRecipient.objects.filter(message__sent_at__gte=interval).filter(read_at__isnull=True)
    users = [r.user for r in recips]
    # we might have duplicates in our list of recipients, so filter them
    # out. Tried using distinct() on the queryset for this but didn't work.
    # used a technique from here to do it http://www.peterbe.com/plog/uniqifiers-benchmark
    set = {}
    map(set.__setitem__, users, [])
    send_list = set.keys()
    messages = []
    for r in send_list:
      p = r.get_profile()
      if p.messagenotify=="d":
        ctx = {'user': r, 'site': Site.objects.get_current()}
        message = render_to_string('umessages/pm_digest_notification.txt', ctx)
        # send mass email requires email address in a list
        recipient = [r.email]
        m = (subject, message, from_email, recipient)
        messages.append(m)
    n = send_mass_mail(tuple(messages))
    self.stdout.write("%d messages sent\n" % n)

  