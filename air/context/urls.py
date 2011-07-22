from django.conf.urls.defaults import *

urlpatterns = patterns('context.views',
    url(r'^browse/$', 'browse', name='browse'),
    url(r'^friends/$', 'friends', name='friends'),
    url(r'^friends/filtered$', 'filtered_friends', name='filtered_friends'),
    url(r'^pages/$', 'pages', name='pages'),
    url(r'^pages/lookup/$', 'page_lookup', name='page_lookup'),
    url(r'^category/(\d+)/(\d+)$', 'category_more', name='category_more'),
    url(r'^category/(\d+)$', 'category', name='category'),
    url(r'^$', 'home', name='home'),
)
