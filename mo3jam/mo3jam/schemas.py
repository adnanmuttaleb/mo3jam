import uuid

from marshmallow import Schema, fields, validates, pre_load, pre_dump, ValidationError
from mo3jam.models import DomainView, UserView

class RoleSchema(Schema):
    id = fields.UUID(dump_only=True)
    class Meta:
        fields = ('id', 'name', 'description')

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['name'] =  in_data['name'].lower().strip()
        in_data['description'] =  in_data['description'].lower().strip()
        return in_data


class TerminologySchema(Schema):
    id = fields.UUID(dump_only=True)
    creation_date = fields.DateTime(dump_only=True)
    domain = fields.UUID(required=True)
    creator = fields.UUID(required=True)
    
    class Meta:
        fields = ('id', 'term', 'language', 'domain', 'creator', 'creation_date')

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['term'] =  in_data['term'].lower().strip()
        return in_data

    @pre_dump
    def predump(self, in_data, **kwargs):
        in_data['domain'] = in_data['domain'].id
        in_data['creator'] = in_data['creator'].id
        return in_data

    @validates('domain')
    def validate_domain(self, value):
        try:
            assert DomainView.objects.get(id=value)
        except AssertionError:
            raise ValidationError("Domain does not Exist!")

    @validates('creator')
    def validate_creator(self, value):
        try:
            assert UserView.objects.get(id=value)
        except AssertionError:
            raise ValidationError("User does not Exist!")


class TranslationSchema(Schema):
    id = fields.UUID(dump_only=True)
    creation_date = fields.DateTime(dump_only=True)
    creator = fields.UUID()
    author = fields.UUID()

    class Meta:
        fields = ('id', 'value', 'notes', 'creator', 'author', 'creation_date')

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['value'] = in_data['value'].lower().strip()
        in_data['notes'] = in_data['notes'].lower().strip()
        return in_data

    @validates('creator')
    def validate_creator(self, value):
        try:
            assert UserView.objects.get(id=value)
        except AssertionError:
            raise ValidationError("User does not Exist!")
        
    @validates('author')
    def validate_author(self, value):
        try: 
            assert Source.objects.get(id=value) 
        except AssertionError:
            raise ValidationError("Source does not Exist!")
    
    #to be done whether  user is also author   


