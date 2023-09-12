import os
from time import sleep
from json import loads, dumps
from redis import Redis
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request
from werkzeug.exceptions import HTTPException
from models.database import init_db, migrate_db
from models.helpers import env

load_dotenv()

class GroupManager:
    def __init__(self) -> None:
        self.HTTP_OK = 200
        self.HTTP_CREATED = 201
        self.HTTP_NOT_FOUND = 404
        self.HTTP_UNPROCESSABLE = 422
        self.HTTP_INTERNAL_SERVER_ERROR = 500
           
    def create_instance_path(self, app):
        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass
        
    def start(self, test_config=None):
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(SECRET_KEY=env("APP_SECRET_KEY"))
        self.create_instance_path(app)


        @app.post('/register')
        def register():
            return { "msg": "Registered" }, self.HTTP_CREATED


        @app.post('/deanonymize')
        def deanonymize():
            return { "msg": "Deanonymized" }, self.HTTP_OK
        
        
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
            
            return {"msg": e.description }, self.HTTP_INTERNAL_SERVER_ERROR

        return app


def create_app(test_config=None):
    return GroupManager().start(test_config)

if __name__ == '__main__':
    import sys
    
    if (len(sys.argv) >= 2):
        command = sys.argv[1]
        
        if command == 'migrate':
            init_db()
            migrate_db()
        else:
            print("Invalid Command")
    else:
        print("NO ARGUMENT PROVIDED")
    