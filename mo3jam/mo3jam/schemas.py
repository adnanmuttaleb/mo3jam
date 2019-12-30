import uuid

from marshmallow import Schema, fields, validates, pre_load, post_load, pre_dump, ValidationError
from mo3jam.models import DomainView, Source, GenericUser, UserView

class RoleSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['name'] =  in_data['name'].lower().strip()
        in_data['description'] =  in_data['description'].lower().strip()
        return in_data


class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    password = fields.String(load_only=True)
    username = fields.String(required=True)
    active = fields.Boolean(missing=False)
    confirmed_at = fields.DateTime(dump_only=True)
    email = fields.Email()
    roles = fields.List(fields.UUID())


class UnRegisteredUserSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email()


class TranslationSchema(Schema):
    id = fields.UUID(dump_only=True)
    creation_date = fields.DateTime(dump_only=True)
    value = fields.String(required=True)
    notes = fields.String()
    creator = fields.UUID(required=True)
    author = fields.UUID(missing=None)
    source = fields.UUID(missing=None)

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['value'] = in_data['value'].lower().strip()
        in_data['notes'] = in_data['notes'].lower().strip()
        return in_data

    @post_load
    def postload(self, in_data, **kwargs):
        in_data['creator'] = UserView.objects.get(id=in_data['creator'])
        if in_data['author']: in_data['author'] = GenericUser.objects.get(id=in_data['author'])
        if in_data['source']: in_data['source'] = Source.objects.get(id=in_data['source'])
        return in_data
    
    @pre_dump
    def predump(self, in_data, **kwargs):
        if in_data['author']: in_data['author'] = in_data['author'].id
        if in_data['source']: in_data['source'] = in_data['source'].id   
        in_data['creator'] = in_data['creator'].id
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
            if value:
                assert GenericUser.objects.get(id=value)
        except AssertionError:
            raise ValidationError("Author does not Exist!")

    @validates('source')
    def validate_source(self, value):
        try: 
            if value:
                assert Source.objects.get(id=value)
        except AssertionError:
            raise ValidationError("Source does not Exist!")


class NoteSchema(Schema):
    id = fields.UUID(dump_only=True)
    creation_date = fields.DateTime(dump_only=True)
    value = fields.String(required=True)
    creator = fields.UUID(required=True)

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['value'] = in_data['value'].lower().strip()
        return in_data

    @post_load
    def postload(self, in_data, **kwargs):
        in_data['creator'] = UserView.objects.get(id=in_data['creator'])
        return in_data

    @pre_dump
    def predump(self, in_data, **kwargs): 
        in_data['creator'] = in_data['creator'].id
        return in_data

    @validates('creator')
    def validate_creator(self, value):
        try:
            assert UserView.objects.get(id=value)
        except AssertionError:
            raise ValidationError("User does not Exist!")


class TerminologySchema(Schema):
    id = fields.UUID(dump_only=True)
    creation_date = fields.DateTime(dump_only=True)
    term = fields.String(required=True)
    language = fields.String(required=True)
    domain = fields.UUID(required=True)
    creator = fields.UUID(required=True)
    translations = fields.List(fields.Nested(TranslationSchema), load_only=True)
    notes = fields.List(fields.Nested(NoteSchema), load_only=True)

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
    

class DomainSchema(Schema):
    id = fields.UUID(dump_only=True)
    creation_date = fields.DateTime(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    creator = fields.UUID(required=True)

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['name'] = in_data['name'].lower().strip()
        in_data['description'] = in_data['description'].lower().strip()
        return in_data

    @pre_dump
    def predump(self, in_data, **kwargs):  
        in_data['creator'] = in_data['creator'].id
        return in_data
    
    @validates('creator')
    def validate_creator(self, value):
        try:
            assert UserView.objects.get(id=value)
        except AssertionError:
            raise ValidationError("User does not Exist!")


class DictionarySchema(Schema):
    id = fields.UUID(dump_only=True)
    publication_date = fields.Date(format='%d-%m-%Y', required=True)
    title = fields.String(required=True)
    author = fields.List(fields.String(), required=True)

    class Meta:
        fields = ('id', 'title', 'author', 'publication_date')

    @pre_load
    def preload(self, in_data, **kwargs):
        in_data['title'] = in_data['title'].lower().strip()
        in_data['author'] = [author.lower().strip() for author in in_data['author']]
        return in_data



