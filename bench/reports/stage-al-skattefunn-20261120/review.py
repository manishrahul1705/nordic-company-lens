"""Retain ten source-cell checks, including the cohort's #N/A decision date."""
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.build_skattefunn_snapshot import read_rows, COLUMNS


def main():
    raw = Path('bench/cache/skattefunn-20261120/source.xlsx')
    candidates = json.loads(Path('bench/runs/stage-al-skattefunn1000/review-candidates.json').read_text(encoding='utf-8'))
    selected = [x for x in candidates if x['claim']['value']['decision_date'] is None][:1]
    seen = {x['orgnr'] for x in selected}
    for x in candidates:
        if x['orgnr'] not in seen:
            selected.append(x); seen.add(x['orgnr'])
        if len(selected) == 10:
            break
    numbered = {int(re.search(r' row (\d+);', x['evidence']['source_identifier']).group(1)): x for x in selected}
    verified = set()
    for n, row in read_rows(raw):
        if n not in numbered:
            continue
        x = numbered[n]; c = x['claim']; v = c['value']; e = x['evidence']
        assert {k: row[k] for k in COLUMNS} == x['source_cells']
        assert row['Organisasjonsnummer'] == x['orgnr'] == v['organisation_number']
        assert row['Prosjektnummer'] == v['project_id'] and row['Prosjekttittel'] == v['title']
        assert row['Søknad godkjent'] == 'JA' and row['Søknad avslått'] == 'NEI'
        body = json.dumps(x['source_cells'], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        assert hashlib.sha256(body).hexdigest() == e['content_sha256'] and e['claim_span'] in body.decode()
        x['source_row'] = n
        x['why_correct'] = ('Exact applicant organisation number; explicit approved JA and rejected NEI; title and project period copied from that row. '
            + ('Decision is #N/A, correctly published as null without substituting the application date. ' if row['Vedtaksdato'] == '#N/A'
               else 'Decision date is the explicit Excel decision-date cell converted to a calendar date. ')
            + 'Historical R&D tax deduction approval only; no monetary award or claimed deduction is asserted.')
        verified.add(n)
    assert len(verified) == 10
    Path(__file__).with_name('hand-review-10.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps([{'company': x['company'], 'orgnr': x['orgnr'], 'project': x['claim']['value']['project_id'],
        'title': x['claim']['value']['title'], 'period': [x['claim']['value']['start_year'], x['claim']['value']['end_year']],
        'decision': x['claim']['value']['decision_date'], 'raw_decision': x['source_cells']['Vedtaksdato'], 'row': x['source_row']} for x in selected], ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
