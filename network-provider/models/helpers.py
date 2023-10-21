from os import getenv
from collections import namedtuple

CDR = namedtuple('CDR', ['src', 'dst', 'ts', 'prev', 'curr', 'next'])

def env(envname, default=""):
    value = getenv(envname)
    return value or default

def not_found():
    return { 'msg': 'The requested resource could not be found' }, 404
        
def toEpoch(date):
    return int(date.timestamp())

