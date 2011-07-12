from django.conf.urls.defaults import *

urlpatterns = patterns('survey.views',
    url(r'^(\d+)/friends/(\d+)$', 'friends', name='s_friends_page'),
    url(r'^(\d+)/friends/$', 'friends', name='s_friends_start'),
    url(r'^(\d+)/profile/(\d+)$', 'profile', name='s_profile'),
    url(r'^(\d+)/profile/$', 'profile', name='s_userprofile'),
    url(r'^(\d+)/like/(\d+)$', 'like', name='s_like'),
    url(r'^(\d+)/(\d+)$', 'category', name='s_category_page'),
    url(r'^(\d+)/$', 'category', name='s_category_start'),
    url(r'^$', 'home', name='s_home'),
)
