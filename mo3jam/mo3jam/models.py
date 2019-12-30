import functools
import uuid
import six

from datetime import datetime

from passlib.hash import pbkdf2_sha256 as sha256
from mongoengine import signals
from eventsourcing.domain.model.decorators import subscribe_to

from . import mongo_db
from .search import add_to_index, remove_from_index, query_index, bulk_add_to_index
from .entities import Terminology, Domain


class SearchableMixin():

    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__indexname__, expression, page, per_page)
        queryset = cls.objects(id__in=ids)
        return queryset, total

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        add_to_index(sender.__indexname__, document)

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        remove_from_index(sender.__indexname__, document)

    @classmethod
    def reindex(cls):
        bulk_add_to_index(cls.__indexname__, cls.objects)

    def to_representation(self):
        return self.__class__._to_representation(self)
    
    @classmethod
    def _to_representation(cls, obj):
        if not hasattr(obj, '__searchable__'):
            try:
                if isinstance(obj, six.string_types):
                    raise Exception
                return [cls._to_representation(x) for x in obj]
            except Exception as e:
                return obj

        representation = {}
        for key in obj.__searchable__:
            representation[key] = cls._to_representation(obj[key])

        return representation


def register_signals(cls):
    signals.post_save.connect(cls.post_save, sender=cls)
    signals.post_delete.connect(cls.post_delete, sender=cls)
    return cls


class Source(mongo_db.Document):
    id = mongo_db.UUIDField(primary_key=True)
    meta = {
        'allow_inheritance': True
    }

class DictionaryView(Source):
    __searchable__ = ['author', 'title',]
    id = mongo_db.UUIDField(primary_key=True)
    author = mongo_db.ListField(mongo_db.StringField(max_length=400,))
    title = mongo_db.StringField(max_length=200, required=True)
    publication_date = mongo_db.DateTimeField()


class Role(mongo_db.Document):
    id = mongo_db.UUIDField(primary_key=True)
    name = mongo_db.StringField(max_length=80, unique=True)
    description = mongo_db.StringField(max_length=255)


class GenericUser(mongo_db.Document):
    id = mongo_db.UUIDField(primary_key=True)
    meta = {
        'allow_inheritance': True
    }

class UnRegisteredUser(GenericUser):
    id = mongo_db.UUIDField(primary_key=True)
    name = mongo_db.StringField(max_length=30, required=True, unique=True)
    email = mongo_db.EmailField(required=True, unique=True)


@register_signals
class UserView(GenericUser, SearchableMixin):
    __indexname__ = 'users'
    __searchable__ = ['username']
    
    id = mongo_db.UUIDField(primary_key=True)
    username = mongo_db.StringField(max_length=30, required=True, unique=True)
    email = mongo_db.EmailField(required=True, unique=True)
    password = mongo_db.StringField(max_length=255)
    active = mongo_db.BooleanField(default=False)
    confirmed_at = mongo_db.DateTimeField()
    roles = mongo_db.ListField(mongo_db.ReferenceField(Role))

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)    
    
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class TranslationView(mongo_db.EmbeddedDocument):
    __searchable__ = ['value']

    id = mongo_db.UUIDField(primary_key=True)
    value = mongo_db.StringField(max_length=50, required=True)
    creator = mongo_db.ReferenceField(UserView, required=True,)
    author = mongo_db.ReferenceField(GenericUser)
    source = mongo_db.ReferenceField(Source)
    creation_date = mongo_db.DateTimeField(default=datetime.now)
    notes = mongo_db.StringField(max_length=2000)


class Note(mongo_db.EmbeddedDocument):
    id = mongo_db.UUIDField(primary_key=True)
    value = mongo_db.StringField(max_length=500, required=True)
    creation_date = mongo_db.DateTimeField(default=datetime.now)
    creator = mongo_db.ReferenceField(UserView, required=True)


@register_signals
class TerminologyView(mongo_db.Document, SearchableMixin):
    __indexname__ = 'terminologies'
    __searchable__ = ['term', 'creation_date', 'creator', 'translations', 'language', 'notes']

    id = mongo_db.UUIDField(primary_key=True)
    term = mongo_db.StringField(max_length=300, required=False, unique=True, sparse=True)
    language = mongo_db.StringField(max_length=30, required=False, default='en')
    translations = mongo_db.EmbeddedDocumentListField(TranslationView, required=False)
    notes = mongo_db.EmbeddedDocumentListField(Note, required=False)
    domain = mongo_db.ReferenceField('DomainView', required=True)
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField(default=datetime.now)

    def add_translation(self, value, creator, notes="", source=None, author=None):
        if source == None and author == None:
            raise Exception("A translation object must has either a source or an author") 

        translation = TranslationView(
            id=uuid.uuid4(),
            value=value,
            creator=creator, 
            notes=notes,
            source=source,
            author=author,
        )
        self.update(
            push__translations=translation,
        )
        return translation

    def delete_translation(self, id):
        self.update(
            pull__translations=self.translations.get(id=id)
        )

    def update_translation(self, id, data):
        self.translations.filter(id=id).update(
            **data,     
        )
        self.save()

    def change_language(self, language):
        self.update(language=language)
    
    def change_domain(self, domain):
        self.update(domain=domain)
    
    def add_note(self, value, creator):
        note = Note(
            id=uuid.uuid4(),
            value=value,
            creator=creator, 
        )
        self.update(push__notes=note)
        return note
    
    def edit_note(self, id, value, **kwargs):
        self.notes.filter(id=id).update(
            value=value,     
        )
        self.save()
    
    def delete_note(self, id):
        self.update(pull__notes=self.notes.get(id=id))


@register_signals
class DomainView(mongo_db.Document, SearchableMixin):
    __indexname__ = 'domains'
    __searchable__ = ['name', 'creation_date', 'creator', 'description']
    
    id = mongo_db.UUIDField(primary_key=True)
    name = mongo_db.StringField(max_length=200)
    description = mongo_db.StringField(max_length=2000)
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField(default=datetime.now)

    def edit_name(self, name):
        self.update(name=name)

    def edit_description(self, description):
        self.update(description=description)