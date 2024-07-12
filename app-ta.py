import os
from dotenv import load_dotenv
from flask import Flask, request
import jager.witenc as witenc
import jager.helpers as helpers
import jager.config as config
import jager.response as response
import jager.groupsig as groupsig

load_dotenv()

class TraceAuth:
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
        refresh = False
        keys: config.WEKeys = witenc.load_ta_keys()
        gpk = groupsig.get_gpk()
        
        @app.post('/authorize')
        def authorize():
            groupsig.validate_signature_from_request(request=request, gpk=gpk)
            labels = helpers.validate_json_list(request.form.get('payload'))
            sigs = witenc.server_authorize(sk=keys.sk, labels=labels)
            return response.ok({ 'res': sigs })
        
        @app.errorhandler(response.NOT_FOUND)
        def page_not_found(e):
            return response.not_found()
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            return response.handle_ex(e)

        return app


def create_app(test_config=None):
    return TraceAuth().start(test_config)