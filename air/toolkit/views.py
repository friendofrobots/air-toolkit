from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User

import json, facebook
from celery.result import AsyncResult, TaskSetResult
from celery.task.sets import TaskSet
from toolkit import tasks
from toolkit.models import Entity, Link, PMI, DownloadStatus
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

def download(request, template_name="toolkit/download.html"):
    if request.user.is_authenticated():
        if request.user.profile.all()[0].downloadStatus.exists():
            stage = request.user.profile.all()[0].downloadStatus.all()[0].stage
        else:
            stage = None
    else:
        return HttpResponseRedirect('/')
    return render_to_response(template_name, {
                "stage" : stage,
                }, context_instance=RequestContext(request))

def startDownload(request):
    """
    Ajax call to start the download
    """
    if request.user.is_authenticated():
        if request.method == 'POST':
            profile = request.user.profile.all()[0]
            if not profile.downloadStatus.exists():
                graphapi = facebook.GraphAPI(profile.access_token)
                me = graphapi.get_object('me')
                friends = [(f['id'],f['name']) for f in graphapi.get_connections('me','friends')['data']]
                friends.append((me['id'],me['name']))
                for friend in friends:
                    Entity.objects(owner=profile,
                                   fbid=friend[0],
                                   name=friend[1])
                subtasks = [tasks.dlUser.subtask((graphapi,fbid)) for (fbid,name) in friendIds]
                result = TaskSet(tasks=subtasks).apply_async()
                result.save()
                status = DownloadStatus.objects.create(owner=profile,stage=1,task_id=result.taskset_id)
                status.save()
                r = tasks.checkTaskSet.delay(result.taskset_id,profile.fbid,status.id)
                response_data = {
                    "stage":1,
                    "completed": result.completed_count(),
                    "total": result.total,
                    }
            else:
                status = profile.downloadStatus.all()[0],
                response_data = {
                    "error": "download already started",
                    "stage" : status.stage,
                    }
                if status.stage == 1:
                    result = TaskSetResult.restore(status.task_id)
                    response_data['completed'] = result.completed_count()
                    response_data['total'] = result.total
                else:
                    result = AsyncResult(status.task_id)
                    response_data['state'] = result.state
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
        status = request.user.profile.all()[0].downloadStatus.all()[0]
        """
        I need to execute 3 separate tasks:
        1) Download users with a TaskSet - this should already be started
        2) Save the user data
        3) Calculate and save pmi information
        """
        if status.stage==1:
            result = TaskSetResult.restore(status.task_id)
            response_data = {
                "stage":1,
                "completed": result.completed_count(),
                "total": result.total,
                }
        elif status.stage==2:
            result = AsyncResult(status.task_id)
            response_data = {
                "stage":2,
                "state": result.state,
                }
        elif status.stage==3:
            result = AsyncResult(status.task_id)
            response_data = {
                "stage":3,
                "state": result.state,
                }
        else:
            response_data = {
                "stage":4,
                "state": "completed",
                }
    else:
        responset_data = {
            "error": "user must be logged in"
            }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")
