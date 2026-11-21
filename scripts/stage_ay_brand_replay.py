"""Compare existing brands with current offline extraction from saved HTML proofs."""
import collections
import json
from pathlib import Path
from signalpost.web.collector import extract_public_brand
from signalpost.web.html import Page
from stage_ay_field_inventory import JURY, ROOT, OUT


def replay(path, blobs, allowed=None):
    changes = []
    seen = set()
    old_brands = 0
    for row in map(json.loads, path.open(encoding='utf8')):
        org = row['organisation_number']
        if (allowed is not None and org not in allowed) or org in seen:
            continue
        seen.add(org)
        evidence = {e['id']:e for e in row['evidence']}
        for claim in row['claims']:
            if claim['field'] != 'public_brand' or claim['availability'] != 'available':
                continue
            old_brands += 1
            proof = next((evidence[i] for i in claim['evidence_ids'] if i in evidence and evidence[i].get('content_sha256')), None)
            assert proof is not None
            page = Page((blobs / proof['content_sha256']).read_bytes(), proof['source_url'])
            new = extract_public_brand(page, row['run']['legal_identity'].get('legal_name'))
            if new != claim['value']:
                changes.append({'orgnr':org,'before':claim['value'],'after':new,'source_url':proof['source_url']})
    return {'companies':len(seen),'published_brands_before':old_brands,'changes':changes,'http_requests':0}


def main():
    allowed=set(json.loads((JURY/'jury-sample.json').read_text(encoding='utf8'))['active'][:300])
    data={'unseen300':replay(JURY/'jury-first-envelopes.jsonl',JURY/'out/state/blobs',allowed),
          'final1000':replay(ROOT/'bench/runs/final-20261120/envelopes.jsonl',
                             ROOT/'bench/runs/final-20261120/state/blobs')}
    (OUT/'brand-replay.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(data,ensure_ascii=True))


if __name__=='__main__':main()
