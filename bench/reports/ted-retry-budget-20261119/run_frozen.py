"""Time the official default command with fresh state and a frozen input."""
import hashlib,json,os,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path

out=Path(sys.argv[1] if len(sys.argv)>1 else 'bench/runs/ted-budget-20261119')
if out.exists():raise SystemExit('Refusing to reuse runtime state')
out.mkdir(parents=True)
input_path=Path('bench/inputs/1000-r3/batch.jsonl')
cmd=[sys.executable,'-m','signalpost.cli','run','--organisations',str(input_path),
     '--output',str(out/'envelopes.jsonl'),'--report',str(out/'report.json'),
     '--state-dir',str(out/'state'),'--site-dir',str(out/'site'),'--expected-count','1000']
meta={'input_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),
      'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
      'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('src').rglob('*.py')},
      'command':cmd,'started_at':datetime.now(timezone.utc).isoformat(),
      'conditions':'Fresh state; defaults including site ON and 3600-second local budget; no bulk; live sources.'}
Path('bench/reports/ted-retry-budget-20261119/source.patch').write_bytes(subprocess.check_output(['git','diff']))
(out/'measurement.json').write_text(json.dumps(meta,indent=2))
env=os.environ.copy();env['PYTHONUTF8']='1'
began=time.perf_counter()
with (out/'process.txt').open('w',encoding='utf-8') as stdout,(out/'stderr.txt').open('w',encoding='utf-8') as stderr:
    result=subprocess.run(cmd,stdout=stdout,stderr=stderr,env=env)
meta.update(wall_seconds=round(time.perf_counter()-began,3),exit_code=result.returncode,
            ended_at=datetime.now(timezone.utc).isoformat())
(out/'measurement.json').write_text(json.dumps(meta,indent=2))
print(json.dumps({k:v for k,v in meta.items() if k!='source_sha256'},indent=2))
raise SystemExit(result.returncode)
