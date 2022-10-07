"""
Model exported as python.
Name : secondary_missingdp
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_missingdp(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demandpoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('cartograpgictext', 'cartographictext', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterline', 'streetcenterline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographicline', 'topographicline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Preprocessed_dp', 'preprocessed_dp', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # updated_missingdp
        alg_params = {
            'cartograpgictext': parameters['cartograpgictext'],
            'demandpoints': parameters['demandpoints'],
            'gaist': parameters['gaist'],
            'landboundary': parameters['landboundary'],
            'streetcenterline': parameters['streetcenterline'],
            'topographicline': parameters['topographicline'],
            'native:mergevectorlayers_3:preprocessed_dp': parameters['Preprocessed_dp']
        }
        outputs['Updated_missingdp'] = processing.run('model:updated_missingdp', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Preprocessed_dp'] = outputs['Updated_missingdp']['native:mergevectorlayers_3:preprocessed_dp']
        return results

    def name(self):
        return 'secondary_missingdp'

    def displayName(self):
        return 'secondary_missingdp'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_missingdp()
