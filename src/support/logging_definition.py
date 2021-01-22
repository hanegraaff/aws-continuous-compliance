"""Author: Mark Hanegraaff -- 2021
This module initializes the logger, so that it can produce consistent logging
across all services
"""
import logging

# fix for aws Lambda
ROOT = logging.getLogger()
if ROOT.handlers:
    for handler in ROOT.handlers:
        ROOT.removeHandler(handler)
#

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')
