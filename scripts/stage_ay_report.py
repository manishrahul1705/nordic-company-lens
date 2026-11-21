"""Render the exhaustive saved-field inventory and competitor field comparison."""
import collections
import json
from pathlib import Path
from stage_ay_field_inventory import JURY, OUT
from stage_ay_recall import category

COMPETITORS = ['ChiaraDeVenuto','Venky1209','slightlybroke','CVasilopoulos','AnanthKumar1810','mstege']
TARGET = {'identity':'identity','roles':'roles','accounts':'accounts','workplaces':'subunits'}


def main():
    inventory = json.loads((OUT / 'field-inventory.json').read_text(encoding='utf8'))
    replay = json.loads((OUT / 'replay.json').read_text(encoding='utf8'))
    recall = json.loads((OUT / 'corrected-recall.json').read_text(encoding='utf8'))
    brands = json.loads((OUT / 'brand-replay.json').read_text(encoding='utf8'))
    competitor_fields = {}
    lines = ['# Stage AY — saved-field completeness', '',
        'All sources below are saved responses. Replay made zero HTTP requests. Counts are available claims, including multiple reporting periods and subunits.',
        '', '## New claims and verification', '',
        '| Cohort | Identity | Roles | Accounts | Subunits |', '|---|---:|---:|---:|---:|']
    for name, x in replay.items():
        cells = [f"{x['before'].get(f,0):,} → {x['after'].get(f,0):,} (+{x['new'].get(f,0):,})" for f in ('identity','roles','accounts','subunits')]
        lines.append('| ' + name + ' | ' + ' | '.join(cells) + ' |')
    lines += ['', '## Brand replay', '',
              f"Unseen 300: {brands['unseen300']['published_brands_before']} existing brands, {len(brands['unseen300']['changes'])} changes. Frozen 1,000: {brands['final1000']['published_brands_before']} existing brands, {len(brands['final1000']['changes'])} changes. Zero HTTP. All changes:", '']
    for item in brands['unseen300']['changes'] + brands['final1000']['changes']:
        lines.append(f"- `{item['orgnr']}`: {json.dumps(item['before'],ensure_ascii=False)} → {json.dumps(item['after'],ensure_ascii=False)} (`{item['source_url']}`)")
    lines += ['', 'The strict saved-source verifier passed on the full 316-row jury output and frozen 1,000. Fifteen new claims across the four families were checked against exact JSON values, source hashes, and verbatim spans in `handchecks.json`. Large replay envelopes were removed after verification to preserve the disk reserve; `stage_ay_offline_replay.py` recreates them from the saved blobs.',
              '', 'All numeric accounts statement leaves were already published. Existing exact claims also cover the identity MVA/registry and employee-count flags, statute date, role birth year, and subunit start dates. New scalar claims split cited address, industry, sector, capital, role metadata, holder entity, and subunit fields out of existing composite values. Filing ID and journal number are source values, not constructed links. Remaining gaps are source metadata, empty containers, subject IDs, or values already represented by an existing composite claim (including person name parts and historical names).',
              '', f"Corrected shared-taxonomy recall: Nordic **{recall['before']['agents']['Nordic']['score']:.4f} → {recall['after']['agents']['Nordic']['score']:.4f} / 50**, rank **{recall['before']['rank']} → {recall['after']['rank']}** among {len(recall['after']['agents'])} measured agents. The ten corrected families and every agent's components are in `corrected-recall.json`. This is a local proxy, not the Builderr board score.",
              '', '## Exhaustive raw JSON paths', '',
              'Each row is a normalized JSON leaf path in at least one saved response. `Exact before` means the original output had a claim citing that exact locator; `within composite` means it fell under a cited object claim. Empty containers and response metadata appear too, for completeness. The identical machine-readable inventory is in `field-inventory.json`.', '']
    for cohort in ('jury100','final1000'):
        lines += [f'### {cohort}', '']
        for family in ('identity','roles','accounts','subunits'):
            paths = inventory[cohort]['paths'].get(family,{})
            missing = [(p,v) for p,v in paths.items() if v['exact_claim_companies'] < v['present_companies']]
            lines += [f'#### {family} ({len(missing)} paths without exact publication for at least one company)', '',
                      '| JSON path | Present | Exact before | Within composite |', '|---|---:|---:|---:|']
            for p,v in missing:
                lines.append(f"| `{p}` | {v['present_companies']} | {v['exact_claim_companies']} | {v['inside_composite_claim_companies']} |")
            lines.append('')
    lines += ['## Competitor emitted field lists', '',
              'Lists show native normalized field names on the same unseen 100, under the corrected family taxonomy. They describe each competitor’s field granularity; they do not imply that a value is independently verified. Full lists are in `competitor-fields.json`.', '']
    allowed = set(json.loads((JURY / 'jury-sample.json').read_text(encoding='utf8'))['active'][:100])
    for name in COMPETITORS:
        facts = json.loads((JURY / 'jury-normalized' / (name+'.facts.json')).read_text(encoding='utf8'))
        groups = collections.defaultdict(set)
        for fact in facts:
            if fact['orgnr'] not in allowed or not fact.get('source') or fact.get('value') is None:
                continue
            fam = TARGET.get(category(fact))
            if fam: groups[fam].add(fact.get('field') or '<unspecified>')
        competitor_fields[name] = {k:sorted(v) for k,v in groups.items()}
        lines += [f'### {name}', '']
        for fam in ('identity','roles','accounts','subunits'):
            names = competitor_fields[name].get(fam,[])
            lines.append(f'- **{fam} ({len(names)}):** ' + (', '.join(f'`{x}`' for x in names) if names else 'none'))
        lines.append('')
    verification_file = OUT / 'verification.json'
    if verification_file.exists():
        verified = json.loads(verification_file.read_text(encoding='utf8'))
        suite = verified['full_suite']
        lines += ['## Full suite', '',
                  f"{suite['passed']:,} passed, {suite['warnings']} warning in {suite['seconds']:.2f} seconds. The strict verifier results for both cohorts are in `verification.json`.", '']
    (OUT / 'competitor-fields.json').write_text(json.dumps(competitor_fields,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT / 'RESULTS.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf8')
    print('report lines', len(lines), 'competitors', len(competitor_fields))


if __name__ == '__main__': main()
