import pickle, json, sys, types, facebook
import auth_fb

class FBGraphError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Concept:
    def __init__(self, id, name, type, links=None):
        self.id = id
        self.name = name
        self.type = type
        self.links = {}
        if links:
            self.links = links

    def __str__(self):
        return self.name

    def addLink(self,key,link):
        if key not in self.links:
            self.links[key] = link
        elif type(self.links[key]) == types.ListType:
            for l in self.links[key]:
                if l[0] == link[0]:
                    return (l[0],l[1],l[2]+1)
            self.links[key].append(link)
        else:
            if self.links[key][0] == link[0]:
                self.links[key][2] += 1
                return self.links[key]
            self.links[key] = [self.links[key],link]
        return link

    def getLink(self,key):
        if key in self.links:
            if type(self.links[key]) == types.ListType:
                return [l[0] for l in self.links[key]]
            return self.links[key][0]
        else:
            return None


class FBGraph():
    def __init__(self, jsondata=None):
        self.idtable = {}
        self.concepts = []
        if jsondata:
            for c in jsondata:
                links = {}
                for key in c['links']:
                    if type(c['links'][key][0]) == types.ListType:
                        links[key] = [tuple(l) for l in c['links'][key]]
                    else:
                        links[key] = tuple(c['links'][key])
                concept = Concept(c['id'],c['name'],c['type'],links)
                self.idtable[concept.id] = concept
                self.concepts.append(concept)

        self.name = "fbgraph"
        self.filename = None
        self.ready = False

    def readyToExport(self):
        return self.ready

    def setReady(self):
        self.ready = True

    def exported(self):
        return self.filename

    def getConcepts(self):
        return self.concepts

    def getById(id):
        if id in self.idtable:
            return self.idtable[id]
        else:
            raise FBGraphError("That id isn't in the graph")

    # Download Facebook
    def dlMe(self,graph):
        mydata = graph.get_object('me')
        me = self.addProfileFromData(mydata)
        self.idtable['me'] = me
        return me

    def dlFriends(self,profileId,graph):
        count = 0
        friendData = graph.get_connections(profileId,"friends")['data']
        friends = []
        for f in friendData:
            print 'downloading friends',count,'/',len(friendData),'\r',
            sys.stdout.flush()
            while(True):
                try:
                    fdata = graph.get_object(f['id'])
                    friend = self.addProfileFromData(fdata)
                    break
                except IOError as e:
                    print e, '-- on friend', count,'/',len(friendData)
            """ Unfortunately, it doesn't look like I have permissions for this.
            while(True):
                try:
                    friendsfriends = graph.get_connections(f['id'],'friends')['data']
                    self.addFriendLinks(friend,friendsfriends)
                    break
                except IOError as e:
                    print e, '-- on friend', count,'/',len(friendData)
                except facebook.GraphAPIError as e:
                    print e, '-- on friend', count,'/',len(friendData)
                    break
            """
            friends.append(friend)
            count += 1
        print 'downloading friends',count,'/',len(friendData)
        return friends

    def dlLikes(self,profile,graph):
        likes = []
        while(True):
            try:
                for l in graph.get_connections(profile.id, "likes")['data']:
                    like = self.addPageFromData(l)
                    profile.addLink('like',(like.id,'likes',1))
                    likes.append(like)
                break
            except IOError as e:
                print e
        return likes

    def addProfileFromData(self,profiledata):
        if profiledata['id'] in self.idtable:
            profile = self.idtable[profiledata['id']]
        else:
            profile = Concept(profiledata['id'],profiledata['name'],'profile')
            links = {}
            if 'gender' in profiledata:
                profile.addLink('gender',(self.addPageFromData({
                                'name':profiledata['gender'],
                                'category':'Gender',
                                'id':profiledata['gender'],
                                }).id,'hasProperty',1))
            if 'hometown' in profiledata:
                if profiledata['hometown']['id']:
                    profile.addLink('hometown',(self.addPageFromData({
                                    'name':profiledata['hometown']['name'],
                                    'category':'City',
                                    'id':profiledata['hometown']['id'],
                                    }).id,'isFrom',1))
            if 'education' in profiledata:
                for item in profiledata['education']:
                    if 'school' in item:
                        profile.addLink('school',(self.addPageFromData({
                                        'name':item['school']['name'],
                                        'category':'School',
                                        'id':item['school']['id'],
                                        }).id,'wentTo',1))
                    if 'year' in item:
                        profile.addLink('schoolyear',(self.addPageFromData({
                                        'name':item['year']['name'],
                                        'category':'SchoolYear',
                                        'id':item['year']['id'],
                                        }).id,'graduatedIn',1))
                    if 'concentration' in item:
                        for c in item['concentration']:
                            profile.addLink('concentration',(self.addPageFromData({
                                            'name':c['name'],
                                            'category':'Concentration',
                                            'id':c['id'],
                                            }).id,'majoredIn',1))
            if 'work' in profiledata:
                for item in profiledata['work']:
                    if 'employer' in item:
                        profile.addLink('employer',(self.addPageFromData({
                                        'name':item['employer']['name'],
                                        'category':'Employer',
                                        'id':item['employer']['id'],
                                        }).id,'workedFor',1))
            if 'significant_other' in profiledata:
                if profiledata['significant_other']['id'] in self.idtable:
                    profile.addLink('significant_other',
                                    (profiledata['significant_other']['id'],'isInRelationshipWith',1))
                    self.idtable[profiledata['significant_other']['id']].addLink('significant_other',
                                                                                 (profiledata['id'],'isInRelationshipWith',1))
            if 'religion' in profiledata:
                profile.addLink('religion',(self.addPageFromData({
                                'name':profiledata['religion']['name'],
                                'category':'Religion',
                                'id':profiledata['religion']['id'],
                                }).id,'believesIn',1))
            if 'political' in profiledata:
                profile.addLink('political',(self.addPageFromData({
                                'name':profiledata['poltical']['name'],
                                'category':'PoliticalView',
                                'id':profiledata['political']['id'],
                                }).id,'votes',1))
            self.idtable[profile.id] = profile
            self.concepts.append(profile)
        return profile

    def addFriendLinks(self,profile,friends):
        for friend in friends:
            if friend['id'] in self.idtable:
                profile.addLink('friend',(friend['id'],'isFriendsWith',1))
                self.idtable[friend['id']].addLink('friend',(profile.id,'isFriendsWith',1))

    def addPageFromData(self,pageData):
        if pageData['id'] in self.idtable:
            page = self.idtable[pageData['id']]
        else:
            category = self.getorcreateCategory(pageData['category'])
            page = Concept(pageData['id'],pageData['name'],'page')
            page.addLink('category',(category.id,'isCategory',1))
            self.idtable[page.id] = page
            self.concepts.append(page)
        return page

    def getorcreateCategory(self,categoryName):
        if categoryName in self.idtable:
            return self.idtable[categoryName]
        else:
            category = Concept(categoryName,categoryName,'page')
            self.idtable[category.id] = category
            self.concepts.append(category)
            return category

    def export(self):
        filename = self.name+'.graph'
        f = open(filename,'w')
        f.close()
        with open(filename,'a') as gf:
            for concept in self.concepts:
                self.add_concept_to_graph(concept,gf)
        self.filename = filename
        return filename

    def append_to_file(self,subject,link,file):
        line = subject+'\t'+link[0]+"\t{'freq': "+str(link[2])+", 'score': 1, 'rel': u'"+link[1]+"'}\n"
        file.write(line)

    def add_concept_to_graph(self,concept,file):
        for key in concept.links:
            if type(concept.links[key]) == types.ListType:
                for link in concept.links[key]:
                    self.append_to_file(concept.id,link,file)
            else:
                self.append_to_file(concept.id,concept.links[key],file)

    def getTriples(self):
        weighted_triples = []
        for concept in self.concepts:
            for key in concept.links:
                if type(concept.links[key]) == types.ListType:
                    for link in concept.links[key]:
                        weighted_triples.append(((concept.name+'-'+concept.id[-4:],link[1],self.idtable[link[0]].name+'-'+link[0][-4:]),link[2]))
                else:
                    weighted_triples.append(((concept.name+'-'+concept.id[-4:],concept.links[key][1],self.idtable[concept.links[key][0]].name+'-'+concept.links[key][0][-4:]),concept.links[key][2]))
        return weighted_triples
        

    def save(self):
        with open(self.name+'.pickle','w') as fbgf:
            pickle.dump(self,fbgf)

    def saveData(self):
        with open(self.name+'.json','w') as fbjson:
            conceptsdata = [ {'name':concept.name,
                              'id':concept.id,
                              'type':concept.type,
                              'links':concept.links,
                              } for concept in self.concepts ]
            json.dump(conceptsdata,fbjson)

    # Edit graph capabilities
    def removeLikeFromProfile(self,profileId,pageId):
        profile = self.getById(profileId)
        page = self.getById(pageId)
        for l in profile.links['like']:
            if page.id == l[0]:
                profile.links['like'].remove(l)
                break

    def createConcept(self,name,type,keylinks):
        id = ''
        while True:
            c = 0
            if 'new'+str(c) not in self.idtable:
                id = 'new'+str(c)
                break
            c += 1
        profile = Concept(id,name,type)
        for keylink in keylinks:
            profile.addLink(keylink[0],keylink[1])
        self.concepts.append(profile)
        self.idtable[profile.id] = profile
        self.filename = None
        return profile

    def setName(self,name):
        self.name = name


class GraphBuilder:
    @staticmethod
    def buildFBGraph(fbgpickle=None,fbgjson=None):
        if fbgpickle:
            with open(fbgpickle,'rb') as fbgf:
                fbg = pickle.load(fbgf)
            return fbg
        if fbgjson:
            with open(fbgjson,'rb') as fbgf:
                jsondata = json.load(fbgf)
            return FBGraph(jsondata)
        fbgraph = FBGraph()
        token = auth_fb.get_access_token()
        graph = facebook.GraphAPI(token)
        print 'downloading me 0/1','\r',
        sys.stdout.flush()
        me = fbgraph.dlMe(graph)
        myLikes = fbgraph.dlLikes(me,graph)
        print 'downloading me 1/1'

        friends = fbgraph.dlFriends('me',graph)
        count = 0
        for friend in friends:
            print 'downloading like',count,'/',len(friends),'\r',
            sys.stdout.flush()
            fbgraph.dlLikes(friend,graph)
            count += 1
        print 'downloading like',count,'/',len(friends)
        fbgraph.setReady()
        fbgraph.save()
        print 'finished.'
        return fbgraph
