# Stage A test fix and publication preparation

The shipped NAV index is not redated. The test now parses built_at as ISO-8601, requires an aware zero-offset UTC timestamp, rejects future timestamps, and retains the existing schema-validating load for 30 November 2026 plus the configured age bound. No literal rebuild date is pinned. Runtime code is unchanged.

Full suite: **1,382 passed, 0 failed in 417.36 seconds** (`pytest.txt`).

Authorized merge target: `main` at `https://github.com/manishrahul1705/nordic-company-lens.git`. A normal no-fast-forward merge preserves all more-websites history. No tags or other repositories are targeted.

Tracked-tree and new-history filename audits found no raw crawl/bulk/universe downloads, nav.key, .env, private-key directories or credential files. The tracked-text credential-signature scan found no private-key, GitHub-token or AWS-key signatures. Frozen benchmark subsets and bundled derived indexes are intentional tracked data. Rebuilt CC and NAV gzip files are tracked; the search adapter is absent. No credentials were added by this change. Post-push remote SHA and main-tree checks are reported separately after the push.
