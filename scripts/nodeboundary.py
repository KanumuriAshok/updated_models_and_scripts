"""
Model exported as python.
Name : NODEBOUNDARY
Group : 
With QGIS : 32003
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Nodeboundary(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('cluster', 'cluster', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('plotboundary', 'plotboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('FinalBoundary', 'FINAL BOUNDARY', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # demand_land_join
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['plotboundary'],
            'JOIN': parameters['demand'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Demand_land_join'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # lrnb
        alg_params = {
            'cluster': parameters['cluster'],
            'landboundry': parameters['plotboundary'],
            'native:deleteholes_1:cleanboundary': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Lrnb'] = processing.run('model:lrnb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # lrnb_mdu
        alg_params = {
            'cluster': parameters['cluster'],
            'landboundry': outputs['Demand_land_join']['OUTPUT'],
            'native:deleteholes_1:cleanboundary': QgsProcessing.TEMPORARY_OUTPUT,
            'native:extractbyexpression_1:match': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Lrnb_mdu'] = processing.run('model:lrnb_mdu', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # finalbndry
        alg_params = {
            'selected': outputs['Lrnb_mdu']['native:deleteholes_1:cleanboundary'],
            'native:convexhull_1:op': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Finalbndry'] = processing.run('model:finalbndry', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '\"cluster_id\" IS NOT NULL',
            'INPUT': outputs['Finalbndry']['native:convexhull_1:op'],
            'OUTPUT': parameters['FinalBoundary']
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['FinalBoundary'] = outputs['ExtractByExpression']['OUTPUT']
        return results

    def name(self):
        return 'NODEBOUNDARY'

    def displayName(self):
        return 'NODEBOUNDARY'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Nodeboundary()
