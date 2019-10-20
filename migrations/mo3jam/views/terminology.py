import uuid
from datetime import datetime

from eventsourcing.example.application import (
    get_example_application, 
)

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource, fields

from .. import api
from ..entities import *
from ..models import TerminologyView, UserView, DomainView, DictionaryView


terminology_ns = api.namespace('terminologies', description='Terminology Endpoint',)

terminology_fields = terminology_ns.model('Terminology', {
    "term": fields.String(min_length=2),
    "creator": fields.String
})

translation_fields = terminology_ns.model('Translation', {
    "value": fields.String,
    "creator": fields.String,
    "author": fields.String,
    "notes": fields.String
})


@terminology_ns.route('/')
class TerminologyList(Resource):

    def get(self):
        query = request.args.get('q', '')
        page = request.args.get('page', 1)
        queryset,_ = TerminologyView.search(query, page, current_app.config['RESULTS_PER_PAGE'])
        return jsonify(TerminologyView.objects)
    
    @terminology_ns.expect(terminology_fields, validate=True)    
    def post(self):

        term = request.json['term']
        creator_id = uuid.UUID(request.json['creator'])
        domain_id = uuid.UUID(request.json['domain'])
        creator = UserView.objects.get(id=creator_id)
        domain = DomainView.objects.get(id=domain_id)        
        
        terminology = Terminology.__create__(
            term=term, 
            domain=domain.id,
            creator=creator.id,
            creation_date=datetime.now() 
        )

        terminology.__save__()
        
        return '', 200


@terminology_ns.route('/<string:term_id>')
@terminology_ns.doc(params={'term_id': "Terminology's ID " })
class TerminologyDetails(Resource):

    def get(self, term_id):
        terminology = TerminologyView.objects(id=term_id).first()
        if terminology:
            return jsonify(terminology)
        else:
            abort(404)

    @terminology_ns.expect(terminology_fields)    
    def put(self, term_id):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(term_id)]

        domain = DomainView.objects.get(id=uuid.UUID(request.json.get('domain')))
        if domain and domain.id != terminology.domain:
            terminology.set_domain(domain.id)
        
        terminology.__save__()
        return '', 200

    def delete(self, term_id):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(term_id)]
        terminology.__discard__()
        terminology.__save__()

        return '', 204

@terminology_ns.route('/<string:term_id>/translations')
@terminology_ns.doc(params={'term_id': "Terminology's ID " })
class TranslationsList(Resource):

    def get(self, term_id):
        terminology = TerminologyView.objects(id=term_id).first()
        if terminology:
            return jsonify(terminology.translations)
        else:
            abort(404)
   
    @terminology_ns.expect(translation_fields, validate=True)
    def post(self, term_id):

        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(term_id)]

        value = request.json['value']
        notes = request.json['notes']
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


@terminology_ns.route('/<string:term_id>/translations/<string:trans_id>')
@terminology_ns.doc(params={'term_id': "Terminology's ID ", "trans_id": "Translation's ID"})
class TranslationDetails(Resource):

    def get(self, term_id, trans_id):
        terminology = TerminologyView.objects(id=term_id).first()
        for tans in terminology.translations:
            if trans.id == trans_id:
                return jsonify(trans)
        
        abort(404)

    @terminology_ns.expect(translation_fields,)
    def put(self, term_id, trans_id):
        
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(term_id)]
        
        value = request.json.get('value')
        notes = request.json.get('notes')
        author_id = uuid.UUID(request.json['author'])

        author = DictionaryView.objects.get(id=author_id) or UserView.objects.get(id=author_id) 
        
        translation = Translation(
            id =uuid.UUID(trans_id),
            author=author.id,
            notes=notes,
            creator=None,
            value=value
        )        

        terminology.update_translation(translation)
        terminology.__save__()

        return '', 200

    def delete(self, term_id, trans_id):

        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(term_id)]

        trans_id = uuid.UUID(trans_id)
        terminology.delete_translation(trans_id)
        terminology.__save__()

        return '', 204

