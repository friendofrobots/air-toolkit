from django.conf.urls.defaults import *

urlpatterns = patterns('toolkit.views',
    url(r'^download/start/$', 'startDownload', name='startDownload'),
    url(r'^download/status/$', 'status', name='status'),
    url(r'^pmis/(\d+)$', 'page_pmis', name='page_pmis'),
    url(r'^category/new/(\S+)$', 'newCategory', name='categoryNewRedirect'),
    url(r'^category/new/$', 'newCategory', name='categoryNew'),
    url(r'^category/start/$', 'startCategoryCreation', name='categoryCreate'),
    url(r'^category/add/(\w+)$', 'addSeed', name='addSeed'),
    url(r'^category/delete/(\w+)$', 'deleteSeed', name='deleteSeed'),
    url(r'^category/rename/$', 'rename', name='categoryRename'),
    url(r'^category/status/(\d+)$', 'categoryStatus', name='categoryStatus'),
    url(r'^category/reset/(\d+)$', 'categoryReset', name='categoryReset'),
)
