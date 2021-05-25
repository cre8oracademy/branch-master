from django.test import TestCase
from fuksubs.models import UserSub, activate_sub
from django.contrib.auth.models import User, Group
from paypal.standard.ipn.models import PayPalIPN

from django.conf import settings

import datetime
# TODO un-hardcode expiry date for new subs

POSTGROUPS=settings.POSTGROUPS

class SubsTest(TestCase):
  fixtures = ['ipn_test']

  def setUp(self):
    """ Set up some users"""
    self.basic = User.objects.create_user(username="basic", email="tester@example.com", password="!")
    self.elite = User.objects.create_user(username="elite", email="elite@example.com", password="!")
    elites = Group.objects.get(pk=POSTGROUPS['Elite'])
    self.elite.groups.add(elites)
    self.newbie = User.objects.create_user(username="newbie", email="newbie@example.com", password="!")

  def test_activate_subscription(self):
    """ upgrade a basic user's account to elite"""
    profile = self.basic.get_profile()
    self.assertFalse(profile.is_elite()) # should not be elite member
    # add a subscription entry for member
    expiry = datetime.date(2012, 12, 31)
    sub = UserSub(user=self.basic, status='u', expiry=expiry, paypalref='askljdhfkjasdkfasdfkjahsdfaskdlfhkasj')
    sub.save()
    sub.activate()
    # should now be elite
    updated = self.basic.get_profile()
    self.assertTrue(updated.is_elite())
    self.assertIn('jimmy_av.gif', updated.badge())
    
  def test_deactivate_subscription(self):
    """ downgrade an elite user's account to basic """
    profile = self.elite.get_profile()
    self.assertTrue(profile.is_elite()) # should be elite member
    # add a subscription entry for member
    expiry = datetime.date(2012, 12, 31)
    sub = UserSub(user=self.elite, status='a', expiry=expiry, paypalref='askljdhfkjasdkfasdfkjahsdfaskdlfhkasj')
    sub.save()
    sub.deactivate()
    # should now be basic
    updated = self.elite.get_profile()
    self.assertFalse(updated.is_elite())
    self.assertEqual('', updated.badge())

  def test_signup_signal(self):
    """ test user is upgraded via ipn signal """
    u = User.objects.get(pk=1)
    self.assertEquals(u.username, "basic")
    signup_obj = PayPalIPN.objects.get(custom=u.id, txn_type="subscr_signup") # get our preloaded IPN
    activate_sub(signup_obj)
    # should now be elite
    updated = u.get_profile()
    self.assertTrue(updated.is_elite())

  def test_eot_signal(self):
  	""" test user subscription is marked for expiry"""
  	pass