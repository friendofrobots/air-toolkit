"""
airtoolkit.py should hold the functions for calculating the PMI, creating
categories from seeds and discovering categories.

The trick here is to try to figure out a good way of getting the data into these
functions in a way that makes sense for a variety of data storage possibilities.
"""
import math

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
                if link[1] == rel:
                    filtered.append(link)
        return filtered

    def getNodes(self):
        return self.graph.keys()

    """
    Warning: this action is permanent for the data in memory
    """
    def filterByActivity(self,min):
        activity = dict([(item,0) for item in self.graph.keys()])
        for left, links in self.graph.iteritems():
            activity[left] += len(links)
            for right in links:
                if right not in activity:
                    activity[right] = 0
                activity[right] += 1

        purge = [item for item,n in activity.iteritems() if n < min]
        
        for item in purge:
            if item in self.graph:
                self.graph.pop(item,False)
            for left in self.graph:
                if item in self.graph[left]:
                    self.graph[left].pop(item,False)
        # temporary thing for testing
        return activity

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
                if item1 not in self.matrix:
                    self.matrix[item1] = {}
                if len(lb1.intersection(lb2)) == 0:
                    self.matrix[item1][item2] = 0
                else:
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
        for i in xrange(2):
            self.spreadActivation(i,scores)
        return scores

    def spreadActivation(self,i,scores):
        for s in scores

    def findCategories(self):
        """
        Probably use the erosion and dilation spreading activation algorithm
        from the TasteFabric paper.
        Returns a list of category vectors.
        """
        categories = [{},{}]
        return categories

def calculatePMIs(links):
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
            if item1 not in self.matrix:
                self.matrix[item1] = {}
            if len(lb1.intersection(lb2)) == 0:
                self.matrix[item1][item2] = 0
            else:
                self.matrix[item1][item2] = math.log(len(lb1.intersection(lb2))*len(links)/(len(lb1)*len(lb2)),2)

"""
for each object, create a set of objects that link to it

for each pair of objects
calculate pmi by dividing the intersection of the two sets by the product of both sets
"""
