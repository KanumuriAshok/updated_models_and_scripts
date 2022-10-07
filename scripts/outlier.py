"""
Model exported as python.
Name : outlier
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Outlier(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('outlier', 'outlier', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('cluster', 'cluster', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Outlier', 'outlier', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # outlierjoin
        alg_params = {
            'cluster': parameters['cluster'],
            'outlier': parameters['outlier'],
            'native:joinattributestable_2:trial': parameters['Outlier']
        }
        outputs['Outlierjoin'] = processing.run('model:outlierjoin', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Outlier'] = outputs['Outlierjoin']['native:joinattributestable_2:trial']
        return results

    def name(self):
        return 'outlier'

    def displayName(self):
        return 'outlier'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Outlier()
