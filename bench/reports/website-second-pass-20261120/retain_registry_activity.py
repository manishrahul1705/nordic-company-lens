"""Zero-HTTP correction of replay ordering; production merges registry activity later."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.models.shapes import serialize
from signalpost.synthesis.cohort import build_index,context
from signalpost.synthesis.template import generate
from scripts.verify_output import verify


def block_network(event,args):
    if event in {'socket.connect','socket.getaddrinfo'}:raise AssertionError('Offline correction: no network')


def main():
    sys.addaudithook(block_network)
    base=Path('bench/runs/stage-am-live1000');out=Path('bench/runs/website-second-pass-checkpoint-20261120')
    original={}
    for l in (base/'envelopes.jsonl').open(encoding='utf-8'):
        r=Envelope.model_validate(json.loads(l));ev={e.id:e for e in r.evidence}
        original[r.organisation_number]=[c for c in r.claims if c.family=='activity' and c.availability=='available'
            and c.evidence_ids and all(ev[e].source_class!='company_owned' for e in c.evidence_ids)]
    rows=[Envelope.model_validate(json.loads(l)) for l in (out/'envelopes.jsonl').open(encoding='utf-8')]
    restored=0
    for r in rows:
        fields={c.field for c in r.claims};old=[c for c in original[r.organisation_number] if c.field not in fields]
        r.claims.extend(old);restored+=len(old)
    assert restored>0,'Do not apply replay correction twice'
    cohort=build_index(rows);tmp=out/'envelopes-corrected.jsonl'
    with tmp.open('w',encoding='utf-8') as f:
        for r in rows:
            r.run.synthesis=generate(r,context(r,cohort));r.profile=CompactProfile(organisation_number=r.organisation_number,
                values={c.field:c.value for c in r.claims},evidence_ids=[e.id for e in r.evidence],synthesis=r.run.synthesis)
            f.write(json.dumps(serialize(r,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
    result=verify(tmp,out/'state',1000)
    tmp.replace(out/'envelopes.jsonl')
    p=Path(__file__).with_name('measurement.json');m=json.loads(p.read_text(encoding='utf-8'))
    m['prior_official_activity_claims_retained_for_pipeline_order']=restored;m['strict_verifier']=result
    m['offline_correction_HTTP']=0
    p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'restored_prior_official_activity_claims':restored,'HTTP':0,'strict_verifier':result},indent=2))


if __name__=='__main__':main()
