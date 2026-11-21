"""Copy the self-sufficient extract and reproduce checks while denying bench/runs reads."""
import hashlib,runpy,shutil,sys
from pathlib import Path
source=Path(__file__).parent/'accuracy'
dest=Path(sys.argv[1] if len(sys.argv)>1 else 'bench/cache/final-ap-extract-only').resolve()
assert not dest.exists(),'Choose a fresh destination'
shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__'))
assert not (dest/'bench'/'runs').exists()
def guard(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        p=str(args[0]).replace('\\','/').lower()
        if '/bench/runs/'in p or p.endswith('/bench/runs'):raise AssertionError('bench/runs is forbidden for this reproduction')
sys.addaudithook(guard)
sys.path.insert(0,str(dest))
expected=__import__('json').loads((dest/'hand-review-support.json').read_text(encoding='utf-8'))
for script in ['review_support.py','adjudicate_sample.py','reproduce.py','attribution_audit.py','adjudicate_bulk.py']:
    sys.argv=[str(dest/script)];runpy.run_path(str(dest/script),run_name='__main__')
assert __import__('json').loads((dest/'hand-review-support.json').read_text(encoding='utf-8'))==expected
print('PASS: extract-only reproduction, with all bench/runs opens forbidden; regenerated hand-review context is identical.')
