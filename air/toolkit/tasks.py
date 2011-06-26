from django.db.models import Count, Q, Max, Min
from django.db import transaction
from celery.decorators import task
from celery.result import TaskSetResult
from toolkit.models import DownloadStatus, Person, Page, PMI, Category, CategoryScore, CategoryMembership
from fbauth.models import Profile
import json, urllib2, urllib, math, facebook

from celery.task.sets import TaskSet

"""
So I need a download tasks, process them and dump them in the database
Then I need to run through and process the PMI information, ideally in
a task format so I can give progress on it.
"""        

@task(ignore_result=True)
def dlUser(profile_id,graphapi,fbid,name):
    try:
        profile = Profile.objects.get(id=profile_id)
        person = Person.objects.create(owner=profile,
                                       fbid=fbid,
                                       name=name)

        likes = graphapi.get_connections(fbid,"likes")['data']
        for like in likes:
            if len(like['name']) > 180:
                like['name'] = like['name'][:180]
            page, success = Page.objects.get_or_create(
                owner=profile,
                fbid=like['id'],
                defaults={
                    'name':like['name'],
                    'category':like['category']
                    })
            person.likes.add(page)

        interests = graphapi.get_connections(fbid,"interests")['data']
        for interest in interests:
            page, success = Page.objects.get_or_create(
                owner=profile,
                fbid=interest['id'],
                defaults={
                    'name':interest['name'],
                    'category':interest['category']
                    })
            person.likes.add(page)

    except (ValueError,IOError,facebook.GraphAPIError,urllib2.URLError), exc:
        print exc
        dlUser.retry(countdown=15, max_retries=None, throw=False)

@task(ignore_result=True)
def checkTaskSet(taskset_id,profile_id,status_id):
    result = TaskSetResult.restore(taskset_id)
    if result.ready():
        profile = Profile.objects.get(id=profile_id)
        pages = Page.objects.filter(owner=profile).annotate(activity=Count('likedBy')).filter(activity__gt=1)
        numpeople = Person.objects.filter(likes__in=pages).distinct().count()

        subtasks = [calcPMIs.subtask((profile_id,page.id,pages,numpeople)) for page in pages]
        r = TaskSet(tasks=subtasks).apply_async()
        r2 = checkPMISet.delay(r.taskset_id,profile.id,status_id)
        status = DownloadStatus.objects.get(id=status_id)
        status.numpeople = numpeople
        status.stage = 2
        status.task_id = r.task_id
        status.save()
    else:
        checkTaskSet.retry(countdown=15, max_retries=None)

def testPMIs(profile_id,status_id):
    profile = Profile.objects.get(id=profile_id)
    pages = Page.objects.filter(owner=profile).annotate(activity=Count('likedBy')).filter(activity__gt=1)
    numpeople = Person.objects.filter(likes__in=pages).distinct().count()

    subtasks = [calcPMIs.subtask((profile_id,page.id,pages,numpeople)) for page in pages]
    r = TaskSet(tasks=subtasks).apply_async()
    r2 = checkPMISet.delay(r.taskset_id,profile.id,status_id)
    status = DownloadStatus.objects.get(id=status_id)
    status.stage = 2
    status.task_id = r.task_id
    status.save()

@task(ignore_result=True)
def calcPMIs(profile_id, page_id1, pages, numpeople):
    """
    Pmi(i1,i2) = log(Pr(i1,i2) / Pr(i1)Pr(i2))
               = log(num(i1,i2)*totalPeople / num(i1)num(i2))

    pmis are symmetric, so only store the link from the one with the
      lower id to the one with the higher id (note: ids are strings,
      so the sort is alphabetical in this case)
    """
    profile = Profile.objects.get(id=profile_id)
    fromPage = Page.objects.get(id=page_id1)
    with transaction.commit_on_success():
        for toPage in pages:
            intersect = fromPage.likedBy.filter(id__in=[lb.id for lb in toPage.likedBy.all()]).distinct().count()
            if intersect>0:
                PMI.objects.get_or_create(
                    owner=profile,
                    fromPage=fromPage,
                    toPage=toPage,
                    value=math.log(1.*intersect*numpeople/(fromPage.likedBy.count()*toPage.likedBy.count()),2))
    downloadStatus = profile.downloadStatus
    agg = PMI.objects.filter(owner=profile).aggregate(Min('value'),Max('value'))
    downloadStatus.minpmi, downloadStatus.maxpmi = agg['value__min'],agg['value__max']
                    
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

@task(ignore_result=True)
def createCategory(profile_id, category_id,
                   startvalue, threshold, decayrate):
    profile = Profile.objects.get(id=profile_id)
    category = Category.objects.get(id=category_id)
    if not category.scores.exists():
        pages = Page.objects.filter(owner=profile).annotate(activity=Count('likedBy')).filter(activity__gt=1)
        for page in pages:
            CategoryScore.objects.get_or_create(owner=profile,
                                         category=category,
                                         page=page)
    category.startvalue = startvalue
    category.threshold = threshold
    category.decayrate = decayrate
    category.status = ""
    category.save()
    category.scores.update(value=0.0,fired=False)
    downloadStatus = profile.downloadStatus
    minpmi, maxpmi = downloadStatus.minpmi, downloadStatus.maxpmi
    """
    Spreading Activation Algorithm:
    F is firing threshold, D is decay factor, W is link weight
    for each unfired node [i] where A[i]>F:
        For each link [i,j] adjust A[j] = A[j] + (A[i]*W[i,j]*D)
        (cap at 1, mark all fired so they don't fire again)
        nodes with A[i]>F fire next time
    """
    category.scores.filter(page__in=category.seeds.all()).update(value=startvalue)
    toFire = category.scores.filter(fired=False,value__gte=threshold)
    # going back and forth between nodes and score, need to clear this up
    try:
        while toFire:
            if toFire.count() > 400:
                category.addNumToStatus(str(toFire.count())+', got too big so I had to quit')
                break
            category.addNumToStatus(toFire.count())
            with transaction.commit_on_success():
                for score1 in toFire:
                    for pmi in score1.page.pmisFrom.all():
                        if score1.page != pmi.toPage:
                            score2 = pmi.toPage.categoryScore.get(category=category)
                            newValue = score2.value + (score1.value*pmi.normalized_value()*decayrate)
                            if newValue > 1:
                                newValue = 1.0
                            score2.value = newValue
                            score2.save()
                    score1.fired = True
                    score1.save()
                toFire = category.scores.filter(fired=False,value__gte=threshold)
                decayrate = decayrate**2
        calcMemberships(profile.id, category.id)
    finally:
        category.task_id = ""
        category.active = None
        category.save()

@task(ignore_result=True)
def calcMemberships(profile_id, category_id):
    profile = Profile.objects.get(id=profile_id)
    category = Category.objects.get(id=category_id)

    with transaction.commit_on_success():
        for person in Person.objects.filter(owner=profile):
            membership = 0
            for score in category.scores.filter(page__in=person.likes.all()):
                membership += score.value
            CategoryMembership.objects.get_or_create(
                owner=profile,
                category=category,
                member=person,
                value=membership)
