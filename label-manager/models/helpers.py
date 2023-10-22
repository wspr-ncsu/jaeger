import json
from os import getenv
import traceback as ex
from werkzeug.exceptions import HTTPException

def env(envname, default=""):
    value = getenv(envname)
    return value or default

def not_found():
    return { 'msg': 'The requested resource could not be found' }, 404

def handle_ex(e):
    if isinstance(e, HTTPException):
        return { 'msg': e.description }, e.code
    else:
        print("\n")
        ex.print_exc()
        print("\n")
        
        return {
            'msg': 'An unexpected error occurred'
        }, 500

def validate_cid(cid):
    if not cid:
        raise Panic("Missing cid")
    
    cid = int(cid)
    
    if cid < 1 or cid > 7000:
        raise Panic("Unrecognized ID")
    
    return cid

def validate_xs(payload):
    if not payload:
        raise Panic("Missing payload")
    
    xs = json.loads(payload)['xs']
    
    if not isinstance(xs, list):
        raise Panic("xs must be a list")

    return xs

class Panic(HTTPException):
    code = 422
    description = "Unprocessable entity"

    def __init__(self, message, code = 422):
        super().__init__()
        self.description = message
        self.code = code