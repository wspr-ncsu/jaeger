from redis import Redis
from rq import Queue
import json
from . import database

queue = Queue(connection=Redis())

def job(payload: str):
    """Job to be run in the background"""
    calls = json.loads(payload)
    records = []
    
    for call in calls:
        if not groupsig_verify(call['s'], f"{call['l']}|{call['c']}"):
            continue
        records.append([call['l'], call['s'], call['c']])
        
    database.insert_records(records)

def submit(request):
    payload = reject_request(request)
    
    if payload == True:
        return
    
    queue.enqueue(job, payload)
    
def traceback(request):
    payload = reject_request(request)
    
    if not payload:
        return []

    labels = json.loads(payload)
    
    return database.get_ciphertexts(labels)

def reject_request(request):
    sig: str = request.headers.get('X-Privytrace').split(' ')[1]
    payload = request.form.get('payload')
    
    if groupsig_verify(sig, payload):
        return payload
    else:
        return True

def groupsig_verify(sig: str, msg):
    return True

def trace_auth_verify(sig: str, msg):
    return True