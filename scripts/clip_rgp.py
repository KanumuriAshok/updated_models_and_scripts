"""
Model exported as python.
Name : clip_rgp
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Clip_rgp(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pnboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('rawgooglepoles', 'rawgooglepoles', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Rawgooglepoles', 'rawgooglepoles', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Clip
        alg_params = {
            'INPUT': parameters['rawgooglepoles'],
            'OVERLAY': parameters['pnboundary'],
            'OUTPUT': parameters['Rawgooglepoles']
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Rawgooglepoles'] = outputs['Clip']['OUTPUT']
        return results

    def name(self):
        return 'clip_rgp'

    def displayName(self):
        return 'clip_rgp'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Clip_rgp()
