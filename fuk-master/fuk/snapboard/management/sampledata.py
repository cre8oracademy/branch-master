import os

from django.db.models import signals 
from django.conf import settings

from snapboard import models as snapboard_app
import postdata

def test_setup(**kwargs):
    from random import choice
    from django.contrib.auth.models import User, Group
    from snapboard.models import Thread, Post, Category
    from fprofiles.models import UserProfile
    from django.template.defaultfilters import slugify

    if not settings.DEBUG:
        return 

    if Thread.objects.all().count() > 0:
        # return, since there seem to already be threads in the database.
        return
    
    # ask for permission to create the test
    msg = """
    You've installed SNAPboard with DEBUG=True, do you want to populate
    the board with random users/threads/posts to test-drive the application?
    (yes/no):
    """
    populate = raw_input(msg).strip()
    while not (populate == "yes" or populate == "no"):
        populate = raw_input("\nPlease type 'yes' or 'no': ").strip()
    if populate == "no":
        return

    # create categories
    # cats=("General Discussion", "Fashion Discussion", "Classifieds")
    # for cat in cats:
    #   slug= slugify(cat)
    #   grp=Group.objects.get(pk=2)
    #   c, created = Category.objects.get_or_create(name=cat, slug=slug, read_group=grp, post_group=grp, new_thread_group=grp)
    # create 10 random users

    users = ('john', 'sally', 'susan', 'amanda', 'bob', 'tully', 'fran')
    for u in users:
        user, created = User.objects.get_or_create(username=u, first_name=u)
        user.groups.add(Group.objects.get(pk=2)) # make them all goldens
        # user.is_staff = True
    # make sure all users have profiles
    allusers= User.objects.all()
    for u in allusers:
      try:
        u.get_profile()
      except UserProfile.DoesNotExist:
        p=UserProfile(user=u)
        p.save()


    # create up to 30 posts
    tc = range(1, 50)
    for i in range(0, 35):
        print 'thread ', i, 'created'
        u=choice(User.objects.all())
        cat= choice(Category.objects.all())
        subj = choice(postdata.objects.split('\n'))
        thread = Thread.objects.create_thread(name=subj, category=cat, user=u)
        thread.save()

        for j in range(0, choice(tc)):
            if j > 0: # first post only by thread creator
                u=choice(User.objects.all())
            text = '\n\n'.join([postdata.sample_data() for x in range(0, choice(range(2, 5)))])
            # create a post
            post = Post.objects.create_and_notify(
                    user=u,
                    thread=thread,
                    text=text,
                    ip='.'.join([str(choice(range(1,255))) for x in (1,2,3,4)]),
                    )
            # allows setting of arbitrary ip
            post.save()

signals.post_syncdb.connect(test_setup, sender=snapboard_app) 
# vim: ai ts=4 sts=4 et sw=4

