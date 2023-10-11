import numpy as np
from . import oprf
from . import scheme
from . import label_mgr
from . import groupsig
from . import traceback_provider
from .helpers import CDR
from typing import List
from oblivious.ristretto import scalar as Scalar, point as Point

cid = None

def init(id, mem_key, grp_key, vk):
    """Initialize the scheme with the given verification key"""
    global cid
    
    cid = id
    scheme.init(vk)
    groupsig.init(mem_key, grp_key)

def contribute(cdrs: List[CDR]):
    """Contribute a CDR to the database"""
    
    labels = get_labels(cdrs)
    return labels
    ciphertexts = encrypt(cdrs)
    signatures = sign(labels=labels, ciphertexts=ciphertexts)
    traceback_provider.submit(labels, ciphertexts, signatures)
    
def get_labels(cdrs: List[CDR]) -> List[str]:
    """Get the labels for the CDRs by querying the label manager through OPRF"""
    
    xs, masks = mask_labels(cdrs)
    evaluations = label_mgr.evaluate(cid, xs)
    labels = unmask_evaluations(evaluations, masks)
    
    return labels

def mask_labels(cdrs: List[CDR]) -> (List[str], List[Scalar]):
    """Mask the labels using OPRF"""
    
    xs = []
    masks = []
    
    for cdr in cdrs:
        label = f'{cdr.src}|{cdr.dst}|{cdr.ts}'
        s, x = oprf.mask(label) # x is a point, scaler is a scalar
        x = oprf.export_point(x)
        masks.append(s)
        xs.append(x)

    return xs, masks

def unmask_evaluations(evaluations: List[str], masks: List[Scalar]):
    """Unmask the evaluations using OPRF to remove initial masking"""

    for index, evaluation in enumerate(evaluations):
        print(evaluation)
        fx = oprf.import_point(evaluation)
        fx = oprf.unmask(masks[index], fx)
        evaluations[index] = oprf.export_point(fx)
        
    return evaluations
    
def sign(labels, ciphertexts):
    """Sign the ciphertexts and labels"""
    
    signatures = np.empty(len(ciphertexts), dtype=str)
    
    for index, ciphertext in enumerate(ciphertexts):
        signatures[index] = groupsig.sign(labels[index], ciphertext)
        
    return signatures

def encrypt(cdrs):
    """Encrypt the CDRs. We use the witness encryption scheme"""
    cts = np.empty(len(cdrs), dtype=str)
    
    for index, cdr in enumerate(cdrs):
        cts[index] = scheme.encrypt(cdr)
        
    return cts