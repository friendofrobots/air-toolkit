from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
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
        try:
            stage = request.user.profile.downloadStatus.stage
        except:
            stage = None
    else:
        return redirect('home')
    return render_to_response(template_name, {
                "stage" : stage,
                }, context_instance=RequestContext(request))

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
