"""Recheck published brands against saved proof pages; performs no HTTP."""
import collections
import json
from pathlib import Path

from signalpost.web.collector import extract_public_brand
from signalpost.web.html import Page

root = Path(__file__).resolve().parents[1]
run = root / 'bench/runs/final-20261120'
before = collections.Counter()
after = collections.Counter()
changes = []
rows = 0
for line in (run / 'envelopes.jsonl').open(encoding='utf8'):
    row = json.loads(line)
    rows += 1
    claims = row['claims']
    before.update(c['family'] for c in claims if c['availability'] == 'available')
    brands = [c for c in claims if c['field'] == 'public_brand' and c['availability'] == 'available']
    for brand in brands:
        evidence = {e['id']: e for e in row['evidence']}
        source = next((evidence[i] for i in brand['evidence_ids']
                       if i in evidence and evidence[i].get('content_sha256')), None)
        if source is None:
            raise AssertionError('Brand proof blob missing: ' + row['organisation_number'])
        page = Page((run / 'state/blobs' / source['content_sha256']).read_bytes(), source['source_url'])
        legal = row['run']['legal_identity'].get('legal_name')
        new = extract_public_brand(page, legal)
        if new != brand['value']:
            changes.append({'orgnr': row['organisation_number'], 'old': brand['value'], 'new': new,
                            'proof_url': source['source_url']})
            if new is None:
                after['website'] -= 1
    after.update(c['family'] for c in claims if c['availability'] == 'available')
result = {'rows': rows, 'http_requests': 0, 'existing_brands_changed': len(changes),
          'family_counts_before': dict(before), 'family_counts_after': dict(after), 'changes': changes}
target = root / 'bench/stage-aw/brand-replay.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(result, ensure_ascii=False))
