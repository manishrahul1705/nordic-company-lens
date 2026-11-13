"""Offline replay of rejected contact-only sites and malformed social links."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.config import Config
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate
from signalpost.web.html import Page
from signalpost.web.policy import domain
from signalpost.web.social import profile_url
from final_precision_extract import ROOT,OUT,CLONE,source

def main():
 records=json.loads((OUT/'special-review-input.json').read_text(encoding='utf8'));cfg=Config(organisations=OUT/'orgnrs.txt',output=OUT/'unused',report=OUT/'unused-report');sites=[];social=[]
 for r in records:
  if r['category']=='website':
   contacts=r.get('registry_contacts',{});addr=contacts.get('identity.registered_address') or {};context={'name':r['company'],'email':contacts.get('identity.registered_email'),'phone':contacts.get('identity.registered_phone'),'mobile':contacts.get('identity.registered_mobile'),'street':addr.get('adresse'),'postcode':addr.get('postnummer'),'city':addr.get('poststed')}
   v=r['claim']['value'];proofs=[]
   for e in r['sources']:
    p=Page(source(e['content_sha256']).encode('utf8'),e['source_url']);proof=candidate_proof(p,r['orgnr'],context,Candidate(v['final_url'],domain(v['final_url']),v['candidate_origin']),[],cfg)
    proofs.append({'url':e['source_url'],'level':proof.level,'type':proof.proof_type,'reason':proof.reason})
   sites.append({'orgnr':r['orgnr'],'company':r['company'],'prior_type':v['proof_type'],'proof_page_retained':any(p['level']=='VERIFIED' for p in proofs),'proofs':proofs})
  elif r['category']=='social':social.append({'orgnr':r['orgnr'],'url':r['claim']['value']['url'],'valid_profile_url':profile_url(r['claim']['value']['url']) is not None})
 result={'mode':'Offline proof-page decision replay only; original outputs untouched. Final-code live rerun is recorded separately.','sites':sites,'social_urls':social}
 (OUT/'offline-correction-replay.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'removed_proof_pages':[r for r in sites if not r['proof_page_retained']],'rejected_urls':[r for r in social if not r['valid_profile_url']]},ensure_ascii=True,indent=2))
if __name__=='__main__':main()
