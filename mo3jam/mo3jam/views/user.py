import uuid

from flask import request, current_app
from flask_restplus import Resource, Namespace
from flask_jwt_extended import  jwt_required, get_jwt_identity, verify_jwt_in_request

from mo3jam.models import UserView, Role
from mo3jam.schemas import UserSchema
from mo3jam.utils import get_pagination_urls, roles_accepted, roles_required, get_json_schema

user_ns = Namespace('users', description='Users API',)
user_fields = user_ns.schema_model(
    'User',
    get_json_schema(UserSchema)
)


@user_ns.route('/')
class UserList(Resource):
    schema = UserSchema()

    def get(self):
        response = {}
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset = UserView.objects[(page-1)*page_size:page*page_size]
        response['users'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
        return response
    
    @user_ns.expect(user_fields)
    def post(self):
        data = self.schema.load(request.get_json())
        data["password"] = UserView.generate_hash(data["password"])        
        user = UserView(
            id=uuid.uuid4(),
            **data
        )
        user.save()
        return self.schema.dump(user)


@user_ns.route('/<string:user_id>')
@user_ns.doc(params={
    "user_id": 'ID of user to be updated.'
})
class UserDetails(Resource):
    schema = UserSchema()

    def get(self, user_id):
        return self.schema.dump(UserView.objects.get_or_404(id=user_id))
    
    @user_ns.expect(user_fields)
    def put(self, user_id):       
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        if uuid.UUID(current_user_id) != uuid.UUID(user_id):
            return {'msg': 'Not Authorized'}, 403

        data = self.schema.load(request.get_json())
        user = UserView.objects.get_or_404(id=user_id)
        user.update(
            **data
        )
        user.reload()
        return self.schema.dump(user)

    def delete(self, user_id):
        user = UserView.objects.get_or_404(id=user_id)
        user.delete()
        return '', 204
    

