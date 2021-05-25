from fuksubs.models import *
from django.contrib import admin

class SubscriptionAdmin(admin.ModelAdmin):
	pass

admin.site.register(UserSub, SubscriptionAdmin)
