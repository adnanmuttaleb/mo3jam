from flask_restplus import Resource, fields

from .. import api
from ..models import TerminologyView, UserView, DomainView, DictionaryView


author_fields = api.model(
    'Author', 
    {   'type': fields.String(
            attribute=lambda x: 'author' if not x else\
            'dictionary' if x._cls == DictionaryView.__name__\
            else 'user'
        ),
        'username': fields.String,
        'email': fields.String,
        'title': fields.String,
        'author': fields.String,
        'publication_date': fields.Date,
        'id': fields.String,

    }
)

dictionary_fields = api.model(
    'Dictionary', 
    {   
        'title': fields.String,
        'author': fields.String,
        'publication_date': fields.Date,
        'id': fields.String,

    }
)

user_fields = api.model(
    'User', 
    {
        'username': fields.String,
        'email': fields.String,
        'id': fields.String 

    }
)

translation_fields = api.model(
    'Translation', 
    {
        'value': fields.String,
        'creator': fields.Nested(user_fields),
        'author': fields.Nested(author_fields, skip_none=True),
        'creation_date': fields.DateTime,
        'notes': fields.String,
        'id': fields.String

    }
)

domain_fields = api.model(
    'Domain', 
    {
        'name': fields.String,
        'description': fields.String,
        'creator': fields.Nested(user_fields),
        'creation_date': fields.DateTime,
        'id': fields.String 

    }
)

terminology_fields = api.model(
    'Terminology', 
    {
        'term': fields.String(min_length=2),
        'language': fields.String,
        'creator': fields.Nested(user_fields),
        'creation_date': fields.DateTime,
        'notes': fields.List(fields.String),
        'domain': fields.Nested(domain_fields),
        'id': fields.String,
        'translations': fields.Nested(translation_fields),
    }
)

