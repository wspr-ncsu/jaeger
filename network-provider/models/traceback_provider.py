from . import http
from .helpers import env

traceback_base_url = env('TRACEBACK_URL', 'http://localhost:9003')

def submit(labels, cts, sigs):
    """Submit a call record to the database"""
    
    data = { 'calls': [] }
    for index, label in enumerate(labels):
        data['calls'].append([label, cts[index], sigs[index]])
        
    res = http.post(f'{traceback_base_url}/submit', data)
    
    print(res)
        
    
def traceback(cdrs):
    """Trace a given call"""