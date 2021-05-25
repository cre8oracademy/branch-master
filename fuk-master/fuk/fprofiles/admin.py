from fprofiles.models import *
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    
class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)

class AvatarAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)

admin.site.register(Avatar, AvatarAdmin)