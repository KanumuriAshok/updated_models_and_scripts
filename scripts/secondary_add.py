"""
Model exported as python.
Name : secondary_add
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_add(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demandpoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints (3)', 'onExisting', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints (2)', 'poproposed', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Labelsn', 'labelsn', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # AddressCreation_1
        alg_params = {
            'DemandPoints': parameters['demandpoints'],
            'PIAStructures': parameters['demandpoints (3)'],
            'proposed': parameters['demandpoints (2)'],
            'native:joinbynearest_1:Address': parameters['Labelsn']
        }
        outputs['Addresscreation_1'] = processing.run('model:AddressCreation_1', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Labelsn'] = outputs['Addresscreation_1']['native:joinbynearest_1:Address']
        return results

    def name(self):
        return 'secondary_add'

    def displayName(self):
        return 'secondary_add'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_add()
