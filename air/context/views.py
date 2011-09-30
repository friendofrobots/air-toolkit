from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator, InvalidPage, EmptyPage

import json
from toolkit.models import *

def home(request, template_name="context/home.html"):
    """
    Home Page
    Download data if data does not exist
    After download, two big buttons
      one for filtering friends
      other for finding individual objects
    """
    if request.user.is_authenticated():
        profile = request.user.profile
        categories = Category.objects.filter(owner=profile).order_by('-last_updated')
        unread = categories.filter(unread=True)
    else:
        return redirect('auth:login_redirect','context:home')
    return render_to_response(template_name, {
            'profile' : profile,
            'categories' : categories,
            'unread' : unread,
            }, context_instance=RequestContext(request))

def friends(request, template_name="context/friends.html"):
    """
    For finding groups of friends.
    Should be able to filter and select with AJAX.
    """
    if request.user.is_authenticated():
        profile = request.user.profile
        friends = profile.getActivePeople().order_by('name','fbid')
        filters = []
        for relation in PersonProperty.RELATIONS:
            properties = PersonProperty.objects.filter(owner=profile,
                                                       relation=relation[0],
                                                       people__in=friends).distinct()
            ordered = properties.annotate(activity=Count('people')).order_by('-activity','id')
            filters.append((relation,[prop for prop in ordered]))

        toplikes = profile.getActivePages().annotate(activity=Count('likedBy')).order_by('-activity','fbid')[:16]

        categories = Category.objects.filter(owner=profile).order_by('-last_updated')
        unread = categories.filter(unread=True)
    else:
        return redirect('context:home')
    return render_to_response(template_name, {
            'friends' : friends,
            'filters' : filters,
            'toplikes' : toplikes,
            'categories' : categories,
            'unread' : unread,
            }, context_instance=RequestContext(request))

def filtered_friends(request):
    """
    First, apply active filters.
    Second, count filters for results
    """
    if request.user.is_authenticated():
        profile = request.user.profile
        if request.method == "GET":
            filtered_people = profile.getActivePeople().order_by('name','fbid')
            filters = dict([(relation[0],[]) for relation in PersonProperty.RELATIONS])
            for prop_id in request.GET.getlist('filters[]'):
                filtered_people = filtered_people.filter(properties=prop_id)
            for like_id in request.GET.getlist('likes[]'):
                filtered_people = filtered_people.filter(likes=like_id)

            new_filters = {}
            for relation in PersonProperty.RELATIONS:
                properties = PersonProperty.objects.filter(owner=profile,
                                                           relation=relation[0],
                                                           people__in=filtered_people).distinct()
                props = properties.annotate(new_activity=Count('people')).order_by('-new_activity','id')
                new_filters[relation[0]] = [[prop.id,prop.name,prop.new_activity] for prop in props]

            likes = Page.objects.filter(owner=profile,
                                        likedBy__in=filtered_people).distinct()
            toplikes = [[like.id,like.name,like.new_activity] for like in 
                        likes.annotate(new_activity=Count('likedBy')).order_by('-new_activity','fbid')[:16]]
            response_data = {
                'people': [[x.id, x.name, x.fbid] for x in filtered_people],
                'filters': new_filters,
                'likes': toplikes,
                }
        else:
            response_data = {
                'error' : 'must be GET request'
                }
    else:
        response_data = {
            'error' : 'user must be logged in'
            }
    return HttpResponse(json.dumps(response_data), mimetype='application/json')

def pages(request, template_name="context/pages.html"):
    """
    Find individual pages
    Search interface with autocomplete
    """
    if request.user.is_authenticated():
        profile = request.user.profile
        # Top active_pages
        pages = profile.getActivePages().order_by('-activity')
        categories = Category.objects.filter(owner=profile).order_by('-last_updated')
        unread = categories.filter(unread=True)
    else:
        return redirect('context:home')
    return render_to_response(template_name, {
            'toppages' : pages[:12],
            'categories' : categories,
            'unread' : unread,
            }, context_instance=RequestContext(request))

def page_lookup(request):
    """
    Let's try returning a result from name__istartswith=query, then ends with
    name__icontains=query,name__not__in=otherresult
    """
    if request.user.is_authenticated():
        profile = request.user.profile
        if request.method == "GET":
            if request.GET.has_key('query'):
                query = request.GET.get('query')
                pages = profile.getActivePages().annotate(activity=Count('likedBy'))
                starts = pages.filter(name__istartswith=query).order_by('-activity')
                contains = pages.filter(name__icontains=query).order_by('-activity')
                results = list(starts)
                results.extend(contains.exclude(name__istartswith=query))
                
                page = int(request.GET.get('page',1))
                response_data = {
                    'query':query,
                    'results': [[x.id,
                                 x.name,
                                 x.fbid,
                                 x.category,
                                 [y.name for y in x.likedBy.all()[:12]]] for x in results[12*(page-1):12*page]]
                    }
            else:
                response_data = {
                    'error' : 'no query'
                    }
        else:
            response_data = {
                'error' : 'must be GET request'
                }
    else:
        response_data = {
            'error' : 'user must be logged in'
            }
    return HttpResponse(json.dumps(response_data), mimetype='application/json')

def category(request, category_id=None, template_name="context/category.html"):
    """
    Display category status if calculating
    else display category and friends
    """
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
        scores = category.scores.filter(value__gt=0).order_by('-value','page__fbid')
        paginator = Paginator(scores,24)
        score_page = paginator.page(1)

        try:
            topmembers = category.memberships.order_by('-value')[:6]
            people = category.group.people.order_by('name')
        except PersonGroup.DoesNotExist:
            topmembers = category.memberships.order_by('-value')[:6]
            people = None

        categories = Category.objects.filter(owner=profile).order_by('-last_updated')
        unread = categories.filter(unread=True)
    return render_to_response(template_name, {
            'category' : category,
            'score_page' : score_page,
            'people' : people,
            'topmembers' : topmembers,
            'categories' : categories,
            'unread' : unread,
            }, context_instance=RequestContext(request))

def category_more(request, category_id=None, page_num=1):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
        scores = category.scores.filter(value__gt=0).order_by('-value','page__fbid')
        paginator = Paginator(scores,24)
        try:
            score_page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            score_page = paginator.page(paginator.num_pages)

        response_data = {
            'pages' : [[x.page.id, x.page.name, x.page.fbid] for x in score_page.object_list],
            'next_page' : score_page.next_page_number if score_page.has_next() else None,
            }
    else:
        response_data = {
            'error' : 'user must be logged in'
            }

def browse(request):
    categories = Category.objects.filter(owner=profile).order_by('-last_updated')
    unread = categories.filter(unread=True)
    return render_to_response(template_name, {
            'categories' : categories,
            'unread' : unread,
            }, context_instance=RequestContext(request))
