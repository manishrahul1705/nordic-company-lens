"""Compare the frozen Stage C live runs without normalising away differences."""
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/stage-c'


def main():
    OUT.mkdir(exist_ok=True);snapshots={};result={}
    for label in ('before','after'):
        run=ROOT/('bench/runs/stage-c-'+label)
        rows=[json.loads(line) for line in (run/'envelopes.jsonl').open(encoding='utf8')]
        claims={r['organisation_number']:{c['field']:c for c in r['claims'] if c['availability']=='available' and c['value'] is not None} for r in rows}
        snapshots[label]=claims
        report=json.loads((run/'report.json').read_text(encoding='utf8'));execution=json.loads((run/'execution.json').read_text())
        counts={k:0 for k in ('identity','people','locations','financials','website','social','jobs','activity','news')}
        for cs in claims.values():
            for key,family in [('identity','identity'),('people','roles'),('locations','subunits'),('financials','accounts'),('website','website'),('jobs','hiring'),('activity','activity')]:counts[key]+=any(c['family']==family for c in cs.values())
            counts['social']+=any(c['field'].startswith(('social_profile.','registry_social.')) for c in cs.values())
            counts['news']+=any(c['field'].startswith('dated_item.') for c in cs.values())
        ids=[[org,sorted(c['id'] for c in cs.values())] for org,cs in sorted(claims.items())]
        result[label]={'companies':len(rows),'published_claims':sum(map(len,claims.values())),
            'families':dict(Counter(c['family'] for cs in claims.values() for c in cs.values())),
            'published_companies_by_family':counts,'published_ids_sha256':hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest(),
            'requests':report['requests'],'deadline_hits':report['deadline_hits'],'exit_code':execution['exit_code'],'wall_seconds':execution['wall_seconds']}
    assert snapshots['before'].keys()==snapshots['after'].keys()
    differences=[]
    for org,old in snapshots['before'].items():
        new=snapshots['after'][org]
        for field in old.keys()|new.keys():
            a=old.get(field);b=new.get(field)
            if (a or {}).get('id')!=(b or {}).get('id'):differences.append({'orgnr':org,'field':field,'before':a,'after':b})
    result['identical_published_counts_and_ids']=not differences and result['before']['published_companies_by_family']==result['after']['published_companies_by_family']
    result['different_fields']=len(differences)
    for name,value in [('live-comparison.json',result),('live-differences.json',differences)]:
        (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
    if not result['identical_published_counts_and_ids']:raise SystemExit(1)

if __name__=='__main__':main()
