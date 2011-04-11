import json, airfb, airtoolkit, operator
from django.contrib.auth.models import User
from fbauth.models import Profile
from toolkit.models import Data

def createUserFromDataFile(filename, pk, fbid):
    graph = airfb.FBGraph()
    graph.load(filename)
    unfiltereds = json.dumps(graph.graph, ensure_ascii=False)
    print len(graph.graph),'objects before filtering'
    activity = graph.filterByActivity(3)
    print len(graph.graph),'objects after filtering'
    likes = graph.linksOfRel('likes')
    print 'number of likes',len(likes)
    pmi = airtoolkit.PMIMatrix(likes)

    print 'dumping json'
    filtereds = json.dumps(graph.graph, ensure_ascii=False)
    lookups = json.dumps(graph.lookup, ensure_ascii=False)
    p = [(graph.getName(x),
          sorted([(graph.getName(z),y[z]) for z in y],key=operator.itemgetter(1), reverse=True))
         for x,y in pmi.matrix.iteritems()]
    pmis = json.dumps(p,ensure_ascii=False)

    print 'creating django objects'
    user = User.objects.get(pk=pk)
    profile = Profile.objects.get(user=user)#, defaults={'fbid':fbid,'name':graph.lookup[fbid]})
    #profile = Profile.objects.get_or_create(user=user, defaults={'fbid':fbid,'name':graph.lookup[fbid]})
    data = Data.objects.get_or_create(profile=profile,defaults={
            'graph':unfiltereds,
            'lookup':lookups,
            'filtered_graph':filtereds,
            'pmi_matrix':pmis,
            })
    
