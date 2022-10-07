"""
Model exported as python.
Name : pn_nodeplacement
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Pn_nodeplacement(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pnboundary', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pnnode', 'pnnode', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructure', 'piastructure', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cabinet', 'cabinet', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Enclosure', 'enclosure', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(7, model_feedback)
        results = {}
        outputs = {}

        # Center Line
        alg_params = {
            'CityFibreLincolndata': parameters['gaist'],
            'native:simplifygeometries_1:Center Line': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CenterLine'] = processing.run('model:Center Line', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract by expression_ug
        alg_params = {
            'EXPRESSION': ' "fedtype"  = \'ug\'',
            'INPUT': parameters['pnboundary'],
            'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_ug'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by expression_jc
        alg_params = {
            'EXPRESSION': ' "category"  =  \'JOINTING CHAMBER\' ',
            'INPUT': parameters['piastructure'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_jc'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extract by location_ugnode
        alg_params = {
            'INPUT': parameters['pnnode'],
            'INTERSECT': outputs['ExtractByExpression_ug']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation_ugnode'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by location_aerialorhybrid
        alg_params = {
            'INPUT': parameters['pnnode'],
            'INTERSECT': outputs['ExtractByExpression_ug']['FAIL_OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation_aerialorhybrid'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,  # Prefer aligning nodes, insert extra vertices where required
            'INPUT': outputs['ExtractByLocation_ugnode']['OUTPUT'],
            'REFERENCE_LAYER': outputs['ExtractByExpression_jc']['OUTPUT'],
            'TOLERANCE': 30,
            'OUTPUT': parameters['Enclosure']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Enclosure'] = outputs['SnapGeometriesToLayer']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,  # Prefer aligning nodes, insert extra vertices where required
            'INPUT': outputs['ExtractByLocation_aerialorhybrid']['OUTPUT'],
            'REFERENCE_LAYER': outputs['CenterLine']['native:simplifygeometries_1:Center Line'],
            'TOLERANCE': 10,
            'OUTPUT': parameters['Cabinet']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cabinet'] = outputs['SnapGeometriesToLayer']['OUTPUT']
        return results

    def name(self):
        return 'pn_nodeplacement'

    def displayName(self):
        return 'pn_nodeplacement'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Pn_nodeplacement()
