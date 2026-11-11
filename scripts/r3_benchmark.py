"""Run the same README command in isolated revisions, one at a time."""
import argparse, hashlib, json, os, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    repo=args.repo.resolve();source=args.input.resolve();out=args.output.resolve()
    free=shutil.disk_usage(repo).free
    if free<10*1024**3:raise RuntimeError('At least 10 GiB free required')
    out.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ)
    for key in list(env):
        if any(x in key.upper() for x in ('API_KEY','APIKEY','TOKEN','SECRET','CREDENTIAL')) or key.startswith(('SIGNALPOST_SEARCH','SIGNALPOST_LLM')):
            env.pop(key)
    env['PYTHONUTF8']='1'
    command=['uv','run','--frozen','signalpost','run','--organisations',str(source),
             '--output',str(out/'envelopes.jsonl'),'--profiles-output',str(out/'profiles.jsonl'),
             '--report',str(out/'report.json'),'--state-dir',str(out/'state'),'--site-dir',str(out/'site')]
    metadata={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
              'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'command':command,
              'started_utc':datetime.now(timezone.utc).isoformat(),'free_bytes_before':free,
              'credentials':'Key/token/secret variables and optional provider selectors removed; values not recorded',
              'fresh_state':True,'mode':'README command; no bulk; default budgets'}
    (out/'execution.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')
    began=time.perf_counter();last=0
    with (out/'process.log').open('wb') as log:
        child=subprocess.Popen(command,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT)
        while child.poll() is None:
            if time.perf_counter()-last>=30:
                last=time.perf_counter()
                progress=out/'state/progress.json'
                info={}
                if progress.exists():
                    try:
                        state=json.loads(progress.read_text(encoding='utf8'))
                        info={k:state[k] for k in ('completed','completed_companies','input_rows','current_stage') if k in state}
                    except (OSError,ValueError):pass
                print(json.dumps({'elapsed_seconds':round(time.perf_counter()-began,1),'progress':info}),flush=True)
            time.sleep(1)
    metadata.update(exit_code=child.returncode,wall_seconds=time.perf_counter()-began,finished_utc=datetime.now(timezone.utc).isoformat())
    (out/'execution.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')
    print(json.dumps(metadata,indent=2),flush=True)
    raise SystemExit(child.returncode)


if __name__=='__main__':main()
