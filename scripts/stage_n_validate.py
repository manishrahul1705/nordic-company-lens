"""Offline-only Stage N verification with source and output integrity checks."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from signalpost.site import generate_site
from signalpost.power import SystemAwake
out=ROOT/'bench/reports/stage-n';source=ROOT/'bench/runs/stage-g-run1/envelopes.jsonl'
inputs=[source,source.with_name('profiles.jsonl')]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
with SystemAwake():
    with (out/'pytest.txt').open('wb') as f:r=subprocess.run(['uv','run','--frozen','pytest','-q'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    (out/'test-exit.json').write_text(json.dumps({'exit_code':r.returncode})+'\n')
    if r.returncode:raise SystemExit(r.returncode)
    site=ROOT/'bench/cache/stage-n-after'
    metrics=generate_site(source,site)
    first={str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}
    again=generate_site(source,site)
    second={str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}
    assert first==second
    assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    (out/'generation-after.json').write_text(json.dumps({'first':metrics,'second':again,'byte_identical_files':len(first),'input_sha256_unchanged':before,'warnings':[]},indent=2)+'\n')
    command=['uv','run','--no-project','--with','playwright','python','scripts/stage_n_audit.py','--phase','after']
    with (out/'browser-after.log').open('wb') as log:code=subprocess.call(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    print('Browser exit',code,flush=True)
    raise SystemExit(code)
