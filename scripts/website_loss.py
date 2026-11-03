"""Explain the furthest recorded website-discovery stage without making requests."""
import argparse
from collections import Counter
import json
from pathlib import Path


def diagnose(row):
    attempts=[]
    errors=[e for e in row.get('errors',[]) if e['section']=='website']
    for e in errors:
        if e['code']=='website_candidates':
            try:attempts.extend(json.loads(e['message']))
            except (ValueError,TypeError):pass
    reasons={str(x.get('reason','')) for x in attempts} | {e['code'] for e in errors}
    state=row['run']['sections'].get('website')
    if state=='available':return None
    # LOW is also assigned to DNS exceptions; only proof-scoring records have
    # points/signals. Do not call an unfetched NXDOMAIN guess a fetched page.
    fetched=any(200<=x.get('status',0)<300 or 'points' in x or x.get('level') in {'MEDIUM','HIGH','VERIFIED','REJECT'} for x in attempts)
    if state=='ambiguous':reason='ambiguous (name-only or competing candidates)';stage='ownership proof'
    elif state=='blocked' or reasons & {'robots','robots_unavailable','http_blocked','block_page'}:reason='robots or blocked';stage='HTTP / policy'
    elif 'foreign_orgnr' in reasons:reason='proof conflict (other orgnr)';stage='ownership proof'
    elif reasons & {'website_budget_exhausted','budget_exhausted','deadline'}:reason='budget exhausted';stage='request budget'
    elif reasons & {'website_connect_error','website_timeout','dns_timeout','dns_unavailable','dns_error'}:reason='TLS-connect failure';stage='connection / DNS timeout'
    elif fetched:reason='fetched but no proof';stage='ownership proof'
    elif attempts and reasons <= {'no_such_domain','', 'website_candidates'}:reason='all candidates DNS-missing';stage='DNS'
    elif not attempts:reason='no candidates generated';stage='nomination'
    else:reason='fetched but no proof';stage='HTTP non-success or insufficient recorded proof'
    return {'organisation_number':row['organisation_number'],
            'name':next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name' and c['availability']=='available'),None),
            'state':state,'furthest_stage':stage,'reason':reason,
            'candidates':list(dict.fromkeys(x['domain'] for x in attempts if x.get('domain'))),
            'diagnostics':attempts,'error_codes':[e['code'] for e in errors]}


def analyze(run):
    rows=list(map(json.loads,(run/'envelopes.jsonl').read_text(encoding='utf8').splitlines()))
    missing=[d for r in rows if (d:=diagnose(r))]
    counts=Counter(d['reason'] for d in missing)
    return {'run':str(run),'companies':len(rows),'available':len(rows)-len(missing),'counts':dict(counts.most_common()),
            'companies_without_available_website':missing,
            'top_three_examples':{reason:[d for d in missing if d['reason']==reason][:10] for reason,_ in counts.most_common(3)},
            'interpretation':'Reasons are exclusive stop buckets from recorded candidate diagnostics, not inferred exhaustive absence. Budget includes request/deadline limits. DNS/transient TLS failures are grouped conservatively when low-level transport messages are unavailable.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--scale-run',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report={'primary':analyze(a.run)}
    if a.scale_run:report['scale']=analyze(a.scale_run)
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'website-loss.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    lines=['# Website loss diagnosis','','This is a read-only analysis of saved run diagnostics. No network requests or behavior changes.','']
    for label,data in report.items():
        lines += ['## '+label+' — '+str(data['companies'])+' companies','',f"Available: {data['available']}; missing: {data['companies']-data['available']}.",'','| Stop reason | Companies |','|---|---:|']
        lines += [f'| {k} | {v} |' for k,v in data['counts'].items()]
        lines += ['',data['interpretation'],'']
        if label=='primary':
            for reason,examples in data['top_three_examples'].items():
                lines+=['### '+reason,'','| Company | Name | Candidate domains |','|---|---|---|']
                lines += ['| '+d['organisation_number']+' | '+str(d['name'])+' | '+', '.join(d['candidates'])+' |' for d in examples]
                if len(examples)<10:lines+=['',f'Only {len(examples)} companies occupy this bucket; every example is listed.']
                lines+=['']
    lines+=['## Recovery priority','','Choose recovery work from the measured buckets: DNS-missing legal-name guesses need new nominations (Wikidata, then optional search); fetched/name-only pages need additional ownership evidence; budget stops need enough reserved proof requests. More budget does not make absent DNS guesses valid, and none of these bucket counts is a measured recovery promise.']
    (a.output/'website-loss.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({k:{'available':v['available'],'counts':v['counts']} for k,v in report.items()}))


if __name__=='__main__':main()
