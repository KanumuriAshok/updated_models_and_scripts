"""
Model exported as python.
Name : secondary_fianl_nb
Group : 
With QGIS : 31801
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class Secondary_fianl_nb(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaistdata', 'gaistdata', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterline', 'streetcenterline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographic_lines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('updatedcluster', 'updated_cluster', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Final_boundary', 'final_boundary', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # final_nb
        alg_params = {
            'gaistdata': parameters['gaistdata'],
            'landboundary': parameters['landboundary'],
            'streetcenterline': parameters['streetcenterline'],
            'topographiclines': parameters['topographiclines'],
            'updatedcluster': parameters['updatedcluster'],
            'native:deleteholes_1:final_boundaries': parameters['Final_boundary']
        }
        outputs['Final_nb'] = processing.run('model:final_nb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Final_boundary'] = outputs['Final_nb']['native:deleteholes_1:final_boundaries']
        return results

    def name(self):
        return 'secondary_fianl_nb'

    def displayName(self):
        return 'secondary_fianl_nb'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_fianl_nb()
