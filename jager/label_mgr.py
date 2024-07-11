from . import oprf
from . import redis
from typing import List
from .config import LM_BASE_URL, LM_SK
from .helpers import CDR
from . import http


def setup():
    return oprf.export_scalar(oprf.keygen())

def load_sk():
    return oprf.import_scalar(LM_SK)

def server_evaluate(sk: oprf.scalar, x: oprf.point):
    x = oprf.import_point(x)
    fx = oprf.eval(sk, x)
    return oprf.export_point(fx)

def server_batch_evaluation(sk: oprf.scalar, xs: List):
    return [server_evaluate(sk, x) for x in xs]


# Client side functions
# Will be called by client functions

def client_request_labels(group: dict, cdrs: List[CDR], lm_sk: oprf.scalar = None) -> List[str]:
    """Get the labels for the CDRs by querying the label manager through OPRF"""
    
    xs, masks = client_mask_labels(cdrs)
    evaluations = client_evaluate(group=group, xs=xs, lm_sk=lm_sk)
    labels = client_unmask_evaluations(evaluations, masks)
    
    return labels

def client_mask_labels(cdrs: List[CDR]) -> (List[str], List[oprf.scalar]):
    """Mask the labels using OPRF"""
    
    xs = []
    masks = []
    
    for cdr in cdrs:
        s, x = oprf.mask(cdr.get_call_detail()) # x is a point, scaler is a scalar
        x = oprf.export_point(x)
        masks.append(s)
        xs.append(x)

    return xs, masks

def client_unmask_evaluations(evaluations: List[str], masks: List[oprf.scalar]):
    """Unmask the evaluations using OPRF to remove initial masking"""

    for index, evaluation in enumerate(evaluations):
        # print(evaluation)
        fx = oprf.import_point(evaluation)
        fx = oprf.unmask(masks[index], fx)
        evaluations[index] = oprf.export_point(fx)
        
    return evaluations

def client_evaluate(group: dict, xs: List[str], lm_sk: oprf.scalar = None) -> List[oprf.scalar]:
    if lm_sk:
        return server_batch_evaluation(lm_sk, xs=xs)
    else:
        url = LM_BASE_URL + '/evaluate'
        res = http.post(url=url, group=group, data=xs)
        return res