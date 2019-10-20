import pytest
from ...models import TerminologyView, DomainView

@pytest.mark.parametrize(
    'domain',
    [
        ('New Domain', 'tech field')
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    'terminology',
    [
        'schema'
    ],
    indirect=True,
)
def test_terminology_domain_changed(test_client, terminology, domain):
    terminology.set_domain(domain.id)
    assert TerminologyView.objects.get(id=terminology.id).domain ==  DomainView.objects.get(id=domain.id)
