"""
Model exported as python.
Name : clustergrpouing_A
Group : 
With QGIS : 31604
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class Clustergrpouing_a(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'DEMAND_POINTS', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetlines', 'street lines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cluster', 'cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Est_nodes', 'est_nodes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Out', 'out', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(8, model_feedback)
        results = {}
        outputs = {}

        # Points along geometry
        alg_params = {
            'DISTANCE': 1,
            'END_OFFSET': 0,
            'INPUT': parameters['streetlines'],
            'START_OFFSET': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsAlongGeometry'] = processing.run('native:pointsalonglines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Distance to nearest hub (line to hub)
        alg_params = {
            'FIELD': 'streetname',
            'HUBS': outputs['PointsAlongGeometry']['OUTPUT'],
            'INPUT': parameters['demandpoints'],
            'UNIT': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestHubLineToHub'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': 'hubdist< 60',
            'INPUT': outputs['DistanceToNearestHubLineToHub']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['demandpoints'],
            'JOIN': outputs['ExtractByExpression']['OUTPUT'],
            'JOIN_FIELDS': ['hubname'],
            'METHOD': 2,
            'PREDICATE': [0,3],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # NOTNULLHUBNAME
        alg_params = {
            'EXPRESSION': '\"HubName\"  IS NOT NULL',
            'INPUT': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Notnullhubname'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Add unique value index field
        alg_params = {
            'FIELD': 'streetname',
            'FIELD_NAME': 'indexed',
            'INPUT': outputs['Notnullhubname']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddUniqueValueIndexField'] = processing.run('native:adduniquevalueindexfield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Min Max K-Means Clustering Street Constraint Outliers
        alg_params = {
            'INPUT': outputs['AddUniqueValueIndexField']['OUTPUT'],
            'MAXPOINTS': 24,
            'MAX_ITER': 1,
            'MINPOINTS': 3,
            'OUTLIERS': parameters['Out'],
            'OUTPUT': parameters['Cluster'],
            'OUTPUT_CENTERS': parameters['Est_nodes']
        }
        outputs['MinMaxKmeansClusteringStreetConstraintOutliers'] = processing.run('script:min_max_kmeans3', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cluster'] = outputs['MinMaxKmeansClusteringStreetConstraintOutliers']['OUTPUT']
        results['Est_nodes'] = outputs['MinMaxKmeansClusteringStreetConstraintOutliers']['OUTPUT_CENTERS']
        results['Out'] = outputs['MinMaxKmeansClusteringStreetConstraintOutliers']['OUTLIERS']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Min Max K-Means Clustering Street Constraint
        alg_params = {
            'INPUT': outputs['AddUniqueValueIndexField']['OUTPUT'],
            'MAXPOINTS': 24,
            'MAX_ITER': 1,
            'MINPOINTS': 3,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_CENTERS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MinMaxKmeansClusteringStreetConstraint'] = processing.run('script:min_max_kmeans2', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'clustergrpouing_A'

    def displayName(self):
        return 'clustergrpouing_A'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Clustergrpouing_a()
