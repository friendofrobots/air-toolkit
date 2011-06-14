from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.models import User

import json, facebook
from celery.result import AsyncResult, TaskSetResult
from celery.task.sets import TaskSet
from toolkit.models import Entity, Link, PMI, DownloadStatus, Category, CategoryScore
from toolkit import tasks
from toolkit.forms import CategoryCreateForm
from fbauth.models import Profile

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

## Download Views ##
def startDownload(request):
    """
    Ajax call to start the download
    """
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            try:
                status = profile.downloadStatus
                if status.stage < 3:
                    result = TaskSetResult.restore(status.task_id)
                    response_data = {
                        "error": "download already started",
                        "stage" : status.stage,
                        "completed" : result.completed_count(),
                        "total" : result.total,
                        }
                else:
                    reponse_data = {
                        "error": "download already finished",
                        "stage" : status.stage,
                        "state" : "completed",
                        }
            except:
                graphapi = facebook.GraphAPI(profile.access_token)
                me = graphapi.get_object('me')
                friends = [(f['id'],f['name']) for f in graphapi.get_connections('me','friends')['data']]
                friends.append((me['id'],me['name']))
                for friend in friends:
                    Entity.objects.create(owner=profile,
                                          fbid=friend[0],
                                          name=friend[1])
                subtasks = [tasks.dlUser.subtask((profile.id,graphapi,fbid)) for (fbid,name) in friends]
                result = TaskSet(tasks=subtasks).apply_async()
                status = DownloadStatus.objects.create(owner=profile,stage=1,task_id=result.taskset_id)
                status.save()
                result.save()
                r = tasks.checkTaskSet.delay(result.taskset_id,profile.id,status.id)
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
        status = request.user.profile.downloadStatus
        """
        I need to execute 2 separate tasks:
        1) Download and save (set) - this should already be started
        2) Calculate and save pmi information (set)
        """
        if status.stage==1:
            result = TaskSetResult.restore(status.task_id)
            response_data = {
                "stage":1,
                "completed": result.completed_count(),
                "total": result.total,
                }
        elif status.stage==2:
            result = TaskSetResult.restore(status.task_id)
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

## Entity Views ##
def entityLikedBy(request, entity_id):
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def like_pmis(request, entity_id):
    if request.user.is_authenticated():
        profile = request.user.profile
        like = get_object_or_404(Entity,id=entity_id)
        response_data = {
            "pmis": [[pmi.fromEntity.name,pmi.value] if pmi.toEntity == like else [pmi.toEntity.name,pmi.value] for pmi in like.getpmis()]
            }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data),mimetype="application/json")

def addSeed(request, seed_id):
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile
            try:
                active = profile.activeCategory
                seed = Entity.objects.get(id=seed_id)
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
                seed = Entity.objects.get(id=seed_id)
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
                createForm = CategoryCreateForm({ 'id':category.id })
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

def startCategoryCreation(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = CategoryCreateForm(request.POST)
            if form.is_valid():
                profile = request.user.profile
                category = Category.objects.get(id=form.cleaned_data['category_id'])
                startvalue = form.cleaned_data['startvalue']
                threshold = form.cleaned_data['threshold']
                decayrate = form.cleaned_data['decayrate']
                result = tasks.createCategory.delay(profile.id,
                                                    category.id,
                                                    startvalue,
                                                    threshold,
                                                    decayrate)
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
    
    
def categoryStatus(request, category_id):
    if request.user.is_authenticated():
        profile = request.user.profile
        try:
            category = Category.objects.get(id=category_id)
            if category.task_id:
                response_data = {
                    "status": category.getStatus(),
                    "id": category.id,
                    "name": category.name,
                    }
            else:
                response_data = {
                    "status": "completed",
                    "id": category.id,
                    "name": category.name,
                    }
        except Category.DoesNotExist:
            response_data = {
                "error" : "no active category"
                }
    else:
        response_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

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
        return redirect('categories')
    else:
        return redirect('home')
