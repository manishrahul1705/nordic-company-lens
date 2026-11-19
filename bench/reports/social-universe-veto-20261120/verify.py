import json
from pathlib import Path
import subprocess
import sys
import time

out=Path(__file__).parent
run=Path('bench/runs/social-universe-veto-20261120')
command=[sys.executable,'-X','utf8','scripts/verify_output.py','--first',str(run/'envelopes.jsonl'),
         '--organisations','bench/inputs/1000-r3/batch.jsonl','--count','1000',
         '--state-dir','bench/runs/stage-ag-20261119/state','--report',str(run/'report.json')]
start=time.perf_counter()
with (out/'strict-verifier.txt').open('w',encoding='utf-8') as output:
    result=subprocess.run(command,stdout=output,stderr=subprocess.STDOUT)
meta={'command':command,'exit_code':result.returncode,'seconds':round(time.perf_counter()-start,3)}
(out/'verifier-timing.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps(meta,indent=2))
raise SystemExit(result.returncode)
