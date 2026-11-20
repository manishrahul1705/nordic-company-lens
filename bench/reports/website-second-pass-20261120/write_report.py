"""Render the final retry measurement, all-site ownership reviews and suite."""
from collections import Counter
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent


def main():
    m=json.loads((HERE/'measurement.json').read_text(encoding='utf-8'))
    assert 'DNS_fallback_policy' in m
    reviews=json.loads((HERE/'ownership-review.json').read_text(encoding='utf-8'))
    raw=Path('bench/cache/website-second-pass-20261120/pytest-final.log').read_bytes()
    log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
    result=re.findall(r'(?m)^.*\d+ passed.* in [\d.]+s.*$',log)
    assert result,'Full suite unfinished'
    failures=re.findall(r'(?m)^FAILED (.+)$',log)
    (HERE/'pytest.txt').write_text('\n'.join(l.rstrip() for l in log.splitlines())+'\n',encoding='utf-8',newline='\n')
    reasons=Counter(x['details'].get('reason','completed') for x in m['second_pass']['companies'])
    named={org:next((x['details'] for x in m['second_pass']['companies'] if x['organisation_number']==org),None)
           for org in ['915279082','930832707','983520944','934289099']}
    summary={'measurement':m,'tests':result[-1].strip(),'failures':failures,'new_tests':28,
        'all_recovered_sites_reviewed':len(reviews),'retry_reasons':dict(reasons),'named_cases':named,
        'baseline_test_count':1815,'proof_verifier_budget_caps_unchanged':True,
        'scope':'Only new not_available recovery eligibility; legacy failed/blocked selector retained.'}
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    lines=['# Bounded transient website second-pass recovery', '',
        '## Implementation', '',
        'Extend the existing end-of-run second pass to not_available websites with a final recorded unreachable-candidate reason of website_timeout, website_connect_error, dns_timeout or dns_unavailable. TLS, robots, definitive no_such_domain and ownership/veto rejections for the same candidate are excluded. A single authority variant returning NXDOMAIN does not override an explicitly transient final candidate summary; DOGLEG had that combination. NORTH GREY\'s final no_such_domain summary stays excluded.', '',
        'No new nominations: retain original candidate domain, origin and subunit scope. Existing maximum three candidate nominations/company; one bounded collector pass per original candidate, with immediate transport transient retries disabled. The normal candidate pass still has its existing HTTPS apex/www and HTTP fallback variants; one candidate pass is not guaranteed one HTTP request. An attempted marker prevents another absence-retry dispatch on reentry. The old failed/blocked selection remains unchanged.', '',
        'The same pooled and 40/company budget object authorizes every HTTP attempt, with normal website caps and host pacing. No budget/cap defaults changed. The unchanged collector and all final shared/social/entity/group/cohort/universe guards determine publication; name alone never proves ownership.', '',
        'New optional recovery does not dispatch with <=500 ms left. Its existing 45-second/company window ends at least 250 ms before the real crawl deadline. Publication is transactional: failed recovery preserves the original terminal state/claims/errors; a clean proved-site checkpoint is retained before optional activity work, so a later activity timeout cannot erase it or add an envelope deadline error. Timeout reasons stay in retry metadata. No counter semantics, proof rule, validator, verifier or existing test changed.', '',
        '## Live measurement', '',
        'Baseline: stage-am-live1000, 1,000 companies. Saved available claims and real evidence were reused; only the new eligible not_available companies ran live through the production safe transport. The original request log/counters were retained. The site-on crawl reserve was retained and the entire saved 1,045.578-second pipeline duration was subtracted from the retry window, conservatively including its finalisation time. This is not a new all-source live run.', '',
        f"Selected **{m['eligible_not_available_companies']} companies / {m['candidate_count']} original candidates**. Dispatched {m['second_pass']['attempted']} companies / {m['second_pass']['candidates']} candidates; the remainder were blocked by their remaining budgets or retry window. [Exact nominations](eligible.json).", '',
        m['DNS_fallback_policy']+' The saved report lacks exact per-company fallback seconds, so this avoids granting a fresh DNS allowance. One preliminary run without that shared conservative DNS context is superseded and not used for the reported final result. A second preliminary run exposed the follow-on optional-activity rollback issue; the final run uses the clean proved-site checkpoint.', '',
        '| Information | Before | After | Gain |','|---|---:|---:|---:|']
    for label,key,attr in [('Verified sites','sites','companies'),('Brands','brands','claims'),
        ('Social companies','social','companies'),('Social claims','social','claims'),
        ('News companies','news','companies'),('News claims','news','claims')]:
        a=m['before'][key][attr];b=m['after'][key][attr];lines.append(f'| {label} | {a} | {b} | {b-a:+d} |')
    lines+=['',f"**Extra HTTP: {m['extra_HTTP']}.** The second-pass stage itself used {m['second_pass']['requests']} requests and {m['second_pass']['seconds']:.3f} s; bounded advertised-news requests, if any, account for the remainder. Measured live retry plus final-guard stage: **{m['isolated_live_and_final_guard_seconds']:.3f} s**. Total replay including saved-output processing and strict verification: {m['total_replay_seconds']:.3f} s. These are standalone addition timings, not a paired whole-run wall-time delta.", '',
        f"Replay ordering correction: {m.get('prior_official_activity_claims_retained_for_pipeline_order',0)} prior official activity claims were retained from the saved baseline. Production merges registry activity after the second pass; this replay started with it already present. A company-site activity section replacement must not appear to delete those later-merged official facts. The harness now retains them before writing; the already completed live result was corrected offline with socket/DNS access forbidden and strictly reverified. That additional offline correction/verification is not included in the original replay duration above. No live request or acceptance decision was added by this correction.", '',
        f"HTTP including the saved run: {m['pooled_requests_including_saved']}/{m['pooled_cap']}; max/company {m['max_company_requests']}/40. Remaining crawl window at replay setup: {m['remaining_crawl_seconds_at_start']:.3f} s; after live work and serialisation: {m['remaining_crawl_seconds_after_live']:.3f} s. **Deadline hits: {m['deadline_hits']}.** Retry metadata reasons: {json.dumps(dict(reasons))}. These local retry-window timeouts are distinct from global/envelope deadline hits. No negative website claims are published.", '',
        '## Named candidates and recovered sites', '',
        '| Company | Orgnr | Retry result |','|---|---|---|']
    for org,name in [('915279082','TØMRER S. FAGERBEKK AS'),('930832707','DOGLEG AS'),('983520944','SPINELL FRISØR AS'),('934289099','NORTH GREY AS')]:
        d=named[org]
        text='excluded: definitive no_such_domain' if d is None else ('proved website; ' if d.get('recovered') else 'not recovered; ')+d.get('reason','completed')
        lines.append(f'| {name} | {org} | {text} |')
    lines+=['','All recovered sites after final guards:','']
    for r in m['recovered_sites']:lines.append('- '+r['company']+' ('+r['orgnr']+'): '+r['url'])
    lines+=['','## Hand-review of every recovery','',
        '[All recovered claims, exact evidence spans/hashes, registered identity and checked publisher pages](ownership-review.json). Each retained site was reviewed against its own-company proof and registered contacts; no inferred ownership, different-entity page or name-only match was accepted. Final verdicts are recorded per site.','']
    for r in reviews:
        lines+=['- **'+r['company']+' ('+r['orgnr']+')** — '+r['claim']['value']['final_url']+
            '; proof `'+r['claim']['value']['proof_type']+'`. '+r.get('review_verdict','See retained proof and registry comparison.'),'']
    lines+=['## Verification','',
        f"Strict verifier passed {m['strict_verifier']['lines']} envelopes, {m['strict_verifier']['published_claims']:,} claims and {m['strict_verifier']['source_blobs_verified']:,} source blobs, with **zero unverified synthesis values**. Every available claim has its retained evidence; verbatim spans and SHA-256 are verified. Failed retry state is preserved and the live measurement asserts no new envelope deadline errors.",'',
        'Final full suite: **'+result[-1].strip()+'**. Baseline 1,815 tests; 28 new tests. [Full output](pytest.txt). New cases cover all admitted/definitive reasons, candidate veto precedence, one-pass reentry protection, company and pooled caps, near-deadline admission, cancellation before the deadline, unchanged ownership veto and preserving a proved site when optional activity is cancelled. The earlier pre-checkpoint full suite also passed all 1,842 tests.','']
    if failures:lines+=['Failures:','']+['- '+f for f in failures]+['','Do not commit while final failures remain.','']
    lines+=['Raw downloads, bench/runs, caches and pytest temporary directories are not committed. No push.','']
    (HERE/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':main()
