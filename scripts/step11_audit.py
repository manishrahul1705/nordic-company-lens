"""Step 11 saved-evidence diagnosis and final-run inventories. No networking."""
import argparse
import json
from collections import Counter
from pathlib import Path
from signalpost.web.html import Page
from signalpost.web.candidates import legal_name
from signalpost.web.round2 import real_page,unique_eligible
from signalpost.web.proof import score
from signalpost.web.policy import domain,extract
from signalpost.web.social import compact

OUT=Path('bench/reports/s6-step11')
PREVIOUS=Path('bench/cache/s6-step11-baseline')
TRIAL10=Path('bench/runs/20261106T085057525871Z-2851a42')


def rows(path):return [json.loads(line) for line in path.open(encoding='utf8')]


def summarize(directory):
    data=rows(directory/'envelopes.jsonl')
    profiles=rows(directory/'profiles.jsonl')
    counts={family:sum(r['run']['sections'].get(family)=='available' for r in data) for family in ['identity','roles','subunits','accounts','website','hiring','activity']}
    counts['website']=sum(any(c['field']=='official_website' and c['availability']=='available' for c in r['claims']) for r in data)
    counts['social']=sum(any(c['field'].startswith(('social_profile.','registry_social.')) and c['availability']=='available' for c in r['claims']) for r in data)
    counts['location_profiles']=sum(p['evidence']['locations']['status']=='available' for p in profiles)
    return counts


def saved_unique_review():
    data=rows(TRIAL10/'envelopes.jsonl');report=json.loads((TRIAL10/'report.json').read_text(encoding='utf8'))
    reviewed=[]
    for row in data:
        website=next((c for c in row['claims'] if c['field']=='official_website' and c['value']['proof_type']=='unique_legal_core_domain'),None)
        if not website:continue
        org=row['organisation_number'];values={c['field']:c['value'] for c in row['claims'] if c['availability']=='available'}
        address=values.get('identity.registered_address') or {}
        context={'name':values.get('identity.legal_name'),'street':address.get('adresse'),'postcode':address.get('postnummer'),
                 'municipality':address.get('kommune'),'city':address.get('poststed'),'phone':values.get('identity.registered_phone'),
                 'email':values.get('identity.registered_email'),'nace':(values.get('identity.nace1') or {}).get('kode')}
        leaders=[c['value'].get('name') for c in row['claims'] if c['family']=='roles' and isinstance(c['value'],dict) and isinstance(c['value'].get('name'),str) and (c['value'].get('role_type') or {}).get('kode') in {'DAGL','LEDE'}]
        uniqueness=False;query_sha=None
        for evidence in row['evidence']:
            if '/api/enheter?navn=' not in evidence['source_url']:continue
            document=json.loads((TRIAL10/'state/blobs'/evidence['content_sha256']).read_text(encoding='utf8'))
            entries=document.get('_embedded',{}).get('enheter',[]);page=document.get('page',{})
            matches={str(e.get('organisasjonsnummer')) for e in entries if legal_name(e.get('navn'))==legal_name(context['name'])}
            if page.get('totalPages',2)<=1 and page.get('totalElements')==len(entries) and matches=={org}:
                uniqueness=True;query_sha=evidence['content_sha256'];break
        pages=[];seen=set()
        for event in report['request_log']:
            if event['organisation_number']!=org or event.get('status')!=200 or event.get('section')!='website' or not event.get('content_sha256') or '/robots.txt' in event['url'] or domain(event['url'])!=domain(website['value']['final_url']):continue
            key=(event['url'],event['content_sha256'])
            if key in seen:continue
            seen.add(key)
            body=(TRIAL10/'state/blobs'/key[1]).read_bytes()
            if b'<urlset' in body[:500] or b'<sitemapindex' in body[:500] or b'<rss' in body[:500]:continue
            page=Page(body,key[0]);veto=real_page(page,context) or (score(page,org,context,'legal_name_slug',leaders).reason if score(page,org,context,'legal_name_slug',leaders).level=='REJECT' else None)
            pages.append({'url':key[0],'sha256':key[1],'title':page.title,'veto':veto,'corroborated':unique_eligible(page,context,leaders)})
        vetoes=sorted({p['veto'] for p in pages if p['veto']})
        eligible=uniqueness and not vetoes and any(p['corroborated'] for p in pages)
        reviewed.append({'organisation_number':org,'company':context['name'],'url':website['value']['final_url'],
                         'recorded_registry_unique':uniqueness,'query_sha256':query_sha,'eligible':eligible,'vetoes':vetoes,'pages':pages})
    assert len(reviewed)==29
    (OUT/'unique-29-review.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# Re-check of all 29 rejected unique-name websites','','Saved Step10 bodies and recorded complete registry-name queries only. No new requests. Passing this re-check nominates a trial; it is not a new live ownership claim. Any veto on a captured page rejects the host.','','| Company / orgnr | URL | Eligible | Veto / missing condition |','|---|---|---|---|']
    for r in reviewed:lines.append('| '+r['company']+' / '+r['organisation_number']+' | '+r['url']+' | '+str(r['eligible'])+' | '+(', '.join(r['vetoes']) or ('none' if r['eligible'] else 'approved name / corroboration / complete registry uniqueness missing'))+' |')
    (OUT/'UNIQUE_29.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print({'reviewed':29,'eligible':sum(r['eligible'] for r in reviewed)},flush=True)


def inventory(run):
    before={r['organisation_number']:r for r in rows(PREVIOUS/'envelopes.jsonl')};after=rows(run/'envelopes.jsonl')
    items=[];funnel={k:Counter() for k in 'ABCDEF'}
    for row in after:
        org=row['organisation_number'];old=before[org]
        keys={(c['field'],json.dumps(c['value'],sort_keys=True)) for c in old['claims'] if c['availability']=='available'}
        evidence={e['id']:e for e in row['evidence']}
        name=next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),org)
        for c in row['claims']:
            if c['availability']!='available' or not (c['field']=='official_website' or c['field'].startswith(('social_profile.','registry_social.','hiring.site_job.','hiring.job.'))):continue
            if (c['field'],json.dumps(c['value'],sort_keys=True)) in keys:continue
            items.append({'organisation_number':org,'company':name,'field':c['field'],'value':c['value'],'evidence':[evidence[e] for e in c['evidence_ids']], 'verdict':'pending'})
        website=next((c for c in row['claims'] if c['field']=='official_website' and c['availability']=='available'),None)
        for entry in row['run']['refresh'].get('recall_round2',{}).get('candidates',[]):
            rules=[]
            if entry['origin']=='registry_email':rules.append('A')
            if entry['origin'].startswith('subunit_registry_'):rules.append('B')
            label=extract(entry['domain'])
            core=compact(legal_name(name))
            if entry.get('unique_candidate') or (label.suffix=='no' and label.domain==core and len(core)>=5):rules.append('C')
            if 'discovered_proof_targets' in entry:rules.append('D')
            for rule in rules:
                f=funnel[rule];f['candidates']+=1;f['fetched']+=bool(entry.get('fetched'))
                accepted=website is not None and (domain(website['value']['final_url'])==entry.get('final_domain',entry['domain']) or (entry.get('accepted') and website['value']['candidate_origin']==entry['origin']))
                if rule=='C':accepted=accepted and website['value']['proof_type']=='unique_no_corroborated'
                if rule=='D':accepted=accepted and website['value']['proof_page_url'] in entry.get('discovered_proof_targets',[])
                f['accepted']+=accepted
        jobs=row['run']['refresh'].get('company_jobs',{})
        for key in ['candidates','fetched']:funnel['E'][key]+=jobs.get(key,0)
        funnel['E']['accepted']+=sum(c['field'].startswith('hiring.site_job.') and c['availability']=='available' for c in row['claims'])
        if website and not any(c['field']=='official_website' for c in old['claims']):
            funnel['F']['candidates']+=1
            funnel['F']['fetched']+=1
            found=sum(c['field'].startswith(('social_profile.','dated_item.')) and c['availability']=='available' for c in row['claims'])
            funnel['F']['accepted']+=bool(found)
            funnel['F']['accepted_items']+=found
    (OUT/'new-items.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'funnel.json').write_text(json.dumps({k:dict(v) for k,v in funnel.items()},indent=2)+'\n',encoding='utf8')
    print({'items':len(items),'counts':summarize(run)},flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path);args=parser.parse_args();OUT.mkdir(exist_ok=True)
    if args.run:inventory(args.run)
    else:
        (OUT/'baseline.json').write_text(json.dumps(summarize(PREVIOUS),indent=2)+'\n',encoding='utf8')
        saved_unique_review()


if __name__=='__main__':main()
