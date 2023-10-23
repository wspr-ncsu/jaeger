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
        
        witneses = trace_auth.authorize(group=group, labels=labels)
        
        records = traceback_provider.query_trace(group=group, labels=labels)
        
        dec_cdrs = decrypt_records(records=records, witneses=witneses)
    
        faulty_set = get_faulty_set(records, dec_cdrs)
        
        if faulty_set:
            groupsig.open(group=group, faulty_set=faulty_set)
            
        return link_cdrs(dec_cdrs['msgs'])
    
        
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

def decrypt_records(records: List[dict], witneses: List[str]):
    """Decrypt a list of records"""
    msgs = {}
    no_witness = []
    
    for label in records:
        if label not in witneses:
            no_witness.append(label)
            continue
        
        sig: G2Element = scheme.import_sig(witneses[label])
        
        for record in records[label]:
            ct: dict = scheme.import_ct(record['ct'])
            
            if label not in msgs:
                msgs[label] = []
                
            msgs[label].append(scheme.decrypt(sig=sig, ct=ct))
        
    return { 'msgs': msgs, 'no_witness': no_witness }

def get_faulty_set(records, dec_cdrs):
    return []

def link_cdrs(cdrs: dict):
    """Link a list of decrypted cdrs"""
    msgs = []
    
    for label in cdrs:
        msgs += cdrs[label]
    
    origin, transit, terminal = parse_cdrs(msgs)
    sub_paths = find_subpath(origin, transit)
    
    sub_paths.insert(0, origin['id'])
    print('Linked CDRs \n', ' --> '.join(sub_paths))
    
    if len(sub_paths) < len(msgs):
        fragmentation_fault(msgs=msgs)
        
    return msgs
    
def fragmentation_fault(msgs):
    print('\nFragmentation detected.')
    print('CDRs are fragmented into multiple paths.')
    
    for msg in msgs:
        prev, curr, next = msg.split('|')
        print(f'{curr} --> {next}')
        
    print('\n')
    
def find_subpath(_from, transit):
    path = []
    
    if _from == None:
        return path
    
    next = _from['next']
    
    while next != None:
        path.append(next)
        
        if next in transit:
            next = transit[next]['next']
        else:
            next = None
            
    return path
                
def parse_cdrs(msgs: list):
    transit = {}
    origin = None
    terminal = None
    
    for msg in msgs:
        prev, curr, next = msg.split('|')
        
        record = { 
            'prev': prev if prev.lower() != 'none' else None, 
            'id': curr, 
            'next': next if next.lower() != 'none' else None
        }
        
        if record['prev'] == None:
            origin = record
        elif record['next'] == None:
            terminal = record
        else:
            transit[curr] = record
        
    return origin, transit, terminal