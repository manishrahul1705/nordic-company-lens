"""Count benchmark coverage without changing the agent or its output.

Fact/state rules match compare/analyze.py used for the November 2026 comparison.
Canonical source states and exported profile states remain separate. Budget and
deadline error conditions may overlap canonical states; they are never substituted.
"""
import argparse
from collections import Counter
import json
from pathlib import Path


SECTIONS = {
    'identity': ('identity', 'registry_live'),
    'people': ('roles', 'roles'),
    'locations': ('subunits', 'locations'),
    'financials': ('accounts', 'financials'),
    'website': ('website', 'website'),
    'social': ('social', None),
    'jobs': ('hiring', 'hiring'),
    'news/activity': ('activity', 'activity'),
}
STATES = ('available', 'not_available', 'not_applicable', 'failed', 'ambiguous',
          'blocked', 'budget_exhausted', 'deadline')


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines()
            if line.strip()]


def meaningful(claim):
    return claim.get('availability') == 'available' and claim.get('value') is not None


def matches(claim, family):
    field = claim.get('field', '')
    if family == 'social':
        return field.startswith('social_profile.') or (
            field.startswith('registry_social.') and isinstance(claim.get('value'), dict))
    if family == 'website':
        return claim.get('family') == 'website' and not field.startswith(
            ('social_profile.', 'registry_social.'))
    return claim.get('family') == family


def build_scoreboard(rows, report, profiles, execution=None):
    organisations = [row['organisation_number'] for row in rows]
    if [row['organisation_number'] for row in profiles] != organisations:
        raise ValueError('Profile membership/order differs from envelope membership/order')
    if report['emitted_envelopes'] != len(rows):
        raise ValueError('Report envelope count differs from actual output')
    profile_by = {row['organisation_number']: row for row in profiles}
    execution = execution or {}
    wall = execution.get('wall_seconds')
    result = {
        'schema_version': 1,
        'commit': execution.get('commit'),
        'run_id': report.get('run_id'),
        'exit_code': execution.get('exit_code'),
        'wall_seconds': wall if wall is not None else report['runtime_ms'] / 1000,
        'wall_seconds_source': 'execution' if wall is not None else 'report_runtime_ms',
        'http_requests': report['requests'],
        'envelopes': len(rows),
        'profiles': len(profiles),
        'deadline_hits': report['deadline_hits'],
        'warnings': report['warnings'],
        'website_budget_exhausted_count': sum(
            any(e.get('section') == 'website' and e.get('code') == 'website_budget_exhausted'
                for e in row.get('errors', [])) for row in rows),
        'latest_year_accounts_count': 0,
        'registry_latest_year_matched_count': 0,
        'sections': {},
    }
    for name, (family, profile_key) in SECTIONS.items():
        states, exported, conditions = Counter(), Counter(), Counter()
        facts = set()
        for row in rows:
            selected = [c for c in row['claims'] if meaningful(c) and matches(c, family)]
            state = row['run']['sections'].get(family, 'not_applicable')
            if family == 'social':
                web = row['run']['sections'].get('website', 'not_applicable')
                state = 'available' if selected else 'not_available' if web == 'available' else web
            states[state] += 1
            if profile_key:
                exported[profile_by[row['organisation_number']]['evidence'][profile_key]['status']] += 1
            else:
                exported['available' if selected else 'not_found' if state == 'not_available'
                         else {'failed': 'source_error', 'ambiguous': 'source_error'}.get(state, state)] += 1
            for claim in selected:
                facts.add((row['organisation_number'], claim['field'],
                           json.dumps(claim['value'], sort_keys=True, ensure_ascii=True),
                           json.dumps(claim.get('reporting_period'), sort_keys=True)))
            error_family = 'website' if family == 'social' else family
            for flag in ('budget_exhausted', 'deadline'):
                if any(e.get('section') == error_family and flag in e.get('code', '')
                       for e in row.get('errors', [])):
                    conditions[flag] += 1
        result['sections'][name] = {
            'states': {key: states[key] for key in dict.fromkeys((*STATES, *states))},
            'profile_states': {key: exported[key] for key in dict.fromkeys((
                'available', 'not_found', 'source_error', 'not_applicable', 'blocked',
                'failed', 'ambiguous', 'budget_exhausted', 'deadline', *exported))},
            'distinct_facts': len(facts),
            'error_conditions': {key: conditions[key] for key in ('budget_exhausted', 'deadline')},
        }
    for row in rows:
        accounts = [c for c in row['claims'] if meaningful(c) and c.get('family') == 'accounts'
                    and (c.get('reporting_period') or {}).get('fiscal_year')
                    and not c.get('field', '').startswith('accounts.history.')]
        if accounts:
            result['latest_year_accounts_count'] += 1
            years = {str(c['reporting_period']['fiscal_year']) for c in accounts}
            declared = next((str(c['value']) for c in row['claims']
                             if c['field'] == 'identity.latest_submitted_accounts' and meaningful(c)), None)
            result['registry_latest_year_matched_count'] += declared in years
    return result


def summary(score):
    parts = []
    for name, section in score['sections'].items():
        counts = ','.join(f'{key}={value}' for key, value in section['states'].items())
        parts.append(f"{name}({counts},facts={section['distinct_facts']})")
    return ' | '.join(parts + [
        f"latest_accounts={score['latest_year_accounts_count']}",
        f"wall_seconds={score['wall_seconds']:.3f}", f"http={score['http_requests']}",
        f"envelopes={score['envelopes']}", f"deadlines={score['deadline_hits']}",
        f"website_budget_exhausted={score['website_budget_exhausted_count']}",
        'warnings=' + json.dumps(score['warnings'], ensure_ascii=True),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--envelopes', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--profiles', type=Path, required=True)
    parser.add_argument('--execution', type=Path, help='Measured wall time and commit; defaults to report sibling execution.json')
    parser.add_argument('--output', type=Path, default=Path('scoreboard.json'))
    args = parser.parse_args()
    execution_path = args.execution or args.report.with_name('execution.json')
    execution = json.loads(execution_path.read_text(encoding='utf-8-sig')) if execution_path.exists() else None
    score = build_scoreboard(read_jsonl(args.envelopes),
                             json.loads(args.report.read_text(encoding='utf-8-sig')),
                             read_jsonl(args.profiles), execution)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(score, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(summary(score))


if __name__ == '__main__':
    main()
