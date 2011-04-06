import airfb, airtoolkit, sys, time#, pygraph.readwrite.dot, pygraph.classes.graph

def downloadPrint(access_token):
    downloader = Downloader()
    print 'Starting download'
    downloader.startDownload(access_token)

    while (not downloader.ready()):
        status = downloader.status()
        r = 1.0 * status[0] / status[1]
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

    graph = downloader.get()
    return graph

def makeGraph(filename):
    sys.path.append('..')
    sys.path.append('/usr/local/lib/graphviz/python/')
    import gv
    graph = airfb.FBGraph()
    graph.load(filename)
    print 'filtering'
    graph.filterByActivity(3)

    gr = pygraph.classes.graph.graph()
    print 'creating graph'
    for node in graph.getNodes():
        gr.add_node(graph.getName(node)+'-'+node[-4:])
    for node1 in graph.getNodes():
        for node2,link in graph.getLinks(node1).iteritems():
            if not gr.has_edge((graph.getName(node1)+'-'+node1[-4:],
                         graph.getName(node2)+'-'+node2[-4:])):
                gr.add_edge((graph.getName(node1)+'-'+node1[-4:],
                             graph.getName(node2)+'-'+node2[-4:]),
                            wt=link[2],
                            label=link[1])
    print 'writing'
    dot = pygraph.readwrite.dot.write(gr)
    gvv = gv.readstring(dot)
    print 'layout'
    gv.layout(gvv,'dot')
    print 'rendering'
    gv.render(gvv,'png',graph.getName('me')+'.png')

def getPMI(filename):
    graph = airfb.FBGraph()
    graph.load(filename)
    print len(graph.graph),'objects before filtering'
    activity = graph.filterByActivity(3)
    print len(graph.graph),'objects after filtering'
    likes = graph.linksOfRel('likes')
    print 'number of likes',len(likes)
    pmi = airtoolkit.PMIMatrix(likes)
    return graph, activity, pmi