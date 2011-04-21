from celery.decorators import task
from celery.task.sets import TaskSet
from toolkit.models import Entity, Link, PMI
import json, urllib2, urllib, math, facebook

"""
So I need a download tasks, process them and dump them in the database
Then I need to run through and process the PMI information, ideally in
a task format so I can give progress on it.
"""

@task()
def dlUser(graphapi,fbid):
    try:
        entities = set()
        links = set()
        # info
        info = graphapi.get_object(fbid)
        infoEntities, infoLinks = parseInfo(fbid,info)
        entities.update(infoEntities)
        links.update(infoLinks)
        # likes
        likes = graphapi.get_connections(fbid,"likes")['data']
        likeEntities, likeLinks = parseLikes(fbid,likes)
        entities.update(likeEntities)
        links.update(likeLinks)
        # interests
        interests = graphapi.get_connections(fbid,"interests")['data']
        interestEntities, interestLinks = parseInterests(fbid,interests)
        entities.update(interestEntities)
        links.update(interestLinks)
        # friends
        args = {
            "access_token" : graphapi.access_token,
            "target_uid" : fbid,
            "format" : 'JSON',
            }
        file = urllib2.urlopen("https://api.facebook.com/method/friends.getMutualFriends?"
                              + urllib.urlencode(args))
        friends = json.load(file)
        friendEntities, friendLinks = parseFriends(fbid,friends)
        entities.update(friendEntities)
        links.update(friendLinks)

        return entities, links
    except (ValueError,IOError,facebook.GraphAPIError,urllib2.URLError), exc:
        print exc
        dlUser.retry(exc=exc)

@task(ignore_result=True)
def saveUserData(join, profile, callback=None):
    """
    Creates django objects and saves them
    TODO: filter for entities with less than 2 like links
    """
    entities = set()
    for e,l in join:
        entities.update(e)
    for fbid,name in entities:
        Entity.objects.get_or_create(
            owner=profile,
            fbid=fbid,
            name=name)
    for entity, links in join:
        for link in links:
            try:
                Link.objects.create(
                    owner=profile,
                    fromEntity=Entity.objects.get(fbid=link[0]),
                    relation=link[1],
                    weight=link[2],
                    toEntity=Entity.objects.get(fbid=link[3]))
            except Exception, e:
                print e
                print link
                raise Exception()

@task(ignore_result=True)
def calcPMIs(links, callback=None):
    linkedBy = {}
    for link in links:
        if link.toEntity.fbid not in linkedBy:
            linkedBy[link.toEntity.fbid] = set()
        linkedBy[link.toEntity.fbid].add(link.fromEntity.fbid)

    """
    Pmi(i1,i2) = log(Pr(i1,i2) / Pr(i1)Pr(i2))
               = log(num(i1,i2)*totalLinks / num(i1)num(i2))
    """

    """
    pmis are symmetric, so only store the link from the one with the
      lower id to the one with the higher id (note: ids are strings,
      so the sort is alphabetical in this case)
    """
    for fbid1,lb1 in linkedBy.iteritems():
        for fbid2,lb2 in linkedBy.iteritems():
            if fbid1 <= fbid2 and len(lb1.intersection(lb2))>0:
                PMI.objects.get_or_create(
                    owner=profile,
                    fromEntity=Entity.objects.get(fbid=fbid1),
                    toEntity=Entity.objects.get(fbid=fbid2),
                    value=math.log(len(lb1.intersection(lb2))*len(links)/(len(lb1)*len(lb2)),2))

def parseInfo(fbid,data):
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

def parseLikes(fbid,data):
    entities,links = set(),set()
    for like in data:
        e,l = parseLink(fbid,
                        like['id'],
                        like['name'],
                        'likes',1,like['category'])
        entities.update(e)
        links.update(l)
    return entities, links

def parseInterests(fbid,data):
    entities,links = set(),set()
    for interest in data:
        e,l = parseLink(fbid,
                        interest['id'],
                        interest['name'],
                        'isInterestedIn',1,interest['category'])
        entities.update(e)
        links.update(l)
    return entities, links

def parseFriends(fbid,data):
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

