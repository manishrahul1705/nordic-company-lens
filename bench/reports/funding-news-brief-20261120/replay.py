"""Offline brief replay; network connections are forbidden by a Python audit hook."""
import json,sys,time,hashlib,subprocess
from pathlib import Path
from collections import Counter
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.models.evidence import digest,canonical
from signalpost.models.shapes import serialize
from signalpost.synthesis.cohort import build_index,context
from signalpost.synthesis.template import generate
from signalpost.synthesis.validate import ALL_SECTIONS,sentence_error
from signalpost.synthesis.funding_news import funding_sentence,news_sentences

def no_network(event,args):
 if event in {'socket.connect','socket.getaddrinfo'}:raise AssertionError('Offline replay forbids network: '+event)
sys.addaudithook(no_network)
base=Path('bench/runs/news-items-20261120');out=Path('bench/runs/funding-news-brief-final-20261120');reports=Path(__file__).parent
if out.exists():raise SystemExit('Refusing reused replay output')
out.mkdir(parents=True);rows=[];before=Counter();before_by={};t=time.perf_counter();linked=[]
for line in (base/'envelopes.jsonl').open(encoding='utf-8'):
 r=Envelope.model_validate(json.loads(line));before_by[r.organisation_number]=r.run.synthesis
 for k in ALL_SECTIONS:before[k]+=len(getattr(r.run.synthesis.sections,k))
 proof=next((c for c in r.claims if c.field=='official_website' and c.availability=='available'),None)
 for c in r.claims:
  if c.field.startswith('news_item.'):
   assert proof and proof.value['identity_level']=='VERIFIED' and set(proof.evidence_ids)&set(c.evidence_ids)
   old=c.id;c.value['identity_claim_id']=proof.id;c.id=digest([r.organisation_number,c.field,canonical(c.value),c.availability,c.reporting_period]);linked.append({'orgnr':r.organisation_number,'old_id':old,'new_id':c.id,'identity_claim_id':proof.id})
 rows.append(r)
cohort=build_index(rows);after=Counter();funding=[];news=[]
with (out/'envelopes.jsonl').open('w',encoding='utf-8') as stream:
 for row in rows:
  row.run.synthesis=generate(row,context(row,cohort));row.profile=CompactProfile(organisation_number=row.organisation_number,values={c.field:c.value for c in row.claims},evidence_ids=[e.id for e in row.evidence]);row.profile.synthesis=row.run.synthesis
  for k in ALL_SECTIONS:after[k]+=len(getattr(row.run.synthesis.sections,k))
  name=next(c.value for c in row.claims if c.field=='identity.legal_name')
  def record(s):
   assert sentence_error(s,row) is None
   claims=[c for c in row.claims if c.id in s.claim_ids];assert len(claims)==len(s.claim_ids) and all(c.availability=='available' and c.evidence_ids for c in claims)
   return {'orgnr':row.organisation_number,'company':name,'sentence':s.model_dump(),'claims':[c.model_dump(mode='json') for c in claims]}
  f=funding_sentence(row)
  if f:
   assert any(s.text==f.text for s in row.run.synthesis.sections.standing);funding.append(record(f))
  for n in news_sentences(row):
   assert any(s.text==n.text for s in row.run.synthesis.sections.changes)
   assert any(s.text==n.text for s in row.run.synthesis.brief.changes);news.append(record(n))
  stream.write(json.dumps(serialize(row,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
report=json.loads((base/'report.json').read_text());report['replay']={'kind':'funding and news brief synthesis','new_http_requests':0,'network_connections_forbidden':True};(out/'report.json').write_text(json.dumps(report),encoding='utf-8')
summary={'baseline':str(base),'output':str(out),'new_http_requests':0,'network_guard':'socket.connect and getaddrinfo forbidden',
 'funding_briefs_gained':len(funding),'funding_sentences':len(funding),'news_briefs_gained':len({n['orgnr'] for n in news}),'news_sentences':len(news),
 'synthesis_sentences_before':sum(before.values()),'synthesis_sentences_after':sum(after.values()),'sections_before':dict(before),'sections_after':dict(after),
 'published_claims':sum(c.availability=='available' for r in rows for c in r.claims),'news_claim_identity_links_added':len(linked),'seconds':round(time.perf_counter()-t,3),
 'validator_sha256':hashlib.sha256(Path('src/signalpost/synthesis/validate.py').read_bytes()).hexdigest(),
 'test_count_before':1716}
(reports/'measurement.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');(reports/'sentences.json').write_text(json.dumps({'funding':funding,'news':news},ensure_ascii=False,indent=1),encoding='utf-8');(reports/'news-identity-links.json').write_text(json.dumps(linked,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
