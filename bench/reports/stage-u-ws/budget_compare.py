"""HTTP budget comparison between runs: totals, TED share, pooled cap, per-company cap hits."""
import json,sys,collections
out={}
for name,path in (a.split('=',1) for a in sys.argv[1:]):
    r=json.load(open(path))
    log=r['request_log'];by=collections.Counter(e['organisation_number'] for e in log)
    ted=[e for e in log if e.get('host') in ('api.ted.europa.eu','ted.europa.eu')]
    caps=sorted(o for o,n in by.items() if n>=40 and o.isdigit())
    errs=collections.Counter(e.get('error') for e in log if e.get('error') in ('budget_exhausted','company_budget_exhausted'))
    out[name]={'requests':r['requests'],'request_log':len(log),'pooled_cap':r['limits'].get('max_requests') if isinstance(r.get('limits'),dict) else None,
        'limits':r.get('limits'),'ted_requests':len(ted),'ted_search':sum(e['host']=='api.ted.europa.eu' for e in ted),'ted_notice_xml':sum(e['host']=='ted.europa.eu' for e in ted),
        'ted_attributed_to':sorted({e['organisation_number'] for e in ted}),'official_extra_requests':by['__official_extra__'],
        'max_requests_per_company':r['max_requests_per_company'],'companies_at_40':caps,'deadline_hits':r['deadline_hits'],
        'budget_rejections':dict(errs),'rejection_reasons':{k:v for k,v in (r.get('rejection_reasons') or {}).items() if 'budget' in k}}
print(json.dumps(out,indent=1,default=str))
