"""Synthetic production integration, not real-source accuracy measurement."""
import asyncio
import json
from pathlib import Path

from scripts.production_replay import run_production_replay


def test_external_sources_strict_replay(tmp_path):
    root = Path('tests/fixtures/external_integration')
    async def execute(label):
        target = tmp_path / label
        await run_production_replay(
            input_path=root/'batch.txt', output_envelopes=target/'envelopes.jsonl',
            output_report=target/'report.json', state_dir=target/'state',
            manifest_path=root/'manifest.json', fixtures_dir=root/'blobs',
            websites=True, hiring=True, public_activity=True, workers=1,
            observation_time='2026-10-15T10:00:00Z')
        return [json.loads(line) for line in (target/'envelopes.jsonl').read_text().splitlines()]
    first = asyncio.run(execute('first'))
    second = asyncio.run(execute('second'))
    assert [row['organisation_number'] for row in first] == ['923609016','988258229','999592236','923609016','123456789']
    def published(row):
        return {c['field']:c['value'] for c in row['claims'] if c['availability']=='available'}
    claims = published(first[0])
    assert claims['official_website']['identity_level']=='VERIFIED'
    assert claims['official_website']['relationship_note']=='group_site'
    assert any(key.startswith('contact.email.') for key in claims)
    assert not any(key.startswith('social_profile.') for key in claims)
    assert 'sibling@zephyrsynthetic.no' not in claims.values()
    assert not any(isinstance(value,dict) and 'sibling-synthetic' in str(value.get('url','')) for value in claims.values())
    assert not any(key.startswith('website_description.') for key in claims)
    jobs = [value for key,value in claims.items() if key.startswith('hiring.job.')]
    assert {job['employer_orgnr'] for job in jobs} == {'923609016','993578843'}
    # Job claims cite the anonymously reachable public ad page, never the
    # token-gated feed API; the feed entry is retained as discovery provenance.
    evidence = {e['id']:e for e in first[0]['evidence']}
    blobs_dir = tmp_path/'first'/'state'/'blobs'
    for claim in first[0]['claims']:
        if not claim['field'].startswith('hiring.job.') or claim['availability']!='available':continue
        cited = [evidence[i] for i in claim['evidence_ids']]
        assert {e['source_url'] for e in cited} == {'https://arbeidsplassen.nav.no/stillinger/stilling/'+claim['value']['uuid']}
        for e in cited:
            body = (blobs_dir/e['content_sha256']).read_bytes().decode('utf-8')
            assert e['claim_span'] in body
        assert any(claim['value']['employer_orgnr'] in e['claim_span'] for e in cited)
        assert 'pam-stilling-feed.nav.no/api/v1/feedentry/' in json.loads(cited[0]['source_identifier'])['discovery_url']
    activity = [value for key,value in claims.items() if key.startswith('dated_item.')]
    assert activity == []  # Group-site activity cannot describe the subsidiary.
    assert 'official_website' not in published(first[1])
    assert first[2]['run']['sections']['accounts']=='failed'
    assert not published(first[-1])
    assert published(first[0])==published(first[3])
    for a,b in zip(first,second):
        # Run IDs and runtime diagnostics are volatile. Compare all scientific
        # outputs, including full provenance, timestamps, unknowns and synthesis.
        for key in ['claims','evidence','changes','modules']:
            assert a[key]==b[key], key
        assert a['run']['synthesis']==b['run']['synthesis']
        assert a['run']['sections']==b['run']['sections']


def test_partner_directory_does_not_prove_owner():
    from signalpost.web.html import Page
    from signalpost.web.proof import score
    raw = ('<html><title>Directory</title><h1>Our partners</h1>'
           '<p>Quartzsynthetic AS Org.nr. 988258229</p><p>Other AS Org.nr. 999592236</p>'
           + '<p>Directory listing for partner services.</p>'*20 + '</html>')
    proof = score(Page(raw.encode(),'https://quartzsynthetic.no/'), '988258229',
                  {'name':'Quartzsynthetic AS'}, 'registry_website', [])
    assert proof.level=='REJECT'
    assert proof.reason=='partner_directory_mention'
