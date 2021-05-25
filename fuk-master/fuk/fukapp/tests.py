"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson
from django.contrib.auth.models import User, Group
from fukapp.models import Competition, CompetitionEntry

class CompetitionTestCase(TestCase):
  fixtures = ['comptest', 'snapboard/fixtures/snap_test_data.json']
  
  def setUp(self):
    self.tester = User.objects.create_user(username="tester", email="tester@example.com", password="secret")
    self.newbie = User.objects.create_user(username="newbie", email="newbie@example.com", password="secret")
    self.elite = User.objects.create_user(username="elite", email="elite@example.com", password="secret")
    goldens=Group.objects.get(name="Goldens")
    self.elite.groups.add(goldens)
    """ Using the competition fixture, set the go live date to a week ago, and the end date to next week."""
    d = datetime.date.today()
    w = datetime.timedelta(days=7)
    for c in Competition.objects.all():
      c.end_date = d+w
      c.start_date = d-w
      c.save()

    
  def test_comp_entry(self):
    """ Enter one user in to one competition, check is entered and another user isn't"""
    c = Competition.objects.all()[0]
    ce = CompetitionEntry.objects.create(user=self.newbie, competition=c)
    self.assertEqual(c.user_has_entered(self.newbie), True)
    self.assertEqual(c.user_has_entered(self.tester), False)
    
  def test_comp_is_live(self):
    """ Start date is in past, end date in future, comp should be live."""
    c = Competition.objects.all()[0]
    self.assertEqual(c.is_live(), True)

  def test_comp_is_closed(self):
    """ Change start date to yesterday, comp should be closed"""
    d = datetime.date.today() - datetime.timedelta(days=1)
    c = Competition.objects.all()[0]
    c.end_date = d
    c.save()
    self.assertEqual(c.is_live(), False)


  def test_comp_eligibilty(self):
    """ For an elite only comp, newbie can't enter, elite can"""
    c = Competition.objects.get(pk=2) # comp 2 in fixture is elite only.
    self.client.login(username=self.elite.username, password="secret")
    uri = c.get_absolute_url()
    # check for create an entry button
    r = self.client.get(uri)
    self.assertContains(r, '<button class="entrylink" type="submit">Enter for <b>%s</b></button>' % self.elite.username)
    self.client.logout()
    self.client.login(username=self.newbie.username, password="secret")
    s = self.client.get(uri)
    self.assertContains(s, 'You need to be an')

 
  def test_comp_entry_submits(self):
    """check entry can be submitted"""
    c = Competition.objects.get(pk=2) # comp 2 in fixture is elite only.
    self.client.login(username=self.elite.username, password="secret")
    # test ajax entry submission.
    uri = reverse('competition_enter')
    # although this is an ajax call off the web page, it seems
    # to only work in testing if made as a standard post, without
    # serialising the form in to JSON.
    p = self.client.post(uri, data={'comp': c.comp_id, 'mailingpref': 1})
    self.assertContains(p, 'Thanks for entering, good luck!')
    # try a duplicate entry
    s = self.client.post(uri, data={'comp': c.comp_id, 'mailingpref': 1})
    self.assertContains(s, 'You have already entered this competition.')

    
    
    
class PrivateMessageTestCase(TestCase):
  
    fixtures = ['snapboard/fixtures/snap_test_data.json']
    
    def setUp(self):
      self.tester = User.objects.create_user(username="tester", email="tester@example.com", password="secret")
      self.newbie = User.objects.create_user(username="newbie", email="newbie@example.com", password="secret")
      self.elite = User.objects.create_user(username="elite", email="elite@example.com", password="secret")
      goldens=Group.objects.get(name="Goldens")
      self.elite.groups.add(goldens)

    def test_basic_message(self):
      """ Create a message and make sure it is visible """
      sender = self.tester
      recip = self.newbie
      body = "how's it going mate?"
      self.client.login(username=sender.username, password="secret")
      uri = reverse('userena_umessages_compose')
      p = self.client.post(uri, data = {'body': body, 'to': recip.username},
       follow=True)
      # we should redirect to our conversation page, which will contain the 
      # message
      self.assertTemplateUsed(p, 'umessages/message_detail.html')
      self.assertContains(p, body)
      self.client.logout()
      self.client.login(username=recip.username, password="secret")
      spk = sender.id
      uri = reverse('userena_umessages_list')
      r = self.client.get(uri)
      # Check that our sender is listed in our inbox
      self.assertContains(r, sender.username)
      # and that the message shows up on our conversation page
      uri = reverse('userena_umessages_detail', kwargs={'user_id': spk})
      r = self.client.get(uri)
      self.assertContains(r, body)







