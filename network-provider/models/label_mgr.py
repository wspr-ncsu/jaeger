import requests
from .helpers import env
import json

label_mgr_base_url = env('LABEL_MGR_URL')

def register(cid):
    url = label_mgr_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    return data['kprf']

def evaluate(labels):
    url = label_mgr_base_url + '/evaluate'
    res = requests.post(url, data={'xs': json.dumps(labels)})
    res.raise_for_status()
    return res.json()