from django.conf.urls.defaults import *

urlpatterns = patterns('survey.views',
    url(r'^(\d+)/friends/(\d+)$', 'friends', name='friends_page'),
    url(r'^(\d+)/friends/$', 'friends', name='friends_start'),
    url(r'^(\d+)/profile/(\d+)$', 'profile', name='profile'),
    url(r'^(\d+)/profile/$', 'profile', name='userprofile'),
    url(r'^(\d+)/like/(\d+)$', 'like', name='like'),
    url(r'^(\d+)/(\d+)$', 'category', name='category_page'),
    url(r'^(\d+)/$', 'category', name='category_start'),
    url(r'^$', 'home', name='home'),
)
