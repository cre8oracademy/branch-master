import os

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

# from snapboard.urls import feeds
from snapboard.models import *
from snapboard.utils import *
from snapboard.templatetags import sb_tags

class ViewsTest(TestCase):
    # urls = "snapboard.tests.test_urls"
    # fixtures = ["test_data.json"]
    fixtures = ["initial_data.json"]

    
    def setUp(self):        
         # get our groups
         newbies=Group.objects.get(name="Newbies")
         basics=Group.objects.get(name="Basics")
         goldens=Group.objects.get(name="Goldens")
         # create some users.
         self.newbie = User.objects.create_user(username="newbie", email="newbie@example.com", password="secret")
         self.newbie.groups.add(newbies)
         self.basic = User.objects.create_user(username="basic", email="basic@example.com", password="secret")
         self.basic.groups.add(basics)
         # we can't create group permissions through fixtures, so we do them here
         p=Permission.objects.get(codename="post_unmoderated")
         basics.permissions.add(p)
         self.golden = User.objects.create_user(username="golden", email="golden@example.com", password="secret")
         self.golden.groups.add(basics, goldens)
         self.admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="secret") 
         # create one new thread in menswear
         cat = Category.objects.get(pk=1)
         self.thread = Thread(user=self.basic, name="thread", slug="thread", category=cat)
         self.thread.save()
         self.initialpost = Post(user=self.basic, thread=self.thread, text="initial post text")
         self.initialpost.save()  
#     
#     def tearDown(self):
#         settings.TEMPLATE_DIRS = self.old_template_dir
#         settings.SNAP_POST_FILTER = self.old_snap_post_filter
#     

    # Helpers ##################################################################

    def login(self, username="basic"):
        self.client.login(username=username, password="secret")

    def assertJSON(self, name, expected=None, pk=1, post=None):
        self.login()
        uri = reverse("sb_%s" % name)
        if post is None:
            post = {"id": pk}
        r = self.client.post(uri, post)
        
        if expected is not None:
            self.assertEquals(r.content, expected)
        else:
            self.assertEquals(r.status_code, 200)


    # Tests ####################################################################

    def test_preview(self):
       self.assertJSON("preview")
    
    def test_sticky(self):
        self.assertJSON("sticky")

    def test_close(self):
        self.assertJSON("close")

    def test_watch(self):
        self.assertJSON("watch")
    
    # def test_edit(self):
    #     self.assertJSON("edit")

    def test_category_list(self):
        uri = reverse("sb_category_list")
        r = self.client.get(uri)
        self.assertTemplateUsed(r, "snapboard/category_list.html")

    def test_category(self):
        uri = reverse("sb_category", kwargs={"slug": "menswear"})
        r = self.client.get(uri)
        self.assertTemplateUsed(r, "snapboard/thread_list.html")

    def test_thread_list(self):
        uri = reverse("sb_thread_list")
        r = self.client.get(uri)
        self.assertTemplateUsed(r, "snapboard/thread_list.html")
    
    def test_thread(self):
        uri = reverse("sb_thread", kwargs={"tslug": "thread"})
        r = self.client.get(uri)
        self.assertTemplateUsed(r, "snapboard/paged_thread.html")
        
        # Log in to create a post.
        self.login("basic")

        # Creating a post redirects to the new post.
        r = self.client.post(uri, {"text": "post"})
        new_post = Post.objects.order_by("-date")[0]
        expected_uri = new_post.get_url()
        self.assertRedirects(r, expected_uri)

    def test_post_filtering(self):
        """Test posts are correctly filtered, markup converted and not over-escaped"""
        testpost="""
             http://www.bbc.co.uk is a great site"""
        uri = reverse("sb_new_thread", args=["menswear"])
        r = self.client.get(uri)
        self.login()
        r = self.client.post(uri, {"subject": "thread subject", "post": testpost, "category": "1"}, follow=True)
        self.assertContains(r, '<a href="http://www.bbc.co.uk"', status_code=200)


    def test_new_thread(self):
        # check user has post permission
        self.assertTrue(self.basic.has_perm("snapboard.post_unmoderated"))
        # Log in to create a thread.
        self.login()

        uri = reverse("sb_new_thread", args=["menswear"])
        r = self.client.get(uri)
        self.assertTemplateUsed(r, "snapboard/new_thread.html")
        
        # Creating a thread redirects to the new thread.
        r = self.client.post(uri, {"subject": "thread subject", "post": "post", "category": "1"})
        new_thread = Thread.objects.order_by("-updated")[0]
        expected_uri = new_thread.get_url()
        self.assertRedirects(r, expected_uri)

    def test_favorites(self):
        # Login to see favs.
        self.login()    
        uri = reverse("sb_favorites")
        r = self.client.get(uri)
        self.assertTemplateUsed(r, "snapboard/thread_list.html")
    
# 
#     def test_feeds(self):
#         for feed in feeds.keys():
#             uri = reverse("sb_feeds", args=[feed])
#             r = self.client.get(uri)
#             self.assertEquals(r.status_code, 200)
    
    def test_thread_slug(self):
        # No problems with dupe slugs right? There is a existing thread w/ slug "thread"
        self.login()
        uri = reverse("sb_new_thread", args=["menswear"])        
        r = self.client.post(uri, {"subject": "thread", "post": "post", "category": "1"})
        new_thread = Thread.objects.order_by("-updated")[0]
        self.assertEquals(new_thread.slug, "thread-1")

    def test_newbie_moderation(self):
        """Test that a newbie post is moderated"""
        self.login("newbie")
        uri = reverse("sb_new_thread_nocat")
        # make a post in random questions (cat 9)
        r = self.client.post(uri, {"subject": "thread", "post": "post", "category": "9"})
        expected_uri = reverse("sb_moderated")
        self.assertRedirects(r, expected_uri)
        # new thread should not be accessible until moderated
        new_thread = Thread.objects.order_by("-updated")[0]
        nt_uri = reverse("sb_thread", args=[new_thread.slug])
        s = self.client.get(nt_uri)
        self.assertEquals(s.status_code, 404)
        # moderate the post
        p = new_thread.post_set.all()[0]
        # get a user object to use as the moderator, doesn't matter that they dont
        # have perms, as that would normally be checked in the view.]
        p.moderate(status='a', moduser=self.basic)
        
    def test_active_threads_block(self):
        """ Test that the active threads block shows the right posts to the right people."""
        self.login("golden")
        uri = reverse("sb_new_thread_nocat")
        # make a new thread in general
        r = self.client.post(uri, {"subject": "a general thread", "post": "post text", "category": "2"})
        # and one in elite
        e = self.client.post(uri, {"subject": "an elite thread", "post": "post text", "category": "4"})
        tslist = sb_tags.active_threads(self.golden)
        # check that our elite user can see the elite posts in the list
        self.assertIn("an elite thread", tslist)
        self.assertIn("a general thread", tslist)
        # check that the normal user can only see the open thread
        tslist2 = sb_tags.active_threads(self.basic)
        self.assertIn("a general thread", tslist2)
        self.assertNotIn("an elite thread", tslist2)
        
        
        


class ThreadTest(TestCase):
    fixtures = ["test_data.json"]

    # def test_get_notify_recipients(self):
    #     # should just return a set of the admins
    #     r = Thread.objects.get(pk=1).get_notify_recipients()
    #     self.assertEquals(r, set([t[1] for t in settings.ADMINS]))
    #     
        
class UtilsTest(TestCase):
    pass
    # def test_bcc_mail(self):
    #     recipient_list = ["to@example.com"]
    #     bcc_mail("subj", "body", "from@example.com", recipient_list)
    #     self.assertEquals(len(mail.outbox), 1)
    #     self.assertEquals(mail.outbox[0].to, [])
    #     self.assertEquals(mail.outbox[0].bcc, recipient_list)