from .helpers import CDR
from typing import List
from . import label_mgr

MAX_EPOCHS = 60 # Seconds

def trace(cdr: CDR):
    """Trace given call detail records"""
    cdrs = get_range(cdr)
    labels = label_mgr.get_labels(cdrs)
    
        
def get_range(cdr: CDR) -> List[CDR]:
    start_epoch: int = cdr.ts - MAX_EPOCHS
    end_epoch: int = cdr.ts + MAX_EPOCHS
    cdrs = []
    
    for epoch in range(start_epoch, end_epoch):
        cdrs.append(
            CDR(src=cdr.src, dst=cdr.dst, ts=epoch, prev=cdr.prev, curr=cdr.curr, next=cdr.next)
        )
        
    return cdrs