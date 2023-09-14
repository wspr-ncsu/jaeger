import requests
from .helpers import env

label_mgr_base_url = env('LABEL_MGR_URL')

def register(cid):
    url = label_mgr_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    return data['kprf']