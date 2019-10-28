import uuid
from datetime import datetime

from eventsourcing.example.application import (
    get_example_application, 
)

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource, fields
from flask_restplus.marshalling import marshal, marshal_with

from .. import api
from ..entities import *
from ..models import TerminologyView, UserView, DomainView, DictionaryView
from .serializers import terminology_fields, translation_fields
from .utils import get_pagination_urls

terminology_ns = api.namespace('terminologies', description='Terminology Endpoint',)


@terminology_ns.route('/')
class TerminologyList(Resource):

    def get(self):
        response = {}
        page = request.args.get('page', 1)
        page_size = request.args.get('page_size', current_app.config['RESULTS_PER_PAGE']) 
        queryset = list(TerminologyView.objects[(page-1)*page_size:page*page_size])
        response['terminologies'] = marshal(
            queryset,
            terminology_fields,
        )
        response.update(get_pagination_urls(queryset, page, page_size))
        return response
    
    @terminology_ns.expect(terminology_fields)    
    def post(self):

        term = request.json['term']
        language = request.json.get('language')
        creator_id = uuid.UUID(request.json['creator'])
        domain_id = uuid.UUID(request.json['domain'])
        creator = UserView.objects.get(id=creator_id)
        domain = DomainView.objects.get(id=domain_id)        
        
        terminology = Terminology.__create__(
            term=term, 
            domain=domain.id,
            creator=creator.id,
            creation_date=datetime.now(),
            language=language,
        )

        terminology.__save__()
        
        return '', 200


@terminology_ns.route('/<string:id>')
@terminology_ns.doc(params={'id': "Terminology's ID " })
class TerminologyDetails(Resource):
    
    @marshal_with(terminology_fields)
    def get(self, id):
        terminology = TerminologyView.objects(id=id).first()
        if terminology:
            return terminology
        else:
            abort(404)

    @terminology_ns.expect(terminology_fields)    
    def put(self, id):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]
        
        language = request.json.get('language')
        domain_id = request.json.get('domain')
       
        if domain_id:
            domain = DomainView.objects.get(id=domain_id)
            if domain.id != terminology.domain:
                terminology.set_domain(domain.id)
        if language and language != terminology.language:
            terminology.change_language(language)

        terminology.__save__()
        return '', 200

    def delete(self, id):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]
        terminology.__discard__()
        terminology.__save__()

        return '', 204

@terminology_ns.route('/<string:id>/translations')
@terminology_ns.doc(params={'id': "Terminology's ID " })
class TranslationsList(Resource):
    
    @marshal_with(translation_fields)
    def get(self, id):
        terminology = TerminologyView.objects(id=id).first()
        if terminology:
            return terminology.translations
        else:
            abort(404)
   
    @terminology_ns.expect(translation_fields)
    def post(self, id):

        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]

        value = request.json['value']
        notes = request.json.get('notes', '')
        author_id = uuid.UUID(request.json['author'])
        creator_id = uuid.UUID(request.json['creator'])

        
        creator = UserView.objects.get(id=creator_id)
        author = DictionaryView.objects.get(id=author_id) or creator 
        
        translation = Translation(
            id =uuid.uuid4(), 
            value=value, 
            author=author.id, 
            creator=creator.id,
            creation_date=datetime.now(),
            notes=notes
        )        

        terminology.add_translation(translation)
        terminology.__save__()

        return '', 200


@terminology_ns.route('/<string:id>/translations/<string:trans_id>')
@terminology_ns.doc(params={'id': "Terminology's ID ", "trans_id": "Translation's ID"})
class TranslationDetails(Resource):
    
    @marshal_with(translation_fields)
    def get(self, id, trans_id):
        terminology = TerminologyView.objects(id=id).first()
        translation = terminology.translations.get(id=trans_id)
        if translation:
            return translation
        abort(404)

    @terminology_ns.expect(translation_fields,)
    def put(self, id, trans_id):
        
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]
        data = {}

        value = request.json.get('value')
        notes = request.json.get('notes')
        
        try:
            author_id = uuid.UUID(request.json.get('author'))
            author = DictionaryView.objects.get(id=author_id) or UserView.objects.get(id=author_id) 
        except Exception:
            author = None

        if value:
            data['value'] = value
        if notes:
            data['notes'] = notes
        if author:
            data['author'] = author.id


        terminology.update_translation(uuid.UUID(trans_id), data)
        terminology.__save__()

        return '', 200

    def delete(self, id, trans_id):

        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]

        trans_id = uuid.UUID(trans_id)
        terminology.delete_translation(trans_id)
        terminology.__save__()

        return '', 204

