from . import http
from typing import List
from .config import ITG_BASE_URL
from . import database

def submit(labels, cts, sigs, group: dict, over_http:bool = False):
    """Submit a call record to the database"""
    calls = []
    
    for index, label in enumerate(labels):
        if over_http:
            calls.append({ 'l': label, 'c': cts[index], 's': sigs[index]})
        else:
            calls.append([label, cts[index], sigs[index]])
    
    if over_http:
        http.post(url=f'{ITG_BASE_URL}/submit', data=calls, group=group)
    else:
        database.insert_ct_records(calls)
        
    
def request_a_trace(group: dict, labels: List[str]):
    """Trace a given call"""
    res = http.post(url=f'{ITG_BASE_URL}/traceback', data=labels, group=group)
    return res