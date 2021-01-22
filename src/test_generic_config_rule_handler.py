"""Author: Mark Hanegraaff -- 2021
    
    This script tests and facilitates the local developmet of the the Generic Compliance Rule Lambda Function.

    It simply allows the function to be executed locally using some test input.

    Before running the script be sure to set the "COMPLIANCE_APP_AWS_EVENTACCTID"
    to the AWS account ID you are using. this will ensure that the event will work
    when supplied to your lambda function. 

    For example:

    export COMPLIANCE_APP_AWS_EVENTACCTID = 999999999999
    python test_generic_config_rule_handler.py
"""

import lambda_functions.generic_config_rule_handler as generic_config_rule_handler

import os
import logging
from support import logging_definition

log = logging.getLogger()

COMPLIANCE_APP_AWS_EVENTACCTID = "COMPLIANCE_APP_AWS_EVENTACCTID"

AWS_ACCOUNT_ID = os.environ.get(COMPLIANCE_APP_AWS_EVENTACCTID, None)

if AWS_ACCOUNT_ID == None:
    log.error("You must specify the following environment variable: %s" %
              COMPLIANCE_APP_AWS_EVENTACCTID)
    exit(1)

TEST_TRIGGERED_EVENT = {
    'version': '1.0',
    'invokingEvent': '{"configurationItemDiff":{"changedProperties":{"SupplementaryConfiguration.BucketVersioningConfiguration.Status":{"previousValue":"Enabled","updatedValue":"Suspended","changeType":"UPDATE"}},"changeType":"UPDATE"},"configurationItem":{"relatedEvents":[],"relationships":[],"configuration":{"name":"cf-templates-1xatrtwowvbwh-us-east-1","owner":{"displayName":null,"id":"eadb5178bbc89e74466498016ffb01b950e758026c6d44296c35646518db9217"},"creationDate":"2020-12-28T03:36:13.000Z"},"supplementaryConfiguration":{"AccessControlList":"{\\"grantSet\\":null,\\"grantList\\":[{\\"grantee\\":{\\"id\\":\\"eadb5178bbc89e74466498016ffb01b950e758026c6d44296c35646518db9217\\",\\"displayName\\":null},\\"permission\\":\\"FullControl\\"}],\\"owner\\":{\\"displayName\\":null,\\"id\\":\\"eadb5178bbc89e74466498016ffb01b950e758026c6d44296c35646518db9217\\"},\\"isRequesterCharged\\":false}","BucketAccelerateConfiguration":{"status":null},"BucketLoggingConfiguration":{"destinationBucketName":null,"logFilePrefix":null},"BucketNotificationConfiguration":{"configurations":{}},"BucketPolicy":{"policyText":null},"BucketTaggingConfiguration":{"tagSets":[{"tags":{"application_id":"ADM"}}]},"BucketVersioningConfiguration":{"status":"Suspended","isMfaDeleteEnabled":null},"IsRequesterPaysEnabled":false,"ServerSideEncryptionConfiguration":{"rules":[{"applyServerSideEncryptionByDefault":{"sseAlgorithm":"AES256","kmsMasterKeyID":null}}]}},"tags":{"application_id":"ADM"},"configurationItemVersion":"1.3","configurationItemCaptureTime":"2021-01-13T05:00:23.319Z","configurationStateId":1610514023319,"awsAccountId":"[[AWSACCTID]]","configurationItemStatus":"OK","resourceType":"AWS::S3::Bucket","resourceId":"cf-templates-1xatrtwowvbwh-us-east-1","resourceName":"cf-templates-1xatrtwowvbwh-us-east-1","ARN":"arn:aws:s3:::cf-templates-1xatrtwowvbwh-us-east-1","awsRegion":"us-east-1","availabilityZone":"Regional","configurationStateMd5Hash":"","resourceCreationTime":"2020-12-28T03:36:13.000Z"},"notificationCreationTime":"2021-01-13T05:00:23.352Z","messageType":"ConfigurationItemChangeNotification","recordVersion":"1.3"}'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    'ruleParameters': '{"MasterAccountID":"[[AWSACCTID]]", "ComplianceCommand":"S3_ENABLE_VERSIONING"}'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    'resultToken': 'xxx',
    'eventLeftScope': False,
    'executionRoleArn': 'arn:aws:iam::[[AWSACCTID]]:role/config-role'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    'configRuleArn': 'arn:aws:config:us-east-1:[[AWSACCTID]]:config-rule/aws-service-rule/config-conforms.amazonaws.com/config-rule-ksup2m'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    'configRuleName': 'compliance-sample-rule-conformance-pack-g8jksafmi',
    'configRuleId': 'config-rule-ksup2m',
    'accountId': '[[AWSACCTID]]'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID)
}

TEST_PERIODIC_EVENT = {
    "invokingEvent": "{\"awsAccountId\":\"[[AWSACCTID]]\",\"notificationCreationTime\":\"2016-07-13T21:50:00.373Z\",\"messageType\":\"ScheduledNotification\",\"recordVersion\":\"1.0\"}".replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    "ruleParameters": '{"MasterAccountID":"[[AWSACCTID]]", "ComplianceCommand":"S3_ENABLE_VERSIONING"}'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    "resultToken": "myResultToken",
    "eventLeftScope": False,
    "executionRoleArn": 'arn:aws:iam::[[AWSACCTID]]:role/config-role'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    "configRuleArn": 'arn:aws:config:us-east-1:[[AWSACCTID]]:config-rule/aws-service-rule/config-conforms.amazonaws.com/config-rule-ksup2m'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    "configRuleName": 'compliance-sample-rule-conformance-pack-g8jksafmi',
    "configRuleId": 'config-rule-ksup2m',
    "accountId": '[[AWSACCTID]]'.replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    "version": "1.0"
}

generic_config_rule_handler.evaluate_compliance(TEST_TRIGGERED_EVENT, {})
