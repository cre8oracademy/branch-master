from registration.signals import user_activated
from django.contrib.auth import login
from django.contrib.auth.models import User, Group

# assign newly activated users to the "Newbies" group.

def new_user_group_assign(sender, **kwargs):
  u=kwargs['user']
  try:
    newbiegroup=Group.objects.get(name="Newbies")
    u.groups.add(newbiegroup)
  except:
    pass
    
    
user_activated.connect(new_user_group_assign)


# taken from Stack Overflow answer http://stackoverflow.com/questions/6222656/auto-log-in-and-re-send-email

def login_on_activation(user, request, **kwargs):
    user.backend='django.contrib.auth.backends.ModelBackend'
    login(request, user)

user_activated.connect(login_on_activation)