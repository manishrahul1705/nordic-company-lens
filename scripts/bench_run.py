"""Shared implementation for bench.ps1 and bench.sh; never changes runtime defaults."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

if __package__:
    from .scoreboard import build_scoreboard, read_jsonl, summary
else:
    from scoreboard import build_scoreboard, read_jsonl, summary


def verify_inputs(directory, manifest):
    entries = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            digest, name = line.split(None, 1)
            entries[name.strip()] = digest
    hashes = {}
    for filename in ('batch.jsonl', 'registry.csv'):
        path = directory / filename
        relative = path.relative_to(manifest.parent).as_posix()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if entries.get(relative) != actual:
            raise ValueError(f'Frozen input hash mismatch: {relative}')
        hashes[filename] = actual
    return hashes


def benchmark_environment(environment=None):
    env = dict(os.environ if environment is None else environment)
    for key in list(env):
        if (any(marker in key.upper() for marker in ('API_KEY', 'APIKEY', 'TOKEN', 'SECRET', 'CREDENTIAL'))
                or key.startswith('SIGNALPOST_LLM')):
            env.pop(key)
    return env



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', choices=(20, 100, 1000), type=int, default=100)
    parser.add_argument('--website-suffix-contact-proof',action=argparse.BooleanOptionalAction,default=True)
    parser.add_argument('--website-domain-location-proof',action='store_true')
    parser.add_argument('--website-transient-retry',action=argparse.BooleanOptionalAction,default=True)
    parser.add_argument('--website-request-cap',type=int,default=40)
    parser.add_argument('--nav-index-path',type=Path,help='Explicit fixture override for stale/malformed index benchmarks')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        env = benchmark_environment()
    except ValueError as exc:
        parser.error(str(exc))
    if args.size == 1000:
        if __package__:
            from .prepare_bench_inputs import prepare
        else:
            from prepare_bench_inputs import prepare
        inputs, manifest = prepare(root)
    else:
        inputs, manifest = root / f'bench/inputs/{args.size}', root / 'bench/inputs/MANIFEST.txt'
    hashes = verify_inputs(inputs, manifest)
    batch = read_jsonl(inputs / 'batch.jsonl')
    if len(batch) != args.size or len({row['organisation_number'] for row in batch}) != args.size:
        raise ValueError('Benchmark requires exactly the selected number of distinct input companies')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'],
                                        cwd=root, text=True).strip())
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination = root / 'bench/runs' / f'{stamp}-{commit[:7]}'
    destination.mkdir(parents=True, exist_ok=False)
    # Pin the exact input bytes with the run, including the optional cache cohort.
    run_inputs = destination / 'inputs'
    run_inputs.mkdir()
    for filename in hashes:
        shutil.copyfile(inputs / filename, run_inputs / filename)
    shutil.copyfile(manifest, run_inputs / 'MANIFEST.txt')
    if (inputs / 'source.json').exists():
        shutil.copyfile(inputs / 'source.json', run_inputs / 'source.json')
    state = destination / 'state'
    assert not state.exists()
    command = ['signalpost', 'run', '--organisations', str(run_inputs / 'batch.jsonl'),
               '--bulk', str(run_inputs / 'registry.csv'), '--output', str(destination / 'envelopes.jsonl'),
               '--profiles-output', str(destination / 'profiles.jsonl'),
               '--report', str(destination / 'report.json'), '--site-dir', str(destination / 'site'),
               '--state-dir', str(state), '--websites', '--hiring', '--public-activity',
               '--run-id', 'bench-' + stamp, '--expected-count', str(args.size)]
    command.append('--website-suffix-contact-proof' if args.website_suffix_contact_proof else '--no-website-suffix-contact-proof')
    if args.website_domain_location_proof: command.append('--website-domain-location-proof')
    command.append('--website-transient-retry' if args.website_transient_retry else '--no-website-transient-retry')
    command.extend(['--website-request-cap',str(args.website_request_cap)])
    if args.nav_index_path:
        command.extend(['--nav-index-path',str(args.nav_index_path.resolve())])
    execution = {'commit': commit, 'working_tree_dirty': dirty, 'size': args.size,
                 'started_at': datetime.now(timezone.utc).isoformat(), 'command': command,
                 'input_sha256': hashes,
                 'website_suffix_contact_proof':args.website_suffix_contact_proof,
                 'website_domain_location_proof':args.website_domain_location_proof,
                 'website_transient_retry':args.website_transient_retry,
                 'website_request_cap':args.website_request_cap,
                 'credentials': 'API key, token, secret and model-selector variables removed'}
    execution_path = destination / 'execution.json'
    if args.nav_index_path:
        execution['nav_index_override_sha256']=hashlib.sha256(args.nav_index_path.read_bytes()).hexdigest()
    execution_path.write_text(json.dumps(execution, indent=2) + '\n', encoding='utf-8')
    print('Benchmark output: ' + str(destination), flush=True)
    began = time.perf_counter()
    with (destination / 'stdout.log').open('w', encoding='utf-8') as stdout, (
            destination / 'stderr.log').open('w', encoding='utf-8') as stderr:
        process = subprocess.run(command, cwd=root, env=env, stdout=stdout, stderr=stderr)
    execution.update(exit_code=process.returncode, wall_seconds=time.perf_counter() - began,
                     finished_at=datetime.now(timezone.utc).isoformat())
    execution_path.write_text(json.dumps(execution, indent=2) + '\n', encoding='utf-8')
    required = [destination / name for name in ('envelopes.jsonl', 'report.json', 'profiles.jsonl')]
    if all(path.exists() for path in required):
        score = build_scoreboard(read_jsonl(required[0]),
                                 json.loads(required[1].read_text(encoding='utf-8')),
                                 read_jsonl(required[2]), execution)
        (destination / 'scoreboard.json').write_text(json.dumps(score, indent=2) + '\n', encoding='utf-8')
        line = summary(score)
        (destination / 'summary.txt').write_text(line + '\n', encoding='utf-8')
        print(line, flush=True)
        if score['envelopes'] != args.size:
            return 1
    else:
        print('Benchmark did not create every required output; inspect stdout.log and stderr.log', file=sys.stderr)
        return process.returncode or 1
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())
