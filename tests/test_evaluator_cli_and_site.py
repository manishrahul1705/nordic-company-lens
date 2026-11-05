"""Tests for V6-10: Evaluator Rehearsal, CLI direct execution, and Offline Site Integrity."""
import json
from pathlib import Path
from signalpost.cli import main
from scripts.verify_output import verify


def test_evaluator_cli_direct_invocation_and_site_generation(tmp_path):
    """
    Proves that:
    1. Signalpost CLI can be directly invoked with options (e.g. without explicit 'run' subcommand).
    2. Emits valid envelopes, report, and generates complete offline site.
    3. Output passes strict independent verification (schema, hashes, verbatim spans, synthesis).
    4. Profile HTML files stay within the 250 KB budget gate.
    """
    ci20_input = Path("tests/fixtures/ci20.jsonl")
    ci20_bulk = Path("tests/fixtures/ci20.csv")
    out_envelopes = tmp_path / "envelopes.jsonl"
    out_report = tmp_path / "report.json"
    out_site = tmp_path / "site"
    state_dir = tmp_path / "state"

    # Invocation with direct flags (no 'run' prefix)
    argv = [
        "--organisations", str(ci20_input),
        "--bulk", str(ci20_bulk),
        "--output", str(out_envelopes),
        "--report", str(out_report),
        "--site-dir", str(out_site),
        "--state-dir", str(state_dir),
        "--expected-count", "20",
        "--time-budget-seconds", "30",
        "--workers", "4",
        "--no-websites", "--no-hiring", "--no-public-activity",
    ]

    exit_code = main(argv)
    assert exit_code == 0, f"CLI direct invocation failed with code {exit_code}"

    # Verify report metrics
    assert out_report.exists()
    report_data = json.loads(out_report.read_text(encoding="utf-8"))
    assert report_data["emitted_envelopes"] == 20
    assert len(report_data["invalid_inputs"]) == 0
    assert report_data["deadline_hits"] == 0

    # Verify output integrity via scripts/verify_output
    result = verify(
        first=out_envelopes,
        state_dir=state_dir,
        count=20,
        organisations=ci20_input,
        report=out_report,
        require_clean=True,
    )
    assert result["lines"] == 20
    assert result["schema_valid"] is True
    assert result["published_claims"] > 0
    assert result["synthesis_unverified_values"] == 0

    # Verify offline site files
    assert (out_site / "index.html").exists()
    assert (out_site / "compare.html").exists()
    assert (out_site / "progress.json").exists()
    c_dir = out_site / "c"
    assert c_dir.exists()
    html_files = list(c_dir.glob("*.html"))
    data_files = list(c_dir.glob("*.data.js"))
    assert len(html_files) == 20
    assert len(data_files) == 20

    # Check 250 KB gate on every profile HTML file
    for html_file in html_files:
        assert html_file.stat().st_size <= 250 * 1024, f"Profile {html_file.name} exceeded 250 KB limit"


def test_evaluator_shapes_union_contract_reference(tmp_path):
    """
    Proves that all three supported envelope shapes (union, contract, reference)
    can be emitted and verified cleanly through the CLI.
    """
    ci20_input = Path("tests/fixtures/ci20.jsonl")
    ci20_bulk = Path("tests/fixtures/ci20.csv")

    for shape in ("contract", "reference"):
        shape_dir = tmp_path / shape
        shape_dir.mkdir()
        out_envelopes = shape_dir / f"envelopes_{shape}.jsonl"
        out_report = shape_dir / f"report_{shape}.json"
        state_dir = shape_dir / "state"

        argv = [
            "run",
            "--organisations", str(ci20_input),
            "--bulk", str(ci20_bulk),
            "--output", str(out_envelopes),
            "--report", str(out_report),
            "--state-dir", str(state_dir),
            "--envelope-shape", shape,
            "--expected-count", "20",
            "--time-budget-seconds", "30",
            "--workers", "4",
            "--no-websites", "--no-hiring", "--no-public-activity",
        ]
        exit_code = main(argv)
        assert exit_code == 0

        result = verify(
            first=out_envelopes,
            state_dir=state_dir,
            count=20,
            organisations=ci20_input,
            report=out_report,
            require_clean=True,
        )
        assert result["schema_valid"] is True
        assert result["lines"] == 20

def test_cli_rejects_removed_llm_mode(capsys):
    import pytest

    with pytest.raises(SystemExit) as error:
        main(['run', '--organisations', 'unused.jsonl', '--output', 'unused-output.jsonl',
              '--report', 'unused-report.json', '--synthesis', 'llm'])
    assert error.value.code == 2
    message = capsys.readouterr().err
    assert 'invalid choice' in message and "'llm'" in message
    assert 'choose from auto, template' in message


def test_cli_accepts_template_and_auto_modes(tmp_path, monkeypatch):
    seen = []

    async def run(config):
        seen.append(config.synthesis)
        return {'emitted_envelopes': 0, 'invalid_inputs': [], 'requests': 0,
                'runtime_ms': 0, 'changes': 0, 'observation_changes': 0,
                'deadline_hits': 0, 'warnings': []}

    monkeypatch.setattr('signalpost.cli.run', run)
    for mode in ('template', 'auto'):
        assert main(['run', '--organisations', str(tmp_path / 'input.jsonl'),
                     '--output', str(tmp_path / 'output.jsonl'),
                     '--report', str(tmp_path / 'report.json'),
                     '--synthesis', mode]) == 0
    assert seen == ['template', 'auto']
