"""Check raw shared-URL flags against independently retained official row bodies."""
import base64,hashlib,json,lzma,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import common as C

def main():
    blobs=C.read_blobs();rows=list(C.read_envelopes());raw=json.loads((C.HERE/'attribution.json').read_text(encoding='utf-8'));urls=set(raw['examples']['page_url_reuse']);count=0;problems=[];subunit_rows=0
    if '--capture' in sys.argv:
        source=Path(sys.argv[sys.argv.index('--capture')+1])/'state'/'blobs'
        for r in rows:
            ev={e['id']:e for e in r['evidence']}
            for c in r['claims']:
                for ref in c['evidence_ids']:
                    e=ev[ref]
                    if e['source_url'] in urls:blobs[e['content_sha256']]=(source/e['content_sha256']).read_bytes()
            # Retain registry relationship evidence for explicitly scoped recipient subunits.
            for c in r['claims']:
                if c['field'].startswith('subunits.unit.'):
                    for ref in c['evidence_ids']:
                        e=ev[ref];blobs[e['content_sha256']]=(source/e['content_sha256']).read_bytes()
        with lzma.open(C.EXTRACT/'blobs.jsonl.xz','wb',preset=9|lzma.PRESET_EXTREME)as f:
            for sha,b in sorted(blobs.items()):
                assert hashlib.sha256(b).hexdigest()==sha
                f.write((json.dumps({'sha256':sha,'b64':base64.b64encode(b).decode()})+'\n').encode())
        m=json.loads((C.EXTRACT/'manifest.json').read_text());m['retained_blobs_total']=len(blobs);m['additional_scope']='All selected source rows behind raw official bulk URL-reuse flags, for independent attribution adjudication.';m['files']['blobs.jsonl.xz']=hashlib.sha256((C.EXTRACT/'blobs.jsonl.xz').read_bytes()).hexdigest();(C.EXTRACT/'manifest.json').write_text(json.dumps(m,indent=1)+'\n')
    allowed={'research.':'organisasjonsnummer','state_aid.':'recipient_orgnr','skattefunn.':'Organisasjonsnummer','cleaning_approval.':'organisation_number'}
    for r in rows:
        ev={e['id']:e for e in r['evidence']}
        for c in r['claims']:
            for ref in c['evidence_ids']:
                e=ev[ref]
                if e['source_url']not in urls:continue
                count+=1
                keys=[k for pre,k in allowed.items()if c['field'].startswith(pre)]
                try:
                    body=blobs[e['content_sha256']];assert hashlib.sha256(body).hexdigest()==e['content_sha256'];record=json.loads(body)
                    assert len(keys)==1
                    recipient=record[keys[0]]
                    if recipient!=r['organisation_number']:
                        assert c['field'].startswith('state_aid.')
                        assert c['value']['recipient_orgnr']==recipient and c['value']['subject_company_orgnr']==r['organisation_number']
                        assert c['value']['matched_via']=='registered recipient subunit '+recipient
                        unit=next(x for x in r['claims'] if x['field']=='subunits.unit.'+recipient)
                        assert unit['value']['organisation_number']==recipient
                        proved=False
                        for ref2 in unit['evidence_ids']:
                            e2=ev[ref2];b2=blobs[e2['content_sha256']];assert hashlib.sha256(b2).hexdigest()==e2['content_sha256']
                            doc2=json.loads(b2);at=C.pointer(doc2,e2['locator'])
                            if isinstance(at,dict) and at.get('organisasjonsnummer')==recipient and (at.get('overordnetEnhet')==r['organisation_number'] or r['organisation_number'] in e2['source_url']):proved=True
                        assert proved
                        subunit_rows+=1
                except (AssertionError,KeyError,ValueError)as exc:problems.append([r['organisation_number'],c['field'],type(exc).__name__])
    other=raw['dangling']+raw['registry_mismatch']+raw['foreign_label']+raw['page_hash_reused_across_envelopes']
    result={'raw_shared_URL_flags':len(urls),'independent_exact_subject_row_checks':count,'explicitly_scoped_registered_subunit_rows':subunit_rows,'subject_mismatches':problems,'other_raw_contamination_flags':other,'cross_company_contamination':len(problems)+other,'basis':'Exact subject identifiers in retained SHA-256-checked official bulk rows; no changes to raw Stage X audit host list or checks.'}
    dest=C.HERE/'bulk-adjudication.json'
    if '--capture'in sys.argv:dest.write_text(json.dumps(result,indent=2)+'\n')
    else:assert json.loads(dest.read_text())==result
    print(json.dumps(result));assert result['cross_company_contamination']==0
if __name__=='__main__':main()
