"""Author: Mark Hanegraaff -- 2021
"""

import boto3
from exception.exceptions import AWSError
from aws_connector.aws_client import AWSClient


def get_all_buckets(boto_s3_client: object):
    '''
        Returns the list of S3 buckets belonging to all regions
        as a list. E.g.

        ['bucketA', 'bucketB', 'bucketC', ...]
    '''
    all_s3_buckets = []

    try:
        bucket_list = boto_s3_client.list_buckets()

        for bucket in bucket_list['Buckets']:
            bucket_name = bucket['Name']

            all_s3_buckets.append(bucket_name)
    except Exception as e:
        raise AWSError("Could not list s3 buckets", e)

    return all_s3_buckets


def get_all_bucket_versioning_configuration(boto_s3_client: object):
    '''
        Scans all S3 buckets and returns the bucket versioning configuration
        as a dictionary. E.g.

        {
            "bucketA": "Enabled"
            "bucketB": "Suspended"
        }

        additionally retuns all buckets that could not be scanned because of an
        error as a dictionary. E.g.

        {
            "bucketC": ExceptionObject
        }
    '''

    all_bucket_names = get_all_buckets(boto_s3_client)

    versioning_dict = {}
    exception_dict = {}

    for bucket_name in all_bucket_names:
        try:
            versioning_response = boto_s3_client.get_bucket_versioning(
                Bucket=bucket_name)
            versioning_dict[bucket_name] = versioning_response.get(
                'Status', 'Suspended')
        except Exception as e:
            exception_dict[bucket_name] = e

    return (versioning_dict, exception_dict)


def enable_versioning(boto_s3_client: object, bucket_name: str):
    '''
        Enables versioning given a bucket name.
    '''

    try:
        boto_s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                'Status': 'Enabled'
            }
        )
    except Exception as e:
        raise AWSError(
            "Could not enable versioning on S3 Bucket: %s" % bucket_name, e)
