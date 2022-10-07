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
from math import ceil
import pandas as pd
from qgis.core import *
from qgis.gui import *
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
from qgis.core import QgsProject
import processing
##MIN MAX CLUSTERING
#REFERENCE - https://github.com/Behrouz-Babaki/MinSizeKmeans/blob/master/minsize_kmeans/minmax_kmeans.py
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

class ConstrainedKMeansAlgorithm(QgsProcessingAlgorithm):
    """Calculates the 2D distance based k-means cluster number for each input feature"""
    INPUT = 'INPUT'
    
    MINPOINTS = 'MINPOINTS'
    OUTPUT = 'OUTPUT'
    OUTPUT_CENTERS = 'OUTPUT_CENTERS'
    MAXPOINTS = 'MAXPOINTS'
    MAX_ITER = 'MAX_ITER'
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
                'MINPOINTS',
                self.tr('Miminum Number of Points per Cluster'),
                QgsProcessingParameterNumber.Integer,
                8, False, 1
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MAXPOINTS',
                self.tr('Maximum Number of Points per Cluster'),
                QgsProcessingParameterNumber.Integer,
                24, False, 1
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'MAX_ITER',
                self.tr('Maximum Number of Iterations'),
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
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_CENTERS,
                'Centroids',
                QgsProcessing.TypeVectorAnyGeometry
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source= self.parameterAsSource(parameters, self.INPUT, context)
        
        minpoints = self.parameterAsInt(parameters, self.MINPOINTS, context)
        maxpoints = self.parameterAsInt(parameters, self.MAXPOINTS, context)
        max_iter = self.parameterAsInt(parameters, self.MAX_ITER, context)
        
        cols = [f.name() for f in source.fields()]
        datagen = ([f[col] for col in cols] for f in source.getFeatures())
        df = pd.DataFrame.from_records(data=datagen, columns=cols)
        
        k = ceil((df["PON_HOMES"].sum())/maxpoints)
        
        outputFields = source.fields()
        outputFieldsCenter = source.fields()
        
        newFields = QgsFields()
        newFields.append(QgsField('CLUSTER_ID', QVariant.Int))
        newFields.append(QgsField('CLUSTER_SIZE', QVariant.Int))
        
        newFields_center = QgsFields()
        newFields_center.append(QgsField('CLUSTER_ID', QVariant.Int))
        
        outputFields = QgsProcessingUtils.combineFields(outputFields, newFields)
        outputFieldsCenter = QgsProcessingUtils.combineFields(outputFieldsCenter, newFields_center)
        
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            outputFields,
            source.wkbType(),
            source.sourceCrs()
            )
        sink_center, dest_id_center = self.parameterAsSink(
            parameters,
            self.OUTPUT_CENTERS,
            context,
            outputFieldsCenter,
            source.wkbType(),
            source.sourceCrs()
            )
        feedback.pushInfo(self.tr( "Collecting input points"))
        
        features = [f for f in source.getFeatures()]
        data = []
        new_features = []
        for f in range(len(features)):
            conn_cnt = int(features[f]["PON_HOMES"])
            while(conn_cnt):
                obj = features[f]
                obj["PON_HOMES"] = 1
                geometry = obj.geometry()
                if geometry.wkbType() == QgsWkbTypes.Point:
                    point = geometry
                else:
                    point = geometry.centroid()
                
                data.append([point.asPoint().x(), point.asPoint().y()])
                conn_cnt-=1
                new_features.append(obj)
        features = new_features[:]
            
        #print(data)
        if(len(data)==df["PON_HOMES"].sum()):
            feedback.pushInfo(self.tr("Connections Validated!"))
        else:
            feedback.pushInfo(self.tr("Connections Not Validated!"))
            feedback.pushInfo(self.tr(f"Length of data = {len(data)}"))
            feedback.pushInfo(self.tr(f"Connection Sum is = {df['PON_HOMES'].sum()}"))
        feedback.pushInfo(self.tr( f"Total Clusters are {k}"))
        feedback.pushInfo(self.tr( "Input ready"))
        feedback.pushInfo(self.tr( "Computing clusters"))
        
        print("MinimumPoints =",minpoints)
        print("MaximumPoints =",maxpoints)
        #demand = [minpoints] * k
        
        best = None
        best_clusters = None
        best_centers = None
        for i in range(max_iter):
            print("Current Iteration -",i)
            clusters, centers = minsize_kmeans(data, k, 
                                               minpoints, maxpoints)
            if clusters:
                quality = compute_quality(data, clusters)
                if not best or (quality < best):
                    best = quality
                    best_clusters = clusters
                    best_centers = centers
        
        print("DONE")
        if best:
            
            print('cluster assignments:')
            for i in range(len(best_clusters)):
                print('%d: %d'%(i, best_clusters[i]))
            print("Centers Value")
            print(best_centers)
            print('sum of squared distances: %.4f'%(best))
        else:
            print('no clustering found')
        
        feedback.pushInfo(self.tr( "Clusters ready"))

        # M is the cluster assignment for the data points
        # Compute cluster sizes
        M = np.array(best_clusters)
        sorted_M = np.sort(M)
        sizes = [len(list(group)) for key, group in groupby(sorted_M)]
        
        print("Features =",features)
        for index, out_f in enumerate(features):
            attributes = out_f.attributes()
            cluster_id = M[index].item()
            #print(attributes)
            attributes.append(cluster_id + 1)
            attributes.append(sizes[cluster_id])

            out_f.setAttributes(attributes)
            sink.addFeature(out_f, QgsFeatureSink.FastInsert)
        cluster_id = 0
        
        for center in best_centers:
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(center[0], center[1])))
            
            attributes = [None for x in range(len(cols))]
            attributes.append(cluster_id + 1)
            #print(attributes)
            
            f.setAttributes(attributes)
            sink_center.addFeature(f, QgsFeatureSink.FastInsert)
            cluster_id += 1
            
        return {self.OUTPUT: sink,self.OUTPUT_CENTERS:sink_center} 

    def name(self):
        return 'min_max_kmeans'

    def displayName(self):
        return self.tr('Min Max K-Means Clustering')
        
    def shortHelpString(self):
        return self.tr('Min Max K-Means Clustering algorithm PyQGIS implementation')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConstrainedKMeansAlgorithm()


