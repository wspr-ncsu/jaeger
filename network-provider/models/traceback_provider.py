from . import http
from .helpers import env

traceback_base_url = env('TRACEBACK_URL', 'http://localhost:9993')

def submit(labels, cts, sigs, group: dict):
    """Submit a call record to the database"""
    
    calls = []
    
    for index, label in enumerate(labels):
        calls.append({ 'l': label, 'c': cts[index], 's': sigs[index]})
    
    res = http.post(url=f'{traceback_base_url}/submit', data=calls, group=group)
    print(res)
        
    
def traceback(group: dict, labels: list, witneses: list):
    """Trace a given call"""
    records = []
    
    for index, label in enumerate(labels):
        records.append({ 'l': label, 'w': witneses[index] })
    
    res = http.post(url=f'{traceback_base_url}/traceback', data=records, group=group)
    
    return res