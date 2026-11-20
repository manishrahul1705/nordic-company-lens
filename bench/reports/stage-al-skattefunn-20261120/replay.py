"""Offline addition replay: sockets are forbidden, prior claim IDs must survive."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from signalpost.models.envelope import Envelope, CompactProfile
from signalpost.models.shapes import serialize
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.skattefunn import publish
from signalpost.synthesis.cohort import build_index, context
from signalpost.synthesis.template import generate
from scripts.verify_output import verify


def no_network(event, args):
    if event in {'socket.connect', 'socket.getaddrinfo'}:
        raise AssertionError('Offline replay forbids ' + event)


def counts(rows):
    result = {}
    for prefix in ['skattefunn.', 'research.', 'state_aid.']:
        claims = [(r.organisation_number, c) for r in rows for c in r.claims
                  if c.field.startswith(prefix) and c.availability == 'available']
        result[prefix.rstrip('.')] = {'companies': len({o for o, c in claims}), 'claims': len(claims)}
    result['all_published'] = sum(c.availability == 'available' for r in rows for c in r.claims)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path); p.add_argument('output', type=Path)
    p.add_argument('--summary', type=Path, required=True)
    args = p.parse_args(); sys.addaudithook(no_network); start = time.perf_counter()
    if args.output.exists():
        raise ValueError('Refusing reused replay directory')
    rows = [Envelope.model_validate(json.loads(line)) for line in args.source.open(encoding='utf-8')]
    before = counts(rows)
    old = {r.organisation_number: {c.id for c in r.claims if c.availability == 'available'} for r in rows}
    needed = {e.content_sha256 for r in rows for e in r.evidence}
    state = args.output / 'state'; blobdir = state / 'blobs'; blobdir.mkdir(parents=True)
    # Saved addition replays reference earlier immutable content-addressed blobs.
    for directory in Path('bench/runs').glob('*/state/blobs'):
        if directory.resolve() == blobdir.resolve():
            continue
        for file in directory.iterdir():
            if file.name in needed:
                os.link(file, blobdir / file.name); needed.remove(file.name)
        if not needed:
            break
    if needed:
        raise ValueError('Missing saved evidence blobs: ' + str(sorted(needed)[:10]))
    blobs = BlobStore(state); reviews = []
    for row in rows:
        publish(row, blobs)
        assert old[row.organisation_number] <= {c.id for c in row.claims if c.availability == 'available'}
        evidence = {e.id: e for e in row.evidence}
        for c in row.claims:
            if not c.field.startswith('skattefunn.'):
                continue
            ev = evidence[c.evidence_ids[0]]
            body = blobs.read(ev.content_sha256)
            assert hashlib.sha256(body).hexdigest() == ev.content_sha256
            cells = json.loads(body)
            assert cells['Organisasjonsnummer'] == row.organisation_number and cells['Søknad godkjent'] == 'JA'
            reviews.append({'orgnr': row.organisation_number,
                'company': next((c.value for c in row.claims if c.field == 'identity.legal_name'), None),
                'claim': c.model_dump(mode='json'), 'evidence': ev.model_dump(mode='json'), 'source_cells': cells})
    cohort = build_index(rows)
    dest = args.output / 'envelopes.jsonl'
    with dest.open('w', encoding='utf-8') as f:
        for row in rows:
            row.run.synthesis = generate(row, context(row, cohort))
            row.profile = CompactProfile(organisation_number=row.organisation_number,
                values={c.field: c.value for c in row.claims}, evidence_ids=[e.id for e in row.evidence], synthesis=row.run.synthesis)
            f.write(json.dumps(serialize(row, 'union'), ensure_ascii=False, separators=(',', ':')) + '\n')
    verified = verify(dest, state, len(rows))
    summary = {'source': str(args.source), 'output': str(args.output), 'companies': len(rows),
        'before': before, 'after': counts(rows), 'new_HTTP_requests': 0,
        'network_guard': 'socket.connect and socket.getaddrinfo forbidden', 'prior_published_claims_removed': 0,
        'deduplicated_against_research': sum(r.run.refresh['funding_snapshots']['skattefunn']['deduplicated'] for r in rows
            if 'skattefunn' in r.run.refresh.get('funding_snapshots', {})),
        'seconds': round(time.perf_counter() - start, 3), 'strict_verifier': verified}
    args.summary.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    (args.output / 'review-candidates.json').write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
