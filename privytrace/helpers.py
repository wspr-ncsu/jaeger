import json
from os import getenv
from .response import Panic

def write_to_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)

def read_from_file(filename):
    with open(filename, "r") as f:
        return f.read()
        
def validate_cid(cid):
    if not cid:
        raise Panic("Missing cid")
    
    cid = int(cid)
    
    if cid < 1 or cid > 7000:
        raise Panic("Unrecognized ID")
    
    return cid

def validate_json_list(payload):
    if not payload:
        raise Panic("Missing payload")
    
    payload = json.loads(payload)
    
    if not isinstance(payload, list):
        raise Panic("xs must be a list")

    return payload

def validate_json(payload):
    if not payload:
        raise Panic("Missing payload")
    
    payload = json.loads(payload)
    
    if not isinstance(payload, dict):
        raise Panic("xs must be a dict")

    return payload