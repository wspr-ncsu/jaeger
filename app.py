import os
from time import sleep
from json import loads, dumps
from redis import Redis
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request
from psycopg2 import connect as db_connect
from werkzeug.exceptions import HTTPException

load_dotenv()

def env(envname, default=""):
    """
    Gets environment variable from .env
    
    Args: 
        envname: Environment variable name
        default: The default value for this variable if not set
        
    Returns:
        A string of value of variable from .env
    """
    value = os.getenv(envname)
    return value or default


class Database:
    def __init__(self) -> None:
        pass
    
    
    def open_db(self):
        """
        Establishes a database connection
        """
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
        
        
    def create_insert_query_string(self, items):
        """
        Creates insert statement query string with multiple values
        
        Args: 
            items: Contributed records to be processed. Each of this record has tbc, tfc and cci
            
        Returns:
            A string of insert statement with multiple values
        """
        query = "INSERT INTO cdrs"
        query += "(cci,tbc,tfc)"
        query += " VALUES"

        for item in items:
            item = loads(item)
            cci = item.get('cci')
            tbc = item.get('tbc')
            tfc = item.get('tfc')

            query += f" ('{cci}', '{tbc}','{tfc}'),"

        # remove trailing comma and add a semicolon
        query = query[:-1] + ";"

        return query
    
    
    def migrate(self):
        """
        Drops and recreates the database tables and their integrity constraints
        """
        print('Starting Database Migrations')
        opened_database = self.open_db()
        SCHEMA_FILE = os.getcwd() + "/schema.sql"

        with opened_database.cursor() as cursor:
            with open(SCHEMA_FILE, "r") as schema:
                query = schema.read()
                cursor.execute(query)
            opened_database.commit()

        print('Migrations Completed.')
        
        
class Queue:
    def __init__(self):
        self.queue_name = env("QUEUE")
        self.batch_size = 1000
        
        self.connection = Redis(
            host=env("REDIS_HOST"),
            port=env("REDIS_PORT"),
            password=env("REDIS_PASS"),
            db=env("REDIS_DB")
        )


    def enqueue(self, payload):
        """
        Adds item to the head of queue
        
        Args: 
            payload: data to be added to the queue
        """
        self.connection.rpush(self.queue_name, dumps(payload))


    def retrieve(self, length=1000):
        """
        Get the first N items from the rear of the queue
        
        Args: 
            length: number of items to be retrieved from the queue
            
        Returns:
            Data items from the queue
        """
        counter = 0
        pipeline = self.connection.pipeline()
        queue_length = self.connection.llen(self.queue_name)
        length = queue_length if length > queue_length else length

        while counter < length:
            pipeline.rpop(self.queue_name)
            counter = counter + 1

        return pipeline.execute()
    
    
    def work(self):
        """
        Background thread to process the queue items in batches
        """
        counter = 1
        database = Database()
        
        while True:
            counter += 1
            items = self.retrieve(length=self.batch_size)
            items_size = len(items)

            # if there's nothing in redis queue sleep for 5 seconds
            if items_size == 0:
                sleep(5)
                continue

            # create a new insert statement and insert into database
            query = database.create_insert_query_string(items)

            with database.open_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()

            # if items retrieved was less than the batch size
            # let's slow down the queue
            # if items is x then we will slow down by (1000 - x) / 10 milliseconds
            delay = (self.batch_size - items_size) / self.batch_size

            if delay > 0:
                sleep(delay)


class Contribution:
    def __init__(self, request):
        self.tbc = request.form.get('tbc')
        self.tfc = request.form.get('tfc')
        self.cci = request.form.get('cci')


    def verify(self):
        """
        Validates request data from contributions and verifies the authenticity.
        Throws an exception if validation fails
        
        Args: 
            self.tfc: trace forward component
            self.tbc: trace back component
            self.cci: caller callee information
        """
        if self.tbc == None or self.tfc == None or self.cci == None:
            raise PanicAttack("Valid values of tbc, tfc and cci are required")


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
        """
        Validates request data from trace queries and verifies the authenticity.
        Throws an exception if validation fails
        
        Args: 
            self.type: Type of trace request
            self.tfc: trace forward component
            self.tbc: trace back component
            self.cci: caller callee information
        """
        if self.type not in ['traceforward', 'traceback', 'lookup']:
            raise PanicAttack('Invalid type parameter')
        
        if self.type == 'traceback' and self.tbc == None:
            raise PanicAttack('tbc is required for traceback requests')
        
        if self.type == 'traceforward' and self.tfc == None:
            raise PanicAttack('tfc is required for traceforward requests')
        
        if self.type == 'lookup' and self.cci == None:
            raise PanicAttack('cci is required for full trace requests')


    def compute(self):
        """
        Computes a traceback, traceforward or a full/partial lookups
            
        Returns:
            Traceback, A set of encrypted records
        """
        if self.type == 'traceback':
            return self.traceback()
        elif self.type == 'traceforward':
            return self.traceforward()
        elif self.type == 'lookup':
            return self.partial_lookup()
        else:
            raise PanicAttack("Unrecognized trace action", 400)
        
        
    def traceback(self):
        """
        Performs a trace back query
        
        Args: 
            self.tfc: trace back component which was submitted during contribution
            
        Returns:
            Traceback, A set of encrypted records
        """
        db = Database()
        connection = db.open_db()
        cursor = connection.cursor()
        
        tbc = self.tbc
        result_set = [tbc]
        
        while tbc is not None:
            query = f"SELECT tbc, tfc FROM cdrs WHERE cdrs.tfc = %s ORDER BY cdrs.created_at ASC"
            
            try:
                cursor.execute(query, (tbc,))
                record = cursor.fetchone()
                
                if record is None:
                    break
                else:
                    retrieved_tbc = record[0]
                    
                    result_set.insert(0, retrieved_tbc)
                    tbc = retrieved_tbc
            except Exception as feeling: 
                print(feeling.with_traceback())
                break
        
        cursor.close()
        connection.close()
        
        return result_set
    
    
    def traceforward(self):
        """
        Performs a trace forward query
        
        Args: 
            self.tfc: trace forward component which was submitted during contribution
            
        Returns:
            Traceforward, A set of encrypted records
        """
        db = Database()
        connection = db.open_db()
        cursor = connection.cursor()
        
        tfc = self.tfc
        result_set = [tfc]
        
        while tfc is not None:
            query = f"SELECT tbc, tfc FROM cdrs WHERE cdrs.tbc = %s ORDER BY cdrs.created_at ASC"
            print(query)
            
            try:
                cursor.execute(query, (tfc,))
                record = cursor.fetchone()
                
                if record is None:
                    break
                else:
                    retrieved_tfc = record[1]
                    
                    result_set.append(retrieved_tfc)
                    tfc = retrieved_tfc
            except Exception as feeling: 
                print(feeling.with_traceback())
                break
        
        cursor.close()
        connection.close()
        
        return result_set
    
    
    def partial_lookup(self):
        """
        Performs full/partial lookups. Usually for cases where there's fragmentation
        
        Args:
            self.cci: caller/callee information
            
        Returns:
            A set of encrypted records
        """
        db = Database()
        connection = db.open_db()
        cursor = connection.cursor()
        
        cipher_set = ','.join([self.cci])
        
        query = f"SELECT tfc FROM cdrs WHERE cdrs.cci in (%s)"
        
        cursor.execute(query, (cipher_set,))
        query_result = cursor.fetchall()
        result_set = []
        
        for row in query_result:
            result_set.append(row[0])
       
        cursor.close()
        connection.close()
        
        return result_set
    
    
class PanicAttack(HTTPException):
    code = 422
    description = "Unprocessable entity"

    def __init__(self, message, code = 422):
        super().__init__()
        self.description = message
        self.code = code
        
          
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
        daemon = Thread(target=self.queue.work, daemon=True, name='BULK INSERTIONS')
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
    