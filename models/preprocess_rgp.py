"""
Model exported as python.
Name : preprocess_rgp
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Preprocess_rgp(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructures', 'piastructures', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pnboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('rawgooglepoles', 'rawgooglepoles', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Poles_at_5mtrs', 'poles_at_5mtrs', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Googlepoles', 'googlepoles', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
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

        # Extract by expression
        alg_params = {
            'EXPRESSION': ' "obj_class"  =  \'POLE\'',
            'INPUT': parameters['piastructures'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by location_rgpoles
        alg_params = {
            'INPUT': parameters['rawgooglepoles'],
            'INTERSECT': parameters['pnboundary'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation_rgpoles'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Buffer_piapoles
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 5,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer_piapoles'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Buffer_rgpoles
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 6,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['ExtractByLocation_rgpoles']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer_rgpoles'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Centroids_rgpoles
        alg_params = {
            'ALL_PARTS': True,
            'INPUT': outputs['Buffer_rgpoles']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids_rgpoles'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract by location_2
        alg_params = {
            'INPUT': outputs['Centroids_rgpoles']['OUTPUT'],
            'INTERSECT': outputs['Buffer_piapoles']['OUTPUT'],
            'PREDICATE': [2],  # disjoint
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation_2'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,  # Prefer aligning nodes, insert extra vertices where required
            'INPUT': outputs['ExtractByLocation_2']['OUTPUT'],
            'REFERENCE_LAYER': outputs['CenterLine']['native:simplifygeometries_1:Center Line'],
            'TOLERANCE': 10,
            'OUTPUT': parameters['Googlepoles']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Googlepoles'] = outputs['SnapGeometriesToLayer']['OUTPUT']

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Buffer_5mtrs
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 5,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['SnapGeometriesToLayer']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer_5mtrs'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Polygons to lines
        alg_params = {
            'INPUT': outputs['Buffer_5mtrs']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonsToLines'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': parameters['rawgooglepoles'],
            'INTERSECT': outputs['PolygonsToLines']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': parameters['Poles_at_5mtrs']
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Poles_at_5mtrs'] = outputs['ExtractByLocation']['OUTPUT']
        return results

    def name(self):
        return 'preprocess_rgp'

    def displayName(self):
        return 'preprocess_rgp'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Preprocess_rgp()
