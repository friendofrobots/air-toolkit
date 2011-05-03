from django.conf.urls.defaults import *

urlpatterns = patterns('fbauth.views',
    url(r'^logout/$', 'fblogout', name='logout'),
    url(r'^login/$', 'fblogin', name='login'),
)
