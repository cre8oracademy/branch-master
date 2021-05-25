from django.conf.urls import *
from fukphotos.models import Photo
from fukphotos.views import DeletePhoto


urlpatterns = patterns('',
  url(r'^user/(?P<uid>[0-9]+)/(?P<page>[0-9]+)/', 'fukphotos.views.user_photos', name='photo_user'),
  url(r'^tag/(?P<tagslug>[-_\w]+)/(?P<page>[0-9]+)/', 'fukphotos.views.tagged_photos', name='photo_tag'),
  url(r'^recent/(?P<page>[0-9]+)/', 'django.views.generic.list_detail.object_list', {'queryset': Photo.objects.all(), 'paginate_by': 20, 'extra_context':{'list_title': 'Recent photos'}}, name='photo_recent'),
  url(r'^add', 'fukphotos.views.create_photo', name='photo_add'),
  url(r'^view/(?P<slug>[-_\w]+)/$', 'django.views.generic.list_detail.object_detail', {'queryset': Photo.objects.all(), 'template_object_name': 'photo'}, name='photo_detail'),
  url(r'^edit/(?P<slug>[-_\w]+)/$', 'fukphotos.views.edit_photo', name='photo_edit'),
  url(r'^delete/(?P<slug>[-_\w]+)/$', DeletePhoto.as_view(), name='photo_delete'),
   )
   
   
