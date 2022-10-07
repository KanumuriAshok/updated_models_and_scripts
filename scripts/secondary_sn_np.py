"""
Model exported as python.
Name : secondary_sn_np
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_sn_np(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('piastructure', 'piastructure', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('googlepoles', 'googlepoles', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('clusterboundary', 'clusterboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Existingpoles_asn', 'existingpoles_asn', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ugnode_sn', 'ugnode_sn', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # hybrid_nodeplacement_2
        alg_params = {
            'clusterboundary': parameters['clusterboundary'],
            'googlepoles': parameters['googlepoles'],
            'piastructure': parameters['piastructure'],
            'native:snapgeometries_1:ugnode_sn': parameters['Ugnode_sn'],
            'native:snapgeometries_2:existingpoles_asn': parameters['Existingpoles_asn']
        }
        outputs['Hybrid_nodeplacement_2'] = processing.run('model:hybrid_nodeplacement_2', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Existingpoles_asn'] = outputs['Hybrid_nodeplacement_2']['native:snapgeometries_2:existingpoles_asn']
        results['Ugnode_sn'] = outputs['Hybrid_nodeplacement_2']['native:snapgeometries_1:ugnode_sn']
        return results

    def name(self):
        return 'secondary_sn_np'

    def displayName(self):
        return 'secondary_sn_np'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_sn_np()
