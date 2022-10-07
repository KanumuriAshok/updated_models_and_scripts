"""
Model exported as python.
Name : secondary_bf
Group : 
With QGIS : 31604
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_bf(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('duct', 'duct', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('googlepoles', 'googlepoles', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastruc', 'pia_struc', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetlines', 'streetlines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('A_dp', 'a_dp', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Aireal_drop', 'aireal_drop', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Asn_boundary', 'asn_boundary', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Demand_points', 'demand_points', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('E_nodes', 'e_nodes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Largemdu', 'largemdu', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Lb_ug', 'lb_ug', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Mdu_medium', 'mdu_medium', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ug_cluster', 'ug_cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Withleading', 'withleading', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # brown_2605_1
        alg_params = {
            'demand': parameters['demand'],
            'duct': parameters['duct'],
            'googlepoles': parameters['googlepoles'],
            'landboundary': parameters['landboundary'],
            'piastruc': parameters['piastruc'],
            'streetlines': parameters['streetlines'],
            'native:convexhull_1:asnboundary': parameters['Asn_boundary'],
            'native:difference_2:lb_ug': parameters['Lb_ug'],
            'native:extractbyexpression_4:MDU_medium': parameters['Mdu_medium'],
            'native:extractbyexpression_5:Large_MDU': parameters['Largemdu'],
            'native:joinattributesbylocation_2:WITHLEAD': parameters['Withleading'],
            'native:joinattributesbylocation_3:demand_points': parameters['Demand_points'],
            'native:joinattributesbylocation_4:aireal_drop': parameters['Aireal_drop'],
            'native:joinattributesbylocation_5:a_dp': parameters['A_dp'],
            'script:clustergrpouing_u_1:estimated_sn': parameters['E_nodes'],
            'script:clustergrpouing_u_1:ug_cluster': parameters['Ug_cluster']
        }
        outputs['Brown_2605_1'] = processing.run('model:brown_2605_1', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['A_dp'] = outputs['Brown_2605_1']['native:joinattributesbylocation_5:a_dp']
        results['Aireal_drop'] = outputs['Brown_2605_1']['native:joinattributesbylocation_4:aireal_drop']
        results['Asn_boundary'] = outputs['Brown_2605_1']['native:convexhull_1:asnboundary']
        results['Demand_points'] = outputs['Brown_2605_1']['native:joinattributesbylocation_3:demand_points']
        results['E_nodes'] = outputs['Brown_2605_1']['script:clustergrpouing_u_1:estimated_sn']
        results['Largemdu'] = outputs['Brown_2605_1']['native:extractbyexpression_5:Large_MDU']
        results['Lb_ug'] = outputs['Brown_2605_1']['native:difference_2:lb_ug']
        results['Mdu_medium'] = outputs['Brown_2605_1']['native:extractbyexpression_4:MDU_medium']
        results['Ug_cluster'] = outputs['Brown_2605_1']['script:clustergrpouing_u_1:ug_cluster']
        results['Withleading'] = outputs['Brown_2605_1']['native:joinattributesbylocation_2:WITHLEAD']
        return results

    def name(self):
        return 'secondary_bf'

    def displayName(self):
        return 'secondary_bf'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_bf()
