from oblivious.ristretto import point, scalar

def keygen():
    return scalar.random()

def eval(sk: scalar, x: point):
    return sk * x

def import_x(pt):
    return point.from_base64(pt)

def export_sk(sk):
    return sk.to_base64()

def import_sk(sk):
    return scalar.from_base64(sk)

def export_fx(fx):
    return fx.to_base64()