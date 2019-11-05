import uuid
from dateutil.parser import parse as date_parser
from datetime import datetime

from eventsourcing.example.application import (
    get_example_application, 
)

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource
from flask_restplus.marshalling import marshal, marshal_with

from .. import api
from ..entities import *
from ..models import TerminologyView, DomainView, UserView
from .serializers import domain_fields, user_fields
from .utils import get_pagination_urls, roles_accepted, roles_required

domain_ns = api.namespace('domains', description='Domain Endpoint',)

@domain_ns.route('/')
class DomainList(Resource):
    
    def get(self):
        response = {}
        page = request.args.get('page', 1)
        page_size = request.args.get('page_size', current_app.config['RESULTS_PER_PAGE']) 
        queryset = list(DomainView.objects[(page-1)*page_size:page*page_size])
        response['domains'] = marshal(
            queryset,
            domain_fields,
        )
        response.update(get_pagination_urls(queryset, page, page_size))
        return response

    @roles_accepted(['superuser', 'editor',])
    @domain_ns.expect(domain_fields,)
    def post(self):
        
        name = request.json['name']
        description = request.json.get('description')
        creator_id = uuid.UUID(request.json['creator'])
        creation_date = datetime.now()

        creator = UserView.objects.get(id=creator_id)

        domain = Domain.__create__(
            name=name,
            description=description,
            creator=creator.id, 
            creation_date=creation_date,
        )
        domain.__save__()

        return '', 200


@domain_ns.route('/<string:domain_id>')
@domain_ns.doc(params={
    "domain_id": "Domain ID"
})
class DomainDetails(Resource):
    
    @marshal_with(domain_fields)
    def get(self, domain_id):
        return DomainView.objects.get_or_404(id=domain_id)
    
    @roles_accepted(['superuser', 'editor',])
    @domain_ns.expect(domain_fields)
    def put(sef, domain_id):
        
        app = get_example_application()
        domain = app.example_repository[uuid.UUID(domain_id)]

        name = request.json.get('name')
        description = request.json.get('description')

        if name and name != domain.name:
            domain.edit_name(name)
       
        if description and description != domain.description:
            domain.edit_description(description)

        domain.__save__()
       
        return '', 200

    @roles_accepted(['superuser', 'editor',])
    def delete(self, domain_id):
        app = get_example_application()
        domain = app.example_repository[uuid.UUID(domain_id)]
        domain.__discard__()
        domain.__save__()

        return '', 204