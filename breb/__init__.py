"""
BREB Consumer Python Client

A Python package for interacting with the Bangladesh REB / Palli Bidyut
consumer-mobile-app API (login, customer details, bill lookup).

Example:
    >>> from breb import BREBConsumerAPI
    >>> client = BREBConsumerAPI()
    >>> client.login(phone_number="01XXXXXXXXX")
    >>> client.customer_info("1010018581900")
    >>> client.bill("1010018581900")
"""

from .breb import BREBConsumerAPI

# Version will be updated by GitHub Actions during release
__version__ = "1.0.0"
__author__ = "Md Minhazul Haque"
__email__ = "mdminhazulhaque@gmail.com"

__all__ = ["BREBConsumerAPI"]
