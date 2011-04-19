from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User

import pickle, types, json
from toolkit.models import Entity
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
    """
    Display the loading html page.
    """
    return render_to_response(template_name, {
                "ftw" : SO_MUCH_WIN,
                }, context_instance=RequestContext(request))
    
def startDownload(request):
    """
    Ajax call to start the download
    """
    graphapi = facebook.GraphAPI(access_token)
    self.me = graphapi.get_object('me')
    friendIds = [f['id'] for f in graphapi.get_connections('me','friends')['data']]
    friendIds.append(self.me['id'])
    tasks = []
    for i, fbid in enumerate(friendIds):
        tasks.append(dlFriends.subtask((graphapi,fbid)))
        tasks.append(dlInfo.subtask((graphapi,fbid)))
        tasks.append(dlLikes.subtask((graphapi,fbid)))
        tasks.append(dlInterests.subtask((graphapi,fbid)))
    job = TaskSet(tasks)
    result = job.apply_async()
    return HttpResponse(json.dumps({}), mimetype="application/json")


def status(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        "task": {
            "id": task_id,
            "status": result.status(),
            "completed": result.status(),
            "total": result.status(),
            }
        }

def pmi_all(request, greg=True, template_name="toolkit/pmi.html"):
    if greg:
        data = User.objects.get(pk=1).profile_set.all()[0].data_set.all()[0]
    if request.user.is_authenticated():
        data = request.user.profile_set.all()[0].data_set.all()[0]
    # These may not be here yet, check for that
    print 'loading json'
    pmi = json.loads(data.pmi_matrix)
    graph = json.loads(data.filtered_graph)
    print 'rendering html'
    print pmi
    return render_to_response(template_name, {
                "objects" : pmi.keys()[:100],
                "lookup" : lookup,
                }, context_instance=RequestContext(request))

def getPmiVector(request, fbid):
    """
    load pmi matrix
    vector = pmi[fbid]
    filter our 0s
    """
    return HttpResponse(json.dumps(VECTOR),mimetype="application/json")
