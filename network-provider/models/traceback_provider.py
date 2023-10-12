from . import http
from .helpers import env

traceback_base_url = env('TRACEBACK_URL', 'http://localhost:9003')

def submit(labels, cts, sigs):
    """Submit a call record to the database"""
    
    data = { 'batch': [] }
    for index, label in enumerate(labels):
        data['batch'].append({
            'lbl': label,
            'ct': cts[index],
            'sig': sigs[index]
        })
        
    res = http.post(f'{traceback_base_url}/submit', data)
    
    print(res)
        
    
def traceback(cdrs):
    """Trace a given call"""