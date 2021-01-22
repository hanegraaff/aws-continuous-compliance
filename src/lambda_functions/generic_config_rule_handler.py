"""Author: Mark Hanegraaff -- 2021
"""
import boto3
import json
from aws_connector.aws_client import AWSClient
from exception.exceptions import ValidationError
from compliance import factory

import logging
from support import logging_definition

log = logging.getLogger()


def evaluate_compliance(event, context):
    '''
        Generic Config rule Lambda Function main entrypoint
    '''
    def parse_config_event(event: dict):
        '''
            Parse the config event and extract info needed. 
            If anything is missing raise a Validation Error
        '''
        try:
            aws_account_id = event['accountId']
            rule_parameters = json.loads(event['ruleParameters'])
            invoking_event = json.loads(event['invokingEvent'])
        except Exception as e:
            raise ValidationError("Could not parse Config Payload", e)

        # validate the rule parameters
        try:
            rule_parameters['ComplianceCommand']
        except Exception as e:
            raise ValidationError("Invalid Rule Parameters", e)

        return (aws_account_id, rule_parameters, invoking_event)

    log.info("Generic Config rule was invoked")

    (aws_account_id, rule_parameters, invoking_event) = parse_config_event(event)
    log.info("Event Account Origin: %s" % aws_account_id)
    execution_role_arn = 'arn:aws:iam::%s:role/role-compliance-generic-rule' % aws_account_id

    try:
        rule_name = rule_parameters['ComplianceCommand']

        # Load the appropriate compliance module and apply it.
        compliance_module = factory.load_compliance_module(
            rule_parameters['ComplianceCommand'], execution_role_arn, aws_account_id)

        event_type = invoking_event['messageType']
        if event_type == 'ScheduledNotification':
            log.info("Processing a scheduled event")
            results = compliance_module.evaluate_compliance_all()
            ordering_timestamp = invoking_event['notificationCreationTime']
        else:
            log.info("Processing a configuration change event")
            configuration_item = invoking_event['configurationItem']
            results = validate_configuration_item(configuration_item)
            if results is None:
                results = compliance_module.evaluate_compliance_resource(
                    configuration_item)
            ordering_timestamp = configuration_item[
                'configurationItemCaptureTime']

        # Send evaluations back to the config service
        # Note that we are interacting with the master account and so
        # no assume role is needed
        aws_client = AWSClient()
        config_client = aws_client.get_boto_client("config")

        evaluations = []
        for evaluation in results:
            evaluations.append({
                'ComplianceResourceType': evaluation["resource_type"],
                'ComplianceResourceId':   evaluation['resource_id'],
                'ComplianceType':         evaluation["compliance_type"],
                "Annotation":             evaluation["annotation"],
                'OrderingTimestamp':      ordering_timestamp
            })
        log.info("Publishing compliance status of %d resource(s) to Config Service" % len(
            evaluations))
        config_client.put_evaluations(
            Evaluations=evaluations,
            ResultToken=event['resultToken'])
    except Exception as e:
        log.error("There was an error executing evaluating compliance rule: %s" % e)
        log.error("Function Payload: %s" % str(event))
        raise e


def validate_configuration_item(configuration_item):
    '''
        Checks the configuration item and determines whether it shoukd be
        filtered out
    '''
    # Check if resource was deleted
    if configuration_item['configurationItemStatus'] == "ResourceDeleted":
        return {
            "resource_type": configuration_item['resourceType'],
            "resource_id": configuration_item['resourceId'],
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "This resource was deleted."
        }

    return None
