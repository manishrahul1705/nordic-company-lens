"""
Regression tests for V6-09:
- Multi-line statutory purpose clean sentence joining.
- NACE code/description deduplication.
- Honest, scoped negative NAV claims in unknown explanations.
- Validation through validate_synthesis.
"""
import hashlib
import json
import pytest

from signalpost.models.evidence import utc_now
from signalpost.models.synthesis import Unknown
from signalpost.runner import placeholder
from signalpost.sources.extract import Section, Source, add
from signalpost.synthesis.readability import unknown_text
from signalpost.synthesis.template import generate
from signalpost.synthesis.validate import validate_synthesis


def test_v6_09_multiline_statutory_purpose_joined_cleanly():
    """
    V6-09: When statutory purpose is a list of lines/clauses, they must be joined cleanly
    and pass synthesis validation without cutting off mid-clause.
    """
    org = "923609016"
    purpose_lines = [
        "Selskapets formal er a drive IT-virksomhet.",
        "Herunder ogsa investere i andre foretak og verdipapirer.",
    ]
    raw_json = json.dumps({"vedtektsfestetFormaal": purpose_lines}).encode("utf-8")
    sha = hashlib.sha256(raw_json).hexdigest()
    source = Source("https://data.brreg.no/enhetsregisteret/api/enheter/923609016", raw_json, sha, utc_now())

    sec = Section()
    add(sec, source, org, "identity", "identity.statutory_purpose", purpose_lines, "/vedtektsfestetFormaal")

    env = placeholder(org, "run-1", utc_now())
    env.claims.extend(sec.claims)
    env.evidence.extend(sec.evidence)

    synth = generate(env)

    what_it_does = synth.sections.what_it_does
    purpose_sentence = next((s for s in what_it_does if "Registered purpose" in s.text), None)

    assert purpose_sentence is not None
    # Must contain both parts joined together, not cut off after first line
    assert "Selskapets formal er a drive IT-virksomhet" in purpose_sentence.text
    assert "Herunder ogsa investere i andre foretak" in purpose_sentence.text
    assert synth.checks.dropped_sentences == 0


def test_v6_09_duplicate_nace_deduplicated():
    """
    V6-09: Duplicate NACE claims must not produce repeated sentences in what_it_does.
    """
    org = "923609016"
    nace_val = {"kode": "62.010", "beskrivelse": "Programmeringstjenester"}
    raw_json = json.dumps({"naeringskode1": nace_val, "naeringskode2": nace_val}).encode("utf-8")
    sha = hashlib.sha256(raw_json).hexdigest()
    source = Source("https://data.brreg.no/enhetsregisteret/api/enheter/923609016", raw_json, sha, utc_now())

    sec = Section()
    add(sec, source, org, "identity", "identity.nace1", nace_val, "/naeringskode1")
    add(sec, source, org, "identity", "identity.nace2", nace_val, "/naeringskode2")

    env = placeholder(org, "run-1", utc_now())
    env.claims.extend(sec.claims)
    env.evidence.extend(sec.evidence)

    synth = generate(env)

    nace_sentences = [s for s in synth.sections.what_it_does if "62.010" in s.text]
    assert len(nace_sentences) == 1  # Deduplicated to exactly 1 sentence
    assert synth.checks.dropped_sentences == 0


def test_v6_09_scoped_negative_nav_explanation():
    """
    V6-09: Negative NAV claims must be honestly scoped:
    'No active NAV advertisements were found in the sources checked during this run.'
    """
    org = "923609016"
    env = placeholder(org, "run-1", "2026-10-21T00:00:00Z")
    unk = Unknown(family="hiring", state="not_available", reason="not_available")

    explanation = unknown_text(unk, env)
    assert explanation == "No active NAV advertisements were found in the sources checked during this run."
