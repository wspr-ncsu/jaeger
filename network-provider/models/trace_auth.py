import requests
from .helpers import env
from witenc import utils

trace_auth_base_url = env('TRACE_AUTH_URL', 'http://localhost:9001')

def register(cid):
    url = trace_auth_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    return utils.import_pk(data['vk'])
