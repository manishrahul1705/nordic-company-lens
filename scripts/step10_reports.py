"""Render saved Step 10 diagnostics and differential review inventories; no network."""
import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding='utf8'))


def cell(value):
    return str(value or '').replace('|', '/').replace('\n', ' ').replace('\r', '')


def baseline(root):
    data = load(root/'baseline/funnel.json')
    lines = ['# Saved-run funnel diagnosis', '', data['definitions'], '',
             'Source: `' + data['run'] + '`. No new crawl was used for diagnosis.', '',
             '| Candidate source | Companies nominated | Domains nominated/tried | Observed resolves | Fetched OK | Proof passed | Proof failed | Group withheld |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for source, counts in data['counts'].items():
        keys = ['companies_present','domains_present','resolved_observed_domains','fetched_ok_domains','proof_passed_domains','proof_failed_domains','group_withheld_domains']
        lines.append('| ' + source + ' | ' + ' | '.join(str(counts[k]) for k in keys) + ' |')
    lines += ['', 'The categories overlap; their proof totals must not be added. Subunit domains are from retained registry records. Resolution is a lower bound because the old run did not retain every DNS outcome.', '',
              '| Source | Failed proof reason | Domains |', '|---|---|---:|']
    for source, reasons in data['proof_failure_reasons'].items():
        for reason, count in reasons.items():lines.append(f'| {source} | {reason} | {count} |')
    lines += ['', '## Thirty seeded fetched-OK / unverified cases', '',
              'Seed 10; one company/domain per sampled item. Titles and reasons are from saved responses and diagnostics, not live checks.', '',
              '| Company / orgnr | Domain | Page title(s) | Reason |', '|---|---|---|---|']
    for item in data['sample_30']:
        lines.append('| ' + ' | '.join(cell(v) for v in [item['company']+' / '+item['organisation_number'],item['domain'], '; '.join(p['title'] for p in item['pages']),item['reason']])+' |')
    (root/'FUNNEL.md').write_text('\n'.join(lines)+'\n', encoding='utf8')


def inventory(root, previous, current):
    before = {r['organisation_number']:r for r in map(json.loads,(previous/'envelopes.jsonl').read_text(encoding='utf8').splitlines())}
    after = list(map(json.loads,(current/'envelopes.jsonl').read_text(encoding='utf8').splitlines()))
    result = []
    for row in after:
        old = before.get(row['organisation_number'], {})
        known = {(c['field'],json.dumps(c['value'],sort_keys=True,ensure_ascii=False)) for c in old.get('claims',[]) if c['availability']=='available'}
        name = next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),row['organisation_number'])
        evidence = {e['id']:e for e in row['evidence']}
        for c in row['claims']:
            if c['availability']!='available' or not (c['field']=='official_website' or c['field'].startswith(('social_profile.','registry_social.','hiring.site_job.'))):continue
            if (c['field'],json.dumps(c['value'],sort_keys=True,ensure_ascii=False)) in known:continue
            result.append({'organisation_number':row['organisation_number'],'company':name,'field':c['field'],'value':c['value'],
                           'evidence':[evidence[e] for e in c['evidence_ids'] if e in evidence], 'verdict':'pending'})
    (root/'new-items.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    old_profiles={r['organisation_number']:r for r in map(json.loads,(previous/'profiles.jsonl').read_text(encoding='utf8').splitlines())}
    new_profiles=list(map(json.loads,(current/'profiles.jsonl').read_text(encoding='utf8').splitlines()))
    locations=[]
    for profile in new_profiles:
        org=profile['organisation_number']
        def values(p):
            section=(p.get('evidence') or {}).get('locations') or {}
            return (section.get('value') or {}).get('locations') or []
        previous_values=values(old_profiles.get(org,{}))
        previous_addresses={json.dumps(v.get('address'),sort_keys=True,ensure_ascii=False) for v in previous_values}
        for value in values(profile):
            if value.get('type')=='registered_business_address' and json.dumps(value['address'],sort_keys=True,ensure_ascii=False) not in previous_addresses:
                row=next(r for r in after if r['organisation_number']==org)
                claim=next(c for c in row['claims'] if c['field']=='identity.registered_address')
                evidence={e['id']:e for e in row['evidence']}
                locations.append({'organisation_number':org,'value':value,'claim_id':claim['id'],
                                  'evidence':[evidence[e] for e in claim['evidence_ids']], 'verdict':'pending'})
    (root/'new-locations.json').write_text(json.dumps(locations,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print({'review_items':len(result)})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('bench/reports/s6-step10'))
    parser.add_argument('--previous',type=Path)
    parser.add_argument('--current',type=Path)
    args=parser.parse_args()
    baseline(args.out)
    if args.current:inventory(args.out,args.previous,args.current)


if __name__=='__main__':main()
