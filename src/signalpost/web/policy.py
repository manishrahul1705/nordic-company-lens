import asyncio
import ipaddress
import re
import socket
from contextvars import ContextVar
from urllib.parse import urlsplit, urlunsplit
import httpx
import tldextract
import dns.asyncresolver
from httpcore._backends.auto import AutoBackend
from ..budget import SourceFailure

extract = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None, include_psl_private_domains=True)
DNS_ORG = ContextVar('signalpost_dns_org', default='__shared__')
class DNSFallbackBudget:
    """Serialize and cap best-effort public DNS fallback time per company/run."""
    def __init__(self):
        self.elapsed_by_company = {}
        self.attempts_by_company = {}
        self.successful_domains_by_company = {}
        self.nxdomain_candidates_by_company = {}
        self.nxdomain_cache = {}
        self._locks = {}

    def register_nxdomain_candidate(self, company, host):
        candidates = self.nxdomain_candidates_by_company.setdefault(company, set())
        if host in candidates:
            return True
        if len(candidates) >= 3:
            return False
        candidates.add(host)
        return True

    def metrics(self):
        elapsed = sum(self.elapsed_by_company.values())
        return {'dns_fallback_attempts': sum(self.attempts_by_company.values()),
                'dns_fallback_successes': sum(len(hosts) for hosts in self.successful_domains_by_company.values()),
                'dns_fallback_seconds': round(elapsed, 3),
                'dns_fallback_max_seconds_per_company': round(max(self.elapsed_by_company.values(), default=0), 3),
                'dns_fallback_companies': len(self.attempts_by_company)}

    async def resolve(self, host, port, failure):
        company = DNS_ORG.get()
        lock = self._locks.setdefault(company, asyncio.Lock())
        async with lock:
            cache_key = (company, host)
            if failure.code == 'no_such_domain':
                if host not in self.nxdomain_candidates_by_company.get(company, set()):
                    raise failure
                if cache_key in self.nxdomain_cache:
                    cached = self.nxdomain_cache[cache_key]
                    if cached:
                        return list(cached)
                    raise failure
            remaining = max(0.0, 4.0 - self.elapsed_by_company.get(company, 0.0))
            if remaining <= 0.01:
                raise failure
            started = asyncio.get_running_loop().time()
            self.attempts_by_company[company] = self.attempts_by_company.get(company, 0) + 1
            answers = []
            try:
                remaining = max(0.0, 4.0 - self.elapsed_by_company.get(company, 0.0))
                if failure.code == 'no_such_domain':
                    servers = ('1.1.1.1',)
                    per_resolver = min(1.0, remaining)
                else:
                    servers = ('1.1.1.1', '8.8.8.8')
                    per_resolver = min(DNS_FALLBACK_RESOLVER_TIMEOUT_SECONDS, remaining)
                resolvers = []
                for server in servers:
                    resolver = dns.asyncresolver.Resolver(configure=False)
                    resolver.nameservers = [server]
                    resolver.timeout = per_resolver
                    resolver.lifetime = per_resolver
                    resolvers.append(resolver)
                async def query(resolver):
                    async with asyncio.timeout(per_resolver):
                        return await asyncio.gather(*(
                            resolver.resolve(host, record_type, raise_on_no_answer=False,
                                             search=False, lifetime=per_resolver)
                            for record_type in ('A', 'AAAA')), return_exceptions=True)
                results_by_resolver = await asyncio.gather(*(query(r) for r in resolvers), return_exceptions=True)
                for results in results_by_resolver:
                    if isinstance(results, Exception):
                        continue
                    for result in results:
                        if not isinstance(result, Exception):
                            answers.extend(str(item) for item in result)
                if answers:
                    checked = check_ips(list(dict.fromkeys(answers)))
                    self.successful_domains_by_company.setdefault(company, set()).add(host)
                    if failure.code == 'no_such_domain':
                        self.nxdomain_cache[cache_key] = tuple(checked)
                    return checked
                if failure.code == 'no_such_domain':
                    self.nxdomain_cache[cache_key] = None
                raise failure
            finally:
                elapsed = asyncio.get_running_loop().time() - started
                self.elapsed_by_company[company] = min(4.0, self.elapsed_by_company.get(company, 0.0) + elapsed)


DNS_FALLBACK_STATE = ContextVar('signalpost_dns_fallback_state', default=None)
DNS_FALLBACK_RESOLVER_TIMEOUT_SECONDS = 2.0
SOCIAL = {"facebook.com", "instagram.com", "linkedin.com", "x.com", "twitter.com", "youtube.com", "tiktok.com"}
DIRECTORIES = {"proff.no", "proff.com", "proff.dk", "proff.se", "gulesider.no", "1881.no", "purehelp.no", "finn.no", "fb.me", "fb.com", "youtu.be", "lnkd.in", "t.co", "threads.net"}
# These services reproduce registry identity/contact data; a matching company
# entry is not evidence that the company owns the service's website.
DIRECTORIES |= {"utdanning.no", "vat-validation.com", "nordlei.no"}
FREE_MAIL = {"gmail.com", "googlemail.com", "hotmail.com", "hotmail.no", "outlook.com", "live.com", "live.no", "yahoo.com", "yahoo.no", "online.no", "icloud.com", "me.com", "protonmail.com", "proton.me", "aol.com", "msn.com", "mail.com"}
FREE_MAIL |= {'outlook.no', 'hotmail.co.uk', 'outlook.co.uk', 'yahoo.co.uk',
              'yahoo.fr', 'ymail.com', 'mac.com', 'getmail.no', 'start.no',
              'broadpark.no', 'frisurf.no', 'chello.no', 'telenor.no'}


def domain(url):
    host = (urlsplit(url if "://" in url else "https://" + url).hostname or "").lower().rstrip(".")
    result = extract(host)
    return result.top_domain_under_public_suffix


def normalize_url(value):
    value = str(value or "").strip()
    if not value:
        return None
    parts = urlsplit(value if "://" in value else "https://" + value)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        return None
    try:
        if parts.port not in (None, 80, 443):
            return None
        host = parts.hostname.encode("idna").decode("ascii").lower().rstrip(".")
        if not extract(host).suffix:
            return None
    except (ValueError, UnicodeError):
        return None
    port = f":{parts.port}" if parts.port and parts.port != (443 if parts.scheme == "https" else 80) else ""
    return urlunsplit((parts.scheme, host + port, parts.path or "/", "", ""))


def is_directory_record(url):
    """An LEI lookup record identifies a registry entry, not an owned site."""
    return bool(re.search(r'/lei/[a-z0-9]{20}(?:/|$)', urlsplit(url).path, re.I))


def validate_url(url, domains):
    normalized = normalize_url(url)
    if normalized is None or domain(normalized) not in domains or domain(normalized) in SOCIAL | DIRECTORIES or is_directory_record(normalized):
        raise SourceFailure("url_refused", "URL lies outside this company's permitted candidate domains")
    return normalized


def check_ips(ips):
    if not ips:
        raise SourceFailure("no_such_domain")
    for value in ips:
        address = ipaddress.ip_address(value)
        if not address.is_global or address.is_multicast or address.is_reserved or address.is_unspecified:
            raise SourceFailure("ssrf", "Destination is not a public unicast address")
    return ips


async def resolve_public(host, port=443):
    failure = None
    try:
        records = await asyncio.wait_for(asyncio.get_running_loop().getaddrinfo(host, port, type=socket.SOCK_STREAM), timeout=8)
    except asyncio.TimeoutError as exc:
        failure = SourceFailure("dns_timeout"); failure.__cause__ = exc
    except socket.gaierror as exc:
        if exc.errno in {socket.EAI_NONAME, getattr(socket, 'EAI_NODATA', socket.EAI_NONAME)}:
            failure = SourceFailure("no_such_domain")
        elif exc.errno in {socket.EAI_AGAIN, 11002}:
            failure = SourceFailure('dns_servfail')
        else:
            failure = SourceFailure("dns_error")
        failure.__cause__ = exc
    except OSError as exc:
        failure = SourceFailure("dns_error"); failure.__cause__ = exc
    else:
        return check_ips(list(dict.fromkeys(item[4][0] for item in records)))

    if failure.code not in {'dns_timeout', 'dns_servfail', 'no_such_domain'}:
        raise failure
    state = DNS_FALLBACK_STATE.get()
    if state is None:
        state = DNSFallbackBudget()
    return await state.resolve(host, port, failure)


class PublicNetworkBackend:
    """Validate at connection time and pin TCP to the vetted IP; TLS keeps SNI."""
    def __init__(self, dns_metrics=None):
        self.backend = AutoBackend()
        self.dns_metrics = dns_metrics

    async def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        if isinstance(host, bytes):
            host = host.decode("ascii")
        if port not in (80, 443):
            raise SourceFailure("ssrf", "Non-web port refused")
        if self.dns_metrics is not None:
            self.dns_metrics['dns_lookups'] = self.dns_metrics.get('dns_lookups', 0) + 1
            by_org = self.dns_metrics.setdefault('dns_by_company', {})
            org = DNS_ORG.get();by_org[org] = by_org.get(org, 0) + 1
        connect_timeout = timeout.get('connect_timeout') if isinstance(timeout, dict) else timeout
        if not isinstance(connect_timeout, (int, float)) or connect_timeout <= 0:
            connect_timeout = 8.0
        async with asyncio.timeout(connect_timeout):
            ips = await resolve_public(host, port)
        ips.sort(key=lambda ip: ipaddress.ip_address(ip).version)
        last = None
        for ip in ips:
            try:
                return await self.backend.connect_tcp(ip, port, timeout, local_address, socket_options)
            except Exception as exc:
                last = exc
        raise last

    async def connect_unix_socket(self, *args, **kwargs):
        raise SourceFailure("ssrf", "Unix sockets refused")

    async def sleep(self, seconds):
        await self.backend.sleep(seconds)


def safe_transport(max_connections, dns_metrics=None):
    transport = httpx.AsyncHTTPTransport(limits=httpx.Limits(max_connections=max_connections, max_keepalive_connections=max_connections))
    # The locked httpx/httpcore versions expose this connection backend. DNS is
    # checked again here, so preflight checks cannot be bypassed by rebinding.
    transport._pool._network_backend = PublicNetworkBackend(dns_metrics)
    return transport
