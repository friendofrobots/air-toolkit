from django.conf.urls.defaults import *

urlpatterns = patterns('air_explorer.views',
    url(r'^friends/$', 'friends', name='friends'),
    url(r'^likes/(w+)$', 'likes', name='likes'),
    url(r'^pmi/(w+)$', 'getPmiVector', name='pmivector'),
    url(r'^$', 'home', name='home'),
)
