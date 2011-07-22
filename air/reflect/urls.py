from django.conf.urls.defaults import *

urlpatterns = patterns('reflect.views',
    url(r'^categories/(\d+)$', 'categories', name='categories'),
    url(r'^categories/$', 'categories', name='categories'),
    url(r'^profile/(\d+)$', 'profile', name='profile'),
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^friends/$', 'friends', name='friends'),
    url(r'^$', 'home', name='home'),
)
