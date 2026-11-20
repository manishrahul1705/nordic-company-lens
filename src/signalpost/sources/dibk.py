"""Bounded DiBK enterprise-page observations; never API, search or link crawling."""
import asyncio
from datetime import datetime
from html import unescape
import re
import time
from urllib.robotparser import RobotFileParser

import httpx
from ..budget import SourceFailure
from ..models.evidence import digest, utc_now
from ..workers import offload
from .extract import Section, Source, add
from .http import Response

HOST = 'sgregister.dibk.no'
ORIGIN = 'https://' + HOST
METHOD = 'signalpost.dibk.enterprise-html.v1'


def selected(envelope):
    if envelope.run.sections.get('identity') != 'available':
        return False
    codes = [c.value.get('kode', '') for c in envelope.claims
             if c.field in {'identity.nace1', 'identity.nace2', 'identity.nace3'}
             and c.availability == 'available' and not c.carried_forward
             and c.evidence_ids and isinstance(c.value, dict)]
    return any(isinstance(code, str) and re.fullmatch(r'(?:4[123]\.\d{3}|71\.[12]\d{2})', code) for code in codes)


def plain(markup):
    return ' '.join(unescape(re.sub(r'<[^>]+>', ' ', markup)).split())


def extract(response, org):
    section = Section()
    if response.status != 200 or response.url != ORIGIN + '/enterprises/' + org:
        return section
    raw = response.body.decode('utf-8', errors='strict')
    # Bind to the labelled enterprise identity, not an incidental number in a footer.
    identity = re.search(r'<b\b[^>]*>\s*Organisasjonsnummer\s*</b>\s*<p\b[^>]*>\s*([0-9]{9})\s*</p>', raw)
    if not identity or identity[1] != org:
        return section
    period = re.search(r'Godkjenningsperiode:\s*</b>\s*<span\b[^>]*>(.*?)</span>', raw, re.S)
    dates = re.fullmatch(r'(\d{2}\.\d{2}\.\d{4})\s*[–-]\s*(\d{2}\.\d{2}\.\d{4})', plain(period[1])) if period else None
    if not dates:
        return section
    try:
        start, end = [datetime.strptime(x, '%d.%m.%Y').date() for x in dates.groups()]
        observed = datetime.fromisoformat(response.retrieved_at.replace('Z', '+00:00')).date()
    except ValueError:
        return section
    if start > end:
        return section
    # Current status requires both the page's explicit statement and valid dates.
    current = re.search(r'<h3\b[^>]*>\s*Foretaket har sentral godkjenning\s*</h3>', raw)
    expired = re.search(r'<h[1-6]\b[^>]*>[^<]*(?:utløpt|ikke lenger gyldig)[^<]*</h[1-6]>', raw, re.I)
    if current and start <= observed <= end:
        status, status_span = 'approved', current[0]
    elif end < observed and expired:
        status, status_span = 'expired', expired[0]
    else:
        return section
    source = Source(response.url, response.body, response.sha, response.retrieved_at,
                    'Direktoratet for byggkvalitet; live enterprise-page observation')
    seen = set()
    for table_index, table in enumerate(re.findall(r'<table\b[^>]*>.*?</table>', raw, re.S)):
        header = re.search(r'<thead\b[^>]*>(.*?)</thead>', table, re.S)
        if not header or [plain(x) for x in re.findall(r'<th\b[^>]*>(.*?)</th>', header[1], re.S)][:3] != ['Funksjon', 'Fagområde', 'Tiltaksklasse']:
            continue
        for row_index, row in enumerate(re.findall(r'<tr\b[^>]*>.*?</tr>', table, re.S)):
            cells = re.findall(r'<td\b[^>]*>.*?</td>', row, re.S)
            if len(cells) < 3:
                continue
            function, area, klass = map(plain, cells[:3])
            if not function or not area or klass not in {'1', '2', '3'}:
                continue
            key = (function, area, klass)
            if key in seen:
                continue
            seen.add(key)
            v = {'organisation_number': org, 'area': area, 'class': klass, 'function': function,
                 'valid_from': dates[1], 'valid_to': dates[2], 'status': status,
                 'date_format': 'DD.MM.YYYY', 'source_url': response.url}
            field = 'central_approval.' + digest(list(key))[:24]
            locator = '/table/' + str(table_index) + '/row/' + str(row_index)
            # One bounded verbatim span per asserted source cell, identity, period and status.
            spans = [identity[0], period[0], status_span, *cells[:3]]
            if any(len(span) > 300 for span in spans):
                continue
            for i, span in enumerate(spans):
                proof = Section()
                add(proof, source, org, 'certification', field, v, locator + '/support/' + str(i),
                    span=span, source_class='official_registry', method=METHOD)
                section.evidence.extend(proof.evidence)
                if i == 0:
                    claim = proof.claims[0]
                    claim.reasons.update(label='DiBK sentral godkjenning: ' + area,
                        attribution='Direktoratet for byggkvalitet', observation='Status as stated at retrieval; recheck before reliance')
                    section.claims.append(claim)
                else:
                    claim.evidence_ids.extend(proof.claims[0].evidence_ids)
    return section


class Collector:
    def __init__(self, client, config, budget, blobs):
        self.client, self.config, self.budget, self.blobs = client, config, budget, blobs
        self.semaphore = asyncio.Semaphore(2)
        self.lock = asyncio.Lock(); self.next_start = 0
        self.robots_lock = asyncio.Lock(); self.robots = None
        self.robots_failure = None
        self.tasks = []; self.queried = set(); self.started = time.monotonic()
        self.completed_at = None
        self.stop_reason = 'deadline'

    async def request(self, path, org):
        if path != '/robots.txt' and path != '/enterprises/' + org:
            raise SourceFailure('dibk_url_refused')
        url = ORIGIN + path
        async with self.semaphore:
            async with self.lock:
                await asyncio.sleep(max(0, self.next_start - time.monotonic()))
                self.budget.check()
                self.next_start = time.monotonic() + self.config.website_politeness_seconds
            event = self.budget.reserve(url, HOST, org)
            event['section'] = 'dibk'; began = time.monotonic()
            try:
                timeout = min(self.config.request_timeout, max(.001, self.budget.deadline - time.monotonic()))
                async with asyncio.timeout(timeout), self.client.stream('GET', url, headers={'User-Agent': self.config.website_user_agent,
                    'Accept': 'text/plain' if path == '/robots.txt' else 'text/html'},
                    timeout=timeout, follow_redirects=False) as r:
                    event['status'] = r.status_code
                    chunks = []; size = 0
                    async for chunk in r.aiter_bytes():
                        size += len(chunk)
                        if size > 2 * 1024 * 1024:
                            raise SourceFailure('body_cap')
                        chunks.append(chunk)
                    body = b''.join(chunks)
                    if r.status_code == 200 and r.headers.get('content-type', '').split(';')[0] not in {'text/html', 'text/plain'}:
                        raise SourceFailure('content_type')
                    sha = await offload(self.blobs.put, body); event['content_sha256'] = sha
                    return Response(body, r.status_code, url, utc_now(), sha)
            except (httpx.HTTPError, TimeoutError, SourceFailure) as exc:
                event['error'] = exc.code if isinstance(exc, SourceFailure) else type(exc).__name__
                raise
            except asyncio.CancelledError:
                event['error'] = self.stop_reason; raise
            finally:
                self.next_start = max(self.next_start, time.monotonic() + self.config.website_politeness_seconds)
                event['runtime_ms'] = round((time.monotonic() - began) * 1000)

    async def allowed(self, org):
        async with self.robots_lock:
            if self.robots_failure is not None:
                raise SourceFailure('robots_unavailable', self.robots_failure)
            if self.robots is None:
                # One shared, budgeted robots request; never attributed to a fake input company.
                try:
                    response = await self.request('/robots.txt', '__dibk_robots__')
                except (httpx.HTTPError, TimeoutError, SourceFailure) as exc:
                    self.robots_failure = str(exc)
                    raise
                if response.status != 200:
                    self.robots_failure = 'HTTP ' + str(response.status)
                    raise SourceFailure('robots_unavailable')
                parser = RobotFileParser(ORIGIN + '/robots.txt')
                try:
                    parser.parse(response.body.decode('utf-8').splitlines())
                except (UnicodeError, ValueError) as exc:
                    self.robots_failure = str(exc)
                    raise SourceFailure('robots_unavailable') from exc
                self.robots = parser
            if not self.robots.can_fetch(self.config.website_user_agent, ORIGIN + '/enterprises/' + org):
                raise SourceFailure('robots')

    def schedule(self, row):
        if not selected(row) or row.organisation_number in self.queried:
            return
        self.queried.add(row.organisation_number)
        self.tasks.append(asyncio.create_task(self.collect(row)))

    async def collect(self, row):
        org = row.organisation_number
        diagnostic = {'selected': True, 'requests': 0}
        row.run.refresh['dibk'] = diagnostic
        try:
            await self.allowed(org)
            response = await self.request('/enterprises/' + org, org)
            section = await offload(extract, response, org)
            diagnostic.update(http_status=response.status, claims=len(section.claims),
                state='available' if section.claims else 'not_found' if response.status == 404 else 'not_established' if response.status == 200 else 'fetch_failed')
            row.claims.extend(section.claims); row.evidence.extend(section.evidence)
        except (httpx.HTTPError, TimeoutError, SourceFailure, ValueError) as exc:
            diagnostic.update(state='fetch_failed', reason=exc.code if isinstance(exc, SourceFailure) else type(exc).__name__)
        except asyncio.CancelledError:
            diagnostic.update(state='fetch_failed', reason=self.stop_reason); raise
        finally:
            diagnostic['requests'] = sum(e.get('host') == HOST and e['organisation_number'] == org for e in self.budget.events)
            self.completed_at = time.monotonic()

    async def finish(self, max_wait=60):
        if self.tasks:
            remaining = max(.001, self.budget.deadline - time.monotonic())
            self.stop_reason = 'dibk_tail_timeout' if max_wait < remaining else 'deadline'
            try:
                async with asyncio.timeout(min(max_wait, remaining)):
                    await asyncio.gather(*self.tasks)
            except TimeoutError:
                pass

    async def cancel(self):
        for task in self.tasks:
            if not task.done(): task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
