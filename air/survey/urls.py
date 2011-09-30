from django.conf.urls.defaults import *

urlpatterns = patterns('survey.views',
    url(r'^post/(\d+)/(\w+)$', 'post_survey', name='post_survey'),
    url(r'^results/$', 'surveys', name='surveys'),
    url(r'^results/(\d+)/$', 'results', name='results'),
    url(r'^results/check/$', 'check', name='check'),
    url(r'^results/summary/$', 'summary', name='summary'),

    url(r'^(\d+)/friends/(\d+)$', 'friends', name='friends_page'),
    url(r'^(\d+)/friends/$', 'friends', name='friends_start'),
    url(r'^(\d+)/profile/(\d+)$', 'profile', name='profile'),
    url(r'^(\d+)/profile/$', 'profile', name='userprofile'),
    url(r'^(\d+)/like/(\d+)$', 'like', name='like'),
    url(r'^(\d+)/(\d+)$', 'category', name='category_page'),
    url(r'^(\d+)/$', 'category', name='category_start'),
    url(r'^$', 'home', name='home'),
)
