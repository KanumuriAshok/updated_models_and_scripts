"""
Model exported as python.
Name : secondary_pre_gp
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class Secondary_pre_gp(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaistdata', 'gaist_data', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructure', 'pia_structure', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pn_boundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('rawgooglepoles', 'raw_google_poles', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Flagged_poles', 'flagged_poles', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Updated_gp', 'updated_gp', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # preprocess_gp
        alg_params = {
            'gaist': parameters['gaistdata'],
            'googlePoles': parameters['rawgooglepoles'],
            'piastructurepoles': parameters['piastructure'],
            'pnboundary': parameters['pnboundary'],
            'native:extractbylocation_2:flagged': parameters['Flagged_poles'],
            'qgis:deletecolumn_2:updated_gp': parameters['Updated_gp']
        }
        outputs['Preprocess_gp'] = processing.run('model:preprocess_gp', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Flagged_poles'] = outputs['Preprocess_gp']['native:extractbylocation_2:flagged']
        results['Updated_gp'] = outputs['Preprocess_gp']['qgis:deletecolumn_2:updated_gp']
        return results

    def name(self):
        return 'secondary_pre_gp'

    def displayName(self):
        return 'secondary_pre_gp'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_pre_gp()
