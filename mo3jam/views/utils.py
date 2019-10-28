
from werkzeug.urls import url_encode
from flask import request

def get_pagination_urls(queryset, page, page_size):
    pagination = {}
    
    if queryset: 
        args = request.args.copy()
        for key, value in {'page': page+1, 'page_size':page_size}.items():
            args[key] = value

        print(args)
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
    
