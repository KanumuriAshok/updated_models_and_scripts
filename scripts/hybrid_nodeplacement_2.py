"""
Model exported as python.
Name : hybrid_nodeplacement_2
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


class Hybrid_nodeplacement_2(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('clusterboundary', 'clusterboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('googlepoles', 'googlepoles', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructure', 'piastructure', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ugnode_sn', 'ugnode_sn', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Existingpoles_asn', 'existingpoles_asn', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(13, model_feedback)
        results = {}
        outputs = {}

        # Extract by expression_aerial
        alg_params = {
            'EXPRESSION': 'regexp_match(  "struct_id" ,\'p\')',
            'INPUT': parameters['clusterboundary'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_aerial'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Centroids_aerial
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['ExtractByExpression_aerial']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids_aerial'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': ' "category"  =  \'POLE\' ',
            'INPUT': parameters['piastructure'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extract by expression_jb
        alg_params = {
            'EXPRESSION': ' "obj_class"  =  \'JB\' ',
            'INPUT': parameters['piastructure'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_jb'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by expression_jb23
        alg_params = {
            'EXPRESSION': '"plant_item" is not  \'JB 23\' ',
            'INPUT': outputs['ExtractByExpression_jb']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_jb23'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 100,
            'FIELD_NAME': 'polename',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "concat('p', @row_number)",
            'INPUT': parameters['googlepoles'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract by expression_ug
        alg_params = {
            'EXPRESSION': 'regexp_match(  "struct_id" ,\'u\')',
            'INPUT': parameters['clusterboundary'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_ug'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Centroids_ug
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['ExtractByExpression_ug']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids_ug'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['ExtractByExpression']['OUTPUT'],outputs['FieldCalculator']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Extract by expression_jb26
        alg_params = {
            'EXPRESSION': '"plant_item" is not \'JB 26\' ',
            'INPUT': outputs['ExtractByExpression_jb23']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_jb26'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,  # Prefer aligning nodes, insert extra vertices where required
            'INPUT': outputs['Centroids_ug']['OUTPUT'],
            'REFERENCE_LAYER': outputs['ExtractByExpression_jb26']['OUTPUT'],
            'TOLERANCE': 20,
            'OUTPUT': parameters['Ugnode_sn']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Ugnode_sn'] = outputs['SnapGeometriesToLayer']['OUTPUT']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Field calculator_finalpoles
        alg_params = {
            'FIELD_LENGTH': 100,
            'FIELD_NAME': 'struct_id',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'concat(  "struc_name", "polename" )',
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator_finalpoles'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,  # Prefer aligning nodes, insert extra vertices where required
            'INPUT': outputs['Centroids_aerial']['OUTPUT'],
            'REFERENCE_LAYER': outputs['FieldCalculator_finalpoles']['OUTPUT'],
            'TOLERANCE': 20,
            'OUTPUT': parameters['Existingpoles_asn']
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Existingpoles_asn'] = outputs['SnapGeometriesToLayer']['OUTPUT']
        return results

    def name(self):
        return 'hybrid_nodeplacement_2'

    def displayName(self):
        return 'hybrid_nodeplacement_2'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Hybrid_nodeplacement_2()
