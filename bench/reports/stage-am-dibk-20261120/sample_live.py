"""Live DiBK-only sample replay under normal pooled/per-company budgets."""
import asyncio
import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import httpx
from signalpost.config import Config
from signalpost.budget import Budget
from signalpost.models.envelope import Envelope, CompactProfile
from signalpost.models.shapes import serialize
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.dibk import Collector, selected
from signalpost.web.policy import safe_transport
from scripts.verify_output import verify


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('bench/runs/stage-al-skattefunn100/envelopes.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('bench/runs/stage-am-sample100'))
    parser.add_argument('--summary', type=Path, default=Path(__file__).with_name('sample100.json'))
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    source = args.source
    rows = [Envelope.model_validate(json.loads(l)) for l in source.open(encoding='utf-8')]
    inputs = out / 'input.txt'; inputs.write_text('\n'.join(r.organisation_number for r in rows), encoding='utf-8')
    cfg = Config(organisations=inputs, output=out / 'envelopes.jsonl', report=out / 'report.json',
        state_dir=out / 'state', dibk=True)
    budget = Budget(cfg); blobs = BlobStore(cfg.state_dir); begin = time.monotonic()
    async with httpx.AsyncClient(transport=safe_transport(4), trust_env=False) as client:
        collector = Collector(client, cfg, budget, blobs)
        for row in rows: collector.schedule(row)
        # This harness times the isolated batch, not a pipeline tail. Its wait
        # is bounded by the normal crawl deadline; production joins cap at 60s.
        await collector.finish(max_wait=max(.001, budget.deadline - time.monotonic()))
    seconds = time.monotonic() - begin
    # Link immutable evidence already stored by the saved input replay.
    needed = {e.content_sha256 for r in rows for e in r.evidence if not (blobs.directory / e.content_sha256).exists()}
    for directory in Path('bench/runs').glob('*/state/blobs'):
        if directory.resolve() == blobs.directory.resolve(): continue
        for path in directory.iterdir():
            if path.name in needed:
                os.link(path, blobs.directory / path.name); needed.remove(path.name)
        if not needed: break
    assert not needed
    with cfg.output.open('w', encoding='utf-8') as f:
        for row in rows:
            row.profile = CompactProfile(organisation_number=row.organisation_number,
                values={c.field: c.value for c in row.claims}, evidence_ids=[e.id for e in row.evidence], synthesis=row.run.synthesis)
            f.write(json.dumps(serialize(row, 'union'), ensure_ascii=False, separators=(',', ':')) + '\n')
    claims = [(r.organisation_number, c) for r in rows for c in r.claims if c.field.startswith('central_approval.')]
    summary = {'mode': 'saved-cohort replay plus live DiBK-only fetches; not a fresh all-source crawl',
        'companies': len(rows),
        'selected': sum(selected(r) for r in rows), 'companies_with_approvals': len({org for org,c in claims}),
        'approval_claims': len(claims), 'HTTP_added': len(budget.events),
        'enterprise_HTTP': sum(e['organisation_number'] != '__dibk_robots__' for e in budget.events),
        'robots_HTTP': sum(e['organisation_number'] == '__dibk_robots__' for e in budget.events),
        'isolated_fetch_seconds': seconds, 'requests': budget.events,
        'diagnostics': {r.organisation_number: r.run.refresh.get('dibk') for r in rows if selected(r)},
        'strict_verifier': verify(cfg.output, cfg.state_dir, len(rows))}
    args.summary.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in {'requests','diagnostics'}}, indent=2))


if __name__ == '__main__': asyncio.run(main())
