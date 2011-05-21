from django.conf.urls.defaults import *

urlpatterns = patterns('toolkit.views',
    url(r'^download/start/$', 'startDownload', name='startDownload'),
    url(r'^download/status/$', 'status', name='status'),
    url(r'^pmis/(\d+)$', 'like_pmis', name='like_pmis'),
    url(r'^category/add/(\w+)$', 'addSeed', name='addSeed'),
    url(r'^category/delete/(\w+)$', 'deleteSeed', name='deleteSeed'),
    url(r'^category/rename/$', 'rename', name='categoryRename'),
    url(r'^category/status/$', 'categoryStatus', name='categoryStatus'),
)
