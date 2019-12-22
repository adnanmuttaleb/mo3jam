from flask import jsonify, request, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
    get_raw_jwt
)
from flask_restplus import Resource, Namespace
from ..models import UserView

auth_ns = Namespace('auth', description='Authentication API',)
blacklist = set()

@auth_ns.route('/login', methods=['POST'])
class Login(Resource):
  
    def post(self):
        if not request.is_json:
            return {"msg": "Missing JSON in request"}, 400

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            return {"msg": "Missing username parameter"}, 400
        if not password:
            return {"msg": "Missing password parameter"}, 400
    
        try: 
            
            user = UserView.objects(username=username).first()
            if not UserView.verify_hash(password, user.password):
                return {"msg": "This password is incorrrect"}, 401

            tokens = {
                'access_token': create_access_token(identity=user.id),
                'refresh_token': create_refresh_token(identity=user.id)
            }

            return tokens, 200
   
        except Exception as e:
            return {"msg": "This username does not exist"}, 401


@auth_ns.route('/refresh', methods=['POST'])
class Refresh(Resource):
    
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        tokens = {
            'access_token': create_access_token(identity=current_user)
        }
        
        return tokens, 200


@auth_ns.route('/logout', methods=['DELETE'])
class RevokeToken(Resource):

    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return {'msg': 'Access token has been revoked'}, 200


@auth_ns.route('/logout/refresh', methods=['DELETE'])
class RevokeRefreshToken(Resource):
    @jwt_refresh_token_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return {'msg': 'Refresh token has been revoked'}, 200




