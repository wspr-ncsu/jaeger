from redis import Redis
from rq import Queue
import json
from . import database
from pygroupsig import groupsig, signature, constants, grpkey

queue = Queue(connection=Redis())

def job(payload: str, gpk_str: str):
    """Job to be run in the background"""
    calls = json.loads(payload)
    records = []
    
    # Initialize the group signature module
    groupsig.init(constants.BBS04_CODE, 0)
    # Import the group public key
    gpk = grpkey.grpkey_import(constants.BBS04_CODE, gpk_str)
    
    for call in calls:
        if not groupsig_verify(sig=call['s'], msg=f"{call['l']}|{call['c']}", gpk=gpk):
            continue
        
        records.append([call['l'], call['s'], call['c']])
        
    database.insert_records(records)

def submit(request, gpk):
    payload = reject_request(request=request, gpk=gpk)
    
    if payload == True:
        return
    
    gpk_ex = grpkey.grpkey_export(gpk)
    queue.enqueue(job, payload, gpk_ex)
    
def traceback(request, gpk):
    payload = reject_request(request=request, gpk=gpk)
    
    if not payload:
        return []

    labels = json.loads(payload)
    
    return database.get_ciphertexts(labels)

def reject_request(request, gpk):
    sig: str = request.headers.get('X-Privytrace').split(' ')[1]
    payload: str = request.form.get('payload')
    
    if groupsig_verify(sig=sig, msg=payload, gpk=gpk):
        return payload
    else:
        return True

def groupsig_verify(sig: str, msg: str, gpk):
    sig = signature.signature_import(constants.BBS04_CODE, sig)
    return groupsig.verify(sig, msg, gpk)
