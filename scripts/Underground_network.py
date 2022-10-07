"""
Model exported as python.
Name : underground
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


class Underground(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'DEMAND_POINTS', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetlines', 'street lines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Classified', 'classified', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Shortest_path', 'shortest_path', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Estimated_nodes', 'Estimated_nodes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('New_cluster', 'New_Cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
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
            'FIELD': 'STREETNAME',
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
            'OUTPUT': parameters['Shortest_path']
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Shortest_path'] = outputs['ExtractByExpression']['OUTPUT']

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

        # Add unique value index field
        alg_params = {
            'FIELD': 'hubname',
            'FIELD_NAME': 'indexed',
            'INPUT': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OUTPUT': parameters['Classified']
        }
        outputs['AddUniqueValueIndexField'] = processing.run('native:adduniquevalueindexfield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Classified'] = outputs['AddUniqueValueIndexField']['OUTPUT']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Min Max K-Means Clustering Street Constraint
        alg_params = {
            'INPUT': outputs['AddUniqueValueIndexField']['OUTPUT'],
            'MAXPOINTS': 48,
            'MAX_ITER': 1,
            'MINPOINTS': 16,
            'OUTPUT': parameters['New_cluster'],
            'OUTPUT_CENTERS': parameters['Estimated_nodes']
        }
        outputs['MinMaxKmeansClusteringStreetConstraint'] = processing.run('script:min_max_kmeans2', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Estimated_nodes'] = outputs['MinMaxKmeansClusteringStreetConstraint']['OUTPUT_CENTERS']
        results['New_cluster'] = outputs['MinMaxKmeansClusteringStreetConstraint']['OUTPUT']
        return results

    def name(self):
        return 'underground'

    def displayName(self):
        return 'underground'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Underground()
