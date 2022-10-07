"""
Model exported as python.
Name : arcombi
Group : 
With QGIS : 31604
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Arcombi(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('street', 'street', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('Cluster', 'cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Nodes', 'nodes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

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
            
            'script:min_max_kmeans2:cluster': parameters['Cluster'],
            'script:min_max_kmeans2:nodes': parameters['Nodes']
        }
        outputs['Aerial_updated'] = processing.run('model:aerial_UPDATED', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cluster'] = outputs['Aerial_updated']['script:min_max_kmeans2:cluster']
        results['Nodes'] = outputs['Aerial_updated']['script:min_max_kmeans2:nodes']
        return results

    def name(self):
        return 'arcombi'

    def displayName(self):
        return 'arcombi'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Arcombi()
