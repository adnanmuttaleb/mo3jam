import sentry_sdk
from flask import Flask
from flask_jwt_extended import JWTManager

from flask_mongoengine import MongoEngine
from elasticsearch import Elasticsearch
from sentry_sdk.integrations.flask import FlaskIntegration

mongo_db = MongoEngine()
jwt_manager = JWTManager()

def create_app(test_config=None):
   
    app = Flask(__name__)
    
    if not test_config:
        app.config.from_pyfile('config.py')
        app.config.from_envvar('SETTINGS', silent=True)
    else:
        app.config.from_mapping(test_config)
        
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if 'ELASTICSEARCH_URL' in app.config else None
    
    from .models import UserView, Role
    from .views import api

    mongo_db.init_app(app)
    api.init_app(app)
    jwt_manager.init_app(app)
    
    if 'SENTRY_DSN' in app.config:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()]
        )
    
    @jwt_manager.user_claims_loader
    def add_claims_to_access_token(identity):
        return {   
            "roles": [role.name for role in UserView.objects.get(id=identity).roles]
        }

    @jwt_manager.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return jti in blacklist

    @app.before_first_request
    def before_first_request():
        pass
    
    return app
    