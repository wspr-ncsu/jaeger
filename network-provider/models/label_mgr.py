import requests
from .helpers import env
import json
from typing import List
from .helpers import CDR
from typing import List
from . import oprf

label_mgr_base_url = env('LABEL_MGR_URL', 'http://localhost:9002')
cid = None

def init(carrier_id):
    global cid
    cid = carrier_id

def get_labels(cdrs: List[CDR]) -> List[str]:
    """Get the labels for the CDRs by querying the label manager through OPRF"""
    
    xs, masks = mask_labels(cdrs)
    evaluations = evaluate(cid, xs)
    labels = unmask_evaluations(evaluations, masks)
    
    return labels

def mask_labels(cdrs: List[CDR]) -> (List[str], List[oprf.scalar]):
    """Mask the labels using OPRF"""
    
    xs = []
    masks = []
    
    for cdr in cdrs:
        s, x = oprf.mask(cdr.get_call_detail()) # x is a point, scaler is a scalar
        x = oprf.export_point(x)
        masks.append(s)
        xs.append(x)

    return xs, masks

def unmask_evaluations(evaluations: List[str], masks: List[oprf.scalar]):
    """Unmask the evaluations using OPRF to remove initial masking"""

    for index, evaluation in enumerate(evaluations):
        print(evaluation)
        fx = oprf.import_point(evaluation)
        fx = oprf.unmask(masks[index], fx)
        evaluations[index] = oprf.export_point(fx)
        
    return evaluations
 

def evaluate(cid: str, labels: List[str]) -> List[oprf.scalar]:
    if not cid:
        raise Exception('Carrier ID not set')
    
    url = label_mgr_base_url + '/evaluate'
    data = { 'xs': json.dumps(labels), 'cid': cid }
    res = requests.post(url, data=data)
    print(data)
    print(res.text)
    res.raise_for_status()
    return res.json()['fxs']