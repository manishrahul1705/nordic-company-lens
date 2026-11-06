import pytest
from tests.test_synthesis import envelope
from signalpost.synthesis.template import generate
from signalpost.synthesis.company_brief import validate


def test_three_parts_are_cited_and_metadata_is_explicit(tmp_path):
    row, _ = envelope(tmp_path)
    result = row.run.synthesis
    brief = result.brief
    assert brief and brief.what and brief.changes and brief.unknowns
    ids = {c.id for c in row.claims} | {c.id for c in result.change_claims} | {c.id for c in brief.context_claims}
    assert all(s.claim_ids and set(s.claim_ids) <= ids for part in (brief.what, brief.changes, brief.unknowns) for s in part)
    assert len(brief.what) <= 2
    assert any('Financials: not found' in s.text for s in brief.unknowns)
    validate(brief, result, row)


def test_dated_no_change_and_stale_note_are_recomputed(tmp_path):
    row, _ = envelope(tmp_path)
    row.run.refresh.update(mode='refresh', previous_completed_at='2026-11-05T12:00:00Z',
                           stale_sections={'website': {'previous_state': 'available', 'attempt_state': 'failed',
                              'failed_attempt_at': '2026-11-06T12:00:00Z', 'failure_codes': ['dns_timeout']}})
    row.run.sections['website'] = 'available'
    result = generate(row)
    assert result.brief.changes[0].text == 'No changes since 2026-11-05.'
    assert any('stale' in s.text and 'dns_timeout' in s.text and '2026-11-06' in s.text for s in result.brief.unknowns)
    changed = result.brief.model_copy(deep=True)
    changed.changes[0].text = 'No changes since 2026-11-01.'
    with pytest.raises(ValueError, match='Unsupported company brief'):
        validate(changed, result, row)
    changed = result.brief.model_copy(deep=True)
    changed.context_claims[0].value = {'state': 'available'}
    with pytest.raises(ValueError):
        validate(changed, result, row)


def test_missing_and_forged_citations_fail(tmp_path):
    row, _ = envelope(tmp_path)
    result = row.run.synthesis
    for citation in ([], ['invented']):
        brief = result.brief.model_copy(deep=True)
        brief.unknowns[0].claim_ids = citation
        with pytest.raises(ValueError):
            validate(brief, result, row)


def test_previous_to_current_role_summary_has_both_source_sides(tmp_path):
    from tests.test_registry import config, execute, handler
    first = config(tmp_path / 'first', ['923609016'])
    execute(first)
    _, rows = execute(config(tmp_path / 'next', ['923609016'], previous=first.output), handler('Person Two'))
    from signalpost.models.envelope import Envelope
    row = Envelope.model_validate(rows[0])
    brief = row.run.synthesis.brief
    assert any('Person One → Person Two' in s.text for s in brief.changes)
    ids = {c.id for c in row.run.synthesis.change_claims}
    assert any(len(set(s.claim_ids) & ids) == 2 for s in brief.changes)
    validate(brief, row.run.synthesis, row)


def test_writer_rejects_a_forged_brief(tmp_path):
    from signalpost.io.envelope_writer import write
    from signalpost.sources.blobstore import BlobStore
    row, cfg = envelope(tmp_path)
    row.run.synthesis.brief.unknowns[0].text = 'All sources are complete.'
    with pytest.raises(ValueError, match='Unsupported company brief'):
        write(tmp_path / 'forged.jsonl', [row], 'union', BlobStore(cfg.state_dir))
    assert not (tmp_path / 'forged.jsonl').exists()
