from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User

import pickle, types, json
from toolkit.models import Data
from fbauth.models import Profile

def pmi_all(request, greg=True, template_name="toolkit/pmi.html"):
    if greg:
        data = User.objects.get(pk=1).profile_set.all()[0].data_set.all()[0]
    if request.user.is_authenticated():
        data = request.user.profile_set.all()[0].data_set.all()[0]
    # These may not be here yet, check for that
    print 'loading json'
    pmi = json.loads(data.pmi_matrix)
    graph = json.loads(data.filtered_graph)
    print 'rendering html'
    print pmi
    return render_to_response(template_name, {
                "objects" : pmi.keys()[:100],
                "lookup" : lookup,
                }, context_instance=RequestContext(request))

def getPmiVector(request, fbid):
    """
    load pmi matrix
    vector = pmi[fbid]
    filter our 0s
    """
    return HttpResponse(json.dumps(VECTOR),mimetype="application/json")

# OLD STUFF

# Choose a Profile/Page or Categories
def explore(request, template_name="explore/explore.html"):
    if not request.user.is_authenticated():
        return render_to_response(template_name, {
                "profiles": [],
                "pages_by_category": {},
                }, context_instance=RequestContext(request))
    else:
        toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
        pages_by_category = {}
        for page in toolkit.getType('page'):
            cat = page.getLink('category')
            if not cat:
                continue
            if cat not in pages_by_category:
                pages_by_category[cat] = []
            pages_by_category[cat].append(page)
        return render_to_response(template_name, {
                "profiles": toolkit.getType('profile'),
                "pages_by_category": pages_by_category,
                }, context_instance=RequestContext(request))

# Given profile, choose action
def object(request, id, template_name="explore/object.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    fbobject = toolkit.getById(id)
    properties = {}
    for link in fbobject.links:
        if type(fbobject.links[link]) == types.ListType:
            properties[link] = [toolkit.getById(l[0]) for l in fbobject.links[link]]
        else:
            properties[link] = [toolkit.getById(fbobject.links[link][0])]
    return render_to_response(template_name, {
        "object": fbobject,
        "properties": properties,
        "topSim": toolkit.topSimilarity(id),
        "topPre": toolkit.topPredictions(id),
        }, context_instance=RequestContext(request))

# Choose what to compare it to
def compareTo(request, id, template_name="explore/compareto.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "object": toolkit.getById(id),
        "profiles": toolkit.getType('profile'),
        "pages": toolkit.getType('page'),
        }, context_instance=RequestContext(request))

# Calculate similarity
def compare(request, id1, id2, template_name="explore/compare.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    return render_to_response(template_name, {
        "object1": toolkit.getById(id1),
        "object2": toolkit.getById(id2),
        "weight": toolkit.compare(id1,id2),
        }, context_instance=RequestContext(request))

# Choose items for category
def categories(request, template_name="explore/categories.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    pages_by_category = {}
    for page in toolkit.getType('page'):
        cat = page.getLink('category')
        if not cat:
            continue
        if cat not in pages_by_category:
            pages_by_category[cat] = []
        pages_by_category[cat].append(page)
    profiles = toolkit.getType('profile')
    for profile in profiles:
        profile.name = "User"+str(profile.id[-4:])
    return render_to_response(template_name, {
        "profiles": toolkit.getType('profile'),
        "pages_by_category": pages_by_category,
        }, context_instance=RequestContext(request))

# Show category features
def category(request, template_name="explore/category.html"):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('categories'))
    ids = request.POST.getlist('object')
    if len(ids) < 1:
        return HttpResponseRedirect(reverse('categories'))
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    category = toolkit.createCategory(ids)
    objects = [toolkit.getById(id) for id in ids]
    for o in objects:
        o.name = "User"+str(o.id[-4:])
        o.properties = {}
        for link in o.links:
            if link == 'like' or link == 'likes':
                continue
            if type(o.links[link]) == types.ListType:
                o.properties[link] = [toolkit.getById(l[0]) for l in o.links[link]]
            else:
                o.properties[link] = [toolkit.getById(o.links[link][0])]
    return render_to_response(template_name, {
        "objects": objects,
        "topFea": toolkit.categoryTopFeatures(category),
        "topSim": toolkit.categoryTopSimilarity(category),
        "topPre": toolkit.categoryTopPredictions(category),
        }, context_instance=RequestContext(request))

def projection(request, id1, id2, thresh=.005, template_name="explore/projection.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    profile1 = toolkit.getById(id1)
    properties = {}
    for link in profile1.links:
        if link == 'likes' or link == 'like':
            continue
        if type(profile1.links[link]) == types.ListType:
            properties[link] = [toolkit.getById(l[0]) for l in profile1.links[link]]
        else:
            properties[link] = [toolkit.getById(profile1.links[link][0])]
    profile1likes = [toolkit.getById(l[0]) for l in profile1.links['likes']]
    profile2 = toolkit.getById(id2)
    profile2likes = [toolkit.getById(l[0]) for l in profile2.links['likes']]

    #anonymizing it
    profile1.name = "User"+str(profile1.id[-4:])
    profile2.name = "User"+str(profile2.id[-4:])
    return render_to_response(template_name, {
        "profile1": profile1,
        "profile1properties": properties,
        "profile1likes": profile1likes,
        "profile2": profile2,
        "profile2likes": profile2likes,
        "projected_likes": toolkit.project_prediction(id1,id2,thresh=thresh),
        }, context_instance=RequestContext(request))

def add(request, template_name="explore/add.html"):
    toolkit = airtoolkit.AIRToolkit(FBGraph.objects.all()[0].filename)
    if request.method == 'POST':
        keylinks = [('gender',(request.POST.get('gender'),'hasProperty',1)),
                ('hometown',(request.POST.get('hometown'),'isFrom',1))]
        keylinks.extend([('like',(likeid,'likes',1)) for likeid in request.POST.getlist('likes')])
        profileName = request.POST.get('name')
        profile = toolkit.createProfile("FBGraphAltered",profileName,keylinks)
        graphpointer = FBGraph.objects.all()[0]
        graphpointer.filename = "FBGraphAltered.pickle"
        graphpointer.altered = True
        graphpointer.save()
        return HttpResponseRedirect(reverse('object',args=[profile.id]))
    likes_by_category = {}
    for like in toolkit.getType('page'):
        cat = like.getLink('category')
        if not cat or cat == 'Gender':
            continue
        if cat not in likes_by_category:
            likes_by_category[cat] = []
        likes_by_category[cat].append(like)
    return render_to_response(template_name, {
        "hometowns": [x for x in toolkit.getType('page') if x.getLink('category') == 'City'],
        "likes_by_category": likes_by_category,
        }, context_instance=RequestContext(request))

def reset(request):
    graphpointer = FBGraph.objects.all()[0]
    graphpointer.filename = "FBGraph.pickle"
    graphpointer.altered = False
    graphpointer.save()
    return HttpResponseRedirect(reverse('explore'))
