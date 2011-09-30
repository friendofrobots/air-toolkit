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
            'profile' : request.user.profile,
            }, context_instance=RequestContext(request))

def categories(request, category_id=None, template_name="reflect/categories.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        categories = Category.objects.filter(owner=profile).order_by('-last_updated')
        if not category_id:
            category = categories[0]
        else:
            category = get_object_or_404(Category,id=category_id)
    else:
        return redirect('reflect:home')
    return render_to_response(template_name, {
            'category' : category,
            'categories' : categories[:12],
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
        categories = Category.objects.filter(owner=profile).order_by('-last_updated')[:12]

        fbcategories = {}
        for like in person.likes.order_by('category'):
            if like.category not in fbcategories:
                fbcategories[like.category] = []
            fbcategories[like.category].append(like)
        likes_by_fbcat = fbcategories.items()
        likes_by_fbcat.sort(key=lambda x : len(x[1]))
        likes_by_fbcat.reverse()

        mapping = dict([(
                    category.id,
                    [ x['page_id'] for x in category.overThreshold().filter(page__in=person.likes.values('id')).values('page_id') ]
                    ) for category in categories])
                
    else:
        return redirect('reflect:home')
    return render_to_response(template_name, {
            'person' : person,
            'categories':categories,
            'likes_by_fbcat':likes_by_fbcat,
            'mapping':json.dumps(mapping),
            }, context_instance=RequestContext(request))

def friends(request, template_name="reflect/profile.html"):
    return redirect('reflect:home')
