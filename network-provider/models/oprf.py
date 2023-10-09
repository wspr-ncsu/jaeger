from oblivious.ristretto import point, scalar

def msg_to_x(msg):
    return point.hash(msg.encode())

def export_x(x):
    return x.to_base64()

def import_x(x):
    return point.from_base64(x)

def export_fx(fx):
    return fx.to_base64()

def import_fx(fx):
    return scalar.from_base64(fx)