import json, facebook, sys, time
from django.db.models import Count
from toolkit.models import Link,Entity
from toolkit import tasks
from celery.task.sets import TaskSet
    
def download(access_token):
    print 'Starting download'
    graphapi = facebook.GraphAPI(access_token)
    me = graphapi.get_object('me')
    friendIds = [f['id'] for f in graphapi.get_connections('me','friends')['data']]
    friendIds.append(me['id'])
    result = TaskSet(tasks=[tasks.dlUser.subtask((graphapi,fbid)) for fbid in friendIds]).apply_async()
    return result

def printStatus(result,message='loading',done='done.'):
    count = 0
    while (not result.ready()):
        print message+''.join(['.' for x in xrange(count)]), '\r',
        count += 1
        if count > 5:
            count = 0
        sys.stdout.flush()
        time.sleep(1)
    print done

def printSetStatus(result):
    while (not result.ready()):
        r = 1.0 * result.completed_count() / result.total
        bars = int(70*r)
        str_list = ['/']
        for i in xrange(70):
            if i < bars:
                str_list.append('-')
            else:
                str_list.append(' ')
        print ''.join(str_list),'/ ',int(100*r), '%\r',
        sys.stdout.flush()
        time.sleep(1)
    print '/'+''.join(['-' for n in xrange(70)]),'/','100%'

def saveData(result):
    r = tasks.saveUserData.delay((result.join()))
    printStatus(r,'saving data','saved.')

def calcPmis():
    likes = Link.objects.annotate(entity_activity=Count('toEntity__linksTo')).filter(entity_activity__gt=1,relation="likes")
    pr = tasks.calcPMIs.delay((likes))
    printStatus(pr,'calculating pmis')
    return pr
    
