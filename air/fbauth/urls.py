from django.conf.urls.defaults import *

urlpatterns = patterns('fbauth.views',
    url(r'^login/?$', 'login', name='login'),
    url(r'^logout/?$', 'logout', name='logout'),
    url(r'^login/authenticated/?$', 'authenticated', name='authenticated'),
)
