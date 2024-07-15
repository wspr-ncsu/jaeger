from . import redis
from . import helpers
from . import config
from .response import Panic
from . import http
from . import redis
from . import database
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, gml as GML

SCHEME = config.GS_Scheme

def setup():
    bbs04 = groupsig.setup(SCHEME)
    mkeys = mgr_generate_member_keys(bbs04['mgrkey'], bbs04['grpkey'], bbs04['gml'])
    msk = mgrkey.mgrkey_export(bbs04['mgrkey'])
    gpk = grpkey.grpkey_export(bbs04['grpkey'])
    gml = GML.gml_export(bbs04['gml'])
    
    return msk, gpk, gml

def mgr_import_keys():
    groupsig.init(SCHEME, 0)
    return {
        'msk': mgrkey.mgrkey_import(SCHEME, config.GM_MSK),
        'gpk': grpkey.grpkey_import(SCHEME, config.GM_GPK),
        'gml': GML.gml_import(SCHEME, config.GM_GML)
    }
        
def mgr_register_carrier(cid, gsign_keys):
    usk = mgr_generate_member_keys(gsign_keys['msk'], gsign_keys['gpk'], gsign_keys['gml'])
    database.register_carrier(cid, f'carrier-{cid}', usk)
    return usk

def mgr_generate_member_keys(msk, gpk, gml):
    groupsig.init(SCHEME, 0)
    if (type(msk) == str):
        msk = mgrkey.mgrkey_import(SCHEME, msk)
    if (type(gpk) == str):
        gpk = grpkey.grpkey_import(SCHEME, gpk)
    if (type(gml) == str):
        gml = GML.gml_import(SCHEME, gml)
        
    msg1 = groupsig.join_mgr(0, msk, gpk, gml=gml)
    msg2 = groupsig.join_mem(1, gpk, msgin = msg1)
    usk = msg2['memkey']
    return memkey.memkey_export(usk)
    
def mgr_validate_request(request, gpk):
    sig: str = request.headers.get(config.SIG_HEADER).split(' ')[1]
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
    
    if not config.GM_GPK:
        raise Exception('GPK not set')
    
    return grpkey.grpkey_import(config.GS_Scheme, config.GM_GPK)

def validate_signature_from_request(request, gpk):
    sig: str = request.headers.get(config.SIG_HEADER).split(' ')[1]
    msg: str = request.form.get('payload')
    
    sig = signature.signature_import(SCHEME, sig)
    
    if not groupsig.verify(sig, msg, gpk):
        raise Panic("Bad Request")
    
def sign(group: dict, msg: str) -> str:
    sigma = groupsig.sign(msg, group['usk'], group['gpk'])
    return signature.signature_export(sigma)

def client_open(group: dict, faulty_set: list):
    """Open a faulty set"""
    url = f'{config.GM_HOST}:{config.GM_PORT}/open'
    http.post(url=url, data=faulty_set, group=group)
    
def client_register(cid: str) -> dict:
    carrier = database.get_carrier(cid)
    if not carrier:
        raise Panic("Carrier not found")
    
    groupsig.init(SCHEME, 0)
    usk = memkey.memkey_import(SCHEME, carrier.gsk)
    gpk = grpkey.grpkey_import(SCHEME, config.GM_GPK)
    
    return { 'usk': usk, 'gpk': gpk }

def client_import_usk(usk: str) -> dict:
    groupsig.init(SCHEME, 0)
    return memkey.memkey_import(SCHEME, usk)