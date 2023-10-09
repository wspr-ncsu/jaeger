from . import database as db
from . import oprf

sk_label = 'LM.sk'

def setup(refresh = False):
    db.connect()
    
    # retrieve setup keys
    kprf = None if refresh else db.find(sk_label)
    
    if not kprf:
        kprf = oprf.keygen()
        db.save(sk_label, oprf.export_sk(kprf))
        return kprf
    
    return oprf.import_sk(kprf)

def evaluate(sk, x):
    x = oprf.import_x(x)
    fx = oprf.eval(sk, x)
    return oprf.export_fx(fx)

def batch_evaluation(sk, xs):
    return [evaluate(sk, x) for x in xs]
 