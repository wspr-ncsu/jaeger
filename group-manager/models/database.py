from redis import Redis
from .helpers import env
from json import loads, dumps

connection = None
queue_name = None
queue_conn = None
batch_size = None

def init_db():
    global connection, queue_name, queue_conn, batch_size
    
    queue_name = env('QUEUE', 'default')
    batch_size = env('BATCH_SIZE', 1000)
    queue_conn = env('QUEUE_CONNECTION', 'redis')
    
    connection = Redis(
        host=env("REDIS_HOST"),
        port=env("REDIS_PORT"),
        password=env("REDIS_PASS"),
        db=env("REDIS_DB")
    )
    
def migrate_db():
    pass
    
def enqueue(payload, queue = None):
    global connection
    queue = queue or queue_name
    connection.rpush(queue, dumps(payload))

def retrieve(queue=None, length=1000):
    counter = 0
    queue = queue or queue_name
    pipeline = connection.pipeline()
    queue_length = connection.llen(queue_name)
    length = queue_length if length > queue_length else length

    while counter < length:
        pipeline.rpop(queue_name)
        counter = counter + 1

    return pipeline.execute()