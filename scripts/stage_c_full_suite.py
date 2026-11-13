"""Run Stage C full-suite validation with a temporary idle-sleep request."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from signalpost.power import SystemAwake
out=ROOT/'bench/reports/stage-c';out.mkdir(exist_ok=True)
with SystemAwake():
    with (out/'pytest.txt').open('wb') as f:
        result=subprocess.run(['uv','run','--frozen','pytest','-q'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
(out/'test-exit.json').write_text(json.dumps({'exit_code':result.returncode})+'\n')
print('Stage C suite exit',result.returncode,flush=True)
raise SystemExit(result.returncode)
