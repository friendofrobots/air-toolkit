from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Count, Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import json
from toolkit.models import Entity, Link, PMI

def home(request, template_name="air_explorer/home.html"):
    if request.user.is_authenticated() and request.user.profile.exists():
        profile = request.user.profile.all()[0]
        if not profile.downloadStatus.exists() or profile.downloadStatus.all()[0].stage < 4:
            return HttpResponseRedirect('/download/')
        ready = True
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

def likes(request, startsWith=None, page=1, template_name="air_explorer/likes.html"):
    if request.user.is_authenticated():
        profile = request.user.profile.all()[0]
        if not profile.downloadStatus.exists() or profile.downloadStatus.all()[0].stage < 4:
            return HttpResponseRedirect('/download/')
        if startsWith == None:
            startsWith = 'a'
        objects = Entity.objects.filter(owner=profile,linksTo__relation="likes").distinct()
        likes = objects.annotate(entity_activity=Count('linksTo'))
        if startsWith == u'~':
            likes = likes.filter(entity_activity__gt=1,name__iregex=r'\A\W').order_by('name')
        else:
            likes = likes.filter(entity_activity__gt=1,name__istartswith=startsWith).order_by('name')
        paginator = Paginator(likes,25)
        try:
            like_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            like_page = paginator.page(paginator.num_pages)
        return render_to_response(template_name, {
                'startsWith': startsWith,
                'likes' : like_page,
                }, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')

def pmivector(request, fbid):
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
