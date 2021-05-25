from snapboard.models import Thread, WatchList, Read, NotifyRun
from datetime import datetime, timedelta
from django.template import Context
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings

from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand, CommandError

# Search through the updated threads, if they are:
# - on a user's watchlist
# - not been read by user
# send notification(s)

class Command(BaseCommand):
    """Process a batch of notifications of thread updates. tp is 'i' for immediate 'd' for daily digest. (immediate can still be a digest of notifications if more than one has been updated since the last run.)"""
    args = "immediate or daily"
    help = "Process thread update notification emails."

    def handle(self, *args, **options):
        types = {'immediate': 'i', 'daily': 'd'}
        if not args[0] in types:
          raise CommandError("Type must be 'immediate' or 'daily'")
        tp = types[args[0]]
        starttime = datetime.now()
        try:
            lastrun = NotifyRun.objects.filter(notifytype=tp).latest()
            lastruntime = lastrun.starttime
        except NotifyRun.DoesNotExist:
            lastruntime = starttime-timedelta(hours=1) # default to an hour ago, if we have no runs
        # Find threads that have been updated since lastruntime
        # Store details of threads (name and url) in a dict keyed on the thread ID
        # Store users to be notified in another dict, with their id as a key, email and threads (list) as values
        threads = Thread.objects.filter(updated__gte=lastruntime)
        thr={}
        notifs={}    
        domain = Site.objects.get_current().domain
        for thread in threads:
            recips=thread.get_notify_recipients(postnotify=tp)
            thr[thread.pk] = dict(name=thread.name, url="http://%s%s" % (domain, thread.get_absolute_url()))
            for r in recips.keys():
                try:
                    o = Read.objects.get(user=r, thread=thread.pk)
                    if o.time > thread.updated:
                        # user has already read updated thread, drop them from the updates dict
                        recips.pop(r)
                    else:
                        # add this thread to the list for this recipient, or create the list if this is the first.
                        if r in notifs:
                            notifs[r]['threads'].append(thread.pk)
                        else:
                            notifs[r]={'threads': [thread.pk], 'email': recips[r]}
                except Read.DoesNotExist:
                    pass
                    # Should be impossible, but handle error silently if it happens.
        # process each notification
        messages = []
        for n in notifs.iterkeys():
            uthreads=[thr[i] for i in notifs[n]['threads']]
            email= notifs[n]['email']
            ctx={'email': email, 'threads': uthreads}
            ctx['ntype']='immediate'
            if tp=='d':
                ctx['ntype']='digest'
            subject = render_to_string('snapboard/notification_subject.txt', ctx)
            body = render_to_string('snapboard/notification_body.txt', ctx)
            messages.append((subject, body, settings.DEFAULT_FROM_EMAIL, [email]))
        if messages:
            try:
                send_mass_mail(tuple(messages), fail_silently=False)
            except smtplib.SMTPException as e:
                raise CommandError(e.value)
        elapsed=datetime.now()-starttime
        notifcount = len(notifs)
        nt=NotifyRun(starttime=starttime, elapsed=elapsed.seconds, threadcount=threads.count(), usercount=len(notifs), notifytype=tp)
        nt.save()
        self.stdout.write('Sent %d notifications\n' % notifcount)
        
    

