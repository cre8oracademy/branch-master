from django.db import models
from django.forms import ModelForm

from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse

from django.db.models.signals import post_delete
import logging

# user uploadable photos

logger = logging.getLogger('nufuk.models.fukphotos')

class Photo(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    slug = models.SlugField(unique=True, blank=False)
    description = models.TextField(blank=True)
    public = models.BooleanField(default=False)
    user = models.ForeignKey("auth.User", verbose_name='user')
    original_image = models.ImageField(upload_to='uploads/photos', verbose_name='Image')
    num_views = models.PositiveIntegerField(editable=False, default=0)
    created = models.DateTimeField(auto_now_add=True, null=True)
    
    # using django-taggit
    tags = TaggableManager(blank=True)
    

    def get_tag_list(self):
      return self.tags.all()
    
    def get_absolute_url(self):
      return reverse('photo_detail', kwargs={'slug': self.slug})

    def __unicode__(self):
      return self.title
          

class PhotoForm(ModelForm):
  class Meta:
    model = Photo
    fields = ('title', 'description', 'original_image', 'tags')
    
# signal receiver to clean up after photo deleted. Does not deal with derivative thumbs ATM.
def cleanup_photo(sender, **kwargs):
  if sender == Photo:
    i = kwargs['instance']
    try:
      i.original_image.delete(save=False)
    except:
      msg = 'Could not delete file %s' % (i.original_image.filename)
      logger.warning(msg)
      

post_delete.connect(cleanup_photo)
