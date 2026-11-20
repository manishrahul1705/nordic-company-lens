"""Build shared-domain withholding nominations from an official local BRREG bulk CSV."""
import argparse
import json
from pathlib import Path
if __package__:
    from .brreg_index_data import read_source, write_index
else:
    from brreg_index_data import read_source, write_index
from signalpost.web.policy import domain, normalize_url


def build(source, download_manifest, destination, manifest_path):
    records, provenance = read_source(source, download_manifest)
    owners = {}
    website_rows = 0
    for org, (_, website) in records.items():
        url = normalize_url(website)
        host = domain(url) if url else ''
        if host:
            owners.setdefault(host, set()).add(org)
            website_rows += 1
    domains = {host: sorted(orgs) for host, orgs in sorted(owners.items()) if len(orgs) >= 2}
    payload = {'schema_version': 2, 'purpose': 'conservative shared-domain nominations; never ownership proof',
        **provenance,
        'transformations': [
            'Read main-entity organisasjonsnummer and hjemmeside from the official full CSV.',
            'Validate organisation numbers; trim fields and exclude empty registered names.',
            'Normalize website URLs with the production policy and group by registrable domain.',
            'Keep domains naming at least two distinct valid organisations; sort domains and numbers.',
            'Serialize canonical UTF-8 JSON and gzip with mtime=0; no page bodies or contact fields.'],
        'domains': domains}
    return write_index(destination, payload, manifest_path, rows=len(domains),
                       source_entities=len(records), website_rows=website_rows,
                       domain_orgnr_pairs=sum(map(len, domains.values())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--download-manifest', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=Path('src/signalpost/data/registry_domains.json.gz'))
    parser.add_argument('--manifest', type=Path, default=Path('src/signalpost/data/registry_domains_build.json'))
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.download_manifest, args.destination, args.manifest), indent=2))
