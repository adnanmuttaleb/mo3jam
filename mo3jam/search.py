from flask import current_app
from elasticsearch.helpers import bulk

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = model.to_dict()
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)

def bulk_add_to_index(index, models):
    
    if not current_app.elasticsearch:
        return

    # where is the ids??!!     
    payload = ({
        "_index": index, 
        "_type": "_doc", 
        "_id": model.id, 
        "doc": model.to_dict()} for model in models)
   
    bulk(current_app.elasticsearch,  payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [hit['_id'] for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']

