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
        self.addParameter(QgsProcessingParameterVectorLayer('plotboundary', 'plotboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Clean', 'clean', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('FinalBoundary', 'FINAL BOUNDARY', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        print(f"context = {context}")
         
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # lrnb
        alg_params = {
            'cluster': parameters['cluster'],
            'landboundry': parameters['plotboundary'],
            'native:deleteholes_1:cleanboundary': parameters['Clean']
        }
        outputs['Lrnb'] = processing.run('model:lrnb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Clean'] = outputs['Lrnb']['native:deleteholes_1:cleanboundary']
        
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # finalbndry
        alg_params = {
            'selected': outputs['Lrnb']['native:deleteholes_1:cleanboundary'],
            'native:convexhull_1:op': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Finalbndry'] = processing.run('model:finalbndry', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
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

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'STYLE': 'C:\\Users\\jyothy\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\processing\\models\\STYLE1.qml'
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
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
