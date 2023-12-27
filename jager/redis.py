from redis import Redis
from . import config

def connect():
    return Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASS,
        db=config.REDIS_DB,
        decode_responses=True
    )

def find(key: str, dtype = str):
    data = connect().get(key) or None
    if dtype == int:
        return int(data)
    return data

def save(key: str, value: str):
    if type(value) != str:
        raise TypeError("Value must be a string")
    
    return connect().set(key, value)