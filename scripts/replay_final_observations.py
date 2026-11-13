"""Replay only final observation bookkeeping on an untouched saved live pair."""
import copy
import hashlib
import json
from pathlib import Path

from signalpost.models.envelope import Envelope
from signalpost.refresh.diff import reconcile_final_observations
from verify_output import verify

ROOT = Path(__file__).resolve().parents[1]
CLONE = ROOT / 'bench/cache/final-precision-final-clone-v2'
OUT = ROOT / 'bench/reports/refresh-bookkeeping'
REPLAY = ROOT / 'bench/cache/refresh-bookkeeping-replay'


def main():
    OUT.mkdir(exist_ok=True)
    REPLAY.mkdir(exist_ok=True)
    first = CLONE / 'validation/run1/envelopes.jsonl'
    second = CLONE / 'validation/run2/envelopes.jsonl'
    originals = {p: p.read_bytes() for p in (first, second)}
    old = {r['organisation_number']: r for r in map(json.loads, first.read_text(encoding='utf8').splitlines())}
    output = []
    removed = []
    for line in second.read_text(encoding='utf8').splitlines():
        raw = json.loads(line)
        row = Envelope.model_validate(raw)
        reconcile_final_observations(row, old[row.organisation_number])
        observations = row.run.refresh['observation_changes']
        if observations != raw['run']['refresh']['observation_changes']:
            removed.append({'orgnr': row.organisation_number,
                            'before': raw['run']['refresh']['observation_changes'], 'after': observations})
        replayed = copy.deepcopy(raw)
        replayed['run']['refresh']['observation_changes'] = observations
        # No claims, section states, proof diagnostics, briefings or evidence may change.
        checked = copy.deepcopy(replayed)
        checked['run']['refresh']['observation_changes'] = raw['run']['refresh']['observation_changes']
        assert checked == raw
        output.append(replayed)
    path = REPLAY / 'envelopes.jsonl'
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in output), encoding='utf8')
    result = verify(first, CLONE / 'out/state', 103, CLONE / 'orgnrs.txt',
                    CLONE / 'validation/run1/report.json', False, path, None)
    # Independently validate all second-run evidence, not only its refresh IDs.
    second_result = verify(path, CLONE / 'out/state', 103, CLONE / 'orgnrs.txt',
                           CLONE / 'validation/run2/report.json', False, None, None)
    assert all(p.read_bytes() == data for p, data in originals.items())
    result = {'method': 'Offline replay of final bookkeeping only; original saved pair is unchanged.',
              'original_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(data).hexdigest()
                                  for p, data in originals.items()},
              'removed_observations': removed, 'strict_pair': result, 'second_run_evidence': second_result}
    (OUT / 'offline-verifier.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
