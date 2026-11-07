"""Re-extract corrected TED amounts offline; retain pre-correction bytes compressed."""
import asyncio
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import time
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.sources.http import Response
from signalpost.sources.official_extra import award_extract
from signalpost.sources.blobstore import BlobStore
from signalpost.io.envelope_writer import write
from signalpost.profiles import write as write_profiles
from signalpost.synthesis.service import Service
from signalpost.site import generate_site
from scoreboard import build_scoreboard,read_jsonl


async def main():
    base=Path('bench/runs/20261107T073418068646Z-42def8c')
    out=base/'enrichment-continuation';before=out/'before-amounts';before.mkdir(exist_ok=False)
    hashes={}
    for name in ['envelopes.jsonl','profiles.jsonl','report.json','execution.json','scoreboard.json']:
        h=hashlib.sha256()
        with (out/name).open('rb') as src,gzip.open(before/(name+'.gz'),'wb') as dst:
            for block in iter(lambda:src.read(1024*1024),b''):h.update(block);dst.write(block)
        hashes[name]=h.hexdigest()
    (before/'SHA256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    clock=time.monotonic();rows=[];changes=[];service=Service()
    for line in gzip.open(before/'envelopes.jsonl.gz','rt',encoding='utf-8'):
        row=Envelope.model_validate_json(line);old=[c for c in row.claims if c.field.startswith('procurement_award.')]
        records={e.id:e for e in row.evidence};new={};evidence={}
        for claim in old:
            ev=records[claim.evidence_ids[0]];body=(base/'state/blobs'/ev.content_sha256).read_bytes()
            assert hashlib.sha256(body).hexdigest()==ev.content_sha256
            response=Response(body,200,ev.source_url,ev.retrieved_at,ev.content_sha256)
            section=award_extract(response,claim.value['notice_id'],row.organisation_number,date.fromisoformat(ev.retrieved_at[:10]))
            for c in section.claims:
                if c.field==claim.field:new[c.field]=c
            evidence.update({e.id:e for e in section.evidence})
        if old:
            assert {c.field for c in old}==set(new)
            for c in old:
                if c.value!=new[c.field].value:changes.append({'orgnr':row.organisation_number,'old_id':c.id,'new_id':new[c.field].id,'old':c.value,'new':new[c.field].value})
            row.claims=[c for c in row.claims if not c.field.startswith('procurement_award.')]+list(new.values())
            row.evidence=list({**records,**evidence}.values())
            row.run.synthesis=await service.summarize(row);row.profile.synthesis=row.run.synthesis
        row.profile=CompactProfile(organisation_number=row.organisation_number,values={c.field:c.value for c in row.claims},evidence_ids=[e.id for e in row.evidence],synthesis=row.run.synthesis)
        rows.append(row)
    write(out/'envelopes.jsonl',rows,'union',BlobStore(base/'state'),512)
    write_profiles(out/'profiles.jsonl',rows)
    site=generate_site(out/'envelopes.jsonl',out/'site')
    report=json.loads(gzip.open(before/'report.json.gz','rt',encoding='utf-8').read())
    report['site']={'state':'available',**site}
    report['saved_xml_amount_projection']={'http_requests':0,'claim_count_unchanged':True,'changed_claim_values':len(changes),'seconds':time.monotonic()-clock,'preserved_before':str(before),'source_bytes_unchanged':True}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    execution=json.loads(gzip.open(before/'execution.json.gz','rt',encoding='utf-8').read())
    score=build_scoreboard(read_jsonl(out/'envelopes.jsonl'),report,read_jsonl(out/'profiles.jsonl'),execution={'commit':execution['commit'],'exit_code':0,'wall_seconds':execution['cumulative_elapsed_seconds']})
    (out/'scoreboard.json').write_text(json.dumps(score,indent=2),encoding='utf-8')
    dest=Path('bench/reports/s6-step20')
    (dest/'amount-projection.json').write_text(json.dumps({'metrics':report['saved_xml_amount_projection'],'changes':changes},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['saved_xml_amount_projection']))


if __name__=='__main__':asyncio.run(main())
