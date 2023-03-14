import os
from time import sleep
from json import loads
from redis import Redis
from dotenv import load_dotenv
from flask import Flask, request
from psycopg2 import connect as db_connect
from werkzeug.exceptions import HTTPException

load_dotenv()

def env(envname, default=""):
    value = os.getenv(envname)
    return value or default

class Database:
    def __init__(self) -> None:
        pass
    
    def open_db(self):
        DB_HOST = env("DB_HOST")
        DB_NAME = env("DB_NAME")
        DB_USER = env("DB_USER")
        DB_PASS = env("DB_PASS")
        
        return db_connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        
    def insert_query(self, items):
        query = "INSERT INTO RoutingRecords"
        query += "(call_meta,route_meta)"
        query += " VALUES"

        for item in items:
            item = loads(item)
            cm = item.get('call_meta')
            rm = item.get('route_meta')

            query += f" ('{cm}','{rm}'),"

        # remove trailing comma and add a semicolon
        query = query[:-1] + ";"

        return query
    
    def migrate(self):
        print('Starting Database Migrations')
        opened_database = self.open_db()
        SCHEMA_FILE = os.getcwd() + "/schema.sql"

        with opened_database.cursor() as cursor:
            with open(SCHEMA_FILE, "r") as schema:
                query = schema.read()
                cursor.execute(query)
            opened_database.commit()

        print('Migrations Completed.')
        
    def process_daemon(self):
        batch_size = 1000
        
        # Open redis queue
        queue = Queue()
        counter = 1

        while True:
            counter += 1
            items = queue.retrieve(length=batch_size)
            items_size = len(items)

            # if there's nothing in redis queue sleep for 5 seconds
            if items_size == 0:
                sleep(5)
                continue

            # create a new insert statement and insert into database
            query = self.insert_query(items)

            print(query)

            with self.open_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()

            # if items retrieved was less than the batch size
            # let's slow down the queue
            # if items is x then we will slow down by (1000 - x) / 10 milliseconds
            delay = (batch_size - items_size) / batch_size

            if delay > 0:
                sleep(delay)
        
class Queue:
    def __init__(self):
        self.queue_name = env("DIGEST_QUEUE")
        
        self.connection = Redis(
            host=env("REDIS_HOST"),
            port=env("REDIS_PORT"),
            password=env("REDIS_PASS"),
            db=env("REDIS_DIGEST_DB")
        )

    # Add payload to digest queue
    def enqueue(self, payload):
        self.connection.rpush(self.queue_name, str(payload))

    # Get first N items from digest queue using redis pipelines
    def retrieve(self, length=1000):
        counter = 0

        pipeline = self.connection.pipeline()

        queue_length = self.connection.llen(self.queue_name)
        length = queue_length if length > queue_length else length

        while counter < length:
            pipeline.rpop(self.queue_name)
            counter = counter + 1

        return pipeline.execute()

class Contribution:
    def __init__(self, request):
        self.tbc = request.form.get('tbc')
        self.tfc = request.form.get('tfc')
        self.cci = request.form.get('cci')

    def verify(self):
        if self.tbc == None or self.tfc == None or self.cci == None:
            raise ValidationError("Valid values of tbc, tfc and cci are required")

    def sanitize(self):
        return {
            'tbc': self.tbc,
            'tfc': self.tfc,
            'cci': self.cci
        }

class Tracer:
    def __init__(self, request):
        self.type = request.form.get('type')
        self.tbc = request.form.get('tbc')
        self.tfc = request.form.get('tfc')
        self.cci = request.form.get('cci')

    def verify(self):
        if self.type not in ['forward', 'back', 'lookup']:
            raise ValidationError('Invalid type parameter')
        
        if self.type == 'back' and self.tbc == None:
            raise ValidationError('tbc is required for traceback requests')
        
        if self.type == 'forward' and self.tfc == None:
            raise ValidationError('tfc is required for traceforward requests')
        
        if self.type == 'lookup' and self.tfc == None:
            raise ValidationError('cci is required for full trace requests')

    def compute(self):
        return {
            'tbc': self.tbc,
            'tfc': self.tfc,
            'cci': self.cci,
            'type': self.type
        }
    
class ValidationError(HTTPException):
    code = 422
    description = "Unprocessable entity"

    def __init__(self, message):
        super().__init__()
        self.description = message
        
          
class Server:
    def __init__(self) -> None:
        self.HTTP_OK = 200
        self.HTTP_CREATED = 201
        self.HTTP_NOT_FOUND = 404
        self.HTTP_UNPROCESSABLE = 422
        
        self.queue = Queue()
        
    def create_instance_path(self, app):
        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass
        
    def start_insertion_daemon(self):
        print('Starting insertion daemon...')
        daemon = Thread(target=process_daemon, daemon=True, name='INSERT DIGESTS')
        daemon.start()
        
    def start(self, test_config=None):
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(SECRET_KEY=env("APP_SECRET_KEY"))
        self.create_instance_path(app)

        # start daemon to insert data into db
        self.start_insertion_daemon()

        @app.post('/contribute')
        def contributions():
            contribution = Contribution(request)
            contribution.verify()
            # sanitize and enqueue
            sanitized = contribution.sanitize()
            self.queue.enqueue(sanitized)
            return { "msg": "Record inserted" }, self.HTTP_CREATED


        @app.post('/tracer')
        def trace_query():
            tracer = Tracer(request)
            tracer.verify()
            result = tracer.compute()
            return result, self.HTTP_OK
        
        
        @app.errorhandler(self.HTTP_NOT_FOUND)
        def page_not_found(e):
            return {
                'msg': 'The requested resource could not be found'
            }, self.HTTP_NOT_FOUND
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            if isinstance(e, HTTPException):
                return {
                    'msg': e.description
                }, e.code
            
            return {"msg": e.description }, self.HTTP_NOT_FOUND


        return app

def create_app(test_config=None):
    return Server().start(test_config)

if __name__ == '__main__':
    import sys
    
    if (len(sys.argv) >= 2):
        command = sys.argv[1]
        
        if command == 'migrate':
            Database().migrate()
        else:
            print("Invalid Command")
    else:
        print("NO ARGUMENT PROVIDED")
    