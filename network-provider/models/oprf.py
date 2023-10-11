from oblivious.ristretto import point, scalar

def mask(msg: str) -> (scalar, point):
    x = point.hash(msg.encode())
    s = scalar.random()
    # return (s, s * x)
    return (s, x) # debug

def unmask(s: scalar, fx: point) -> point:
    return fx / s

def export_point(pt: point) -> str:
    return pt.to_base64()

def import_point(pt: str) -> point:
    return point.from_base64(pt)