import os
import traceback as ex
from dotenv import load_dotenv
from flask import Flask, request
import models.helpers as helpers
import models.response as response
from werkzeug.exceptions import HTTPException
import models.jobs as jobs

load_dotenv()

class TracebackProvider:
    def create_instance_path(self, app):
        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass
        
    def start(self, test_config=None):
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(SECRET_KEY=helpers.env("APP_SECRET_KEY"))
        self.create_instance_path(app)

        @app.post('/submit')
        def submit():
            jobs.submit(request)
            return response.ok()

        @app.post('/traceback')
        def traceback():
            cts = jobs.traceback(request)
            return response.ok({'res': cts})
        
        
        @app.errorhandler(404)
        def page_not_found(e):
            return response.not_found()
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            if isinstance(e, HTTPException):
                return e
            else:
                print("\n")
                ex.print_exc()
                print("\n")
                return response.internal_server_error()

        return app


def create_app(test_config=None):
    return TracebackProvider().start(test_config)