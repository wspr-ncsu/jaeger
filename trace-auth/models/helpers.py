import json
from os import getenv
import traceback as ex
from collections import namedtuple
from werkzeug.exceptions import HTTPException
from pygroupsig import groupsig, signature, constants, grpkey
from . import database

Keys = namedtuple('Keys', ['sk', 'pk'])

def env(envname, default=""):
    value = getenv(envname)
    return value or default

def not_found():
    return { 'msg': 'The requested resource could not be found' }, 404

def handle_ex(e):
    if isinstance(e, HTTPException):
        return e
    else:
        print("\n")
        ex.print_exc()
        print("\n")
        
        return {
            'msg': 'An unexpected error occurred'
        }, 500
    
class Panic(HTTPException):
    code = 422
    description = "Unprocessable entity"

    def __init__(self, message, code = 422):
        super().__init__()
        self.description = message
        self.code = code
        

def validate_cid(cid):
    if not cid:
        raise Panic("Missing cid")
    
    cid = int(cid)
    
    if cid < 1 or cid > 7000:
        raise Panic("Unrecognized ID")
    
    return cid

def validate_labels(labels):
    labels = json.loads(labels)
    
    if not len(labels):
        raise Panic("Missing labels")
    
    return labels

def get_gpk():
    database.connect()
    groupsig.init(constants.BBS04_CODE, 0)
    gpk = database.find('GM.gpk')
    
    if not gpk:
        raise Exception('GPK not found in Redis')
    
    gpk = grpkey.grpkey_import(constants.BBS04_CODE, gpk)
    
    return gpk

def validate_signature(request, gpk):
    sig: str = request.headers.get('X-Privytrace').split(' ')[1]
    msg: str = request.form.get('payload')
    
    sig = signature.signature_import(constants.BBS04_CODE, sig)
    
    if not groupsig.verify(sig, msg, gpk):
        raise Panic("Bad Request")