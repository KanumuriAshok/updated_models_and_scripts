"""
Model exported as python.
Name : sndry_snboundry
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


class Sndry_snboundry(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('aerialdp', 'aerial_dp', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaistdata', 'gaistdata', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetlines', 'streetlines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographiclines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('ugdp', 'ug_dp', defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterVectorLayer('lndbnry', 'lndbnry', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('New_clusters', 'new_clusters', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Nodeboundary', 'nodeboundary', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # snboundary
        alg_params = {
            'aerialdp': parameters['aerialdp'],
            'gaistdata': parameters['gaistdata'],
            'lndbnry': parameters['lndbnry'],
            'streetcenterline': parameters['streetlines'],
            'topographiclines': parameters['topographiclines'],
            'undergrounddp': parameters['ugdp'],
            'model:dp_clusters_1:new_clusters': parameters['New_clusters'],
            'native:deleteholes_1:final_boundaries': parameters['Nodeboundary']
        }
        outputs['Snboundary'] = processing.run('model:snboundary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['New_clusters'] = outputs['Snboundary']['model:dp_clusters_1:new_clusters']
        results['Nodeboundary'] = outputs['Snboundary']['native:deleteholes_1:final_boundaries']
        return results

    def name(self):
        return 'sndry_snboundry'

    def displayName(self):
        return 'sndry_snboundry'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Sndry_snboundry()
