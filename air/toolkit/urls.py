from django.conf.urls.defaults import *

urlpatterns = patterns('toolkit.views',
    url(r'^p/(\w+)$', 'getPmiVector', name='pmiVector'),
    url(r'^g/(\w+)$','getPmiVector',name='g_pmiVector',kwargs={'greg':True}),
    url(r'^g/$','pmi_all',name='g_pmi',kwargs={'greg':True}),
    url(r'^$', 'pmi_all', name='pmi_all'),
)
