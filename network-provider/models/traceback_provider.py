from . import http
from .helpers import env

traceback_base_url = env('TRACEBACK_URL', 'http://localhost:9993')

def submit(labels, cts, sigs):
    """Submit a call record to the database"""
    
    calls = []
    
    for index, label in enumerate(labels):
        calls.append({ 'l': label, 'c': cts[index], 's': sigs[index]})
    
    res = http.post(f'{traceback_base_url}/submit', calls)
    
    
    print(res)
        
    
def traceback(cdrs):
    """Trace a given call"""