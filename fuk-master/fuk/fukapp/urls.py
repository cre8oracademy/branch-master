from django.conf.urls import *

from fukapp.views import CompetitionListView
 

urlpatterns = patterns('', 
 url(r'^enter/$', 'fukapp.views.competition_enter', name='competition_enter'),
 url(r'^(?P<slug>[-_\w]+)/$', 'fukapp.views.competition_detail', name='competition_detail'),
 url(r'^', CompetitionListView.as_view(), name='competitions_all'),
   

)