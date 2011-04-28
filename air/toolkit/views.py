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

def download(request, template_name="toolkit/downloading.html"):
    started = True
    """
    Display the loading html page.
    """
    return render_to_response(template_name, {
                "started" : started,
                }, context_instance=RequestContext(request))
    
def startDownload(request):
    """
    Ajax call to start the download
    """
    if user.is_authenticated():
        if request.method == 'POST':
            graphapi = facebook.GraphAPI(access_token)
            me = graphapi.get_object('me')
            friendIds = [f['id'] for f in graphapi.get_connections('me','friends')['data']]
            friendIds.append(me['id'])
            profile = request.user.profile.all()[0]
            status = DownloadStatus.objects.create(owner=profile,stage=1)
            result = TaskSet(tasks=[tasks.dlUser.subtask((graphapi,fbid)) for fbid in friendIds]).apply_async()
            r = checkTaskSet(result.taskset_id,profile.fbid,status.id)
            status.task_id = result.taskset_id
            status.save()
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
        stage = request.user.profile.downloadStatus.stage
        task_id = request.user.profile.downloadStatus.task_id
        """
        I need to execute 3 separate tasks:
        1) Download users with a TaskSet - this should already be started
        2) Save the user data
        3) Calculate and save pmi information
        """
        if stage==1:
            result = TaskSetResult.restore(task_id)
            response_data = {
                "stage":1,
                "completed": result.completed_count(),
                "total": result.total,
                }
        elif stage==2:
            result = AsyncResult(task_id)
            response_data = {
                "stage":2,
                "state": result.state,
                }
        elif stage==3:
            result = AsyncResult(task_id)
            response_data = {
                "stage":3,
                "state": result.state,
                }
        else:
            response_data = {
                "stage":4,
                "status": "completed",
                }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")
