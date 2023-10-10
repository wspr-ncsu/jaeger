from . import database as db
from pygroupsig import groupsig, signature, memkey, grpkey, mgrkey, constants

manager_secret = 'GM.sK_G'
group_key = 'GM.vK_G'

def setup(refresh = False):
    db.connect()
    
    # retrieve setup keys
    mgr_key = None if refresh else db.find(manager_secret)
    grp_key = None if refresh else db.find(group_key)
    
    if not mgr_key or not grp_key:
        issuer = groupsig.setup(constants.GL19_CODE)
        
        # Export keys into base64 encoded strings
        mgr_key = mgrkey.mgrkey_export(issuer['mgrkey'])
        grp_key = grpkey.grpkey_export(issuer['grpkey'])
        
        db.save(manager_secret, mgr_key)
        db.save(group_key, grp_key)
    
    return mgr_key, grp_key
    
def register(cid, grp_key, mgr_key, refresh = False):
    db.connect()
    dbkey = f'GM.members.{cid}'
    
    mem_key = None if refresh else db.find(dbkey)
    
    if not mem_key:
        groupsig.init(constants.GL19_CODE, 0)
        
        # Convert base64 encoded key strings into objects
        mgr_key = mgrkey.mgrkey_import(constants.GL19_CODE, mgr_key)
        grp_key = grpkey.grpkey_import(constants.GL19_CODE, grp_key)
        
        msg1 = groupsig.join_mgr(0, mgr_key, grp_key)
        msg2 = groupsig.join_mem(1, grp_key, msgin = msg1)
        mem_key = msg2['memkey']
        
        msg3 = groupsig.join_mgr(2, mgr_key, grp_key, msg2['msgout'])
        msg4 = groupsig.join_mem(3, grp_key, msgin = msg3, memkey = mem_key)
        mem_key = memkey.memkey_export(msg4['memkey'])

        db.save(dbkey, mem_key)
        
    return mem_key
