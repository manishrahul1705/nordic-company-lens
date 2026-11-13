# Publication role allowlist extension

Branch `more-websites`; base `c33f535`. No push. The only runtime change extends `ROLES`; personal-name rejection, exact registered-email exceptions, free-mail/domain rules, phone placement, carry-forward handling and ownership proof are unchanged. No network or new live benchmark was performed.

Added the requested role locals while retaining existing entries: contact, kontor, firma, epost, e-post, hi, enquiries, inquiries, orders, order, reservasjon, drift, teknisk, marked, marketing, jobb, jobs, career, karriere, hr, personal, innkjop, purchase, accounts, lonn, bilag and invoice. The requested already-present firmapost, mail, hello, booking, bestilling, resepsjon and regnskap remain present.

## Offline replay on the same saved 1,000 companies

Source: `bench/runs/news-contact-live`, identical to the preceding contact precision replay. Original saved artifacts were not changed. Every inspected response hash and cited span was verified. The replay re-evaluates the original 350 published contact candidates; it adds no newly discovered data and does not reapply the rejected news trial. Baseline results and their manual reviews remain untouched in `bench/reports/contact-precision`.

| Metric | Previous policy | Extended policy |
|---|---:|---:|
| Contact facts | 150 | 156 |
| Email facts | 78 | 84 |
| Phone facts | 72 | 72 |
| Companies with contacts | 87 | 89 |

No previously retained fact is lost. The replay asserts that every phone decision remains identical and every gain is an email. Original 20-item sample: 13 retained, 7 removed; the five disallowed personal emails and two staff-list phones remain excluded. The functional TECTRAP contact mailbox is now allowed as requested.

## Complete new-item review

Only **6 newly retained items exist**. All six were reviewed; sampling 20 distinct new items is therefore impossible. The deterministic fixed-seed sample covers all six. **6 correct, 0 wrong, 0 doubtful, 0 personal emails.**

| Company | Orgnr | Newly retained role mailbox |
|---|---|---|
| STOA AUTOREP AS | 920918204 | kontor@stoaautorep.no |
| LOFOTPOSTEN AS | 968386085 | marked@lofotposten.no |
| CONTROL SOLUTIONS AS | 926490060 | contact@control-solutions.no |
| ASKØY24 AS | 923998012 | marked@askoy24.no |
| TANGERIN AS | 989145509 | invoice@tangerin.no |
| TECTRAP AS | 920542158 | contact@tectrap.com |

Each is a functional mailbox cited on the same verified company's site: office, marketing/advertising, company footer, invoicing or enquiry contact. Tangerin's invoice address is separate from its named registered/personal contacts; Tectrap's functional alias remains a role address even on an individual's company profile page. No name inference was used. Exact URLs, short source spans and verdicts are in `REVIEW.md` and `new-items-review.json`.

Reproduce: `uv run --frozen python scripts/replay_contact_role_extension.py`. Detailed policy decisions: `decisions.json`; comparison: `summary.json`. New tests cover all requested locals plus unchanged rejection of personal name/initial/concatenated addresses. Focused tests: 81 passed. Full suite: **1,382 passed in 398.89 s** (`pytest.txt`).

Changed files: the publication allowlist constant, `tests/test_contact_role_extension.py`, the reproducible replay helper, `IMPROVEMENT_LOG.md`, the prior report's follow-up note and this report folder. No existing test fixture or expectation was changed; no dependency/lockfile changes.
