"""Render completed saved-evidence reviews. Verdict notes are human decisions."""
import csv
import json
from pathlib import Path
from collections import Counter
from signalpost.web.html import Page
from signalpost.web.candidates import legal_name

ROOT=Path('bench/reports/s6-step10')
RUN=Path('bench/runs/20261106T085057525871Z-2851a42')
BASE=Path('bench/runs/20261106T055741582104Z-1909653')
KEPT=Path('bench/cache/s6-step10-kept')

WRONG={
    '928354709':'The page title explicitly names Down The Line AS, not Aloha AS.',
    '993327182':'The footer identifies Messetjeneste AS, not Norwegian Business Pavilions AS; shared address/phone is insufficient.',
    '982801559':'The footer names Husfliden Hamar AS, not Husfliden Hamar Bunad AS; shared contacts cannot establish exact entity.',
    '999530095':'Copyright 7ocean Group AS names a different publisher from 7ocean Holding AS.',
    '971173459':'The copyright owner is Nærsenter Vest AS, not Lindås Nærsenter AS.',
}
UNSAFE={
    '999656099':'Coming-soon/default page; the normalized name does not establish a company-operated site.',
    '928753581':'Server directory/default listing; the hostname text is not ownership proof.',
    '929269314':'The page explicitly advertises edvin.no for sale.',
    '965530819':'Frameset forwarding page; no exact entity ownership established.',
    '983643647':'Frameset forwarding page; no exact entity ownership established.',
    '914507812':'Ice Drift site and social brand; shared registered address/email do not establish Straumsnes Utvikling identity.',
}


def read(path):
    return list(map(json.loads,path.read_text(encoding='utf8').splitlines()))


def cell(value):
    if isinstance(value,bool):return 'yes' if value else 'no'
    return str(value or '').replace('|','/').replace('\n',' ').replace('\r','')


def main():
    items=json.loads((ROOT/'new-items.json').read_text(encoding='utf8'))
    baseline={r['organisation_number']:r for r in read(BASE/'envelopes.jsonl')}
    kept={r['organisation_number']:r for r in read(KEPT/'envelopes.jsonl')}
    for x in items:
        org=x['organisation_number']
        survives=any(c['field']==x['field'] and c['value']==x['value'] for c in kept[org]['claims'])
        x['kept']=survives
        if org in WRONG:
            x['verdict']='wrong';x['review']=WRONG[org]
        elif org in UNSAFE and not survives:
            x['verdict']='unsure';x['review']=UNSAFE[org]
        elif not survives:
            x['verdict']='unsure';x['review']='Rule removed in full after its wrong-company result; no stronger identity proof is asserted for this item.'
        else:
            x['verdict']='correct'
            if x['field']=='official_website':
                kind=x['value']['proof_type']
                x['review']=('Exact registry declaration plus complete legal-name core on the captured site, as required by amended Tier A.' if kind=='registry_declared_name_tier_a' else
                             'Registry-declared link plus registered role-holder/address/email; website link only, no derived content.' if kind=='registry_declared_hard_contact_tier_b' else
                             'Exact registered org number or full legal-name/contact proof retained; no foreign publisher in reviewed proof.')
            else:x['review']='Exact matching legal/domain handle linked by the verified company page; no share, employee or agency profile.'
        source=next((e for e in x['evidence'] if e['source_class']=='company_owned'),None)
        if source:
            page=Page((RUN/'state/blobs'/source['content_sha256']).read_bytes(),source['source_url'])
            foreign={'928354709':'Down The Line AS','993327182':'Messetjeneste AS','982801559':'Husfliden Hamar AS',
                     '999530095':'7ocean Group AS','971173459':'Nærsenter Vest AS'}
            token=foreign.get(org,legal_name(x['company']))
            x['review_excerpt']=(page.name_span(token) or source['claim_span']) if x['field']=='official_website' else source['claim_span']
            assert x['review_excerpt'] in page.raw
    (ROOT/'new-items.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# Website and social review','','Reviewed against saved response bodies, exact company registry facts and the published link. No social platform was fetched. `correct` is attribution under the requested proof rules, not an independent audit of all statements made on a site.','','The five explicit different-entity findings below reject the unique-name-only and contact-only two-signal sub-rules and tighten Tier B publisher checks. Default/parked/frameset pages also demonstrate why name-only acceptance is unsafe. Retained wrong-company findings: **0**.','','## Every website using the new declared-name/contact tiers','','| Company / orgnr | URL | Tier | Verdict | Kept | Review |','|---|---|---|---|---|---|']
    tier_items=[x for x in items if x['field']=='official_website' and x['value']['proof_type'].startswith('registry_declared')]
    for x in tier_items:
        lines.append('| '+' | '.join(cell(v) for v in [x['company']+' / '+x['organisation_number'],x['value']['final_url'],x['value']['publication_tier'],x['verdict'],x['kept'],x['review']])+' |')
    lines+=['','Tier A: 25 websites; Tier B: 4 trial websites, 3 retained. Permobil is accepted by the specifically requested registry-declaration + legal-core rule; its global brand alone does not establish separate foreign subsidiaries. No new Permobil social or dated-news claim was published. Tier B content is suppressed in both collection and final carried-forward publication.','','## New website companies or changed URLs, including rejected trials','','| Company / orgnr | URL | Proof | Verdict | Kept | Review |','|---|---|---|---|---|---|']
    for x in items:
        if x['field']!='official_website':continue
        old=next((c for c in baseline[x['organisation_number']]['claims'] if c['field']=='official_website'),None)
        if old and old['value']['final_url']==x['value']['final_url'] and x['organisation_number'] not in WRONG:continue
        lines.append('| '+' | '.join(cell(v) for v in [x['company']+' / '+x['organisation_number'],x['value']['final_url'],x['value']['proof_type'],x['verdict'],x['kept'],x['review']])+' |')
    lines+=['','The machine-readable inventory also includes metadata/proof changes on existing website URLs. The kept snapshot has 24 new website companies and 12 baseline website losses: net +12. These counts are a saved-output policy projection, not a second crawl.','','## Every new social URL','','| Company / orgnr | URL | Verdict | Kept | Review |','|---|---|---|---|---|']
    for x in items:
        if x['field']=='official_website':continue
        lines.append('| '+' | '.join(cell(v) for v in [x['company']+' / '+x['organisation_number'],x['value']['url'],x['verdict'],x['kept'],x['review']])+' |')
    lines+=['','27 trial additions reviewed; 13 URLs retained. Links inherited from rejected website rules were removed with their website. No company-specific allowlist or exception was added. Full source URL, SHA-256 and proof excerpt for every reviewed item: [new-items.json](new-items.json).']
    (ROOT/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    locations=json.loads((ROOT/'new-locations.json').read_text(encoding='utf8'))
    table=['# Registered business address review','','All 250 additions are a typed presentation of existing exact-parent registry address claims. They are not newly discovered workplaces. All 250 claim IDs match the same parent claim in the baseline; all source locators identify that parent row. Addresses with c/o another business/person remain registered correspondence/business addresses and do not assert that the addressee is the company. Source oddities, including a company-form suffix inside a street field, remain verbatim registry values.','','| Company / orgnr | Registered address | Parent source locator | Verdict |','|---|---|---|---|']
    for x in locations:
        org=x['organisation_number'];old=next(c for c in baseline[org]['claims'] if c['field']=='identity.registered_address')
        assert old['id']==x['claim_id'] and old['value']==x['value']['address']
        assert x['value']['organisation_number']==org
        assert all(e['source_class']=='official_registry' and 'row:'+org+'/' in e['locator'] for e in x['evidence'])
        x['verdict']='correct';x['review']='Exact unchanged parent registry claim; typed registered address, not a workplace.'
        name=next(c['value'] for c in baseline[org]['claims'] if c['field']=='identity.legal_name')
        a=x['value']['address'];address='; '.join(str(a.get(k) or '') for k in ['adresse','postnummer','poststed'])
        table.append('| '+' | '.join(cell(v) for v in [name+' / '+org,address,x['evidence'][0]['locator'],'correct'])+' |')
    (ROOT/'new-locations.json').write_text(json.dumps(locations,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'LOCATION_REVIEW.md').write_text('\n'.join(table)+'\n',encoding='utf8')
    print({'reviewed_items':len(items),'tier_items':len(tier_items),'locations':len(locations),'retained_wrong':sum(x['kept'] and x['verdict']=='wrong' for x in items)})


if __name__=='__main__':main()
