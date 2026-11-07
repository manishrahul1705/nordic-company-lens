"""Measure primary briefings and select an unchanged stratified review sample."""
import argparse
import collections
import json
import random
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    out = Path('bench/reports/s6-step17')
    pools = collections.defaultdict(list)
    counts = collections.Counter()
    facts = collections.Counter()
    lengths = collections.Counter()
    for line in (args.run/'envelopes.jsonl').open(encoding='utf-8'):
        row = json.loads(line)
        claims = {c['id']: c for c in row['claims'] if c['availability']=='available'}
        fields = {c['field']:c for c in claims.values()}
        facts.update(c['family'] for c in claims.values())
        brief = row['run']['synthesis']['analyst_brief']
        assert row['run']['synthesis']['generator']['version']=='5'
        counts.update(s['sentence_type'] for s in brief['sentences'])
        lengths[len(brief['sentences'])] += 1
        site = 'official_website' in fields
        article = any(f.startswith('dated_item.') for f in fields)
        # Only six companies in this batch have all three of site, company news
        # and revenue. Review all six, then four additional fact-rich sites.
        group = 'rich' if site and article and 'accounts.revenue' in fields else 'medium' if site else 'sparse'
        contexts = {c['id']:c for c in brief['context_claims']}
        evidence = {e['id']:e for e in row['evidence']}
        sentences = []
        for sentence in brief['sentences']:
            support = [claims.get(cid) or contexts[cid] for cid in sentence['claim_ids']]
            ids = sorted({eid for c in support for eid in c['evidence_ids']})
            sentences.append({**sentence,'support':support,'evidence':[evidence[eid] for eid in ids]})
        pools[group].append({'orgnr':row['organisation_number'],'name':fields.get('identity.legal_name',{}).get('value'),'fact_count':len(claims),
                             'group':group,'sentences':sentences})
    rng = random.Random(20261107)
    strict_rich_count = len(pools['rich'])
    rich = rng.sample(pools['rich'],min(10,strict_rich_count))
    extras = rng.sample(sorted(pools['medium'],key=lambda r:(-r['fact_count'],r['orgnr']))[:30],10-len(rich))
    for item in extras:
        pools['medium'].remove(item)
        item['group']='rich'
        item['rich_supplement']='Website and financial facts; no company-published article'
    rich += extras
    pools['rich'].extend(extras)
    sample = rich + [item for group in ('medium','sparse') for item in rng.sample(pools[group],10)]
    (out/'review-sample.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2),encoding='utf-8')
    metrics = {'run':str(args.run),'sentence_types':counts,'sentence_lengths':lengths,
               'primary_sentences':sum(counts.values()),'mean_sentences':sum(counts.values())/1000,
               'claims':facts,'total_claims':sum(facts.values()),'cohorts':{k:len(v) for k,v in pools.items()},
               'strict_rich_population':strict_rich_count,'rich_review_supplement':len(extras)}
    (out/'summary-metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    lines=['# Six final analyst briefings','']
    for group in ('rich','medium','sparse'):
        for item in [s for s in sample if s['group']==group][:2]:
            lines += ['## '+item['name']+' / '+item['orgnr']+' ('+group+')','']
            lines += [s['text']+' '+ ' '.join('`'+cid+'`' for cid in s['claim_ids'])+'\n' for s in item['sentences']]
    (out/'EXAMPLES.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(metrics,indent=2))


if __name__=='__main__': main()
