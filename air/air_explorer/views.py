from django.shortcuts import render_to_response, get_object_or_404
import json
from toolkit.models import Entity, Link, PMI

def home(request, template_name="toolkit/downloading.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))

def friends(request, template_name="toolkit/friends.html"):
    if request.user.is_authenticated():
        friends = Entity.objects.filter(owner=request.user.profile,linksFrom__relation="likes").distinct()
    else:
        friends = []
    return render_to_response(template_name, {
            'friends' : friends,
            }, context_instance=RequestContext(request))

def likes(request, template_name="toolkit/likes.html"):
    if request.user.is_authenticated():
        likes = Link.objects.annotate(entity_activity=Count('toEntity__linksTo'))
        .filter(owner.request.user.profile,entity_activity__gt=1,relation="likes")
    return render_to_response(template_name, {
            'friends' : friends,
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
