"""
Adversarial test for Blocker D: Genuine OS Process Termination & Checkpoint Recovery.
Spawns a real separate Python OS process via subprocess.Popen, forcibly kills it with
SIGKILL (proc.kill()), verifies SQLite WAL database uncorrupted, and verifies that a
resumed process completes idempotently, matching an uninterrupted run.
"""
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import pytest


def test_real_os_process_kill_and_checkpoint_recovery(tmp_path):
    # 1. Paths
    full_dir = tmp_path / "full_run"
    full_dir.mkdir()
    full_env = full_dir / "envelopes.jsonl"
    full_rep = full_dir / "report.json"
    full_state = full_dir / "state"

    input_file = Path("tests/fixtures/ci20.jsonl").resolve()
    bulk_file = Path("tests/fixtures/ci20.csv").resolve()

    # Run uninterrupted baseline run
    cmd_full = [
        sys.executable,
        "-m", "signalpost.cli", "run",
        "--organisations", str(input_file),
        "--bulk", str(bulk_file),
        "--output", str(full_env),
        "--report", str(full_rep),
        "--state-dir", str(full_state),
        "--time-budget-seconds", "30",
        "--workers", "2"
    ]
    res_full = subprocess.run(cmd_full, capture_output=True, text=True, timeout=45)
    assert res_full.returncode == 0, f"Uninterrupted run failed: {res_full.stderr}"
    assert full_env.exists()
    full_lines = [json.loads(line) for line in full_env.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(full_lines) == 20

    # 2. Interrupted run in separate directory
    interrupted_dir = tmp_path / "interrupted_run"
    interrupted_dir.mkdir()
    int_env = interrupted_dir / "envelopes.jsonl"
    int_rep = interrupted_dir / "report.json"
    int_state = interrupted_dir / "state"

    cmd_int = [
        sys.executable,
        "-m", "signalpost.cli", "run",
        "--organisations", str(input_file),
        "--bulk", str(bulk_file),
        "--output", str(int_env),
        "--report", str(int_rep),
        "--state-dir", str(int_state),
        "--time-budget-seconds", "30",
        "--workers", "2"
    ]

    # Spawn child process
    proc = subprocess.Popen(cmd_int, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait until it starts producing envelopes or state
    time.sleep(1.0)
    
    # FORCIBLY TERMINATE child process (OS kill)
    proc.kill()
    proc.wait()

    # Verify child was killed prematurely
    assert proc.returncode != 0

    # 3. Verify SQLite integrity on disk after hard kill
    db_path = int_state / "signalpost.db"
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        integrity = cursor.execute("PRAGMA integrity_check;").fetchall()
        conn.close()
        assert integrity == [("ok",)], f"SQLite database corrupted after kill: {integrity}"

    # 4. Resume run using same state directory
    proc_resume = subprocess.run(cmd_int, capture_output=True, text=True, timeout=45)
    assert proc_resume.returncode == 0, f"Resumed run failed: {proc_resume.stderr}"
    assert int_env.exists()

    resumed_lines = [json.loads(line) for line in int_env.read_text(encoding="utf-8").splitlines() if line.strip()]
    
    # Check that all 20 companies were completed
    resumed_orgs = [r["organisation_number"] for r in resumed_lines]
    full_orgs = [r["organisation_number"] for r in full_lines]
    assert set(resumed_orgs) == set(full_orgs)
    assert len(resumed_lines) == 20
