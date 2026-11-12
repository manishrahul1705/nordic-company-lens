# Contact-email and phone publication precision

Branch `more-websites`; no push. Publication-only change; website ownership scoring, registered-email proof, foreign/group vetoes and request budgets are unchanged. No live benchmark or network fetch was performed for this fix.

## Rules

An exact registered email remains publishable, including a personal or free-mail address. Otherwise, email must use the verified site's registered domain and an explicit approved role local part, or its company-name/domain label. Unknown/personal locals are withheld by default; dotted names, names found on the page, common Norwegian personal-name patterns and unregistered free-mail addresses are rejected. The requested role list is explicit: `contact` is not silently added as another role. Registered-email proof keeps its previous stricter ownership conditions; this filter is never called by proof scoring.

A phone must equal the registered phone/mobile or occur in a corporate contact/footer area outside staff lists. The placement parser recognizes staff classes, Person markup, Norwegian business-card layouts, name/title grids, job-title blocks and named paragraph/heading cards. Corporate footer phones remain eligible even on a staff-directory page. Exact registered numbers remain eligible. Only captured HTML is inspected; no additional page requests occur.

The same publication policy filters carried-forward contacts after refresh carry-forward, so a failed website refresh cannot resurrect an old unregistered personal contact. Valid role and registered contacts retain their carry-forward behavior. Proof claims and source evidence are not rewritten by this filter.

## Offline re-derivation from the latest saved 1,000 run

Source: `bench/runs/news-contact-live`, the latest completed 1,000-company run. Its rejected news trial remains reverted; this contact replay does not reapply that feature. Every existing cited contact was evaluated with the exact new runtime predicates, against its saved response and registered contact fields. Each inspected blob hash and verbatim span was verified. No original run files were rewritten, no new contacts were searched or added, and no requests were made. This is a bounded re-evaluation of already published contacts, not a new live coverage measurement.

| Contact metric | Before | After |
|---|---:|---:|
| Total contact facts | 350 | 150 |
| Email facts | 202 | 78 |
| Phone facts | 148 | 72 |
| Companies with a contact fact | 102 | 87 |

The 200 withheld facts include unregistered personal/unknown email locals and unregistered numbers outside a qualifying corporate block or inside staff lists. It is not claimed that all 200 were false values or personal addresses. Positive allowlists intentionally abstain from unconfirmed contacts. Website proof and all non-contact facts are outside this re-evaluation and remain unchanged.

Reproduce: `uv run --frozen python scripts/replay_contact_precision.py`. Results: `summary.json`, every before/after decision and cited evidence in `decisions.json`.

## Re-check of the original 20 contacts

**12 retained; 8 removed. Zero disallowed personal emails remain.** All five previously flagged personal emails are removed: CONPLAN `per.eirik` and `edith`, VS ELEMENT `dawit.hurrisa`, IDESTOVA `anny`, and STYREGUIDEN `vidar`. The AAS BETONG and ELEKTROKOMPETANSE staff-list mobiles are removed. TECTRAP `contact@tectrap.com` is also withheld because it is neither registered nor in the explicit requested role/company-name allowlist.

A separate fixed-seed random sample of **20 retained contacts** was checked against saved sources: 20 correct under the new policy, 0 wrong/doubtful. One named email, `siv@kanobutikken.no`, equals the exact registered email and is intentionally kept under rule (a); zero unregistered personal emails remain. Corporate footer/registered numbers, role locals, original source excerpts and organisation attribution were checked. See `REVIEW.md`, `original-20-recheck.json` and `retained-20-review.json`.

## Validation and changed files

New regression cases cover every requested role, company/domain local, exact registered personal/free-mail email, personal/initial/concatenated email rejection, free-mail/foreign-domain rejection, staff cards/grids/paragraphs, registered and footer phone positives, staff-list negatives and carried-forward bypass. Existing integration/refresh tests passed unchanged (66 focused cases). No prior wrong-company regression fixtures or expectations were changed. Final full suite: **1,343 passed in 335.40 s** (`pytest.txt`). All 42 new publication-policy cases pass; existing fixtures and expectations are unchanged.

Runtime files: `web/contact_policy.py` (publication predicates and captured HTML regions), `web/collector.py` (apply at extraction), `runner.py` (filter carried-forward contacts before publication guards). Supporting files: `tests/test_contact_publication_precision.py`, `scripts/replay_contact_precision.py`, `docs/SOURCES.md`, `IMPROVEMENT_LOG.md` and these reports. No dependency or lockfile changes. No ownership-proof source file was changed.
