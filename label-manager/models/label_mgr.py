from . import database as db

kprf_label = 'LM.kPRF'

def setup(refresh = False):
    db.connect()
    
    # retrieve setup keys
    kprf = None if refresh else db.find(kprf_label)
    
    if not kprf:
        kprf = 1
        db.save(kprf_label, kprf)
    
    return kprf
 