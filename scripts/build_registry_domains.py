"""Build conservative shared-domain nominations from a local frozen corpus.

No network access. Nominations can only withhold shared-site content, never
authorize ownership or publication. Full supplied BRREG snapshots additionally
contribute every registry website, including companies outside the input batch.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from signalpost.web.policy import domain, normalize_url
from signalpost.identity.orgnr import valid


def build(source, destination):
    owners = {}
    with gzip.open(source, 'rt', encoding='utf8') as handle:
        for line in handle:
            row = json.loads(line)
            org = row['organisation_number']
            url = normalize_url(row.get('website'))
            if valid(org) and url:
                owners.setdefault(domain(url), set()).add(org)
    data = {'schema_version': 1, 'purpose': 'conservative shared-domain nominations; never ownership proof',
            'source_url': 'https://builderr.ai/signalpost-company-universe-2025.jsonl.gz',
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'domains': {host: sorted(orgs) for host, orgs in sorted(owners.items()) if len(orgs) >= 2}}
    destination.write_bytes(gzip.compress(json.dumps(data, separators=(',', ':'), sort_keys=True).encode(), mtime=0))
    print(json.dumps({'shared_domains': len(data['domains']), 'bytes': destination.stat().st_size,
                      'source_sha256': data['source_sha256']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    build(args.source, args.destination)
