import json
import requests
from . import groupsig

def post(url: str, data: dict, group: dict, headers: dict = None):
    """Post data to a given URL"""
    
    data = json.dumps(data)
    headers = make_headers(group=group, payload=data, override=headers)
    res = requests.post(url, data={ 'payload': data }, headers=headers)
    res.raise_for_status()
    res = res.json()
    
    return res

def make_headers(group: dict, payload: str = None, override: dict = None):
    """Make headers for a request"""

    headers = {}
    
    if (payload):
        payload = bytes(payload, 'utf-8')
        headers['X-Privytrace'] = 'Sig ' + groupsig.sign(group=group, msg=payload)
    
    return headers if not override else { **headers, **override }

    