"""Detached release validation worker; no crawl collection or credentials."""
import argparse,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from signalpost.power import SystemAwake
import r3_benchmark
OUT=ROOT/'bench/reports/r3-release'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--benchmark-only',action='store_true');args=parser.parse_args()
    os.chdir(ROOT);env=dict(os.environ)
    for k in list(env):
        if any(x in k.upper() for x in ('API_KEY','APIKEY','TOKEN','SECRET','CREDENTIAL')) or k.startswith(('SIGNALPOST_SEARCH','SIGNALPOST_LLM')):env.pop(k)
    env['PYTHONUTF8']='1';os.environ.clear();os.environ.update(env)
    with SystemAwake() as awake:
        print(json.dumps({'power':awake.result}),flush=True)
        if not args.benchmark_only:
            with (OUT/'pytest-final.txt').open('wb') as f:r=subprocess.run(['uv','run','--frozen','pytest','-q'],env=env,stdout=f,stderr=subprocess.STDOUT)
            (OUT/'test-exit.json').write_text(json.dumps({'exit_code':r.returncode})+'\n')
            print('Full suite exit',r.returncode,flush=True)
            if r.returncode:raise SystemExit(r.returncode)
        sys.argv=['r3_benchmark','--repo',str(ROOT),'--input',str(ROOT/'bench/inputs/1000-r3/batch.jsonl'),'--output',str(ROOT/'bench/runs/r3-release-final')]
        r3_benchmark.main()

if __name__=='__main__':main()
