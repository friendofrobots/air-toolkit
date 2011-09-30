from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect

import json
from toolkit.models import *
from survey.models import Survey

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


def post_survey(request, category_id=None, question=None):
    if request.user.is_authenticated():
        if request.method == 'POST' or True:
            profile = request.user.profile
            category = get_object_or_404(Category,id=category_id)
            survey, created = Survey.objects.get_or_create(owner=profile,category=category)
            response_data = {
                'profile':survey.owner_id,
                'category':survey.category_id
                }
            if question == "individual":
                survey.individual = request.POST.get('individual')
                survey.save()
                response_data['individual'] = survey.individual
            elif question == "subgroup":
                if request.POST.__contains__('subgroup1'):
                    survey.subgroup1 = request.POST.get('subgroup1')
                    survey.save()
                    response_data['subgroup1'] = survey.subgroup1
                if request.POST.__contains__('subgroup2'):
                    survey.subgroup2 = request.POST.get('subgroup2')
                    survey.save()
                    response_data['subgroup2'] = survey.subgroup2
                if request.POST.__contains__('subgroup3'):
                    survey.subgroup3 = request.POST.get('subgroup3')
                    survey.save()
                    response_data['subgroup3'] = survey.subgroup3
            elif question == "unifying":
                survey.unifying = request.POST.get('unifying')
                survey.save()
                response_data['unifying'] = survey.unifying
            elif question == "surprise":
                if request.POST.__contains__('surprise1-id'):
                    survey.surprise1_page = Page.objects.get(id=request.POST.get('surprise1-id'))
                    survey.save()
                    response_data['surprise1-id'] = survey.surprise1_page.id
                if request.POST.__contains__('surprise1-describe'):
                    survey.surprise1_describe = request.POST.get('surprise1-describe')
                    survey.save()
                    response_data['surprise1-describe'] = survey.surprise1_describe
                if request.POST.__contains__('surprise2-id'):
                    survey.surprise2_page = Page.objects.get(id=request.POST.get('surprise2-id'))
                    survey.save()
                    response_data['surprise2-id'] = survey.surprise2_page.id
                if request.POST.__contains__('surprise2-describe'):
                    survey.surprise2_describe = request.POST.get('surprise2-describe')
                    survey.save()
                    response_data['surprise2-describe'] = survey.surprise2_describe
            elif question == "actor":
                survey.actor = request.POST.get('actor')
                survey.save()
                response_data['actor'] = survey.actor
            elif question == "learned":
                survey.learned = request.POST.get('learned')
                survey.save()
                response_data['learned'] = survey.learned
            elif question == "further_thoughts":
                survey.further_thoughts = request.POST.get('further_thoughts')
                survey.save()
                response_data['further_thoughts'] = survey.further_thoughts
            response_data['success'] = True
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }        
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def surveys(request, template_name="survey/surveys.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        surveys = Survey.objects.order_by('-owner__fblogin__name')
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'surveys' : surveys,
            }, context_instance=RequestContext(request))

def results(request, survey_id, template_name="survey/results.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        survey = get_object_or_404(Survey,id=survey_id)
        scores = survey.category.scores.filter(value__gt=0).order_by('-value','page__fbid')
        memberships = survey.category.memberships.order_by('-value')[:12]
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'survey' : survey,
            'scores' : scores[:24],
            'memberships' : memberships,
            }, context_instance=RequestContext(request))

def check(request, template_name="survey/check.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
        surveys = Survey.objects.order_by('owner__fblogin__name')
        saturated = [54,66,73,74]
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            'path' : request.path,
            'surveys' : surveys,
            'saturated' : saturated,
            }, context_instance=RequestContext(request))

def summary(request, template_name="survey/summary.html"):
    if request.user.is_authenticated():
        profile = request.user.profile
    else:
        return redirect('explore:home')
    return render_to_response(template_name, {
            }, context_instance=RequestContext(request))
