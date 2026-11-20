"""Offline additive Stage AS replay; fail on any socket access."""
import json,sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.models.shapes import serialize
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.approval_websites import publish
from signalpost.synthesis.cohort import build_index,context
from signalpost.synthesis.template import generate
from scripts.verify_output import verify

def block(event,args):
    if event in ('socket.connect','socket.getaddrinfo'):raise AssertionError('Offline replay forbids network')
sys.addaudithook(block)
base=Path('bench/runs/website-second-pass-checkpoint-20261120');out=Path('bench/runs/stage-as-offline');out.mkdir(exist_ok=True)
shutil.copytree(base/'state'/'blobs',out/'state'/'blobs',dirs_exist_ok=True)
rows=[Envelope.model_validate(json.loads(l))for l in (base/'envelopes.jsonl').open(encoding='utf-8')]
blobs=BlobStore(out/'state');reviews={};counts={}
for r in rows:
    old=[c.model_dump()for c in r.claims];publish(r,blobs)
    assert [c.model_dump()for c in r.claims[:len(old)]]==old
    for c in r.claims[len(old):]:
        kind=c.field.split('.')[0];reviews.setdefault(kind,[]).append({'company':r.run.legal_identity.get('legal_name'),'orgnr':r.organisation_number,'claim':c.model_dump(),'evidence':[e.model_dump()for e in r.evidence if e.id in c.evidence_ids]})
for n in (1000,100):
    selected=rows[:n];cohort=build_index(selected);dest=out/('envelopes'+str(n)+'.jsonl')
    with dest.open('w',encoding='utf-8')as f:
        for r in selected:
            r.run.synthesis=generate(r,context(r,cohort));r.profile=CompactProfile(organisation_number=r.organisation_number,values={c.field:c.value for c in r.claims},evidence_ids=[e.id for e in r.evidence],synthesis=r.run.synthesis)
            f.write(json.dumps(serialize(r,'union'),ensure_ascii=False)+'\n')
    stats={k:{'companies':len({r.organisation_number for r in selected if any(c.field.startswith(k+'.')for c in r.claims)}),'claims':sum(c.field.startswith(k+'.')for r in selected for c in r.claims)}for k in reviews}
    counts[str(n)]={'HTTP':0,'counts':stats,'verifier':verify(dest,out/'state',n)}
p=Path(__file__).parent;(p/'measurement.json').write_text(json.dumps(counts,indent=2),encoding='utf-8');(p/'review.json').write_text(json.dumps(reviews,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(counts,indent=2))
