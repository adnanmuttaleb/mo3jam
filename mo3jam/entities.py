from eventsourcing.domain.model.aggregate import BaseAggregateRoot

class ValueObject():
    
    @property
    def attrs(self):
        return (attr for attr in self.__dict__ if not callable(getattr(self, attr)) and not attr.startswith('__'))

class Translation(ValueObject):

    def __init__(self, id, value, creator, author, creation_date, notes=None):
        self.id = id
        self.value = value
        self.creator = creator
        self.author = author
        self.creation_date = creation_date
        self.notes = notes

class Terminology(BaseAggregateRoot):
    
    def __init__(self, term, domain, creator, creation_date, *args, translations=None, **kwargs):
        super(Terminology, self).__init__(*args, **kwargs)
        self.term = term
        self.domain = domain
        self.creator = creator
        self.creation_date = creation_date
        if not translations:
            self.translations = ()
        else:
            self.translations = translations
    
    class Event(BaseAggregateRoot.Event):
        pass

    class Created(Event, BaseAggregateRoot.Created):
        pass
   
    class Discarded(Event, BaseAggregateRoot.Discarded):
        pass
   
    class DomainSet(Event):
        def mutate(self, obj):
            obj.domain = self.domain  

    class TranslationAdded(Event):
        def mutate(self, obj):
            obj.translations = (*obj.translations, self.translation)   

    class TranslationDeleted(Event):
        def mutate(self, obj):
            obj.translations = tuple(
                trans for trans in obj.translations if trans.id != self.translation_id
            ) 

    class TranslationUpdated(Event):

        def update(self, translation):
            translation.__dict__.update(self.data)
            return translation

        def mutate(self, obj):
            obj.translations = tuple(trans if trans.id != self.translation_id else self.update(trans) for trans in obj.translations)
        
    def add_translation(self, translation):
        self.__trigger_event__(Terminology.TranslationAdded, translation=translation) 
    
    def delete_translation(self, translation_id):
        self.__trigger_event__(Terminology.TranslationDeleted, translation_id=translation_id) 

    def update_translation(self, translation_id, data):
        self.__trigger_event__(
            Terminology.TranslationUpdated, 
            translation_id=translation_id,
            data=data,
        ) 
    
    def set_domain(self, domain):
        self.__trigger_event__(Terminology.DomainSet, domain=domain)
    

class Domain(BaseAggregateRoot):

    def __init__(self, name, creator, creation_date, *args, description=None, **kwargs):
        super(Domain, self).__init__(*args, **kwargs)
        self.name = name
        self.creator = creator
        self.creation_date = creation_date
        self.description = description
    

    class Event(BaseAggregateRoot.Event):
        pass

    class Created(Event, BaseAggregateRoot.Created):
        pass
   
    class Discarded(Event, BaseAggregateRoot.Discarded):
        pass

    class NameChanged(Event):
        def mutate(self, obj):
            obj.name = self.name
    
    class DescriptionChanged(Event):
        def mutate(self, obj):
            obj.description = self.description
    
    def edit_name(self, new_name):
        self.__trigger_event__(Domain.NameChanged, name=new_name)
    
    def edit_description(self, new_description):
        self.__trigger_event__(Domain.DescriptionChanged, description=new_description)


