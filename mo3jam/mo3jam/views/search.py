import uuid
from datetime import datetime

from flask import request, jsonify, abort, current_app, url_for
from flask_restplus import Resource, Namespace
from flask_restplus.marshalling import marshal

from mo3jam.models import TerminologyView, UserView, DomainView, DictionaryView
from mo3jam.schemas import TerminologySchema, DomainSchema, UserSchema
from mo3jam.utils import get_pagination_urls

search_ns = Namespace('search', description='Search Endpoint',)


@search_ns.route('/terminology')
class TerminologySearch(Resource):
    schema = TerminologySchema()

    def get(self):
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset, count = TerminologyView.search(query, page, page_size)

        response = {}
        response['count'] = count
        response['terminologies'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
        
        return response
    
    
@search_ns.route('/domain')
class DomainSearch(Resource):
    schema = DomainSchema()

    def get(self):
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE']))
        queryset, count = DomainView.search(query, page, page_size)
        
        response = {}
        response['count'] = count
        response['domains'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
       
        return response
    

@search_ns.route('/user')
class UserSearch(Resource):
    schema = UserSchema()

    def get(self):
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset, count = UserView.search(query, page, page_size)
        
        response = {}
        response['count'] = count
        response['users'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
        
        return response
    
