from . import http

def submit(labels, cts, sigs):
    """Submit a call record to the database"""
    
    data = { 'batch': [] }
    for index, label in enumerate(labels):
        data['batch'].append({
            'lbl': label,
            'ct': cts[index],
            'sig': sigs[index]
        })
        
    res = http.post('submit', data)
    
    print(res)
        
    
def traceback(labels, cts, sigs):
    """Trace a given call"""