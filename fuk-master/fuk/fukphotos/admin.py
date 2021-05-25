from fukphotos.models import *
from django.contrib import admin

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')

admin.site.register(Photo, PhotoAdmin)


   