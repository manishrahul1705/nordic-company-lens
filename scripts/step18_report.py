"""Saved-output metrics and deterministic Step 18 review selection; no requests."""
import argparse
import collections
import json
from pathlib import Path
import random
import shutil
from verify_registry_changes import check


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('run',type=Path)
    args=parser.parse_args()
    out=Path('bench/reports/s6-step18')
    baseline=Path('bench/runs/20261107T052914870839Z-acaca26')
    old=set();old_events=set()
    for line in (baseline/'envelopes.jsonl').open(encoding='utf-8'):
        row=json.loads(line)
        old.update(c['id'] for c in row['claims'] if c['availability']=='available' and c['field'].startswith('registry_change.'))
        old_events.update((row['organisation_number'],c['value']['event_id']) for c in row['claims'] if c['availability']=='available' and c['field'].startswith('registry_change.'))
    counts=collections.Counter();types=collections.Counter();lengths=collections.Counter()
    briefs=[];events=[];examples=[];checks=[]
    example_orgs={'922828172','993919675','935180678','936855865','926077422','932386933'}
    for line in (args.run/'envelopes.jsonl').open(encoding='utf-8'):
        row=json.loads(line);org=row['organisation_number']
        claims={c['id']:c for c in row['claims'] if c['availability']=='available'}
        fields={c['field']:c for c in claims.values()}
        counts.update(c['family'] for c in claims.values())
        brief=row['run']['synthesis']['analyst_brief']
        assert row['run']['synthesis']['generator']['version']=='6'
        lengths[len(brief['sentences'])]+=1
        contexts={c['id']:c for c in brief['context_claims']}
        evidence={e['id']:e for e in row['evidence']}
        sentences=[]
        for s in brief['sentences']:
            support=[claims.get(cid) or contexts[cid] for cid in s['claim_ids']]
            ids={eid for c in support for eid in c['evidence_ids']}
            sentences.append({**s,'support':support,'evidence':[evidence[eid] for eid in sorted(ids)]})
        record={'orgnr':org,'name':fields.get('identity.legal_name',{}).get('value'),'sentences':sentences}
        briefs.append(record)
        if org in example_orgs:examples.append(record)
        for c in claims.values():
            if not c['field'].startswith('registry_change.'):continue
            types[c['value']['title']]+=1
            if c['id'] not in old:
                ev=[evidence[eid] for eid in c['evidence_ids']]
                events.append({'organisation_number':org,'name':record['name'],'claim':c,'evidence':ev})
    rng=random.Random(20261108)
    distinct={(e['organisation_number'],e['claim']['value']['event_id']):e for e in events
              if (e['organisation_number'],e['claim']['value']['event_id']) not in old_events}
    selected=rng.sample(list(distinct.values()),20)
    for item in selected:
        proof=check({'organisation_number':item['organisation_number'],'evidence':item['evidence']},item['claim'],args.run/'state/blobs')
        item['independent_check']=proof
        ev=item['evidence'][0]
        raw=json.loads((args.run/'state/blobs'/ev['content_sha256']).read_bytes())
        from verify_registry_changes import pointer
        item['raw_record']=pointer(raw,ev['locator'].split('/endringer/')[0])
        checks.append(proof)
    selected_briefs=rng.sample(briefs,10)
    report=json.loads((args.run/'report.json').read_text(encoding='utf-8'))
    metrics={'run':str(args.run),'claims':counts,'total_facts':sum(counts.values()),'registry_titles':types,
        'registry_announcement_claims':sum(types.values()),'new_registry_claims':len(events),'new_distinct_event_records':len(distinct),
        'retained_previous_announcements':sum(types.values())-len(events),
        'primary_sentences':sum(k*v for k,v in lengths.items()),'sentence_lengths':lengths,
        'requests':report['requests'],'mean_requests':report['amortized_requests_per_company'],
        'max_requests':report['max_requests_per_company'],
        'feed_requests':sum('/oppdateringer/' in e['url'] for e in report['request_log']),
        'deadlines':report['deadline_hits'],'warnings':report['warnings'],'synthesis':report['synthesis']}
    for name,value in [('metrics.json',metrics),('event-review.json',selected),('briefing-review.json',selected_briefs)]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    for name in ['scoreboard.json','execution.json']:shutil.copyfile(args.run/name,out/('benchmark-'+name))
    text=['# Six polished company briefings','']
    for item in examples:
        text+=['## '+item['name']+' / '+item['orgnr'],'']
        text += [s['text']+' '+ ' '.join('`'+cid+'`' for cid in s['claim_ids'])+'\n' for s in item['sentences']]
    (out/'EXAMPLES.md').write_text('\n'.join(text),encoding='utf-8')
    print(json.dumps(metrics,indent=2))


if __name__=='__main__':main()
