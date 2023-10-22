from . import oprf
from . import scheme
from . import label_mgr
from . import groupsig
from .helpers import CDR
from typing import List
from . import traceback_provider as ITG
from oblivious.ristretto import scalar as Scalar, point as Point
from blspy import G1Element

cid = None

def init(carrier_id: str, group_signature_keys: dict, trace_auth_pub_key: G1Element):
    """Initialize the scheme with the given verification key"""
    global cid
    
    cid = carrier_id
    scheme.init(trace_auth_pub_key=trace_auth_pub_key)
    groupsig.init(group_signature_keys)
    label_mgr.init(carrier_id=carrier_id)

def contribute(cdrs: List[CDR]):
    """Contribute a CDR to the database"""
    
    labels = label_mgr.get_labels(cdrs)
    cts = encrypt(cdrs)
    sigs = sign(labels=labels, cts=cts)
    
    ITG.submit(labels=labels, cts=cts, sigs=sigs)
    
   
def sign(labels, cts):
    """Sign the ciphertexts and labels"""
    
    signatures = []
    
    for index, ct in enumerate(cts):
        msg = bytes(f'{labels[index]}|{ct}', 'utf-8')
        signatures.append(groupsig.sign(msg))
        
    return signatures

def encrypt(cdrs: List[CDR]):
    """Encrypt the CDRs. We use the witness encryption scheme"""
    cts = []
    
    for cdr in cdrs:
        ct: dict = scheme.encrypt(cdr)
        cts.append(scheme.export_ct(ct))
        
    return cts