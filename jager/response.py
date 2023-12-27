from json import dumps
import traceback as ex
from werkzeug.exceptions import HTTPException

OK = 200
CREATED = 201
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

class Panic(HTTPException):
    code = 422
    description = "Unprocessable entity"

    def __init__(self, message, code = 422):
        super().__init__()
        self.description = message
        self.code = code

def res(payload, code):
    return dumps(payload), code

def ok(payload={'res': 'OK'}):
    return res(payload, 200)

def created(payload={'res': 'Created'}):
    return res(payload, 201)

def not_found(payload={'res': 'Cannot find resource'}):
    return res(payload, 404)

def internal_server_error(payload={'res': 'An unexpected error occurred'}):
    return res(payload, 500)

def handle_ex(e):
    if isinstance(e, HTTPException):
        return { 'res': e.description }, e.code
    else:
        print("\n")
        ex.print_exc()
        print("\n")
        
        return internal_server_error()