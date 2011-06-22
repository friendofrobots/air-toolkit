from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect

import json
from toolkit.models import Entity, Link, PMI, Category, CategoryScore

def home(request, template_name="reflect/home.html"):
    if request.user.is_authenticated():
        try:
            status = request.user.profile.downloadStatus
        except:
            status = None
    else:
        # This doesn't work, I need to figure out how to redirect properly
        return redirect('login_redirect','r_home')
    return render_to_response(template_name, {
            'status' : status,
            }, context_instance=RequestContext(request))

def categories(request, category_id=None, template_name="reflect/categories.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        categories = Category.objects.filter(owner=profile).order_by('id')
        if not category_id:
            category = categories[0]
        else:
            category = get_object_or_404(Category,id=category_id)
    else:
        return redirect('r_home')
    return render_to_response(template_name, {
            'category' : category,
            'categories' : categories,
            }, context_instance=RequestContext(request))    

def profile(request, entity_id=None, template_name="reflect/profile.html"):
    if request.user.is_authenticated():
        """ I need categories of objects, sorted.
       Then I need to either determine the category for each object
        or put that off and do it by ajax. I'm thinking about pre-calculating.
        """
        profile = request.user.profile
        if not entity_id:
            entity = Entity.objects.get(owner=profile,fbid=profile.fbid)
        else:
            entity = get_object_or_404(Entity,id=entity_id)
        categories = Category.objects.filter(owner=profile).order_by('id')
        likeLinks = entity.likes()
        likes = Entity.objects.filter(linksTo__in=likeLinks).distinct()

        fbcategories = {}
        for like in likes:
            fbcat_link = like.linksFrom.filter(relation="category")[0]
            if fbcat_link.toEntity.name not in fbcategories:
                fbcategories[fbcat_link.toEntity.name] = []
            fbcategories[fbcat_link.toEntity.name].append(like)
        facebook_categories = fbcategories.items()
        facebook_categories.sort(key=lambda x : len(x[1]))
        facebook_categories.reverse()

        mapping = ["'"+str(like.id)+"':"+str(like.topCategory()) for like in likes]
        # I don't want to call topCategory() twice, so I'm checking for None on a second stage
        mapping = ','.join([s for s in mapping if s[-1] != 'e'] )
                
    else:
        return redirect('r_home')
    return render_to_response(template_name, {
            'entity' : entity,
            'categories':categories,
            'facebook_categories':facebook_categories,
            'mapping':mapping,
            }, context_instance=RequestContext(request))

def friends(request, entity_id=None, template_name="reflect/profile.html"):
    return redirect('r_home')
