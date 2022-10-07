"""
Model exported as python.
Name : secondary_np
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_np(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('existing', 'existing', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('node', 'node', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterVectorLayer('cluster', 'cluster', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Existing', 'existing', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Proposed', 'proposed', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # nodeplacement_ar
        alg_params = {
            'cluster': parameters['cluster'],
            'existing': parameters['existing'],
            'gaist': parameters['gaist'],
            'landboundary': parameters['landboundary'],
            'nodes': parameters['node'],
            'native:extractbyexpression_4:on_existing': parameters['Existing'],
            'native:snapgeometries_2:proposed': parameters['Proposed']
        }
        outputs['Nodeplacement_ar'] = processing.run('model:nodeplacement_ar', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Existing'] = outputs['Nodeplacement_ar']['native:extractbyexpression_4:on_existing']
        results['Proposed'] = outputs['Nodeplacement_ar']['native:snapgeometries_2:proposed']
        return results

    def name(self):
        return 'secondary_np'

    def displayName(self):
        return 'secondary_np'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_np()
