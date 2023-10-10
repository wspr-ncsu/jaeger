import requests
from .helpers import env
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, constants

grp_sig_base_url = env('GRP_SIG_URL')

mK = None
gK = None

def init(mem_key, grp_key):
    """Initialize the scheme with the given verification key"""
    mK = mem_key
    gK = grp_key
    
def sign(label, ciphertext):
    pass

# post request to registration server
def register(cid):
    mem_key, grp_key = None, None
    
    url = grp_sig_base_url + '/register'
    res = requests.post(url, data={'cid': cid})
    res.raise_for_status()
    data = res.json()
    
    # initialize the groupsig library otherwise segmentation fault occurs
    groupsig.init(constants.GL19_CODE, 0)
    mem_key, grp_key = data['mem_key'], data['grp_key']
    
    # import the keys from base64 to pygroupsig objects
    mem_key = memkey.memkey_import(constants.GL19_CODE, mem_key)
    grp_key = grpkey.grpkey_import(constants.GL19_CODE, grp_key)
    
    return mem_key, grp_key