import pytest
from tests.test_contact_publication_precision import contacts


@pytest.mark.parametrize('local',"contact kontor firma firmapost mail epost e-post hello hi enquiries inquiries orders order booking reservasjon bestilling resepsjon drift teknisk marked marketing jobb jobs career karriere hr personal innkjop purchase accounts regnskap lonn bilag invoice".split())
def test_extended_role_locals_publish(local):
    address=local+'@example.no'
    assert address in contacts(f'<footer><a href="mailto:{address}">Email</a></footer>')


@pytest.mark.parametrize('local',['kari.nordmann','k.nordmann','karinordmann','per.eirik','anny'])
def test_extension_does_not_accept_personal_emails(local):
    address=local+'@example.no'
    assert address not in contacts(f'<div class="staff"><h3>Kari Nordmann</h3><a href="mailto:{address}">Email</a></div>')
