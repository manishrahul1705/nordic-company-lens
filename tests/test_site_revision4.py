"""Revision 4 offline-site presentation: readable values, verbatim excerpts, citations."""
from pathlib import Path

from signalpost.site import (display_markup_dates, display_value, value_html, value_text, source_link,
                             capped_citations, evidence_panel)

ASSET = Path('src/signalpost/site_assets/site.js').read_text(encoding='utf-8')


def test_registry_objects_and_numbers_are_readable():
    form = {'_links': {'self': {'href': 'https://data.brreg.no/enhetsregisteret/api/organisasjonsformer/AS'}},
            'beskrivelse': 'Aksjeselskap', 'kode': 'AS'}
    assert value_text(form) == 'Aksjeselskap (AS)'
    assert 'href' not in value_html(form) and '_links' not in value_html(form)
    address = {'adresse': ['Vognmannsløkka 10'], 'kommune': 'VÅGAN', 'kommunenummer': '1865', 'land': 'Norge',
               'landkode': 'NO', 'postnummer': '8310', 'poststed': 'KABELVÅG'}
    assert display_value(address) == 'Vognmannsløkka 10, 8310 KABELVÅG'
    assert value_text({'id': 'YI42', 'other': None}) == 'YI42 (ISO 20275 entity legal form code)'
    assert value_text(10095955.0) == '10,095,955' and value_text(-2410.5) == '-2,410.5'
    assert value_text(2025) == '2025' and value_text('2025') == '2025'  # years are never regrouped


def test_verbatim_excerpts_keep_their_dates():
    markup = ('<p>Founded 2015-05-01</p><blockquote class="excerpt" data-verbatim>"stiftelsesdato":"2015-05-01"'
              '<mark>2015-05-01</mark></blockquote><p>2016-01-02</p>')
    shown = display_markup_dates(markup)
    assert '<p>Founded 1 May 2015</p>' in shown and '<p>2 Jan 2016</p>' in shown
    assert '"stiftelsesdato":"2015-05-01"<mark>2015-05-01</mark>' in shown


def test_batched_source_is_short_and_labelled_but_full_url_stays_reachable():
    url = ('https://api.gleif.org/api/v1/lei-records?filter%5Bentity.registeredAs%5D=812173472%2C812+173+472%2C'
           '812181912%2C812+181+912%2C915574858')
    html = source_link(url)
    assert 'href="' + url.replace('&', '&amp;') + '"' in html and 'title="' in html
    assert '>api.gleif.org/api/v1/lei-records?…</a>' in html
    assert 'shared request covering 3 organisations' in html
    assert 'shared request' not in source_link('https://data.brreg.no/enhetsregisteret/api/enheter/915574858')


def test_evidence_record_shows_date_and_locator_before_the_link_and_marks_excerpts_verbatim():
    claim = {'id': 'c' * 64, 'field': 'identity.founding_date', 'value': '2015-05-01', 'availability': 'available',
             'evidence_ids': ['e1']}
    record = {'id': 'e1', 'source_url': 'https://data.brreg.no/enhetsregisteret/api/enheter/915574858', 'source_class': 'official_registry',
              'retrieved_at': '2026-11-14T17:29:01Z', 'claim_span': '"stiftelsesdato":"2015-05-01"', 'content_sha256': 'a' * 64,
              'extraction_method': 'signalpost.registry.v1', 'locator': '/stiftelsesdato'}
    html = evidence_panel(claim, {'e1': record})
    assert html.index('Retrieved at') < html.index('Record in source') < html.index('Source link')
    assert '<blockquote class="excerpt" data-verbatim>' in html


def test_sentence_citations_are_capped_but_all_reachable():
    cites = ['<a class="citation" href="#fact-%d">[source]</a>' % n for n in range(8)]
    html = capped_citations(cites)
    assert all(c in html for c in cites)
    assert html.index(cites[2]) < html.index('<details class="more-citations"><summary>+5 more sources</summary>') < html.index(cites[3])
    assert capped_citations(cites[:3]) == ' '.join(cites[:3])


def test_receipts_collapse_beyond_three_records_without_dropping_any(tmp_path):
    from signalpost.site import receipt_pages
    evidence = [{'id': 'e%d' % n, 'source_url': 'https://data.brreg.no/enhetsregisteret/api/enheter/915574858',
                 'source_class': 'official_registry', 'retrieved_at': '2026-11-14T17:29:01Z', 'claim_span': 'span %d' % n,
                 'content_sha256': '%064x' % n, 'extraction_method': 'signalpost.registry.v1', 'locator': '/navn/%d' % n}
                for n in range(7)]
    row = {'organisation_number': '915574858', 'evidence': evidence,
           'claims': [{'id': 'c' * 64, 'field': 'identity.legal_name', 'value': 'CR1.NO AS', 'availability': 'available',
                       'evidence_ids': [e['id'] for e in evidence]}]}
    files, _ = receipt_pages(row, 'Nordic Company Lens')
    html = ''.join(files.values())
    assert all('span %d' % n in html for n in range(7))
    assert html.count('<details class="more-evidence"><summary>4 more supporting sources</summary>') == 1
    assert html.index('span 2') < html.index('more-evidence') < html.index('span 3')


def test_home_headline_leads_with_findings_and_title_is_the_brand():
    import inspect
    from signalpost import site
    source = inspect.getsource(site)
    assert "% with {key}" not in source and 'cited claims' in source
    assert inspect.signature(site.generate_site).parameters['title'].default == 'Nordic Company Lens'


def test_search_accepts_spaced_orgnr_and_compare_cards_use_a_middle_dot():
    assert "const searchKey = text =>" in ASSET
    assert "searchKey(globalInput.value)" in ASSET and "searchKey(searchInput?.value)" in ASSET
    assert "r.orgnr+' ? '" not in ASSET and "r.orgnr+' · '+(r.municipality" in ASSET
