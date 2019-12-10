import uuid

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource
from flask_restplus.marshalling import marshal, marshal_with
from flask_jwt_extended import  jwt_required, get_jwt_identity, verify_jwt_in_request

from .. import api
from ..models import UserView, Role
from .serializers import user_fields
from .utils import get_pagination_urls, roles_accepted, roles_required

user_ns = api.namespace('users', description='Users API',)

@user_ns.route('/')
class UserList(Resource):
    
    def get(self):
        response = {}
        page = request.args.get('page', 1)
        page_size = request.args.get('page_size', current_app.config['RESULTS_PER_PAGE']) 
        queryset = list(UserView.objects[(page-1)*page_size:page*page_size])
        response['users'] = marshal(
            queryset,
            user_fields,
        )
        response.update(get_pagination_urls(queryset, page, page_size))
        return response
    
    @user_ns.expect(user_fields)    
    def post(self):

        data = {}
        data['username'] = request.json['username'].lower()
        data['email'] = request.json['email'].lower()
        data["password"] = UserView.generate_hash(request.json["password"])
        
        roles = request.json.get("roles", [])
        data["id"] = uuid.uuid4()
        data["roles"] = Role.objects(id__in=roles)
        
        user = UserView(**data)
        user.save()

        return marshal(user, user_fields)


@user_ns.route('/<string:user_id>')
@user_ns.doc(params={
    "user_id": 'ID of user to be updated.'
})
class UserDetails(Resource):
   
    @marshal_with(user_fields)
    def get(self, user_id):
        return UserView.objects.get_or_404(id=user_id)

    @user_ns.expect(user_fields, validate=True)    
    def put(self, user_id):       
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        if uuid.UUID(current_user_id) != uuid.UUID(user_id):
            return {'msg': 'Not Authorized'}, 403

        data = {}
        data['username'] = request.json['username']
        data['email'] = request.json['email']
       
        user = UserView.objects.get_or_404(id=user_id)
        user.update(
            **data
        )

        return marshal(user, user_fields)

    
    def delete(self, user_id):
        user = UserView.objects.get_or_404(id=user_id)
        user.delete()
        return '', 204
    

