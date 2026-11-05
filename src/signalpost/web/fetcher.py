from ..workers import offload
import asyncio
import time
import ssl
from dataclasses import dataclass, replace
from urllib.parse import urlsplit, urljoin, urlunsplit
from urllib.robotparser import RobotFileParser
import httpx
from ..budget import SourceFailure
from ..models.evidence import utc_now
from ..sources.http import Response
from . import policy


def transport_failure_code(exc):
    """TLS requires actual TLS evidence; a generic ConnectError is not enough."""
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        message = str(exc).casefold()
        if isinstance(exc, ssl.SSLError) or any(marker in message for marker in
                ('certificate verify failed', 'certificate_verify_failed', 'tls', '[ssl:')):
            return 'website_tls_error'
        exc = exc.__cause__ or exc.__context__
    return 'website_connect_error'


@dataclass
class DomainGate:
    semaphore: asyncio.Semaphore
    start_lock: asyncio.Lock
    next_start: float = 0


class WebsiteHttp:
    def __init__(self, client, config, budget, blobs, resolver=None, dns_metrics=None):
        self.client, self.config, self.budget, self.blobs = client, config, budget, blobs
        self.resolver = resolver
        self.counts = {}
        self.gates = {}
        self.robots = {}
        self.robot_locks = {}
        self.attempts = {}
        self.dns_cache = {}
        self.dns_locks = {}
        self.dns_counts = {}
        self.dns_lookups = 0
        self.activity_extra = set()
        self.accepted_pages = {}
        self.dns_metrics = dns_metrics

    async def resolve(self, host, port, org):
        if self.dns_metrics is not None:
            self.dns_metrics['dns_lookups'] = self.dns_metrics.get('dns_lookups', 0) + 1
            by_org = self.dns_metrics.setdefault('dns_by_company', {})
            by_org[org] = by_org.get(org, 0) + 1
        return await (self.resolver or policy.resolve_public)(host, port)

    async def precheck(self, candidate, org):
        if candidate.origin == 'registry_website' or not self.config.dns_precheck:
            return
        host = urlsplit(candidate.url).hostname
        dns_cap = 74 if candidate.origin == 'search_brave' else 64
        if self.dns_counts.get(org, 0) >= dns_cap:
            raise SourceFailure('dns_unavailable')
        self.dns_counts[org] = self.dns_counts.get(org, 0) + 1
        lock = self.dns_locks.setdefault(host, asyncio.Lock())
        async with lock:
            if host not in self.dns_cache:
                self.budget.check()
                self.dns_lookups += 1
                try:
                    ips = await asyncio.wait_for(self.resolve(host, 443, org), timeout=min(3, max(.001, self.budget.deadline-time.monotonic())))
                    self.dns_cache[host] = policy.check_ips(ips)
                except (TimeoutError, OSError):
                    self.dns_cache[host] = 'dns_unavailable'
                except SourceFailure as exc:
                    self.dns_cache[host] = exc.code if exc.code in {'no_such_domain', 'ssrf'} else 'dns_unavailable'
            result = self.dns_cache[host]
            if isinstance(result, str):
                raise SourceFailure(result)
            policy.check_ips(result)

    async def raw(self, url, org, domains, xml=False, obey_robots=False, allow_redirects=False):
        domains = set(domains)
        url = policy.validate_url(url, domains)
        for hop in range(4):
            parts = urlsplit(url)
            if obey_robots:
                await self.ensure_robots(url, org, domains, allow_redirects=allow_redirects)
            policy.check_ips(await self.resolve(parts.hostname, parts.port or (443 if parts.scheme == "https" else 80), org))
            root = policy.domain(url)
            gate = self.gates.setdefault(root, DomainGate(asyncio.Semaphore(2), asyncio.Lock()))
            async with gate.semaphore:
                async with gate.start_lock:
                    while (delay := gate.next_start - time.monotonic()) > 0:
                        await asyncio.sleep(delay)
                    self.budget.check()
                    gate.next_start = time.monotonic() + self.config.website_politeness_seconds
                registry_requests = sum(e['organisation_number']==org and e.get('section')!='website' for e in self.budget.events)
                company_cap = min(self.config.website_request_cap + int(org in self.activity_extra),max(0,self.config.website_total_request_cap-registry_requests))
                if self.counts.get(org, 0) >= company_cap:
                    raise SourceFailure("website_budget_exhausted")
                event = self.budget.reserve(url, parts.hostname, org)
                event["section"] = "website"
                self.counts[org] = self.counts.get(org, 0) + 1
                began = time.monotonic()
                response = None
                chunks = []
                try:
                    remaining = self.budget.deadline - time.monotonic()
                    async with asyncio.timeout(min(8, max(.001, remaining))):
                        async with self.client.stream("GET", url, headers={"User-Agent": self.config.website_user_agent, "Accept": "application/xml,text/xml,application/rss+xml,application/atom+xml" if xml else "text/html,application/xhtml+xml,text/plain"}, timeout=min(8, max(.001, remaining)), follow_redirects=False) as stream:
                            chunks = []
                            size = 0
                            event["status"] = stream.status_code
                            async for chunk in stream.aiter_bytes():
                                size += len(chunk)
                                if size > 2 * 1024 * 1024:
                                    event["error"] = "body_cap"
                                    partial = (b"".join(chunks) + chunk)[:2 * 1024 * 1024]
                                    event["content_sha256"] = await offload(self.blobs.put,partial)
                                    event["truncated"] = True
                                    raise SourceFailure("body_cap")
                                chunks.append(chunk)
                            body = b"".join(chunks)
                            sha = await offload(self.blobs.put,body)
                            event["content_sha256"] = sha
                            response = Response(body, stream.status_code, url, utc_now(), sha)
                            content_type = stream.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                            if stream.is_redirect:
                                if hop == 3:
                                    raise SourceFailure("redirect_limit")
                                target = urljoin(url, stream.headers.get("location", ""))
                                if allow_redirects:
                                    domains.add(policy.domain(target))
                                url = policy.validate_url(target, domains)
                                continue
                            permitted = {"text/html", "application/xhtml+xml", "text/plain"}
                            if xml:
                                permitted |= {"application/xml", "text/xml", "application/rss+xml", "application/atom+xml"}
                            if stream.status_code == 200 and content_type not in permitted:
                                raise SourceFailure("content_type", content_type)
                            return response
                except (TimeoutError, httpx.TimeoutException) as exc:
                    event["error"] = type(exc).__name__
                    raise SourceFailure("website_timeout") from exc
                except (httpx.NetworkError, httpx.ProtocolError) as exc:
                    event["error"] = type(exc).__name__
                    code = transport_failure_code(exc)
                    event["failure_code"] = code
                    raise SourceFailure(code) from exc
                except asyncio.CancelledError:
                    event["error"] = "deadline"
                    raise
                finally:
                    # Completion-based spacing is conservative and avoids starts
                    # being less than one second apart due to transport overhead.
                    gate.next_start = max(gate.next_start, time.monotonic() + self.config.website_politeness_seconds)
                    if chunks and "content_sha256" not in event:
                        event["content_sha256"] = await offload(self.blobs.put,b"".join(chunks)[:2 * 1024 * 1024])
                        event["truncated"] = True
                    event["runtime_ms"] = round((time.monotonic() - began) * 1000)

    async def ensure_robots(self, url, org, domains, allow_redirects=False):
        p = urlsplit(url)
        origin = urlunsplit((p.scheme, p.netloc, "", "", ""))
        lock = self.robot_locks.setdefault(origin, asyncio.Lock())
        async with lock:
            if origin not in self.robots:
                response = await self.raw(origin + "/robots.txt", org, domains, allow_redirects=allow_redirects)
                parser = RobotFileParser(origin + "/robots.txt")
                if response.status in (404, 410):
                    parser.parse([])
                elif response.status == 200:
                    await offload(parser.parse,response.body.decode("utf8",errors="replace").splitlines())
                else:
                    if response.status >= 500:
                        raise SourceFailure('website_http_5xx')
                    raise SourceFailure("robots_unavailable", f"HTTP {response.status}")
                self.robots[origin] = parser
                final = urlsplit(response.url)
                self.robots[urlunsplit((final.scheme, final.netloc, "", "", ""))] = parser
            if not await offload(self.robots[origin].can_fetch,self.config.website_user_agent,url):
                raise SourceFailure("robots")

    async def get(self, url, org, candidate_domain, proven=(), xml=False, allow_redirects=False):
        domains = {candidate_domain, *proven}
        # Robots are checked again on the effective redirect authority. raw()
        # can follow only already permitted domains; content is not extracted
        # until the final authority's policy has also been checked.
        return await self.raw(url, org, domains, xml, obey_robots=True, allow_redirects=allow_redirects)

    def discovery_cap(self, org):
        """Original per-company ceiling (6, within a total of 9 with registry calls).

        Sitemap/feed guessing for other domains keeps it; the larger cap is for proof pages.
        """
        registry_requests = sum(e['organisation_number'] == org and e.get('section') != 'website' for e in self.budget.events)
        return min(6, max(0, 9 - registry_requests))

    async def candidate(self, candidate, org, proven=()):
        """Try HTTPS apex/www, then HTTP www/apex after a transport failure.

        Redirect targets are nominations only. The collector proves ownership
        on the final host; public-IP, robots and request limits still apply.
        """
        p = urlsplit(candidate.url)
        host = p.hostname[4:] if p.hostname.startswith('www.') else p.hostname
        trials = [('https', host), ('https', 'www.' + host),
                  ('http', 'www.' + host), ('http', host)]
        notes = self.attempts.setdefault(org, [])
        transport_errors = {'website_tls_error', 'website_connect_error', 'website_timeout',
                            'dns_timeout', 'dns_error', 'dns_unavailable', 'no_such_domain'}
        stop_errors = {'robots', 'robots_unavailable', 'block_page', 'ssrf', 'url_refused',
                       'budget_exhausted', 'website_budget_exhausted', 'deadline'}
        failed_transport = False
        last = None
        for position, (scheme, authority) in enumerate(trials):
            # A normal HTTP response from the apex (including 4xx/5xx) does
            # not trigger transport fallback. The www/HTTP sequence is for
            # apex transport failures such as TLS, connection or DNS errors.
            if position == 1 and not failed_transport:
                break
            if scheme == 'http' and not failed_transport:
                break
            target = urlunsplit((scheme, authority, p.path or '/', '', ''))
            try:
                await self.precheck(replace(candidate, url=target), org)
                response = await self.get(target, org, candidate.domain, proven, allow_redirects=True)
                notes.append({'domain':candidate.domain,'origin':candidate.origin,'url':target,
                              'final_url':response.url,'status':response.status})
                if 200 <= response.status < 300 or response.status in {401,403,429}:
                    return response
                last = SourceFailure('website_http_5xx' if response.status >= 500 else 'http_' + str(response.status))
            except SourceFailure as exc:
                notes.append({'domain':candidate.domain,'origin':candidate.origin,'url':target,'reason':exc.code})
                last = exc
                if exc.code in stop_errors:
                    raise
                failed_transport |= exc.code in transport_errors
        raise last or SourceFailure('no_such_domain')
