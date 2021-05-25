from django.views.generic.list import ListView

from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils import simplejson
from django.conf import settings

from fukapp.models import *
from snapboard.utils import *

class CompetitionListView(ListView):
  """Main competition listing, live comps ordered by start date descending"""
  model = Competition
  paginate_by = getattr(settings, "COMPETITION_LISTING_COUNT", 20)
  queryset = Competition.objects.filter(published=True).order_by('-start_date')


def competition_detail(request, slug):
  try:
    comp = Competition.objects.get(slug=slug)
  except Competition.DoesNotExist:
    raise Http404
  ctx = {'comp': comp, 'winners': '', 'has_ended': False, 'user_can_enter': False }
  ctx['splitterms'] = comp.terms.splitlines()
  if not comp.published:
    pass # might want to alter the page based on this setting.
  if comp.has_ended():
    ctx['has_ended'] = True
    winners = comp.winners()
    if len(winners) == 1:
      ctx['winners'] = 'The winner was <strong>%s</strong>' % winners[0]
    if len(winners) > 1:
      ctx['winners'] = 'The winners were ' + ', '.join(["<strong>%s</strong>" % (w,) for w in winners])
  # Comp is active, are we able to enter (is it elite only?), have we entered already?
  elif request.user.is_authenticated():
    ctx['user_can_enter'] = comp.user_can_enter(request.user)
    ctx['user_has_entered'] =  comp.user_has_entered(request.user)
  return render(request, 'fukapp/competition_detail.html', ctx)
  
# using json_response decorator from snapboard.utils.
@json_response
def competition_enter(request):
  if request.method != "POST":
    return '' # shouldn't be possible to submit via get, but just in case, we don't want to change anything, so return an empty string.
  comp_id = request.POST.get('comp')
  mailingpref = request.POST.get('mailingpref') == 'on' or False
  try:
    comp = Competition.objects.get(comp_id=comp_id)
  except Competition.DoesNotExist:
    return {'result': 'Competition does not exist'}
  if not comp.is_live:
    return {'result': 'Sorry, this competition is not active.'}
  if comp.user_has_entered(request.user):
    return {'result': 'You have already entered this competition.'}
  else:
    ce = CompetitionEntry.objects.create(user=request.user, competition=comp, mailingpref=mailingpref)
    ce.save()
    return {'result': 'Thanks for entering, good luck!'}
  # shouldn't happen
  return {'result': ''}
  
  
def view_archive_item(request, nid):
  obj=get_object_or_404(ArchiveContent, pk=nid)
  ctx = {'object': obj}
  return render(request, 'fukapp/archive_content.html', ctx)
  
  
class ShoppingListView(ListView):
  def get_queryset(self):
    return ShoppingItem.objects.get_user_query_set(self.request.user)
  template_name = 'fukapp/shopping_list.html'

  

@json_response
def autocomplete_user(request):
  """Autocomplete from the User model for the Private Message compose box.
  Could be modified to narrow down the search base, perhaps returning people from your contacts first."""
  search_qs = User.objects.filter(username__istartswith=request.REQUEST['term'])
  results = []
  for r in search_qs:
    results.append(r.username)
  return results
  
  