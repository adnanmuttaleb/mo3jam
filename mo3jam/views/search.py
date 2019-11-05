import uuid
from datetime import datetime

from flask import request, jsonify, abort, current_app, url_for
from flask_restplus import Resource
from flask_restplus.marshalling import marshal

from .. import api
from ..models import TerminologyView, UserView, DomainView, DictionaryView
from .serializers import *
from .utils import get_pagination_urls

search_ns = api.namespace('search', description='Search Endpoint',)


@search_ns.route('/terminology')
class TerminologySearch(Resource):

    def get(self):

        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset,count = TerminologyView.search(query, page, page_size)
        queryset = list(queryset)
        
        response = {}
        response['count'] = count
        response['terminologies'] = marshal(queryset, terminology_fields,)
        response.update(get_pagination_urls(queryset, page, page_size))
        
        return response
    
    

@search_ns.route('/domain')
class DomainSearch(Resource):

    def get(self):
        
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE']))
        queryset,count = DomainView.search(query, page, page_size)
        queryset = list(queryset)
        
        response = {}
        response['count'] = count
        response['domains'] = marshal(queryset, domain_fields)
        response.update(get_pagination_urls(queryset, page, page_size))
       
        return response
    

@search_ns.route('/user')
class UserSearch(Resource):

    def get(self):

        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset, count = UserView.search(query, page, page_size)
        queryset = list(queryset)
        
        response = {}
        response['count'] = count
        response['users'] = marshal(queryset, user_fields)
        response.update(get_pagination_urls(queryset, page, page_size))
        
        return response
    
