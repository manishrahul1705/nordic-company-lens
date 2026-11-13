import hashlib
from types import SimpleNamespace
import pytest
from signalpost.sources.extract import Section
from signalpost.web.collector import extract_contacts_and_social
from signalpost.web.html import Page


def contacts(body,**context):
    raw=('<html><body>'+body+'</body></html>').encode()
    response=SimpleNamespace(url='https://example.no/kontakt',body=raw,sha=hashlib.sha256(raw).hexdigest(),retrieved_at='2026-11-12T00:00:00Z')
    page=Page(raw,response.url);section=Section()
    proof=SimpleNamespace(value={'final_url':response.url,'identity_level':'VERIFIED'})
    extract_contacts_and_social(section,'923609016',proof,[(response,page)],{'name':'Example AS',**context})
    for e in section.evidence:assert e.claim_span in raw.decode()
    return {c.value for c in section.claims if c.field.startswith('contact.')}


@pytest.mark.parametrize('local',['post','postmottak','firmapost','info','kontakt','kundeservice','service','salg','sales','booking','bestilling','ordre','regnskap','faktura','admin','office','hello','hei','mail','support','resepsjon','example'])
def test_role_or_company_email_kept(local):
    value=local+'@example.no'
    assert value in contacts(f'<footer><a href="mailto:{value}">Email</a></footer>')


@pytest.mark.parametrize('email',['kari.nordmann@example.no','kari.nordmann@gmail.com'])
def test_exact_registered_email_kept_even_personal_or_free_mail(email):
    assert email in contacts(f'<a href="mailto:{email}">{email}</a>',email=email.upper())


@pytest.mark.parametrize('email',['per.eirik@example.no','p.moltu@example.no','pereirikmoltu@example.no','anny@example.no','info@gmail.com','sales@agency.no'])
def test_staff_unknown_free_mail_and_foreign_email_skipped(email):
    assert email not in contacts(f'<div class="staff"><h3>Per Eirik Moltu</h3><a href="mailto:{email}">{email}</a></div>')


def test_phone_in_staff_card_skipped_but_corporate_footer_kept():
    values=contacts('<section id="contact"><div class="staff"><h3>Kari Nordmann</h3><a href="tel:91234567">Call Kari</a></div></section><footer><a href="tel:22334455">Office</a></footer>')
    assert '+4791234567' not in values and '+4722334455' in values


def test_heading_based_staff_card_without_staff_class_is_skipped():
    assert '+4791234567' not in contacts('<div><h3>Rune Skybak</h3><p>Servicemont\u00f8r <a href="tel:91234567">Mobil</a></p></div>')


def test_registered_phone_kept_even_on_staff_page():
    assert '+4791234567' in contacts('<div class="staff"><a href="tel:91234567">Call</a></div>',mobile='912 34 567')


def test_visible_phone_in_contact_block_kept():
    assert '+4722334455' in contacts('<footer>Tlf: 22 33 44 55</footer>')


@pytest.mark.parametrize('body',[
    '<div class="visittkort"><div class="a-navn">Rune Skybak</div><div class="jobtitle">Technician</div><a href="tel:91234567">Mobile</a></div>',
    '<div class="grid"><h6>Navn</h6><h6>Tittel/Avdeling</h6><div>Kari Nordmann</div><div>Daglig leder</div><a href="tel:91234567">Mobile</a></div>',
    '<section><p>Filip Kumar Karlsen Tamang</p><p>Selger<br><a href="tel:91234567">Mobile</a></p></section>'
])
def test_staff_directory_markup_without_staff_class_is_skipped(body):
    assert '+4791234567' not in contacts(body)


def test_staff_page_does_not_hide_corporate_footer_phone():
    from signalpost.web.contact_policy import Regions,phone_allowed
    page=Page(b'<footer><a href="tel:22334455">Office</a></footer>','https://example.no/tilsette')
    context={'name':'Example AS'}
    assert phone_allowed('+4722334455',page,context,page.links[0].span,Regions(page,context))


@pytest.mark.parametrize('local',['oleolsen','kari.nordmann','g.nordmann'])
def test_personal_pattern_is_not_rescued_by_name_based_domain(local):
    from signalpost.web.contact_policy import email_allowed
    assert not email_allowed(local+'@'+local.replace('.','')+'.no',
        {'name':local.replace('.',' ')+' AS'},local.replace('.','')+'.no',SimpleNamespace(people=set()))


def test_carried_personal_contact_cannot_bypass_publication_policy(tmp_path):
    from signalpost.web.contact_policy import filter_carried_contacts
    from signalpost.sources.blobstore import BlobStore
    from signalpost.models.claim import Claim
    def claim(field,value,carried=False):
        return Claim(field=field,value=value,availability='available',id=field,evidence_ids=['source'],family='website' if field.startswith('contact.') else 'identity',carried_forward=carried,first_observed_at='now',last_observed_at='now')
    private=claim('contact.email.old','kari.nordmann@example.no',True)
    office=claim('contact.email.office','office@example.no',True)
    registered=claim('contact.email.registered','ole.olsen@gmail.com',True)
    identity=claim('identity.registered_email','ole.olsen@gmail.com')
    source=SimpleNamespace(id='source',source_url='https://example.no/kontakt',content_sha256='missing',claim_span='old')
    row=SimpleNamespace(claims=[private,office,registered,identity],evidence=[source],changes=[],profile=SimpleNamespace(values={}))
    filter_carried_contacts(row,BlobStore(tmp_path))
    assert private not in row.claims and office in row.claims and registered in row.claims and identity in row.claims
