from django.conf.urls.defaults import *

urlpatterns = patterns('air_explorer.views',
    url(r'^friends/$', 'friends', name='friends'),
    url(r'^friends/browse/$', 'friends', name='friends_start'),
    url(r'^friends/browse/(\d+)$', 'friends', name='friends_page'),
    url(r'^friends/(\d+)/$', 'friend', name='friend_start'),
    url(r'^friends/(\d+)/(\d+)$', 'friend', name='friend_page'),
    url(r'^likes/$', 'likes', name='likes'),
    url(r'^likes/browse/(\S+)/$', 'likes', name='likes_start'),
    url(r'^likes/browse/(\S+)/(\d+)$', 'likes', name='likes_page'),
    url(r'^likes/pmis/(\d+)/$', 'like', name='like_start'),
    url(r'^likes/pmis/(\d+)/(\d+)$', 'like', name='like_page'),
    url(r'^category/$', 'categories', name='categories'),
    url(r'^category/(\d+)/$', 'category', name='category_start'),
    url(r'^category/(\d+)/(\d+)$', 'category', name='category_page'),
    url(r'^download/$', 'download', name='download'),
    url(r'^$', 'home', name='home'),
)
