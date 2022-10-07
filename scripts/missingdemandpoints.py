"""
Model exported as python.
Name : missingdemandpoints
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class Missingdemandpoints(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('cartograpgictext', 'cartographictext', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demandpoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterline', 'streetcenterline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographicline', 'topographicline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Preprocessed_dp', 'preprocessed_dp', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(13, model_feedback)
        results = {}
        outputs = {}

        # Points along geometry
        alg_params = {
            'DISTANCE': 0.5,
            'END_OFFSET': 0,
            'INPUT': parameters['streetcenterline'],
            'START_OFFSET': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsAlongGeometry'] = processing.run('native:pointsalonglines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Distance to nearest hub (line to hub)
        alg_params = {
            'FIELD': 'include',
            'HUBS': outputs['PointsAlongGeometry']['OUTPUT'],
            'INPUT': parameters['demandpoints'],
            'UNIT': 0,  # Meters
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestHubLineToHub'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_lns
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [parameters['streetcenterline'],parameters['topographicline'],outputs['DistanceToNearestHubLineToHub']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_lns'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Polygons to lines
        alg_params = {
            'INPUT': parameters['gaist'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonsToLines'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_s
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [parameters['streetcenterline'],outputs['DistanceToNearestHubLineToHub']['OUTPUT'],outputs['PolygonsToLines']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_s'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Polygonize_lns
        alg_params = {
            'INPUT': outputs['MergeVectorLayers_lns']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize_lns'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Polygonize_s
        alg_params = {
            'INPUT': outputs['MergeVectorLayers_s']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize_s'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Difference_mlns
        alg_params = {
            'INPUT': outputs['Polygonize_lns']['OUTPUT'],
            'OVERLAY': parameters['landboundary'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference_mlns'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['Difference_mlns']['OUTPUT'],
            'INTERSECT': outputs['Polygonize_s']['OUTPUT'],
            'PREDICATE': [2],  # disjoint
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_fnlland
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [parameters['landboundary'],outputs['ExtractByLocation']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_fnlland'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by location_withdp
        alg_params = {
            'INPUT': outputs['MergeVectorLayers_fnlland']['OUTPUT'],
            'INTERSECT': parameters['demandpoints'],
            'PREDICATE': [2],  # disjoint
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation_withdp'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Extract by location_missingdp
        alg_params = {
            'INPUT': parameters['cartograpgictext'],
            'INTERSECT': outputs['ExtractByLocation_withdp']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation_missingdp'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [parameters['demandpoints'],outputs['ExtractByLocation_missingdp']['OUTPUT']],
            'OUTPUT': parameters['Preprocessed_dp']
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Preprocessed_dp'] = outputs['MergeVectorLayers']['OUTPUT']
        return results

    def name(self):
        return 'missingdemandpoints'

    def displayName(self):
        return 'missingdemandpoints'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Missingdemandpoints()
