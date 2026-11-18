"""Offline brand replay of long-label-clean-20261118: old vs fixed extract_public_brand. Zero HTTP.

For each company with a verified website, the brand is recomputed on the saved proof page
(the page the collector extracted the brand from) with three versions of the function:
HEAD (old), HEAD with only the encoding-literal fix (mojibake), and the current code.
A brand counts as published only if it also passes the span check publish() applies.
"""
import json, re, html, subprocess, collections
from pathlib import Path
from signalpost.models.envelope import Envelope
from signalpost.sources.text import decode_body
from signalpost.web.html import Page
from signalpost.web.candidates import legal_name
from signalpost.web.collector import extract_public_brand as new_fn

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'bench/runs/long-label-clean-20261118'
OUT = ROOT / 'bench/reports/brand-replay-20261118'


def old_function(fix_mojibake):
    src = subprocess.run(['git', 'show', '2edc83b:src/signalpost/web/collector.py'], capture_output=True,
                         cwd=ROOT, check=True).stdout.decode('utf8')
    fn = src[src.index('def extract_public_brand'):src.index('def registry_context')]
    if fix_mojibake:
        fn = (fn.replace('â€“', '–').replace('bÃ¥tutstyr', 'båtutstyr').replace('vilk[aÃ¥]r', 'vilk[aå]r')
                .replace('A-ZÃ†Ã˜Ã…a-zÃ¦Ã¸Ã¥', 'A-ZÆØÅa-zæøå'))
    scope = {'re': re, 'html': html, 'legal_name': legal_name, 'Page': Page}
    exec(fn, scope)
    return scope['extract_public_brand']


def published(fn, page, body, name):
    brand = fn(page, name)
    if not brand:
        return None
    span = (page.span_for(brand) or '')[:150]
    return brand if span and span in decode_body(body) else None


def main():
    old, mid = old_function(False), old_function(True)
    blobs = RUN / 'state' / 'blobs'
    changes, totals, sanity = [], collections.Counter(), {'matches_run': 0, 'differs_from_run': 0}
    for line in open(RUN / 'envelopes.jsonl', encoding='utf-8-sig'):
        row = Envelope.model_validate_json(line)
        site = next((c for c in row.claims if c.field == 'official_website' and c.availability == 'available'), None)
        if not site:
            continue
        ev = {e.id: e for e in row.evidence}
        brand_claim = next((c for c in row.claims if c.field == 'public_brand' and c.availability == 'available'), None)
        pages = [ev[i] for i in (brand_claim or site).evidence_ids if i in ev and ev[i].source_class == 'company_owned']
        if not pages:
            continue
        e = pages[0]
        body = (blobs / e.content_sha256).read_bytes()
        page = Page(body, e.source_url)
        name = row.run.legal_identity.get('legal_name')
        a, b, c = published(old, page, body, name), published(mid, page, body, name), published(new_fn, page, body, name)
        totals['companies'] += 1
        totals['old_published'] += bool(a); totals['new_published'] += bool(c)
        run_value = brand_claim.value if brand_claim else None
        if a == run_value: sanity['matches_run'] += 1
        else:
            sanity['differs_from_run'] += 1
            sanity.setdefault('differs', []).append({'orgnr': row.organisation_number, 'run': run_value, 'recomputed_old': a, 'page': e.source_url})
        if a != c:
            changes.append({'orgnr': row.organisation_number, 'legal_name': name, 'page': e.source_url,
                            'title': page.title, 'og_site_name': page.meta.get('og:site_name'),
                            'old': a, 'new': c,
                            'cause': 'encoding literals' if a != b and b == c else 'page words' if a == b else 'both'})
    result = {'http_requests': 0, **totals, 'old_recompute_vs_published': dict(sanity),
              'changed': len(changes), 'changes': changes}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'brand-replay.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'changes'}, ensure_ascii=False))
    for x in changes:
        print(x['orgnr'], '|', x['legal_name'], '|', repr(x['old']), '->', repr(x['new']), '|', x['cause'], '| title:', x['title'][:80])


if __name__ == '__main__':
    main()
