"""Author: Mark Hanegraaff -- 2021
    
    This script tests and facilitates the local developmet of the the Generic Remediation Lambda Function.

    It simply allows the function to be executed locally using some test input.

    Before running the script be sure to set the "COMPLIANCE_APP_AWS_EVENTACCTID"
    to the AWS account ID you are using. this will ensure that the event will work
    when supplied to your lambda function. 

    For example:

    export COMPLIANCE_APP_AWS_EVENTACCTID = 999999999999
    python test_simple_remediation_handler.py
"""

import lambda_functions.simple_remediation_handler as simple_remediation_handler

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

TEST_EVENT = {
    "resourceID": "bucketA",
    "remediationAccountID": "[[AWSACCTID]]".replace("[[AWSACCTID]]", AWS_ACCOUNT_ID),
    "complianceCommand": "S3_ENABLE_VERSIONING"
}

simple_remediation_handler.remediate_resource(TEST_EVENT, {})
