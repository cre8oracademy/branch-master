# Custom context processors for fuk templates.
from userena.contrib.umessages.models import MessageRecipient
from fprofiles.models import UserProfile, get_user_info
# should we display the login/user info block?
# We do this here to check possible pages where it should be excluded in one place, then add the single check to the template.
def login_block(request):
  display_login=True
  if request.path_info in ("/accounts/login/", "/accounts/logout/", "/accounts/activate/", "/accounts/activate/complete/"):
    display_login=False
  return {'display_login': display_login}
    


def user_info(request):
  # check this request has a user, needed for oembed
  if hasattr(request, 'user'):
    if request.user and request.user.is_authenticated():
      info = get_user_info(request.user)
      info['inbox_count'] = MessageRecipient.objects.count_unread_messages_for(request.user)
      return {'user_info': info}
  return {}
