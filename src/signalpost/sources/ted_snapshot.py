"""Read the bundled, declared TED award-notice snapshot (built by scripts/ted_snapshot.py).

The snapshot replaces only *transport*: nomination uses the same literal
identifier intersection as the live search path, and each nominated notice's
verbatim XML is handed to the unchanged ``award_extract``. Evidence keeps the
real ted.europa.eu XML URL and the snapshot's own retrieval timestamp.
"""
import gzip
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

from ..budget import SourceFailure
from .official_extra import ted_nominated

FILENAME = 'ted-no-notices.jsonl.gz'
MANIFEST = 'ted_snapshot_build.json'
TYPES = {'can-standard', 'can-social'}
MAX_COMPRESSED = 96_000_000


def default_path():
    here = Path(__file__).resolve()
    for base in (here.parents[1] / 'data', here.parents[3] / 'data'):
        if (base / FILENAME).exists():
            return base / FILENAME
    return here.parents[3] / 'data' / FILENAME


class Snapshot:
    def __init__(self, path, manifest, age_days):
        self.path, self.manifest, self.age_days = path, manifest, age_days

    def metrics(self):
        return {'built_at': self.manifest['built_at'], 'age_days': round(self.age_days, 3),
                'records': self.manifest['records'], 'file_sha256': self.manifest['file_sha256'],
                'retrieved_at_range': self.manifest.get('retrieved_at_range')}

    def nominate(self, orgs, since):
        """Return {notice: (scope, record)} exactly as the live search would nominate.

        Live: notice-type in (can-standard, can-social), publication-date >= since,
        and an exact nine-digit match after whitespace-only normalisation (ted_nominated).
        """
        orgs = set(orgs)
        found = {}
        with gzip.open(self.path, 'rt', encoding='utf8') as f:
            for line in f:
                record = json.loads(line)
                if record['notice_type'] not in TYPES:
                    continue
                scope = ted_nominated(orgs, record['winner_identifier'] + record['buyer_identifier'])
                if not scope:
                    continue
                try:
                    published = date.fromisoformat(str(record['publication_date'])[:10])
                except ValueError:
                    continue
                if published < since:
                    continue
                found[record['publication_number']] = (scope, record)
        return found


def body(record):
    """Verbatim XML bytes, rejected if they do not match the recorded content hash."""
    if record.get('xml') is None:
        raise SourceFailure('ted_snapshot_notice_missing')
    raw = record['xml'].encode('utf-8')
    if hashlib.sha256(raw).hexdigest() != record['content_sha256']:
        raise SourceFailure('ted_snapshot_hash_mismatch')
    return raw


def load(path=None, max_age_days=30, now=None):
    path = Path(path) if path else default_path()
    manifest_path = path.with_name(MANIFEST)
    try:
        if path.stat().st_size > MAX_COMPRESSED:
            raise SourceFailure('ted_snapshot_size_invalid')
        manifest = json.loads(manifest_path.read_text(encoding='utf8'))
        digest = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                digest.update(chunk)
    except FileNotFoundError:
        raise SourceFailure('ted_snapshot_missing') from None
    except (OSError, ValueError):
        raise SourceFailure('ted_snapshot_invalid') from None
    if manifest.get('schema_version') != 1 or digest.hexdigest() != manifest.get('file_sha256'):
        raise SourceFailure('ted_snapshot_invalid')
    try:
        built = datetime.fromisoformat(manifest['built_at']).replace(tzinfo=timezone.utc)
    except (KeyError, ValueError, TypeError):
        raise SourceFailure('ted_snapshot_invalid') from None
    age = ((now or datetime.now(timezone.utc)) - built).total_seconds() / 86400
    if age < -1 or age > max_age_days:
        raise SourceFailure('ted_snapshot_stale')
    return Snapshot(path, manifest, age)
