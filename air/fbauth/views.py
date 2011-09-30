from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

import urllib, urllib2, cgi, facebook
from fbauth.models import FBLogin

authorize_url = 'https://graph.facebook.com/oauth/authorize'
access_token_url = 'https://graph.facebook.com/oauth/access_token'

"""
I need to figure out how to do this by popping up a new window or something.
That would make the flow much nicer and less dependent on the toolkit.
"""

def fblogin(request, redirectTo='explore:home'):
    args = dict(client_id=settings.FB_ID,
                redirect_uri='http://'+request.get_host()+request.path,
                )
    if request.GET.__contains__("code"):
        args["client_secret"] = settings.FB_SECRET
        args["code"] = request.GET.get("code")
        response = cgi.parse_qs(urllib2.urlopen(
                access_token_url + "?" +
                urllib.urlencode(args)).read())
        access_token = response["access_token"][-1]

        # Download the user fblogin
        graph = facebook.GraphAPI(access_token)
        me = graph.get_object('me')

        try:
            fblogin = FBLogin.objects.get(fbid=me['id'])
            fblogin.user.backend = 'django.contrib.auth.backends.ModelBackend'
            fblogin.user.save()
            fblogin.access_token = access_token
            fblogin.save()
            user = fblogin.user
            if redirectTo == 'facebook' or redirectTo == 'facebook/':
                redirectTo = 'context:home'
        except FBLogin.DoesNotExist:
            user = User.objects.create_user(me['id'],
                                            me['id']+'@facebook.com',
                                            access_token)
            fblogin = FBLogin.objects.create(
                user=user,
                fbid=me['id'],
                name=me['name'],
                access_token=access_token,
                )
            user = authenticate(username=fblogin.user.username,
                                password=access_token)

        login(request, user)

        return redirect('toolkit:newUser_redirect', redirectTo)
    elif request.GET.__contains__("error"):
        raise Exception("got an error from facebook")
        return render_to_response("fbauth/login.html", {
                "error":request.GET.get("error"),
                }, context_instance=RequestContext(request))
    else:
        args['scope'] = settings.FB_PERMS
        return HttpResponseRedirect(authorize_url + "?" +
                                    urllib.urlencode(args))

def fblogout(request,redirectTo="explore:home"):
    logout(request)
    return redirect(redirectTo)
