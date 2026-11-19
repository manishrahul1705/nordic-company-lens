"""Publish case-specific review notes only when final values match those read."""
import json
from pathlib import Path
from review_notes import NOTES

out = Path(__file__).parent
initial = json.loads((out/'initial-measurement/review-candidates.json').read_text(encoding='utf-8'))
final = json.loads((out/'review-candidates.json').read_text(encoding='utf-8'))
reviewed = {}
lines = ['# Stage AF: thirty evidence reviews', '',
         'Ten distinct companies per type. Group selection covers five explicit parents and five registered subsidiaries. '
         'The signature/procuration selection includes person-role bases, role-only wording, alternatives, and joint/conditional grants. '
         'These are deliberate source reviews, not a random precision estimate.', '',
         'Each value was read against its cited registry evidence. Final-run values must match the inspected initial-run values before these notes can be published. '
         'The independent full-output audit additionally checks the requested company identity, stored-body SHA-256, JSON pointer, and every published value; '
         'mandate values retain the whole registered basis except personal birth dates/identifiers. '
         'No grant is taken from possible signers or interpreted/statutory combinations.', '']

def cell(text):
    return str(text).replace('|', '&#124;').replace('\n', '<br>')

for kind in ('group_structure', 'signatur', 'prokura'):
    before = {(r['organisation_number'],r['field']):r for r in initial[kind]}
    assert len(final[kind]) == 10
    assert {r['organisation_number'] for r in final[kind]} == set(NOTES[kind])
    reviewed[kind] = []
    lines += ['## ' + kind, '', '| Company | Published value | Cited evidence | Why correct |', '|---|---|---|---|']
    for row in final[kind]:
        key = row['organisation_number'],row['field']
        assert row['value'] == before[key]['value'], 'Changed value needs a new hand review: ' + str(key)
        note = NOTES[kind][key[0]]
        row = {**row, 'verdict':'correct', 'why_correct':note, 'final_value_matches_inspected_value':True}
        reviewed[kind].append(row)
        e = row['evidence']
        citation = f"[Own registry lookup]({e['source_url']})<br>`{e['locator']}`<br>SHA-256 `{e['content_sha256']}`"
        value = '`' + json.dumps(row['value'], ensure_ascii=False) + '`'
        lines.append('| ' + ' | '.join(map(cell, [f"{row['company']} ({key[0]})", value, citation, note])) + ' |')
    lines.append('')
(out/'REVIEW.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')
(out/'reviewed.json').write_text(json.dumps(reviewed,indent=2,ensure_ascii=False),encoding='utf-8')
print('30 reviewed claims: 10 distinct companies per type; all final values match inspected values')
