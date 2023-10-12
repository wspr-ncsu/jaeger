from . import database as db
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, constants, gml as GML

SCHEME = constants.BBS04_CODE
msk_key = 'GM.msk'
gpk_key = 'GM.gpk'
gml_key = 'GM.gml'

GML_SAVED = False

def setup(refresh = False):
    db.connect()
    
    # retrieve setup keys
    msk_str = None if refresh else db.find(msk_key)
    gpk_str = None if refresh else db.find(gpk_key)
    gml_str = None if refresh else db.find(gml_key)
    
    if not msk_str or not gpk_str or not gml_str:
        bbs04 = groupsig.setup(SCHEME)
        
        gpk = bbs04['grpkey']
        msk = bbs04['mgrkey']
        gml = bbs04['gml']
        
        # Export keys into base64 encoded strings
        msk_str = mgrkey.mgrkey_export(msk)
        gpk_str = grpkey.grpkey_export(gpk)
        
        db.save(msk_key, msk_str)
        db.save(gpk_key, gpk_str)
    else:
        # Convert base64 encoded key strings into objects
        groupsig.init(SCHEME, 0)
        msk = mgrkey.mgrkey_import(SCHEME, msk_str)
        gpk = grpkey.grpkey_import(SCHEME, gpk_str)
        gml = GML.gml_import(SCHEME, gml_str)
    
    return { 'msk': msk, 'gpk': gpk, 'gml': gml }
    
def register(cid, gsign_keys, refresh = False):
    db.connect()
    dbkey = f'GM.members.{cid}'
    
    msk = gsign_keys['msk']
    gpk = gsign_keys['gpk']
    gml = gsign_keys['gml']
    
    usk = None if refresh else db.find(dbkey)
    
    if not usk:
        groupsig.init(SCHEME, 0)
        msg1 = groupsig.join_mgr(0, msk, gpk, gml = gml)
        msg2 = groupsig.join_mem(1, gpk, msgin = msg1)
        usk = msg2['memkey']
        usk = memkey.memkey_export(usk)

        db.save(dbkey, usk)
    
    gpk = grpkey.grpkey_export(gpk)
    
    # hacky way to save gml instead of saving in the setup function
    save_gml(gml)
    
    return { 'usk': usk, 'gpk': gpk }

def save_gml(gml):
    global GML_SAVED
    
    if GML_SAVED:
        return
    
    db.connect()
    saved = db.find(gml_key)
    export_d = GML.gml_export(gml)
    
    if saved != export_d:
        db.save(gml_key, export_d)
        
    GML_SAVED = True