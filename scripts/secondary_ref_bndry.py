"""
Model exported as python.
Name : secondary_ref_bndry
Group : 
With QGIS : 31801
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_ref_bndry(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('lndbnry', 'lndbnry', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographic_lines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaistdata', 'gaistdata', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterline', 'streetcenterline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('aerialdp', 'aerial_dp', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('undergrounddp', 'ugc', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Clusters', 'clusters', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ref_bndry', 'ref_bndry', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # ref_bndry
        alg_params = {
            'aerialdp': parameters['aerialdp'],
            'gaistdata': parameters['gaistdata'],
            'lndbnry': parameters['lndbnry'],
            'streetcenterline': parameters['streetcenterline'],
            'topographiclines': parameters['topographiclines'],
            'undergrounddp': parameters['undergrounddp'],
            'native:deleteholes_1:final_boundaries': parameters['Ref_bndry'],
            'native:fieldcalculator_3:new_clusters': parameters['Clusters']
        }
        outputs['Ref_bndry'] = processing.run('model:ref_bndry', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Clusters'] = outputs['Ref_bndry']['native:fieldcalculator_3:new_clusters']
        results['Ref_bndry'] = outputs['Ref_bndry']['native:deleteholes_1:final_boundaries']
        return results

    def name(self):
        return 'secondary_ref_bndry'

    def displayName(self):
        return 'secondary_ref_bndry'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_ref_bndry()
