import numpy as np
from . import oprf
from . import scheme
from . import label_mgr
from . import groupsig
from . import traceback_provider

def init(vk, mem_key, grp_key):
    """Initialize the scheme with the given verification key"""
    scheme.init(vk)
    groupsig.init(mem_key, grp_key)

def contribute(cdrs):
    """Contribute a CDR to the database"""
    labels = get_labels(cdrs)
    ciphertexts = encrypt(cdrs)
    signatures = sign(labels=labels, ciphertexts=ciphertexts)
    traceback_provider.submit(labels, ciphertexts, signatures)
    
def sign(labels, ciphertexts):
    """Sign the ciphertexts and labels"""
    signatures = np.zeros(len(ciphertexts), dtype=str)
    
    for index, ciphertext in enumerate(ciphertexts):
        signatures[index] = groupsig.sign(labels[index], ciphertext)
        
    return signatures

def encrypt(labels, cdrs):
    """Encrypt the CDRs. We use the witness encryption scheme"""
    cts = np.zeros(len(cdrs), dtype=str)
    
    for index, cdr in enumerate(cdrs):
        cts[index] = scheme.encrypt(cdr)
        
    return cts

def get_labels(cdrs):
    """Get the labels for the CDRs by querying the label manager through OPRF"""
    xs, masks = mask_labels(cdrs)
    evaluations = label_mgr.evaluate(xs)
    labels = unmask_evaluations(evaluations, masks)
    
    return labels

def mask_labels(cdrs):
    """Mask the labels using OPRF"""
    labels = np.zeros(len(cdrs))
    masks = np.zeros(len(cdrs))
    
    for index, cdr in enumerate(cdrs):
        label = f'{cdr.src}|{cdr.dst}|{cdr.ts}'
        
        x = oprf.msg_to_x(label)
        (masked_x, scaler) = oprf.mask_x(x)
        masked_x = oprf.export_x(masked_x)
        
        labels[index] = masked_x
        masks[index] = scaler

    return labels, masks

def unmask_evaluations(evaluations, masks):
    """Unmask the evaluations using OPRF to remove initial masking"""
    for index, evaluation in enumerate(evaluations):
        evaluations[index] = oprf.unmask_fx(evaluation, masks[index])
        
    return evaluations