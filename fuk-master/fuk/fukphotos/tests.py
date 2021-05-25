from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from fukphotos.models import Photo
from django.contrib.auth.models import User

class PhotoTest(TestCase):

  def setUp(self):
    # create a user
    self.basic = User.objects.create_user(username="basic", email="basic@example.com", password="secret") 

    

  def test_photo_upload(self):
    """ Test logged in user with post permission can post, others can't"""
    testphoto = "/Users/ben/Dropbox/djangoProjects/nufuk/fuk/fukphotos/testphoto.jpg"
    p = open(testphoto, 'rb')
    self.client.login(username="basic", password="secret")
    resp = self.client.post('/photos/add', {'title': "test photo", 'description':"this is a test photo", 'tags':"tag1, tag2", 'original_image':p}, follow=True)
    p.close()
    self.assertEqual(resp.status_code, 403)
    self.client.logout()
    # give some more perms
    p = Permission.objects.get(codename="add_photo")
    self.basic.user_permissions.add(p)
    p = open(testphoto, 'rb')
    self.client.login(username="basic", password="secret")
    resp = self.client.post('/photos/add', {'title': "test photo", 'description':"this is a test photo", 'tags':"tag1, tag2", 'original_image':p}, follow=True)
    p.close()
    self.assertContains(resp, "<h2>test photo</h2>", status_code=200)
        
    
