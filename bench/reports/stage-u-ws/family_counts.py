"""Four-count comparison: registry changes, dated items, website companies, social companies."""
import json,sys,collections
def claims(o):
    if isinstance(o,dict):
        if 'field' in o and 'family' in o and 'availability' in o:yield o;return
        for v in o.values():yield from claims(v)
    elif isinstance(o,list):
        for v in o:yield from claims(v)
def counts(path):
    c=collections.Counter();web=set();soc=set();ted=set();n=0
    for line in open(path,encoding='utf8'):
        e=json.loads(line);org=e['organisation_number'];n+=1
        for x in claims(e):
            if x['availability']!='available':continue
            p=x['field'].split('.')[0]
            if x['family']=='activity':c[p]+=1
            if p=='official_website':web.add(org)
            if p=='social_profile':soc.add(org)
            if p=='procurement_award':ted.add(org)
        c['_fam_'+'x']+=0
    return {'envelopes':n,'registry_changes':c['registry_change'],'dated_items':c['dated_item'],'website_companies':len(web),'social_companies':len(soc),
            'ted_awards':c['procurement_award'],'ted_companies':len(ted)}
out={name:counts(path) for name,path in (a.split('=',1) for a in sys.argv[1:])}
print(json.dumps(out,indent=1))
