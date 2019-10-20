import uuid

from flask import request, jsonify, abort, current_app
from flask_restplus import Resource, fields

from .. import api
from ..models import UserView

user_ns = api.namespace('users', description='Users API',)
user_fields = user_ns.model(
    'User',
    {
        'username': fields.String,
        'email': fields.String,
    }
)

@user_ns.route('/')
class UserList(Resource):

    def get(self):
        queryset = UserView.objects
        return jsonify(queryset)
    
    @user_ns.expect(user_fields, validate=True)    
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

    def get(self, user_id):
        user = UserView.objects.get_or_404(id=user_id)
        return jsonify(user)
    
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
    

