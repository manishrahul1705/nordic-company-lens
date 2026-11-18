"""Checks: the four repetitions, and national-comparison wording, over generated sections."""
import json,re,sys
NATIONAL=re.compile(r'\b(national|nationally|nationwide|in norway|norwegian companies|all companies|country|countrywide|percentile)\b',re.I)
rows=[json.loads(l) for l in open(sys.argv[1],encoding='utf8')]
def sec(r):return r['sections'] if 'sections' in r else r['run']['synthesis']['sections']
out={'address_repeated_in_reach':0,'missing_address_outside_not_established':0,'missing_address_in_not_established':0,
     'website_domain_named_twice':0,'national_or_unbounded_wording':[],'standing_without_run_basis':[]}
for r in rows:
    s=sec(r);reach=[x['text'] for x in s['reach']];ne=[x['text'] for x in s['not_established']]
    addr=next((t[len('Registered business address: '):].split(', in ')[0] for t in reach if t.startswith('Registered business address: ')),None)
    if addr and any(t.startswith('Registered workplace: ') and addr in t for t in reach) and sum(t.startswith('Registered workplace: ') for t in reach)==1:out['address_repeated_in_reach']+=1
    allt=[x['text'] for k in s for x in s[k] if isinstance(x,dict) and 'text' in x and k!='unknowns']
    out['missing_address_outside_not_established']+=sum('Business address: none registered' in t for k in s if k not in ('not_established','unknowns') for t in [x['text'] for x in s[k]])
    out['missing_address_in_not_established']+=sum('Business address: none registered' in t for t in ne)
    web=' '.join(t for t in ne if t.startswith(('Website and social media','Declared homepage','Own website')))
    for d in set(re.findall(r'\b[\w-]+(?:\.[\w-]+)*\.(?:no|com|net|org|eu|se|dk)\b',web)):
        if web.count(d)>1:out['website_domain_named_twice']+=1;break
    for t in allt:
        if NATIONAL.search(re.sub(r'«.*?»',' ',t)):out['national_or_unbounded_wording'].append((r['organisation_number'],t[:140]))
    for t in [x['text'] for x in s['standing']]:
        if 'in this run' not in t:out['standing_without_run_basis'].append((r['organisation_number'],t[:140]))
print(json.dumps(out,indent=1,ensure_ascii=False))
