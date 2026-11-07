"""Offline field coverage audit of saved Step 15 BRREG evidence; no HTTP."""
import csv, hashlib, io, json, re
from collections import defaultdict
from pathlib import Path

RUN=Path('bench/runs/20261106T183808924157Z-1db7047')
OUT=Path('bench/reports/s6-step16')
ALIASES={'organisation_number':'organisasjonsnummer','name':'navn','address':'beliggenhetsadresse','nace':'naeringskode1','employees':'antallAnsatte','role_type':'type','entity_organisation_number':'enhet/organisasjonsnummer','inactive':'avregistrert','from_date':'fraDato'}

def leaves(value,path=''):
    if isinstance(value,dict):
        for k,v in value.items():yield from leaves(v,path+'/'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from leaves(v,path+'/'+str(i))
    elif value is not None and value!='':yield path,value

def get(data,path):
    try:
        for k in path.strip('/').split('/'):
            if k:data=data[int(k)] if isinstance(data,list) else data[k]
        return data
    except (KeyError,IndexError,ValueError,TypeError):return None

def normalize(path):return re.sub(r'/[0-9]+(?=/|$)','/*',path)

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    found={}; all_present=defaultdict(set); total_blobs=set()
    rows=[json.loads(l) for l in (RUN/'envelopes.jsonl').read_text(encoding='utf8').splitlines()]
    for row in rows:
        org=row['organisation_number'];evidence={e['id']:e for e in row['evidence']};sources={}
        for e in row['evidence']:
            url=e['source_url']
            if not url.startswith('https://data.brreg.no/'):continue
            family='roles' if '/roller' in url else 'subunits' if '/api/underenheter?' in url else 'accounts' if '/regnskapsregisteret/regnskap/' in url else 'identity' if '/enhetsregisteret/api/enheter/' in url and '/oppdateringer/' not in url else None
            if not family:continue
            if family=='accounts' and url.rstrip('/').rsplit('/',1)[-1]!=org:continue
            if family=='roles' and '/'+org+'/roller' not in url:continue
            if family=='identity' and '/lastned/csv' not in url and url.rstrip('/').rsplit('/',1)[-1]!=org:continue
            key=(family,e['content_sha256']);sources[key]=e
        for (family,sha),e in sources.items():
            raw=(RUN/'state/blobs'/sha).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;total_blobs.add(sha)
            csv_source='/lastned/csv' in e['source_url']
            data=next(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))) if csv_source else json.loads(raw)
            present=dict(leaves(data));covered=set(); metadata=set()
            if csv_source:
                present={'/'+k:v for k,v in data.items() if v not in (None,'')}
                metadata.add('/organisasjonsnummer')
            for c in row['claims']:
                if c['family']!=family or c['availability']!='available':continue
                for eid in c['evidence_ids']:
                    ev=evidence[eid]
                    if ev['content_sha256']!=sha:continue
                    locator=ev['locator']
                    if csv_source:
                        if '/column:' in locator:covered.add('/'+locator.split('/column:',1)[1])
                        elif '/columns:' in locator and isinstance(c['value'],dict):
                            prefix=locator.split('/columns:',1)[1].removesuffix('.*')
                            covered.update('/'+prefix+'.'+k for k in c['value'])
                        continue
                    if not locator.startswith('/'):continue
                    value=c['value'];source=get(data,locator)
                    if not isinstance(value,(dict,list)):covered.add(locator);continue
                    if isinstance(value,list):covered.update(p for p,_ in leaves(source,locator));continue
                    for key,val in value.items():
                        if val is None:continue
                        rawkey=key if isinstance(source,dict) and key in source else ALIASES.get(key,key)
                        if family=='roles' and key in {'name','entity_organisation_number','last_changed','group_type'}:continue
                        target=locator+'/'+rawkey
                        if family=='subunits' and key=='address' and not get(data,target):target=locator+'/postadresse'
                        subtree=get(data,target)
                        if subtree is not None:covered.update(p for p,_ in leaves(subtree,target))
                    if family=='roles' and c['field'].startswith('roles.role.'):
                        for prefix in ('/person/navn','/enhet/navn','/enhet/organisasjonsnummer'):
                            covered.update(p for p,_ in leaves(get(data,locator+prefix),locator+prefix))
                        group=locator.rsplit('/roller/',1)[0]
                        for suffix in ('/type','/sistEndret'):
                            covered.update(p for p,_ in leaves(get(data,group+suffix),group+suffix))
            for path,value in present.items():
                normalized=normalize(path);all_present[(family,normalized)].add(org)
                if path in covered:continue
                technical=((family=='subunits' and path.endswith('/overordnetEnhet')) or (family=='identity' and path=='/organisasjonsnummer') or '/_links/' in path or path.startswith('/page/') or path in metadata or (family=='accounts' and re.match(r'^/[0-9]+/(id|journalnr|virksomhet/organisasjonsnummer)$',path)))
                key=(family,normalized)
                entry=found.setdefault(key,{'family':family,'path':normalized,'companies':set(),'examples':[],'fallback_examples':[],'account_types':set(),'classification':'transport/scope metadata' if technical else 'unpublished fact/statement attribute'})
                entry['companies'].add(org)
                if family=='accounts':entry['account_types'].add(str(data[int(path.split('/')[1])].get('regnskapstype')))
                if len(entry['fallback_examples'])<2 and not any(x['organisation_number']==org for x in entry['fallback_examples']):entry['fallback_examples'].append({'organisation_number':org,'value':value,'source_url':e['source_url'],'sha256':sha,'locator':path})
                if len(entry['examples'])<2 and not any(x['value']==value for x in entry['examples']):entry['examples'].append({'organisation_number':org,'value':value,'source_url':e['source_url'],'sha256':sha,'locator':path})
    result=[]
    for key,v in sorted(found.items()):
        v['account_types']=sorted(v['account_types'])
        for ex in v.pop('fallback_examples'):
            if len(v['examples'])<2 and not any((x['organisation_number'],x['locator'])==(ex['organisation_number'],ex['locator']) for x in v['examples']):v['examples'].append(ex)
        v['companies']=sorted(v['companies']);v['company_count']=len(v['companies']);v['present_company_count']=len(all_present[key]);result.append(v)
    facts=[r for r in result if r['classification']=='unpublished fact/statement attribute'];union=set().union(*(set(r['companies']) for r in facts))
    summary={'run':str(RUN),'companies':len(rows),'blobs_sha256_verified':len(total_blobs),'unpublished_fact_paths':len(facts),'companies_with_unpublished_facts':len(union),'technical_paths':len(result)-len(facts),'threshold_met':len(facts)>=10 and len(union)>=300,'note':'Source leaf paths; repeated indices normalized to *. Fields already carried in structured claim values count as published. Reporting-period metadata is distinguished from standalone claims. CSV identity rows were used by this frozen run, not per-company identity JSON. No new requests.'}
    (OUT/'audit.json').write_text(json.dumps({'summary':summary,'fields':result},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# Step 16 pre-code saved-response field audit','',json.dumps(summary,ensure_ascii=False),'','| Family | Unpublished source path | Companies | Two example values |','|---|---|---:|---|']
    for r in facts:
        examples='; '.join(json.dumps(x['value'],ensure_ascii=False).replace('|',chr(92)+'|') for x in r['examples'])
        lines.append(f"| {r['family']} | `{r['path']}` | {r['company_count']} | {examples} |")
    lines+=['','Transport links/pagination/source IDs and already-output organisation scope are separately listed in audit.json; they do not satisfy the fact threshold. All examples retain exact source URL, locator and verified SHA-256 in that ledger.']
    (OUT/'AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf8');print(json.dumps(summary))

if __name__=='__main__':main()
