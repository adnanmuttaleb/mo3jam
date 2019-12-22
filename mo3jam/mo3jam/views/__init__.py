from flask_restplus import Api

from .domain import domain_ns
from .user import user_ns
from .terminology import terminology_ns
from .dictionary import dictionary_ns
from .search import search_ns
from .role import role_ns
from .auth import auth_ns, blacklist


api = Api(title='Mo3jam API', version="1.0", doc='/api/v1.0/docs', prefix='/api/v1.0')

api.add_namespace(domain_ns)
api.add_namespace(user_ns)
api.add_namespace(terminology_ns)
api.add_namespace(dictionary_ns)
api.add_namespace(search_ns)
api.add_namespace(role_ns)
api.add_namespace(auth_ns)

