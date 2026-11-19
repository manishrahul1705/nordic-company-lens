# Frozen 1,000 attribution audit

> **History.** The run this audit read (`bench/runs/long-label-clean-20261118`) no longer exists, so it cannot be rerun. It is superseded by the rerunnable audit in [stage-x-accuracy/REPORT.md](stage-x-accuracy/REPORT.md) (`attribution_audit.py`).

**Result: 0 of 1,000 envelopes contain a claim, evidence record, or cited saved company page attributable to a different organisation number.** No code was changed for this audit.

## Scope and checks

Audited `bench/runs/long-label-clean-20261118/envelopes.jsonl` (1,000 envelopes; 175,486 claims; 173,974 evidence records) and its `report.json` request log. For every envelope, claim evidence IDs resolve to that envelope's evidence table: **0 dangling references**. Entity-specific registry evidence URLs (`/api/enheter/{orgnr}`) matched the enclosing envelope number: **0 mismatches**. Company-owned evidence page URLs and content hashes were not reused across different envelopes: **0 cross-envelope reuses**. Evidence snippets contained **0 explicit foreign organisation-number labels**.

Claims are attributed by their enclosing envelope. Registry facts can legitimately name related subunits or role-holding entities; those references do not transfer the parent envelope's claims to those entities.

## 986665358 and 919038438

The saved registry record for **986665358** names **FALSEN TRANSPORT AS**, founded 2004-02-23 and registered 2004-03-18. The legal entity record has `historiskeNavn: []`. Its registered subunit **972105139** is also FALSEN TRANSPORT AS and has a former name, **FALSENS TRANSPORT** (1995-02-23 through 2004-03-22). The former name belongs to that subunit record.

**919038438** is **BERGEN CONTAINER TRANSPORT AS**, a separate registry entity. The frozen records provide no relationship between it and 986665358. Neither envelope's evidence snippets nor claim values reference the other number.

The Falsen candidate was generated from the legal name (`origin: legal_name_slug`) as `falsentransport.no`. The registry record had no registered website. The request log associates root, contact, robots, and sitemap requests directly with 986665358; the saved run shows no redirect, and no company-owned page evidence was reused across envelopes. This is a name-derived website candidate, not a registry-declared website or an association through 919038438. The website section failed with `invalid_span`; **no website claim was published for 986665358**.

**Conclusion:** no published claim in this frozen run is shown to be attributed to the wrong company.
