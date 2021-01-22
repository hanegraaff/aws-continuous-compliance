"""Author: Mark Hanegraaff -- 2021

This module contains a small factory capable of generating appropriate
compliance module objects based on a name
"""

from exception.exceptions import NotSupportedError
from compliance.modules.s3_versioning import S3Versioning
from aws_connector.aws_client import AWSClient


def load_compliance_module(module_name: str, assume_role_name: str, aws_account_id: str):
    '''
        Returns the appropriate compliance module module given
        the module name. If one cannot be found, raise a NotSupported error
    '''

    if module_name == "S3_ENABLE_VERSIONING":
        return S3Versioning(AWSClient(assume_role_name), aws_account_id)
    else:
        raise NotSupportedError
