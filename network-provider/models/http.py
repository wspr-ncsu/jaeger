import requests
from .groupsig import sign
import json

def post(url, data, headers = None):
    """Post data to a given URL"""
    
    data = json.dumps(data)
    headers = make_headers(headers, data)
    res = requests.post(url, data={ 'payload': data }, headers=headers)
    res.raise_for_status()
    res = res.json()
    
    return res

def make_headers(override=None, payload=None):
    """Make headers for a request"""

    headers = {}
    
    if (payload):
        headers['X-Privytrace'] = 'Sig ' + sign(payload)
    
    return headers if not override else { **headers, **override }

    