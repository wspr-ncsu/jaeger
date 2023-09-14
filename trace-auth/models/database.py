from redis import Redis
from .helpers import env

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