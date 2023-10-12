from .helpers import env
import requests
from .groupsig import sign
import json

traceback_base_url = env('TRACEBACK_URL', 'http://localhost:9003')

def post(endpoint, data, headers = None):
    """Post data to a given URL"""
    
    url = traceback_base_url + f'/{endpoint}'
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

    