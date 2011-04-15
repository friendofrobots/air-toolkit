from celery.decorators import task
from toolkit.models import Entity, Link, PMI
import json, urllib2, urllib, math

"""
So I need a download tasks, process them and dump them in the database
Then I need to run through and process the PMI information, ideally in
a task format so I can give progress on it.
"""

@task()
def dlUser(graphapi,fbid):
    try:
        links = []
        entities = set()
        # info
        info = graphapi.get_object(fbid)
        infoLinks, infoEntities = parseInfo(info)
        links.extend(infoLinks)
        entities.update(infoEntities)
        # likes
        likes = graphapi.get_connections(fbid,"likes")['data']
        likeLinks, likeEntities = parseLikes(likes)
        links.extend(likeLinks)
        entities.update(likeEntities)
        # interests
        interests = graphapi.get_connections(fbid,"interests")['data']
        interestLinks, interestEntities = parseInterests(interests)
        links.extend(interestLinks)
        entities.update(interestEntities)
        # friends
        args = {
            "access_token" : graphapi.access_token,
            "target_uid" : fbid,
            "format" : 'JSON',
            }
        file = urllib2.urlopen("https://api.facebook.com/method/friends.getMutualFriends?"
                              + urllib.urlencode(args))
        friends = json.load(file)
        friendLinks, friendEntities = parseFriends(friends)
        links.extend(friendLinks)
        entities.update(friendEntities)

        return entities, links
    except (ValueError,IOError,facebook.GraphAPIError,urllib2.URLError), exc:
        print exc
        dlUser.retry(exc=exc)

@task()
def saveData(join, callback=None):
    """
    Creates django objects and saves them
    """
    entities = set().update([e for (e,l) in join])
    entity = Entity.objects.create(fbid=fbid,name=name) for fbid, name in entities
    for entity, links in join:
        Link.objects.create(fromEntity=Entity.objects.get(fbid=link[0]),
                            relation=link[1],
                            weight=link[2],
                            toEntity=Entity.objects.get(fbid=link[3])) for link in links

@task()
def calculatePMIs(links, callback=None):
    linkedBy = {}
    for link in links:
        if link.toEntity.fbid not in linkedBy:
            linkedBy[link.toEntity.fbid] = set()
        linkedBy[link.toEntity.fbid].add(link.fromEntity.fbid)

    """
    PMI(i1,i2) = log(Pr(i1,i2) / Pr(i1)Pr(i2))
               = log(num(i1,i2)*totalLinks / num(i1)num(i2))
    """

    """
    pmis are symmetric, so only store the link from the one with the
      lower id to the one with the higher id (note: ids are strings,
      so the sort is alphabetical in this case)
    """
    for fbid1,lb1 in linkedBy.iteritems() if len(lb1) > 1:
        for fbid2,lb2 in linkedBy.iteritems() if fbid1 <= fbid2 and len(lb2) > 1:
            if len(lb1.intersection(lb2)) > 0:
                PMI.objects.create(fromEntity=Entity.objects.get(fbid=fbid1),
                                   toEntity=Entity.objects.get(fbid=fbid2),
                                   value=math.log(len(lb1.intersection(lb2))*len(links)/(len(lb1)*len(lb2)),2))

def parseInfo(data):
    entities = set()
    links = []
    if 'gender' in data:
        if data['gender'] == 'male':
            links.append((fbid,'gender',1,'male')
        elif data['gender'] == 'female':
            links.append((fbid,'gender',1,'female')
    if 'hometown' in data:
        self.addPage(graph,fbid,data['hometown']['id'],data['hometown']['name'],'City')
        graph.addLink(fbid,'isFrom',data['hometown']['id'])
    if 'location' in data:
        self.addPage(graph,fbid,data['location']['id'],data['location']['name'],'City')
        graph.addLink(fbid,'livesIn',data['location']['id'])
    if 'education' in data:
        for item in data['education']:
            if 'school' in item:
                self.addPage(graph,fbid,item['school']['id'],item['school']['name'],'School')
                graph.addLink(fbid,'attended',item['school']['id'])
            if 'year' in item:
                self.addPage(graph,fbid,item['year']['id'],item['year']['name'],'SchoolYear')
                graph.addLink(fbid,'graduatedIn',item['year']['id'])
            if 'concentration' in item:
                for c in item['concentration']:
                    self.addPage(graph,fbid,c['id'],c['name'],'Concentration')
                    graph.addLink(fbid,'majoredIn',c['id'])
    if 'work' in data:
        for item in data['work']:
            if 'employer' in item:
                self.addPage(graph,fbid,item['employer']['id'],item['employer']['name'],'Employer')
                graph.addLink(fbid,'workedFor',item['employer']['id'])
    if 'significant_other' in data:
        graph.addName(data['significant_other']['id'],data['significant_other']['name'])
        graph.addLink(fbid,'isInRelationshipWith',data['significant_other']['id'])
    if 'religion' in data:
        try:
            self.addPage(graph,fbid,data['religion']['id'],data['religion']['name'],'Religion')
            graph.addLink(fbid,'believesIn',data['religion']['id'])
        except:
            self.addPage(graph,fbid,data['religion'],data['religion'],'Religion')
            graph.addLink(fbid,'believesIn',data['religion'])
    if 'political' in data:
        try:
            self.addPage(graph,fbid,data['political']['id'],data['political']['name'],'PoliticalView')
            graph.addLink(fbid,'votes',data['political']['id'])
        except:
            self.addPage(graph,fbid,data['political'],data['political'],'PoliticalView')
            graph.addLink(fbid,'believesIn',data['political'])

def parseLikes(data):
    for like in data:
        self.addPage(graph,fbid,like['id'],like['name'],like['category'])
        graph.addLink(fbid,'likes',like['id'])

def parseInterests(data):
    for interest in data:
        self.addPage(graph,fbid,interest['id'],interest['name'],interest['category'])
        graph.addLink(fbid,'interests',interest['id'])

def parseFriends(data):
    for friend in data:
        graph.addLink(fbid,'isFriendsWith',friend)
