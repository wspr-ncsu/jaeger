import requests
from . import helpers
from blspy import G1Element
from . import database as db
from . import http

trace_auth_base_url = helpers.env('TRACE_AUTH_URL', 'http://localhost:9992')

tapk_key = 'TA.pk'

def register(cid: str) -> G1Element:
    db.connect()
    
    pk: str = db.find(tapk_key)
    
    if not pk:
        raise Exception("Trace Auth Public Key not found")
    
    return G1Element.from_bytes(bytes.fromhex(pk))

def authorize(group: dict, labels: list, sigs: list):
    """Request signature from Trace Auth"""
    records = []
    
    for index, label in enumerate(labels):
        records.append({ 'l': label, 's': sigs[index]})
    
    url = f'{trace_auth_base_url}/authorize'
    res = http.post(url=url, data=records, group=group)
    return res
