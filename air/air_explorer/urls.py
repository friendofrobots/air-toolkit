from django.conf.urls.defaults import *

urlpatterns = patterns('air_explorer.views',
    url(r'^friends/$', 'friends', name='friends'),
    url(r'^likes/$', 'likes', name='likes'),
    url(r'^likes/(\S+)/$', 'likes', name='likes_start'),
    url(r'^likes/(\S+)/(\d+)$', 'likes', name='likes_page'),
    url(r'^category/add/(\w+)$', 'addSeed', name='addSeed'),
    url(r'^category/delete/(\w+)$', 'deleteSeed', name='deleteSeed'),
    url(r'^category/status/$', 'categoryStatus', name='categoryStatus'),
    url(r'^category/$', 'categories', name='categories'),
    url(r'^category/(\d+)$', 'category', name='category'),
    url(r'^category/(\d+)/(\d+)$', 'category', name='category_page'),
    url(r'^$', 'home', name='home'),
)
