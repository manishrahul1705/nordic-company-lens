"""Independent raw-binding checks for every final Wikidata-supported claim."""
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

root=Path('bench/runs/stage-ag-20261119')
out=Path(__file__).parent
measurement=json.loads((root/'measurement.json').read_text(encoding='utf-8'))
assert not measurement['projection_exceeds_user_stop_threshold'], 'Stop: 1,100-company projection exceeds 3,000 seconds'
report=json.loads((root/'report.json').read_text(encoding='utf-8'))
requests=[e for e in report['request_log'] if e.get('section')=='wikidata']
assert len(requests)==5
assert all(e['status']==200 for e in requests)
downloaded={e['content_sha256'] for e in requests}
cache={};checked=0;conflicts=0;core_websites=0
statement_values=set()
currency_units=set()

def load(ev):
    sha=ev['content_sha256']
    if sha not in cache:
        raw=(root/'state/blobs'/sha).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==sha
        cache[sha]=json.loads(raw)
    node=cache[sha]
    for bit in ev['locator'].split('/')[1:]:
        node=node[int(bit)] if isinstance(node,list) else node[bit]
    return node

def cell(b,key):return b.get(key,{}).get('value')

def temporal(b,qualifier=False):
    return {'time':cell(b,'pointInTime' if qualifier else 'value'),
            'precision':int(cell(b,'pointPrecision' if qualifier else 'precision')),
            'calendar':cell(b,'pointCalendar' if qualifier else 'calendar')}

def expected(b):
    prop=cell(b,'property').rsplit('/',1)[1]
    raw=cell(b,'value')
    if prop=='P1448':return {'text':raw,'language':b['value'].get('xml:lang')}
    if prop=='P571':return temporal(b)
    if prop in {'P159','P452'}:
        value={'entity':raw}
        if 'valueLabel' in b:value.update(label=cell(b,'valueLabel'),label_language=b['valueLabel'].get('xml:lang'))
        return value
    if prop in {'P1128','P2139'}:
        value={'amount':raw,'unit':cell(b,'unit'),'point_in_time':temporal(b,True)}
        if 'currencyCode' in b:value['currency']=cell(b,'currencyCode')
        assert Decimal(raw).is_finite() and Decimal(raw)>=0
        if prop=='P1128':assert Decimal(raw)==Decimal(raw).to_integral_value()
        currency_units.add((prop,cell(b,'unit'),cell(b,'currencyCode')))
        return value
    return raw

def same_url(a,b):
    def key(u):
        p=urlsplit(u)
        return p.scheme.lower(),p.netloc.lower(),p.path or '/',p.query,p.fragment
    return key(a)==key(b)

for line in (root/'envelopes.jsonl').open(encoding='utf-8'):
    row=json.loads(line);org=row['organisation_number']
    evs={e['id']:e for e in row['evidence']};claims={c['id']:c for c in row['claims']}
    for claim in row['claims']:
        if claim['availability']!='available':continue
        for ref in claim['evidence_ids']:
            e=evs[ref]
            if e['source_class']!='wikidata':continue
            b=load(e);prop=cell(b,'property').rsplit('/',1)[1]
            assert cell(b,'org')==org
            item=cell(b,'item').rsplit('/',1)[1];rev=cell(b,'revision')
            assert re.fullmatch(r'Q[1-9]\d*',item) and re.fullmatch(r'[1-9]\d*',rev)
            revision_url=f'https://www.wikidata.org/w/index.php?title={item}&oldid={rev}'
            assert revision_url in e['source_identifier']
            assert e['content_sha256'] in downloaded
            p=urlsplit(e['source_url']);params=parse_qs(p.query);query=params['query'][0]
            assert p.scheme=='https' and p.hostname=='query.wikidata.org' and p.path=='/sparql'
            assert 'wdt:P2333 ?org' in query and json.dumps(org) in query and '?revision' in query
            assert params['format']==['json']
            prefixes={'P1448':'identity.wikidata.official_name.','P571':'identity.wikidata.inception.',
                      'P159':'identity.wikidata.headquarters.','P452':'identity.wikidata.industry.',
                      'P1128':'identity.wikidata.employees.','P2139':'accounts.wikidata.revenue.',
                      'P856':'identity.wikidata.official_website.'}
            if prop in prefixes:assert claim['field'].startswith(prefixes[prop])
            if prop in {'P2002','P2003','P2013','P4264','P2397'}:
                assert claim['field'].startswith('social_profile.')
                roots={'P2002':'https://x.com/','P2003':'https://www.instagram.com/',
                       'P2013':'https://www.facebook.com/','P4264':'https://www.linkedin.com/company/',
                       'P2397':'https://www.youtube.com/channel/'}
                assert claim['value']['url']==roots[prop]+cell(b,'value').lstrip('@')
                # Use the unchanged attribution test, in addition to raw value
                # and identity checks above; do not invent a Wikidata exception.
                from signalpost.web.social import matches_profile,social_company_names
                context={'name':next(c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),
                         'subunits':[c['value'] for c in row['claims'] if c['field'].startswith('subunits.unit.') and c['availability']=='available']}
                observed=row['run']['refresh'].get('website',{}).get('observed_social_profiles',[])
                assert matches_profile(claim['value']['url'],social_company_names(context)) or claim['value']['url'] in observed
            elif prop=='P856':
                assert same_url(claim['value'],expected(b))
                assert claim['field'].startswith('identity.wikidata.official_website.')
            else:assert claim['value']==expected(b),(org,prop,claim['value'],expected(b))
            assert claim['field']!='official_website'
            statement_values.add((org,prop,claim['id']))
            checked+=1
    for conflict in row['run']['refresh'].get('wikidata',{}).get('disagreements',[]):
        registry=claims[conflict['registry_claim_id']]
        assert registry['availability']=='available' and registry['value']==conflict['registry_value']
        assert registry['evidence_ids']==conflict['registry_evidence_ids']
        for ref in conflict['wikidata_evidence_ids']:
            e=evs[ref];b=load(e)
            assert cell(b,'org')==org
            assert expected(b)==conflict['wikidata_value']
            assert cell(b,'revision')==conflict['revision']
        conflicts+=1
result={'passed':True,'sparql_http_requests':len(requests),'wikidata_evidence_links_checked':checked,
        'wikidata_supported_claims':len(statement_values),'disagreements_checked':conflicts,
        'source_hashes_checked':len(cache),'units_seen':list(currency_units),
        'primary_website_ownership_promoted_from_wikidata':False}
(out/'audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
