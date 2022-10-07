"""
Model exported as python.
Name : Secondary_Address
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_address(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Proposed', 'Proposed', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Onexisting', 'On-existing', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Demandpoints', 'Demandpoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Address', 'Address', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # addressCreationNew
        alg_params = {
            'DemandPoints': parameters['Demandpoints'],
            'Onexisting': parameters['Onexisting'],
            'Proposed': parameters['Proposed'],
            'native:joinbynearest_1:Address': parameters['Address']
        }
        outputs['Addresscreationnew'] = processing.run('model:addressCreationNew', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Address'] = outputs['Addresscreationnew']['native:joinbynearest_1:Address']
        return results

    def name(self):
        return 'Secondary_Address'

    def displayName(self):
        return 'Secondary_Address'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_address()
