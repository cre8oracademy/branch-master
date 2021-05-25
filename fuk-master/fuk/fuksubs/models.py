from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from datetime import datetime
from paypal.standard.ipn.signals import subscription_signup
import logging
logger = logging.getLogger(__name__)

"""
Subscriptions System
====================

We have a master subs table, the UserSub model, which contains information
about a user's subscription: a link to their user id, a subscription status
and an expiry date.

The Django-paypal table contains a record of all PayPal transactions relating to 
subscriptions. 

Status updates are triggered on signals as the PayPal notifications appear. However,
it would be a good idea to incorporate some sort of batch offline processing that
runs through the tables and makes sure everything is up-to-date.

Lifetime GJs have their expiry date set to some distant point in the future.

Status can also be set to unknown in situations where we have no payment record.


"""

POSTGROUPS=settings.POSTGROUPS

STATUS_CHOICES=(
	('a', 'Active'),
	('e', 'Expired'),
    ('u', 'Unknown')
)


class UserSub(models.Model):
    """A user's subscription"""
    user = models.OneToOneField(User, verbose_name='user', related_name='usersubscription')
    # use choices, active, expired
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    expiry = models.DateTimeField(blank=False)
    paypalref = models.CharField(max_length= 64, verbose_name='Paypal Reference', help_text='The Paypal subscription reference')

    def activate(self):
        """Make subscription active, add to elite group"""
        prof = self.user.get_profile()
        if prof.is_elite():
            return    
        elites = Group.objects.get(pk=POSTGROUPS['Elite'])
        self.user.groups.add(elites)
        self.status = 'a'
        self.save()

    def deactivate(self):
        """deactivate a subscription"""
        prof = self.user.get_profile()
        if not prof.is_elite():
            return
        elites = Group.objects.get(pk=POSTGROUPS['Elite'])
        self.user.groups.remove(elites)
        self.status = 'e'
        self.save()
        

def activate_sub(sender, **kwargs):
    ipn_obj = sender
    uid = ipn_obj.custom # get users id from ipn
    try:
        u=User.objects.get(pk=uid)
    except User.DoesNotExist: # do we have a valid uid?
        logger.error("Subscription activation error: No user with id %d" % uid)
        return
    try:
        exsub=u.usersubscription
        if exsub.paypalref == ipn_obj.subscr_id:
            # this is a dupe of an already updated sub
            return
        else:
            # this is  a new and unnecessary subscription, let someone know.
            logger.error("Subscription activation error: User %s has an existing subscription, reference %s" %
                (u.username, exsub.paypalref))
    except UserSub.DoesNotExist:
        pass
    # paypal doesn't give us a clear expiry date, so we'll make our own
    # TODO this hardcodes the subscription duration - problem?
    xp = datetime.now()
    xp = xp.replace(year=xp.year+1)
    sub = UserSub(user=u, status='a', expiry=xp, paypalref=ipn_obj.subscr_id)
    sub.save()
    sub.activate()
    logger.info("New elite subscription created for %s" % u.username)

def deactivate_sub(sender, **kwargs):
    """ Deactivate subscription when eot signal received from paypal"""
    ipn_obj = sender
    paypalref=ipn_obj.subscr_id
    # Get the user's subscription record
    try:
        sub=UserSub.objects.get(paypalref=paypalref)
    except UserSub.DoesNotExist: # do we have a valid uid?
        logger.error("Subscription deactivation error: No user with paypal reference %s" % paypalref)
        return
    
    sub.deactivate()
    logger.info("Subscription terminated for user %s" % sub.user.username)

subscription_signup.connect(activate_sub)
