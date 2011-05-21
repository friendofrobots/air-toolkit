from django.conf.urls.defaults import *

urlpatterns = patterns('fbauth.views',
    url(r'^logout/$', 'fblogout', name='logout'),
    url(r'^login/(\S+)$', 'fblogin', name='login_redirect'),
    url(r'^login/$', 'fblogin', name='login'),
)
