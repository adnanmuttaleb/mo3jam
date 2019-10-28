import uuid

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource
from flask_restplus.marshalling import marshal, marshal_with

from .. import api
from ..models import UserView
from .serializers import user_fields
from .utils import get_pagination_urls

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

        username = request.json['username']
        email = request.json['email']

        user = UserView(id=uuid.uuid4(), username=username, email=email)
        user.save()

        return jsonify(user)


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

        username = request.json['username']
        email = request.json['email']
        
        user = UserView.objects.get_or_404(id=user_id)
        user.update(
            username=username, 
            email=email
        )

        return '', 200

    def delete(self, user_id):
        user = UserView.objects.get_or_404(id=user_id)
        user.delete()
        return '', 204
    

