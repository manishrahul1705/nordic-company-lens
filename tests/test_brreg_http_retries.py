import asyncio
import time
from types import SimpleNamespace

import httpx
import pytest

from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Http


ORG = "123456789"


class RecordingBudget:
    def __init__(self):
        self.deadline = time.monotonic() + 30
        self.events = []

    def check(self):
        assert time.monotonic() < self.deadline

    def reserve(self, url, host, org):
        event = {"url": url, "host": host, "organisation_number": org}
        self.events.append(event)
        return event


def make_http(tmp_path, transport, budget):
    config = SimpleNamespace(host_concurrency=1, request_timeout=5)
    client = httpx.AsyncClient(transport=transport)
    http = Http(client, config, budget, BlobStore(tmp_path / "blobs"))
    return client, http


def test_network_error_retry_uses_one_to_two_second_jitter(tmp_path, monkeypatch):
    attempts = 0
    waits = []

    def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ConnectError("synthetic transport failure", request=request)
        return httpx.Response(200, content=b"ok")

    async def sleep(delay):
        waits.append(delay)

    monkeypatch.setattr("signalpost.sources.http.asyncio.sleep", sleep)
    budget = RecordingBudget()
    client, http = make_http(tmp_path, httpx.MockTransport(handler), budget)
    try:
        response = asyncio.run(http.get(f"https://data.brreg.no/enhetsregisteret/api/enheter/{ORG}", ORG))
    finally:
        asyncio.run(client.aclose())

    assert response.status == 200
    assert attempts == 2
    assert len(budget.events) == 2
    assert len(waits) == 1 and 1.0 <= waits[0] <= 2.0


def test_timeout_retry_keeps_original_backoff(tmp_path, monkeypatch):
    attempts = 0
    waits = []

    def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ConnectTimeout("synthetic timeout", request=request)
        return httpx.Response(200, content=b"ok")

    async def sleep(delay):
        waits.append(delay)

    monkeypatch.setattr("signalpost.sources.http.asyncio.sleep", sleep)
    budget = RecordingBudget()
    client, http = make_http(tmp_path, httpx.MockTransport(handler), budget)
    try:
        response = asyncio.run(http.get(f"https://data.brreg.no/enhetsregisteret/api/enheter/{ORG}", ORG))
    finally:
        asyncio.run(client.aclose())

    assert response.status == 200
    assert attempts == 2
    assert len(waits) == 1 and 0.1 <= waits[0] <= 0.3
    assert len(budget.events) == 2


@pytest.mark.parametrize(
    "url,expected_attempts",
    [
        (f"https://data.brreg.no/enhetsregisteret/api/enheter/{ORG}", 2),
        (f"https://data.brreg.no/regnskapsregisteret/api/regnskap/{ORG}", 3),
        (f"https://data.brreg.no/api/oppdateringer/enheter?organisasjonsnummer={ORG}", 1),
    ],
)
def test_retry_attempt_counts_and_budget_reservations_unchanged(
    tmp_path, monkeypatch, url, expected_attempts
):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts < expected_attempts:
            return httpx.Response(503, headers={"Retry-After": "0"}, content=b"retry")
        return httpx.Response(200, content=b"ok")

    async def sleep(_delay):
        return None

    monkeypatch.setattr("signalpost.sources.http.asyncio.sleep", sleep)
    budget = RecordingBudget()
    client, http = make_http(tmp_path, httpx.MockTransport(handler), budget)
    try:
        response = asyncio.run(http.get(url, ORG))
    finally:
        asyncio.run(client.aclose())

    assert response.status == 200
    assert attempts == expected_attempts
    assert len(budget.events) == expected_attempts
