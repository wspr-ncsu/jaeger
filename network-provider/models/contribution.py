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

def init(id: str, gsign_keys: dict, pk: G1Element):
    """Initialize the scheme with the given verification key"""
    global cid
    
    cid = id
    scheme.init(pk=pk)
    groupsig.init(gsign_keys)

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
        msg = f'{labels[index]}|{ct}'.encode()
        signatures.append(groupsig.sign(msg))
        
    return signatures

def encrypt(cdrs):
    """Encrypt the CDRs. We use the witness encryption scheme"""
    cts = []
    
    for cdr in cdrs:
        cts.append(scheme.encrypt(cdr))
        
    return cts