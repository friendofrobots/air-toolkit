from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
import json
from toolkit.models import Entity, Link, PMI

def home(request, template_name="air_explorer/home.html"):
    if request.user.is_authenticated():
        profile = request.user.profile.all()[0]
        ready = profile.downloadStatus.exists() and profile.downloadStatus.all()[0].stage == 4
    else:
        ready = False
    return render_to_response(template_name, {
            'ready' : ready,
            }, context_instance=RequestContext(request))

def friends(request, template_name="air_explorer/friends.html"):
    if request.user.is_authenticated():
        friends = Entity.objects.filter(owner=request.user.profile,linksFrom__relation="likes").distinct()
    else:
        friends = []
    return render_to_response(template_name, {
            'friends' : friends,
            }, context_instance=RequestContext(request))

def likes(request, startsWith, template_name="air_explorer/likes.html"):
    if request.user.is_authenticated():
        profile = request.user.profile.all()[0]
        if not profile.downloadStatus.exists() or profile.downloadStatus.stage != 4:
            return HttpResponseRedirect('/d/')
        links = Link.objects.annotate(entity_activity=Count('toEntity__linksTo'))
        likes = links.filter(owner.request.user.profile,entity_activity__gt=1,relation="likes")
        if startsWith:
            likes = likes.filter(name__istartswith=startsWith)
    return render_to_response(template_name, {
            'likes' : likes,
            }, context_instance=RequestContext(request))

def getPmiVector(request, fbid):
    if request.user.is_authenticated():
        vector = [{
                'fromName':pmi.fromEntity.name,
                'fromId':pmi.fromEntity.fbid,
                'toName':pmi.toEntity.name,
                'toId':pmi.toEntity.fbid,
                'value':pmi.value,
                } for pmi
                  in PMI.objects.filter(owner=request.user.profile,
                                        fromEntity=Entity.objects.get(owner=request.user.profile,fbid=fbid))
                  .order_by('-value')]
    else:
        vector = []
    return HttpResponse(json.dumps(vector),mimetype="application/json")
