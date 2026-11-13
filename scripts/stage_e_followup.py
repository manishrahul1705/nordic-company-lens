"""Wait for Stage E benchmark, then fresh-clone refresh validation."""
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
record=ROOT/'bench/runs/stage-e-live/execution.json'
while True:
    if record.exists():
        data=json.loads(record.read_text())
        if 'exit_code' in data:
            if data['exit_code']:raise SystemExit(data['exit_code'])
            break
    fail=ROOT/'bench/reports/stage-e/test-exit.json'
    if fail.exists() and json.loads(fail.read_text())['exit_code']:raise SystemExit(1)
    time.sleep(15)
raise SystemExit(subprocess.call([sys.executable,'-u','scripts/stage_e_refresh.py'],cwd=ROOT))
