"""
Model exported as python.
Name : secondary_drop_ug
Group : 
With QGIS : 31604
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_drop_ug(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Lead_in', 'lead_in', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # dropntwrk_ug
        alg_params = {
            'demand': parameters['demand'],
            'gaist': parameters['gaist'],
            'qgis:distancetonearesthublinetohub_1:leadin': parameters['Lead_in']
        }
        outputs['Dropntwrk_ug'] = processing.run('model:dropntwrk_ug', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Lead_in'] = outputs['Dropntwrk_ug']['qgis:distancetonearesthublinetohub_1:leadin']
        return results

    def name(self):
        return 'secondary_drop_ug'

    def displayName(self):
        return 'secondary_drop_ug'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_drop_ug()
