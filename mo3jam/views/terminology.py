import uuid
from datetime import datetime

import pyexcel as px
from eventsourcing.example.application import (
    get_example_application, 
)

from flask import request, abort, current_app, make_response, send_file
from flask_restplus import Resource, fields
from flask_restplus.marshalling import marshal, marshal_with

from .. import api
from ..entities import *
from ..models import TerminologyView, UserView, DomainView, DictionaryView
from .serializers import terminology_fields, translation_fields
from .utils import get_pagination_urls, roles_accepted, roles_required
from ..utils.file_utils import get_records, get_spreadsheet

terminology_ns = api.namespace('terminologies', description='Terminology Endpoint',)

def parse_terminology(obj):
    data = {}
    data['term'] = obj['term'].lower()
    data['language'] = obj.get('language', 'en')
    creator_id = uuid.UUID(obj['creator'])
    domain_id = uuid.UUID(obj['domain'])
    data['creator'] = UserView.objects.get(id=creator_id).id
    data['domain'] = DomainView.objects.get(id=domain_id).id           
    
    return data


def parse_translation(obj):
    data = {}
    data['value'] = obj['value'].lower()
    data['notes'] = obj.get('notes', '').lower()
    creator_id = uuid.UUID(obj['creator'])
    author_id = uuid.UUID(obj['author'])
    data['creator'] = UserView.objects.get(id=creator_id).id
    data['author'] = DictionaryView.objects(id=author_id).first()
    
    data['author'] = data['author'].id if data['author'] else data['creator']
    return data


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
        terminology_data = parse_terminology(request.json)
        terminology = Terminology.__create__(
            **terminology_data,
            creation_date=datetime.now(),
        )

        terminology.__save__()
        return '', 200


@terminology_ns.route('/<string:id>')
@terminology_ns.doc(params={'id': "Terminology's ID " })
class TerminologyDetails(Resource):
    
    @marshal_with(terminology_fields)
    def get(self, id):
        return TerminologyView.objects.get_or_404(id=id)

    @roles_accepted(['superuser', 'editor',])
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

    @roles_accepted(['superuser', 'editor',])
    def delete(self, id):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]
        terminology.__discard__()
        terminology.__save__()

        return '', 204


@terminology_ns.route('/upload')
class UploadTerminologies(Resource):

    def save(self, record):
        terminology_data = parse_terminology(record)
        terminology = Terminology.__create__(
            **terminology_data,
            creation_date=datetime.now(),
        )

        terminology.__save__()
        return terminology
        

    def post(self): 
        if 'file' not in request.files:
            abort(400, 'No File Selected')

        uploaded_file = request.files["file"]
        records = get_records(uploaded_file, file_type='xlsx')
        saved, failed = [],[]
        
        for record in records:
            try:
                terminology = self.save(record)
                record.update(id=str(terminology.id))
                saved.append(record)
            except Exception as e:
                record.update(reason=str(e))
                failed.append(record)
                
        output_file = get_spreadsheet(
            {
                'Saved': saved, 
                'Failed': failed
            }
        )
        
        return send_file(
            output_file, 
            as_attachment=True, 
            attachment_filename='upload-reports.xlsx'
        )

@terminology_ns.route('/<string:id>/translations')
@terminology_ns.doc(params={'id': "Terminology's ID " })
class TranslationsList(Resource):
    
    @marshal_with(translation_fields)
    def get(self, id):
        return TerminologyView.objects.get_or_404(id=id).translations
    
    @terminology_ns.expect(translation_fields)
    def post(self, id):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]
        data = parse_translation(request.json)

        translation = Translation(
            **data,
            id =uuid.uuid4(), 
            creation_date=datetime.now(),          
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
    
    @roles_accepted(['superuser', 'editor',])
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
    
    @roles_accepted(['superuser', 'editor',])
    def delete(self, id, trans_id):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]

        trans_id = uuid.UUID(trans_id)
        terminology.delete_translation(trans_id)
        terminology.__save__()

        return '', 204


@terminology_ns.route('/<string:id>/upload/translations')
class UploadTranslations(Resource):

    def save(self, record):
        app = get_example_application()
        terminology = app.example_repository[uuid.UUID(id)]
        data = parse_translation(record)

        translation = Translation(
            **data,
            id =uuid.uuid4(), 
            creation_date=datetime.now(),          
        )        

        terminology.add_translation(translation)
        terminology.__save__()
        
        return translation
    
    def post(self, id): 
        if 'file' not in request.files:
            abort(400, 'No File Selected')

        uploaded_file = request.files["file"]
        records = get_records(data_file=uploaded_file, file_type='xlsx')
        saved, failed = [], []
        
        for record in records:
            try:
                translation = self.save(record)
                record.update(id=str(translation.id))
                saved.append(record)
            except Exception as e:
                record.update(reason=str(e))
                failed.append(record)          

        output_file = get_spreadsheet(
            {
                'Saved': saved, 
                'Failed': failed
            }
        )

        return send_file(
            output_file, 
            as_attachment=True, 
            attachment_filename='upload-reports.xlsx'
        )