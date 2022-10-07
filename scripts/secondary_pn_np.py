"""
Model exported as python.
Name : secondary_pn_np
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_pn_np(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pnboundary', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pnnode', 'pnnode', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructure', 'piastructure', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cabinet', 'cabinet', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Enclosure', 'enclosure', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # pn_nodeplacement
        alg_params = {
            'gaist': parameters['gaist'],
            'piastructure': parameters['piastructure'],
            'pnboundary': parameters['pnboundary'],
            'pnnode': parameters['pnnode'],
            'native:snapgeometries_1:cabinet': parameters['Cabinet'],
            'native:snapgeometries_2:enclosure': parameters['Enclosure']
        }
        outputs['Pn_nodeplacement'] = processing.run('model:pn_nodeplacement', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cabinet'] = outputs['Pn_nodeplacement']['native:snapgeometries_1:cabinet']
        results['Enclosure'] = outputs['Pn_nodeplacement']['native:snapgeometries_2:enclosure']
        return results

    def name(self):
        return 'secondary_pn_np'

    def displayName(self):
        return 'secondary_pn_np'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_pn_np()
