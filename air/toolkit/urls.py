from django.conf.urls.defaults import *

urlpatterns = patterns('air.views',
    url(r'^p/(\w+)$', 'object', name='object'),
    url(r'^compare/(\w+)$', 'compareTo', name='compareTo'),
    url(r'^compare/(\w+)/(\w+)$', 'compare', name='compare'),
    url(r'^categories/$', 'categories', name='categories'),
    url(r'^category/$', 'category', name='category'),
    url(r'^projection/(\w+)/(\w+)$', 'projection', name='projection'),
    url(r'^add/$', 'add', name='add'),
    url(r'^reset/$', 'reset', name='reset'),
    url(r'^$', 'explore', name='explore'),
)
