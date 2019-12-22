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

SENTRY_DSN = "https://279b767a15ac40dc9ef3aee616d79adb@sentry.io/1797633"


JWT_SECRET_KEY = 'supersecret'
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']