"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase
from django.core.urlresolvers import reverse

from git_posthook.models import GitAction

class ViewsTest(TestCase):
  
  def test_post_receive(self):
    uri = '/webhooks/post_receive'
    r = self.client.post(uri, {"payload": "some random text"})
    self.assertEquals(r.status_code, 200)
    g = GitAction.objects.all()[0]
    self.assertEquals(g.payload, "some random text")