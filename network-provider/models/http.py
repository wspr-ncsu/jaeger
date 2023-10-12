import requests
from .groupsig import sign
import json

def post(url, data, headers = None):
    """Post data to a given URL"""
    
    headers = make_headers(headers, json.dumps(data))
    res = requests.post(url, data=data, headers=headers)
    res.raise_for_status()
    res = res.json()
    
    return res

def make_headers(override=None, payload=None):
    """Make headers for a request"""

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    
    if (payload):
        headers['X-Privytrace-Sig'] = 'Sig ' + sign(payload)
    
    return headers if not override else { **headers, **override }

    