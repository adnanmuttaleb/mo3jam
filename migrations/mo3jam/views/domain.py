import uuid
from dateutil.parser import parse as date_parser
from datetime import datetime

from eventsourcing.example.application import (
    get_example_application, 
)

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource, fields

from .. import api
from ..entities import *
from ..models import TerminologyView, DomainView, UserView


domain_ns = api.namespace('domains', description='Domain Endpoint',)

domain_fields = domain_ns.model('Domain', {
    "name": fields.String,
    "creator": fields.String,
    "description": fields.String,
})

@domain_ns.route('/')
class DomainList(Resource):
    
    def get(self):
        queryset = DomainView.objects
        return jsonify(queryset)
    
    @domain_ns.expect(domain_fields, validate=True)
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

    def get(self, domain_id):
        domain = DomainView.objects.get_or_404(id=domain_id)
        return jsonify(domain)

    @domain_ns.expect(domain_fields, validate=True)
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


    def delete(self, domain_id):
        app = get_example_application()
        domain = app.example_repository[uuid.UUID(domain_id)]
        domain.__discard__()
        domain.__save__()

        return '', 204