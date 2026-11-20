"""Normal website transport preflight/diagnosis; never ignore TLS or robots."""
import argparse
import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import httpx
from signalpost.budget import Budget, SourceFailure
from signalpost.config import Config
from signalpost.sources.blobstore import BlobStore
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web.policy import safe_transport, domain
from signalpost.web.html import Page


def chain(exc):
    seen = set(); out = []
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc)); out.append({'class': type(exc).__name__, 'message': str(exc),
            'errno': getattr(exc, 'errno', None), 'winerror': getattr(exc, 'winerror', None)})
        exc = exc.__cause__ or exc.__context__
    return out


class DiagnosticBudget(Budget):
    def reserve(self, url, host, org):
        if self.by_company[org] >= 5:
            raise SourceFailure('diagnostic_five_request_limit')
        return super().reserve(url, host, org)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['good', 'known'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args(); cache = Path('bench/cache/stage-aq')
    targets = json.loads((cache / 'good.json').read_text()) if a.mode == 'good' else [
        {'orgnr': '912492575', 'url': 'https://www.haugel.no/'},
        {'orgnr': '914248906', 'url': 'https://indigoboom.com/'},
        {'orgnr': '982410851', 'url': 'http://www.marun.no/'}]
    state = cache / a.output.stem
    inputs = cache / (a.output.stem + '-input.txt')
    inputs.write_text('\n'.join(x['orgnr'] for x in targets))
    cfg = Config(organisations=inputs, output=state / 'unused', report=state / 'unused-report',
        state_dir=state, websites=True, website_transient_retry=False)
    budget = DiagnosticBudget(cfg); blobs = BlobStore(state)
    results = []
    async with httpx.AsyncClient(transport=safe_transport(8), trust_env=False) as client:
        http = WebsiteHttp(client, cfg, budget, blobs)
        for t in targets:
            try:
                r = await http.get(t['url'], t['orgnr'], domain(t['url']))
                p = Page(r.body, r.url)
                results.append({**t, 'status': r.status, 'final_url': r.url, 'sha256': r.sha,
                    'title': p.title, 'visible': p.visible[:10000], 'links': [{'url': l.href, 'text': l.text} for l in p.links]})
            except Exception as exc:
                errors = chain(exc); results.append({**t, 'error': errors})
                # One blocked network preflight invalidates a bulk measurement.
                if any(e['winerror'] in {5, 10013} or e['errno'] == 13 or 'forbidden by its access permissions' in e['message'] for e in errors):
                    break
    retained=[{k:v for k,v in r.items() if k not in {'visible','links'}} for r in results] if a.mode=='good' else results
    a.output.write_text(json.dumps({'transport': 'production safe_transport; trust_env=False; TLS and robots unchanged',
        'results': retained, 'requests': budget.events}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps([{'orgnr': x['orgnr'], 'url': x['url'], 'status': x.get('status'),
        'final_url': x.get('final_url'), 'error': x.get('error')} for x in results], ensure_ascii=True, indent=2))


if __name__ == '__main__': asyncio.run(main())
