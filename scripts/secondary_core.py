"""
Model exported as python.
Name : secondary_core
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


class Secondary_core(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('feederring', 'feeder ring', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Fw4', 'fw4', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Highlighted', 'highlighted', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Proposed_sj', 'proposed_sj', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # core_1
        alg_params = {
            'feederring': parameters['feederring'],
            'native:extractbyexpression_2:highlighted': parameters['Highlighted'],
            'native:pointsalonglines_1:proposed_sj': parameters['Proposed_sj'],
            'native:pointsalonglines_2:fw4': parameters['Fw4']
        }
        outputs['Core_1'] = processing.run('model:core_1', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Fw4'] = outputs['Core_1']['native:pointsalonglines_2:fw4']
        results['Highlighted'] = outputs['Core_1']['native:extractbyexpression_2:highlighted']
        results['Proposed_sj'] = outputs['Core_1']['native:pointsalonglines_1:proposed_sj']
        return results

    def name(self):
        return 'secondary_core'

    def displayName(self):
        return 'secondary_core'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_core()
