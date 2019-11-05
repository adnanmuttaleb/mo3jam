import functools
import json
import uuid
import six

from passlib.hash import pbkdf2_sha256 as sha256
from mongoengine import signals
from eventsourcing.domain.model.decorators import subscribe_to

from . import mongo_db
from .search import add_to_index, remove_from_index, query_index, bulk_add_to_index
from .entities import Terminology, Domain


ROLES = (
    ('superuser', 'Super User'),
    ('editor', 'Editor'),
    ('moderator', 'Moderator'),
)


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


class DictionaryView(mongo_db.Document,):
    __searchable__ = ['author', 'title',]
    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    author = mongo_db.StringField(max_length=400,)
    title = mongo_db.StringField(max_length=200, required=True)
    publication_date = mongo_db.DateTimeField()

class Role(mongo_db.Document):
    name = mongo_db.StringField(max_length=80, unique=True)
    description = mongo_db.StringField(max_length=255)


@register_signals
class UserView(mongo_db.Document, SearchableMixin):
    __indexname__ = 'users'
    __searchable__ = ['username']
  
    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    username = mongo_db.StringField(max_length=30, required=True, unique=True)
    email = mongo_db.EmailField(required=True, unique=True)
    password = mongo_db.StringField(max_length=255)
    active = mongo_db.BooleanField(default=True)
    confirmed_at = mongo_db.DateTimeField()
    roles = mongo_db.ListField(mongo_db.StringField(choices=ROLES), default=[])

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)    
    
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class TranslationView(mongo_db.EmbeddedDocument):
    __searchable__ = ['value']

    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    value = mongo_db.StringField(max_length=200, required=True)
    author = mongo_db.GenericReferenceField()
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField()
    notes = mongo_db.StringField(max_length=2000, required=True)


@register_signals
class TerminologyView(mongo_db.Document, SearchableMixin):
    __indexname__ = 'terminologies'
    __searchable__ = ['term', 'creation_date', 'creator', 'translations', 'language', 'notes']

    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    term = mongo_db.StringField(max_length=300, required=False, unique=True, sparse=True)
    language = mongo_db.StringField(max_length=30, required=False, default='en')
    translations = mongo_db.EmbeddedDocumentListField(TranslationView, required=False)
    notes = mongo_db.ListField(mongo_db.StringField(max_length=2000), required=False)
    domain = mongo_db.ReferenceField('DomainView', required=True)
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField()

@register_signals
class DomainView(mongo_db.Document, SearchableMixin):
    __indexname__ = 'domains'
    __searchable__ = ['name', 'creation_date', 'creator', 'description']
    
    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    name = mongo_db.StringField(max_length=200)
    description = mongo_db.StringField(max_length=2000)
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField()


@subscribe_to(
    Terminology.Created, 
    Terminology.TranslationAdded, 
    Terminology.TranslationDeleted,
    Terminology.TranslationUpdated,
    Terminology.DomainSet, 
    Terminology.LanguageChanged, 
    Terminology.Discarded,
    Domain.Created,
    Domain.NameChanged,
    Domain.DescriptionChanged,
    Domain.Discarded
)
@functools.singledispatch
def consume(event):
    raise TypeError('Unknown Event Type: {}'.format(type(event)))

@consume.register(Terminology.Created)
def _(event):

    terminology = TerminologyView(
        id=event.originator_id, 
        term=event.term,
        domain=event.domain,
        language=event.language,
        creator=event.creator,
        creation_date=event.creation_date,
        
    )

    terminology.save()

@consume.register(Terminology.DomainSet)
def _(event):
    terminology = TerminologyView.objects.get(id=event.originator_id)
    domain = DomainView.objects.get(id=event.domain)
    terminology.update(domain=domain)

@consume.register(Terminology.LanguageChanged)
def _(event):
    terminology = TerminologyView.objects.get(id=event.originator_id)
    terminology.update(language=event.language)

@consume.register(Terminology.TranslationAdded,)
def _(event):

    trans_id = event.translation.id
    value = event.translation.value
    creator = UserView.objects(id=event.translation.creator).first()
    author = DictionaryView.objects(id=event.translation.author).first() or UserView.objects(id=event.translation.author).first()
    creation_date = event.translation.creation_date
    notes = event.translation.notes

    translation = TranslationView(
        id=trans_id,
        value=value, 
        creator=creator, 
        author=author, 
        creation_date=creation_date,
        notes=notes
    )

    TerminologyView.objects(id=event.originator_id).update_one(
        push__translations=translation,
    )

@consume.register(Terminology.TranslationDeleted,)
def _(event):
    try:
        trans_id = uuid.UUID(event.translation_id)
    except Exception:
        trans_id = event.translation_id

    TerminologyView.objects(id=event.originator_id).update_one(
        pull__translations=TerminologyView.objects(
            id=event.originator_id
        ).first().translations.get(id=trans_id)
    )

@consume.register(Terminology.TranslationUpdated,)
def _(event):
    try:
        trans_id = uuid.UUID(event.translation_id)
    except Exception:
        trans_id = event.translation_id
    
    update_data = dict(event.data)
    update_data['author'] = DictionaryView.objects(id=update_data['author']).first() or \
                            UserView.objects(id=update_data['author']).first()

    terminology = TerminologyView.objects.get(id=event.originator_id)
    terminology.translations.filter(id=trans_id).update(
        **update_data,     
    )
    terminology.save()


@consume.register(Terminology.Discarded)
def _(event):
    terminology = TerminologyView.objects(id=event.originator_id).first()
    terminology.delete()


@consume.register(Domain.Created)
def _(event):
    domain = DomainView(
        id=event.originator_id,
        name=event.name,
        description=event.description,
        creator=event.creator,
        creation_date=event.creation_date
    )

    domain.save()

@consume.register(Domain.NameChanged)
def _(event):
    DomainView.objects(id=event.originator_id).update_one(name=event.name)
    

@consume.register(Domain.DescriptionChanged)
def _(event):
    DomainView.objects(id=event.originator_id).update_one(description=event.description)


@consume.register(Domain.Discarded)
def _(event):
    domain = DomainView.objects(id=event.originator_id).first()
    domain.delete()
    
