from . import helpers
from . import database as db
from . import http
from pygroupsig import groupsig, signature, memkey, grpkey, constants

gm_base_url = helpers.env('GRP_SIG_URL', 'http://localhost:9990')
    
def sign(group: dict, msg: str) -> str:
    sigma = groupsig.sign(msg, group['usk'], group['gpk'])
    return signature.signature_export(sigma)

def open(group: dict, faulty_set: list):
    """Open a faulty set"""
    http.post(f'{gm_base_url}/open', data=faulty_set, group=group)
    
# post request to registration server
def register(cid: str) -> dict:
    db.connect()
    
    usk = db.find(f'GM.members.{cid}')
    gpk = db.find(f'GM.gpk')
    
    if not usk or not gpk:
        raise Exception("Group Signature Keys not found")
    
    # initialize the groupsig library otherwise segmentation fault occurs
    groupsig.init(constants.BBS04_CODE, 0)
    usk = memkey.memkey_import(constants.BBS04_CODE, usk)
    gpk = grpkey.grpkey_import(constants.BBS04_CODE, gpk)
    
    return { 'usk': usk, 'gpk': gpk }