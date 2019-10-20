import functools
import json
import uuid

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

class DictionaryView(mongo_db.Document):
    __indexname__ = 'dictionaries'
    __searchable__ = ['author', 'title', 'publication_date']
    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    author = mongo_db.StringField(max_length=400,)
    title = mongo_db.StringField(max_length=200, required=True)
    publication_date = mongo_db.DateTimeField()

class UserView(mongo_db.Document):
    __indexname__ = 'users'
    __searchable__ = ['username', 'email']
    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    username = mongo_db.StringField(max_length=30, required=True)
    email = mongo_db.EmailField(required=True)

class TranslationView(mongo_db.EmbeddedDocument):
    __searchable__ = ['value']

    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    value = mongo_db.StringField(max_length=200, required=True)
    author = mongo_db.GenericReferenceField()
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField()
    notes = mongo_db.StringField(max_length=2000, required=True)

class TerminologyView(mongo_db.Document, SearchableMixin):
    __indexname__ = 'terminologies'
    __searchable__ = ['id', 'term', 'translations', 'notes']

    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    term = mongo_db.StringField(max_length=300, required=False, unique=True, sparse=True)
    translations = mongo_db.EmbeddedDocumentListField(TranslationView, required=False)
    notes = mongo_db.ListField(mongo_db.StringField(max_length=2000), required=False)
    domain = mongo_db.ReferenceField('DomainView', required=True)
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField()


    def to_dict(self):
        as_json = super(TerminologyView, self).to_json()
        as_dict = json.loads(as_json)
        del as_dict['_id']
        return as_dict


class DomainView(mongo_db.Document, SearchableMixin):
    __indexname__ = 'domains'
    __searchable__ = ['name', 'creation_date', 'creator', 'description']
    
    id = mongo_db.UUIDField(max_length=300, required=True, primary_key=True)
    name = mongo_db.StringField(max_length=200)
    description = mongo_db.StringField(max_length=2000)
    creator = mongo_db.ReferenceField(UserView)
    creation_date = mongo_db.DateTimeField()
    terminologies =  mongo_db.ListField(mongo_db.ReferenceField(TerminologyView))



@subscribe_to(
    Terminology.Created, 
    Terminology.TranslationAdded, 
    Terminology.TranslationDeleted,
    Terminology.TranslationUpdated,
    Terminology.DomainSet, 
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
        creator=event.creator,
        creation_date=event.creation_date,
        
    )
    terminology.save()

@consume.register(Terminology.DomainSet)
def _(event):
    terminology = TerminologyView.objects.get(id=event.originator_id)
    try:
        terminology.domain.update(
            pull__terminologies=terminology
        )
    except Exception:
        pass

    domain = DomainView.objects.get(id=event.domain)
    terminology.update(domain=domain)
    domain.update(
        push__terminologies=terminology
    )

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
        trans_id = uuid.UUID(event.modified_translation.id)
    except Exception:
        trans_id = event.modified_translation.id
    
    TerminologyView.objects(
        id=event.originator_id, 
        translations__id=trans_id
    ).update(
            set__translations__S__value=event.modified_translation.value ,
            set__translations__S__notes=event.modified_translation.notes ,
            set__translations__S__author=DictionaryView.objects(id=event.modified_translation.author).first() or \
                                        UserView.objects(id=event.modified_translation.author).first()
    )      


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
    


signals.post_save.connect(TerminologyView.post_save, sender=TerminologyView)
signals.post_delete.connect(TerminologyView.post_delete, sender=TerminologyView)