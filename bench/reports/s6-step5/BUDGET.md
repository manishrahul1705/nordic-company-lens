# Budget diagnosis

The saved flags-OFF run has 103 companies with `website_budget_exhausted`; ON has 102. Of the OFF companies, 80 occupy the exclusive budget loss bucket, because ambiguous/blocked/conflicting-owner outcomes take precedence for the others.

These errors are raised by WebsiteHttp.raw when the company request count reaches the minimum of the website cap (14 plus one reserved activity request) and the total-company cap (18 minus official requests). They are not a per-company time limit. There is no per-company time budget in this implementation. Both runs have zero company `deadline` errors, zero global `budget_exhausted` errors, and zero run deadline hits. Individual request timeouts are a different failure: they do not mean a company's time budget expired.

Therefore the requested conditional trial (at least 80 companies exhausting time budget) is not triggered. No concurrent fallback or 4-second timeout change was made. Shorter timeouts would not directly lift these request-count ceilings. Counts and request exception classes are recorded in `budget.json`.
