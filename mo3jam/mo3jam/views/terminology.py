import uuid
from datetime import datetime

from flask import request, abort, current_app, send_file
from flask_restplus import Resource, Namespace

from mo3jam.schemas import TerminologySchema, TranslationSchema, NoteSchema
from mo3jam.models import TerminologyView
from mo3jam.utils import (
    get_pagination_urls, 
    roles_accepted, roles_required, 
    get_records, get_spreadsheet, get_json_schema
)

terminology_ns = Namespace('terminologies', description='Terminology Endpoint',)

terminology_fields = terminology_ns.schema_model(
    'Terminology', 
    get_json_schema(TerminologySchema)
)

translation_fields = terminology_ns.schema_model(
    'Translation', 
    get_json_schema(TranslationSchema)
)

note_fields = terminology_ns.schema_model(
    'Note', 
    get_json_schema(NoteSchema)
)

@terminology_ns.route('/')
class TerminologyList(Resource):
    schema = TerminologySchema()
   
    def get(self):
        response = {}
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset = TerminologyView.objects[(page-1)*page_size:page*page_size]
        response['terminologies'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
        return response
    
    def _post(slef, data):
        translations = []
        if 'translations' in data:
            translations = data.pop('translations')
        
        if 'notes' in data:
            notes = data.pop('notes')
        
        terminology = TerminologyView(
            **data,
            id=uuid.uuid4()
        )

        terminology.save()

        for translation in translations:
            terminology.add_translation(**translation)
        
        for note in notes:
            terminology.add_note(**note)
    
    @terminology_ns.expect(terminology_fields)
    def post(self):
        content = request.get_json()
        if isinstance(content, dict):
            content = [content]

        parsed_content = self.schema.load(content, many=True)
        for doc in parsed_content:
            self._post(doc)

        return '', 200


@terminology_ns.route('/<string:id>')
@terminology_ns.doc(params={'id': "Terminology's ID " })
class TerminologyDetails(Resource):
    schema = TerminologySchema()

    def get(self, id):
        return self.schema.dump(TerminologyView.objects.get_or_404(id=id))
    
    @terminology_ns.expect(terminology_fields)
    def put(self, id):
        terminology = TerminologyView.objects.get(id=uuid.UUID(id))
        data = self.schema.load(request.get_json())
        if data["domain"] != terminology.domain.id:
            terminology.change_domain(data["domain"])
        if data['language'] != terminology.language:
            terminology.change_language(data['language'])
        return '', 200

    def delete(self, id):
        terminology = TerminologyView.objects.get(uuid.UUID(id))
        terminology.delete()
        return '', 204


@terminology_ns.route('/<string:id>/translations')
@terminology_ns.doc(params={'id': "Terminology's ID " })
class TranslationList(Resource):
    schema = TranslationSchema()

    def get(self, id):        
        return self.schema.dump(
            TerminologyView.objects.get_or_404(id=id).translations, 
            many=True
        )

    @terminology_ns.expect(translation_fields)
    def post(self, id):
        terminology = TerminologyView.objects.get(id=uuid.UUID(id))
        data = self.schema.load(request.get_json())
        terminology.add_translation(**data)
        return '', 200


@terminology_ns.route('/<string:id>/translations/<string:trans_id>')
@terminology_ns.doc(params={'id': "Terminology's ID ", "trans_id": "Translation's ID"})
class TranslationDetails(Resource):
    schema = TranslationSchema()
    
    def get(self, id, trans_id):
        terminology = TerminologyView.objects.get(id=id)
        translation = terminology.translations.get(id=trans_id)
        if translation:
            return self.schema.dump(translation)
        abort(404)
    
    @terminology_ns.expect(translation_fields)
    def put(self, id, trans_id):
        terminology = TerminologyView.objects.get(id=uuid.UUID(id))
        data = self.schema.load(request.get_json())
        terminology.update_translation(uuid.UUID(trans_id), data)
        return '', 200
    
    def delete(self, id, trans_id):
        terminology = TerminologyView.objects.get(id=uuid.UUID(id))
        terminology.delete_translation(uuid.UUID(trans_id))
        return '', 204



@terminology_ns.route('/<string:id>/notes')
@terminology_ns.doc(params={'id': "Terminology's ID " })
class NoteList(Resource):
    schema = NoteSchema()

    def get(self, id):        
        return self.schema.dump(
            TerminologyView.objects.get_or_404(id=id).notes, 
            many=True
        )
    
    @terminology_ns.expect(note_fields)
    def post(self, id):
        terminology = TerminologyView.objects.get(id=uuid.UUID(id))
        data = self.schema.load(request.get_json())
        terminology.add_note(**data)
        return '', 200


@terminology_ns.route('/<string:id>/notes/<string:note_id>')
@terminology_ns.doc(params={'id': "Terminology's ID ", "note_id": "Note's ID"})
class NoteDetails(Resource):
    schema = NoteSchema()    
    
    @terminology_ns.expect(note_fields)
    def put(self, id, note_id):
        terminology = TerminologyView.objects.get(id=uuid.UUID(id))
        data = self.schema.load(request.get_json())
        terminology.edit_note(note_id, **data)
        return '', 200
    
    def delete(self, id, note_id):
        terminology = TerminologyView.objects.get(id=uuid.UUID(id))
        terminology.delete_note(uuid.UUID(note_id))
        return '', 204