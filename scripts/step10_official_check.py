"""Fresh local checkout, literal README command twice, strict pair verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


COMMAND = ['uv','run','--frozen','signalpost','run','--organisations','orgnrs.txt',
           '--output','out/envelopes.jsonl','--profiles-output','out/profiles.jsonl',
           '--report','out/report.json','--state-dir','out/state','--site-dir','out/site']


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--clone',type=Path,default=Path('bench/cache/s6-step10-official'))
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--input',type=Path,help='Explicit fresh cohort; default retains the historical official sample')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    target=(root/args.clone).resolve()
    assert target.is_relative_to(root/'bench/cache') and target!=root/'bench/cache'
    env={k:v for k,v in os.environ.items() if not (any(x in k.upper() for x in ('API_KEY','APIKEY','TOKEN','SECRET','CREDENTIAL')) or k.startswith('SIGNALPOST_'))}
    env['UV_CACHE_DIR']=str(root/'.uv-cache-task')
    if not target.exists():
        subprocess.run(['git','clone','--local','--no-hardlinks',str(root),str(target)],cwd=root,env=env,check=True)
    source=(root/args.input).resolve() if args.input else root/'bench/reports/s6-step8/official_orgnrs.txt'
    if not (target/'orgnrs.txt').exists():shutil.copyfile(source,target/'orgnrs.txt')
    records=target/'validation';records.mkdir(exist_ok=True)
    if args.prepare_only:return
    subprocess.run(['uv','sync','--frozen'],cwd=target,env=env,check=True)
    results={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=target,text=True).strip(),
             'command':COMMAND,'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'credentials':'Application credential/search environment removed; NAV public token may be fetched in memory', 'runs':[]}
    for n in (1,2):
        begin=time.monotonic()
        with (records/f'run{n}-stdout.log').open('w',encoding='utf8') as out,(records/f'run{n}-stderr.log').open('w',encoding='utf8') as err:
            completed=subprocess.run(COMMAND,cwd=target,env=env,stdout=out,stderr=err)
        elapsed=time.monotonic()-begin
        for filename in ('envelopes.jsonl','profiles.jsonl','report.json'):
            shutil.copyfile(target/'out'/filename,records/f'run{n}-{filename}')
        report=json.loads((target/'out/report.json').read_text(encoding='utf8'))
        results['runs'].append({'number':n,'exit_code':completed.returncode,'wall_seconds':elapsed,
                               'http_requests':report.get('requests',report.get('http_requests')),
                               'changes':report.get('changes'),'observation_changes':report.get('observation_changes')})
        (records/'execution.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')
        print(json.dumps(results['runs'][-1]),flush=True)
        if completed.returncode:raise SystemExit(completed.returncode)
    verify=['uv','run','--frozen','python','scripts/verify_output.py','--first','validation/run1-envelopes.jsonl',
            '--second','validation/run2-envelopes.jsonl','--state-dir','out/state','--count','103',
            '--organisations','orgnrs.txt','--report','validation/run2-report.json']
    with (records/'verification.txt').open('w',encoding='utf8') as out:
        checked=subprocess.run(verify,cwd=target,env=env,stdout=out,stderr=subprocess.STDOUT)
    results['verification_exit_code']=checked.returncode
    (records/'execution.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')
    print({'verification_exit_code':checked.returncode},flush=True)
    return checked.returncode


if __name__=='__main__':raise SystemExit(main())
