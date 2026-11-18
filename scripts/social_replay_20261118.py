"""Offline social replay of long-label-clean-20261118 with the current matcher. Zero HTTP.

For each company with a verified website: every saved page fetched for it on the proof
domain is parsed; social profiles are attributed with the current matcher, filtered by the
collector's group/foreign-page skips, the publication span check, and the shared-profile
check (a profile observed for more than one company is dropped). Each profile counts once
per company (profile_key). Compared against social claims published in the run.
"""
import collections, json, sys
from pathlib import Path
from signalpost.models.envelope import Envelope
from signalpost.sources.text import decode_body
from signalpost.web.html import Page
from signalpost.web.policy import domain, normalize_url, REGISTRY_SOCIAL
from signalpost.web.social import (attributed, observed_profiles, profile_key, profile_url,
                                   matches_profile, social_company_names, context_for_envelope)
from signalpost.web.entity_scope import foreign_entity_page

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'bench/runs/long-label-clean-20261118'
OUT = ROOT / 'bench/reports/social-replay-20261118'
PREFIX = ('social_profile.', 'registry_social.')


def main():
    blobs = RUN / 'state' / 'blobs'
    log = json.load(open(RUN / 'report.json', encoding='utf-8-sig'))['request_log']
    pages_by_org = collections.defaultdict(dict)
    for e in log:
        if e.get('section') == 'website' and e.get('status') == 200 and e.get('content_sha256'):
            pages_by_org[e['organisation_number']].setdefault(e['content_sha256'], e['url'])
    rows = [Envelope.model_validate_json(l) for l in open(RUN / 'envelopes.jsonl', encoding='utf-8-sig')]
    old, new, observed, reasons = {}, {}, collections.defaultdict(set), {}
    for row in rows:
        org = row.organisation_number
        old[org] = {profile_key(c.value['url']): c.value['url'] for c in row.claims
                    if c.field.startswith(PREFIX) and c.availability == 'available'}
        proof = next((c.value for c in row.claims if c.field == 'official_website' and c.availability == 'available'), None)
        if not proof:
            continue
        context = context_for_envelope(row)
        context['website'] = row.run.legal_identity.get('registered_website')
        is_group = bool(proof.get('other_orgnrs')) or proof.get('relationship_note') == 'group_site'
        target = domain(proof.get('final_url') or proof.get('proof_page_url') or '')
        found = {}
        social = profile_url(normalize_url(context.get('website')) or '')
        if social and domain(social) in REGISTRY_SOCIAL and matches_profile(social, social_company_names(context)):
            found[profile_key(social)] = (social, 'registry website field', None)
        for sha, url in pages_by_org.get(org, {}).items():
            path = blobs / sha
            if domain(url) != target or not path.exists():
                continue
            body = path.read_bytes()
            try:
                page = Page(body, url)
            except Exception:
                continue
            observed_all = observed_profiles(page)
            for u in observed_all:
                observed[profile_key(u)].add(org)
            if is_group or foreign_entity_page(page, org, context.get('name'), check_ids=True):
                continue
            text = decode_body(body)
            for u, span in attributed(page, proof, context).items():
                if not span or len(span) > 300 or span not in text:
                    continue  # publication check
                found.setdefault(profile_key(u), (u, url, span))
        new[org] = found
        reasons[org] = social_company_names(context)
    for org, found in new.items():
        for key in found:
            observed[key].add(org)
    shared = {k for k, owners in observed.items() if len(owners) > 1}
    for org in new:
        new[org] = {k: v for k, v in new[org].items() if k not in shared}

    def table(side, values):
        per = collections.defaultdict(lambda: [set(), 0])
        for org, profiles in values.items():
            for key in profiles:
                p = key.split('/')[0]
                per[p][0].add(org); per[p][1] += 1
        return {p: {'companies': len(v[0]), 'claims': v[1]} for p, v in sorted(per.items())}
    before, after = table('old', old), table('new', {o: v for o, v in new.items()})
    added, removed = [], []
    for org in sorted(set(old) | set(new)):
        n, o = new.get(org, {}), old.get(org, {})
        name = next((r.run.legal_identity.get('legal_name') for r in rows if r.organisation_number == org), '')
        for key in sorted(set(n) - set(o)):
            u, page, span = n[key]
            added.append({'orgnr': org, 'company': name, 'url': u, 'page': page, 'span': span,
                          'matched_against': reasons.get(org)})
        for key in sorted(set(o) - set(n)):
            removed.append({'orgnr': org, 'company': name, 'url': o[key],
                            'shared': key in shared})
    result = {'http_requests': 0, 'companies_with_verified_website': len(new),
              'before': before, 'after': after, 'added': added, 'removed': removed,
              'shared_profiles_dropped': len(shared)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'social-replay.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('added', 'removed')}, indent=1))
    print('added', len(added), 'removed', len(removed))
    for a in added: print('+', a['orgnr'], a['company'], a['url'], '|', (a['span'] or '')[:80])
    for r in removed: print('-', r['orgnr'], r['company'], r['url'], 'shared' if r['shared'] else '')


if __name__ == '__main__':
    main()
