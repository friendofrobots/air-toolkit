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
        return redirect('login')
    return render_to_response(template_name, {
            'status' : status,
            }, context_instance=RequestContext(request))

def categories(request, category_id=None, template_name="reflect/categories.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        categories = Category.objects.filter(owner=profile)
        if not category_id:
            category = Category.objects.filter(owner=profile)[0]
        else:
            category = get_object_or_404(Category,id=category_id)
    else:
        return redirect('r_home')
    return render_to_response(template_name, {
            'category' : category,
            'categories' : categories,
            }, context_instance=RequestContext(request))

def rename(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            category = Category.objects.get(id=request.POST.get("category_id"))
            category.name = request.POST.get("name",category.name)
            category.save
            response_data = {
                "success":True,
                "name":category.name,
                }
        else:
            response_data = {
                "error":"must be post",
                }
    else:
        response_data = {
            "error":"not logged in",
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")
    

def profile(request, entity_id=None, template_name="reflect/profile.html"):
    if request.user.is_authenticated():
        """ I need categories of objects, sorted.
       Then I need to either determine the category for each object
        or put that off and do it by ajax. I'm thinking about pre-calculating.
        """
        profile = request.user.profile
        if not entity_id:
            entity = Entity.objects.get(fbid=profile.fbid)
        else:
            entity = get_object_or_404(Entity,id=entity_id)
        categories = Category.objects.filter(owner=profile)
        likeLinks = entity.linksFrom.filter(relation="likes")
        likes = Entity.objects.filter(linksTo__in=likeLinks).distinct()

        category_links = Link.objects.filter(owner=profile,relation='category')
        fbcategories = {}
        for like in likes:
            fbcat_link = category_links.filter(fromEntity=like)[0]
            if fbcat_link.toEntity.name not in fbcategories:
                fbcategories[fbcat_link.toEntity.name] = []
            fbcategories[fbcat_link.toEntity.name].append(like)

        mapping = ["'"+str(like.toEntity_id)+"':"+str(like.toEntity.topCategory()) for like in entity.likes()]
        # I don't want to call topCategory() twice, so I'm checking for None on a second stage
        mapping = ','.join([s for s in mapping if s[-1] != 'e'] )
        mapping = []
                
    else:
        return redirect('r_home')
    return render_to_response(template_name, {
            'entity' : entity,
            'categories':categories,
            'facebook_categories':fbcategories,
            'mapping':mapping,
            }, context_instance=RequestContext(request))

def friends(request, entity_id=None, template_name="reflect/profile.html"):
    return redirect('r_home')
