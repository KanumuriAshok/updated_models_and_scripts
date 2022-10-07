"""
Model exported as python.
Name : cabinetplacement
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Cabinetplacement(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('nodepoints', 'nodepoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cabinets', 'cabinets', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Center Line
        alg_params = {
            'CityFibreLincolndata': parameters['gaist'],
            'native:simplifygeometries_1:Center Line': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CenterLine'] = processing.run('model:Center Line', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,  # Prefer aligning nodes, insert extra vertices where required
            'INPUT': parameters['nodepoints'],
            'REFERENCE_LAYER': outputs['CenterLine']['native:simplifygeometries_1:Center Line'],
            'TOLERANCE': 10,
            'OUTPUT': parameters['Cabinets']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cabinets'] = outputs['SnapGeometriesToLayer']['OUTPUT']
        return results

    def name(self):
        return 'cabinetplacement'

    def displayName(self):
        return 'cabinetplacement'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Cabinetplacement()
