"""Summarise the saved release smoke test; never fetch sources."""
import json,shutil
from collections import Counter
from pathlib import Path
from verify_output import section_summary

def main():
 root=Path(__file__).resolve().parents[1];clone=root/'bench/cache/s6-release-official';out=root/'bench/reports/release';summary=[]
 for n in (1,2):
  rows=[json.loads(l) for l in (clone/f'validation/run{n}-envelopes.jsonl').read_text(encoding='utf-8').splitlines()]
  profiles=[json.loads(l) for l in (clone/f'validation/run{n}-profiles.jsonl').read_text(encoding='utf-8').splitlines()]
  valid=rows[:100];counts={k:dict(Counter(r['run']['sections'].get(k,'not_enabled') for r in valid)) for k in ['identity','roles','subunits','accounts','website','hiring','activity']}
  counts['social']={'available':sum(any(c['availability']=='available' and c['field'].startswith(('social_profile.','registry_social.')) for c in r['claims']) for r in valid)}
  counts['location_profiles']={'available':sum(p['evidence']['locations']['status']=='available' for p in profiles[:100])}
  issues=section_summary(valid)
  (out/f'run{n}-failed-stale.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  metrics=json.loads((clone/f'validation/run{n}-report.json').read_text(encoding='utf-8'))
  slim={k:metrics.get(k) for k in ['input_rows','emitted_envelopes','counts_by_state','requests','requests_per_company','shared_requests','changes','observation_changes','deadline_hits','warnings','limits','search','cost_usd','hiring','website_second_pass']}
  (out/f'run{n}-metrics.json').write_text(json.dumps(slim,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  invalid=[{'organisation_number':r['organisation_number'],'sections':r['run']['sections']} for r in rows[100:]]
  summary.append({'run':n,'envelopes':len(rows),'profiles':len(profiles),'coverage_valid_100':counts,'failed_or_stale_sections_valid':len(issues),'invalid_results':invalid})
 for name in ['execution.json','verification.txt']:shutil.copyfile(clone/'validation'/name,out/name)
 (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
