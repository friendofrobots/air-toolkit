from django.conf.urls.defaults import *

urlpatterns = patterns('air_explorer.views',
    url(r'^friends/$', 'friends', name='friends'),
    url(r'^likes/$', 'likes', name='likes'),
    url(r'^likes/(\S+)/$', 'likes', name='likes'),
    url(r'^likes/(\S+)/(\d+)$', 'likes', name='likes'),
    url(r'^pmi/(\w+)$', 'pmivector', name='pmivector'),
    url(r'^$', 'home', name='home'),
)
