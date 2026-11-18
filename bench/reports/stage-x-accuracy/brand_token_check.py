"""Apply the brand identity-token rule to every brand published in the final frozen run. Zero HTTP."""
import json, sys
from pathlib import Path
from signalpost.web.collector import shares_identity_token
ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'bench/runs/final-frozen-20261118'
out = []
for line in open(RUN / 'envelopes.jsonl', encoding='utf-8-sig'):
    r = json.loads(line); ev = {e['id']: e for e in r['evidence']}
    for c in r['claims']:
        if c['field'] == 'public_brand' and c['availability'] == 'available':
            url = ev[c['evidence_ids'][0]]['source_url']
            name = r['run']['legal_identity'].get('legal_name')
            out.append({'orgnr': r['organisation_number'], 'legal_name': name, 'brand': c['value'], 'page': url,
                        'kept': shares_identity_token(c['value'], name, url)})
(Path(__file__).parent / 'brand-token-check.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(len(out), 'brands;', sum(not x['kept'] for x in out), 'withheld')
for x in out: print('KEEP' if x['kept'] else 'DROP', x['orgnr'], x['legal_name'], '|', x['brand'], '|', x['page'])
