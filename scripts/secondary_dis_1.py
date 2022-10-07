"""
Model exported as python.
Name : secondary_dis_1
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


class Secondary_dis_1(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('existingducts', 'existing_ducts', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('existingstructures', 'existing_structures', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('primarynodes', 'primary nodes', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('proposednodes', 'proposed_nodes', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Proposed_ducts', 'proposed_ducts', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Usable_existing_ducts', 'usable_existing_Ducts', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # distribution_1005
        alg_params = {
            'existingducts': parameters['existingducts'],
            'existingstructures': parameters['existingstructures'],
            'gaist': parameters['gaist'],
            'primarynodes': parameters['primarynodes'],
            'proposednodes': parameters['proposednodes'],
            'native:extractbyexpression_1:usable_existing_ducts': parameters['Usable_existing_ducts'],
            'native:shortestpathpointtolayer_1:proposed_duct': parameters['Proposed_ducts']
        }
        outputs['Distribution_1005'] = processing.run('model:distribution_1005', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Proposed_ducts'] = outputs['Distribution_1005']['native:shortestpathpointtolayer_1:proposed_duct']
        results['Usable_existing_ducts'] = outputs['Distribution_1005']['native:extractbyexpression_1:usable_existing_ducts']
        return results

    def name(self):
        return 'secondary_dis_1'

    def displayName(self):
        return 'secondary_dis_1'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_dis_1()
