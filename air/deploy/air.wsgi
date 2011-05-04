import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir
addsitedir(abspath(join(dirname(__file__), "../../lib/python2.6/site-packages"))
sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "air.settings"

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
