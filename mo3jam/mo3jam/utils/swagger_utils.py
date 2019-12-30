from marshmallow_jsonschema import JSONSchema
from flask_restplus import SchemaModel

json_schema = JSONSchema() 

def get_json_schema(schema):
    schema_classname = schema.__name__
    return json_schema.dump(schema())['definitions'][schema_classname]