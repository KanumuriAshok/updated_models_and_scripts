"""
Model exported as python.
Name : secondary_ug
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


class Secondary_ug(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('street', 'street', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('Est_nodes', 'est_nodes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ug_cluster', 'ug_cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ug_outliers', 'ug_outliers', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # clustergrpouing_u
        alg_params = {
            'VERBOSE_LOG': False,
            'demandpoints': parameters['demand'],
            'streetlines': parameters['street'],
            'Ug_cluster': parameters['Ug_cluster'],
            'Ug_est_nodes': parameters['Est_nodes'],
            'Ug_outl': parameters['Ug_outliers']
        }
        outputs['Clustergrpouing_u'] = processing.run('script:clustergrpouing_u', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Est_nodes'] = outputs['Clustergrpouing_u']['Ug_est_nodes']
        results['Ug_cluster'] = outputs['Clustergrpouing_u']['Ug_cluster']
        results['Ug_outliers'] = outputs['Clustergrpouing_u']['Ug_outl']
        return results

    def name(self):
        return 'secondary_ug'

    def displayName(self):
        return 'secondary_ug'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_ug()
