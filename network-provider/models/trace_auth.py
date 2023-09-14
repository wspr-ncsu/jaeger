import requests
from .helpers import env

trace_auth_base_url = env('TRACE_AUTH_URL')

def register(cid):
    url = trace_auth_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    return data['vKey']