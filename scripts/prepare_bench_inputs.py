"""Prepare the optional deterministic 1000-company cohort in ignored bench/cache.

The committed 20/100 cohorts never use this network path. The optional 1000
cohort pins universe hashes/seed, but obtains a current BRREG subset on first
use; its exact file hashes and retrieval metadata accompany every run.
"""
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

from sample_universe import ARCHIVE_SHA


def prepare(root):
    cache = root / 'bench/cache'
    target = cache / 'inputs/1000'
    manifest = target / 'MANIFEST.txt'
    if manifest.exists():
        return target, manifest
    target.mkdir(parents=True, exist_ok=True)
    archive = cache / 'universe.jsonl.gz'
    universe_url = 'https://builderr.ai/signalpost-company-universe-2025.jsonl.gz'
    if not archive.exists():
        with urllib.request.urlopen(universe_url, timeout=120) as response, archive.open('wb') as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
    with archive.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Cached universe archive hash mismatch')
    subprocess.run([sys.executable, str(root / 'scripts/sample_universe.py'),
                    '--universe', str(archive), '--output', str(target / 'batch.jsonl'),
                    '--count', '1000', '--seed', '20261103'], check=True)
    wanted = {json.loads(line)['organisation_number']
              for line in (target / 'batch.jsonl').read_text(encoding='utf-8').splitlines()}
    url = 'https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv'
    request = urllib.request.Request(url, headers={
        'User-Agent': 'NordicCompanyLensBenchmark/2.0', 'Accept-Encoding': 'gzip'})
    found = set()
    with urllib.request.urlopen(request, timeout=120) as response:
        buffered = io.BufferedReader(response)
        stream = gzip.GzipFile(fileobj=buffered) if buffered.peek(2)[:2] == b'\x1f\x8b' else buffered
        with io.TextIOWrapper(stream, encoding='utf-8-sig', newline='') as text, (
                target / 'registry.csv').open('w', encoding='utf-8', newline='') as output:
            reader = csv.DictReader(text)
            writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row['organisasjonsnummer'] in wanted:
                    writer.writerow(row)
                    found.add(row['organisasjonsnummer'])
                    if found == wanted:
                        break
    (target / 'source.json').write_text(json.dumps({
        'universe_url': universe_url, 'bulk_url': url, 'seed': 20261103,
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'matched': len(found), 'missing': sorted(wanted - found),
        'note': 'Missing bulk members use the production live fallback.',
    }, indent=2) + '\n', encoding='utf-8')
    manifest.write_text(''.join(hashlib.sha256((target / name).read_bytes()).hexdigest()
                                + '  ' + name + '\n'
                                for name in ('batch.jsonl', 'registry.csv')), encoding='utf-8')
    return target, manifest
