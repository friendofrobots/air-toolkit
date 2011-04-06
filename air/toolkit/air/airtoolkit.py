"""
other things to do:

finish downloader:
  
settle on graph data structure
  look up more graph models
  look up possibilities for storage
"""
class Graph(object):
    def __init__(self,data={}):
        self.graph = data
    
    def addLink(self,left,rel,right):
        if not left or not right:
            return
        if left not in self.graph:
            self.graph[left] = {}
        self.graph[left][right] = (left,rel,1,right)
        """ May not need this (or want it)
        # Add link going other way if link doesn't already exist
        if right not in self.graph:
            self.graph[right] = {}
            self.graph[right][left] = (left,rel,1,right)
        elif left not in self.graph[right]:
            self.graph[right][left] = (left,rel,1,right)
        """

    def getLinks(self,left):
        return self.graph[left]

    def getLink(self,left,right):
        return self.graph[left][right]

    def linksOfRel(self,rel):
        filtered = []
        for id1, links in self.graph.iteritems():
            for id2, link in links.iteritems():
                print link[1],rel
                if link[1] == rel:
                    filtered.append(link)
        return filtered

    def getNodes(self):
        return self.graph.keys()

    """
    Warning: this action is permanent for the data in memory
    """
    def filterByActivity(self,min):
        purge = []
        for left, links in self.graph.iteritems():
            if len(self.graph[left]) < min:
                purge.append(left)
        for item in purge:
            self.graph.pop(item,False)
            for left, links in self.graph.iteritems():
                links.pop(item,False)


class PMIMatrix(object):
    def __init__(self,links):
        self.matrix = {}
        linkedBy = {}
        for link in links:
            if link[3] not in linkedBy:
                linkedBy[link[3]] = set()
            linkedBy[link[3]].add(link[0])

        """
        PMI(i1,i2) = log(Pr(i1,i2) / Pr(i1)Pr(i2))
                   = log(num(i1,i2)*totalLinks / num(i1)num(i2))
        """
        for item1,lb1 in linkedBy.iteritems():
            for item2,lb2 in linkedBy.iteritems():
                self.matrix[item1][item2] = math.log(len(lb1.intersection(lb2))*len(links)/(len(lb1)*len(lb2)),2)

    def getVector(self,o):
        return self.matrix[o]

    def get(self,o,p):
        return self.matrix[o][p]

    def createCategory(self,seed):
        """
        Start by setting the seed objects' category scores to 1.
        Then spread activation from those starting nodes for n iterations.
        Returns a dict mapping objects to their category scores.
        """
        scores = dict([(o,0) for o in self.matrix])
        for o in seed:
            scores[o] = 1
        for i in xrange(10):
            self.spreadActivation(scores)
        return scores

    def findCategories(self):
        """
        Probably use the erosion and dilation spreading activation algorithm
        from the TasteFabric paper.
        Returns a list of category vectors.
        """
        categories = [{},{}]
        return categories
