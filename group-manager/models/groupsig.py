from . import helpers
from . import database as db
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, constants, gml as GML

SCHEME = constants.BBS04_CODE
msk_file = '.keys/groupsig/.msk'
gpk_file = '.keys/groupsig/.gpk'
gml_file = '.keys/groupsig/.gml'

GML_SAVED = False

def setup(refresh = False):
    # retrieve setup keys
    msk_str = None if refresh else helpers.read_from_file(msk_file)
    gpk_str = None if refresh else helpers.read_from_file(gpk_file)
    gml_str = None if refresh else helpers.read_from_file(gml_file)
    
    if not msk_str or not gpk_str or not gml_str:
        bbs04 = groupsig.setup(SCHEME)
        
        gpk = bbs04['grpkey']
        msk = bbs04['mgrkey']
        gml = bbs04['gml']
        
        # Export keys into base64 encoded strings
        msk_str = mgrkey.mgrkey_export(msk)
        gpk_str = grpkey.grpkey_export(gpk)
        
        
        helpers.write_to_file(msk_file, msk_str)
        helpers.write_to_file(gpk_file, gpk_str)
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
    
    saved = helpers.read_from_file(gml_file)
    export_d = GML.gml_export(gml)
    
    if saved != export_d:
        helpers.write_to_file(gml_file, export_d)
        
    GML_SAVED = True