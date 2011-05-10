from django.shortcuts import render_to_response
from django.template import RequestContext
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
        redirect('login',redirect=reverse('r_home'))
    return render_to_response(template_name, {
            'status' : status,
            }, context_instance=RequestContext(request))

def categories(request, category_id=None, template_name="reflect/categories.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        categories = Category.objects.all()
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
        categories = Categories.objects.all()
    else:
        return redirect('r_home')
    return render_to_response(template_name, {
            'friends' : friends,
            }, context_instance=RequestContext(request))
