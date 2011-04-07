from django.conf.urls.defaults import *

urlpatterns = patterns('fbauth.views',
    url(r'^logout/?$', 'logout', name='logout'),
    url(r'^$', 'login', name='login'),
)
