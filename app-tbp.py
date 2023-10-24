import os
import traceback as ex
from dotenv import load_dotenv
from flask import Flask, request
import privytrace.groupsig as groupsig
import privytrace.jobs as jobs
import privytrace.config as config
import privytrace.response as response

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
        app.config.from_mapping(SECRET_KEY=config.APP_SECRET_KEY)
        self.create_instance_path(app)
        gpk = groupsig.get_gpk()

        @app.post('/submit')
        def submit():
            jobs.submit(request=request, gpk=gpk)
            return response.ok()

        @app.post('/traceback')
        def traceback():
            cts = jobs.traceback(request=request, gpk=gpk)
            return response.ok({'res': cts})
        
        
        @app.errorhandler(404)
        def page_not_found(e):
            return response.not_found()
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            return response.handle_ex(e)

        return app


def create_app(test_config=None):
    return TracebackProvider().start(test_config)