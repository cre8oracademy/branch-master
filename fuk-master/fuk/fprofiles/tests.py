"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User, Group

POSTGROUPS=settings.POSTGROUPS

class ProfileTest(TestCase):
  # Load the main board fixture, which gives us groups and permissions
    fixtures = ['snapboard/fixtures/snap_test_data.json']

    def setUp(self):
      self.basic = User.objects.create_user(username="basic", email="tester@example.com", password="pass")
      self.basic.groups.add(Group.objects.get(pk=POSTGROUPS['Basics']))

    def test_avatar_change(self):
      # log in, access profile page
      self.client.login(username='basic', password='pass')
      response = self.client.get('/profile/%d/' % self.basic.id)
      self.assertEqual(response.status_code, 200)
      # access change avatar page
      response = self.client.get('/profile/change_av/')
      self.assertContains(response, 'Change avatar for basic')
      testav = open('snapboard/fixtures/test_image.jpg')
      postresp = self.client.post('/profile/change_av/', {'avatar': testav}, follow=True)
      self.assertEqual(postresp.status_code, 200)
