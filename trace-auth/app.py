import os
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request
import models.witness_enc as witness_enc
import models.helpers as helpers

load_dotenv()

class TraceAuth:
    def __init__(self) -> None:
        self.HTTP_OK = 200
        self.HTTP_CREATED = 201
        self.HTTP_NOT_FOUND = 404
        self.HTTP_UNPROCESSABLE = 422
           
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
        refresh = False

        keys: helpers.Keys = witness_enc.setup(refresh=refresh)

        @app.post('/register')
        def register():
            cid = helpers.validate_cid(request.form.get('cid'))
            return { 'pk': keys.pk }, self.HTTP_OK
        
        @app.post('/authorize')
        def authorize():
            labels = helpers.validate_labels(request.form.get('payload'))
            sigs = witness_enc.authorize(sk=keys.sk, labels=labels)
            return { 'res': sigs }, self.HTTP_OK
        
        @app.errorhandler(self.HTTP_NOT_FOUND)
        def page_not_found(e):
            return helpers.not_found()
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            return helpers.handle_ex(e)

        return app


def create_app(test_config=None):
    return TraceAuth().start(test_config)