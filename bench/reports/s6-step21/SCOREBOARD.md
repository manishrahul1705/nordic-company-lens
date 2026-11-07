# Step 21 - source verification STOP

Starting commit: b3fe202e8ae6a29ef8085af930d53f167969f918. Verification on 7 November 2026, approximately 14:37 IST, before the 16:15 IST hard stop. Search OFF; no application credentials. No runtime changes, tests, benchmark or push.

## Blocking result

https://w2.brreg.no/robots.txt returned HTTP 200 and explicitly states:

```
User-agent: *
Disallow: /kunngjoring/
```

This covers the public announcement landing page and its subordinate query/detail paths. Under the user's explicit stop condition, no ten-company queries (including Tensio) were made and no collector was built. The landing page had already been fetched once during the initial parallel verification before the robots response was inspected; no further announcement-path requests were made afterward. Raw responses: robots.txt and landing.txt.

## Other verified facts and limits

Official owner: Bronnoysund Register Centre, confirmed by the official brreg.no announcements documentation linking to this exact service. Public landing page returned HTTP 200 without authentication; it presents organisation-number searches. No company query was tested, so dates/types/text, exact matching behaviour and per-company request cost remain unverified.

The official subscription documentation says subscriptions are free but require a registered email/user; delivery is daily/weekly email links. Its terms require source attribution. This is not evidence that anonymous automated scraping is permitted or that announcement text is NLOD-licensed. A specific NLOD grant for this service was not verified; the existing Enhetsregisteret API licence is not assumed to cover it.

Sources:
- https://www.brreg.no/registersok/kunngjoringer/om-kunngjoringer/
- https://www.brreg.no/bruke-data-fra-bronnoysundregistrene/abonnement/abonnement-pa-kunngjoringer/
- https://w2.brreg.no/robots.txt

Decision: STOP at step 1 because robots disallows the exact service path. Existing updates-feed collection is unchanged. No workaround, alternate-host bypass or unsupported licence assumption was attempted. No commit made.
