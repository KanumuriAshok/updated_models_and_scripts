"""
Model exported as python.
Name : arcombi
Group : 
With QGIS : 32003
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Arcombi(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('street', 'street', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cluster', 'cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # aerial_UPDATED
        alg_params = {
            'demandpoints': parameters['demand'],
            'streetlines': parameters['street'],
            'native:extractbyexpression_1:shortest_path': QgsProcessing.TEMPORARY_OUTPUT,
            'script:min_max_kmeans2_1:Cluster': QgsProcessing.TEMPORARY_OUTPUT,
            'script:min_max_kmeans2_1:Estimated_nodes': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Aerial_updated'] = processing.run('model:aerial_UPDATED', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cluster'] = outputs['Aerial_updated']['script:min_max_kmeans2_1:cluster']
        results['model:aerial_UPDATED_1:nodes'] = outputs['Aerial_updated']['script:min_max_kmeans2_1:nodes']
        return results

    def name(self):
        return 'arcombination'

    def displayName(self):
        return 'arcombination'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Arcombi()
