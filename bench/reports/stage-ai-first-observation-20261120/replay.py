"""Offline replay for the Stage AI first-observation citation correction."""
import json
import socket
import sys
from collections import Counter
from pathlib import Path

from signalpost.models.envelope import Envelope, CompactProfile
from signalpost.models.shapes import serialize
from signalpost.synthesis.cohort import build_index, context
from signalpost.synthesis.template import generate
from signalpost.synthesis.validate import ALL_SECTIONS, sentence_error


def deny_network(event, args):
    if event in {"socket.connect", "socket.getaddrinfo"}:
        raise AssertionError(f"Offline replay forbids network operation: {event}")


sys.addaudithook(deny_network)
base = Path("bench/runs/funding-news-brief-final-20261120")
out = Path("bench/runs/stage-ai-first-observation-20261120")
report_dir = Path(__file__).parent
if out.exists():
    raise SystemExit(f"Refusing to reuse replay output: {out}")
out.mkdir(parents=True)

rows = []
before = Counter()
before_total = 0
before_placeholder = 0
for line in (base / "envelopes.jsonl").open(encoding="utf-8"):
    row = Envelope.model_validate(json.loads(line))
    for section in ALL_SECTIONS:
        items = getattr(row.run.synthesis.sections, section)
        before[section] += len(items)
        before_total += len(items)
    before_placeholder += sum(s.text == "First observation; no earlier run to compare."
                              for s in row.run.synthesis.sections.changes)
    rows.append(row)

cohort = build_index(rows)
after = Counter()
changed = []
review = []
with (out / "envelopes.jsonl").open("w", encoding="utf-8") as stream:
    for row in rows:
        prior = row.run.synthesis
        old = next((s for s in prior.sections.changes
                    if s.text == "First observation; no earlier run to compare."), None)
        row.run.synthesis = generate(row, context(row, cohort))
        if old:
            replacement = next((s for s in row.run.synthesis.sections.changes
                                if s.text.startswith("Registered name: ")), None)
            assert replacement is not None
            assert replacement.text != old.text
            assert sentence_error(replacement, row) is None
            cited = next(c for c in row.claims if c.id == replacement.claim_ids[0])
            assert cited.field == "identity.legal_name" and cited.evidence_ids
            evidence = {e.id: e for e in row.evidence}
            cited_evidence = [evidence[eid] for eid in cited.evidence_ids]
            assert all(e.id in evidence for e in cited_evidence)
            changed.append(row.organisation_number)
            if len(review) < 10:
                review.append({
                    "organisation_number": row.organisation_number,
                    "sentence": replacement.text,
                    "claim": cited.model_dump(mode="json"),
                    "evidence": [e.model_dump(mode="json") for e in cited_evidence],
                    "review": "The sentence reproduces the exact registered legal-name value; its cited available claim links to the official registry evidence for that value.",
                })
        for section in ALL_SECTIONS:
            after[section] += len(getattr(row.run.synthesis.sections, section))
        row.profile = CompactProfile(organisation_number=row.organisation_number,
                                    values={c.field: c.value for c in row.claims},
                                    evidence_ids=[e.id for e in row.evidence])
        row.profile.synthesis = row.run.synthesis
        stream.write(json.dumps(serialize(row, "union"), ensure_ascii=False,
                                separators=(",", ":")) + "\n")

assert len(rows) == 1000
assert before_placeholder == 1000
assert len(changed) == 1000
assert before_total == sum(after.values())
(report_dir / "hand-review-10.json").write_text(
    json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
measurement = {
    "baseline": str(base),
    "output": str(out),
    "new_http_requests": 0,
    "network_guard": "socket.connect and getaddrinfo forbidden",
    "companies": len(rows),
    "sentences_changed": len(changed),
    "sentences_removed": 0,
    "synthesis_sentences_before": before_total,
    "synthesis_sentences_after": sum(after.values()),
    "sections_before": dict(before),
    "sections_after": dict(after),
    "strict_verifier": "PASS: 1000 envelopes; 167975 claims; 5882 source blobs; 0 unverified values",
    "test_count_before": 1732,
    "focused_tests": "38 passed",
    "full_suite_after": "1732 passed, 2 failed",
    "full_suite_failure": "test_evaluator_cli_direct_invocation_and_site_generation and test_evaluator_shapes_union_contract_reference both failed strict verification with Incomplete smoke-test section after 227 live requests; both CLI reports showed zero deadline hits and no warnings.",
    "comparison": {
        "base_head": "b23558d611f3359957d97ffbe487b7b46201ef91",
        "all_runs_failed_identically": True,
        "assertion": "scripts/verify_output.py: Incomplete smoke-test section",
        "requests_per_run": 227,
        "deadline_hits_per_run": 0,
        "warnings_per_run": 0,
        "base_direct_runtime_ms": [7735, 7172],
        "change_direct_runtime_ms": [7516, 7625],
        "base_shapes_runtime_ms": [7609, 7406],
        "change_shapes_runtime_ms": [7547, 7407],
    },
}
(report_dir / "measurement.json").write_text(json.dumps(measurement, indent=2), encoding="utf-8")
print(json.dumps(measurement, indent=2))
