from json import dumps

def res(payload, code):
    return dumps(payload), code

def ok(payload={'msg': 'OK'}):
    return res(payload, 200)

def not_found(payload={'msg': 'Cannot find resource'}):
    return res(payload, 404)

def internal_server_error(payload={'msg': 'An unexpected error occurred'}):
    return res(payload, 500)