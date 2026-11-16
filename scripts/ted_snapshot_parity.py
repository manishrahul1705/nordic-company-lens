"""Stage U scope check: does the snapshot hold every notice the live path would nominate?

Runs the runtime's exact live TED search (identifier query, 100 orgnrs per batch) for
an input file, applies the same literal nomination, and compares the nominated
publication numbers with the snapshot build's search cache (or the bundled file).
Also counts how many snapshot notices carry a spaced form of an input orgnr, which
the unchanged literal nomination cannot match (measured, not changed).
"""
import argparse
import gzip
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from signalpost.sources.official_extra import TED, ted_nominated, ted_query_values  # noqa: E402


def orgnrs(path):
    out = []
    for line in Path(path).read_text(encoding='utf8').splitlines():
        line = line.strip()
        if not line:
            continue
        value = json.loads(line) if line[0] in '"{[0123456789' else line
        if isinstance(value, dict):
            value = value.get('organisation_number')
        out.append(re.sub(r'\D', '', str(value)))
    return sorted({o for o in out if len(o) == 9})


def live(nums, since):
    found, literal, calls, statuses = {}, {}, 0, {}
    with httpx.Client(timeout=60) as client:
        for start in range(0, len(nums), 100):
            batch = nums[start:start + 100]
            values = ted_query_values(batch)
            q = ('(winner-identifier = ' + values + ' OR buyer-identifier = ' + values +
                 ') AND notice-type = (can-standard OR can-social) AND publication-date >= ' + since.strftime('%Y%m%d'))
            for page in range(1, 11):
                for attempt in range(5):
                    calls += 1
                    r = client.post(TED, json={'query': q, 'fields': ['publication-number', 'notice-type', 'winner-identifier',
                                                                       'buyer-identifier', 'links'], 'limit': 100, 'page': page, 'scope': 'ALL'})
                    statuses[str(r.status_code)] = statuses.get(str(r.status_code), 0) + 1
                    time.sleep(1)
                    if r.status_code == 200:
                        break
                    time.sleep(5 * (attempt + 1))
                else:
                    raise SystemExit('live search failed')
                data = r.json()
                for item in data['notices']:
                    if item.get('notice-type') not in {'can-standard', 'can-social'}:
                        continue
                    ids = (item.get('winner-identifier') or []) + (item.get('buyer-identifier') or [])
                    scope = ted_nominated(batch, ids)
                    if scope:
                        found.setdefault(item['publication-number'], set()).update(scope)
                    if set(batch) & set(ids):
                        literal.setdefault(item['publication-number'], set()).update(set(batch) & set(ids))
                if page * 100 >= data['totalNoticeCount']:
                    break
    return found, literal, calls, statuses


def snapshot_items():
    bundled = ROOT / 'data' / 'ted-no-notices.jsonl.gz'
    if bundled.exists():
        with gzip.open(bundled, 'rt', encoding='utf8') as f:
            for line in f:
                r = json.loads(line)
                yield r['publication_number'], r['notice_type'], r['publication_date'], r['winner_identifier'] + r['buyer_identifier']
        return
    for f in sorted((ROOT / 'bench' / 'cache' / 'ted-snapshot' / 'search').glob('*.json')):
        for item in json.loads(f.read_text(encoding='utf8'))['notices']:
            yield (item['publication-number'], item.get('notice-type'), item.get('publication-date'),
                   (item.get('winner-identifier') or []) + (item.get('buyer-identifier') or []))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--organisations', default=str(ROOT / 'bench/inputs/1000-r3/batch.jsonl'))
    p.add_argument('--since', required=True, help='window start YYYY-MM-DD (run date minus 36 months)')
    p.add_argument('--out', required=True)
    a = p.parse_args()
    nums = orgnrs(a.organisations)
    since = date.fromisoformat(a.since)
    live_found, live_literal, calls, statuses = live(nums, since)
    wanted = set(nums)
    snap_literal, snap_spaced = {}, {}
    for notice, kind, published, ids in snapshot_items():
        if kind not in {'can-standard', 'can-social'} or str(published)[:10] < since.isoformat():
            continue
        literal = wanted & set(ids)
        normalised = ted_nominated(wanted, ids)
        if normalised:
            snap_literal.setdefault(notice, set()).update(normalised)
        if normalised - literal:
            snap_spaced.setdefault(notice, set()).update(normalised - literal)
    missing = sorted(set(live_found) - set(snap_literal))
    extra = sorted(set(snap_literal) - set(live_found))
    result = {'inputs': len(nums), 'since': since.isoformat(), 'live_search_requests': calls, 'live_http_statuses': statuses,
              'rule': 'whitespace-only normalised exact nine-digit nomination (ted_nominated); query sends plain and 3-3-3 spellings',
              'live_nominated_notices': len(live_found), 'snapshot_nominated_notices': len(snap_literal),
              'live_literal_rule_notices': len(live_literal),
              'live_literal_rule_companies': len({o for s in live_literal.values() for o in s}),
              'live_normalised_rule_companies': len({o for s in live_found.values() for o in s}),
              'live_not_in_snapshot': missing, 'snapshot_not_in_live': extra,
              'scope_mismatch_orgnrs': sorted({o for n in missing for o in live_found[n]} | {o for n in extra for o in snap_literal[n]}),
              'snapshot_gain_from_normalisation': {'notices': len(snap_spaced),
                                         'companies': len({o for s in snap_spaced.values() for o in s}),
                                         'publication_numbers': sorted(snap_spaced)}}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, indent=1) + '\n', encoding='utf8')
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
