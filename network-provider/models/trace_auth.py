import requests
from .helpers import env
from blspy import G1Element

trace_auth_base_url = env('TRACE_AUTH_URL', 'http://localhost:9001')

def register(cid: str) -> G1Element:
    url = trace_auth_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    return G1Element.from_bytes(bytes.fromhex(data['pk']))
