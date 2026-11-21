"""Build the committed extract from a full run directory. Needs the run; everything after it does not.

Usage: uv run python bench/reports/stage-x-accuracy/extract.py bench/runs/<run>

Writes extract/envelopes.jsonl.xz (the population index: every published claim with its value and
evidence ids, the evidence records those claims cite (URL, locator, span, content hash), and every
synthesis sentence with its cited claim ids) and extract/blobs.jsonl.xz (the full cited source bytes
for every sampled claim, keyed by SHA-256). extract/manifest.json records the run and file hashes.
"""
import base64, hashlib, json, lzma, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C


def slim(r):
    claims = [c for c in r['claims'] if C.published(c)]
    syn = r['run'].get('synthesis') or {}
    sections = {k: [{'text': s['text'], 'claim_ids': s.get('claim_ids', [])} for s in v]
                for k, v in (syn.get('sections') or {}).items()}
    change = [{'id': x['id'], 'field': x['field'], 'value': x['value']} for x in syn.get('change_claims', [])]
    keep = {i for c in claims for i in c['evidence_ids']}
    return {'organisation_number': r['organisation_number'],
            'legal_name': (r['run'].get('legal_identity') or {}).get('legal_name'),
            'claims': [{k: c.get(k) for k in ('id', 'field', 'value', 'availability', 'evidence_ids')} for c in claims],
            'evidence': [{k: e.get(k) for k in ('id', 'source_url', 'locator', 'claim_span', 'content_sha256')}
                         for e in r['evidence'] if e['id'] in keep],
            'synthesis': sections, 'change_claims': change}


def main():
    run = Path(sys.argv[1]).resolve(); C.EXTRACT.mkdir(exist_ok=True)
    rows = []
    for line in open(run / 'envelopes.jsonl', encoding='utf-8-sig'):
        rows.append(slim(json.loads(line)))
    with lzma.open(C.EXTRACT / 'envelopes.jsonl.xz', 'wb', preset=9 | lzma.PRESET_EXTREME) as fh:
        for r in rows:
            fh.write((json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n').encode('utf-8'))
    pop = C.population(rows); picked = C.draw(pop, C.allocate(pop)); by = {r['organisation_number']: r for r in rows}
    need = set()
    for f, org, field, ident, kind in picked:
        if kind == 'claim':
            r = by[org]; c = next(x for x in r['claims'] if x['id'] == ident); ev = {e['id']: e for e in r['evidence']}
            need |= {ev[i]['content_sha256'] for i in c['evidence_ids'] if i in ev}
    blobdir = run / 'state' / 'blobs'; missing = []
    with lzma.open(C.EXTRACT / 'blobs.jsonl.xz', 'wb', preset=9 | lzma.PRESET_EXTREME) as fh:
        for sha in sorted(need):
            p = blobdir / sha
            if not p.exists():
                missing.append(sha); continue
            fh.write((json.dumps({'sha256': sha, 'b64': base64.b64encode(p.read_bytes()).decode()}) + '\n').encode())
    report = json.loads((run / 'report.json').read_text(encoding='utf-8'))
    man = {'run': run.name, 'envelopes': len(rows), 'run_id': report.get('run_id'), 'sampled_blobs': len(need) - len(missing),
           'missing_blobs': missing,
           'files': {n: hashlib.sha256((C.EXTRACT / n).read_bytes()).hexdigest() for n in ('envelopes.jsonl.xz', 'blobs.jsonl.xz')}}
    (C.EXTRACT / 'manifest.json').write_text(json.dumps(man, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(man, indent=1))


if __name__ == '__main__':
    main()
