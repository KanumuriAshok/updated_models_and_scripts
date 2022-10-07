"""
Model exported as python.
Name : secondary_snb
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_snb(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('adp', 'a_dp', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetline', 'streetline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographic', 'topographic', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('ugcluster', 'ug_cluster', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Final_boudary', 'final_boudary', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # snboundary
        alg_params = {
            'aerialdp': parameters['adp'],
            'gaistdata': parameters['gaist'],
            'lndbnry': parameters['landboundary'],
            'streetcenterline': parameters['streetline'],
            'topographiclines': parameters['topographic'],
            'undergrounddp': parameters['ugcluster'],
            'model:dp_clusters_1:new_clusters': QgsProcessing.TEMPORARY_OUTPUT,
            'native:deleteholes_1:final_boundaries': parameters['Final_boudary']
        }
        outputs['Snboundary'] = processing.run('model:snboundary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Final_boudary'] = outputs['Snboundary']['native:deleteholes_1:final_boundaries']
        return results

    def name(self):
        return 'secondary_snb'

    def displayName(self):
        return 'secondary_snb'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_snb()
