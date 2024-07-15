import requests
from . import helpers
from blspy import G1Element
from . import database as db
from . import http
from .config import TA_BASE_URL, TA_PUBK
from typing import List
from . import redis

def get_public_key() -> G1Element:
    return G1Element.from_bytes(bytes.fromhex(TA_PUBK))

def request_authorization(group: dict, labels: List[str]):
    """Request signature from Trace Auth"""
    url = f'{TA_BASE_URL}/authorize'
    data = http.post(url=url, data=labels, group=group)
    return data
