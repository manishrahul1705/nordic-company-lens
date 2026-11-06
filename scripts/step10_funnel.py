"""Read saved benchmark evidence only; never fetch or resolve a URL."""
import argparse
import collections
import csv
import json
import random
import re
import html
from types import SimpleNamespace
from pathlib import Path
from signalpost.web.policy import domain, normalize_url, FREE_MAIL, SOCIAL, DIRECTORIES
from signalpost.web.html import Page
from signalpost.sources.text import decode_body
from signalpost.web.social import observed_profiles, attributed, context_for_envelope
from signalpost.models.envelope import Envelope


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in (args.run / 'envelopes.jsonl').open(encoding='utf8')]
    report = json.loads((args.run / 'report.json').read_text(encoding='utf8'))
    by_org = collections.defaultdict(list)
    for request in report['request_log']:
        by_org[request['organisation_number']].append(request)
    with (args.run/'inputs/registry.csv').open(encoding='utf-8-sig', newline='') as f:
        registry = {r['organisasjonsnummer']: r for r in csv.DictReader(f)}
    categories = ['registry_homepage', 'registry_email', 'subunit', 'guessed']
    counts = {c: collections.Counter() for c in categories}
    reasons = {c: collections.Counter() for c in categories}
    failed = []
    social = []
    detail = []
    def host(value):
        url = normalize_url(value)
        d = domain(url) if url else ''
        return d if d not in FREE_MAIL | SOCIAL | DIRECTORIES else ''
    def email(value):
        return host(str(value).rsplit('@', 1)[-1]) if '@' in str(value) else ''
    for row in rows:
        org = row['organisation_number']
        name = row['run']['legal_identity'].get('legal_name')
        reg = registry.get(org, {})
        fields = {c['field']:c['value'] for c in row['claims'] if c['availability']=='available'}
        reg = {'hjemmeside':fields.get('identity.registered_website'), 'epostadresse':fields.get('identity.registered_email'), **reg}
        nominations = {c: set() for c in categories}
        if d := host(reg.get('hjemmeside')): nominations['registry_homepage'].add(d)
        if d := email(reg.get('epostadresse')): nominations['registry_email'].add(d)
        for c in row['claims']:
            if c['availability'] != 'available': continue
            if c['field'].startswith('subunits.detail.'):
                if c['field'].endswith('.registered_website') and (d := host(c['value'])): nominations['subunit'].add(d)
                if c['field'].endswith('.registered_email') and (d := email(c['value'])): nominations['subunit'].add(d)
        attempts = []
        for e in row['errors']:
            if e['code'] == 'website_candidates':
                attempts += json.loads(e['message'])
        for a in attempts:
            if a.get('origin') in {'legal_name_slug', 'subunit_name_slug'} and a.get('domain'):
                nominations['guessed'].add(a['domain'])
        requests = by_org[org]
        blobs = args.run/'state/blobs'
        pages = {}
        for request in requests:
            sha = request.get('content_sha256') or request.get('response_sha256')
            if request.get('status') != 200 or not sha: continue
            url = request['url']
            if '/robots.txt' in url or domain(url) in {'brreg.no','nav.no','wikidata.org'}: continue
            body_path = blobs/sha
            if not body_path.exists(): continue
            body = body_path.read_bytes()
            text = decode_body(body)
            if '<html' not in text.lower() and '<!doctype html' not in text.lower(): continue
            match = re.search(r'<title\b[^>]*>(.*?)</title\s*>', text, re.I | re.S)
            pages[url] = SimpleNamespace(title=html.unescape(match[1]).strip() if match else '(no title)', body=body)
        proof = next((c for c in row['claims'] if c['field']=='official_website' and c['availability']=='available'), None)
        scope = row['run'].get('refresh',{}).get('website',{}).get('entity_scope',{})
        for category, domains in nominations.items():
            counter = counts[category]
            counter['companies_present'] += bool(domains)
            counter['domains_present'] += len(domains)
            stage = collections.Counter()
            for d in domains:
                logs = [r for r in requests if domain(r['url']) == d and '/robots.txt' not in r['url']]
                resolved = any(r.get('status') or r.get('request_sent_seconds') is not None for r in logs)
                fetched = any(r.get('status') == 200 for r in logs)
                diagnostics = [a for a in attempts if a.get('domain') == d]
                passed = any(a.get('level') == 'VERIFIED' for a in diagnostics) or bool(proof and domain(proof['value']['final_url']) == d)
                withheld = bool(scope.get('website_status') == 'ambiguous' and scope.get('website_reason') == 'group/shared site' and fetched)
                status = [a.get('reason') for a in diagnostics if a.get('level') in {'LOW','MEDIUM','REJECT','BLOCKED'}]
                reason = next((r for r in status if r in {'foreign_orgnr','name_only','insufficient_owner_proof','parked','unverified_multi_entity_site','name_without_suffix_insufficient_contacts_or_domain'}), status[-1] if status else 'no_proof_diagnostic')
                for key,value in [('resolved_observed',resolved),('fetched_ok',fetched),('proof_passed',passed),('proof_failed',fetched and not passed),('group_withheld',withheld)]:
                    counter[key+'_domains'] += bool(value); stage[key] += bool(value)
                if fetched and not passed:
                    reasons[category][reason] += 1
                    titles = [{'url':url,'title':p.title} for url,p in pages.items() if domain(url)==d]
                    failed.append({'organisation_number':org,'company':name,'category':category,'domain':d,'reason':reason,'pages':titles})
                detail.append({'organisation_number':org,'category':category,'domain':d,'resolved_observed':resolved,'fetched_ok':fetched,'proof_passed':passed,'reason':reason,'group_withheld':withheld})
            for key,value in stage.items(): counter[key+'_companies'] += bool(value)
        if proof:
            env = Envelope.model_validate(row)
            context = context_for_envelope(env)
            published = {c['value']['url'] for c in row['claims'] if c['field'].startswith('social_profile.') and c['availability']=='available'}
            observed = {}
            for url,page in pages.items():
                if domain(url) != domain(proof['value']['final_url']):continue
                page = Page(page.body, url)
                eligible = attributed(page, proof['value'], context)
                for link in observed_profiles(page):
                    if link not in published:
                        observed.setdefault(link,{'url':link,'page':url,'eligible_under_existing_rule':link in eligible,'title':page.title})
            social.append({'organisation_number':org,'company':name,'website':proof['value']['final_url'],'missing_observed_links':list(observed.values()),'pages_checked':list(pages)})
    unique = {(r['organisation_number'],r['domain']):r for r in failed}
    sample = random.Random(10).sample(list(unique.values()),min(30,len(unique)))
    summary = {'run':str(args.run),'companies':len(rows),'definitions':'Categories overlap. Domains are registrable domains. Resolves is observed positive only (HTTP status or request-sent marker); absent DNS telemetry is not called NXDOMAIN. Fetched OK excludes robots. Proof failure is fetched 200 without verified proof. No network requests.', 'counts':{k:dict(v) for k,v in counts.items()},'proof_failure_reasons':{k:dict(v) for k,v in reasons.items()},'sample_30':sample,'published_websites_audited':len(social),'social_missing_observed_links':sum(len(s['missing_observed_links']) for s in social)}
    for filename,data in [('funnel.json',summary),('funnel-domains.json',detail),('social-audit.json',social)]:
        (args.out/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='sample_30'},ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
