"""Unmodified strict verifier, timed separately from the official command."""
import json
from pathlib import Path
import subprocess
import sys
import time

root=Path('bench/runs/stage-ag-20261119')
out=Path(__file__).parent
measurement=json.loads((root/'measurement.json').read_text(encoding='utf-8'))
if measurement['projection_exceeds_user_stop_threshold']:
    raise SystemExit('Stop: 1,100-company projection exceeds 3,000 seconds')
command=[sys.executable,'-X','utf8','scripts/verify_output.py','--first',str(root/'envelopes.jsonl'),
         '--organisations','bench/inputs/1000-r3/batch.jsonl','--count','1000',
         '--state-dir',str(root/'state'),'--report',str(root/'report.json')]
start=time.perf_counter()
with (out/'strict-verifier.txt').open('w',encoding='utf-8') as log:
    result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
meta={'command':command,'exit_code':result.returncode,'seconds':round(time.perf_counter()-start,3)}
(out/'verifier-timing.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps(meta,indent=2))
raise SystemExit(result.returncode)
