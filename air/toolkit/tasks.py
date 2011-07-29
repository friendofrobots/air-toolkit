from django.db.models import Count, Q, Max, Min
from django.db import transaction
from celery.decorators import task
from celery.result import TaskSetResult
from toolkit.models import *
import json, urllib2, urllib, math, facebook

from celery.task.sets import TaskSet

"""
So I need a download tasks, process them and dump them in the database
Then I need to run through and process the PMI information, ideally in
a task format so I can give progress on it.
"""        


def conc_get_or_create(klass,*args,**kwargs):
    """
    Ran into a race condition where two threads would try to get_or_create a PersonProperty,
    see that none existed and both create their own.

    I added a unique_together property on the models so they will throw an exception if it
    already exists and this function will catch it and just get instead.
    """
    try:
        obj, created = klass.objects.get_or_create(*args,**kwargs)
    except:
        defaults = kwargs.pop('defaults',{})
        obj = klass.objects.get(*args,**kwargs)
        created = False
    return obj,created

@task()
def dlUser(profile_id,graphapi,fbid,name):
    try:
        profile = Profile.objects.get(id=profile_id)
        person, created = Person.objects.get_or_create(
            owner=profile,
            fbid=fbid,
            name=name)
        dlInfo(graphapi,profile,person)

        likes = graphapi.get_connections(fbid,"likes")['data']
        for like in likes:
            if not 'name' in like:
                print 'like with no name: ',like
            else:
                if len(like['name']) > 180:
                    like['name'] = like['name'][:180]
                page, created = conc_get_or_create(
                    Page,
                    owner=profile,
                    fbid=like['id'],
                    defaults={
                        'name':like['name'],
                        'category':like['category']
                        })
                person.likes.add(page)

        interests = graphapi.get_connections(fbid,"interests")['data']
        for interest in interests:
            page, created = conc_get_or_create(
                Page,
                owner=profile,
                fbid=interest['id'],
                defaults={
                    'name':interest['name'],
                    'category':interest['category']
                    })
            person.likes.add(page)

    except (ValueError,IOError,NameError,facebook.GraphAPIError,urllib2.URLError), exc:
        print exc
        dlUser.retry(countdown=15, max_retries=100, throw=False)
    except Exception,exc:
        print profile_id, fbid, name
        raise exc

def testDl(profile_id):
    profile = Profile.objects.get(id=profile_id)
    graphapi = facebook.GraphAPI(profile.fblogin.access_token)
    me = graphapi.get_object('me')
    friends = [(f['id'],f['name']) for f in graphapi.get_connections('me','friends')['data']]
    friends.append((me['id'],me['name']))

    subtasks = [dlUser.subtask((profile.id,graphapi,fbid,name)) for (fbid,name) in friends]
    result = TaskSet(tasks=subtasks).apply_async()
    result.save()
    profile.stage = 1
    profile.task_id = result.taskset_id
    profile.save()
    r = checkTaskSet.delay(result,profile.id)
    return result

def testInfo(profile_id):
    profile = Profile.objects.get(id=profile_id)
    graphapi = facebook.GraphAPI(profile.fblogin.access_token)
    me = graphapi.get_object('me')
    friends = [{'id':f['id'],'name':f['name']} for f in graphapi.get_connections('me','friends')['data']]
    friends.append({'id':me['id'],'name':me['name']})

    for friend in friends:
        data = graphapi.get_object(friend['id'])
        friend['data'] = data
        if 'gender' in data:
            friend['gender'] = data['gender']
        if 'hometown' in data:
            if data['hometown']['name']:
                if len(data['hometown']['name']) > 200:
                    hometown = data['hometown']['name'][:200]
                else:
                    hometown = data['hometown']['name']
                friend['hometown'] = hometown
        if 'location' in data:
            if data['location']['name']:
                if len(data['location']['name']) > 200:
                    location = data['location']['name'][:200]
                else:
                    location = data['location']['name']
                friend['location'] = location
        if 'education' in data:
            friend['school'] = []
            for item in data['education']:
                if 'school' in item:
                    if len(item['school']['name']) > 200:
                        school = item['school']['name'][:200]
                    else:
                        school = item['school']['name']
                    friend['school'].append(school)
        if 'work' in data:
            friend['work'] = []
            for item in data['work']:
                if 'employer' in item:
                    if len(item['employer']['name']) > 200:
                        employer = item['employer']['name'][:200]
                    else:
                        employer = item['employer']['name']
                    friend['work'].append(employer)
        if 'relationship_status' in data:
            friend['relationship'] = data['relationship_status']
    return friends
    

def dlInfo(graphapi,profile,person):
    data = graphapi.get_object(person.fbid)
    if 'gender' in data:
        prop, created = conc_get_or_create(
            PersonProperty,
            owner=profile,
            relation='gender',
            name=data['gender'])
        person.properties.add(prop)
    if 'hometown' in data:
        if data['hometown']['name']:
            if len(data['hometown']['name']) > 200:
                hometown = data['hometown']['name'][:200]
            else:
                hometown = data['hometown']['name']
            prop, created = conc_get_or_create(
                PersonProperty,
                owner=profile,
                relation='hometown',
                name=hometown)
            person.properties.add(prop)
    if 'location' in data:
        if data['location']['name']:
            if len(data['location']['name']) > 200:
                location = data['location']['name'][:200]
            else:
                location = data['location']['name']
            prop, created = conc_get_or_create(
                PersonProperty,
                owner=profile,
                relation='location',
                name=location)
            person.properties.add(prop)
    if 'education' in data:
        for item in data['education']:
            if 'school' in item:
                if len(item['school']['name']) > 200:
                    school = item['school']['name'][:200]
                else:
                    school = item['school']['name']
                prop, created = conc_get_or_create(
                    PersonProperty,
                    owner=profile,
                    relation='school',
                    name=school)
                person.properties.add(prop)
    if 'work' in data:
        for item in data['work']:
            if 'employer' in item:
                if len(item['employer']['name']) > 200:
                    employer = item['employer']['name'][:200]
                else:
                    employer = item['employer']['name']
                prop, created = conc_get_or_create(
                    PersonProperty,
                    owner=profile,
                    relation='work',
                    name=employer)
                person.properties.add(prop)
    if 'relationship_status' in data:
        prop, created = conc_get_or_create(
            PersonProperty,
            owner=profile,
            relation='relationship',
            name=data['relationship_status'])
        person.properties.add(prop)
    person.save()

@task(ignore_result=True)
def checkTaskSet(result,profile_id):
    if result.ready():
        profile = Profile.objects.get(id=profile_id)
        profile.page_set.annotate(activity=Count('likedBy')).exclude(activity__gt=1)
        profile.person_set.exclude(likes__in=profile.page_set.all()).distinct()
        numpeople = profile.getActivePeople().count()

        subtasks = [calcPMIs.subtask((profile_id,page.id,numpeople)) for page in pages]
        r = TaskSet(tasks=subtasks).apply_async()
        r.save()
        r2 = checkPMISet.delay(r,profile.id)
        profile.numpeople = numpeople
        profile.stage = 2
        profile.task_id = r.taskset_id
        profile.save()
    else:
        checkTaskSet.retry(countdown=15, max_retries=100)

def testPMIs(profile_id):
    profile = Profile.objects.get(id=profile_id)
    numpeople = profile.getActivePeople().count()

    subtasks = [calcPMIs.subtask((profile_id,page.id,numpeople)) for page in pages]
    r = TaskSet(tasks=subtasks).apply_async()
    r2 = checkPMISet.delay(r,profile.id)
    profile.stage = 2
    profile.task_id = r.taskset_id
    profile.save()
    return r, r2

@task()
def calcPMIs(profile_id, page_id1, numpeople):
    """
    Pmi(i1,i2) = log(Pr(i1,i2) / Pr(i1)Pr(i2))
               = log(num(i1,i2)*totalPeople / num(i1)num(i2))

    pmis are symmetric, so only store the link from the one with the
      lower id to the one with the higher id (note: ids are strings,
      so the sort is alphabetical in this case)
    """
    try:
        profile = Profile.objects.get(id=profile_id)
        pages = profile.getActivePages()
        fromPage = Page.objects.get(id=page_id1)
        likeCount = fromPage.likedBy.count()
        with transaction.commit_on_success():
            for toPage in pages.filter(likedBy__in=fromPage.likedBy.all()):
                intersect = fromPage.likedBy.filter(id__in=toPage.likedBy.all()).distinct().count()
                PMI.objects.get_or_create(
                    owner=profile,
                    fromPage=fromPage,
                    toPage=toPage,
                    value=math.log(1.*intersect*numpeople/(likeCount*toPage.likedBy.count()),2))
    except Exception, exc:
        print profile_id, page_id1
        raise exc
                    
@task(ignore_result=True)
def checkPMISet(result,profile_id):
    if result.ready():
        profile = Profile.objects.get(id=profile_id)
        agg = PMI.objects.filter(owner=profile).aggregate(Min('value'),Max('value'))
        profile.minpmi, profile.maxpmi = agg['value__min'],agg['value__max']
        profile.stage = 3
        profile.task_id = ""
        profile.save()
    else:
        checkPMISet.retry(countdown=15, max_retries=100)

@task(ignore_result=True)
def createCategory(profile_id, category_id, auto=False):
    profile = Profile.objects.get(id=profile_id)
    category = Category.objects.get(id=category_id)
    category.resetScores(auto)
    minpmi, maxpmi = profile.minpmi, profile.maxpmi
    """
    Spreading Activation Algorithm:
    F is firing threshold, D is decay factor, W is link weight
    for each unfired node [i] where A[i]>F:
        For each link [i,j] adjust A[j] = A[j] + (A[i]*W[i,j]*D)
        (cap at 1, mark all fired so they don't fire again)
        nodes with A[i]>F fire next time
    """
    toFire = category.scores.filter(fired=False,value__gte=category.threshold)
    # going back and forth between nodes and score, need to clear this up
    decay = category.decayrate
    try:
        while toFire:
            if toFire.count() > 600:
                category.addNumToStatus(str(toFire.count())+', got too big so I had to quit')
                break
            category.addNumToStatus(toFire.count())
            with transaction.commit_on_success():
                for score1 in toFire:
                    for pmi in score1.page.pmisFrom.all():
                        if score1.page != pmi.toPage:
                            score2 = pmi.toPage.categoryScore.get(category=category)
                            newValue = score2.value + (score1.value*pmi.normalized_value()*decay)
                            if newValue > 1:
                                newValue = 1.0
                            score2.value = newValue
                            score2.save()
                    score1.fired = True
                    score1.save()
                toFire = category.scores.filter(fired=False,value__gte=category.threshold)
                decay = decay**2
        category.calcMemberships()
    except Exception, e:
        raise e
    finally:
        category = Category.objects.get(id=category_id)
        category.task_id = ""
        category.active = None
        category.ready = True
        category.unread = True
        category.save()
