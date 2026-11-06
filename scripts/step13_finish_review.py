"""Persist the human Step 13 source review and integrity checks; no networking."""
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT=Path('bench/reports/s6-step13')
RUN=Path('bench/runs/20261106T125849762180Z-7474c37')


def note(index):
    if index==0:return 'Correct KN Elektro contact-page metadata; exact own footer/company address. This is a truncated metadata self-description, not a new registry activity description.'
    if index in {1,2}:return 'Correct company-published staff email on KN Elektro contact page, under its own footer. No claim that it is a registry email.'
    if 3<=index<=6:return 'Correct Closva AS publication; Norwegian and Danish pages both explicitly name owner Closva AS, orgnr 936629466. Language editions are distinct article URLs of two announcements, not four independent transactions.'
    if index==7:return 'Correct Lofotposten-published customer-service number, not its registry/main-office telephone; publisher footer explicitly names Lofotposten AS.'
    if index in {8,9}:return 'Correct staff mailto link on Control Solutions contact page, whose footer carries own orgnr 926490060.'
    if 10<=index<=19:return 'Correct self-published safety/news article on Feie- og Tilsynstjenester AS site; footer names own 993919675. Publication date is on article. This does not assert that this company or its staff attended the described fire incident.'
    if 20<=index<=44:return 'Correct publication on the already verified Tensio corporate site. Group/customer/operational topics remain dated article titles; no subsidiary employment, group financial amount or incident involvement is inferred as a parent-company fact.'
    if index==45:return 'Correct official LAU CAPITAL AS chair record for Albert Ølnes. Role/person unchanged; the registered group last_changed date is now 2026-11-06. This is a source-metadata update, not a newly discovered chair.'
    if 46<=index<=52:return 'Correct Bridge Technologies publication; article footer carries own VAT NO987002808MVA and Oslo address. Historical article, not a new 2026 event or an assertion about another publisher.'
    if index==53:return 'Correct unchanged-company website under plaintext HTTP with own orgnr 952785052 and full legal name; scheme/proof transport changed, not a newly discovered company site. Developer CustomPublish AS is explicitly credited as developer.'
    if index==54:return 'Correct company-published office-hour metadata on NSNL contact page with own full name and 952785052; not a newly inferred activity description.'
    if index==55:return 'Correct NSNL stable-booking email explicitly published on own-orgnr page, not a registry contact or another entity’s employee.'
    if 56<=index<=58:return 'Correct dedicated Bergen Vaktmestertjenester AS publication with own 990412375 in footer. PHM Group branding is disclosed, not reused as another entity’s company fact. Open-application page is an article only, never counted as an ACTIVE job ad.'
    raise AssertionError(index)


def main():
    items=json.loads((OUT/'new-items.json').read_text(encoding='utf8'));assert len(items)==59
    snippets=[];checked=set()
    lines=['# Step 13 review of every new item','','Human source review: 59 new/changed claims and 217 newly displayed typed locations, all correct attribution; zero wrong-company findings. This includes one website transport/proof change, zero new social URLs and zero new jobs. Brand and second-pass cohorts accepted no new websites.','','| # | Company / orgnr | Item | Verdict | Source review |','|---|---|---|---|---|']
    for i,item in enumerate(items):
        item['verdict']='correct';item['review']=note(i)
        for e in item['evidence']:
            sha=e['content_sha256'];body=(RUN/'state/blobs'/sha).read_bytes()
            if sha not in checked:assert hashlib.sha256(body).hexdigest()==sha;checked.add(sha)
        value=item['value'];label=value.get('title',value.get('final_url',value.get('text',''))) if isinstance(value,dict) else str(value)
        if not label:label=item['field']
        label=label.replace('|','/').replace('\n',' ')[:150]
        lines.append(f"| {i} | {item['company']} / {item['organisation_number']} | {label} | correct | {item['review']} |")
    (OUT/'new-items.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    locations=json.loads((OUT/'new-locations.json').read_text(encoding='utf8'))
    assert len(locations)==217 and all(x['verdict']=='correct' and x['supporting_claim_ids'] for x in locations)
    for x in locations:
        for e in x['evidence']:
            body=(RUN/'state/blobs'/e['content_sha256']).read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256']
    lines+=['','All 49 additional article URL claims were inspected with their titles, article-side publication dates and captured text. They include historical content and language editions; the count does not mean 49 new business events. Canonical redirect aliases are deduplicated.','', 'Every postal place was reviewed from its exact registered parent or subunit address. Care-of recipients are not presented as physical workplace owners. Parent PB / subunit Postboks duplicates are removed generically. [All 217 places and their supporting claim IDs/evidence](new-locations.json); [full claim review with dates, excerpts and SHA-256](new-items.json).','', 'Published schema/evidence verification independently checks all 1000 envelopes and every cited blob. No corporate allowlist/blacklist or per-company runtime exception was added.']
    (OUT/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    # Compact location ledger complements the full machine-readable evidence.
    rows=['# All newly displayed typed locations','','217 entries. Each is correct attribution to the exact registry parent/subunit. Postal address is not a claim of an operating workplace.','','| Parent orgnr | Company | Address subject | Type | Registered address | Verdict |','|---|---|---|---|---|---|']
    for x in locations:
        v=x['value'];a=v['address'];street=a.get('adresse');street=' / '.join(street) if isinstance(street,list) else str(street)
        address=' '.join([street,str(a.get('postnummer','')),str(a.get('poststed',''))]).replace('|','/').replace('\n',' / ')
        rows.append(f"| {x['organisation_number']} | {x['company']} | {v['organisation_number']} | {v['type']} | {address} | correct |")
    (OUT/'LOCATIONS_REVIEW.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    metrics={'new_claim_items':59,'new_location_items':217,'claim_verdicts':dict(Counter(x['verdict'] for x in items)),'wrong_company':0,'claim_review_source_blobs_sha_checked':len(checked)}
    (OUT/'review-summary.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8');print(metrics)


if __name__=='__main__':main()
