from snapboard.models import *
from django.contrib import admin

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'category', 'popular', 'private', 'closed')
    list_display_links = ('name',)
    list_filter = ('closed', 'popular', 'category', 'private',)
    search_fields = ('name',)
    raw_id_fields = ('user', 'last_poster',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('truncated_post', 'user', 'date', 'thread', 'ip', 'status')
    list_filter = ('status',)
    search_fields = ('text', 'user')
    raw_id_fields = ('thread', 'user',)
    
    def truncated_post(self, obj):
      return obj.text[0:50]
    truncated_post.short_description = 'Post'
    
class WatchListAdmin(admin.ModelAdmin):
    list_display = ('user', 'thread',)
    search_fields = ('user',)
    raw_id_fields = ('user',)

class ModerationAdmin(admin.ModelAdmin):
    list_display = ('mod', 'post', 'author', 'oldstatus', 'newstatus', 'timestamp')
    readonly_fields = ('mod', 'post', 'author', 'oldstatus', 'newstatus', 'timestamp')
    list_filter = ('oldstatus', 'newstatus')
    search_fields = ('mod',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(WatchList, WatchListAdmin)
admin.site.register(Moderation, ModerationAdmin)

