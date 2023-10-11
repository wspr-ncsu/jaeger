import requests
from .helpers import env
import json
from typing import List
from oblivious.ristretto import scalar as Scalar

label_mgr_base_url = env('LABEL_MGR_URL', 'http://localhost:9002')

def evaluate(cid: str, labels: List[str]) -> List[Scalar]:
    url = label_mgr_base_url + '/evaluate'
    data = { 'xs': json.dumps(labels), 'cid': cid }
    res = requests.post(url, data=data)
    print(data)
    print(res.text)
    res.raise_for_status()
    return res.json()