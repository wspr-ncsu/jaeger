from . import redis
from . import helpers
from . import config
from .response import Panic
from . import http
from . import redis
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, gml as GML

SCHEME = config.GS_Scheme

def setup():
    bbs04 = groupsig.setup(SCHEME)
    msk = mgrkey.mgrkey_export(bbs04['mgrkey'])
    gpk = grpkey.grpkey_export(bbs04['grpkey'])
    gml = GML.gml_export(bbs04['gml'])
    
    return msk, gpk, gml

def mgr_register_all(gsign_keys, refresh = False):
    for cid in range(7000):
        mgr_register_carrier(cid, gsign_keys, refresh)
        
    mgr_save_gml(gsign_keys['gml'])
    
def mgr_register_carrier(cid, gsign_keys, refresh = False):
    redis.connect()
    dbkey = f'GM.members.{cid}'
    
    msk = gsign_keys['msk']
    gpk = gsign_keys['gpk']
    gml = gsign_keys['gml']
    
    usk = None if refresh else redis.find(dbkey)
    
    if not usk:
        groupsig.init(SCHEME, 0)
        msg1 = groupsig.join_mgr(0, msk, gpk, gml = gml)
        msg2 = groupsig.join_mem(1, gpk, msgin = msg1)
        usk = msg2['memkey']
        usk = memkey.memkey_export(usk)

        redis.save(dbkey, usk)
    
    gpk = grpkey.grpkey_export(gpk)
    
    return { 'usk': usk, 'gpk': gpk }

def mgr_save_gml(gml):
    redis.connect()
    saved = redis.find(gml_key)
    export_d = GML.gml_export(gml)
    
    if saved != export_d:
        redis.save(gml_key, export_d)
        
def mgr_validate_request(request, gpk):
    sig: str = request.headers.get('X-jager').split(' ')[1]
    msg: str = request.form.get('payload')
    
    sig = signature.signature_import(SCHEME, sig)
    
    if not groupsig.verify(sig, msg, gpk):
        raise helpers.Panic('Bad Request')
    
def mgr_open_sigs(records, gsign_keys):
    groupsig.init(SCHEME, 0)
    results = []
    
    for record in records:
        try:
            sig = signature.signature_import(SCHEME, record['sig'])
            opened = groupsig.open(sig, gsign_keys['msk'], gsign_keys['gpk'], gsign_keys['gml'])
        except:
            pass
        
def get_gpk():
    groupsig.init(config.GS_Scheme, 0)
    gpk = redis.find(config.GS_gpk_key)
    
    if not gpk:
        raise Exception('GPK not found in Redis')
    
    gpk = grpkey.grpkey_import(config.GS_Scheme, gpk)
    
    return gpk

def validate_signature_from_request(request, gpk):
    sig: str = request.headers.get('X-jager').split(' ')[1]
    msg: str = request.form.get('payload')
    
    sig = signature.signature_import(SCHEME, sig)
    
    if not groupsig.verify(sig, msg, gpk):
        raise Panic("Bad Request")
    
def sign(group: dict, msg: str) -> str:
    sigma = groupsig.sign(msg, group['usk'], group['gpk'])
    return signature.signature_export(sigma)

def client_open(group: dict, faulty_set: list):
    """Open a faulty set"""
    http.post(f'{config.GM_BASE_URL}/open', data=faulty_set, group=group)
    
def client_register(cid: str) -> dict:
    usk = redis.find(f'GM.members.{cid}')
    gpk = redis.find(config.GS_gpk_key)
    
    if not usk or not gpk:
        raise Exception(f"Group Signature Keys not found for carrier: {cid}")
    
    # initialize the groupsig library otherwise segmentation fault occurs
    groupsig.init(SCHEME, 0)
    usk = memkey.memkey_import(SCHEME, usk)
    gpk = grpkey.grpkey_import(SCHEME, gpk)
    
    return { 'usk': usk, 'gpk': gpk }