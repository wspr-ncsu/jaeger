import os
import traceback as ex
from json import loads
from flask import Flask, request
import privytrace.config as config
import privytrace.helpers as helpers
import privytrace.groupsig as groupsig
import privytrace.response as response

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
        refresh = False

        gsign_keys = groupsig.setup(refresh=refresh)
        groupsig.register_all(gsign_keys, refresh=refresh)

        @app.post('/register')
        def register():
            cid = helpers.validate_cid(request.form.get('cid'))
            payload = groupsig.register(cid=cid, gsign_keys=gsign_keys, refresh=refresh)
            return response.created(payload=payload)


        @app.post('/open')
        def open_sigs():
            groupsig.validate_request(request=request, gpk=gsign_keys['gpk'])
            records = loads(request.form.get('payload'))
            res = groupsig.open_sigs(records=records, gsign_keys=gsign_keys)
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