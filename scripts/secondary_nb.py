"""
Model exported as python.
Name : secondary_nb
Group : 
With QGIS : 32003
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_nb(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('cluster', 'cluster', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demand points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPoint,QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Noudeboundary', 'noudeboundary', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # NODEBOUNDARY
        alg_params = {
            'VERBOSE_LOG': False,
            'cluster': parameters['cluster'],
            'demand': parameters['demandpoints'],
            'plotboundary': parameters['landboundary'],
            'FinalBoundary': parameters['Noudeboundary']
        }
        outputs['Nodeboundary'] = processing.run('script:NODEBOUNDARY', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Noudeboundary'] = outputs['Nodeboundary']['FinalBoundary']
        return results

    def name(self):
        return 'secondary_nb'

    def displayName(self):
        return 'secondary_nb'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_nb()
