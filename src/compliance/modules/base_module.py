"""Author: Mark Hanegraaff -- 2021
"""
from abc import ABC, abstractmethod
from aws_connector.aws_client import AWSClient

import logging
from support import logging_definition

log = logging.getLogger()


class BaseComplianceModule(ABC):
    '''
        Base Class for all compliance Modules. It contains methods that support
        both detection and remediation functionality.


        Attributes:
            APPLICABLE_RESOURCE: The type of resource targeted by this module.
                For example "AWS::S3::Bucket"
            MODULE_NAME: The name of the module. This must match the value of 
                the "ComplianceCommand" supplied to the corresponding Config Rule 
                and SSM Documents.
            DESCRIPTION: A description of this module

    '''
    # The resource type targeted by the detective module "AWS::S3::Bucket"
    APPLICABLE_RESOURCE = ""
    MODULE_NAME = ""

    # A human readable description of what the mdoule does
    DESCRIPTION = ""

    def __init__(self, aws_client_object: object, aws_account_id: str):
        self.aws_client_object = aws_client_object
        self.aws_account_id = aws_account_id
        log.info("Initalized compliance module: %s targeting AWS Account ID: %s" % (
            self.MODULE_NAME, self.aws_account_id))
        log.info("Module description: %s" % self.DESCRIPTION)
        log.info("Applicable Resource: %s" % self.APPLICABLE_RESOURCE)

    @abstractmethod
    def evaluate_compliance_all(self):
        '''
            Evaluate the compliance of all resources that are covered by this
            rule. This method must be called when the AWS Config rule is triggered
            on a schedule.
        '''
        pass

    @abstractmethod
    def evaluate_compliance_resource(self, configuration_item: dict):
        '''
            Evaluates the compliance of the resource supplied, based on the
            module criteria. This method must be called when the AWS Config rule
            is triggered via a configuration change.
        '''
        pass

    @abstractmethod
    def remediate_resource(self, resource_id: str):
        '''
            Remediates a resource based on the module's criteria. This method must
            be called by Remediation Lambda function.
        '''
        pass

    def config_item_resource_applicable(self, configuration_item: dict):
        '''
            Returns True if the configuration item resource type matches that
            of the detective module. This is used to identify configuration events
            that are not suitable for the target module.
        '''

        if configuration_item["resourceType"] != self.APPLICABLE_RESOURCE:
            return False
        else:
            return True
