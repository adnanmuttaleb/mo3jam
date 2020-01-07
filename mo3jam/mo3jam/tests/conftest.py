from datetime import datetime
import uuid

import pytest

from .. import create_app
from ..models import *

@pytest.fixture(scope='session')
def test_client():
    test_conf = {
        'WTF_CSRF_ENABLED': False,
        'TESTING': True,
        'MONGODB_SETTINGS': {
            'db': 'test',
            'host': 'mongomock://localhost'
        }
    }

    app = create_app(test_conf)
    client = app.test_client()  
    ctx = app.app_context()
    ctx.push()
   
    yield client
    ctx.pop()

@pytest.fixture(scope='session')
def user(test_client):
    user = UserView(id=uuid.uuid4(), username='ramiz', email='ramez@ex.com')
    user.save()
    return user.id

@pytest.fixture(scope='module')
def dictionary(test_client):
    dictionary  =  DictionaryView(
        id=uuid.uuid4(),
        title='The Dictionary', 
        author=['Adnan Mut'], 
        publication_date=datetime.now()
    )
    dictionary.save()
    return dictionary

@pytest.fixture(params=[('cs', 'computer science')], scope='module')
def domain(test_client, request, user):
    domain = DomainView(
        id=uuid.uuid4(),
        creator=user,
        creation_date=datetime.now(),
        name=request.param[0],
        description=request.param[1],
    )
    
    domain.save()
    return domain.id


@pytest.fixture(params=['hybrid'], scope='module')
def terminology(test_client, request, user, domain):
    term = TerminologyView(
        term=request.param,
        language='en',
        domain=domain.id,
        creator=user.id,
    )

    term.save()
    return term


@pytest.fixture(params=[
    'some translation',
    '',
])
def translation(request, terminology, user, dictionary):
    return terminology.add_translation(
        value=request.param,
        creator=user.id,
        source= dictionary.id if dictionary else None,
        author=author.id if author else None,
        notes='Some Note'
    )