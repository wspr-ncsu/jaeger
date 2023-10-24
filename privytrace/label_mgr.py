from . import oprf
from . import redis
from typing import List

sk_label = 'LM.sk'

def setup(refresh = False):
    # retrieve setup keys
    sk = None if refresh else redis.find(sk_label)
    
    if not sk:
        sk = oprf.keygen()
        redis.save(sk_label, oprf.export_scalar(sk))
        return sk
    
    return oprf.import_scalar(sk)

def evaluate(sk: oprf.scalar, x: oprf.point):
    x = oprf.import_point(x)
    fx = oprf.eval(sk, x)
    return oprf.export_point(fx)

def batch_evaluation(sk: oprf.scalar, xs: List):
    return [evaluate(sk, x) for x in xs]
 