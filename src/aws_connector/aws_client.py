"""Author: Mark Hanegraaff -- 2021
"""

import boto3
from support.logging_definition import logging
from exception.exceptions import AWSError
import uuid

log = logging.getLogger()


class AWSClient():
    '''
        The AWS Client is a value add class on the of the Boto3 library
        that creates service clients after optionally assuming-role to a
        a different account
    '''

    REGION_NAME = ""

    @classmethod
    def update_region_name(cls, region_name: str):
        cls.REGION_NAME = region_name

    def __init__(self, assume_role_arn: str = None):
        '''
            Initalizes the boto3 session and optionally assume role
            if an assume role arn is supplied.

            Parameters
            ----------
            assume_role_arn: str
                Optional assume role arn. If one is provided, an
                assume-role operation will take place

        '''
        try:
            if assume_role_arn == None:
                self.session = boto3.Session()
            else:
                sts_client = boto3.client('sts')
                assumed_role_response = sts_client.assume_role(
                    RoleArn=assume_role_arn,
                    RoleSessionName=str(uuid.uuid4())
                )

                credentials = assumed_role_response['Credentials']

                self.session = boto3.Session(
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken']
                )
        except Exception as e:
            raise AWSError("Could not initialize AWSClient object", e)

        # store the current region name faciliate some SDK calls
        self.update_region_name(self.session.region_name)

    def get_boto_client(self, service_name: str):
        return self.session.client(service_name)
