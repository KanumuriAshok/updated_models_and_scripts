"""
Model exported as python.
Name : snboundary
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class Snboundary(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('aerialdp', 'aerial_dp', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaistdata', 'gaistdata', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterline', 'streetcenterline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographic_lines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('undergrounddp', 'underground_dp', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterVectorLayer('lndbnry', 'lndbnry', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('New_clusters', 'new_clusters', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Final_boundaries', 'final_boundaries', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(27, model_feedback)
        results = {}
        outputs = {}

        # Polygons to lines
        alg_params = {
            'INPUT': parameters['gaistdata'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonsToLines'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # dp_clusters
        alg_params = {
            'AerialDP': parameters['aerialdp'],
            'undergrounddp': parameters['undergrounddp'],
            'native:deleteduplicategeometries_1:new_clusters': parameters['New_clusters']
        }
        outputs['Dp_clusters'] = processing.run('model:dp_clusters', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['New_clusters'] = outputs['Dp_clusters']['native:deleteduplicategeometries_1:new_clusters']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Points along geometry
        alg_params = {
            'DISTANCE': 1,
            'END_OFFSET': 0,
            'INPUT': parameters['streetcenterline'],
            'START_OFFSET': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsAlongGeometry'] = processing.run('native:pointsalonglines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Center Line
        alg_params = {
            'CityFibreLincolndata': parameters['gaistdata'],
            'native:simplifygeometries_1:Center Line': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CenterLine'] = processing.run('model:Center Line', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Polygonize_topoarea
        alg_params = {
            'INPUT': parameters['topographiclines'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize_topoarea'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Centroids
        alg_params = {
            'ALL_PARTS': True,
            'INPUT': parameters['lndbnry'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Distance to nearest hub (line to hub)
        alg_params = {
            'FIELD': 'include',
            'HUBS': outputs['PointsAlongGeometry']['OUTPUT'],
            'INPUT': outputs['Dp_clusters']['native:deleteduplicategeometries_1:new_clusters'],
            'UNIT': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestHubLineToHub'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Merge vector layers(forrdselection)
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [parameters['streetcenterline'],outputs['CenterLine']['native:simplifygeometries_1:Center Line']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersforrdselection'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Extract by location(Streetpolyogns)
        alg_params = {
            'INPUT': outputs['Polygonize_topoarea']['OUTPUT'],
            'INTERSECT': outputs['MergeVectorLayersforrdselection']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationstreetpolyogns'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Difference_onlyland
        alg_params = {
            'INPUT': outputs['Polygonize_topoarea']['OUTPUT'],
            'OVERLAY': outputs['ExtractByLocationstreetpolyogns']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference_onlyland'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_lines
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['PolygonsToLines']['OUTPUT'],outputs['DistanceToNearestHubLineToHub']['OUTPUT'],parameters['streetcenterline']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_lines'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Polygonize
        alg_params = {
            'INPUT': outputs['MergeVectorLayers_lines']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Difference_missingland
        alg_params = {
            'INPUT': outputs['Difference_onlyland']['OUTPUT'],
            'OVERLAY': parameters['lndbnry'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference_missingland'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Extract by location (for landbndryfeatures)
        alg_params = {
            'INPUT': outputs['Polygonize']['OUTPUT'],
            'INTERSECT': outputs['Centroids']['OUTPUT'],
            'PREDICATE': [0,6],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationForLandbndryfeatures'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Difference (roadscreated)
        alg_params = {
            'INPUT': outputs['Polygonize']['OUTPUT'],
            'OVERLAY': outputs['ExtractByLocationForLandbndryfeatures']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DifferenceRoadscreated'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest_road
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELDS_TO_COPY': ['index'],
            'INPUT': outputs['DifferenceRoadscreated']['OUTPUT'],
            'INPUT_2': outputs['Dp_clusters']['native:deleteduplicategeometries_1:new_clusters'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearest_road'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Dissolve_landbndry
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['Difference_missingland']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolve_landbndry'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts
        alg_params = {
            'INPUT': outputs['Dissolve_landbndry']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSingleparts'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_land
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['MultipartToSingleparts']['OUTPUT'],parameters['lndbnry']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_land'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Centroids_landbndry
        alg_params = {
            'ALL_PARTS': True,
            'INPUT': outputs['MergeVectorLayers_land']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids_landbndry'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['index'],
            'INPUT': outputs['Centroids_landbndry']['OUTPUT'],
            'INPUT_2': outputs['Dp_clusters']['native:deleteduplicategeometries_1:new_clusters'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearest'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest_land
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['index'],
            'INPUT': outputs['MergeVectorLayers_land']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByNearest']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearest_land'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['JoinAttributesByNearest_road']['OUTPUT'],outputs['JoinAttributesByNearest_land']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'REFERENCE_LAYER': outputs['MergeVectorLayers']['OUTPUT'],
            'TOLERANCE': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': outputs['SnapGeometriesToLayer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Dissolve
        alg_params = {
            'FIELD': ['index'],
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Delete holes
        alg_params = {
            'INPUT': outputs['Dissolve']['OUTPUT'],
            'MIN_AREA': 20,
            'OUTPUT': parameters['Final_boundaries']
        }
        outputs['DeleteHoles'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Final_boundaries'] = outputs['DeleteHoles']['OUTPUT']
        return results

    def name(self):
        return 'snboundary'

    def displayName(self):
        return 'snboundary'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Snboundary()
