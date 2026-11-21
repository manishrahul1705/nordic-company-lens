import asyncio
import json

import httpx
import pytest
import respx

from signalpost import cli
from signalpost.identity.orgnr import valid
import time
from signalpost import runner
from signalpost.runner import IDENTITY_OUTAGE_SAMPLE, IdentityOutage, run
from tests.test_registry import config, handler

DEFAULT_RECHECK_DELAY = runner.IDENTITY_OUTAGE_RECHECK_DELAY_SECONDS


@pytest.fixture(autouse=True)
def fast_recheck(monkeypatch):
    monkeypatch.setattr(runner, 'IDENTITY_OUTAGE_RECHECK_DELAY_SECONDS', 0.3)


def orgs(count):
    out, n = [], 910000000
    while len(out) < count:
        n += 1
        if valid(str(n)):
            out.append(str(n))
    return out


def outage(request):
    raise httpx.ConnectError("unreachable", request=request)


def scattered(failing):
    ok = handler(missing_accounts=False)
    def response(request):
        path = request.url.path
        if '/enheter/' in path and path.rsplit('/', 1)[-1] in failing:
            raise httpx.ConnectError("unreachable", request=request)
        return ok(request)
    return response


def execute(cfg, response):
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            return await run(cfg, client)
    return asyncio.run(go())


def test_threshold_is_a_named_constant():
    assert IDENTITY_OUTAGE_SAMPLE == 25
    assert {'dns_unavailable', 'dns_timeout', 'dns_error', 'dns_servfail'} <= runner.IDENTITY_NETWORK_CODES


def test_recheck_window_outlasts_a_ten_second_blip():
    assert DEFAULT_RECHECK_DELAY > 10
    assert runner.IDENTITY_OUTAGE_RECHECK_COUNT >= 2


def test_startup_blip_does_not_abort_and_retries_sampled_lookups(tmp_path, monkeypatch):
    # The registry is down from run start until the second pass begins: every attempt,
    # including Http's own retry, fails - a full sample - then it recovers (a blip).
    numbers = orgs(IDENTITY_OUTAGE_SAMPLE + 15)
    ok = handler(missing_accounts=False)
    down, recheck_started = set(), []
    def response(request):
        org = request.url.path.rsplit('/', 1)[-1]
        identity = request.url.path.startswith('/enhetsregisteret/api/enheter/') and org.isdigit()
        if identity and not recheck_started:
            down.add(org)
            raise httpx.ConnectError("blip", request=request)
        return ok(request)
    real_sleep = asyncio.sleep
    async def sleep(delay, *a, **k):
        if delay == runner.IDENTITY_OUTAGE_RECHECK_DELAY_SECONDS:
            await real_sleep(delay, *a, **k); recheck_started.append(1); return
        return await real_sleep(delay, *a, **k)
    monkeypatch.setattr(runner.asyncio, 'sleep', sleep)
    cfg = config(tmp_path, numbers, websites=False, hiring=False, public_activity=False)
    report = execute(cfg, response)
    assert report['run_status'] == 'completed'
    assert report['companies_failed'] == 0
    assert len(down) >= IDENTITY_OUTAGE_SAMPLE and recheck_started  # The blip covered the sample.
    rows = [json.loads(x) for x in cfg.output.read_text(encoding='utf-8').splitlines()]
    assert all(r['modules']['identity']['state'] == 'complete' for r in rows)
    assert all(r['modules']['roles']['state'] == 'complete' for r in rows)


def test_total_identity_outage_aborts_run(tmp_path):
    cfg = config(tmp_path, orgs(IDENTITY_OUTAGE_SAMPLE + 15), websites=False, hiring=False, public_activity=False)
    with pytest.raises(IdentityOutage) as info:
        execute(cfg, outage)
    assert info.value.host == 'data.brreg.no'
    assert 'data.brreg.no' in str(info.value)
    report = json.loads(cfg.report.read_text())
    assert report['run_status'] == 'failed'
    assert any('identity source' in warning for warning in report['warnings'])


def test_cli_exits_non_zero_and_names_host(tmp_path, monkeypatch, capsys):
    async def fake_run(config):
        raise IdentityOutage('data.brreg.no', IDENTITY_OUTAGE_SAMPLE)
    monkeypatch.setattr(cli, 'run', fake_run)
    batch = tmp_path / 'batch.txt'
    batch.write_text('\n'.join(orgs(3)))
    code = cli.main(['run', '--organisations', str(batch), '--output', str(tmp_path / 'e.jsonl'),
                     '--report', str(tmp_path / 'r.json'), '--state-dir', str(tmp_path / 'state')])
    assert code == cli.IDENTITY_OUTAGE_EXIT != 0
    assert 'data.brreg.no' in capsys.readouterr().err


def test_small_batch_dns_outage_aborts_with_report_warning(tmp_path, monkeypatch, capsys):
    from signalpost.budget import SourceFailure

    batch = tmp_path / 'batch.txt'
    batch.write_text('\n'.join(orgs(5)), encoding='utf-8')
    async def dns_failure(org, http):
        raise SourceFailure('dns_unavailable', 'resolver unavailable')
    monkeypatch.setattr(runner.brreg_enhet, 'fetch', dns_failure)
    code = cli.main(['run', '--organisations', str(batch), '--output', str(tmp_path / 'e.jsonl'),
                     '--report', str(tmp_path / 'r.json'), '--state-dir', str(tmp_path / 'state'),
                     '--no-site', '--no-websites', '--no-hiring', '--no-public-activity',
                     '--no-official-extra-sources', '--no-dibk', '--no-group-structure',
                     '--no-signature-rights', '--no-funding-snapshots', '--no-registry-changes'])
    assert code == cli.IDENTITY_OUTAGE_EXIT == 3
    assert 'identity source data.brreg.no unreachable' in capsys.readouterr().err
    report = json.loads((tmp_path / 'r.json').read_text(encoding='utf-8'))
    assert any('identity source data.brreg.no unreachable' in warning for warning in report['warnings'])


def test_small_batch_with_one_success_exits_zero(tmp_path):
    numbers = orgs(5)
    failing = set(numbers[:-1])
    batch = tmp_path / 'batch.txt'
    batch.write_text('\n'.join(numbers), encoding='utf-8')
    with respx.mock(assert_all_called=False) as router:
        router.get(url__regex=r"https://data\.brreg\.no/.*").mock(side_effect=scattered(failing))
        code = cli.main(['run', '--organisations', str(batch), '--output', str(tmp_path / 'e.jsonl'),
                         '--report', str(tmp_path / 'r.json'), '--state-dir', str(tmp_path / 'state'),
                         '--no-site', '--no-websites', '--no-hiring', '--no-public-activity',
                         '--no-official-extra-sources', '--no-dibk', '--no-group-structure',
                         '--no-signature-rights', '--no-funding-snapshots', '--no-registry-changes'])
    assert code == 0
    report = json.loads((tmp_path / 'r.json').read_text(encoding='utf-8'))
    assert report['run_status'] == 'failed'  # Existing per-company failure reporting remains.
    assert report['companies_succeeded'] == 1
    assert report['companies_failed'] == 4
    assert not any('identity source data.brreg.no unreachable' in warning for warning in report['warnings'])


def test_invalid_only_batch_does_not_trip_outage(tmp_path):
    batch = tmp_path / 'batch.txt'
    batch.write_text('not-a-number\n123', encoding='utf-8')
    code = cli.main(['run', '--organisations', str(batch), '--output', str(tmp_path / 'e.jsonl'),
                     '--report', str(tmp_path / 'r.json'), '--state-dir', str(tmp_path / 'state'), '--no-site'])
    assert code == 0
    report = json.loads((tmp_path / 'r.json').read_text(encoding='utf-8'))
    assert report['run_status'] == 'completed'
    assert report['success_rate'] == 0.0
    assert report['invalid_inputs_count'] == 2
    assert report['requests'] == 0


def test_scattered_identity_failures_continue(tmp_path):
    numbers = orgs(IDENTITY_OUTAGE_SAMPLE + 15)
    failing = set(numbers[::3])
    cfg = config(tmp_path, numbers, websites=False, hiring=False, public_activity=False)
    report = execute(cfg, scattered(failing))
    assert report['emitted_envelopes'] == len(numbers)
    assert report['companies_failed'] == len(failing)
    assert report['companies_succeeded'] == len(numbers) - len(failing)
    assert report['source_errors_by_family']['identity'] == len(failing)
    rows = {r['organisation_number']: r for r in map(json.loads, cfg.output.read_text(encoding='utf-8').splitlines())}
    assert all(rows[o]['state'] == 'complete' for o in numbers if o not in failing)
    assert all(rows[o]['modules']['roles']['state'] == 'complete' for o in numbers if o not in failing)
