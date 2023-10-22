from . import oprf
from . import scheme
from . import label_mgr
from . import groupsig
from .helpers import CDR
from typing import List
from . import traceback_provider as ITG
from oblivious.ristretto import scalar as Scalar, point as Point
from blspy import G1Element

def contribute(group: dict, tapk: G1Element, cdrs: List[CDR]):
    """Contribute a CDR to the database"""
    
    labels = label_mgr.get_labels(group, cdrs)

    payload = encrypt(tapk=tapk, group=group, cdrs=cdrs, labels=labels)
    
    ITG.submit(group=group, labels=labels, cts=payload['cts'], sigs=payload['sigs'])
    

def encrypt(tapk: G1Element, group: dict, cdrs: List[CDR], labels: List[str]) -> dict:
    """Encrypt the CDRs. We use the witness encryption scheme"""
    cts = []
    sigs = []
    
    for index, cdr in enumerate(cdrs):
        label: bytes = bytes(labels[index], 'utf-8')
        msg: bytes = bytes(cdr.get_hops(), 'utf-8')
        
        ct: dict = scheme.encrypt(pk=tapk, label=label, cdr=msg)
        cts.append(scheme.export_ct(ct))
        
        payload = bytes(f'{labels[index]}|{ct}', 'utf-8')
        sigs.append(groupsig.sign(group=group, msg=payload))
        
    return { 'cts': cts, 'sigs': sigs }