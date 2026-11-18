"""Offline A/B replay of the 5 sites with non-UTF-8 HTML bodies in long-label-clean-20261118.

Serves every saved response for these companies from the run's blob store (no HTTP leaves
the process; unknown URLs get 404) and runs the real pipeline twice: once with the span
check's old decoder (UTF-8 with replacement) and once with the fixed one (decode_body).
Reports website claims published and withheld (invalid_span) per company for each side.
"""
import asyncio, json, sys
from pathlib import Path
import httpx
from signalpost.config import Config
from signalpost import runner
from signalpost.web import collector
from signalpost.sources import text

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'bench/runs/long-label-clean-20261118'
OUT = ROOT / 'bench/reports/charset-replay-20261118'
ORGS = ['986665358', '989338811', '933058174', '933784762', '927906694']


def served():
    log = json.load(open(RUN / 'report.json', encoding='utf-8-sig'))['request_log']
    table = {}
    for e in log:
        if e.get('content_sha256') and e.get('status') is not None:
            table.setdefault(e['url'], (e['status'], e['content_sha256']))
    return table


def kind(body):
    head = body.lstrip()[:20]
    if head.startswith(b'%PDF'): return 'application/pdf'
    if head[:1] in (b'{', b'['): return 'application/json'
    if head[:1] == b'<': return 'text/html'
    return 'text/plain'


def run_side(label, decoder, table, offline):
    dest = OUT / label; dest.mkdir(parents=True, exist_ok=True)
    (dest / 'batch.txt').write_text('\n'.join(ORGS))
    collector.decode_body = decoder
    def respond(request):
        offline.append(str(request.url))
        hit = table.get(str(request.url))
        if not hit:
            return httpx.Response(404, content=b'')
        body = (RUN / 'state' / 'blobs' / hit[1]).read_bytes()
        return httpx.Response(hit[0], content=body, headers={'content-type': kind(body)})
    cfg = Config(organisations=dest / 'batch.txt', output=dest / 'envelopes.jsonl', report=dest / 'report.json',
                 state_dir=dest / 'state', websites=True, public_activity=False, hiring=False, registry_changes=False, wikidata=False,
                 official_extra_sources=False, nav_index_path=dest / 'none.json.gz')
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await runner.run(cfg, client)
    asyncio.run(go())
    out = {}
    for line in (dest / 'envelopes.jsonl').read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        web = [c for c in row['claims'] if c['family'] == 'website' and c['availability'] == 'available'
               and not c['field'].endswith('.section')]
        out[row['organisation_number']] = {
            'website_state': row['modules']['website']['state'],
            'published': sorted(c['field'].split('.')[0] + '=' + json.dumps(c['value'], ensure_ascii=False)[:90] for c in web),
            'withheld_invalid_span': sum(e['code'] == 'invalid_span' for e in row['errors'] if e['section'] == 'website')}
    return out


def main():
    table = served()
    old_decoder = lambda body: body.decode('utf8', errors='replace')
    seen = []
    before = run_side('old-decoder', old_decoder, table, seen)
    after = run_side('fixed-decoder', text.decode_body, table, seen)
    change = {}
    for org in ORGS:
        b, a = before[org], after[org]
        change[org] = {'before': b, 'after': a,
                       'newly_published': sorted(set(a['published']) - set(b['published'])),
                       'no_longer_published': sorted(set(b['published']) - set(a['published']))}
    result = {'http_requests_leaving_process': 0, 'mock_requests': len(seen), 'companies': change,
              'published_delta': sum(len(c['newly_published']) - len(c['no_longer_published']) for c in change.values()),
              'withheld_delta': sum(c['after']['withheld_invalid_span'] - c['before']['withheld_invalid_span'] for c in change.values())}
    (OUT / 'charset-replay.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
