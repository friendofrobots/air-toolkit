from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Count, Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, redirect
import json
from toolkit.models import Entity, Link, PMI, Category, CategoryScore
from toolkit.forms import CategoryCreateForm
from toolkit import tasks
from celery.result import AsyncResult

def home(request, template_name="air_explorer/home.html"):
    if request.user.is_authenticated():
        try:
            status = request.user.profile.downloadStatus
            if status.stage < 4:
                return redirect('download')
            ready = True
        except:
            return redirect('download')
    else:
        ready = False
    return render_to_response(template_name, {
            'path' : request.path,
            'ready' : ready,
            }, context_instance=RequestContext(request))

def download(request, template_name="air_explorer/download.html"):
    if request.user.is_authenticated():
        try:
            stage = request.user.profile.downloadStatus.stage
        except:
            stage = None
    else:
        return redirect('home')
    return render_to_response(template_name, {
            'path' : request.path,
            "stage" : stage,
            }, context_instance=RequestContext(request))

def friends(request, template_name="air_explorer/friends.html"):
    if request.user.is_authenticated():
        friends = Entity.objects.filter(owner=request.user.profile,linksFrom__relation="likes").distinct()
    else:
        return redirect('home')
    return render_to_response(template_name, {
            'path' : request.path,
            'friends' : friends,
            }, context_instance=RequestContext(request))

def likes(request, startsWith=None, page=1, template_name="air_explorer/likes.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        try:
            status = profile.downloadStatus
            if status.stage <4:
                return redirect('download')
        except:
            return redirect('download')
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

        try:
            active = profile.activeCategory
            createForm = CategoryCreateForm(initial={'category_id' : active.id,
                                                     'startvalue' : active.startvalue,
                                                     'threshold' : active.threshold,
                                                     'decayrate' : active.decayrate,})
        except Category.DoesNotExist:
            active = None
            createForm = None
        return render_to_response(template_name, {
                'path' : request.path,
                'startsWith': startsWith,
                'likes' : like_page,
                'active' : active,
                'createForm' : createForm,
                }, context_instance=RequestContext(request))
    else:
        return redirect('home')

def categories(request, template_name="air_explorer/categories.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        try:
            active = profile.activeCategory
        except Category.DoesNotExist:
            active = None
        categories = Category.objects.filter(owner=profile).order_by('-id')
    else:
        return redirect('home')
    return render_to_response(template_name, {
            'path' : request.path,
            'categories' : categories,
            'active' : active,
            }, context_instance=RequestContext(request))

def category(request, category_id, page=1, template_name="air_explorer/category.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
        scores = category.scores.filter(value__gt=0).order_by('-value','entity__fbid')
        paginator = Paginator(scores,24)
        try:
            score_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            score_page = paginator.page(paginator.num_pages)
    else:
        return redirect('home')
    return render_to_response(template_name, {
            'path' : request.path,
            'category' : category,
            'scores' : score_page,
            }, context_instance=RequestContext(request))
