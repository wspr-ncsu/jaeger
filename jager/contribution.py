from . import witenc
from . import label_mgr
from . import groupsig
from .helpers import CDR
from typing import List
from . import itg as ITG
from blspy import G1Element
from oblivious.ristretto import scalar as Scalar, point as Point

def contribute(group: dict, tapk: G1Element, cdrs: List[CDR], lm_sk: Scalar = None, over_http: bool = False):
    """Contribute a CDR to the database"""
    
    labels = label_mgr.client_request_labels(group=group, lm_sk=lm_sk, cdrs=cdrs)

    payload = encrypt(tapk=tapk, group=group, cdrs=cdrs, labels=labels)
    
    ITG.submit(group=group, labels=labels, cts=payload['cts'], sigs=payload['sigs'], over_http=over_http)
    

def encrypt(tapk: G1Element, group: dict, cdrs: List[CDR], labels: List[str]) -> dict:
    """Encrypt the CDRs. We use the witness encryption scheme"""
    cts = []
    sigs = []
    
    for index, cdr in enumerate(cdrs):
        label: bytes = bytes(labels[index], 'utf-8')
        msg: bytes = bytes(cdr.get_hops(), 'utf-8')
        
        ct: dict = witenc.client_encrypt(pk=tapk, label=label, cdr=msg)
        ct = witenc.client_export_ct(ct)
        cts.append(ct)
        
        payload = f'{labels[index]}|{ct}'
        sigs.append(groupsig.sign(group=group, msg=payload))
        
    return { 'cts': cts, 'sigs': sigs }