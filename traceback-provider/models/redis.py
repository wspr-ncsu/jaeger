from redis import Redis
from .helpers import env
from dotenv import load_dotenv
from pygroupsig import groupsig, grpkey, constants

load_dotenv()

connection = None

def connect():
    global connection
    
    connection = Redis(
        host=env("REDIS_HOST"),
        port=env("REDIS_PORT"),
        password=env("REDIS_PASS"),
        db=env("REDIS_DB"),
        decode_responses=True
    )

def find(key):
    return connection.get(key) or None

def save(key, value):
    return connection.set(key, value)

def get_gpk():
    connect()
    gpk = find('GM.gpk')
    
    if not gpk:
        raise Exception('GPK not found in Redis')
    
    groupsig.init(constants.BBS04_CODE, 0)
    return grpkey.grpkey_import(constants.BBS04_CODE, gpk)