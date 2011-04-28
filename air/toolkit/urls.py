from django.conf.urls.defaults import *

urlpatterns = patterns('toolkit.views',
    url(r'^start/$', 'startDownload', name='startDownload'),
    url(r'^saveData/$', 'saveData', name='saveData'),
    url(r'^pmis/$', 'calcPMIs', name='calcPMIs'),
    url(r'^status/\d/(w+)$', 'status', name='status'),
    url(r'^$', 'download', name='download'),
)
