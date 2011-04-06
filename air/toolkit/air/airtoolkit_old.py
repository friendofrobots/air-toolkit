import graphbuilder
from csc import divisi2

class AIRToolkit:
    def __init__(self, graphfilename=None):
        # Initialize Graph either empty or from file
        if graphfilename:
            self.graph = graphbuilder.GraphBuilder.buildFBGraph(graphfilename)
        else:
            self.graph = graphbuilder.GraphBuilder.buildFBGraph()
        self.cache = {}

    # Access Objects
    def getById(self,id):
        return self.graph.idtable[id]

    def getType(self,type):
        return [concept for concept in self.graph.getConcepts() if concept.type == type]

    def getCategory(self,categoryId):
        return [concept for concept in self.graph.getConcepts()
                if 'category' in concept.links
                and concept.links['category'][0] == categoryId]

    # Build Matrix
    def getSMatrix(self):
        if 'smatrix' in self.cache:
            return self.cache['smatrix']
        graphFilename = self.graph.exported()
        if not graphFilename:
            graphFilename = self.graph.export()
            self.graph.save()
        matrix = divisi2.load(graphFilename)
        smatrix = divisi2.network.sparse_matrix(matrix, 'nodes', 'features', cutoff=1)
        self.cache['smatrix'] = smatrix
        return smatrix

    def getSVD(self,k=25,normalized=False):
        if normalized:
            return self.getSMatrix().normalize_all().svd(k=k)
        else:
            return self.getSMatrix().svd(k=k)

    # Note: checks post first, then pre, never does both.
    def getSimilarity(self, post_normalize=False, pre_normalize=False):
        if post_normalize:
            if 'sim_post' in self.cache:
                return self.cache['sim_post']
            U,S,V = self.getSVD()
            sim_post = divisi2.reconstruct_similarity(U, S, post_normalize=True)
            self.cache['sim_post'] = sim_post
            return sim_post
        if pre_normalize:
            if 'sim_pre' in self.cache:
                return self.cache['sim_pre']
            U,S,V = self.getSVD(normalized=True)
            sim_pre = divisi2.reconstruct_similarity(U, S, post_normalize=False)
            self.cache['sim_pre'] = sim_pre
            return sim_pre
        else:
            if 'sim' in self.cache:
                return self.cache['sim']
            U,S,V = self.getSVD()
            sim = divisi2.reconstruct_similarity(U, S, post_normalize=False)
            self.cache['sim'] = sim
            return sim

    def getPredictions(self):
        if 'predictions' in self.cache:
            return self.cache['predictions']
        U,S,V = self.getSVD()
        predictions = divisi2.reconstruct(U,S,V)
        self.cache['predictions'] = predictions
        return predictions

    # Use Matrix - similarity and predictions
    def topSimilarity(self,id,n=20):
        sim = self.getSimilarity(post_normalize=True)
        return [(self.getById(x[0]),x[1]) for x in sim.row_named(id).top_items(n)]

    def topPredictions(self,id,n=20):
        predictions = self.getPredictions()
        # for category, expecting id, getting category string. need to make categories pages?
        return [(x[0][1],self.getById(x[0][2]),x[1]) for x in predictions.row_named(id).top_items(n)]
    
    def compare(self,id1,id2):
        sim = self.getSimilarity(post_normalize=True)
        return sim.entry_named(id1,id2)

    # Use Matrix - categories
    def createCategory(self,ids):
        return divisi2.SparseVector.from_dict(dict([(id,1) for id in ids]))

    def categoryTopFeatures(self,category,n=20):
        category_features = divisi2.aligned_matrix_multiply(category, self.getSMatrix())
        return [(x[0][1],self.getById(x[0][2]),x[1]) for x in category_features.to_dense().top_items(n)]

    def categoryTopSimilarity(self,category,n=20):
        sim = self.getSimilarity(post_normalize=True)
        return [(self.getById(x[0]),x[1]) for x in sim.left_category(category).top_items(n)]

    def categoryTopPredictions(self,category,n=20):
        predictions = self.getPredictions()
        return [(x[0][1],self.getById(x[0][2]),x[1]) for x in predictions.left_category(category).top_items(n)]

    # Use Matrix - projections
    def project_prediction(self,id1,id2,thresh=.01):
        predictions = self.getPredictions()
        profile1 = self.getById(id1)
        profile2 = self.getById(id2)
        projected_likes = []
        for like in profile1.getLink('likes'):
            if predictions.entry_named(profile2.id, ('right', 'likes', like)) > thresh:
                projected_likes.append(self.getById(like))
        return projected_likes

    def project_brute(self,id1,id2,thresh=.5):
        sim = self.getSimilarity(post_normalize=True)
        profile1 = self.getById(id1)
        profile2 = self.getById(id2)
        projected_likes = []
        for like in profile1.getLink('like'):
            for compare in profile2.getLink('like'):
                if sim.entry_named(like.id,compare.id) > thresh:
                    projected_likes.append(like)
                    break
        return projected_likes

    # Creating new profile
    def createProfile(self,filename,profileName,keylinks):
        self.graph.setName(filename)
        profile = self.graph.createConcept(profileName,'profile',keylinks)
        self.graph.export()
        self.graph.save()
        return profile
    
