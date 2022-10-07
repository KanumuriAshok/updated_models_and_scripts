"""
Model exported as python.
Name : secondary_preprocess_rgp
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_preprocess_rgp(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructures', 'piastructures', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pnboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('rawgooglepoles', 'rawgooglepoles', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Googlepoles', 'googlepoles', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Poles_at_5mtrs', 'poles_at_5mtrs', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # preprocess_rgp
        alg_params = {
            'gaist': parameters['gaist'],
            'piastructures': parameters['piastructures'],
            'pnboundary': parameters['pnboundary'],
            'rawgooglepoles': parameters['rawgooglepoles'],
            'native:extractbylocation_3:poles_at_5mtrs': parameters['Poles_at_5mtrs'],
            'native:snapgeometries_1:googlepoles': parameters['Googlepoles']
        }
        outputs['Preprocess_rgp'] = processing.run('model:preprocess_rgp', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Googlepoles'] = outputs['Preprocess_rgp']['native:snapgeometries_1:googlepoles']
        results['Poles_at_5mtrs'] = outputs['Preprocess_rgp']['native:extractbylocation_3:poles_at_5mtrs']
        return results

    def name(self):
        return 'secondary_preprocess_rgp'

    def displayName(self):
        return 'secondary_preprocess_rgp'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_preprocess_rgp()
