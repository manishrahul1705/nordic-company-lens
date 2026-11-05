from signalpost.web.entity_scope import group_site_has_own_proof, registered_contact_values
from signalpost.web.html import Page
from types import SimpleNamespace


def test_group_site_requires_own_orgnr_or_exact_name_and_registry_contact():
    org='925310492'
    name='CNC NORWAY AS'
    contact='post@cncnorwayas.no'
    own_id=Page(b'<footer>Group page. Org.nr 925310492</footer>','https://cncnorwayas.no/contact')
    exact_and_contact=Page(b'<h1>CNC NORWAY AS</h1><p>post@cncnorwayas.no</p>',
                           'https://cncnorwayas.no/contact')
    name_only=Page(b'<h1>CNC NORWAY AS</h1><p>Other contact</p>',
                   'https://cncnorwayas.no/contact')
    assert group_site_has_own_proof([own_id],org,name,[contact])
    assert group_site_has_own_proof([exact_and_contact],org,name,[contact])
    assert not group_site_has_own_proof([name_only],org,name,[contact])


def test_group_site_contacts_come_from_registry_identity_claims():
    claims=[SimpleNamespace(field='identity.registered_email',value='registry@example.no',
            availability='available',evidence_ids=['official']),
            SimpleNamespace(field='contact.email.current',value='current@example.no',
            availability='available',evidence_ids=['website'])]
    evidence={'official':SimpleNamespace(source_class='official_registry'),
              'website':SimpleNamespace(source_class='company_owned')}
    assert registered_contact_values(claims,evidence)==['registry@example.no']
