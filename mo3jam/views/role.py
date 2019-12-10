import uuid

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource
from flask_restplus.marshalling import marshal, marshal_with

from .. import api
from ..models import Role
from .serializers import role_fields
from .utils import roles_accepted, roles_required

role_ns = api.namespace('roles', description='Roles API',)

@role_ns.route('/')
class RoleList(Resource):
    
    @marshal_with(role_fields)
    def get(self):
        return list(Role.objects)
    
    @roles_required(["superuser",])
    @role_ns.expect(role_fields)    
    def post(self):
        data = {}
        data['name'] = request.json['name'].lower()
        data['description'] = request.json['description'].lower()

        role = Role(**data)
        role.save()
        return marshal(role, role_fields)


@role_ns.route('/<string:role_id>')
@role_ns.doc(params={
    "role_id": 'ID of role to be updated.'
})
class RoleDetails(Resource):
   
    @marshal_with(role_fields)
    def get(self, role_id):
        return Role.objects.get_or_404(id=role_id)
    
    @roles_required(['superuser'])
    @role_ns.expect(role_fields, validate=True)    
    def put(self, role_id):
        data = {}
        data['description'] = request.json['description']
        data['name'] = request.json['name']
       
        role = Role.objects.get_or_404(id=role_id)
        role.update(
            **data
        )

        return marshal(role, role_fields)

    @roles_required(["superuser",])
    def delete(self, role_id):
        role = Role.objects.get_or_404(id=role_id)
        role.delete()
        return '', 204
    

