from . import http
from typing import List
from .config import ITG_BASE_URL

def submit(labels, cts, sigs, group: dict):
    """Submit a call record to the database"""
    
    calls = []
    
    for index, label in enumerate(labels):
        calls.append({ 'l': label, 'c': cts[index], 's': sigs[index]})
    
    res = http.post(url=f'{ITG_BASE_URL}/submit', data=calls, group=group)
        
    
def request_a_trace(group: dict, labels: List[str]):
    """Trace a given call"""
    res = http.post(url=f'{ITG_BASE_URL}/traceback', data=labels, group=group)
    return res