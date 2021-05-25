# Create your views here.
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response, render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic.list_detail import object_list

from django.views.generic.edit import DeleteView

from models import Photo, PhotoForm
from snapboard.utils import SlugifyUniquely 

from taggit.models import Tag


@permission_required('fukphotos.add_photo', raise_exception=True)
def create_photo(request):
  """Upload a new photo to the site, or display the upload form."""
  if request.method != 'POST':
    form = PhotoForm()
  else:
    form = PhotoForm(request.POST, request.FILES)
    if form.is_valid():
      new_image = form.save(commit=False)
      # create a slug for this image.
      new_image.slug = SlugifyUniquely(new_image.title, Photo)
      new_image.user = request.user
      new_image.save()
      form.save_m2m()
      redir=reverse('photo_detail', kwargs={'slug': new_image.slug})
      return HttpResponseRedirect(redir)
  return render_to_response("fukphotos/photo_form.html", {'form': form}, context_instance=RequestContext(request))
    
    
def edit_photo(request, slug):
  """Edit an existing photo"""
  photo = get_object_or_404(Photo, slug=slug)
  u = request.user
  if  u.is_staff or photo.user.id==u.id:
    if request.method=="POST":
      form = PhotoForm(request.POST, request.FILES, instance=photo)
      if form.is_valid():
        p = form.save()  
        redir=reverse('photo_detail', kwargs={'slug': slug})
        return HttpResponseRedirect(redir)
      else:
        # show the errors
        return render(request, "fukphotos/photo_form.html", {'form': form, 'editing': True})
    else:
      form = PhotoForm(instance=photo)
      return render(request, "fukphotos/photo_form.html", {'form': form, 'editing': True})
  else:
    HttpResponseForbidden("Only the owner of the photo can edit")   
    
    
class DeletePhoto(DeleteView):
  """Delete a photo. Uses generic view as base"""
  model = Photo
  def post(self, request, *args, **kwargs):
    obj = self.get_object()
    if obj.user != self.request.user:
      return HttpResponseForbidden("Only the owner of the photo can delete it")   
    messages.success(request, "Photo deleted")
    return super(DeleteView, self).post(request, *args, **kwargs)
  def get_success_url(self):
    return reverse('photo_user', kwargs={'uid': self.request.user.id, 'page': 1})

   
def user_photos(request, uid, page):
  """ Display photos for the user with id uid. Check that the user exists and is active, otherwise raise a 404"""
  u = get_object_or_404(User, pk=uid)
  if not u.is_active:
    raise Http404
  qs = Photo.objects.all().filter(user=uid)
  
  ltitle = "%s's photos" % u.username
  ec = {'list_title': ltitle, 'emptytext': "There are no photos from this user."}
  return object_list(request, queryset=qs, extra_context=ec, paginate_by= 20, page=page)
  
def tagged_photos(request, tagslug, page):
  """ Display photos with a particular tag"""
  qs = Photo.objects.all().filter(tags__slug=tagslug)
  try:
    tag = Tag.objects.get(slug=tagslug)
  except Tag.DoesNotExist:
    raise Http404
  ltitle = "Photos tagged with '%s'" % tag.name
  ec = {'list_title': ltitle, 'emptytext': "There are no photos with this tag."}
  return object_list(request, queryset=qs, extra_context=ec, paginate_by=20, page=page)