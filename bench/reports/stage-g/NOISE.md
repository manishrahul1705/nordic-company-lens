# Stage G measured two-run variance

Two sequential unchanged-runtime frozen1,000-company runs. Runtime source/tests/lockfiles match007b34f; HEAD802154c adds only reports. Fresh state per run, identical README command, credentials stripped, no bulk override, default budgets. This is an observed two-run range, **not a statistical confidence interval or a blanket transient-failure exemption**. Run2 was selected as the final reported run before its results were known; it has fewer websites, so this is not selection of the better result.

| Metric | Run1 | Run2 (final) | B minus A | Observed min-max | Absolute span |
|---|---:|---:|---:|---|---:|
| websites | 113 | 112 | -1 | 112 - 113 | 1 |
| social_companies | 47 | 47 | +0 | 47 - 47 | 0 |
| jobs | 2 | 2 | +0 | 2 - 2 | 0 |
| activity | 1000 | 1000 | +0 | 1000 - 1000 | 0 |
| news_companies | 7 | 7 | +0 | 7 - 7 | 0 |
| article_claims | 69 | 69 | +0 | 69 - 69 | 0 |
| GLEIF_companies | 32 | 32 | +0 | 32 - 32 | 0 |
| TED_companies | 0 | 0 | +0 | 0 - 0 | 0 |
| TED_awards | 0 | 0 | +0 | 0 - 0 | 0 |
| facts | 165481 | 165481 | +0 | 165481 - 165481 | 0 |
| http_total | 9281 | 9273 | -8 | 9273 - 9281 | 8 |
| http_mean | 9.281 | 9.273 | -0.008 | 9.273 - 9.281 | 0.008 |
| http_max | 40 | 40 | +0 | 40 - 40 | 0 |
| wall_seconds | 2136.968971800001 | 1988.786416499992 | -148.183 | 1988.786416499992 - 2136.968971800001 | 148.183 |
| seconds_per_100 | 213.6968971800001 | 198.8786416499992 | -14.8183 | 198.8786416499992 - 213.6968971800001 | 14.8183 |
| deadline_hits | 0 | 0 | +0 | 0 - 0 | 0 |

## Every website/article difference

Only one website membership difference; **no article URL/value difference** across the two runs (69articles/7companies both).

| Org / company | Run1 | Run2 | Recorded diagnostic |
|---|---|---|---|
| 911691248 / ISTAD ART SOLUTION NORWAY NUF | https://www.pederistad.no | withheld | Same homepage HTTP200/hash ec498f544d8371cdb72955c023a0cf08af140906ddcccdee612776f80400fc64 in both; blob exists in run1 but is absent from run2 state. Final entity-scope guard withholds registered_role_holder-only proof when proof page cannot be read. Both runs also record /om-oss HTTP404 and website_link_only; that shared404 does not explain the difference. |

Exact request events, original errors and final guard state:istad-diagnostics.json; website-article-differences.json retains each differing company/article and all source errors. **No timeout/connect failure was recorded for this homepage.** Missing retained evidence is a storage/retention limitation, not established transport noise. No code or output was changed to hide it. Gate permits reporting the band; main submission limitations include the issue.

Net website span1; membership churn1. Article span0. Social/jobs/activity/GLEIF/TED counts unchanged. No causal inference about runtime from these live measurements.
