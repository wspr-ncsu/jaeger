from .helpers import CDR
from typing import List
from . import label_mgr
from . import groupsig
from . import trace_auth
from . import traceback_provider
from blspy import G1Element, G2Element
from . import scheme

MAX_EPOCHS = 60 # Seconds

def trace(group: dict, tapk: G1Element, cdrs: List[CDR]):
    """Trace given call detail records"""
    for cdr in cdrs:
        cdr_set = get_range(cdr)
        labels = label_mgr.get_labels(group, cdr_set)
        sigs = sign_labels(group, labels)
        
        witneses = trace_auth.authorize(group=group, labels=labels, sigs=sigs)
        records = traceback_provider.traceback(group=group, labels=labels, witneses=witneses)
        dec_cdrs = decrypt_records(witneses=witneses, records=records)
        
        faulty_set = get_faulty_set(records, dec_cdrs)
        
        if faulty_set:
            groupsig.open(group=group, faulty_set=faulty_set)
            
        return link_cdrs(dec_cdrs)
    
        
def get_range(cdr: CDR) -> List[CDR]:
    start_epoch: int = cdr.ts - MAX_EPOCHS
    end_epoch: int = cdr.ts + MAX_EPOCHS
    cdrs = []
    
    for epoch in range(start_epoch, end_epoch):
        cdrs.append(
            CDR(src=cdr.src, dst=cdr.dst, ts=epoch, prev=cdr.prev, curr=cdr.curr, next=cdr.next)
        )
        
    return cdrs

def sign_labels(group: dict, labels: List[str]) -> List[str]:
    sigs = []
    
    for label in labels:
        sigs.append(groupsig.sign(group, label.encode()))
        
    return sigs

def decrypt_records(witneses: List[str], records: List[dict]):
    """Decrypt a list of records"""
    msgs = []
    
    for index, record in enumerate(records):
        sig: G2Element = scheme.import_sig(witneses[index])
        ct: dict = scheme.import_ct(record['ct'])
        msg = scheme.decrypt(sig=sig, ct=ct) 
        msgs.append(msg)
        
    return records

def get_faulty_set(dec_cdrs):
    return []

def link_cdrs(dec_cdrs):
    return []