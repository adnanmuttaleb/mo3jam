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
        'active':fields.String,
        'roles': fields.List(fields.String(attribute='id')),
        'id': fields.String, 
    
    }
)

role_fields = api.model(
    'Role', 
    {
        'name': fields.String,
        'description': fields.String,
        'id': fields.String, 
    }
)

translation_fields = api.model(
    'Translation', 
    {
        'value': fields.String,
        'creator': fields.String(attribute=lambda trans: trans.creator.id),
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
        'creator': fields.String(attribute=lambda domain: domain.creator.id),
        'creation_date': fields.DateTime,
        'id': fields.String 

    }
)

terminology_fields = api.model(
    'Terminology', 
    {
        'term': fields.String(min_length=2),
        'language': fields.String,
        'creator': fields.String(attribute=lambda term: term.creator.id),
        'creation_date': fields.DateTime,
        'notes': fields.List(fields.String),
        'domain': fields.String(attribute=lambda term: term.domain.id),
        'id': fields.String,
        'translations': fields.List(fields.String(attribute='id')),
    }
)

