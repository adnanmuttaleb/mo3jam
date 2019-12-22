import uuid
from functools import wraps

from werkzeug.urls import url_encode
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims, get_current_user

def roles_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_claims()

            if all([role in claims["roles"] for role in roles]):
                return func(*args, **kwargs)
            else:
                return {'msg': 'Not Authorized'}, 403
        
        return wrapper
    
    return decorator


def roles_accepted(roles):
    def decorator(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_claims()

            if any([role in claims["roles"] for role in roles]):
                return func(*args, **kwargs)
            else:
                return {'msg': 'Not Authorized'}, 403
        
        return wrapper
    
    return decorator


def get_pagination_urls(queryset, page, page_size):
    pagination = {}
    
    if queryset: 
        args = request.args.copy()
        for key, value in {'page': page+1, 'page_size':page_size}.items():
            args[key] = value

        pagination['next'] = '{}?{}'.format(
            request.path,
            url_encode(args)  
        )
   
    if page > 1:
        args = request.args.copy()
        for key, value in {'page': page-1, 'page_size':page_size}.items():
            args[key] = value
        
        pagination['previous'] = '{}?{}'.format(
            request.path,
            url_encode(args)
        )
    
    return pagination
    
