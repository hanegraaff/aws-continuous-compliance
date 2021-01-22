"""Author: Mark Hanegraaff -- 2021
"""

import logging
from support import logging_definition
from exception.exceptions import NotSupportedError, ValidationError
from compliance.modules.base_module import BaseComplianceModule
import compliance.rules.s3_rules as s3_rules
import aws_connector.s3_boto_wrapper as s3
log = logging.getLogger()


class S3Versioning(BaseComplianceModule):
    '''
        A compliance module addressing S3 Bucket versioning.

        Please see BaseComplianceModule for additional documentation
    '''

    APPLICABLE_RESOURCE = "AWS::S3::Bucket"
    MODULE_NAME = "S3_ENABLE_VERSIONING"
    DESCRIPTION = "Module that checks if S3 Versioning is enabled"

    def __init__(self, aws_client_object: object, aws_account_id: str):
        super().__init__(aws_client_object, aws_account_id)

    def evaluate_compliance_all(self):
        '''
            Evaluate the compliance of all available S3 buckets
        '''
        log.info("Evaluating the compliance rule for applicable resources: %s" %
                 self.APPLICABLE_RESOURCE)

        (versioning_dict, exception_dict) = s3.get_all_bucket_versioning_configuration(
            self.aws_client_object.get_boto_client('s3'))

        evaluations = []

        for bucket_name in versioning_dict.keys():
            if s3_rules.versioning_enabled(versioning_dict[bucket_name]):
                log.info("%s - %s -> %s" %
                         (bucket_name, self.MODULE_NAME, "COMPLIANT"))
                evaluations.append({
                    "resource_type": self.APPLICABLE_RESOURCE,
                    "resource_id": bucket_name,
                    "compliance_type": "COMPLIANT",
                    "annotation": "Object Versioning is enabled"
                })
            else:
                log.info("%s - %s -> %s" %
                         (bucket_name, self.MODULE_NAME, "NON_COMPLIANT"))
                evaluations.append({
                    "resource_type": self.APPLICABLE_RESOURCE,
                    "resource_id": bucket_name,
                    "compliance_type": "NON_COMPLIANT",
                    "annotation": "Object Versioning is not enabled"
                })

        log.warning(
            "The following S3 bukets could not be evaluated because of an AWS Error")
        for bucket_name in exception_dict.keys():
            log.warning("%s - %s -> %s" % (bucket_name,
                                           self.MODULE_NAME, exception_dict[bucket_name]))

        return evaluations

    def evaluate_compliance_resource(self, configuration_item: dict):
        '''
            evaluates the compliance of a single s3 bucket, contained in the
            configuration item.
        '''
        bucket_name = configuration_item['resourceId']

        log.info(
            "Checking if versioning in enabled for the S3 Bucket: %s" % bucket_name)

        if self.config_item_resource_applicable(configuration_item) == False:
            log.info("This even is not applicable for this module's resource type: " %
                     self.APPLICABLE_RESOURCE)
            return [{
                "resource_type": configuration_item['resourceType'],
                "resource_id": bucket_name,
                "compliance_type": "NOT_APPLICABLE",
                "annotation": "The rule doesn't apply to resources of type "
                    + configuration_item["resourceType"] + "."
                    }]

        try:
            supplementary_config = configuration_item[
                'supplementaryConfiguration']
        except Exception as e:
            raise ValidationError(
                "Count not extract S3 supplementary configuration from event", e)

        versioning_flag = supplementary_config.get(
            "BucketVersioningConfiguration", {}).get('status', None)

        if s3_rules.versioning_enabled(versioning_flag) == True:
            log.info("%s - %s -> %s" %
                     (bucket_name, self.MODULE_NAME, "COMPLIANT"))
            return [{
                "resource_type": configuration_item['resourceType'],
                "resource_id": bucket_name,
                "compliance_type": "COMPLIANT",
                "annotation": "Object Versioning is enabled"
            }]
        else:
            log.info("%s - %s -> %s" %
                     (bucket_name, self.MODULE_NAME, "NON_COMPLIANT"))
            return [{
                "resource_type": configuration_item['resourceType'],
                "resource_id": bucket_name,
                "compliance_type": "NON_COMPLIANT",
                "annotation": "Object Versioning is not enabled"
            }]

    def remediate_resource(self, resource_id: str):
        '''
            remediates a non-compliant s3 bucket by adding versionong to it.
        '''

        boto_s3_client = self.aws_client_object.get_boto_client('s3')

        log.info("Remediating: %s : %s : %s" %
                 (self.APPLICABLE_RESOURCE, resource_id, self.MODULE_NAME))
        s3.enable_versioning(boto_s3_client, resource_id)
