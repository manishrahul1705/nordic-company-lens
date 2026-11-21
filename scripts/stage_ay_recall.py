"""Equal-taxonomy unseen-100 union recall, replacing only Nordic's replayed facts."""
import collections
import json
import statistics
import sys
from pathlib import Path

JURY = Path('C:/Users/Manish/Downloads/jury-audit')
sys.path.insert(0, str(JURY))
from jury_compare import cat as old_cat, canonical
from stage_ay_field_inventory import OUT


def category(fact):
    field = (fact.get('field') or '').lower()
    native = (fact.get('info_type') or '').lower()
    if field in {'synthesis', 'summary_profile'} or field == 'identifier.brreg_public_page':
        return None
    if native == 'hiring_activity':
        if field == 'registry_update' or field == 'company_news': return 'activity'
        if field == 'annual_accounts_filed': return 'accounts'
    if native == 'external_identifiers': return 'group'
    if native == 'company_description' or field in {'company_description','website.description','website_title','website.verified_url','website.official','site_email','site_phone','site_address','external_profile','external_profiles'}:
        return 'website'
    if native == 'site-3' and field.startswith('hiring.'): return 'jobs'
    if native is None or not native:
        if field in {'role'}: return 'roles'
        if field in {'annual_revenue','revenue','operating_result','annual_result','total_assets','equity','debt','profit_before_tax','assets','reporting_period','auditor_opt_out'}:
            return 'accounts'
        if field == 'company_jobs': return 'jobs'
        if field in {'municipality','nace_code','status_liquidating','activity','register_membership','address','institutional_sector','founded_date','founded','founding_date','postal_address'}:
            return 'identity'
    return old_cat(fact)


def from_envelopes(path):
    facts = []
    for row in map(json.loads, path.open(encoding='utf8')):
        ev = {e['id']: e for e in row['evidence']}
        for claim in row['claims']:
            if claim['availability'] != 'available' or claim['field'].endswith('.section'):
                continue
            e = ev[claim['evidence_ids'][0]]
            facts.append({'orgnr': row['organisation_number'], 'info_type': claim['field'].split('.')[0],
                          'field': claim['field'], 'value': claim['value'], 'source': e['source_url'],
                          'period': claim.get('reporting_period')})
    return facts


def score(agents):
    union = collections.defaultdict(set)
    company_union = collections.defaultdict(set)
    bags = {}
    for name, facts in agents.items():
        bag = collections.defaultdict(set)
        for fact in facts:
            if not fact.get('source') or fact.get('value') is None:
                continue
            fam = category(fact)
            if fam is None: continue
            sig = canonical(fact, fam)
            bag[fam].add(sig)
            union[fam].add(sig)
            company_union[fam].add(sig[0])
        bags[name] = bag
    metrics = {}
    for name, bag in bags.items():
        components = {fam: {'companies': len({s[0] for s in bag[fam]}), 'facts': len(bag[fam]),
                            'union_companies': len(company_union[fam]), 'union_facts': len(union[fam])}
                      for fam in union}
        score_value = 50 * statistics.mean(.7*v['companies']/v['union_companies'] + .3*v['facts']/v['union_facts']
                                           for v in components.values())
        metrics[name] = {'score': round(score_value, 4), 'components': components}
    return {'families': sorted(union), 'agents': dict(sorted(metrics.items(),key=lambda pair:-pair[1]['score'])),
            'rank': 1 + sum(m['score'] > metrics['Nordic']['score'] for m in metrics.values())}


def main():
    allowed = set(json.loads((JURY / 'jury-sample.json').read_text(encoding='utf8'))['active'][:100])
    agents = {}
    for path in (JURY / 'jury-normalized').glob('*.facts.json'):
        name = path.name.removesuffix('.facts.json')
        if name in {'Hardik182005', 'tbd-hackathons'} or name.endswith('.nested-facts'):
            continue
        agents[name] = [x for x in json.loads(path.read_text(encoding='utf8')) if x['orgnr'] in allowed]
    before = score(agents)
    agents['Nordic'] = from_envelopes(OUT / 'jury100-envelopes.jsonl')
    after = score(agents)
    result = {'method': 'jury_compare canonical signature and 0.7 company / 0.3 fact shares, equal family weights; same corrected category applied to every agent',
              'excluded': ['Hardik182005', 'tbd-hackathons', 'nested-facts duplicates'],
              'before': before, 'after': after}
    (OUT / 'corrected-recall.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('families', len(after['families']), after['families'])
    print('Nordic before', before['agents']['Nordic']['score'], 'rank', before['rank'])
    print('Nordic after', after['agents']['Nordic']['score'], 'rank', after['rank'])
    print('agents', len(agents))


if __name__ == '__main__': main()
