import uuid

from flask import request, abort, current_app
from flask_restplus import Resource, Namespace

from ..models import DictionaryView
from mo3jam.schemas import DictionarySchema
from ..utils import get_pagination_urls, roles_accepted, roles_required, get_json_schema

dictionary_ns = Namespace('dictionaries', description="Dictionaries' API",)
dictionary_fields = dictionary_ns.schema_model(
    'Dictionary',
    get_json_schema(DictionarySchema)
)


@dictionary_ns.route('/')
class DictionaryList(Resource):
    schema = DictionarySchema()

    def get(self):
        response = {}
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset = DictionaryView.objects[(page-1)*page_size:page*page_size]
        response['dictionaries'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
        return response
       
    @dictionary_ns.expect(dictionary_fields)
    def post(self):
        data = self.schema.load(request.get_json())
        dictionary = DictionaryView(
            id=uuid.uuid4(),
            **data
        )
        dictionary.save()
        return self.schema.dump(dictionary)


@dictionary_ns.route('/<string:dict_id>')
@dictionary_ns.doc(params={
    "dict_id": 'ID of dictionary to be updated.'
})
class DictionaryDetails(Resource):
    schema = DictionarySchema()

    def get(self, dict_id):
        return self.schema.dump(DictionaryView.objects.get_or_404(id=dict_id))
    
    @dictionary_ns.expect(dictionary_fields)
    def put(self, dict_id):
        dictionary = DictionaryView.objects.get_or_404(id=dict_id)
        data = self.schema.load(request.get_json())
        dictionary.update(**data)
        dictionary.reload()
        return self.schema.dump(dictionary)

    def delete(self, dict_id):
        dictionary = DictionaryView.objects.get_or_404(id=dict_id)
        dictionary.delete()
        return '', 204
    