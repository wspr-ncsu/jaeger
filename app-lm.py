import os
from dotenv import load_dotenv
from flask import Flask, request
import jager.config as config
import jager.helpers as helpers
import jager.label_mgr as label_mgr
import jager.response as response

load_dotenv()

class LabelManager:
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

        sk = label_mgr.server_setup(refresh=refresh)

        @app.post('/evaluate')
        def evaluate():
            xs = helpers.validate_json_list(request.form.get('payload'))
            fxs = label_mgr.server_batch_evaluation(sk, xs)
            return response.ok({ 'res': fxs })
        
        @app.errorhandler(response.NOT_FOUND)
        def page_not_found(e):
            return response.not_found()
        
        @app.errorhandler(Exception)
        def handle_all_exceptions(e):
            return response.handle_ex(e)

        return app


def create_app(test_config=None):
    return LabelManager().start(test_config)