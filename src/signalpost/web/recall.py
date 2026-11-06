"""Candidate nominations from already-held sources; never ownership proof."""
import gzip
import json
import re
from functools import lru_cache
from pathlib import Path
from .policy import domain, FREE_MAIL, SOCIAL, DIRECTORIES, normalize_url


@lru_cache(maxsize=1)
def registry_domains():
    try:
        path = Path(__file__).resolve().parents[1] / 'data/registry_domains.json.gz'
        with gzip.open(path, 'rt', encoding='utf8') as f:
            return json.load(f)['domains']
    except (OSError, ValueError, KeyError):
        return {}


def shared_owners(host):
    return set(registry_domains().get(host, []))


def annual_domains(envelope, blobs):
    """Scan retained account/report text only; no PDF/report download is made."""
    from ..sources.text import decode_body
    refs = {r for c in envelope.claims if c.family == 'accounts' for r in c.evidence_ids}
    seen = set(); result = []
    for e in envelope.evidence:
        if e.id not in refs or e.content_sha256 in seen:continue
        seen.add(e.content_sha256)
        path = blobs.directory/e.content_sha256
        if not path.exists():continue
        body = path.read_bytes()
        # Binary PDFs are not text; don't mistake byte strings for site evidence.
        if body.startswith(b'%PDF'):continue
        text = decode_body(body)
        for match in re.finditer(r'(?:https?://|www\.)[a-zA-Z0-9æøåÆØÅ.-]+(?:/[^\s"<>\\]*)?', text):
            url = normalize_url(match.group().rstrip('.,;)'))
            host = domain(url) if url else ''
            if not host or host in FREE_MAIL | SOCIAL | DIRECTORIES | {'brreg.no','nav.no','w3.org','xbrl.org','ifrs.org','schema.org'}:
                continue
            if host not in result:result.append(host)
            if len(result) == 3:return result
    return result


def redirect_names_company(page, org, context):
    from .proof import orgnrs
    from .candidates import legal_name
    allowed = {org, *[u['orgnr'] for u in context.get('subunits', [])]}
    if orgnrs(page.owner_text) & allowed:return True
    text = ' '.join(re.findall(r'\w+', (page.title + ' ' + page.owner_text).casefold()))
    return any((core := legal_name(name)) and re.search(r'(?<!\w)' + re.escape(core) + r'(?!\w)', text)
               for name in [context.get('name'), *[u.get('name') for u in context.get('subunits', [])]])

