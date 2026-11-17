"""Offline: regenerate synthesis for saved envelopes with network access disabled; report section fill."""
import json,socket,sys,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'src'))
def refuse(*a,**k):raise RuntimeError('network access attempted during synthesis')
socket.socket.connect=refuse;socket.create_connection=refuse;socket.getaddrinfo=refuse
from signalpost.models.envelope import Envelope
from signalpost.synthesis.cohort import build_index,context
from signalpost.synthesis.template import generate
from signalpost.synthesis.validate import ALL_SECTIONS
src=Path(sys.argv[1]);out=Path(sys.argv[2]) if len(sys.argv)>2 else None
envs=[Envelope.model_validate(json.loads(l)) for l in src.read_text(encoding='utf8').splitlines() if l.strip()]
index=build_index(envs);empty=collections.Counter();rejections=collections.Counter();examples=collections.defaultdict(list);fill=collections.Counter()
rows=[]
for e in envs:
    s=generate(e,context(e,index));e.run.synthesis=s
    for r in s.checks.rejections:rejections[(r['section'],r['reason'])]+=1
    for k in ALL_SECTIONS:
        if getattr(s.sections,k):fill[k]+=1
        else:empty[k]+=1;examples[k].append(e.organisation_number)
    rows.append({'organisation_number':e.organisation_number,'sections':{k:[x.model_dump() for x in getattr(s.sections,k)] for k in ALL_SECTIONS}})
print(json.dumps({'companies':len(envs),'filled':dict(fill),'empty':dict(empty),'empty_examples':{k:v[:5] for k,v in examples.items()},'rejections':{str(k):v for k,v in rejections.items()}},indent=1))
if out:out.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf8')
