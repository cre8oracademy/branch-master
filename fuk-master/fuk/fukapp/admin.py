import csv

from django.contrib import admin
from django.http import HttpResponse

from fukapp.models import *

# Export as CSV for getting comp entries to promoters
# Inspired by https://djangosnippets.org/snippets/2369/

def export_comp_emails_action(modeladmin, request, queryset):
  """ Export the emails for a competition's optins."""

  # get our competition entries
  comp = queryset[0]
  items = CompetitionEntry.objects.filter(competition=comp, mailingpref=True).select_related()
  fname = "%s Email OptIns" % comp.comp_id
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=%s.csv' % (fname,)

  writer = csv.writer(response)
  for item in items:
    writer.writerow([item.user.email])
  return response
export_comp_emails_action.short_description="Export email optins as CSV"
    
class CompetitionAdmin(admin.ModelAdmin):
  list_display=('comp_id', 'start_date', 'end_date', 'entry_count')
  prepopulated_fields={'slug': ("title",)}
  readonly_fields = ('entry_count',)
  actions = [export_comp_emails_action]
    
admin.site.register(Competition, CompetitionAdmin)

class CompetitionEntryAdmin(admin.ModelAdmin):
  list_display=('user', 'competition', 'entered', 'winner', 'mailingpref')
  list_filter=('competition', 'winner', 'entered', 'mailingpref')
  raw_id_fields=('user',)
  readonly_fields=('entered',)
  
admin.site.register(CompetitionEntry, CompetitionEntryAdmin)

class ShoppingItemAdmin(admin.ModelAdmin):
  list_display = ('__unicode__', 'title', 'content')
  search_fields = ('title', 'content')

admin.site.register(ShoppingItem, ShoppingItemAdmin)

class ArchiveContentAdmin(admin.ModelAdmin):
  list_display=('title', 'ogtype', 'pub_date')
  list_filter=('ogtype',)
  
admin.site.register(ArchiveContent, ArchiveContentAdmin)


class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    list_filter = ('active',)


admin.site.register(Affiliate, AffiliateAdmin)





