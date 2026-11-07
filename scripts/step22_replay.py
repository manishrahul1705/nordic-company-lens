"""Replay only precision-affected companies from saved source bytes; zero HTTP."""
import asyncio,collections,hashlib,json
from pathlib import Path
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.sources import regnskap
from signalpost.web.entity_scope import enforce
from signalpost.synthesis.service import Service
from signalpost.io.envelope_writer import write
from signalpost.profiles import write as write_profiles
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'bench/cache/s6-step22-official';OUT=ROOT/'bench/cache/s6-step22-offline';REPORT=ROOT/'bench/reports/s6-step22'
async def main():
 OUT.mkdir(exist_ok=True);blobs=BlobStore(RUN/'out/state');service=Service();ledger=[]
 for n in [1,2]:
  dest=OUT/f'run{n}';dest.mkdir(exist_ok=True);rows=[];affected=[]
  for line in (RUN/f'validation/run{n}-envelopes.jsonl').open(encoding='utf-8'):
   row=Envelope.model_validate_json(line);es={e.id:e for e in row.evidence};before={c.field:c for c in row.claims};old_ids={c.id for c in row.claims}
   bad=[c for c in row.claims if c.family=='accounts' and any(es[i].extraction_method=='signalpost.pdf_calibration.v1' for i in c.evidence_ids)]
   if bad:
    e=next(es[i] for c in bad for i in c.evidence_ids if es[i].source_class=='official_registry' and '/regnskapsregisteret/' in es[i].source_url)
    body=blobs.read(e.content_sha256);assert hashlib.sha256(body).hexdigest()==e.content_sha256
    section=regnskap.extract(row.organisation_number,Response(body,200,e.source_url,e.retrieved_at,e.content_sha256),blobs);new={c.field:c for c in section.claims}
    for c in bad:
     replacement=new[c.field];assert c.id==replacement.id and c.value==replacement.value and c.reporting_period==replacement.reporting_period
     c.evidence_ids=list(replacement.evidence_ids)
    row.evidence=[e for e in row.evidence if e.extraction_method!='signalpost.pdf_calibration.v1']
   # The sole site with an explicit mismatching full footer publisher.
   # Select by saved pattern, not a company-specific exception.
   proof=next((c for c in row.claims if c.field=='official_website' and c.availability=='available'),None)
   guard_affected=False
   if proof:
    from signalpost.web.html import Page
    from signalpost.web.round2 import real_page
    name=next(c.value for c in row.claims if c.field=='identity.legal_name')
    guard_affected=any(real_page(Page(blobs.read(es[i].content_sha256),es[i].source_url),{'name':name,'allowed_orgnrs':{row.organisation_number}})=='different_legal_entity' for i in proof.evidence_ids if es[i].source_class=='company_owned')
    if guard_affected:enforce([row],blobs,None)
   if bad or guard_affected:
    row.run.synthesis=await service.summarize(row);row.profile.synthesis=row.run.synthesis
    row.profile=CompactProfile(organisation_number=row.organisation_number,values={c.field:c.value for c in row.claims},evidence_ids=[e.id for e in row.evidence],synthesis=row.run.synthesis)
    affected.append({'orgnr':row.organisation_number,'calibration_citations_corrected':len(bad),'removed_fields':sorted(set(before)-{c.field for c in row.claims}),'website_state':row.run.sections.get('website'),'new_claim_ids':sorted({c.id for c in row.claims}-old_ids)})
   rows.append(row)
  write(dest/'envelopes.jsonl',rows,'union',blobs,512);write_profiles(dest/'profiles.jsonl',rows)
  report=json.loads((RUN/f'validation/run{n}-report.json').read_text(encoding='utf-8'));report['offline_precision_replay']={'http_requests':0,'affected_companies':len(affected)}
  (dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
  ledger.append({'run':n,'http_requests':0,'affected':affected,'facts':sum(c.availability=='available' for row in rows for c in row.claims),'sections':{k:dict(collections.Counter(row.run.sections.get(k) for row in rows)) for k in ['identity','roles','subunits','accounts','website','hiring','activity']},'social_companies':sum(any(c.field.startswith(('social_profile.','registry_social.')) and c.availability=='available' for c in row.claims) for row in rows)})
 (REPORT/'offline-replay.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([{k:v for k,v in x.items() if k!='affected'} for x in ledger]))
if __name__=='__main__':asyncio.run(main())
