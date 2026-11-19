"""Fresh-state default run; the existing five Wikidata requests are widened."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

out = Path('bench/runs/stage-ag-20261119')
if out.exists():raise SystemExit('Refusing to reuse runtime state')
out.mkdir(parents=True)
inputs=Path('bench/inputs/1000-r3/batch.jsonl')
command=[sys.executable,'-m','signalpost.cli','run','--organisations',str(inputs),
         '--output',str(out/'envelopes.jsonl'),'--report',str(out/'report.json'),
         '--state-dir',str(out/'state'),'--site-dir',str(out/'site'),'--expected-count','1000']
meta={'command':command,'input_sha256':hashlib.sha256(inputs.read_bytes()).hexdigest(),
      'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('src').rglob('*.py')},
      'started_at':datetime.now(timezone.utc).isoformat(),
      'conditions':'Fresh state; default sources/site ON; no concurrent test suite from this task; other host/provider activity uncontrolled.'}
(out/'measurement.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
env=os.environ.copy();env['PYTHONUTF8']='1'
start=time.perf_counter()
with (out/'stdout.txt').open('w',encoding='utf-8') as stdout,(out/'stderr.txt').open('w',encoding='utf-8') as stderr:
    result=subprocess.run(command,stdout=stdout,stderr=stderr,env=env)
meta.update(wall_seconds=round(time.perf_counter()-start,3),exit_code=result.returncode,
            ended_at=datetime.now(timezone.utc).isoformat())
meta['projection_1100_seconds']=round(meta['wall_seconds']*1.1,3)
meta['projection_exceeds_user_stop_threshold']=meta['projection_1100_seconds']>3000
meta['source_unchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in meta['source_sha256'].items())
(out/'measurement.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in meta.items() if k!='source_sha256'},indent=2))
raise SystemExit(result.returncode or (4 if meta['projection_exceeds_user_stop_threshold'] else 0))
