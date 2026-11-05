"""Retry a seeded sample of saved HTTPS transport failures with three trust stacks.

No search, tokens, redirects, certificate bypasses, or response bodies are used.
Run with: uv run --with truststore python scripts/diagnose_website_tls.py --run ... --output ...
"""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import random
import ssl
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import certifi
import httpx

from signalpost.web.policy import PublicNetworkBackend, resolve_public
from bench_run import benchmark_environment


def exceptions(exc):
    chain, seen = [], set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        chain.append({'class': type(exc).__module__ + '.' + type(exc).__qualname__,
                      'message': str(exc), 'repr': repr(exc)})
        exc = exc.__cause__ or exc.__context__
    return chain


def category(result):
    if result.get('transport_success'):
        return 'HTTP response'
    message = json.dumps(result.get('exceptions', [])) + result.get('stderr', '')
    text = message.lower()
    if any(s in text for s in ('sslcertverificationerror', 'certificate_verify_failed', 'cert_e_',
                              'sec_e_untrusted_root', 'sec_e_wrong_principal', 'sec_e_cert_expired',
                              'certificate verify failed')):
        return 'certificate verification'
    if any(s in text for s in ('getaddrinfo', 'could not resolve', 'no_such_domain', 'dns_')):
        return 'DNS'
    if 'timeout' in text or 'timed out' in text or result.get('exit_code') == 28:
        return 'timeout'
    if any(s in text for s in ('ssl', 'tls', 'schannel')):
        return 'other TLS'
    return 'connection/protocol'


async def python_retry(url, mode):
    import truststore
    # The default and explicit certifi arms are independent repeated controls.
    context = (truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if mode == 'truststore'
               else ssl.create_default_context(cafile=certifi.where()))
    transport = httpx.AsyncHTTPTransport(verify=context, retries=0)
    transport._pool._network_backend = PublicNetworkBackend()
    try:
        async with httpx.AsyncClient(transport=transport, trust_env=False, follow_redirects=False) as client:
            async with asyncio.timeout(8):
                async with client.stream('GET', url, headers={'User-Agent': 'NordicCompanyLensTLSDiagnostic/1.0'}, timeout=8) as response:
                    return {'transport_success': True, 'http_status': response.status_code,
                            'http_2xx': 200 <= response.status_code < 300}
    except Exception as exc:
        return {'transport_success': False, 'exceptions': exceptions(exc)}


async def curl_retry(url):
    parts = urlsplit(url)
    try:
        ips = await resolve_public(parts.hostname, 443)
        ip = sorted(ips, key=lambda value: ':' in value)[0]
        pin = f'{parts.hostname}:443:' + (f'[{ip}]' if ':' in ip else ip)
        process = await asyncio.create_subprocess_exec(
            'curl.exe', '-q', '--noproxy', '*', '--resolve', pin,
            '--connect-timeout', '8', '--max-time', '8', '--max-redirs', '0',
            '-sS', '-o', 'NUL', '-w', '%{http_code}', url,
            env=benchmark_environment(), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        status = int(stdout.decode().strip() or '0')
        return {'transport_success': process.returncode == 0 and status > 0,
                'http_status': status, 'http_2xx': 200 <= status < 300,
                'exit_code': process.returncode, 'stderr': stderr.decode(errors='replace').strip()}
    except Exception as exc:
        return {'transport_success': False, 'exceptions': exceptions(exc)}


async def main(args):
    import truststore
    clean_environment = benchmark_environment()
    os.environ.clear()
    os.environ.update(clean_environment)
    report = json.loads((args.run / 'report.json').read_text(encoding='utf-8'))
    # One company per sample member; prefer its first failed HTTPS request.
    members = {}
    for e in report['request_log']:
        if (e.get('section') == 'website' and e.get('url', '').startswith('https://')
                and e.get('error') in {'ConnectError', 'ConnectTimeout', 'TimeoutError', 'ReadError', 'RemoteProtocolError'}):
            members.setdefault(e['organisation_number'], e)
    sample = random.Random(args.seed).sample(sorted(members), args.size)
    output = {'seed': args.seed, 'sample_population_companies': len(members),
              'source_run': str(args.run), 'started_at': datetime.now(timezone.utc).isoformat(),
              'source_report_sha256': hashlib.sha256((args.run / 'report.json').read_bytes()).hexdigest(),
              'python': platform.python_version(), 'platform': platform.platform(),
              'truststore': truststore.__version__, 'certifi': certifi.__version__,
              'curl_version': subprocess.check_output(['curl.exe', '-q', '--version'], text=True).splitlines()[0],
              'credentials': 'benchmark environment stripped; no credentials or search',
              'method': 'Same failed HTTPS URL; direct connection, verified TLS, no redirects, 8 second cap; HTTP response and 2xx counted separately. Historical logs omit messages; fresh default retry captures full exception chain.',
              'items': []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    gate = asyncio.Semaphore(4)

    async def member(org):
        async with gate:
            event = members[org]
            item = {'org': org, 'url': event['url'], 'historical_event': event, 'results': {}}
            # Rotate arm order to reduce a fixed temporal-order bias.
            arms = ['default', 'truststore', 'certifi', 'curl']
            offset = sample.index(org) % 4
            for mode in arms[offset:] + arms[:offset]:
                result = await (curl_retry(event['url']) if mode == 'curl' else python_retry(event['url'], mode))
                result['category'] = category(result)
                item['results'][mode] = result
                print(org, mode, result['category'], result.get('http_status', ''), flush=True)
            output['items'].append(item)
            args.output.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')

    await asyncio.gather(*(member(org) for org in sample))
    output['items'].sort(key=lambda r: sample.index(r['org']))
    output['summary'] = {mode: {'transport_success': sum(i['results'][mode]['transport_success'] for i in output['items']),
                              'http_2xx': sum(i['results'][mode].get('http_2xx', False) for i in output['items']),
                              'categories': dict(Counter(i['results'][mode]['category'] for i in output['items']))}
                         for mode in ('default', 'truststore', 'certifi', 'curl')}
    output['finished_at'] = datetime.now(timezone.utc).isoformat()
    output['exception_class_counts'] = {
        mode: dict(Counter(i['results'][mode].get('exceptions', [{'class': 'HTTP response'}])[0]['class']
                           for i in output['items'])) for mode in ('default', 'truststore', 'certifi')}
    args.output.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output['summary']), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=20261105)
    parser.add_argument('--size', type=int, default=30)
    asyncio.run(main(parser.parse_args()))
