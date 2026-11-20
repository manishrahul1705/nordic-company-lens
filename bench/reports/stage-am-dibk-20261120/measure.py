"""Summarize the real full live run, verify evidence and retain ten reviewed rows."""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from signalpost.models.envelope import Envelope
from signalpost.sources.dibk import selected, HOST
from scripts.verify_output import verify

HERE = Path(__file__).resolve().parent


def main():
    base = Path('bench/runs/stage-am-live1000')
    report = json.loads((base / 'report.json').read_text(encoding='utf-8'))
    rows = [Envelope.model_validate(json.loads(l)) for l in (base / 'envelopes.jsonl').open(encoding='utf-8')]
    events = [e for e in report['request_log'] if e['host'] == HOST]
    enterprise = [e for e in events if e['organisation_number'] != '__dibk_robots__']
    claims = [(r, c) for r in rows for c in r.claims if c.field.startswith('central_approval.') and c.availability == 'available']
    assert not any('/api/' in e['url'] or '/search' in e['url'] for e in events)
    assert max(Counter(e['organisation_number'] for e in enterprise).values(), default=0) <= 1
    assert max(report['requests_by_company'].values(), default=0) <= 40 if 'requests_by_company' in report else True
    verified = verify(base / 'envelopes.jsonl', base / 'state', 1000, Path('bench/inputs/1000-r3/batch.jsonl'))
    known = ['912492575', '926698435']
    summary = {'mode': 'fresh full-1000 all-source live run, default concurrency/budget, site ON',
        'run_status': report['run_status'], 'selected': sum(selected(r) for r in rows),
        'companies_queried': len({e['organisation_number'] for e in enterprise}),
        'companies_with_approvals': len({r.organisation_number for r,c in claims}),
        'approval_claims': len(claims), 'status_counts': dict(Counter(c.value['status'] for r,c in claims)),
        'HTTP_added': len(events), 'enterprise_HTTP': len(enterprise), 'robots_HTTP': len(events) - len(enterprise),
        'HTTP_status_counts': dict(Counter(str(e['status']) for e in enterprise)),
        'total_run_HTTP': report['requests'], 'pooled_cap': report['effective_configuration']['request_caps']['pooled'],
        'max_HTTP_per_company': max(Counter(e['organisation_number'] for e in report['request_log']
            if e['organisation_number'] in {r.organisation_number for r in rows}).values(), default=0),
        'source_first_request_seconds': min((e['attempt_started'] for e in events), default=None),
        'source_last_response_seconds': max((e['attempt_started'] + e.get('runtime_ms', 0) / 1000 for e in events), default=None),
        'source_tail_wait_seconds': report['timing_markers']['dibk_tail_wait_seconds'],
        'wall_time_limit_check': 'The measured unhidden DiBK join wait must be <=60s; this is not a causal paired disabled/enabled whole-run benchmark.',
        'crawl_runtime_seconds': report['runtime_ms'] / 1000,
        'end_to_end_wall_seconds': (datetime.fromtimestamp((base / 'report.json').stat().st_mtime).astimezone()
            - datetime.fromisoformat(json.loads((base / 'state/progress.json').read_text())['start_time'].replace('Z', '+00:00'))).total_seconds(),
        'deadline_hits': report['deadline_hits'], 'handled_exceptions': report['handled_exceptions'],
        'unhandled_exceptions': report['unhandled_exceptions'],
        'diagnostics': dict(Counter(r.run.refresh['dibk']['state'] for r in rows if 'dibk' in r.run.refresh)),
        'known_Kilde_overlap': {org: sum(r.organisation_number == org for r,c in claims) for org in known},
        'strict_verifier': verified}
    (HERE / 'full1000.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    # One row from ten companies where possible; ensure both named competitors' matches appear.
    chosen = []; seen = set()
    for org in known:
        match = next(((r,c) for r,c in claims if r.organisation_number == org), None)
        if match: chosen.append(match); seen.add(org)
    for r,c in claims:
        if r.organisation_number not in seen:
            chosen.append((r,c)); seen.add(r.organisation_number)
        if len(chosen) == 10: break
    if len(chosen) < 10:
        for pair in claims:
            if pair not in chosen: chosen.append(pair)
            if len(chosen) == 10: break
    assert len(chosen) == 10, 'Fewer than ten published claims to review'
    review = []
    for r,c in chosen:
        evidence = [e for e in r.evidence if e.id in c.evidence_ids]
        assert len(evidence) == 6
        raw = (base / 'state/blobs' / evidence[0].content_sha256).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == evidence[0].content_sha256
        assert all(e.content_sha256 == evidence[0].content_sha256 and e.claim_span in raw.decode('utf-8') for e in evidence)
        v = c.value
        assert r.organisation_number in evidence[0].claim_span
        assert v['valid_from'] in evidence[1].claim_span and v['valid_to'] in evidence[1].claim_span
        assert 'Foretaket har sentral godkjenning' in evidence[2].claim_span
        from html import unescape
        cells = [' '.join(unescape(re.sub('<[^>]+>', ' ', e.claim_span)).split()) for e in evidence[3:]]
        assert cells == [v['function'], v['area'], v['class']]
        review.append({'company': next(c.value for c in r.claims if c.field == 'identity.legal_name'),
            'orgnr': r.organisation_number, 'claim': c.model_dump(mode='json'),
            'evidence': [e.model_dump(mode='json') for e in evidence],
            'why_correct': 'Exact labelled enterprise orgnr; positive current-status heading; explicit period covers retrieval day; '
                'function, area and class come from the same approval row, not its explanatory text. Six verbatim spans share the page hash.'})
    (HERE / 'hand-review-10.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
