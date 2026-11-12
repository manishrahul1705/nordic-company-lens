"""Final-precision fresh-clone README pair and unchanged strict verifier."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLONE=ROOT/'bench/cache/final-precision-clone'
OUT=ROOT/'bench/reports/final-precision'
def main():
    global OUT, CLONE
    parser=argparse.ArgumentParser();parser.add_argument("--final",action="store_true");args=parser.parse_args()
    if args.final:
        CLONE=ROOT/"bench/cache/final-precision-final-clone"
        OUT=ROOT/"bench/reports/final-precision/final-code"
    OUT.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ)
    for key in list(env):
        if any(x in key.upper() for x in ('API_KEY','APIKEY','TOKEN','SECRET','CREDENTIAL')) or key.startswith(('SIGNALPOST_SEARCH','SIGNALPOST_LLM')):env.pop(key)
    env['PYTHONUTF8']='1'
    source=ROOT/'bench/reports/final-precision/orgnrs.txt'
    shutil.copyfile(source,CLONE/'orgnrs.txt')
    command=['uv','run','--frozen','signalpost','run','--organisations','orgnrs.txt','--output','out/envelopes.jsonl','--profiles-output','out/profiles.jsonl','--report','out/report.json','--state-dir','out/state','--site-dir','out/site']
    record={'clone_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=CLONE,text=True).strip(),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'command':command,'credentials':'Removed; values never recorded','runs':[]}
    for n in (1,2):
        began=time.perf_counter()
        with (OUT/f'release-run{n}.log').open('wb') as log:code=subprocess.call(command,cwd=CLONE,env=env,stdout=log,stderr=subprocess.STDOUT)
        dest=CLONE/f'validation/run{n}';dest.mkdir(parents=True,exist_ok=False)
        for name in ('envelopes.jsonl','profiles.jsonl','report.json'):shutil.copyfile(CLONE/'out'/name,dest/name)
        metrics=json.loads((dest/'report.json').read_text(encoding='utf8'))
        item={'number':n,'exit_code':code,'wall_seconds':time.perf_counter()-began,**{k:metrics.get(k) for k in ('requests','changes','observation_changes','deadline_hits','warnings','emitted_envelopes')}}
        record['runs'].append(item);print(json.dumps(item),flush=True)
        (OUT/'release-execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        if code:raise SystemExit(code)
        # Evidence checks are strict; the refresh pair additionally checks stable IDs,
        # zero company changes and zero observation changes without editing outputs.
        verifier=['uv','run','--frozen','python','scripts/verify_output.py','--first',str(CLONE/'validation/run1/envelopes.jsonl'),'--state-dir','out/state','--organisations','orgnrs.txt','--count','103','--report',str(CLONE/'validation/run1/report.json')]
        if n==2:verifier+=['--second',str(dest/'envelopes.jsonl')]
        with (OUT/f'release-run{n}-verification.txt').open('wb') as log:verified=subprocess.call(verifier,cwd=CLONE,env=env,stdout=log,stderr=subprocess.STDOUT)
        record['runs'][-1]['strict_verifier_exit_code']=verified
        (OUT/'release-execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
    print(json.dumps(record,indent=2),flush=True)
if __name__=='__main__':main()
