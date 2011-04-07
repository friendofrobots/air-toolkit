from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

import urllib, urllib2, cgi, facebook
from fbauth.models import Profile

authorize_url = 'https://graph.facebook.com/oauth/authorize'
access_token_url = 'https://graph.facebook.com/oauth/access_token'

def login(request):
    args = dict(client_id=settings.FB_ID,
                redirect_uri='https://127.0.0.1:8000/login',#request.build_absolute_uri(),
                scope=settings.FB_PERMS,
                )
    if request.GET.__contains__("code"):
        args["client_secret"] = settings.FB_SECRET
        args["code"] = request.GET.get("code")
        response = cgi.parse_qs(urllib2.urlopen(
                access_token_url + "?" +
                urllib.urlencode(args)).read())
        access_token = response["access_token"][-1]
        
        # Download the user profile
        graph = facebook.GraphAPI(access_token)
        me = graph.get_object('me')

        try:
            user = User.objects.get(username=me['id'])
        except User.DoesNotExist:
            user = User.objects.create_user(me['id'],
                                            '%s@facebook.com' % me['id'],
                                            access_token)
            user = User.objects.get_or_create(username=me['id'])
            profile = Profile()
            profile.user = user
            profile.access_token = access_token
            profile.save()

        return HttpResponseRedirect('/')
    elif request.GET.__contains__("error"):
        return render_to_response("fbauth/login.html", {
                "error":request.GET.get("error"),
                }, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(authorize_url + "?" +
                                    urllib.urlencode(args))

@login_required
def logout(request):
    logout(request)
    return HttpResponseRedirect('/')
