import uuid

from flask import request
from flask_restplus import Resource, Namespace

from mo3jam.models import Role
from mo3jam.schemas import RoleSchema
from mo3jam.utils import get_pagination_urls, roles_accepted, roles_required, get_json_schema

role_ns = Namespace('roles', description='Roles API',)
role_fields = role_ns.schema_model(
    'Role',
    get_json_schema(RoleSchema)
)


@role_ns.route('/')
class RoleList(Resource):
    def __init__(self, *args, **kwargs):
        super(RoleList, self).__init__(*args, **kwargs)
        self.schema = RoleSchema()
    
    def get(self):
        return self.schema.dump(Role.objects, many=True)
    
    @role_ns.expect(role_fields)
    def post(self):
        data = self.schema.load(request.get_json())
        role = Role(id=uuid.uuid4(), **data)
        role.save()

        return self.schema.dump(role)


@role_ns.route('/<string:role_id>')
@role_ns.doc(params={
    "role_id": 'ID of role to be updated.'
})
class RoleDetails(Resource):
    def __init__(self, *args, **kwargs):
        super(RoleDetails, self).__init__(*args, **kwargs)
        self.schema = RoleSchema()
   
    def get(self, role_id):
        return self.schema.dump(Role.objects.get_or_404(id=role_id))
    
    @role_ns.expect(role_fields)
    def put(self, role_id):
        data = self.schema.load(request.get_json())
        role = Role.objects.get_or_404(id=role_id)
        role.update(**data)
        role.reload()
        return self.schema.dump(role)

    def delete(self, role_id):
        role = Role.objects.get_or_404(id=role_id)
        role.delete()
        return '', 204
    

