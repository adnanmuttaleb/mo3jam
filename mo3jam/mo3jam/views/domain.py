import uuid
from dateutil.parser import parse as date_parser
from datetime import datetime

from flask import request, abort, current_app
from flask_restplus import Resource, Namespace

from mo3jam.models import DomainView, UserView
from mo3jam.schemas import DomainSchema
from mo3jam.utils import get_pagination_urls, roles_accepted, roles_required, get_json_schema

domain_ns = Namespace('domains', description='Domain Endpoint',)
domain_fields = domain_ns.schema_model(
    'Domain',
    get_json_schema(DomainSchema)
)


@domain_ns.route('/')
class DomainList(Resource):
    schema = DomainSchema()
    
    def get(self):
        response = {}
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE']))
        queryset = list(DomainView.objects[(page-1)*page_size:page*page_size])
        response['domains'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
        return response

    @domain_ns.expect(domain_fields)
    def post(self):
        data = self.schema.load(request.get_json())
        domain = DomainView(
            **data,
            id=uuid.uuid4()
        )
        domain.save()
        return '', 200


@domain_ns.route('/<string:domain_id>')
@domain_ns.doc(params={
    "domain_id": "Domain ID"
})
class DomainDetails(Resource):
    schema = DomainSchema()

    def get(self, domain_id):
        return self.schema.dump(DomainView.objects.get_or_404(id=domain_id))
    
    @domain_ns.expect(domain_fields)
    def put(self, domain_id):    
        domain = DomainView.objects.get_or_404(id=domain_id)
        data = self.schema.load(request.get_json())
        if data['name'] != domain.name:
            domain.edit_name(data['name'])
       
        if data['description'] != domain.description:
            domain.edit_description(data['description'])

        return '', 200

    @roles_accepted(['superuser', 'editor',])
    def delete(self, domain_id):
        domain = DomainView.objects.get_or_404(id=domain_id)
        domain.delete()
        return '', 204