from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

import urllib, urllib2, cgi, facebook
from fbauth.models import Profile

authorize_url = 'https://graph.facebook.com/oauth/authorize'
access_token_url = 'https://graph.facebook.com/oauth/access_token'

def fblogin(request, redirect="/"):
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

        # Download the user profile
        graph = facebook.GraphAPI(access_token)
        me = graph.get_object('me')

        try:
            user = User.objects.get(username=me['id'])
            user.set_password(access_token)
            user.save()
            profile = user.profile
            profile.access_token = access_token
            profile.save()
        except User.DoesNotExist:
            user = User.objects.create_user(me['id'],
                                            me['id']+'@facebook.com',
                                            access_token)
            profile = Profile()
            profile.user = user
            profile.fbid = me['id']
            profile.name = me['name']
            profile.access_token = access_token
            profile.save()

        user = authenticate(username=me['id'],
                            password=access_token)
        login(request, user)

        return HttpResponseRedirect(redirect)
    elif request.GET.__contains__("error"):
        raise Exception("got an error from facebook")
        return render_to_response("fbauth/login.html", {
                "error":request.GET.get("error"),
                }, context_instance=RequestContext(request))
    else:
        args['scope'] = settings.FB_PERMS
        return HttpResponseRedirect(authorize_url + "?" +
                                    urllib.urlencode(args))

def fblogout(request):
    logout(request)
    return redirect('home')
