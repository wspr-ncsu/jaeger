from oblivious.ristretto import point, scalar

def keygen():
    return scalar.random()

def eval(sk: scalar, x: point): # sk is a scalar, x is a point
    return sk * x

def export_point(pt: point) -> str:
    return pt.to_base64()

def import_point(pt: str) -> point:
    return point.from_base64(pt)

def import_scalar(s: str) -> scalar:
    return scalar.from_base64(s)

def export_scalar(s: scalar) -> str: 
    return s.to_base64()