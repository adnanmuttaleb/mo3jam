from dateutil.parser import parse as date_parser
import uuid

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource
from flask_restplus.marshalling import marshal, marshal_with

from .. import api
from ..models import DictionaryView
from .serializers import dictionary_fields
from .utils import get_pagination_urls, roles_accepted, roles_required

dictionary_ns = api.namespace('dictionaries', description="Dictionaries' API",)

@dictionary_ns.route('/')
class DictionaryList(Resource):

    def get(self):
        response = {}
        page = request.args.get('page', 1)
        page_size = request.args.get('page_size', current_app.config['RESULTS_PER_PAGE']) 
        queryset = list(DictionaryView.objects[(page-1)*page_size:page*page_size])
        response['dictionaries'] = marshal(
            queryset,
            dictionary_fields,
        )
        response.update(get_pagination_urls(queryset, page, page_size))
        return response
    
    @roles_accepted(['superuser', 'editor',])
    @dictionary_ns.expect(dictionary_fields)    
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

    @marshal_with(dictionary_fields)
    def get(self, dict_id):
        return DictionaryView.objects.get_or_404(id=dict_id)
    
    @roles_accepted(['superuser', 'editor',])
    @dictionary_ns.expect(dictionary_fields,)    
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

    @roles_accepted(['superuser', 'editor',])
    def delete(self, dict_id):
        dictionary = DictionaryView.objects.get_or_404(id=dict_id)
        dictionary.delete()
        return '', 204
    