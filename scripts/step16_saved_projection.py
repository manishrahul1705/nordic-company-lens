"""Re-extract only existing Step15 sources; compare legacy IDs and count new facts."""
import csv,io,json
from collections import Counter
from pathlib import Path
from signalpost.sources import bulk_registry,brreg_enhet,brreg_roller,brreg_underenheter,regnskap
from signalpost.sources.extract import Source,Section
from signalpost.sources.http import Response
from signalpost.sources.blobstore import BlobStore
RUN=Path('bench/runs/20261106T183808924157Z-1db7047');OUT=Path('bench/reports/s6-step16')

def main():
    blobs=BlobStore(Path('bench/cache/s6-step16-projection'))
    before=Counter();after=Counter();lost=[];changed=[];added=Counter();estimated=0
    with (Path('bench/cache/s6-step16-projection')/'saved-new-claims.jsonl').open('w',encoding='utf8') as newfile:
      for line in (RUN/'envelopes.jsonl').open(encoding='utf8'):
        row=json.loads(line);org=row['organisation_number'];ev={e['id']:e for e in row['evidence']};sections={}
        for family in ['identity','roles','subunits','accounts']:
            old=[c for c in row['claims'] if c['family']==family];before[family]+=sum(c['availability']=='available' for c in old)
            sources={}
            for c in old:
                for eid in c['evidence_ids']:
                    e=ev[eid];url=e['source_url']
                    if not url.startswith('https://data.brreg.no/'):continue
                    if family=='accounts' and url!=regnskap.URL+org:continue
                    if family=='roles' and url!=brreg_enhet.BASE+org+'/roller':continue
                    if family=='identity' and not (url==brreg_enhet.BASE+org or '/lastned/csv' in url):continue
                    if family=='subunits' and '/api/underenheter?' not in url:continue
                    sources[e['content_sha256']]=e
            if not sources:
                after[family]+=sum(c['availability']=='available' for c in old);continue
            section=Section()
            for sha,e in sources.items():
                body=(RUN/'state/blobs'/sha).read_bytes();url=e['source_url'];src=Source(url,body,sha,e['retrieved_at'],e.get('source_identifier'))
                if family=='identity':
                    result=bulk_registry.extract(org,next(csv.DictReader(io.StringIO(body.decode('utf-8-sig')))),src) if '/lastned/csv' in url else brreg_enhet.extract(org,json.loads(body),src)
                else:
                    r=Response(body,200,url,e['retrieved_at'],sha)
                    if family=='roles':result=brreg_roller.extract(org,r)
                    elif family=='accounts':result=regnskap.extract(org,r,blobs)
                    else:
                        result=Section();brreg_underenheter.extract_page(org,r,result,0)
                section.claims.extend(result.claims);section.evidence.extend(result.evidence)
            # One field has one meaning; the saved source set must not produce duplicates.
            assert len({c.field for c in section.claims})==len(section.claims),(org,family)
            actual={c.field:c for c in section.claims}
            for c in old:
                if c['field'] not in actual:lost.append({'org':org,'field':c['field'],'id':c['id']})
                elif actual[c['field']].id!=c['id']:changed.append({'org':org,'field':c['field'],'previous':c['value'],'current':actual[c['field']].value})
            oldfields={c['field'] for c in old};evidence={e.id:e for e in section.evidence}
            for c in section.claims:
                if c.field not in oldfields and c.availability=='available':
                    added[family]+=1
                    newfile.write(json.dumps({'organisation_number':org,'claim':c.model_dump(mode='json'),'evidence':[evidence[eid].model_dump(mode='json') for eid in c.evidence_ids]},ensure_ascii=False,separators=(',',':'))+'\n')
            after[family]+=sum(c.availability=='available' for c in section.claims);sections[family]=section
        for family,section in sections.items():
            row['claims']=[c for c in row['claims'] if c['family']!=family]+[c.model_dump(mode='json') for c in section.claims]
            ev.update({e.id:e.model_dump(mode='json') for e in section.evidence})
        row['evidence']=list(ev.values())
        estimated+=len(json.dumps(row,ensure_ascii=False,separators=(',',':')).encode())+1
    result={'before_available_claims':dict(before),'after_available_claims':dict(after),'new_claims':dict(added),'lost_legacy_claims':lost,'changed_legacy_claim_ids':changed,'estimated_envelope_bytes_without_rebuilding_synthesis':estimated,'HTTP_requests':0,'note':'Re-extraction uses only source blobs cited by each existing family; original run untouched. Calibration writes only existing local calibration snippets.'}
    (OUT/'saved-projection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
if __name__=='__main__':main()
