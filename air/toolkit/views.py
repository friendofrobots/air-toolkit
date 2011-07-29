from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.models import User

import json, facebook
from celery.result import AsyncResult, TaskSetResult
from celery.task.sets import TaskSet
from toolkit.models import *
from toolkit import tasks
from toolkit.forms import CategoryCreateForm
from fbauth.models import FBLogin

"""
Flow:
Main page
login
click download button
get loading screen
server:
  taskset of download tasks
  sort out data into graph
  run pmi stuff on data
  run category discovery
redirect to display page
"""

def newUser(request, redirectTo='explore:home'):
    if request.user.is_authenticated():
        try:
            request.user.fblogin
            request.user.profile
        except FBLogin.DoesNotExist:
            return redirect('auth:login')
        except Profile.DoesNotExist:
            Profile.objects.create(
                user=request.user,
                fblogin=request.user.fblogin,
                )
    return redirect(redirectTo)

## Download Views ##
def startDownload(request):
    """
    Ajax call to start the download
    """
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            if profile.stage > 0:
                if profile.stage < 3:
                    result = TaskSetResult.restore(profile.task_id)
                    response_data = {
                        "error": "download already started",
                        "stage" : profile.stage,
                        "completed" : result.completed_count(),
                        "total" : result.total,
                        }
                else:
                    reponse_data = {
                        "error": "download already finished",
                        "stage" : profile.stage,
                        "state" : "completed",
                        }
            else:
                graphapi = facebook.GraphAPI(profile.fblogin.access_token)
                me = graphapi.get_object('me')
                friends = [(f['id'],f['name']) for f in graphapi.get_connections('me','friends')['data']]
                friends.append((me['id'],me['name']))

                subtasks = [tasks.dlUser.subtask((profile.id,graphapi,fbid,name)) for (fbid,name) in friends]
                result = TaskSet(tasks=subtasks).apply_async()
                result.save()
                profile.stage = 1
                profile.task_id = result.taskset_id
                profile.save()
                r = tasks.checkTaskSet.delay(result,profile.id)
                response_data = {
                    "stage":1,
                    "completed": result.completed_count(),
                    "total": result.total,
                    }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def status(request):
    if request.user.is_authenticated():
        profile = request.user.profile
        """
        I need to execute 2 separate tasks:
        1) Download and save (set) - this should already be started
        2) Calculate and save pmi information (set)
        """
        if profile.stage==0:
            response_data = {
                "stage":0,
                "state":'not yet started',
                }
        elif profile.stage==1:
            result = TaskSetResult.restore(profile.task_id)
            response_data = {
                "stage":1,
                "completed": result.completed_count(),
                "total": result.total,
                }
        elif profile.stage==2:
            result = TaskSetResult.restore(profile.task_id)
            response_data = {
                "stage":2,
                "completed": result.completed_count(),
                "total": result.total,
                }
        else:
            response_data = {
                "stage":3,
                "state": "completed",
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

## Page Views ##
def pageLikedBy(request, page_id):
    if request.user.is_authenticated():
        profile = request.user.profile
        page = get_object_or_404(Page,id=page_id)
        response_data = {
            "likedBy": [[person.name,person.fbid,person.id] for person in page.likedBy.order_by('fbid')]
            }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def page_pmis(request, page_id):
    if request.user.is_authenticated():
        profile = request.user.profile
        like = get_object_or_404(Page,id=page_id)
        response_data = {
            "pmis": [[pmi.toPage.name,pmi.value] for pmi in page.pmisFrom.order_by('fbid')]
            }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")


## Category Views ##
def addSeed(request, seed_id):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            try:
                active = profile.activeCategory
                seed = Page.objects.get(id=seed_id)
                active.seeds.add(seed)
                response_data = {
                    "id":seed_id,
                    "name":seed.name,
                    }
            except Category.DoesNotExist:
                response_data = {
                    "error":"start a category first"
                    }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def deleteSeed(request, seed_id):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            try:
                active = profile.activeCategory
                seed = Page.objects.get(id=seed_id)
                active.seeds.remove(seed)
                response_data = {
                    "id":seed_id,
                    "name":seed.name,
                    }
            except Category.DoesNotExist:
                response_data = {
                    "error":"start a category first"
                    }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def newCategory(request, redirect_uri=None):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            try:
                category = profile.activeCategory
                createForm = CategoryCreateForm({ 'id':category.id })
                if redirect_uri:
                    if redirect_uri[0] != '/':
                        redirect_uri = '/'+redirect_uri
                    return redirect(redirect_uri)
                else:
                    response_data = {
                        "error":"another category is currently active"
                    }
            except Category.DoesNotExist:
                category = Category.objects.create(owner=profile,
                                                   name=request.POST.get('name','tempcategoryname'),
                                                   active=profile)
                if category.name == 'tempcategoryname':
                    category.name = 'Category '+unicode(category.id)
                    category.save()
                if redirect_uri:
                    if redirect_uri[0] != '/':
                        redirect_uri = '/'+redirect_uri
                    return redirect(redirect_uri)
                else:
                    response_data = {
                        "success": "true"
                        }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def createCategoryFromGroup(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            people = request.POST.getlist('people')
            if people:
                category = Category.objects.create(owner=profile,
                                                   name=request.POST.get('name','tempcategoryname'))
                group = PersonGroup.objects.create(owner=profile,
                                                   category=category)
                group.people.add(*Person.objects.filter(id__in=people))
                if category.name == 'tempcategoryname':
                    category.name = 'Category '+unicode(category.id)
                category.save()
                if request.POST.__contains__('redirect'):
                    return redirect(request.POST.get('redirect'),category.id)
                else:
                    response_data = {
                        "success": "true",
                        "id":category.id,
                        "url":reverse('context:category',category.id)
                    }
            else:
                response_data = {
                    "error": "must be at least one person"
                    }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def createCategoryFromPage(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            if request.POST.__contains__('seed'):
                seed = Page.objects.get(id=request.POST.get('seed'))
                category = Category.objects.create(owner=profile,
                                                   name='People who like '+seed.name)
                category.seeds.add(seed)
                group = PersonGroup.objects.create(owner=profile,
                                                   category=category)
                group.people.add(*Person.objects.filter(id__in=seed.likedBy.all()))
                if request.POST.__contains__('redirect'):
                    return redirect(request.POST.get('redirect'),category.id)
                else:
                    response_data = {
                        "success": "true",
                        "id":category.id,
                        "url":reverse('context:category',category.id)
                        }
            else:
                response_data = {
                    "error": "must be at least one person"
                    }
        else:
            response_data = {
                "error": "must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def startCategoryCreation(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = CategoryCreateForm(request.POST)
            if form.is_valid():
                profile = request.user.profile
                category = Category.objects.get(id=form.cleaned_data['category_id'])
                category.startvalue = form.cleaned_data['startvalue']
                category.threshold = form.cleaned_data['threshold']
                category.decayrate = form.cleaned_data['decayrate']
                category.save()
                result = tasks.createCategory.delay(profile.id,
                                                    category.id,
                                                    auto=False)
                category.task_id = result.task_id
                category.save()
                response_data = {
                    "stage":1,
                    "status": category.getStatus(),
                    "id": category.id,
                    "name": category.name,
                    }
            else:
                response_data = {
                    "error": form.errors
                    }
        else:
            response_data = {
                "error":"must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def startCreation(request, category_id=None):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            category = Category.objects.get(id=category_id)
            category.startvalue = float(request.POST.get('startvalue',category.startvalue))
            category.threshold = float(request.POST.get('threshold',category.threshold))
            category.decayrate = float(request.POST.get('decayrate',category.decayrate))
            category.save()
            result = tasks.createCategory.delay(profile.id,
                                                category.id,
                                                auto=True)
            category.task_id = result.task_id
            category.save()
            response_data = {
                "status": category.getStatus(),
                "id": category.id,
                "name": category.name,
                }
        else:
            response_data = {
                "error":"must be a post request"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def categoryStatus(request, category_id=None):
    if request.user.is_authenticated():
        profile = request.user.profile
        category = Category.objects.get(id=category_id)
        response_data = {
            "status": category.getStatus() if category.task_id else "completed",
            "num_pages": category.scores.filter(value__gt=0).count(),
            "id": category.id,
            "name": category.name,
            }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def markRead(request, category_id=None):
    if request.user.is_authenticated():
        if request.method == "POST":
            category = Category.objects.get(id=category_id)
            if category.unread:
                category.unread = False
                category.save()
                response_data = {
                    "success":True,
                    "id":category.id,
                    "name":category.name,
                    }
            else:
                response_data = {
                    "success":False,
                    "id":category.id,
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

def rename(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            category = Category.objects.get(id=request.POST.get("category_id"))
            category.name = request.POST.get("name",category.name)
            category.save()
            response_data = {
                "success":True,
                "id":category.id,
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

def categoryReset(request,category_id):
    if request.user.is_authenticated():
        profile = request.user.profile
        if request.method == "POST":
            try:
                profile.activeCategory
            except Category.DoesNotExist:
                category = Category.objects.get(id=category_id)
                category.active = profile
                category.task_id = ""
                category.status = ""
                category.save()
        return redirect('explore:categories')
    else:
        return redirect('explore:home')

def getNotifications(request):
    if request.user.is_authenticated():
        unread = Category.objects.filter(owner=request.user.profile,unread=True).order_by('-last_updated')
        response_data = {
            "success":True,
            "unread":[[c.id,c.name] for c in unread],
            }
    else:
        response_data = {
            "error":"not logged in",
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")
