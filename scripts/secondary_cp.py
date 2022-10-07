"""
Model exported as python.
Name : secondary_cp
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_cp(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('nodepoints', 'nodepoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cabinets', 'cabinets', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # cabinetplacement
        alg_params = {
            'gaist': parameters['gaist'],
            'nodepoints': parameters['nodepoints'],
            'native:snapgeometries_1:cabinets': parameters['Cabinets']
        }
        outputs['Cabinetplacement'] = processing.run('model:cabinetplacement', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cabinets'] = outputs['Cabinetplacement']['native:snapgeometries_1:cabinets']
        return results

    def name(self):
        return 'secondary_cp'

    def displayName(self):
        return 'secondary_cp'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_cp()
