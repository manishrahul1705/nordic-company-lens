import pytest

from signalpost.web.entity_scope import foreign_entity_page
from signalpost.web.html import Page
from tests.test_websites import execute_web, html, OUR, OTHER


@pytest.mark.parametrize('form', ['AB', 'ASA', 'Ltd', 'GmbH', 'Oy'])
def test_zinzino_foreign_entity_page_not_same_brand_proof(form):
    page = Page(html(extra=f'<h1>Zinzino {form}</h1><p>shares@zinzino.com</p>',
                     title=f'Zinzino {form} investor relations').encode(), 'https://zinzino.com/about')
    assert foreign_entity_page(page, OUR, 'Zinzino AS')


def test_different_orgnr_excludes_contacts_and_description(tmp_path, monkeypatch):
    body = html(extra='<h1>Other Company GmbH</h1><a href="mailto:shares@example.no">Email</a>',
                title='Other Company GmbH')
    _, row, _, _ = execute_web(tmp_path, monkeypatch, body)
    assert not any(c['field'].startswith(('contact.', 'website_description.')) for c in row['claims'])


def test_registry_domain_of_non_input_company_is_group_site(tmp_path, monkeypatch):
    bulk = tmp_path / 'registry.csv'
    bulk.write_text('organisasjonsnummer,navn,hjemmeside\n'
                    f'{OUR},Example AS,https://example.no/subsidiary\n'
                    f'{OTHER},Parent AS,https://www.example.no\n', encoding='utf8')
    body = html(extra='<meta name="description" content="Example makes many excellent synthetic products for local clients.">'
                      '<a href="https://facebook.com/example">Example</a>')
    _, row, _, _ = execute_web(tmp_path, monkeypatch, body, bulk=bulk)
    assert any(c['field'] == 'official_website' for c in row['claims'])
    assert row['run']['refresh']['website']['entity_scope']['other_registry_owners'] == [OTHER]
    assert not any(c['field'].startswith(('social_profile.', 'website_description.')) for c in row['claims'])


@pytest.mark.parametrize('form', ['AB', 'ASA', 'Ltd', 'GmbH', 'Oy'])
def test_zinzino_foreign_page_never_attaches_contacts_or_descriptions(tmp_path, monkeypatch, form):
    import tests.test_websites as fixtures
    original = fixtures.entity
    def zinzino(org):
        data = original(org)
        data['navn'] = 'Zinzino AS'
        return data
    monkeypatch.setattr(fixtures, 'entity', zinzino)
    body = html(title=f'Zinzino {form}', extra=(
        f'<meta name="description" content="Zinzino {form} provides shareholder and investor relations information worldwide.">'
        '<a href="mailto:shares@example.no">Investor contact</a>'))
    _, row, _, _ = execute_web(tmp_path, monkeypatch, body)
    assert not any(c['field'] == 'official_website' for c in row['claims'])
    assert not any(c['field'].startswith(('contact.', 'website_description.')) for c in row['claims'])
