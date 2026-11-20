"""Read and retain every new published site's ownership evidence, no HTTP."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from signalpost.web.html import Page
from signalpost.web.proof import orgnrs

HERE=Path(__file__).resolve().parent
OUT=Path('bench/runs/website-second-pass-checkpoint-20261120')


def main():
    reviews=json.loads((OUT/'review-candidates.json').read_text(encoding='utf-8'))
    source={}
    wanted={r['orgnr'] for r in reviews}
    for line in (OUT/'envelopes.jsonl').open(encoding='utf-8'):
        r=json.loads(line)
        if r['organisation_number'] in wanted:source[r['organisation_number']]=r
    for r in reviews:
        c=r['claim'];row=source[r['orgnr']]
        r['registry_identity']={c['field']:c['value'] for c in row['claims']
            if c['availability']=='available' and c['field'] in {'identity.legal_name','identity.registered_address',
                'identity.registered_email','identity.registered_phone','identity.registered_mobile'}}
        pages=[]
        for e in r['evidence']:
            raw=(OUT/'state/blobs'/e['content_sha256']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==e['content_sha256']
            from signalpost.sources.text import decode_body
            assert e['claim_span'] in decode_body(raw)
            if e['source_class']!='company_owned':continue
            page=Page(raw,e['source_url'])
            pages.append({'url':e['source_url'],'sha256':e['content_sha256'],'title':page.title,
                'publisher_orgnrs':sorted(orgnrs(' '.join(page.brand_parts))),
                'owner_orgnrs':sorted(orgnrs(page.owner_text)),
                'claim_span':e['claim_span'],'owner_context':' '.join(page.owner_text.split())[:4000]})
        r['checked_proof_pages']=pages
        if r['orgnr']=='915279082':
            assert any('915279082' in p['publisher_orgnrs'] for p in pages)
            r['review_verdict']='Correct: the homepage publisher footer explicitly states NO 915 279 082 MVA, beside Haukdalsveien 180 / 7288 Soknedal. Exact own orgnr, legal title and registry address agree; this is not a customer reference.'
        elif r['orgnr']=='983520944':
            assert any('post@spinellfrisor.no' in p['owner_context'] and 'Spinell Frisør AS' in p['owner_context'] for p in pages)
            r['review_verdict']='Correct: the page explicitly welcomes visitors to Spinell Frisør AS and publishes the exact registered email post@spinellfrisor.no. The working salon address/phone differ from the registry contact fields, so those are not used as proof. The exact name plus registry email satisfies the unchanged rule; no orgnr is invented.'
        elif r['orgnr']=='930832707':
            assert any('Hegdehaugsveien 3, 0352 Oslo' in p['owner_context'] for p in pages)
            r['review_verdict']='Correct: the site identifies its own studio as Dogleg and its footer gives Hegdehaugsveien 3, 0352 Oslo, exactly matching registered street and postcode/city. This uses the unchanged name-plus-two-registry-contact signals, not name alone. No conflicting publisher or foreign orgnr was found.'
        else:
            raise AssertionError('Review additional recovered site explicitly before committing')
        # Do not retain whole page text from unrelated fetched pages in reports.
        r.pop('checked_pages',None)
    (HERE/'ownership-review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{'company':r['company'],'orgnr':r['orgnr'],'value':r['claim']['value'],
        'registry':r['registry_identity'],'pages':r['checked_proof_pages']} for r in reviews],ensure_ascii=True,indent=2))


if __name__=='__main__':main()
