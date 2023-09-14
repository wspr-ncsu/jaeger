from . import database as db

signing_key = 'TA.sK'
verify_key = 'TA.vK'

def setup(refresh = False):
    db.connect()
    
    # retrieve setup keys
    sign_key = None if refresh else db.find(signing_key)
    ver_key = None if refresh else db.find(verify_key)
    
    if not sign_key or not ver_key:
        sign_key, ver_key = 1, 2
        db.save(signing_key, sign_key)
        db.save(verify_key, ver_key)
    
    return sign_key, ver_key
 