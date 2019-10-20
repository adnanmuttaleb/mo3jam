from sqlalchemy_utils import UUIDType
from flask import Flask
from flask_restplus import Api
from eventsourcing.example.application import (
    init_example_application
)
from eventsourcing.infrastructure.sqlalchemy.manager import (
    SQLAlchemyRecordManager,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mongoengine import MongoEngine
from elasticsearch import Elasticsearch

db = SQLAlchemy()
mongo_db = MongoEngine()
migrate = Migrate()

api = Api(title='Mo3jam API', version="1.0", doc='/docs', prefix='/api/v1.0')

from .views import *


class IntegerSequencedItem(db.Model):
    __tablename__ = 'integer_sequenced_items'

    id = db.Column(db.Integer, primary_key=True,)

    sequence_id = db.Column(UUIDType(), nullable=False)

    position = db.Column(db.BigInteger(), nullable=False, default=0)

    topic = db.Column(db.String(255))

    state = db.Column(db.Text())

    __table_args__ = db.Index('index', 'sequence_id', 'position', unique=True),


def create_app(test_config=None):
   
    app = Flask(__name__)
    
    if not test_config:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_config)
    
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if 'ELASTICSEARCH_URL' in app.config else None
    
    db.init_app(app)
    migrate.init_app(app, db)
    mongo_db.init_app(app)
    api.init_app(app)

    @app.before_first_request
    def before_first_request():
        init_example_application(
            entity_record_manager=SQLAlchemyRecordManager(
                record_class=IntegerSequencedItem,
                session=db.session,
            ),

        )
    
    return app
    