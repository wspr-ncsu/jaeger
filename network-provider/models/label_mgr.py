import requests
from .helpers import env
import json
from typing import List
from .helpers import CDR
from typing import List
from . import oprf
from ...privytrace import http

label_mgr_base_url = env('LABEL_MGR_URL', 'http://localhost:9991')

def get_labels(group: dict, cdrs: List[CDR]) -> List[str]:
    """Get the labels for the CDRs by querying the label manager through OPRF"""
    
    xs, masks = mask_labels(cdrs)
    evaluations = evaluate(group, xs)
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
        # print(evaluation)
        fx = oprf.import_point(evaluation)
        fx = oprf.unmask(masks[index], fx)
        evaluations[index] = oprf.export_point(fx)
        
    return evaluations
 
def evaluate(group: dict, labels: List[str]) -> List[oprf.scalar]:
    url = label_mgr_base_url + '/evaluate'
    data = { 'xs': labels }
    res = http.post(url=url, group=group, data=data)
    # print(res)
    
    return res['fxs']