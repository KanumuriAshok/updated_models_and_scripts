"""
Model exported as python.
Name : secondary_structures
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class Secondary_structures(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('googlepoles', 'googlepoles', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructures', 'pia_structures', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Structures', 'structures', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # structures
        alg_params = {
            'googlepoles': parameters['googlepoles'],
            'piastructures': parameters['piastructures'],
            'native:fieldcalculator_2:structures': parameters['Structures']
        }
        outputs['Structures'] = processing.run('model:structures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Structures'] = outputs['Structures']['native:fieldcalculator_2:structures']
        return results

    def name(self):
        return 'secondary_structures'

    def displayName(self):
        return 'secondary_structures'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_structures()
