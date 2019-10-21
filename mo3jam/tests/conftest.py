from datetime import datetime
import uuid

import pytest

from .. import create_app, db
from ..models import UserView, DictionaryView, DomainView
from ..entities import Terminology, Translation, Domain

@pytest.fixture(scope='module')
def test_client():
 
    test_conf = {
        'WTF_CSRF_ENABLED': False,
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/mo3jam_test.db',
        'MONGODB_SETTINGS': {
            'db': 'mo3jam_test',
            'host': 'mongomock://localhost'
        }
    }

    app = create_app(test_conf)
    client = app.test_client()
    
    ctx = app.app_context()
    ctx.push()

    db.create_all()

    yield client

    ctx.pop()


@pytest.fixture(scope='module')
def user(test_client):
    user = UserView(id=uuid.uuid4(), username='adnan', email='adnan@ex.com')
    user.save()
    return user

@pytest.fixture(scope='module')
def dictionary(test_client):
    dictionary  =  DictionaryView(
        id=uuid.uuid4(),
        title='The Dictionary', 
        author='Adnan Mut', 
        publication_date=datetime.now()
    )
    dictionary.save()
    return dictionary

@pytest.fixture(params=[('CS', 'IT domain')], scope='module')
def domain(test_client, request, user):

    domain = Domain.__create__(
        creator=user.id,
        creation_date=datetime.now(),
        name=request.param[0],
        description=request.param[1],
    )
    
    domain.__save__()
    return domain


@pytest.fixture(params=['hybrid'], scope='module')
def terminology(test_client, request, user, domain):
    term = Terminology.__create__(
        term=request.param,
        domain=domain.id,
        creator=user.id,
        creation_date=datetime.now(),
    )

    term.__save__()
    return term


@pytest.fixture(params=[
    'some translation',
    '',
])
def translation(request, user, dictionary, ):
    return Translation(
        id=None,
        value=request.param,
        creator=user.id,
        author= dictionary.id,
        creation_date=None,
        notes='Some Note'
    )
