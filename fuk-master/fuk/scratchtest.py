from django.core.management import setup_environ 
import settings 
setup_environ(settings)


from django.contrib.auth.models import User, Group
# from fukapp.models import Competition, CompetitionEntry
# 
# c=Competition.objects.all()[0]
# e=CompetitionEntry.objects.all()[0]
# 
# jack=User.objects.all()[1]
# ben=User.objects.all()[0]
# print c.user_has_entered(jack)
# print c.winners()


# Testing the method for importing all the old avatars.
# using this method to programatically add avatar files.
# http://stackoverflow.com/questions/1993939/programmatically-upload-files-in-django
# also http://docs.djangoproject.com/en/dev/ref/files/file/#additional-methods-on-files-attached-to-objects

from fprofiles.models import Avatar
from django.core.files import File
import os
ben=User.objects.get(pk=1)
av = Avatar(user=ben)
pic=os.path.join(settings.MEDIA_ROOT, 'avatar-imports/joze-b+wsquare.jpg')


with open(pic, 'rb') as pic_file:
  av.avatar.save('av0001.jpg', File(pic_file), save=True)
  
