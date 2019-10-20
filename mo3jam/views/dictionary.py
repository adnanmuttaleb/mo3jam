from dateutil.parser import parse as date_parser
import uuid

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource, fields

from .. import api
from ..models import DictionaryView

dictionary_ns = api.namespace('dictionaries', description="Dictionaries' API",)
dictionary_fields = dictionary_ns.model(
    'Dictionary',
    {
        'author': fields.String,
        'title': fields.String,
        'publication_date': fields.Date
    }
)

@dictionary_ns.route('/')
class DictionaryList(Resource):

    def get(self):
        queryset = DictionaryView.objects
        return jsonify(queryset)
    
    @dictionary_ns.expect(dictionary_fields, validate=True)    
    def post(self):
        
        author = request.json['author']
        title = request.json['title']
        pub_date = date_parser(request.json['pub_date'])

        dictionary = DictionaryView(
            id=uuid.uuid4(),
            author=author, 
            title=title, 
            publication_date=pub_date
        )
        dictionary.save()

        return jsonify(dictionary)


@dictionary_ns.route('/<string:dict_id>')
@dictionary_ns.doc(params={
    "dict_id": 'ID of dictionary to be updated.'
})
class DictionaryDetails(Resource):

    def get(self, dict_id):
        dictionary = DictionaryView.objects.get_or_404(id=dict_id)
        return jsonify(dictionary)
    
    @dictionary_ns.expect(dictionary_fields, validate=True)    
    def put(self, dict_id):

        author = request.json['author']
        title = request.json['title']
        pub_date = date_parser(request.json['pub_date'])
        
        dictionary = DictionaryView.objects.get_or_404(id=dict_id)
        dictionary.update(
            author=author, 
            title=title,
            publication_date=pub_date
        )

        return '', 200

    def delete(self, dict_id):
        dictionary = DictionaryView.objects.get_or_404(id=dict_id)
        dictionary.delete()
        return '', 204
    