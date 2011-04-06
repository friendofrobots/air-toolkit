from celery.decorators import task
from celery.task.sets import TaskSet
from celery.task.http import URL
import celery, json, facebook, airtoolkit, urllib2, urllib

class Downloader(object):
    def startDownload(self, access_token):
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
        self.result = result

    def status(self):
        return (self.result.completed_count(), self.result.total)

    def ready(self):
        return self.result.ready()

    def get(self):
        """
        Caution: get will *wait* for taskset to finish.
        """
        graph = self.createGraph(self.result.join())
        graph.addName('me',self.me['id'])
        graph.save(self.me['id']+'-graph.json')
        return graph

    def addPage(self,graph,fbid,objectid,objectname,category):
        new = graph.addName(objectid,objectname)
        graph.addName(category,category)
        if new:
            graph.addLink(objectid,'category',category)

    def createGraph(self, join):
        graph = FBGraph()
        for fbid, type, data in join:
            if type == 'info':
                graph.addName(fbid,data['name'])
                if 'gender' in data:
                    if data['gender'] == 'male':
                        graph.addLink(fbid,'gender','male')
                    elif data['gender'] == 'female':
                        graph.addLink(fbid,'gender','female')
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
                """
                Can't have two links between the same two objects, so this would override a friendship
                if 'significant_other' in data:
                    graph.addName(data['significant_other']['id'],data['significant_other']['name'])
                    graph.addLink(fbid,'isInRelationshipWith',data['significant_other']['id'])
                """
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
            elif type == 'friends':
                for friend in data:
                    graph.addLink(fbid,'isFriendsWith',friend)
            elif type == 'likes':
                for like in data:
                    self.addPage(graph,fbid,like['id'],like['name'],like['category'])
                    graph.addLink(fbid,'likes',like['id'])
            elif type == 'interests':
                for interest in data:
                    self.addPage(graph,fbid,interest['id'],interest['name'],interest['category'])
                    graph.addLink(fbid,'interests',interest['id'])
        return graph
        

class FBGraph(airtoolkit.Graph):
    def __init__(self):
        """
        The graph is a dictionary matching nodes to lists of outgoing edges.
        The edges are tuples: (type, score, object)
        The graph for Facebook also holds a table mapping facebook ids to names.
        """
        super(FBGraph,self).__init__()
        self.lookup = {}
        self.lookup['male'] = 'male'
        self.lookup['female'] = 'female'
        self.addLink('male','category','Gender')
        self.addLink('female','category','Gender')

    def addName(self,fbid,name):
        if not fbid or not name:
            return
        if fbid not in self.lookup:
            self.lookup[fbid] = name
            return True
        else:
            return False
        
    def getName(self, fbid):
        return self.lookup[fbid]

    def save(self,filename):
        with open(filename,'w') as graphjson:
            data = {'graph':self.graph,
                    'lookup':self.lookup}
            json.dump(data,graphjson, sort_keys=True, indent=4)

    def load(self, filename):
        with open(filename,'r') as graphjson:
            data = json.load(graphjson,encoding='UTF-8')
        self.graph = dict(data['graph'])
        self.lookup = dict(data['lookup'])

@task()
def dlInfo(graphapi,fbid):
    try:
        info = graphapi.get_object(fbid)
    except (IOError,facebook.GraphAPIError), exc:
        print exc
        dlInfo.retry(exc=exc)
    return (fbid, 'info', info)

@task()
def dlLikes(graphapi,fbid):
    try:
        likes = graphapi.get_connections(fbid,"likes")['data']
    except (IOError,facebook.GraphAPIError,Exception), exc:
        print exc
        dlLikes.retry(exc=exc)
    return (fbid, 'likes', likes)

@task()
def dlInterests(graphapi,fbid):
    try:
        interests = graphapi.get_connections(fbid,"interests")['data']
    except (IOError,facebook.GraphAPIError,Exception), exc:
        print exc
        dlInterests.retry(exc=exc)
    return (fbid, 'interests', interests)

@task()
def dlFriends(graphapi,fbid):
    try:
        args = {}
        args["access_token"] = graphapi.access_token
        args["target_uid"] = fbid
        args["format"] = 'JSON'
        file = urllib2.urlopen("https://api.facebook.com/method/friends.getMutualFriends?"
                              + urllib.urlencode(args))
        try:
            friends = json.load(file)
        except ValueError, exc:
            dlFriends.retry(exc=exc)
        finally:
            file.close()
        if len(friends) < 1:
            print 'empty friends', friends
        return (fbid, 'friends', friends)
    except (IOError,urllib2.URLError,Exception), exc:
        print exc
        dlFriends.retry(exc=exc)
    except facebook.GraphAPIError, exc:
        print "Permissions issues here", exc
        return (fbid,'friends',{})

"""
Commands for starting rabbitmql and celery
sudo rabbitmq-server -detached
celeryd --loglevel=INFO
"""
