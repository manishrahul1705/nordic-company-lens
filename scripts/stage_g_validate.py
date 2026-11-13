"""Stage G: unchanged-runtime tests and two sequential frozen live runs."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from signalpost.power import SystemAwake
os.chdir(ROOT);out=ROOT/'bench/reports/stage-g';out.mkdir(parents=True,exist_ok=True)
assert not subprocess.check_output(['git','diff','007b34f','--','src','tests','pyproject.toml','uv.lock'])
files=sorted(Path('src').rglob('*.py'))
hashes={str(p).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(out/'runtime-identity.json').write_text(json.dumps({'requested_runtime':'007b34fb691eb02caf121e9da6dc19c3c5bc603a','current_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'diff_007b34f_src_tests_lock':'empty','sha256':hashes},indent=2)+'\n')
with SystemAwake():
    with (out/'pytest.txt').open('wb') as log:
        test=subprocess.run(['uv','run','--frozen','pytest','-q'],stdout=log,stderr=subprocess.STDOUT)
    (out/'test-exit.json').write_text(json.dumps({'exit_code':test.returncode})+'\n')
    if test.returncode:raise SystemExit(test.returncode)
    for number in (1,2):
        assert hashes=={str(p).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        command=[sys.executable,'-u','scripts/r3_benchmark.py','--repo',str(ROOT),'--input',str(ROOT/'bench/inputs/1000-r3/batch.jsonl'),'--output',str(ROOT/f'bench/runs/stage-g-run{number}')]
        print('START run',number,flush=True)
        with (out/f'benchmark{number}.log').open('wb') as log:code=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
        print('FINISH run',number,'exit',code,flush=True)
        if code:raise SystemExit(code)
