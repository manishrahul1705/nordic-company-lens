"""Apply the audited publication rollback to retained output, without a crawl.

This is a saved-evidence projection, never a second benchmark measurement.
"""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from signalpost.models.envelope import Envelope
from signalpost.models.shapes import serialize
from signalpost.sources.blobstore import BlobStore
from signalpost.web.entity_scope import enforce
from signalpost.synthesis.template import generate
from signalpost.profiles import write as write_profiles


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('run',type=Path)
    parser.add_argument('out',type=Path)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    rows=[Envelope.model_validate(json.loads(line)) for line in (args.run/'envelopes.jsonl').read_text(encoding='utf8').splitlines()]
    before={r.organisation_number:{c.field for c in r.claims} for r in rows}
    # enforce reads retained registry nominations plus exact output registry
    # declarations; no network or candidate discovery is involved.
    enforce(rows,BlobStore(args.run/'state'),SimpleNamespace(domain_owners={}))
    changes=[]
    for row in rows:
        removed=before[row.organisation_number]-{c.field for c in row.claims}
        if removed:changes.append({'organisation_number':row.organisation_number,'withheld_fields':sorted(removed)})
        row.run.synthesis=generate(row)
        row.profile.synthesis=row.run.synthesis
    with (args.out/'envelopes.jsonl').open('w',encoding='utf8') as f:
        for row in rows:f.write(json.dumps(serialize(row,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
    write_profiles(args.out/'profiles.jsonl',rows)
    (args.out/'projection.json').write_text(json.dumps({'source':str(args.run),'method':'offline policy projection; no crawl; no replacement candidates tested','withheld':changes},indent=2)+'\n',encoding='utf8')
    print({'companies':len(rows),'withheld_companies':len(changes)},flush=True)


if __name__=='__main__':main()
