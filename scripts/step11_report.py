"""Reproduce Step 11 review tables from saved evidence; no network calls."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import step11_audit as audit
from signalpost.web.html import Page,json_values

OUT=Path('bench/reports/s6-step11')
RUN=Path('bench/runs/20261106T102032689035Z-f774483')
KEPT=Path('bench/cache/s6-step11-kept')

# Human assessments of the saved bodies, identity, registered contacts and
# registry-name query evidence. This is deliberately not an automatic verdict.
NOTES=[
('correct','Footer explicitly publishes as Netad AS; registry email uses netad24.com. Historical affiliate-marketing copy differs from current property NACE, but the legal publisher is exact.'),
('correct','Same Ralston Bau site as baseline; design studio identity and registered domain, with retained Norwegian about/contact evidence. Proof page changed.'),
('correct','Prime Cargo identity in title/metadata, registry email post@primecargo.no and logistics offering. No conflicting publisher. The captured root is metadata-heavy.'),
('correct','Own organisation number 987564911, Næringsøkonomi AS and Tvetenveien 154 on the about page. Existing site, changed proof.'),
('wrong','GLOA AS is not AS Betongbygg. Shared Ringtunveien 8 / 1712 admitted the operating/group site. Drop the new email contact-only Tier B rule, including carried snapshots.'),
('unsure','Global Simply.tv metadata company; Morten Trolle is a shared MEDL, not registered director/chair. No exact Norwegian identity. Drop the newly broadened all-role-holder inference.'),
('correct','Borg Bierstube AS in footer and Torget 6, 1707 Sarpsborg. Existing site, changed proof.'),
('correct','Formosa AS in title and company copy; registered director Katarina Leopax appears. Complete official uniqueness query.'),
('correct','Individual seller identity and own organisation number 914283116 on customer-service terms.'),
('correct','Balderapotek Instagram handle is linked by that same verified pharmacy, matching its brand.'),
('correct','Real Økonomi AS in footer, registered municipality Alver and Kvassnesvegen 15. Postcode changed on site (5916 vs registry 5914), so postcode is not the corroboration.'),
('correct','Cannonball brand, exact .no core, registered Bergen and Flyplassvegen 535. Complete uniqueness query; no other publisher. Website describes travel services, unlike the broad current advertising NACE.'),
('unsure','Credor recovery-audit brand shares Strøket 8 / 1383 and director Ragnar Leknes; no Deigen Holding identity. Do not infer exact entity from shared address. Removed with email Tier B.'),
('unsure','Estonian group site matches NUF email and foreign address; registered HFOR is Nordic Production Group OÜ. Exact Norwegian establishment attribution remains unresolved; removed with email Tier B.'),
('correct','Askøy24 newspaper brand and Storebotn 9B / 5309 Kleppestø match registered publisher, complete uniqueness query; no conflicting publisher found.'),
('correct','Snappy AS title, registered director Christoffer Beddari Kristiansen and Kirkenes in company about copy.'),
('correct','snappy_as Twitter link appears on the verified Snappy company about page and matches its identity.'),
('correct','snappy_as Instagram link appears on the same verified company page.'),
('correct','Tensio exact .no identity and registry-wide uniqueness. Registered Stjørdal appears in its service municipality selector, not an office address: a weak but expressly allowed municipality signal. No conflicting owner on captured pages; this does not establish a subsidiary as a separate publisher.'),
('correct','Own organisation number 992868775, Alfa Lagerhotell A/S and Knarrevikveien 60 in footer. Existing site changes apex/www URL.'),
('correct','Contact page explicitly names ANTISINK AS and organisation number 918486666.'),
('correct','antisink_systems Instagram is a footer link; verified company declares Antisink Systems as its brand.'),
('correct','antisink-as LinkedIn is an owned link with the exact company name.'),
('correct','North Grey exact .no identity, C. J. Hambros plass 2C and Oslo match registry; security offering matches company industry. No foreign publisher.'),
('correct','Ulstein Minilager genuine storage site with Ulsteinvik locality, exact .no name and complete uniqueness query. Plain HTTP is recorded. Physical storage address differs from registered address; no claim of equality.'),
('unsure','Ice Drift crane/logistics site shares Sikterigata 6 / 8622 with Straumsnes Utvikling. Exact company identity absent; removed with email Tier B.'),
('correct','StillasForDeg AS title and company copy, registered Ålesund, exact .no domain and uniqueness. Some leftover English roofing-template prose is a content-quality limitation; substantive scaffolding content and company identity are present.'),
('correct','Ankermann AS and own organisation number 917329435 on contact page, matching minibus business.'),
('correct','Bergen Vaktmestertjenester AS, own 990412375 and registered street are explicit. PHM Group footer is acknowledged; existing site remains exact-entity proved and group content guard applies.'),
]


def main():
    items=json.loads((OUT/'new-items.json').read_text(encoding='utf8'))
    assert len(items)==len(NOTES)==29
    kept=audit.rows(KEPT/'envelopes.jsonl');raw=audit.rows(RUN/'envelopes.jsonl')
    final={r['organisation_number']:{c['field'] for c in r['claims']} for r in kept}
    lines=['# Step 11 manual review','','Every new or changed website value/proof and social URL was inspected from saved company-page bodies. No search or social-destination fetch was used. There are 24 website items (19 new-company sites plus five existing proof/URL changes), five social URLs and zero new jobs. Verdicts are human attribution assessments, not automated name-score labels.','','| Company / orgnr | Item | Verdict | Kept | Review |','|---|---|---|---|---|']
    reviewed=[]
    for item,(verdict,note) in zip(items,NOTES):
        own=[e for e in item['evidence'] if e['source_class']=='company_owned']
        for e in own:
            body=(RUN/'state/blobs'/e['content_sha256']).read_bytes()
            assert hashlib.sha256(body).hexdigest()==e['content_sha256']
        item['verdict']=verdict;item['review']=note;item['kept']=item['field'] in final[item['organisation_number']]
        if item['kept']:assert verdict=='correct'
        item['evidence']=[{k:e.get(k) for k in ('id','source_url','source_class','content_sha256','claim_span','retrieved_at','locator')} for e in item['evidence'] if e['source_class']=='company_owned' or '/api/enheter?navn=' in e['source_url'] or '/underenheter/' in e['source_url']]
        reviewed.append(item)
        url=item['value'].get('final_url',item['value'].get('url'))
        lines.append(f"| {item['company']} / {item['organisation_number']} | [{url}]({url}) | {verdict} | {'KEEP' if item['kept'] else 'WITHHOLD'} | {note} |")
    lines+=['','Retained: 24 correct items (19 website proof/URL items + five social URLs); withheld: one definitively wrong item and four unresolved exact-entity items. The entire new email/subunit contact-only Tier B extension and expanded non-director/chair role inference are disabled, rather than adding company exceptions. Existing stronger orgnr/two-signal proofs and direct homepage Tier B are preserved.','', 'Full excerpts, retrieval dates and SHA-256 values: [review-items.json](review-items.json). Independent verifier additionally checks every published claim and blob in the final projection.']
    (OUT/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (OUT/'review-items.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'new-items.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    original=audit.OUT;audit.OUT=OUT/'kept';audit.OUT.mkdir(exist_ok=True);audit.inventory(KEPT);audit.OUT=original
    selected=json.loads((OUT/'kept/new-items.json').read_text(encoding='utf8'))
    assessments={(i['organisation_number'],i['field']):i for i in reviewed}
    for item in selected:
        assessment=assessments[item['organisation_number'],item['field']]
        item['verdict']=assessment['verdict'];item['review']=assessment['review'];item['kept']=True
        item['evidence']=assessment['evidence']
    (OUT/'kept/new-items.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    trial=json.loads((OUT/'funnel.json').read_text());final_funnel=json.loads((OUT/'kept/funnel.json').read_text())
    funnel={k:{**v,'kept_after_review':final_funnel[k].get('accepted',0)} for k,v in trial.items()}
    (OUT/'funnel-final.json').write_text(json.dumps(funnel,indent=2)+'\n',encoding='utf8')
    counts={'baseline':audit.summarize(audit.PREVIOUS),'trial':audit.summarize(RUN),'kept_projection':audit.summarize(KEPT)}
    (OUT/'counts.json').write_text(json.dumps(counts,indent=2)+'\n',encoding='utf8')
    report=json.loads((RUN/'report.json').read_text());log=report['request_log'];diagnostics=[]
    for row in raw:
        for url in row['run']['refresh'].get('company_jobs',{}).get('urls_checked',[]):
            events=[e for e in log if e['organisation_number']==row['organisation_number'] and e['url']==url and e.get('content_sha256')]
            event=events[-1] if events else None
            p=Page((RUN/'state/blobs'/event['content_sha256']).read_bytes(),url) if event else None
            postings=[node for doc in (p.jsonld if p else []) for node in walk(doc) if 'JobPosting' in str(node.get('@type',''))]
            diagnostics.append({'organisation_number':row['organisation_number'],'url':url,'title':p.title if p else None,
                'status':event.get('status') if event else None,'sha256':event.get('content_sha256') if event else None,
                'jobposting_nodes':len(postings),'reason':'no individual structured JobPosting / active dates proved' if not postings else 'structured posting did not satisfy active/employer gate'})
    (OUT/'jobs-diagnostics.json').write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'JOBS.md').write_text('# Company-site / ATS jobs\n\n38 nominated URLs were checked across '+str(len({d['organisation_number'] for d in diagnostics}))+' companies; zero new individual ACTIVE postings passed. The three NAV jobs remain. This is a recall limitation, not evidence that those employers have no vacancies. Conplan individual-looking career pages and Laksesystemer service-technician pages were fetched, but the current parser requires a structured JobPosting with supported posting/expiry dates. It does not infer active status from an undated careers page or a landing page. Some nominations are ordinary pages or article text containing career terms; none was published as a job. No linked external ATS board produced a new proved posting in this sample. Tenant-boundary and employer-mismatch cases are covered by synthetic end-to-end tests.\n\n[Every URL and captured-body hash](jobs-diagnostics.json). NAV still uses the public-token path with live detail proof; no personal credential is needed.\n',encoding='utf8')
    metrics={k:report[k] for k in ['requests','requests_per_company','amortized_requests_per_company','shared_requests','max_requests_per_company','runtime_ms','deadline_hits','warnings','limits','search','llm','dns_fallback_attempts','dns_fallback_successes','dns_fallback_seconds','dns_fallback_max_seconds_per_company','hiring_prefetch','nav_detail_requests','finalisation']}
    metrics['benchmark_execution']=json.loads((RUN/'execution.json').read_text())
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8')
    print(counts,flush=True)


def walk(value):
    if isinstance(value,dict):
        yield value
        for v in value.values():yield from walk(v)
    elif isinstance(value,list):
        for v in value:yield from walk(v)


if __name__=='__main__':main()
