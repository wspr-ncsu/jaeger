import requests
from . import helpers
from blspy import G1Element
from . import database as db
from . import http
from typing import List

trace_auth_base_url = helpers.env('TRACE_AUTH_URL', 'http://localhost:9992')

tapk_key = 'TA.pk'

def register() -> G1Element:
    db.connect()
    
    pk: str = db.find(tapk_key)
    
    if not pk:
        raise Exception("Trace Auth Public Key not found")
    
    return G1Element.from_bytes(bytes.fromhex(pk))

def authorize(group: dict, labels: List[str]):
    """Request signature from Trace Auth"""
    url = f'{trace_auth_base_url}/authorize'
    res = http.post(url=url, data=labels, group=group)
    return res['res']
