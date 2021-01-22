"""Author: Mark Hanegraaff -- 2021

This module contains all compliance rules pertinent to the S3 Service
"""


def versioning_enabled(status: str):
    '''
        Checks the S3 veriong status and return true if enabled. Otherwise returns False
    '''
    if status == 'Enabled':
        return True
    else:
        return False
