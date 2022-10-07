"""
Model exported as python.
Name : nodeplacement_ar
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


class Nodeplacement_ar(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('cluster', 'cluster', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('existing', 'existing', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'land_boundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('nodes', 'nodes', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('On_existing', 'on_existing', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Proposed', 'proposed', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(12, model_feedback)
        results = {}
        outputs = {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '\"obj_class\"  =  \'POLE\' ',
            'INPUT': parameters['existing'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # not carriage
        alg_params = {
            'EXPRESSION': ' \"highway_ty\" != \'Carriageway\' ',
            'INPUT': parameters['gaist'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NotCarriage'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # footway
        alg_params = {
            'EXPRESSION': ' \"highway_ty\"  =  \'Footway\' ',
            'INPUT': outputs['NotCarriage']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Footway'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # updated_node
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'cluster_id',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'cluster_id',
            'INPUT': parameters['nodes'],
            'INPUT_2': parameters['cluster'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Updated_node'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # plotintersection
        alg_params = {
            'INPUT': parameters['landboundary'],
            'VERTICES': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Plotintersection'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # first snap
        alg_params = {
            'BEHAVIOR': 2,
            'INPUT': outputs['Updated_node']['OUTPUT'],
            'REFERENCE_LAYER': outputs['ExtractByExpression']['OUTPUT'],
            'TOLERANCE': 40,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FirstSnap'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Intersection
        alg_params = {
            'INPUT': outputs['Updated_node']['OUTPUT'],
            'INPUT_FIELDS': ['cluster_id_2'],
            'OVERLAY': outputs['FirstSnap']['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
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

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'cluster_id_2',
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

        # Extract by expression
        alg_params = {
            'EXPRESSION': ' \"cluster_id_2_2_2\" IS NULL ',
            'INPUT': outputs['JoinAttributesByFieldValue']['OUTPUT'],
            'OUTPUT': parameters['On_existing']
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['On_existing'] = outputs['ExtractByExpression']['OUTPUT']

        feedback.setCurrentStep(10)
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

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 2,
            'INPUT': outputs['Intersection']['OUTPUT'],
            'REFERENCE_LAYER': outputs['Intersect']['RESULT'],
            'TOLERANCE': 15,
            'OUTPUT': parameters['Proposed']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Proposed'] = outputs['SnapGeometriesToLayer']['OUTPUT']
        return results

    def name(self):
        return 'nodeplacement_ar'

    def displayName(self):
        return 'nodeplacement_ar'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Nodeplacement_ar()
