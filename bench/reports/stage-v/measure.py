"""Section fill, citation resolution and sentence counts over a run's envelopes; HTTP by host vs a control."""
import json,sys,collections
SECTIONS=('what_it_does','scale','leadership','changes','reach','standing','not_established')
rows=[json.loads(l) for l in open(sys.argv[1],encoding='utf8')]
fill=collections.Counter();sent=collections.Counter();unresolved=[];empty=collections.defaultdict(list);kinds=collections.Counter()
for r in rows:
    syn=r['run']['synthesis'];ids={c['id'] for c in r['claims']}|{c['id'] for c in syn['change_claims']}
    ids|={c['id'] for c in ((syn.get('cohort') or {}).get('role_holdings') or [])}
    for k in SECTIONS:
        ss=syn['sections'][k];sent[k]+=len(ss)
        if ss:fill[k]+=1
        else:empty[k].append(r['organisation_number'])
        for s in ss:
            if not s['claim_ids'] or set(s['claim_ids'])-ids:unresolved.append((r['organisation_number'],k,s['text'][:80]))
        if k=='standing':
            t=ss[0]['text'] if ss else ''
            kinds['percentile' if '% of them.' in t else 'too_thin' if 'needed for a comparison' in t else 'no_comparable_in_run' if t.startswith('No other company in this run') else 'not_compared']+=1
def http(p):
    r=json.load(open(p));return r['requests'],dict(collections.Counter(e['host'] for e in r['request_log']).most_common(8))
out={'companies':len(rows),'filled':{k:fill[k] for k in SECTIONS},'empty':{k:len(empty[k]) for k in SECTIONS},
     'sentences':{k:sent[k] for k in SECTIONS},'unresolved_citations':unresolved,'standing_kinds':dict(kinds),
     'http':{'stage_v':http(sys.argv[2]),'revision4_control_2026-11-16':http(sys.argv[3])}}
print(json.dumps(out,indent=1))
