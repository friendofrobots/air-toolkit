from django.shortcuts import render_to_response, get_object_or_404

from toolkit.models import Entity, Link, PMI

def home(request, template_name="toolkit/downloading.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))

def friends(request, template_name="toolkit/friends.html"):
    friends = Entity.objects.filter(linksFrom__relation="likes").distinct()
    return render_to_response(template_name, {
            'friends' : friends,
            }, context_instance=RequestContext(request))

def likes(request, template_name="toolkit/friends.html"):
    likes = Link.objects.annotate(entity_activity=Count('toEntity__linksTo')).filter(entity_activity__gt=1,relation="likes")
    return render_to_response(template_name, {
            'friends' : friends,
            }, context_instance=RequestContext(request))
