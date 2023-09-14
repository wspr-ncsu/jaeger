import os
import traceback as ex
from time import sleep
from json import loads, dumps
from redis import Redis
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request
from werkzeug.exceptions import HTTPException
from models.helpers import env
import models.groupsig as groupsig

load_dotenv()

class NetworkProvider:
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
        cid = int(env('APP_PORT')) - 9999 # Carrier ID (0 - 6999)
        
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(SECRET_KEY=env("APP_SECRET_KEY"))
        self.create_instance_path(app)

        mem_key, grp_key = groupsig.register(cid)
        
        @app.errorhandler(self.HTTP_NOT_FOUND)
        def page_not_found(e):
            return {
                'msg': 'The requested resource could not be found'
            }, self.HTTP_NOT_FOUND
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            if isinstance(e, HTTPException):
                return e
            else:
                print("\n")
                ex.print_exc()
                print("\n")
                
                return {
                    'msg': 'An unexpected error occurred'
                }, self.HTTP_INTERNAL_SERVER_ERROR

        return app


def create_app(test_config=None):
    return NetworkProvider().start(test_config)