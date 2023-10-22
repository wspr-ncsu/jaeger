from redis import Redis
from rq import Queue
from . import helpers
from . import groupsig
import json
from . import database

queue = Queue(connection=Redis())

def job(payload: str):
    """Job to be run in the background"""
    calls = json.loads(payload)
    records = []
    
    for call in calls:
        if not groupsig.verify(call['s'], f"{call['l']}|{call['c']}"):
            continue
        records.append([call['l'], call['s'], call['c']])
        
    database.insert_records(records)

def submit(request):
    payload = reject_request(request)
    
    if payload == True:
        return
    
    queue.enqueue(job, payload)
    
def trace(request):
    payload = reject_request(request)
    
    if not payload:
        return
    
    # TODO: Implement tracing

def reject_request(request):
    sig: str = request.headers.get('X-Privytrace').split(' ')[1]
    payload = request.form.get('payload')
    
    if groupsig.verify(sig, payload):
        return payload
    else:
        return True
