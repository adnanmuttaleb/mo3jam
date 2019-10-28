SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'dev'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/mo3jam.db'
MONGODB_SETTINGS = {
    'db': 'mo3jam',
    'host': 'localhost',
    'port': 27017,

}


ELASTICSEARCH_URL = "http://localhost:9200"
RESULTS_PER_PAGE = 20

FLASK_ADMIN_SWATCH = 'cerulean'