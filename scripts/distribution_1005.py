"""
Model exported as python.
Name : distribution_1005
Group : 
With QGIS : 31604
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class Distribution_1005(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('existingducts', 'existing_ducts', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('existingstructures', 'existing_structures', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('primarynodes', 'primary nodes', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('proposednodes', 'proposed_nodes', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('usable_existing_ducts', 'usable_existing_ducts', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('proposed_ducts', 'proposed_ducts', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Convert multipoints to points
        alg_params = {
            'MULTIPOINTS': parameters['proposednodes'],
            'POINTS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvertMultipointsToPoints'] = processing.run('saga:convertmultipointstopoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract by expression:not null rag status
        alg_params = {
            'EXPRESSION': ' \"rag_status\"  is not null',
            'INPUT': parameters['existingducts'],
            'OUTPUT': parameters['usable_existing_ducts']
        }
        outputs['ExtractByExpressionnotNullRagStatus'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['usable_existing_ducts'] = outputs['ExtractByExpressionnotNullRagStatus']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Union
        alg_params = {
            'INPUT': outputs['ConvertMultipointsToPoints']['POINTS'],
            'OVERLAY': parameters['existingstructures'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Union'] = processing.run('native:union', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        return results

    def name(self):
        return 'distribution_1005'

    def displayName(self):
        return 'distribution_1005'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Distribution_1005()
