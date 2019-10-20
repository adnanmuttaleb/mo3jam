from datetime import datetime
import logging
import pytest


LOGGER = logging.getLogger(__name__)

@pytest.mark.parametrize(
    'term', 
    [
        'sync', 
        pytest.param('aaaaaa', marks=pytest.mark.xfail)
    ]
)
def test_terminologies_post(test_client, user, domain, term):
    reponse = test_client.post(
        '/api/v1.0/terminologies', 
        json={
            'term': term,
            'creator': user.id,
            'domain': domain.id,
        },
        follow_redirects=True
    )

    assert reponse.status_code == 200

def test_terminologies_put(test_client, terminology, domain):
    reponse = test_client.put(
        '/api/v1.0/terminologies/{!s}'.format(terminology.id.hex), 
        json={
            'domain': domain.id,
        },
        follow_redirects=True,
    )

    assert reponse.status_code == 200



