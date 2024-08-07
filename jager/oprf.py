from oblivious.ristretto import sodium

scalar = sodium.scalar
point = sodium.point

def keygen():
    return scalar.random()

def eval(sk: scalar, x: point): # sk is a scalar, x is a point
    return sk * x

def import_scalar(s: str) -> scalar:
    return scalar.from_base64(s)

def export_scalar(s: scalar) -> str: 
    return s.to_base64()

def mask(msg: str) -> (scalar, point):
    ensure_str(msg, "msg")
    
    x = point.hash(msg.encode())
    s = scalar.random()
    return (s, s * x) # s is a scalar, x is a point

def unmask(s: scalar, pt: point) -> point:
    ensure_scalar(s)
    ensure_point(pt)
    
    return (~s) * pt

def export_point(pt: point) -> str:
    ensure_point(pt)
    
    return pt.to_base64()

def import_point(pt: str) -> point:
    ensure_str(pt)
    
    return point.from_base64(pt)

def ensure_str(s: str, name: str = "s"):
    if not isinstance(s, str):
        raise TypeError(f"{name} must be a string")

def ensure_scalar(s: scalar, name: str = "s"):
    if not isinstance(s, scalar):
        raise TypeError(f"{name} must be a scalar")
    
def ensure_point(pt: point, name: str = "pt"):
    if not isinstance(pt, point):
        raise TypeError(f"{name} must be a point")