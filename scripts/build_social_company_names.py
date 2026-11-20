"""Build the withholding-only name index from an official local BRREG bulk CSV."""
import argparse
import json
from pathlib import Path
if __package__:
    from .brreg_index_data import read_source, write_index
else:
    from brreg_index_data import read_source, write_index


def build(source, download_manifest, destination, manifest_path):
    records, provenance = read_source(source, download_manifest)
    payload = {'schema_version': 2,
        'purpose': 'withholding-only registered-name universe; never ownership or relationship proof',
        **provenance,
        'transformations': [
            'Use every main-entity CSV row, without competition-cohort or legal-form filtering.',
            'Validate organisation-number checksums; exclude invalid numbers or empty names.',
            'Trim surrounding whitespace; preserve registered name spelling; reject duplicate numbers.',
            'Retain only organisation number and registered name; sort by organisation number.',
            'Serialize canonical UTF-8 JSON and gzip with mtime=0; no personal/contact fields retained.'],
        'companies': [[org, name] for org, (name, _) in sorted(records.items())]}
    return write_index(destination, payload, manifest_path, rows=len(records))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--download-manifest', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=Path('data/social_company_names.json.gz'))
    parser.add_argument('--manifest', type=Path, default=Path('data/social_company_names_build.json'))
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.download_manifest, args.destination, args.manifest), indent=2))
