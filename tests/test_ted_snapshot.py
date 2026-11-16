"""Stage U: the bundled TED snapshot replaces transport only; acceptance rules are unchanged."""
import asyncio
import gzip
import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import httpx
import pytest

from signalpost.budget import SourceFailure
from signalpost.io.report import effective_configuration
from signalpost.sources import ted_snapshot
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.sources.official_extra import award_extract, collect
from tests.test_official_extra import ORG, xml
from tests.test_registry_changes import envelope

RECENT = (date.today() - timedelta(days=30)).isoformat()
RETRIEVED = '2026-11-16T09:00:00Z'


def record(notice='1-2026', winners=(ORG,), kind='can-standard', published=None, body=None, **extra):
    raw = (body if body is not None else xml(day=RECENT)).encode()
    out = {'publication_number': notice, 'notice_type': kind, 'publication_date': published or RECENT + '+01:00',
           'winner_identifier': list(winners), 'buyer_identifier': [], 'winner_country': ['NOR'], 'buyer_country': ['NOR'],
           'xml_url': f'https://ted.europa.eu/en/notice/{notice}/xml', 'retrieved_at': RETRIEVED,
           'content_sha256': hashlib.sha256(raw).hexdigest(), 'awards': [], 'xml': raw.decode()}
    out.update(extra)
    return out


def write(tmp_path, records, built=None):
    path = tmp_path / ted_snapshot.FILENAME
    lines = b''.join(json.dumps(r).encode() + b'\n' for r in records)
    path.write_bytes(gzip.compress(lines, mtime=0))
    built = built or datetime.now(timezone.utc).date().isoformat()
    (tmp_path / ted_snapshot.MANIFEST).write_text(json.dumps({
        'schema_version': 1, 'built_at': built, 'records': len(records),
        'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'retrieved_at_range': [RETRIEVED, RETRIEVED]}))
    return path


class Budget:
    def __init__(self):
        self.deadline = time.monotonic() + 60
        self.events = []

    def reserve(self, url, host, org):
        event = {'url': url, 'host': host}
        self.events.append(event)
        return event


def run(tmp_path, path, dispatch=None, **cfg):
    calls = []

    def handler(request):
        calls.append(str(request.url))
        if request.url.host == 'api.gleif.org':
            return httpx.Response(200, json={'data': [], 'meta': {'pagination': {'lastPage': 1}}})
        if dispatch:
            return dispatch(request)
        raise AssertionError('unexpected TED request ' + str(request.url))

    config = SimpleNamespace(ted_snapshot=True, ted_snapshot_path=path, ted_snapshot_max_age_days=30)
    config.__dict__.update(cfg)

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await collect({ORG: envelope(ORG)}, client, Budget(), BlobStore(tmp_path / 'blobs'), config)
    result, metrics = asyncio.run(go())
    return result[ORG], metrics, calls


def test_snapshot_award_is_identical_to_live_extraction_and_cites_the_real_notice(tmp_path):
    section, metrics, calls = run(tmp_path, write(tmp_path, [record()]))
    assert metrics['ted_mode'] == 'snapshot' and metrics['ted_requests'] == 0
    assert not [c for c in calls if 'ted.europa.eu' in c]
    awards = [c for c in section.claims if c.field.startswith('procurement_award.')]
    raw = xml(day=RECENT).encode()
    live = award_extract(Response(raw, 200, 'https://ted.europa.eu/en/notice/1-2026/xml', RETRIEVED,
                                  hashlib.sha256(raw).hexdigest()), '1-2026', ORG, date.today())
    assert [c.id for c in awards] == [c.id for c in live.claims]
    assert [c.value for c in awards] == [c.value for c in live.claims]
    cited = {e.id: e for e in section.evidence}
    for evidence_id in awards[0].evidence_ids:
        assert cited[evidence_id].source_url == 'https://ted.europa.eu/en/notice/1-2026/xml'
        # The snapshot's retrieval time, never the run time.
        assert cited[evidence_id].retrieved_at == RETRIEVED


def test_nomination_uses_the_live_type_window_and_identifier_rule(tmp_path):
    old = (date.today() - timedelta(days=3 * 366 + 2)).isoformat()
    records = [record('2-2026', kind='cn-standard'),
               record('3-2026', published=old),
               record('4-2026', winners=('999999999',)),
               # Only whitespace is normalised: other identifier material never matches.
               record('5-2026', winners=('NO923609016',)),
               record('6-2026', winners=('923609016MVA',)),
               record('7-2026', winners=('92360901',))]
    section, metrics, _ = run(tmp_path, write(tmp_path, records))
    assert metrics['ted_mode'] == 'snapshot' and metrics['tender_notices_nominated'] == 0
    assert not any(c.field.startswith('procurement_award.') for c in section.claims)


@pytest.mark.parametrize('spelling', ['923 609 016', '923  609	016', ' 923609016 '])
def test_spaced_identifier_is_nominated_and_still_needs_the_exact_xml_match(tmp_path, spelling):
    section, metrics, _ = run(tmp_path, write(tmp_path, [record(winners=(spelling,))]))
    assert metrics['tender_notices_nominated'] == 1
    assert len([c for c in section.claims if c.field.startswith('procurement_award.')]) == 1
    # Nomination alone never publishes: the XML must still name the exact company.
    other = record(winners=(spelling,), body=xml(winner='999999999', day=RECENT))
    section, _, _ = run(tmp_path / 'x', write(tmp_path.joinpath('x').mkdir() or tmp_path / 'x', [other]))
    assert not any(c.field.startswith('procurement_award.') for c in section.claims)


def test_ted_identifier_normalisation_is_whitespace_only():
    from signalpost.sources.official_extra import ted_orgnr, ted_query_values
    assert ted_orgnr('923 609 016') == ted_orgnr('923609016') == '923609016'
    assert ted_orgnr('923 609 016') == '923609016'
    for bad in ('NO 923 609 016', '923 609 016 MVA', '923-609-016', '92360901', '9236090160', None, 923609016):
        assert ted_orgnr(bad) is None
    assert ted_query_values(['923609016']) == '("923609016" OR "923 609 016")'


def test_metadata_only_notice_is_fetched_live_and_counted(tmp_path):
    stub = record(xml=None, content_sha256=None, retrieved_at=None, xml_omitted='no_universe_company')
    section, metrics, calls = run(tmp_path, write(tmp_path, [stub]),
                                  lambda request: httpx.Response(200, text=xml(day=date.today().isoformat())))
    assert metrics['ted_mode'] == 'snapshot' and metrics['ted_requests'] == 1
    assert metrics['ted_snapshot']['live_notice_fetches'] == 1
    assert calls[-1] == 'https://ted.europa.eu/en/notice/1-2026/xml'
    assert any(c.field.startswith('procurement_award.') for c in section.claims)


def test_at_most_ten_awards_and_never_a_notice_total(tmp_path):
    records = [record(f'{n}-2026') for n in range(1, 13)]
    section, _, _ = run(tmp_path, write(tmp_path, records))
    awards = [c for c in section.claims if c.field.startswith('procurement_award.')]
    assert len(awards) == 10
    # Two linked tenders: no single lot is attributable, so no amount is published.
    body = xml(day=RECENT).replace('<efac:LotTender><cbc:ID>T</cbc:ID></efac:LotTender></efac:SettledContract>',
                                   '<efac:LotTender><cbc:ID>T</cbc:ID></efac:LotTender><efac:LotTender><cbc:ID>T</cbc:ID></efac:LotTender></efac:SettledContract>')
    section, _, _ = run(tmp_path / 'two', write(tmp_path.joinpath('two').mkdir() or tmp_path / 'two', [record(body=body)]))
    award = next(c for c in section.claims if c.field.startswith('procurement_award.'))
    assert 'value' not in award.value


def test_tampered_notice_is_a_failed_fetch_not_an_award(tmp_path):
    bad = record()
    bad['xml'] = bad['xml'].replace('Bridge maintenance', 'Something else')
    section, metrics, _ = run(tmp_path, write(tmp_path, [bad]))
    assert not any(c.field.startswith('procurement_award.') for c in section.claims)
    missing = record(xml=None, content_sha256=None, retrieved_at=None)
    section, _, _ = run(tmp_path / 'm', write(tmp_path.joinpath('m').mkdir() or tmp_path / 'm', [missing]),
                        lambda request: httpx.Response(503, text='unavailable'))
    assert not any(c.field.startswith('procurement_award.') for c in section.claims)


@pytest.mark.parametrize('case,code', [('missing', 'ted_snapshot_missing'), ('stale', 'ted_snapshot_stale'),
                                       ('tampered', 'ted_snapshot_invalid')])
def test_missing_stale_or_invalid_snapshot_falls_back_to_the_live_path(tmp_path, case, code):
    if case == 'missing':
        path = tmp_path / 'absent' / ted_snapshot.FILENAME
    elif case == 'stale':
        path = write(tmp_path, [record()], built=(date.today() - timedelta(days=31)).isoformat())
    else:
        path = write(tmp_path, [record()])
        path.write_bytes(path.read_bytes() + b'x')
    with pytest.raises(SourceFailure) as exc:
        ted_snapshot.load(path, 30)
    assert exc.value.code == code

    def dispatch(request):
        if request.url.host == 'api.ted.europa.eu':
            return httpx.Response(200, json={'notices': [{'publication-number': '1-2026', 'notice-type': 'can-standard',
                                                          'winner-identifier': [ORG]}], 'totalNoticeCount': 1})
        return httpx.Response(200, text=xml(day=date.today().isoformat()))
    section, metrics, calls = run(tmp_path, path, dispatch)
    assert metrics['ted_mode'] == 'live_fallback' and metrics['ted_snapshot'] == {'fallback_reason': code}
    assert metrics['ted_requests'] == 2 and any(c.field.startswith('procurement_award.') for c in section.claims)


def test_snapshot_can_be_switched_off_and_mode_is_reported(tmp_path):
    def dispatch(request):
        return httpx.Response(200, json={'notices': [], 'totalNoticeCount': 0})
    _, metrics, _ = run(tmp_path, write(tmp_path, [record()]), dispatch, ted_snapshot=False)
    assert metrics['ted_mode'] == 'live' and metrics['ted_requests'] == 1
    config = SimpleNamespace(websites=True, hiring=False, public_activity=True, registry_changes=True,
                             official_extra_sources=True, website_suffix_contact_proof=True, synthesis='template',
                             website_request_cap=40, website_total_request_cap=40, unrecognised_flags=[],
                             output=None, profiles_output=None, report=None, site_dir=None)
    report = {'official_extra': {'ted_mode': 'snapshot', 'ted_snapshot': {'built_at': '2026-11-16'}}}
    ted = effective_configuration(config, SimpleNamespace(cap=380), report)['ted']
    assert ted == {'mode': 'snapshot', 'snapshot_built_at': '2026-11-16', 'fallback_reason': None}


def test_xml_company_id_whitespace_is_normalised_but_the_number_must_be_exact():
    from signalpost.sources.official_extra import award_extract
    def parse(winner):
        raw = xml(winner=winner, day=RECENT).encode()
        r = Response(raw, 200, 'https://ted.europa.eu/en/notice/1-2026/xml', RETRIEVED, hashlib.sha256(raw).hexdigest())
        return award_extract(r, '1-2026', ORG, date.today()).claims
    assert parse('923 609 016') and parse('923 609 016') and parse('NO 923 609 016 MVA')
    assert not parse('923 609 01') and not parse('923 609 0160')
