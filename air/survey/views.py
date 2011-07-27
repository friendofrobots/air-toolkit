from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect

import json
from toolkit.models import *

def home(request, template_name="survey/home.html"):
    if request.user.is_authenticated():
        try:
            profile = request.user.profile
            category = profile.categories.order_by('id')[0]
        except:
            category = None
    else:
        # This doesn't work, I need to figure out how to redirect properly
        return redirect('auth:login_redirect','survey:home')
    return render_to_response(template_name, {
            'profile' : profile,
            'category' : category,
            }, context_instance=RequestContext(request))

def category(request, category_id=None, template_name="survey/category.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
    else:
        return redirect('survey:home')
    return render_to_response(template_name, {
            'category' : category,
            'question_number' : 1,
            'prev' : category.id - 1 if category.id > 1 else None,
            'next' : category.id + 1 if category.id < 12 else None,
            'tab' : 'category',
            }, context_instance=RequestContext(request))

def profile(request, category_id=None, person_id=None, template_name="survey/profile.html"):
    if request.user.is_authenticated():
        """ I need categories of objects, sorted.
       Then I need to either determine the category for each object
        or put that off and do it by ajax. I'm thinking about pre-calculating.
        """
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
        if not person_id:
            person = Person.objects.get(owner=profile,fbid=profile.fblogin.fbid)
        else:
            person = get_object_or_404(Person,id=person_id)

        fbcategories = {}
        for like in person.likes.order_by('-category'):
            if like.category not in fbcategories:
                fbcategories[like.category] = []
            fbcategories[like.category].append(like)
        likes_by_fbcat = fbcategories.items()
        likes_by_fbcat.sort(key=lambda x : len(x[1]))
        likes_by_fbcat.reverse()

        cat_likes = ','.join(["'"+str(like.id)+"'" for like in person.likes.all() if like.categoryScore.filter(category=category).exists() and like.categoryScore.get(category=category).value > .2])

    else:
        return redirect('survey:home')
    return render_to_response(template_name, {
            'person' : person,
            'category' : category,
            'likes_by_fbcat':likes_by_fbcat,
            'cat_likes':cat_likes,
            'question_number' : 1,
            'prev' : category.id - 1 if category.id > 1 else None,
            'next' : category.id + 1 if category.id < 12 else None,
            'tab' : "profile",
            }, context_instance=RequestContext(request))

def friends(request, category_id=None, page_num=None, template_name="survey/friends.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
    else:
        return redirect('survey:home')
    return render_to_response(template_name, {
            'category' : category,
            'memberships' : category.memberships.order_by('-value'),
            'question_number' : 1,
            'prev' : category.id - 1 if category.id > 1 else None,
            'next' : category.id + 1 if category.id < 12 else None,
            'tab' : "friends",
            }, context_instance=RequestContext(request))

def like(request, category_id=None, like_id=None, template_name="survey/like.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = get_object_or_404(Category,id=category_id)
        like = get_object_or_404(Page,id=like_id)
    else:
        return redirect('survey:home')
    return render_to_response(template_name, {
            'category' : category,
            'like' : like,
            'question_number' : 1,
            'prev' : category.id - 1 if category.id > 1 else None,
            'next' : category.id + 1 if category.id < 12 else None,
            'tab' : 'category',
            }, context_instance=RequestContext(request))
