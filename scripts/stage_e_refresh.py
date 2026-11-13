"""Fresh-clone README refresh pair; strict verifier remains unchanged."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLONE=ROOT/'bench/cache/stage-e-clone';OUT=ROOT/'bench/reports/stage-e/refresh'
sys.path.insert(0,str(ROOT/'src'))
from signalpost.power import SystemAwake


def main():
    global CLONE,OUT
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='first');args=parser.parse_args()
    if args.attempt!='first':
        assert args.attempt.isalnum()
        CLONE=ROOT/('bench/cache/stage-e-clone-'+args.attempt);OUT=ROOT/('bench/reports/stage-e/refresh-'+args.attempt)
    OUT.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ)
    for k in list(env):
        if any(x in k.upper() for x in ('API_KEY','APIKEY','TOKEN','SECRET','CREDENTIAL')) or k.startswith(('SIGNALPOST_SEARCH','SIGNALPOST_LLM')):env.pop(k)
    env['PYTHONUTF8']='1'
    with SystemAwake():
        for name,command in [('clone',['git','clone','--local','--no-hardlinks',str(ROOT),str(CLONE)]),('sync',['uv','sync','--frozen'])]:
            with (OUT/(name+'.log')).open('wb') as log:subprocess.run(command,cwd=ROOT if name=='clone' else CLONE,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        source=ROOT/'bench/reports/release/orgnrs.txt';shutil.copyfile(source,CLONE/'orgnrs.txt')
        command=['uv','run','--frozen','signalpost','run','--organisations','orgnrs.txt','--output','out/envelopes.jsonl','--profiles-output','out/profiles.jsonl','--report','out/report.json','--state-dir','out/state','--site-dir','out/site']
        record={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=CLONE,text=True).strip(),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'input_lines':103,'command':command,'credentials':'stripped; values never recorded','runs':[]}
        for number in (1,2):
            began=time.perf_counter()
            with (OUT/f'run{number}.log').open('wb') as log:code=subprocess.call(command,cwd=CLONE,env=env,stdout=log,stderr=subprocess.STDOUT)
            elapsed=time.perf_counter()-began
            dest=CLONE/f'validation/run{number}';dest.mkdir(parents=True,exist_ok=False)
            for name in ('envelopes.jsonl','profiles.jsonl','report.json'):shutil.copyfile(CLONE/'out'/name,dest/name)
            report=json.loads((dest/'report.json').read_text(encoding='utf8'))
            result={'run':number,'exit_code':code,'wall_seconds':elapsed,**{k:report[k] for k in ('requests','changes','observation_changes','emitted_envelopes','deadline_hits','warnings')}}
            record['runs'].append(result);print(json.dumps(result),flush=True)
            (OUT/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
            if code:raise SystemExit(code)
        verify=['uv','run','--frozen','python','scripts/verify_output.py','--first','validation/run1/envelopes.jsonl','--second','validation/run2/envelopes.jsonl','--state-dir','out/state','--organisations','orgnrs.txt','--count','103','--report','validation/run1/report.json']
        with (OUT/'strict-verifier.txt').open('wb') as log:code=subprocess.call(verify,cwd=CLONE,env=env,stdout=log,stderr=subprocess.STDOUT)
        record['strict_verifier_exit_code']=code
        (OUT/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
        print('Strict verifier exit',code,flush=True)
        raise SystemExit(code)

if __name__=='__main__':main()
