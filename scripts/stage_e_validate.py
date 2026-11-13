"""Detached Stage E tests then one credential-free frozen benchmark."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from signalpost.power import SystemAwake
import r3_benchmark
os.chdir(ROOT)
out=ROOT/'bench/reports/stage-e';out.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256((ROOT/'bench/inputs/1000-r3/batch.jsonl').read_bytes()).hexdigest()=='7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782'
(out/'runtime.patch').write_bytes(subprocess.check_output(['git','diff','--','src/']))
with SystemAwake():
    with (out/'pytest.txt').open('wb') as log:
        result=subprocess.run(['uv','run','--frozen','pytest','-q'],stdout=log,stderr=subprocess.STDOUT)
    (out/'test-exit.json').write_text(json.dumps({'exit_code':result.returncode})+'\n')
    if result.returncode:raise SystemExit(result.returncode)
    sys.argv=['r3_benchmark','--repo',str(ROOT),'--input',str(ROOT/'bench/inputs/1000-r3/batch.jsonl'),'--output',str(ROOT/'bench/runs/stage-e-live')]
    r3_benchmark.main()
