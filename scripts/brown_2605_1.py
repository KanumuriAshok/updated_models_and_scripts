"""
Model exported as python.
Name : brown_2605_1
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


class Brown_2605_1(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demand', 'demand', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('duct', 'duct', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('googlepoles', 'googlepoles', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastruc', 'pia_struc', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetlines', 'streetlines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Asnboundary', 'asnboundary', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Lb_ug', 'lb_ug', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Mdu_medium', 'MDU_medium', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Large_mdu', 'Large_MDU', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Newhub', 'newhub', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Withlead', 'WITHLEAD', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Aireal_drop', 'aireal_drop', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Estimated_sn', 'estimated_sn', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ug_cluster', 'ug_cluster', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(21, model_feedback)
        results = {}
        outputs = {}

        # Extract by expression:AVAILABLE:WITH AERIAL AS WELL AS UG be clusteredDP
        alg_params = {
            'EXPRESSION': '\"pon_homes\" <= 24',
            'INPUT': parameters['demand'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionavailablewithAerialAsWellAsUgBeClustereddp'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract by expression:large
        alg_params = {
            'EXPRESSION': '\"pon_homes\" > 24',
            'INPUT': parameters['demand'],
            'OUTPUT': parameters['Large_mdu']
        }
        outputs['ExtractByExpressionlarge'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Large_mdu'] = outputs['ExtractByExpressionlarge']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by expression:medium
        alg_params = {
            'EXPRESSION': '\"pon_homes\" > 5',
            'INPUT': parameters['demand'],
            'OUTPUT': parameters['Mdu_medium']
        }
        outputs['ExtractByExpressionmedium'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Mdu_medium'] = outputs['ExtractByExpressionmedium']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # hub
        alg_params = {
            'demandpoints': parameters['demand'],
            'landboundary': parameters['landboundary'],
            'piastructures': parameters['piastruc'],
            'streetlines': parameters['streetlines'],
            'native:fieldcalculator_1:struct_new': QgsProcessing.TEMPORARY_OUTPUT,
            'native:fieldcalculator_2:demand_new': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Hub'] = processing.run('model:hub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by expression:TO LEADIN
        alg_params = {
            'EXPRESSION': ' \"plant_item\" = \'D54\' OR  \"plant_item\" = \'D56\' ',
            'INPUT': parameters['duct'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressiontoLeadin'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # UnionSTRUCTURE
        alg_params = {
            'INPUT': parameters['googlepoles'],
            'OVERLAY': parameters['piastruc'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Unionstructure'] = processing.run('native:union', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Join by lines (hub lines)
        alg_params = {
            'ANTIMERIDIAN_SPLIT': False,
            'GEODESIC': False,
            'GEODESIC_DISTANCE': 1000,
            'HUBS': outputs['Hub']['native:fieldcalculator_1:struct_new'],
            'HUB_FIELD': 'street_id',
            'HUB_FIELDS': [''],
            'SPOKES': outputs['Hub']['native:fieldcalculator_2:demand_new'],
            'SPOKE_FIELD': 'street_id',
            'SPOKE_FIELDS': [''],
            'OUTPUT': parameters['Newhub']
        }
        outputs['JoinByLinesHubLines'] = processing.run('native:hublines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Newhub'] = outputs['JoinByLinesHubLines']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 30,
            'FIELD_NAME': 'structure',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': 'concat( \"struc_name\" , \"struc_name_2\" )',
            'INPUT': outputs['Unionstructure']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Distance to nearest hub (line to hub)
        alg_params = {
            'FIELD': 'structure',
            'HUBS': outputs['FieldCalculator']['OUTPUT'],
            'INPUT': parameters['demand'],
            'UNIT': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestHubLineToHub'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Extract by expression :STRUCnot bur
        alg_params = {
            'EXPRESSION': ' \"HubName\" NOT LIKE \'BUR%\' ',
            'INPUT': outputs['DistanceToNearestHubLineToHub']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionStrucnotBur'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by expression :STRUCnotcab
        alg_params = {
            'EXPRESSION': '\"HubName\" NOT LIKE \'CAB%\'',
            'INPUT': outputs['ExtractByExpressionStrucnotBur']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionStrucnotcab'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Extract by expression:excludejb
        alg_params = {
            'EXPRESSION': ' \"HubName\" NOT LIKE \'JC%\' ',
            'INPUT': outputs['ExtractByExpressionStrucnotcab']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionexcludejb'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Join attributes by location_ardrp
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': outputs['ExtractByExpressionexcludejb']['OUTPUT'],
            'JOIN': outputs['JoinByLinesHubLines']['OUTPUT'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,
            'PREDICATE': [2],
            'PREFIX': '',
            'OUTPUT': parameters['Aireal_drop']
        }
        outputs['JoinAttributesByLocation_ardrp'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Aireal_drop'] = outputs['JoinAttributesByLocation_ardrp']['OUTPUT']

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Join attributes by locationFEDBYAERIAL
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': parameters['landboundary'],
            'JOIN': outputs['JoinAttributesByLocation_ardrp']['OUTPUT'],
            'JOIN_FIELDS': [''],
            'METHOD': 1,
            'PREDICATE': [0,1,2,3,4,5],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationfedbyaerial'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Dissolve
        alg_params = {
            'FIELD': ['HubName'],
            'INPUT': outputs['JoinAttributesByLocationfedbyaerial']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Difference:TOTAL UG
        alg_params = {
            'INPUT': parameters['landboundary'],
            'OVERLAY': outputs['JoinAttributesByLocationfedbyaerial']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DifferencetotalUg'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Join attributes by locationUGTO BE CLUSTERED DP
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': outputs['ExtractByExpressionavailablewithAerialAsWellAsUgBeClustereddp']['OUTPUT'],
            'JOIN': outputs['DifferencetotalUg']['OUTPUT'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,
            'PREDICATE': [0],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationugtoBeClusteredDp'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # clustergrpouing_u
        alg_params = {
            'VERBOSE_LOG': False,
            'demandpoints': outputs['JoinAttributesByLocationugtoBeClusteredDp']['OUTPUT'],
            'streetlines': parameters['streetlines'],
            'Ug_cluster': parameters['Ug_cluster'],
            'Ug_est_nodes': parameters['Estimated_sn'],
            'Ug_outl': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Clustergrpouing_u'] = processing.run('script:clustergrpouing_u', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Estimated_sn'] = outputs['Clustergrpouing_u']['Ug_est_nodes']
        results['Ug_cluster'] = outputs['Clustergrpouing_u']['Ug_cluster']

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Convex hull
        alg_params = {
            'INPUT': outputs['Dissolve']['OUTPUT'],
            'OUTPUT': parameters['Asnboundary']
        }
        outputs['ConvexHull'] = processing.run('native:convexhull', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Asnboundary'] = outputs['ConvexHull']['OUTPUT']

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': outputs['DifferencetotalUg']['OUTPUT'],
            'JOIN': outputs['ExtractByExpressiontoLeadin']['OUTPUT'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,
            'PREDICATE': [0],
            'PREFIX': '',
            'OUTPUT': parameters['Withlead']
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Withlead'] = outputs['JoinAttributesByLocation']['OUTPUT']

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # DifferenceUG TO CG
        alg_params = {
            'INPUT': outputs['DifferencetotalUg']['OUTPUT'],
            'OVERLAY': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OUTPUT': parameters['Lb_ug']
        }
        outputs['DifferenceugToCg'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Lb_ug'] = outputs['DifferenceugToCg']['OUTPUT']
        return results

    def name(self):
        return 'brown_2605_1'

    def displayName(self):
        return 'brown_2605_1'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Brown_2605_1()
