from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Count, Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, redirect
import json
from toolkit.models import *
from toolkit.forms import CategoryCreateForm
from toolkit import tasks
from celery.result import AsyncResult

def home(request, template_name="air_explorer/home.html"):
    if request.user.is_authenticated():
        try:
            if request.user.profile.stage < 3:
                return redirect('explore:download')
            ready = True
        except:
            return redirect('explore:download')
    else:
        ready = False
    return render_to_response(template_name, {
            'path' : request.path,
            'ready' : ready,
            }, context_instance=RequestContext(request))

def download(request, template_name="air_explorer/download.html"):
    if request.user.is_authenticated():
        try:
            stage = request.user.profile.stage
        except:
            stage = None
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            "stage" : stage,
            }, context_instance=RequestContext(request))

def friends(request, page_num=1, template_name="air_explorer/friends.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        try:
            if profile.stage < 3:
                return redirect('explore:download')
        except:
            return redirect('explore:download')
        friends = Person.objects.filter(owner=profile).order_by('name')
        paginator = Paginator(friends,96)
        
        try:
            friend_page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            friend_page = paginator.page(paginator.num_pages)

        return render_to_response(template_name, {
                'path' : request.path,
                'paginate' : friend_page,
                }, context_instance=RequestContext(request))
    else:
        return redirect('explore:home')

def friend(request, person_id, page_num=1, template_name="air_explorer/friend.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        person = get_object_or_404(Person,id=person_id)
        memberships = person.categoryMembership.order_by('-value')[:12]
        try:
            active = profile.activeCategory
            createForm = CategoryCreateForm(initial={'category_id' : active.id,
                                                     'startvalue' : active.startvalue,
                                                     'threshold' : active.threshold,
                                                     'decayrate' : active.decayrate,})
            allowNew = False
        except Category.DoesNotExist:
            active = None
            createForm = None
            allowNew = True
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'friend' : person,
            'memberships' : memberships,
            'active' : active,
            'createForm' : createForm,
            'allowNew' : allowNew,
            }, context_instance=RequestContext(request))

def likes(request, startsWith=None, page_num=1, template_name="air_explorer/likes.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        try:
            if profile.stage < 3:
                return redirect('explore:download')
        except:
            return redirect('explore:download')
        if startsWith == None:
            startsWith = 'a'
        pages = profile.getActivePages()
        if startsWith == u'~':
            likes = pages.filter(name__iregex=r'\A\W').order_by('name','fbid')
        else:
            likes = pages.filter(name__istartswith=startsWith).order_by('name','fbid')
        paginator = Paginator(likes,24)
        
        try:
            like_page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            like_page = paginator.page(paginator.num_pages)

        try:
            active = profile.activeCategory
            createForm = CategoryCreateForm(initial={'category_id' : active.id,
                                                     'startvalue' : active.startvalue,
                                                     'threshold' : active.threshold,
                                                     'decayrate' : active.decayrate,})
            allowNew = False
        except Category.DoesNotExist:
            active = None
            createForm = None
            allowNew = True
        return render_to_response(template_name, {
                'path' : request.path,
                'startsWith': startsWith,
                'paginate' : like_page,
                'active' : active,
                'createForm' : createForm,
                'allowNew' : allowNew,
                }, context_instance=RequestContext(request))
    else:
        return redirect('explore:home')

def like(request, page_id, page_num=1, template_name="air_explorer/like.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        page = get_object_or_404(Page,id=page_id)
        paginator = Paginator(page.pmisFrom.order_by('-value','toPage__fbid'),24)
        try:
            pmi_page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            pmi_page = paginator.page(paginator.num_pages)

        try:
            active = profile.activeCategory
            createForm = CategoryCreateForm(initial={'category_id' : active.id,
                                                     'startvalue' : active.startvalue,
                                                     'threshold' : active.threshold,
                                                     'decayrate' : active.decayrate,})
            allowNew = False
        except Category.DoesNotExist:
            active = None
            createForm = None
            allowNew = True
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'like' : page,
            'paginate' : pmi_page,
            'active' : active,
            'createForm' : createForm,
            'allowNew' : allowNew,
            }, context_instance=RequestContext(request))

def categories(request, template_name="air_explorer/categories.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        categories = Category.objects.filter(owner=profile).order_by('-last_updated')

        try:
            active = profile.activeCategory
            createForm = CategoryCreateForm(initial={'category_id' : active.id,
                                                     'startvalue' : active.startvalue,
                                                     'threshold' : active.threshold,
                                                     'decayrate' : active.decayrate,})
            allowNew = False
        except Category.DoesNotExist:
            active = None
            createForm = None
            allowNew = True
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'categories' : categories,
            'active' : active,
            'createForm' : createForm,
            'allowNew' : allowNew,
            }, context_instance=RequestContext(request))

def category(request, category_id, page_num=1, template_name="air_explorer/category.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
        scores = category.scores.filter(value__gt=0).order_by('-value','page__fbid')
        paginator = Paginator(scores,24)
        try:
            score_page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            score_page = paginator.page(paginator.num_pages)
        memberships = category.memberships.order_by('-value')[:12]
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'category' : category,
            'paginate' : score_page,
            'memberships' : memberships,
            }, context_instance=RequestContext(request))

def category_raw(request, category_id, template_name="air_explorer/category_raw.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
        scores = category.scores.filter(page__likedBy__in=category.group.people.all()).distinct()
        act = scores.annotate(activity=Count('page__likedBy')).order_by('-activity','page__fbid')
        mult = 1./(1.*max(act,key=lambda x : x.activity).activity)

        paginator = Paginator(act,24)

        score_page = paginator.page(1)
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'category' : category,
            'score_page' : score_page,
            'mult' : mult,
            }, context_instance=RequestContext(request))
