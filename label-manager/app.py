import os
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request
import models.label_mgr as label_mgr
import models.helpers as helpers

load_dotenv()

class GroupManager:
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

        kprf = label_mgr.setup(refresh=refresh)

        @app.post('/register')
        def register():
            cid = request.form.get('cid')
            
            if not cid:
                return {"msg": "Missing cid"}, self.HTTP_UNPROCESSABLE
            
            cid = int(cid)
            
            if cid < 1 or cid > 7000:
                return {"msg": "Unrecognized ID"}, self.HTTP_UNPROCESSABLE
            
            return { 'kprf': kprf }, self.HTTP_OK
        
        @app.errorhandler(self.HTTP_NOT_FOUND)
        def page_not_found(e):
            return helpers.not_found()
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            return helpers.handle_ex(e)

        return app


def create_app(test_config=None):
    return GroupManager().start(test_config)