from django.conf.urls.defaults import *

urlpatterns = patterns('reflect.views',
    url(r'^status/$', 'status', name='r_status'),
    url(r'^categories/$', 'categories', name='r_categories'),
    url(r'^profile/$', 'profile', name='r_profile'),
    url(r'^friends/$', 'friends', name='r_friends'),
    url(r'^$', 'home', name='r_home'),
)
