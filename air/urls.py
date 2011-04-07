from django.conf.urls.defaults import *
from django.contrib import admin
import os.path
admin.autodiscover()
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "media")

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': MEDIA_ROOT}),

    (r'^login/', include('fbauth.urls')),
    (r'^$', include('air.urls')),
)
