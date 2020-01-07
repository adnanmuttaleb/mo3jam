from datetime import datetime
import logging

import pytest
from pytest_cases import pytest_parametrize_plus, fixture_ref


LOGGER = logging.getLogger(__name__)

@pytest_parametrize_plus(
    'term,lang,domain,creator', 
    [    
        pytest.param(('sync', 'en', fixture_ref('domain'), fixture_ref('user')), marks=pytest.mark.xfail),
        ('async', 'en', None, fixture_ref('user')),
        ('meta', 'en', fixture_ref('domain'), None),
    ]
)
def test_terminologies_post(test_client, term, lang, domain, creator):
    reponse = test_client.post(
        '/api/v1.0/terminologies', 
        json={
            'term': term,
            'language': lang,   
            'domain': domain,
            'creator': creator,
        },
        follow_redirects=True
    )

    assert reponse.status_code == 200

# def test_terminologies_put(test_client, terminology, domain, user):
#     reponse = test_client.put(
#         '/api/v1.0/terminologies/{!s}'.format(terminology.id.hex), 
#         json={
#             'creator':   
#             'domain': domain,
#         },
#         follow_redirects=True,
#     )

#     assert reponse.status_code == 200

# def test_translations_post(test_client, terminology, translation):
#     reponse = test_client.post(
#         'api/v1.0/terminologies/{!s}/translations'.format(terminology.id.hex),
#         json={
#             'value': translation.value,
#             'creator': translation.creator,
#             'author': translation.author,
#             'notes': translation.notes

#         },
#         follow_redirects=True,
#     )

#     assert reponse.status_code == 200


# def test_translations_put(test_client, terminology):

#     terminology_obj = TerminologyView.objects.get(id=terminology.id)
#     translation_obj = terminology_obj.translations[0]
#     reponse = test_client.put(
#         'api/v1.0/terminologies/{!s}/translations/{!s}'.format(
#             terminology.id.hex, 
#             translation_obj.id.hex
#         ),
#         json={
#             'value': translation.value,
#             'creator': translation.creator,
#             'author': translation.author,
#             'notes': translation.notes

#         },
#         follow_redirects=True,
#     )

#     assert reponse.status_code == 200


