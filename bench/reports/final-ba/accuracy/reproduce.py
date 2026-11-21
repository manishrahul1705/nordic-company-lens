"""Redraw the Stage X sample and recheck it from the committed extract alone (no bench/runs).

Usage: uv run python bench/reports/stage-x-accuracy/reproduce.py [--write]

Without --write (the verification mode) it redraws the 200-item sample with the recorded seed,
reruns the mechanical checks against the committed source blobs, and exits non-zero unless the
result equals the committed sample.jsonl and the verdict tallies equal summary.json.
--write regenerates sample.jsonl and population.json (used once, before hand review);
--summary records summary.json from verdicts.jsonl (used once, after hand review).
"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C


def tallies(items, verdicts):
    if len(verdicts) != len(items):
        raise SystemExit(f'{len(verdicts)} verdicts for {len(items)} sampled items')
    fam = collections.defaultdict(collections.Counter)
    for i, (it, v) in enumerate(zip(items, verdicts)):
        if (v['index'], v['orgnr'], v['field']) != (i, it['orgnr'], it['field']):
            raise SystemExit(f'verdict {i} does not match sampled item {it["orgnr"]} {it["field"]}')
        if v['verdict'] not in ('correct', 'wrong', 'doubtful'):
            raise SystemExit(f'verdict {i}: unknown verdict {v["verdict"]!r}')
        fam[it['family']][v['verdict']] += 1; fam[it['family']]['basis:' + v['basis']] += 1
    tot = collections.Counter()
    for c in fam.values():
        tot.update(c)
    n = len(items); k = tot['correct']
    return {'sampled': n, 'correct': k, 'wrong': tot['wrong'], 'doubtful': tot['doubtful'],
            'mechanical': tot['basis:mechanical'], 'hand': tot['basis:hand'],
            'wilson_95_lower_bound': round(C.wilson_lower(k, n), 4),
            'by_family': {f: dict(sorted(c.items())) for f, c in sorted(fam.items())}}


def main():
    write = '--write' in sys.argv
    rows = list(C.read_envelopes()); blobs = C.read_blobs()
    pop = C.population(rows); alloc = C.allocate(pop)
    items = C.build_items(C.draw(pop, alloc), {r['organisation_number']: r for r in rows}, blobs)
    popdoc = {'seed': C.SEED, 'size': C.SIZE, 'extract': 'extract/envelopes.jsonl.xz',
              'population': {f: len(pop[f]) for f in sorted(pop)}, 'allocation': alloc}
    lines = [json.dumps(it, ensure_ascii=False, default=str, sort_keys=True) for it in items]
    sample_p = C.HERE / 'sample.jsonl'; pop_p = C.HERE / 'population.json'
    if write:
        sample_p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        pop_p.write_text(json.dumps(popdoc, indent=1) + '\n', encoding='utf-8')
        print(json.dumps(popdoc, indent=1)); return
    fails = []
    if sample_p.read_text(encoding='utf-8').splitlines() != lines:
        fails.append('redrawn sample differs from committed sample.jsonl')
    if json.loads(pop_p.read_text(encoding='utf-8')) != popdoc:
        fails.append('population/allocation differs from committed population.json')
    verdicts = [json.loads(l) for l in open(C.HERE / 'verdicts.jsonl', encoding='utf-8') if l.strip()]
    got = tallies(items, verdicts)
    if '--summary' in sys.argv:  # used once, after hand review, to record the tallies
        (C.HERE / 'summary.json').write_text(json.dumps(got, indent=1) + '\n', encoding='utf-8')
    # Every verdict marked mechanical must still pass its mechanical check on the committed bytes.
    for it, v in zip(items, verdicts):
        if v['basis'] == 'mechanical':
            ch = it.get('check') or {}
            if not (ch.get('span_in_body') and ch.get('org_in_source_url') and ch.get('value_at_locator') == it['value']):
                fails.append(f'mechanical verdict {v["index"]} no longer passes its check')
    want = json.loads((C.HERE / 'summary.json').read_text(encoding='utf-8'))
    if got != want:
        fails.append(f'tallies differ from summary.json: {json.dumps(got)}')
    print(json.dumps({k: got[k] for k in got if k != 'by_family'}))
    if fails:
        print('FAIL\n' + '\n'.join(fails)); sys.exit(1)
    print('OK: sample, population, mechanical checks and verdict tallies reproduced from committed data')


if __name__ == '__main__':
    main()
