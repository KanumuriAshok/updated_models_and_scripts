"""
Model exported as python.
Name : secondary_snadd
Group : 
With QGIS : 31604
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_snadd(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('proposednode', 'proposed_node', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('onexisting', 'on_existing', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoint', 'demandpoint', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Sn_address', 'sn_address', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # sn_address
        alg_params = {
            'demandpoint': parameters['demandpoint'],
            'onexisting': parameters['onexisting'],
            'proposednode': parameters['proposednode'],
            'native:joinbynearest_1:sn_address': parameters['Sn_address']
        }
        outputs['Sn_address'] = processing.run('model:sn_address', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Sn_address'] = outputs['Sn_address']['native:joinbynearest_1:sn_address']
        return results

    def name(self):
        return 'secondary_snadd'

    def displayName(self):
        return 'secondary_snadd'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_snadd()
