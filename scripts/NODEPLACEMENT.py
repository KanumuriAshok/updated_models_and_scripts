"""
Model exported as python.
Name : nodeplacement
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


class Nodeplacement(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('existing', 'existing', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'land_boundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('nodes', 'nodes', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('First', 'FIRST', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Placed_2', 'placed_2', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
        results = {}
        outputs = {}

        # not carriage
        alg_params = {
            'EXPRESSION': ' \"highway_ty\" != \'Carriageway\' ',
            'INPUT': parameters['gaist'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NotCarriage'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # footway
        alg_params = {
            'EXPRESSION': ' \"highway_ty\"  =  \'Footway\' ',
            'INPUT': outputs['NotCarriage']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Footway'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # plotintersection
        alg_params = {
            'INPUT': parameters['landboundary'],
            'VERTICES': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Plotintersection'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': ' \"obj_class\"  =  \'POLE\'  OR  \"obj_class\"  =  \'JB\' ',
            'INPUT': parameters['existing'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.5,
            'END_CAP_STYLE': 0,
            'INPUT': outputs['Plotintersection']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # first snap
        alg_params = {
            'BEHAVIOR': 2,
            'INPUT': parameters['nodes'],
            'REFERENCE_LAYER': outputs['ExtractByExpression']['OUTPUT'],
            'TOLERANCE': 10,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FirstSnap'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Intersection
        alg_params = {
            'INPUT': parameters['nodes'],
            'INPUT_FIELDS': ['cluster_id'],
            'OVERLAY': outputs['FirstSnap']['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Intersect
        alg_params = {
            'A': outputs['Footway']['OUTPUT'],
            'B': outputs['Buffer']['OUTPUT'],
            'SPLIT': True,
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersect'] = processing.run('saga:intersect', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'cluster_id',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'cluster_id',
            'INPUT': outputs['FirstSnap']['OUTPUT'],
            'INPUT_2': outputs['Intersection']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValue'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 2,
            'INPUT': outputs['Intersection']['OUTPUT'],
            'REFERENCE_LAYER': outputs['Intersect']['RESULT'],
            'TOLERANCE': 15,
            'OUTPUT': parameters['Placed_2']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Placed_2'] = outputs['SnapGeometriesToLayer']['OUTPUT']

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': ' \"cluster_id_2\" IS NULL ',
            'INPUT': outputs['JoinAttributesByFieldValue']['OUTPUT'],
            'OUTPUT': parameters['First']
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['First'] = outputs['ExtractByExpression']['OUTPUT']
        return results

    def name(self):
        return 'nodeplacement'

    def displayName(self):
        return 'nodeplacement'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Nodeplacement()
