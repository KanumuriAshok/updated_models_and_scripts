"""
Model exported as python.
Name : AddressCreation_1
Group : Model
With QGIS : 32000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Addresscreation_1(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('DemandPoints', 'DemandPoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('PIAStructures', 'On-Existing', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('proposed', 'Proposed', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Address', 'Address', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Convert Multipoints to Points
        alg_params = {
            'MULTIPOINTS': parameters['proposed'],
            'POINTS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvertMultipointsToPoints'] = processing.run('saga:convertmultipointstopoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Union
        alg_params = {
            'INPUT': outputs['ConvertMultipointsToPoints']['POINTS'],
            'OVERLAY': parameters['PIAStructures'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Union'] = processing.run('native:union', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 30,
            'FIELD_NAME': 'conc',
            'FIELD_PRECISION': 30,
            'FIELD_TYPE': 2,  # String
            'FORMULA': ' concat( \"postcode\",\'-\',\"bld_num\"  )',
            'INPUT': parameters['DemandPoints'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELDS_TO_COPY': ['conc'],
            'INPUT': outputs['Union']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculator']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': parameters['Address']
        }
        outputs['JoinAttributesByNearest'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Address'] = outputs['JoinAttributesByNearest']['OUTPUT']
        return results

    def name(self):
        return 'AddressCreation_1'

    def displayName(self):
        return 'AddressCreation_1'

    def group(self):
        return 'Model'

    def groupId(self):
        return 'Model'

    def createInstance(self):
        return Addresscreation_1()
