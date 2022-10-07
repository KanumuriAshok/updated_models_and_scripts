import networkx as nx
import numpy as np
from itertools import groupby
from PyQt5.QtCore import QCoreApplication, QVariant
import pulp
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, 
    QgsProcessingParameterFeatureSource, QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,QgsFields, QgsField, QgsWkbTypes,
    QgsFeatureSink, QgsProcessingUtils)
import random

class ConstrainedKMeansAlgorithm(QgsProcessingAlgorithm):
    """Calculates the 2D distance based k-means cluster number for each input feature"""
    INPUT = 'INPUT'
    CLUSTERS = 'CLUSTERS'
    MINPOINTS = 'MINPOINTS'
    OUTPUT = 'OUTPUT'
    MAXPOINTS = 'MAXPOINTS'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                self.tr('Input Layer'),
                types=[QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                'CLUSTERS',
                self.tr('Number of Clusters'),
                QgsProcessingParameterNumber.Integer,
                5, False, 1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                'MINPOINTS',
                self.tr('Miminum Number of Points per Cluster'),
                QgsProcessingParameterNumber.Integer,
                1, False, 1
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MAXPOINTS',
                self.tr('Maximum Number of Points per Cluster'),
                QgsProcessingParameterNumber.Integer,
                1, False, 1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Clusters',
                QgsProcessing.TypeVectorAnyGeometry
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source= self.parameterAsSource(parameters, self.INPUT, context)
        k = self.parameterAsInt(parameters, self.CLUSTERS, context)
        minpoints = self.parameterAsInt(parameters, self.MINPOINTS, context)
        maxpoints = self.parameterAsInt(parameters, self.MAXPOINTS, context)
        
        outputFields = source.fields()
        newFields = QgsFields()
        newFields.append(QgsField('CLUSTER_ID', QVariant.Int))
        newFields.append(QgsField('CLUSTER_SIZE', QVariant.Int))

        outputFields = QgsProcessingUtils.combineFields(outputFields, newFields)
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            outputFields,
            source.wkbType(),
            source.sourceCrs()
            )
        feedback.pushInfo(self.tr( "Collecting input points"))
        
        features = [f for f in source.getFeatures()]
        data = []
        for f in features:
            geometry = f.geometry()
            if geometry.wkbType() == QgsWkbTypes.Point:
                point = geometry
            else:
                point = geometry.centroid()
            
            data.append([point.asPoint().x(), point.asPoint().y()])
        
        feedback.pushInfo(self.tr( "Input ready"))
        feedback.pushInfo(self.tr( "Computing clusters"))
        
        print("MinimumPoints =",minpoints)
        print("MaximumPoints =",maxpoints)
        demand = [minpoints] * k
        C, M, f = constrained_kmeans(data, demand)
        best = None
        best_clusters = None
        for i in range(10):
            print(i)
            clusters, centers = minsize_kmeans(data, k, 
                                               minpoints, maxpoints)
            if clusters:
                quality = compute_quality(data, clusters)
                if not best or (quality < best):
                    best = quality
                    best_clusters = clusters
        print("DONE")
        if best:
            
            print('cluster assignments:')
            for i in range(len(best_clusters)):
                print('%d: %d'%(i, best_clusters[i]))
            print('sum of squared distances: %.4f'%(best))
        else:
            print('no clustering found')
        
        feedback.pushInfo(self.tr( "Clusters ready"))

        # M is the cluster assignment for the data points
        # Compute cluster sizes
        sorted_M = np.sort(M)
        sizes = [len(list(group)) for key, group in groupby(sorted_M)]
    
        
        for index, out_f in enumerate(features):
            attributes = out_f.attributes()
            cluster_id = M[index].item()
            attributes.append(cluster_id + 1)
            attributes.append(sizes[cluster_id])

            out_f.setAttributes(attributes)
            sink.addFeature(out_f, QgsFeatureSink.FastInsert)
        return {self.OUTPUT: sink} 

    def name(self):
        return 'constrained_kmeans'

    def displayName(self):
        return self.tr('Min Max K-Means Clustering')
        
    def shortHelpString(self):
        return self.tr('Constrained K-Means Clustering algorithm PyQGIS implementation')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConstrainedKMeansAlgorithm()

# Code adapted from https://adared.ch/constrained-k-means-implementation-in-python/
def constrained_kmeans(data, demand, maxiter=None, fixedprec=1e9):
  data = np.array(data)
  
  min_ = np.min(data, axis = 0)
  max_ = np.max(data, axis = 0)
  
  C = min_ + np.random.random((len(demand), data.shape[1])) * (max_ - min_)
  M = np.array([-1] * len(data), dtype=np.int)
  
  itercnt = 0
  while True:
    itercnt += 1
    
    # memberships
    g = nx.DiGraph()
    g.add_nodes_from(range(0, data.shape[0]), demand=-1) # points
    for i in range(0, len(C)):
      g.add_node(len(data) + i, demand=demand[i])
    
    # Calculating cost...
    cost = np.array([np.linalg.norm(np.tile(data.T, len(C)).T - np.tile(C, len(data)).reshape(len(C) * len(data), C.shape[1]), axis=1)])
    # Preparing data_to_C_edges...
    data_to_C_edges = np.concatenate((np.tile([range(0, data.shape[0])],
    len(C)).T, np.tile(np.array([range(data.shape[0], data.shape[0] +
    C.shape[0])]).T, len(data)).reshape(len(C) * len(data), 1), cost.T *
    fixedprec), axis=1).astype(np.uint64) # Adding to graph
    g.add_weighted_edges_from(data_to_C_edges)
    

    a = len(data) + len(C)
    g.add_node(a, demand=len(data)-np.sum(demand))
    C_to_a_edges = np.concatenate((np.array([range(len(data), len(data) + len(C))]).T, np.tile([[a]], len(C)).T), axis=1)
    g.add_edges_from(C_to_a_edges)
    
    
    # Calculating min cost flow...
    f = nx.min_cost_flow(g)
    
    # assign
    M_new = np.ones(len(data), dtype=np.int) * -1
    for i in range(len(data)):
      p = sorted(f[i].items(), key=lambda x: x[1])[-1][0]
      M_new[i] = p - len(data)
      
    # stop condition
    if np.all(M_new == M):
      # Stop
      return (C, M, f)
      
    M = M_new
      
    # compute new centers
    for i in range(len(C)):
      C[i, :] = np.mean(data[M==i, :], axis=0)
      
    if maxiter is not None and itercnt >= maxiter:
      # Max iterations reached
      return (C, M, f)

##MIN MAX CLUSTERING
def l2_distance(point1, point2):
    return sum([(float(i)-float(j))**2 for (i,j) in zip(point1, point2)])

class subproblem(object):
    def __init__(self, centroids, data, min_size, max_size):

        self.centroids = centroids
        self.data = data
        self.min_size = min_size
        self.max_size= max_size
        self.n = len(data)
        self.k = len(centroids)

        self.create_model()

    def create_model(self):
        def distances(assignment):
            return l2_distance(self.data[assignment[0]], self.centroids[assignment[1]])

        clusters = list(range(self.k))
        assignments = [(i, j)for i in range(self.n) for j in range(self.k)]

        # outflow variables for data nodes
        self.y = pulp.LpVariable.dicts('data-to-cluster assignments',
                                  assignments,
                                  lowBound=0,
                                  upBound=1,
                                  cat=pulp.LpInteger)

        # outflow variables for cluster nodes
        self.b = pulp.LpVariable.dicts('cluster outflows',
                                  clusters,
                                  lowBound=0,
                                  upBound=self.n-self.min_size,
                                  cat=pulp.LpContinuous)

        # create the model
        self.model = pulp.LpProblem("Model for assignment subproblem", pulp.LpMinimize)

        # objective function
        self.model += pulp.lpSum([distances(assignment) * self.y[assignment] for assignment in assignments])

        # flow balance constraints for data nodes
        for i in range(self.n):
            self.model += pulp.lpSum(self.y[(i, j)] for j in range(self.k)) == 1

        # flow balance constraints for cluster nodes
        for j in range(self.k):
            self.model += pulp.lpSum(self.y[(i, j)] for i in range(self.n)) - self.min_size == self.b[j]
            
        # capacity constraint on outflow of cluster nodes
        for j in range(self.k):
            self.model += self.b[j] <= self.max_size - self.min_size 

        # flow balance constraint for the sink node
        self.model += pulp.lpSum(self.b[j] for j in range(self.k)) == self.n - (self.k * self.min_size)


    def solve(self):
        self.status = self.model.solve()

        clusters = None
        if self.status == 1:
            clusters= [-1 for i in range(self.n)]
            for i in range(self.n):
                for j in range(self.k):
                    if self.y[(i, j)].value() > 0:
                        clusters[i] = j
        return clusters

def initialize_centers(dataset, k):
    ids = list(range(len(dataset)))
    random.shuffle(ids)
    return [dataset[id] for id in ids[:k]]

def compute_centers(clusters, dataset):
    # canonical labeling of clusters
    ids = list(set(clusters))
    c_to_id = dict()
    for j, c in enumerate(ids):
        c_to_id[c] = j
    for j, c in enumerate(clusters):
        clusters[j] = c_to_id[c]

    k = len(ids)
    dim = len(dataset[0])
    centers = [[0.0] * dim for i in range(k)]
    counts = [0] * k
    for j, c in enumerate(clusters):
        for i in range(dim):
            centers[c][i] += dataset[j][i]
        counts[c] += 1
    for j in range(k):
        for i in range(dim):
            centers[j][i] = centers[j][i]/float(counts[j])
    return clusters, centers

def minsize_kmeans(dataset, k, min_size=0, max_size=None):
    n = len(dataset)
    if max_size == None:
        max_size = n

    centers = initialize_centers(dataset, k)
    clusters = [-1] * n

    converged = False
    while not converged:
        m = subproblem(centers, dataset, min_size, max_size)
        clusters_ = m.solve()
        if not clusters_:
            return None, None
        clusters_, centers = compute_centers(clusters_, dataset)

        converged = True
        i = 0
        while converged and i < len(dataset):
            if clusters[i] != clusters_[i]:
                converged = False
            i += 1
        clusters = clusters_

    return clusters, centers

def read_data(datafile):
    data = []
    with open(datafile, 'r') as f:
        for line in f:
            line = line.strip()
            if line != '':
                d = [float(i) for i in line.split()]
                data.append(d)
    return data

def cluster_quality(cluster):
    if len(cluster) == 0:
        return 0.0

    quality = 0.0
    for i in range(len(cluster)):
        for j in range(i, len(cluster)):
            quality += l2_distance(cluster[i], cluster[j])
    return quality / len(cluster)

def compute_quality(data, cluster_indices):
    clusters = dict()
    for i, c in enumerate(cluster_indices):
        if c in clusters:
            clusters[c].append(data[i])
        else:
            clusters[c] = [data[i]]
    return sum(cluster_quality(c) for c in clusters.values())