from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Count, Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404
import json
from toolkit.models import Entity, Link, PMI
from toolkit import tasks
from celery.result import AsyncResult

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
        return HttpResponseRedirect('/')
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

        if request.method == 'POST':
            if not profile.activeCategory:
                category = Category.objects.create(owner=profile,
                                                   name=request.POST.get('name','tempcategoryname'),
                                                   active=profile)
                if category.name == 'tempcategoryname':
                    category.name = 'category'+str(category.id)
                    category.save()
        else:
            category = None
        return render_to_response(template_name, {
                'startsWith': startsWith,
                'likes' : like_page,
                'category' : category,
                }, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')

def addSeed(request, fbid):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile.all()[0]
            if profile.activeCategory:
                seed = Entity.objects.get(fbid=fbid)
                profile.activeCategory.seeds.add(seed)
                response_datat = {
                    "id":fbid,
                    "name":name,
                    }
            else:
                response_data = {
                    "error":"start a category first"
                    }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def deleteSeed(request, fbid):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile.all()[0]
            if profile.activeCategory:
                seed = Entity.objects.get(fbid=fbid)
                profile.activeCategory.seeds.remove(seed)
                response_data = {
                    "id":fbid,
                    "name":name,
                    }
            else:
                response_data = {
                    "error":"start a category first"
                    }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def categories(request, template_name="air_explorer/categories.html"):
    if request.user.is_authenticated():
        profile = request.user.profile.all()[0]
        if profile.activeCategory:
            active = profile.activeCategory
        else:
            active = None
        if request.method == 'POST':
            objects = Entity.objects.filter(owner=profile,linksTo__relation="likes").distinct()
            likes = objects.annotate(entity_activity=Count('linksTo')).filter(entity_activity__gt=1)
            for like in likes:
                CategoryScore.create(owner=profile,
                                     category=active,
                                     entity=like)
            result = tasks.createCategory.delay(profile.fbid,
                                                active.id,
                                                request.POST.get('threshold',0.5),
                                                request.POST.get('decayrate',0.5))
            active.task_id = result.task_id
            active.save()
        categories = Category.objects.filter(owner=profile)
    else:
        return HttpResponseRedirect('/')
    return render_to_response(template_name, {
            'categories' : categories,
            'active' : active,
            }, context_instance=RequestContext(request))

def category(request, category_id, page=1, template_name="air_explorer/category.html"):
    if request.user.is_authenticated():
        profile = request.user.profile.all()[0]
        category = get_object_or_404(Category,id=category_id)
        scores = category.scores.all().order_by('-value')
        paginator = Paginator(scores,25)
        try:
            score_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            score_page = paginator.page(paginator.num_pages)
    else:
        return HttpResponseRedirect('/')
    return render_to_response(template_name, {
            'category' : category,
            'scores' : score_page,
            }, context_instance=RequestContext(request))
    
def categoryStatus(request):
    if request.user.is_authenticated():
        profile = request.user.profile.all()[0]
        if profile.activeCategory:
            if profile.activeCategory.task_id:
                result = AsyncResult(status.task_id)
                response_data = {
                    "stage":1,
                    "state": result.state,
                    "id": profile.activeCategory.id,
                    "name": profile.activeCategory.name,
                    }
            else:
                response_data = {
                    "stage":2,
                    "state": "completed",
                    "id": profile.activeCategory.id,
                    "name": profile.activeCategory.name,
                    }
        else:
            response_data = {
                "error" : "no active category"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

