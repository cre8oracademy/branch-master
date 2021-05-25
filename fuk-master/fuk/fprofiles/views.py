# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse

from fprofiles.models import UserProfile, Avatar, avatar_path, get_user_info
from fprofiles.forms import UserProfileForm, AvatarForm
from snapboard.models import Post
# we wrap the default profile view with our own, as simply passing our overridden model form class doesn't work (unicode error).

from profiles import views as profile_views

@login_required
def edit_profile(request):
  success=reverse('fprofiles_profile_detail', kwargs={'uid': request.user.id})
  return profile_views.edit_profile(request, form_class=UserProfileForm, success_url=success)

def view_profile(request, uid):
  u=get_object_or_404(User.objects.all(), id=uid)
  ec = {}
  ec['user_info'] = get_user_info(u)
  if request.user.is_authenticated: # logged in users can see posting history and send PMs
    history = Post.objects.get_recent_by_user(u, request.user)[0:10]
    ec['history'] = history
  return profile_views.profile_detail(request, u.username, extra_context=ec)

@login_required
def change_av(request):  
  if request.method=="POST":
    try:
      # do we have an avatar already?
      avatar = Avatar.objects.get(user=request.user)
      form = AvatarForm(request.POST, request.FILES, instance=avatar)
      newentry = False
    except Avatar.DoesNotExist:
      form = AvatarForm(request.POST, request.FILES)
      newentry = True
    if form.is_valid:
      inst = form.save(commit=False)
      # a new entry will not have a user attribute
      if newentry:
        inst.user = request.user
      inst.save()
      return HttpResponseRedirect(reverse('fprofiles_profile_detail', kwargs={'uid': request.user.id}))
    else:
      return render_to_response('profiles/edit_avatar.html', {'form': form}, context_instance=RequestContext(request))  
  else: 
    form = AvatarForm()
    return render_to_response('profiles/edit_avatar.html', {'form': form}, context_instance=RequestContext(request))

