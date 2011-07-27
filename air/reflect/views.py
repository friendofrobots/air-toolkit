from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect

import json
from toolkit.models import *

def home(request, template_name="reflect/home.html"):
    if not request.user.is_authenticated():
        return redirect('auth:login_redirect','reflect:home')
    return render_to_response(template_name, {
            'profile' : profile,
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
        return redirect('reflect:home')
    return render_to_response(template_name, {
            'category' : category,
            'categories' : categories,
            }, context_instance=RequestContext(request))    

def profile(request, person_id=None, template_name="reflect/profile.html"):
    if request.user.is_authenticated():
        """ I need categories of objects, sorted.
       Then I need to either determine the category for each object
        or put that off and do it by ajax. I'm thinking about pre-calculating.
        """
        profile = request.user.profile
        if not person_id:
            person = Person.objects.get(owner=profile,fbid=profile.fblogin.fbid)
        else:
            person = get_object_or_404(Person,id=person_id)
        categories = Category.objects.filter(owner=profile).order_by('id')

        fbcategories = {}
        for like in person.likes.order_by('-category'):
            if like.category not in fbcategories:
                fbcategories[like.category] = []
            fbcategories[like.category].append(like)
        likes_by_fbcat = fbcategories.items()
        likes_by_fbcat.sort(key=lambda x : len(x[1]))
        likes_by_fbcat.reverse()

        mapping = ["'"+str(like.id)+"':"+str(like.topCategory()) for like in person.likes.all()]
        # I don't want to call topCategory() twice, so I'm checking for None on a second stage
        mapping = ','.join([s for s in mapping if s[-1] != 'e'] )
                
    else:
        return redirect('reflect:home')
    return render_to_response(template_name, {
            'person' : person,
            'categories':categories,
            'likes_by_fbcat':likes_by_fbcat,
            'mapping':mapping,
            }, context_instance=RequestContext(request))

def friends(request, template_name="reflect/profile.html"):
    return redirect('reflect:home')
