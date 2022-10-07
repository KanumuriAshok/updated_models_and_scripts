"""
Model exported as python.
Name : secondary_ar
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_ar(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('street', 'street', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('Cluster', 'cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Est_nodes', 'est_nodes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Outlier', 'outlier', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # clustergrpouing_A
        alg_params = {
            'VERBOSE_LOG': False,
            'demandpoints': parameters['demand'],
            'streetlines': parameters['street'],
            'Cluster': parameters['Cluster'],
            'Est_nodes': parameters['Est_nodes'],
            'Out': parameters['Outlier']
        }
        outputs['Clustergrpouing_a'] = processing.run('script:clustergrpouing_A', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cluster'] = outputs['Clustergrpouing_a']['Cluster']
        results['Est_nodes'] = outputs['Clustergrpouing_a']['Est_nodes']
        results['Outlier'] = outputs['Clustergrpouing_a']['Out']
        return results

    def name(self):
        return 'secondary_ar'

    def displayName(self):
        return 'secondary_ar'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_ar()
