from django.conf.urls.defaults import *

urlpatterns = patterns('toolkit.views',
    url(r'^start/$', 'startDownload', name='startDownload'),
    url(r'^status/$', 'status', name='status'),
    url(r'^$', 'download', name='download'),
)
