import requests
from .helpers import env
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, constants

grp_sig_base_url = env('GRP_SIG_URL', 'http://localhost:9000')

usk = None
gpk = None

def init(gsign_keys):
    """Initialize the scheme with the given verification key"""
    global usk, gpk
    usk = gsign_keys['usk']
    gpk = gsign_keys['gpk']
    
def sign(label: str, ct: str):
    msg = f'{label}|{ct}'.encode()
    sigma = groupsig.sign(msg, usk, gpk)
    return signature.signature_export(sigma)
    

# post request to registration server
def register(cid):
    url = grp_sig_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    # initialize the groupsig library otherwise segmentation fault occurs
    groupsig.init(constants.GL19_CODE, 0)
    usk = memkey.memkey_import(constants.BBS04_CODE, data['usk'])
    gpk = grpkey.grpkey_import(constants.BBS04_CODE, data['gpk'])
    
    return { 'usk': usk, 'gpk': gpk }