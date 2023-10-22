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

    payload = encrypt(cdrs=cdrs, labels=labels)
    
    ITG.submit(labels=labels, cts=payload.cts, sigs=payload.sigs)
    

def encrypt(cdrs: List[CDR], labels: List[str]) -> dict:
    """Encrypt the CDRs. We use the witness encryption scheme"""
    cts = []
    sigs = []
    
    for index, cdr in enumerate(cdrs):
        label: bytes = bytes(labels[index], 'utf-8')
        msg: bytes = bytes(cdr.get_hops(), 'utf-8')
        
        ct: dict = scheme.encrypt(label=label, cdr=msg)
        cts.append(scheme.export_ct(ct))
        
        payload = bytes(f'{labels[index]}|{ct}', 'utf-8')
        sigs.append(groupsig.sign(payload))
        
    return { 'cts': cts, 'sigs': sigs }