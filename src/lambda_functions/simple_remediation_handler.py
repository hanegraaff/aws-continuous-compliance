"""Author: Mark Hanegraaff -- 2021
"""
import boto3
import json
from aws_connector.aws_client import AWSClient
from exception.exceptions import ValidationError
import compliance.factory as factory

import logging
from support import logging_definition

log = logging.getLogger()


def remediate_resource(event, context):
    """
    Lambda hander for the Generic Remediation SSM Document. The lambda function
    expects a payload that matches the SSM Document definition.

    {
        "resourceID" : "bucketA", 
        "remediationAccountID" : "999999999999", 
        "complianceCommand" : "S3_ENABLE_VERSIONING"
    }
    """
    def parse_config_event(event: dict):
        '''
            Parse the payload, validate it, and return the
            relevant fields
        '''

        try:
            resource_id = event["resourceID"]
            remediation_account_id = event["remediationAccountID"]
            compliance_command = event["complianceCommand"]
        except Exception as e:
            raise ValidationError(
                "Could not parse function payload, because one or more fields were invalid", e)

        return (resource_id, remediation_account_id, compliance_command)

    log.info("Generic Remediation Handler was invoked")

    try:
        (resource_id, remediation_account_id,
         compliance_command) = parse_config_event(event)

        log.info("Remediating non-compliant resource: %s, for command: %s in AWS Account: %s" %
                 (resource_id, compliance_command, remediation_account_id))
        execution_role_arn = 'arn:aws:iam::%s:role/role-compliance-generic-remediation' % remediation_account_id

        compliance_module = factory.load_compliance_module(
            compliance_command, execution_role_arn, remediation_account_id)
        compliance_module.remediate_resource(resource_id)

    except Exception as e:
        log.error(
            "There was an error remediating non-compliant resource, because: %s" % str(e))
        log.error("Function Payload: %s" % str(event))
        raise e
