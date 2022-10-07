"""
Model exported as python.
Name : secondary_clusterbndry
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_clusterbndry(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demandpoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('referenceline', 'referenceline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterlines', 'streetcenterlines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographiclines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cluster_bndry', 'cluster_bndry', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Mdu', 'mdu', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # clusterbndry_hybrid_v1
        alg_params = {
            'demandpoints': parameters['demandpoints'],
            'landboundary': parameters['landboundary'],
            'referenceline': parameters['referenceline'],
            'streetcenterlines': parameters['streetcenterlines'],
            'topographiclines': parameters['topographiclines'],
            'native:extractbylocation_2:mdu': parameters['Mdu'],
            'native:fixgeometries_1:cluster_bndry': parameters['Cluster_bndry']
        }
        outputs['Clusterbndry_hybrid_v1'] = processing.run('model:clusterbndry_hybrid_v1', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cluster_bndry'] = outputs['Clusterbndry_hybrid_v1']['native:fixgeometries_1:cluster_bndry']
        results['Mdu'] = outputs['Clusterbndry_hybrid_v1']['native:extractbylocation_2:mdu']
        return results

    def name(self):
        return 'secondary_clusterbndry'

    def displayName(self):
        return 'secondary_clusterbndry'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_clusterbndry()
