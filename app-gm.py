import os
import traceback as ex
from json import loads
from flask import Flask, request
import jager.config as config
import jager.helpers as helpers
import jager.groupsig as groupsig
import jager.response as response

class GroupManager:
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

        gsign_keys = groupsig.mgr_import_keys()
        groupsig.mgr_register_all(gsign_keys)

        @app.post('/register')
        def register():
            cid = helpers.validate_cid(request.form.get('cid'))
            payload = groupsig.mgr_register_carrier(cid=cid, gsign_keys=gsign_keys)
            return response.created(payload=payload)


        @app.post('/open')
        def open_sigs():
            groupsig.validate_signature_from_request(request=request, gpk=gsign_keys['gpk'])
            records = loads(request.form.get('payload'))
            res = groupsig.mgr_open_sigs(records=records, gsign_keys=gsign_keys)
            return response.ok(payload=res)
        
        
        @app.errorhandler(response.NOT_FOUND)
        def page_not_found(e):
            return response.not_found()
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            return response.handle_ex(e)

        return app


def create_app(test_config=None):
    return GroupManager().start(test_config)