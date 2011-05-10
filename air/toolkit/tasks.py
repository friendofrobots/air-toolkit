from django.db.models import Count, Q, Max, Min
from celery.decorators import task
from celery.result import TaskSetResult
from toolkit.models import DownloadStatus, Entity, Link, PMI, Category, CategoryScore
from fbauth.models import Profile
import json, urllib2, urllib, math, facebook

from celery.task.sets import TaskSet

"""
So I need a download tasks, process them and dump them in the database
Then I need to run through and process the PMI information, ideally in
a task format so I can give progress on it.
"""

def test(profile_id):
    links = Link.objects.annotate(entity_activity=Count('toEntity__linksTo'))
    likes = links.filter(owner=Profile.objects.get(id=profile_id),
                         entity_activity__gt=1,relation="likes")
    numpeople = Entity.objects.filter(linksTo__in=likes).distinct().count()
    linkedBy = {}
    for link in likes:
        if link.toEntity.id not in linkedBy:
            linkedBy[link.toEntity.id] = set()
        linkedBy[link.toEntity.id].add(link.fromEntity.id)

    for (n, (entity_id1,lb1)) in enumerate(linkedBy.iteritems()):
        profile = Profile.objects.get(id=profile_id)
        fromEntity = Entity.objects.get(id=entity_id1)
        print fromEntity.name, n,'/',len(linkedBy)
        for entity_id2,lb2 in linkedBy.iteritems():
            if entity_id1 <= entity_id2 and len(lb1.intersection(lb2))>0:
                PMI.objects.get_or_create(
                    owner=profile,
                    fromEntity=fromEntity,
                    toEntity=Entity.objects.get(id=entity_id2),
                    value=math.log(len(lb1.intersection(lb2))*numpeople/(len(lb1)*len(lb2)),2))

@task(ignore_result=True)
def dlUser(profile_id,graphapi,fbid):
    try:
        entities = set()
        links = set()

        # likes
        likeEntities, likeLinks = dlLikes(graphapi,fbid)
        entities.update(likeEntities)
        links.update(likeLinks)

        # interests
        interestEntities, interestLinks = dlInterests(graphapi,fbid)
        entities.update(interestEntities)
        links.update(interestLinks)

        profile = Profile.objects.get(id=profile_id)
        for fbid,name in entities:
            if len(str(fbid)) > 50:
                fbid = str(fbid)[:50]
            if len(name) > 180:
                name = name[:180]
            Entity.objects.get_or_create(
                owner=profile,
                fbid=fbid,
                name=name)

        for link in links:
            if len(str(link[0])) > 50:
                link = (str(link[0])[:50],link[1],link[2],link[3])
            if len(str(link[3])) > 50:
                link = (link[0],link[1],link[2],str(link[3])[:50])
            Link.objects.get_or_create(
                owner=profile,
                fromEntity=Entity.objects.get(fbid=link[0]),
                relation=link[1],
                toEntity=Entity.objects.get(fbid=link[3]),
                defaults={'weight':link[2]})

    except (ValueError,IOError,facebook.GraphAPIError,urllib2.URLError), exc:
        print exc
        dlUser.retry(countdown=15, max_retries=None, throw=False)

@task(ignore_result=True)
def checkTaskSet(taskset_id,profile_id,status_id):
    result = TaskSetResult.restore(taskset_id)
    if result.ready():
        links = Link.objects.annotate(entity_activity=Count('toEntity__linksTo'))
        likes = links.filter(owner=Profile.objects.get(id=profile_id),
                             entity_activity__gt=1,relation="likes")
        numpeople = Entity.objects.filter(linksTo__in=likes).distinct().count()
        linkedBy = {}
        for link in likes:
            if link.toEntity.id not in linkedBy:
                linkedBy[link.toEntity.id] = set()
            linkedBy[link.toEntity.id].add(link.fromEntity.id)

        subtasks = [calcPMIs.subtask((profile_id,linkedBy,entity_id,lb,numpeople)) for (entity_id,lb) in linkedBy.iteritems()]
        r = TaskSet(tasks=subtasks).apply_async()
        r2 = tasks.checkPMISet.delay(r.taskset_id,profile.id,status.id)
        status = DownloadStatus.objects.get(id=status_id)
        status.stage = 2
        status.task_id = r.task_id
        status.save()
    else:
        checkTaskSet.retry(countdown=15, max_retries=None)

@task(ignore_result=True)
def calcPMIs(profile_id, linkedBy, entity_id1, lb1, numpeople):
    """
    Pmi(i1,i2) = log(Pr(i1,i2) / Pr(i1)Pr(i2))
               = log(num(i1,i2)*totalPeople / num(i1)num(i2))

    pmis are symmetric, so only store the link from the one with the
      lower id to the one with the higher id (note: ids are strings,
      so the sort is alphabetical in this case)
    """
    profile = Profile.objects.get(id=profile_id)
    fromEntity = Entity.objects.get(id=entity_id1)
    for entity_id2,lb2 in linkedBy.iteritems():
        if entity_id1 <= entity_id2 and len(lb1.intersection(lb2))>0:
            PMI.objects.get_or_create(
                owner=profile,
                fromEntity=fromEntity,
                toEntity=Entity.objects.get(id=entity_id2),
                value=math.log(len(lb1.intersection(lb2))*numpeople/(len(lb1)*len(lb2)),2))

@task(ignore_result=True)
def checkPMISet(taskset_id,profile_id,status_id):
    result = TaskSetResult.restore(taskset_id)
    if result.ready():
        status = DownloadStatus.objects.get(id=status_id)
        status.stage = 3
        status.task_id = ""
        status.save()
    else:
        checkTaskSet.retry(countdown=15, max_retries=None)

def testCategory(profile_id, category_id):
    category = Category.objects.get(id=category_id)
    category.scores.update(value=0.0,fired=False)
    agg = PMI.objects.aggregate(Min('value'),Max('value'))
    createCategory(profile_id, category_id, .4,.3,agg['value__min'],agg['value__max'])

@task(ignore_result=True)
def createCategory(profile_id, category_id, threshold, decayrate, minpmi, maxpmi):
    """
    F is firing threshold, D is decay factor, W is link weight
    for each unfired node [i] where A[i]>F:
        For each link [i,j] adjust A[j] = A[j] + (A[i]*W[i,j]*D)
        (cap at 1, mark all fired so they don't fire again)
        nodes with A[i]>F fire next time
    """
    profile = Profile.objects.get(id=profile_id)
    category = Category.objects.get(id=category_id)
    
    scores = category.scores
    scores.filter(entity__in=category.seeds.all()).update(value=0.6)
    toFire = scores.filter(fired=False,value__gte=threshold)
    # going back and forth between nodes and score, need to clear this up
    count = category.scores.count()
    while toFire:
        print toFire.count(), '/', count, 'firing this round.', 'decay is',decayrate
        for score1 in toFire:
            for node2 in Entity.objects.filter(pmiTo__fromEntity=score1.entity):
                if score1.entity != node2:
                    pmi = score1.entity.pmiFrom.get(toEntity=node2)
                    node2score = node2.categoryScore.get(category=category)
                    weight = (pmi.value-minpmi) / (maxpmi-minpmi)
                    newValue = node2score.value + (score1.value*weight*decayrate)
                    if newValue > 1:
                        newValue = 1.0
                    node2score.value = newValue
                    node2score.save()
            for node2 in Entity.objects.filter(pmiFrom__toEntity=score1.entity):
                if score1.entity != node2:
                    pmi = score1.entity.pmiTo.get(fromEntity=node2)
                    node2score = node2.categoryScore.get(category=category)
                    weight = (pmi.value-minpmi) / (maxpmi-minpmi)
                    newValue = node2score.value + (score1.value*weight*decayrate)
                    if newValue > 1:
                        newValue = 1.0
                    node2score.value = newValue
                    node2score.save()
            score1.fired = True
            score1.save()
        toFire = scores.filter(fired=False,value__gte=threshold)
        decayrate = decayrate**2
    category.task_id = ""
    category.active = None
    category.save()
                                                
            

def dlInfo(graphapi,fbid):
    data = graphapi.get_object(fbid)
    entities,links = set(),set()
    entities.add((data['id'],data['name']))
    if 'gender' in data:
        if data['gender'] == 'male':
            e,l = parseLink(fbid,
                            'male',
                            'male',
                            'gender',1,'Gender')
            entities.update(e)
            links.update(l)
        elif data['gender'] == 'female':
            e,l = parseLink(fbid,
                            'female',
                            'female',
                            'gender',1,'Gender')
            entities.update(e)
            links.update(l)
    if 'hometown' in data:
        if data['hometown']['id']:
            e,l = parseLink(fbid,
                            data['hometown']['id'],
                            data['hometown']['name'],
                            'isFrom',1,'City')
            entities.update(e)
            links.update(l)
    if 'location' in data:
        if data['location']['id']:
            e,l = parseLink(fbid,
                            data['location']['id'],
                            data['location']['name'],
                            'livesIn',1,'City')
            entities.update(e)
            links.update(l)
    if 'education' in data:
        for item in data['education']:
            if 'school' in item:
                e,l = parseLink(fbid,
                                item['school']['id'],
                                item['school']['name'],
                                'attended',1,'School')
                entities.update(e)
                links.update(l)
            if 'year' in item:
                e,l = parseLink(fbid,
                                item['year']['id'],
                                item['year']['name'],
                                'graduatedIn',1,'SchoolYear')
                entities.update(e)
                links.update(l)
            if 'concentration' in item:
                for c in item['concentration']:
                    e,l = parseLink(fbid,
                                    c['id'],
                                    c['name'],
                                    'majoredIn',1,'Concentration')
                    entities.update(e)
                    links.update(l)
    if 'work' in data:
        for item in data['work']:
            if 'employer' in item:
                e,l = parseLink(fbid,
                                item['employer']['id'],
                                item['employer']['name'],
                                'workedFor',1,'Employer')
                entities.update(e)
                links.update(l)
    if 'significant_other' in data:
        e,l = parseLink(fbid,
                        data['significant_other']['id'],
                        data['significant_other']['name'],
                        'isInRelationshipWith',1)
        entities.update(e)
        links.update(l)
    if 'religion' in data:
        try:
            e,l = parseLink(fbid,
                            data['religion']['id'],
                            data['religion']['name'],
                            'believesIn',1,'Religion')
            entities.update(e)
            links.update(l)
        except:
            e,l = parseLink(fbid,
                            data['religion'],
                            data['religion'],
                            'believesIn',1,'Religion')
            entities.update(e)
            links.update(l)
    if 'political' in data:
        try:
            e,l = parseLink(fbid,
                            data['political']['id'],
                            data['political']['name'],
                            'votes',1,'PoliticalView')
            entities.update(e)
            links.update(l)
        except:
            e,l = parseLink(fbid,
                            data['political'],
                            data['political'],
                            'votes',1,'PoliticalView')
            entities.update(e)
            links.update(l)
    return entities, links

def dlLikes(graphapi,fbid):
    data = graphapi.get_connections(fbid,"likes")['data']
    entities,links = set(),set()
    for like in data:
        e,l = parseLink(fbid,
                        like['id'],
                        like['name'],
                        'likes',1,like['category'])
        entities.update(e)
        links.update(l)
    return entities, links

def dlInterests(graphapi,fbid):
    data = graphapi.get_connections(fbid,"interests")['data']
    entities,links = set(),set()
    for interest in data:
        e,l = parseLink(fbid,
                        interest['id'],
                        interest['name'],
                        'likes',1,interest['category'])
        entities.update(e)
        links.update(l)
    return entities, links

def dlFriends(graphapi,fbid):
    args = {
        "access_token" : graphapi.access_token,
        "target_uid" : fbid,
        "format" : 'JSON',
        }
    file = urllib2.urlopen("https://api.facebook.com/method/friends.getMutualFriends?"
                           + urllib.urlencode(args))
    data = json.load(file)
    try:
        friends["error_code"]
        raise facebook.GraphAPIError(friends["error_code"],
                                     friends["error_msg"])
    except:
        entities,links = set(),set()
        for friend in data:
            links.add((fbid,'isFriendsWith',1,friend))
        return entities, links

def parseLink(fbid,thingid,name,rel,score,category=None):
    e = set([(thingid,name)])
    l = set([(fbid,rel,score,thingid)])
    if category:
        e.add((category,category))
        l.add((thingid,'category',1,category))
    return e,l

@task()
def add(x,y):
    return x+y
