"""Release comparison and exact saved-source website/social review packs."""
import hashlib,json,sys
from pathlib import Path
from r3_analyze import summarize,rows
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.web.html import Page
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/stage-e';OLD=ROOT/'bench/runs/r3-release-final';NEW=ROOT/'bench/runs/stage-e-live'

def main():
    a,prior=summarize(OLD)
    base_extra={'GLEIF_companies':0,'TED_companies':0,'news_companies':0,'articles':0}
    for row in rows(OLD/'envelopes.jsonl'):
        fields=[c['field'] for c in row['claims'] if c['availability']=='available']
        base_extra['GLEIF_companies']+=any(f.startswith('identity.gleif.') for f in fields)
        base_extra['TED_companies']+=any(f.startswith('procurement_award.') for f in fields)
        articles=sum(f.startswith('dated_item.') for f in fields);base_extra['articles']+=articles;base_extra['news_companies']+=bool(articles)
    a.update(base_extra)
    b,current=summarize(NEW)
    extras=[];lost=[];seen=set();gleif=ted=0;news=articles=0;proof_counts={}
    for row in rows(NEW/'envelopes.jsonl'):
        org=row['organisation_number'];old=prior[org];now=current[org]
        claims=[c for c in row['claims'] if c['availability']=='available']
        gleif+=any(c['field'].startswith('identity.gleif.') for c in claims)
        ted+=any(c['field'].startswith('procurement_award.') for c in claims)
        items=[c for c in claims if c['field'].startswith('dated_item.')];news+=bool(items);articles+=len(items)
        ev={e['id']:e for e in row['evidence']}
        old_sites={old['website']['value']['final_url']} if old['website'] else set()
        old_social={c['value']['url'] for c in old['social']}
        wanted=[c for c in claims if (c['field']=='official_website' and c['value']['final_url'] not in old_sites) or
                (c['field'].startswith(('social_profile.','registry_social.')) and c['value']['url'] not in old_social)]
        proof=next((c for c in claims if c['field']=='official_website'),None)
        if proof:
            kind=proof['value'].get('proof_type','unknown');proof_counts[kind]=proof_counts.get(kind,0)+1
        for c in wanted:
            record={'orgnr':org,'company':now['company'],'kind':'website' if c['field']=='official_website' else 'social','claim':c,'proof':proof['value'] if proof else None,'registry_contacts':now['registry_contacts'],'sources':[]}
            refs=list(c['evidence_ids'])
            if proof:refs+=proof['evidence_ids']
            for ref in dict.fromkeys(refs):
                e=ev[ref]
                if e['source_class']!='company_owned':continue
                if not (e['locator'].startswith(('identity-proof:','company-link:')) or c['field'].startswith('registry_social.')):continue
                path=NEW/'state/blobs'/e['content_sha256'];body=path.read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256']
                p=Page(body,e['source_url']);assert e['claim_span'] in p.raw
                record['sources'].append({**e,'title':p.title,'footer':' '.join(p.footer_parts)[:4000],'owner_text':p.owner_text[:4500]})
            extras.append(record)
        if old['website'] and now['website'] and old['website']['value']['final_url']!=now['website']['value']['final_url']:
            lost.append({'kind':'website_alias','orgnr':org,'company':now['company'],'prior':old['website'],'replacement':now['website'],'current_state':now['sections']['website'],'reason':'Same registered domain; host/scheme alias replaced, company website still published.'})
        if old['website'] and not now['website']:lost.append({'kind':'website','orgnr':org,'company':now['company'],'prior':old['website'],'current_state':now['sections']['website'],'diagnostics':now['website_diagnostics'],'errors':now['errors']})
        current_social={c['value']['url'] for c in now['social']}
        for c in old['social']:
            if c['value']['url'] not in current_social:lost.append({'kind':'social','orgnr':org,'company':now['company'],'prior':c,'current_state':now['sections']['website'],'diagnostics':now['website_diagnostics'],'errors':now['errors']})
    b.update(GLEIF_companies=gleif,TED_companies=ted,news_companies=news,articles=articles,websites_by_proof_type=proof_counts)
    result={'baseline':a,'release':b,'new_websites':sum(x['kind']=='website' for x in extras),'new_social_profiles':sum(x['kind']=='social' for x in extras),'lost_websites':sum(x['kind']=='website' for x in lost),'lost_social_profiles':sum(x['kind']=='social' for x in lost)}
    for name,value in [('summary.json',result),('new-items.json',extras),('lost-items.json',lost)]:
        (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
