# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from git_posthook.models import GitAction
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def post_receive(request):
  """Receive values from a GitHub post hook"""
  if request.method != "POST":
    return HttpResponseForbidden()
  payload = request.POST.get('payload')
  if payload:
    ga = GitAction.objects.create(payload=payload)
    ga.save()
  return HttpResponse('OK')