from os import getenv
import traceback as ex
from werkzeug.exceptions import HTTPException
from collections import namedtuple

CDR = namedtuple('CDR', ['src', 'dst', 'ts', 'prev', 'curr', 'next'])

def env(envname, default=""):
    value = getenv(envname)
    return value or default

def not_found():
    return { 'msg': 'The requested resource could not be found' }, 404

def handle_ex(e):
    if isinstance(e, HTTPException):
        return e
    else:
        print("\n")
        ex.print_exc()
        print("\n")
        
        return {
            'msg': 'An unexpected error occurred'
        }, 500
    
class Panic(HTTPException):
    code = 422
    description = "Unprocessable entity"

    def __init__(self, message, code = 422):
        super().__init__()
        self.description = message
        self.code = code
        
        
def toEpoch(date):
    return int(date.timestamp())

