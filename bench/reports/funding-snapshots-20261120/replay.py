"""Zero-HTTP addition replay on the official-BRREG-index saved result."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib,json,os,time
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.models.shapes import serialize
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.funding_snapshots import publish
from signalpost.synthesis.cohort import build_index,context
from signalpost.synthesis.template import generate

base=Path('bench/runs/brreg-index-replay-20261120-new')
original=Path('bench/runs/overnight-all-20261120')
out=Path('bench/runs/funding-snapshots-final-20261120');reports=Path(__file__).parent
if out.exists():raise SystemExit('Refusing to reuse replay state')
out.mkdir(parents=True);state=out/'state';(state/'blobs').mkdir(parents=True)
for p in (original/'state/blobs').iterdir():
    if p.is_file():os.link(p,state/'blobs'/p.name)
blobs=BlobStore(state);rows=[];before={};counts=Counter();companies=defaultdict(set);added=[];t=time.perf_counter()
for line in (base/'envelopes.jsonl').open(encoding='utf-8'):
    row=Envelope.model_validate(json.loads(line));before[row.organisation_number]={c.id for c in row.claims if c.availability=='available'}
    publish(row,blobs)
    for c in row.claims:
        if c.family!='funding':continue
        kind=c.field.split('.')[0];counts[kind]+=1;companies[kind].add(row.organisation_number)
        added.append({'orgnr':row.organisation_number,'company':next(c.value for c in row.claims if c.field=='identity.legal_name'),
            'claim':c.model_dump(mode='json'),'evidence':[e.model_dump(mode='json') for e in row.evidence if e.id in c.evidence_ids]})
    rows.append(row)
cohort=build_index(rows);missing=[];now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
with (out/'envelopes.jsonl').open('w',encoding='utf-8') as f:
    for row in rows:
        current={c.id for c in row.claims if c.availability=='available'};missing.extend(sorted(before[row.organisation_number]-current))
        row.run.completed_at=now;row.completed_at=now
        row.run.synthesis=generate(row,context(row,cohort))
        row.profile=CompactProfile(organisation_number=row.organisation_number,values={c.field:c.value for c in row.claims},evidence_ids=[e.id for e in row.evidence]);row.profile.synthesis=row.run.synthesis
        f.write(json.dumps(serialize(row,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
report=json.loads((base/'report.json').read_text(encoding='utf-8'));report['replay']={'baseline':str(base),'new_http_requests':0,'kind':'Bundled funding snapshot addition replay'};report['site']={'state':'skipped','reason':'saved output replay; sample pages rendered separately'}
(out/'report.json').write_text(json.dumps(report),encoding='utf-8')
summary={'baseline':str(base),'replay':str(out),'companies':len(rows),'new_http_requests':0,'baseline_http_requests':report['requests'],
    'claims_before':sum(map(len,before.values())),'claims_after':sum(c.availability=='available' for r in rows for c in r.claims),
    'prior_claims_removed':missing,'families':{k:{'companies':len(companies[k]),'claims':counts[k]} for k in ['research','state_aid']},'seconds':round(time.perf_counter()-t,3)}
(reports/'measurement.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');(reports/'new-claims.json').write_text(json.dumps(added,ensure_ascii=False,indent=1),encoding='utf-8');print(json.dumps(summary,indent=2))
