from django.conf.urls.defaults import *
from django.contrib import admin
import os.path
admin.autodiscover()
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "media")

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^auth/', include('fbauth.urls', namespace='auth')),
    (r'^t/', include('toolkit.urls', namespace='toolkit')),
    (r'^reflect/', include('reflect.urls', namespace='reflect')),
    (r'^survey/', include('survey.urls', namespace='survey')),
    (r'^context/', include('context.urls', namespace='context')),
    (r'^', include('air_explorer.urls', namespace='explore')),
)
