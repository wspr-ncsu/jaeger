import requests
from .helpers import env
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, constants

grp_sig_base_url = env('GRP_SIG_URL', 'http://localhost:9990')

usk = None
gpk = None

def init(group_signature_keys: dict):
    """Initialize the scheme with the given verification key"""
    global usk, gpk
    usk = group_signature_keys['usk']
    gpk = group_signature_keys['gpk']
    
def sign(msg: bytes) -> str:
    sigma = groupsig.sign(msg, usk, gpk)
    return signature.signature_export(sigma)
    

# post request to registration server
def register(cid: str) -> dict:
    url = grp_sig_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    # initialize the groupsig library otherwise segmentation fault occurs
    groupsig.init(constants.BBS04_CODE, 0)
    usk = memkey.memkey_import(constants.BBS04_CODE, data['usk'])
    gpk = grpkey.grpkey_import(constants.BBS04_CODE, data['gpk'])
    
    return { 'usk': usk, 'gpk': gpk }