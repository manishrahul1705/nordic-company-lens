"""Offline conservative projection of saved R3 claims; never fetches a URL."""
import hashlib,json,sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.web.html import Page
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate
from signalpost.web.policy import domain
from signalpost.web.social import attributed,profile_key,matches_profile,company_names
from signalpost.config import Config
from r3_analyze import rows
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'bench/runs/r3-candidate';OUT=ROOT/'bench/reports/r3-benchmark'

def main():
    cfg=Config(organisations=ROOT/'bench/inputs/1000-r3/batch.jsonl',output=RUN/'unused',report=RUN/'unused-report')
    counts=Counter();facts=0;changes=[];sites={};socials={};body_checks=0
    original_hash=hashlib.sha256((RUN/'envelopes.jsonl').read_bytes()).hexdigest()
    for row in rows(RUN/'envelopes.jsonl'):
        org=row['organisation_number'];claims=row['claims'];available=[c for c in claims if c['availability']=='available'];name=next((c['value'] for c in available if c['field']=='identity.legal_name'),'')
        fields={c['field']:c['value'] for c in available};addr=fields.get('identity.registered_address') or {}
        units={c['value']['organisation_number']:{'orgnr':c['value']['organisation_number'],'name':c['value'].get('name'),'address':c['value'].get('address')} for c in available if c['field'].startswith('subunits.unit.') and isinstance(c['value'],dict)}
        for c in available:
            if c['field'].startswith('subunits.detail.'):
                _,_,number,field=c['field'].split('.',3)
                if number in units:units[number][field.removeprefix('registered_')]=c['value']
        context={'name':name,'email':fields.get('identity.registered_email'),'phone':fields.get('identity.registered_phone'),'mobile':fields.get('identity.registered_mobile'),'street':addr.get('adresse'),'postcode':addr.get('postnummer'),'city':addr.get('poststed'),'municipality':addr.get('kommune'),'subunits':list(units.values()),'registered_brands':[c['value'] for c in available if c['field']=='public_brand' and isinstance(c['value'],str)]}
        website=next((c for c in available if c['field']=='official_website'),None);parsed={};site_ok=bool(website);new_proof=None
        if website:
            host=domain(website['value']['final_url'])
            for e in row['evidence']:
                if e.get('source_class')!='company_owned' or domain(e['source_url'])!=host or 'robots.txt' in e['source_url']:continue
                key=(e['source_url'],e['content_sha256'])
                if key in parsed:continue
                body=(RUN/'state/blobs'/e['content_sha256']).read_bytes()
                assert hashlib.sha256(body).hexdigest()==e['content_sha256'];body_checks+=1
                if b'<html' in body.lower() or b'<!doctype html' in body.lower():parsed[key]=Page(body,e['source_url'])
            if website['value'].get('proof_type') in {'legal_name_masthead','unique_legal_name_domain','registry_email_on_site','registry_phone_on_site'}:
                v=website['value'];candidate=Candidate(v['final_url'],host,v['candidate_origin'],v.get('matched_via_subunit'))
                proofs=[(candidate_proof(p,org,context,candidate,[],cfg),p) for p in parsed.values()]
                verified=[(p,page) for p,page in proofs if p.level=='VERIFIED']
                veto=any(p.level in {'REJECT','BLOCKED'} and p.reason in {'foreign_orgnr','different_legal_entity','parked','placeholder','hosting_default','shared_registry_domain'} for p,_ in proofs)
                site_ok=bool(verified) and not veto
                if site_ok:
                    proof,page=verified[0];new_proof={'proof_type':proof.proof_type,'proof_page_url':page.url,'token':proof.token,'signals':proof.signals,'points':proof.points};sites[org]={**v,**new_proof}
                else:changes.append({'orgnr':org,'company':name,'kind':'website_removed','url':v['final_url'],'before_proof':v['proof_type'],'rechecked_proofs':sorted({p.proof_type+':'+p.level+':'+p.reason for p,_ in proofs})})
            if site_ok and org not in sites:sites[org]=website['value']
        allowed=set()
        if website and site_ok:
            for page in parsed.values():allowed.update(attributed(page,website['value'],context))
        kept=[]
        for c in available:
            field=c['field'];remove=False
            if website and not site_ok:
                remove=(c.get('family')=='website' or field.startswith(('social_profile.','dated_item.','hiring.site_job.')))
            if field.startswith('social_profile.'):
                target=c['value']['url'];remove=remove or (target not in allowed and not matches_profile(target,company_names(context)))
                if remove:changes.append({'orgnr':org,'company':name,'kind':'social_removed','url':target,'reason':'site_proof_removed' if not site_ok else 'strict_company_or_verified_brand_name_required'})
            if not remove:kept.append(c)
        for key,present in [('websites',site_ok),('social_companies',any(c['field'].startswith(('social_profile.','registry_social.')) for c in kept)),('jobs',any(c['field'].startswith(('hiring.job.','hiring.site_job.')) for c in kept)),('activity',any(c.get('family')=='activity' for c in kept))]:counts[key]+=bool(present)
        socials[org]=[c['value']['url'] for c in kept if c['field'].startswith(('social_profile.','registry_social.'))]
        facts+=len({(c['field'],json.dumps(c['value'],sort_keys=True,ensure_ascii=True),json.dumps(c.get('reporting_period'),sort_keys=True)) for c in kept if c['value'] is not None})
    result={**counts,'facts':facts,'mode':'Offline conservative claim projection, not a new live benchmark. Removed-site derived website claims and site article/job claims withheld. Original outputs untouched; no alternate candidate discovery or synthesis/site regeneration. Runtime/HTTP remain those measured before narrowing.','source_envelope_sha256':original_hash,'verified_saved_body_checks':body_checks,'changes':changes,'retained_websites':sites,'retained_social':socials}
    (OUT/'offline-projection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in {'changes','retained_websites','retained_social'}},indent=2))
    print(json.dumps(changes,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
