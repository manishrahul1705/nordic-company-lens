"""Three short parts grounded in validated facts and explicit snapshot metadata."""
from ..models.evidence import digest
from ..models.synthesis import Brief, ChangeClaim, Sentence

LABELS = {'identity': 'Identity', 'roles': 'People', 'subunits': 'Locations',
          'accounts': 'Financials', 'website': 'Website and social',
          'hiring': 'Jobs', 'activity': 'News and activity'}
STATES = {'not_available': 'not found', 'not_applicable': 'not applicable',
          'failed': "couldn't check", 'blocked': 'blocked', 'ambiguous': 'withheld'}


def generate(synthesis, envelope):
    brief = Brief()

    def context(field, value):
        claim = ChangeClaim(id=digest(['snapshot-context', envelope.organisation_number, field, value]),
                            field=field, value=value, evidence_ids=[])
        brief.context_claims.append(claim)
        return claim.id

    # Existing source sentence validator already verifies the quoted values.
    for sentence in synthesis.sections.what_it_does:
        if sentence not in brief.what:
            brief.what.append(sentence)
        if len(brief.what) == 2:
            break
    if not brief.what:
        cid = context('snapshot.identity', {'state': envelope.run.sections.get('identity', 'failed')})
        brief.what.append(Sentence(text='Company identity could not be established from the checked sources.', claim_ids=[cid]))

    if envelope.changes:
        import json
        def short(value):
            if value is None:
                return 'none'
            if isinstance(value, list) and all(isinstance(v, dict) and 'name' in v for v in value):
                return '; '.join(str(v['name']) for v in value)
            return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
        for event in envelope.changes[:3]:
            cid = context('snapshot.change.' + event.field, {'type': event.type, 'field': event.field,
                          'previous': event.old_value, 'current': event.new_value})
            sides = [c.id for c in synthesis.change_claims if c.field in {event.field + '.old', event.field + '.new'}]
            brief.changes.append(Sentence(text=event.field.replace('_', ' ') + ': ' + short(event.old_value) + ' → ' + short(event.new_value) + '.', claim_ids=[cid, *sides]))
    else:
        refresh = envelope.run.refresh
        previous = refresh.get('previous_completed_at')
        cid = context('snapshot.refresh', {'mode': refresh.get('mode'), 'previous_completed_at': previous,
                                         'changes': len(envelope.changes)})
        wording = ('First observation; no previous snapshot.' if refresh.get('mode') == 'baseline'
                   else 'No changes since ' + str(previous)[:10] + '.' if previous
                   else 'No changes since the previous snapshot; its date was not recorded.')
        brief.changes.append(Sentence(text=wording, claim_ids=[cid]))

    stale = envelope.run.refresh.get('stale_sections', {})
    for family, state in sorted(envelope.run.sections.items()):
        if state == 'available' and family not in stale:
            continue
        codes = sorted({e.code for e in envelope.errors if e.section == family and e.code != 'website_candidates'})
        info = {'state': state, 'reasons': codes, 'stale': stale.get(family)}
        cid = context('snapshot.section.' + family, info)
        label = LABELS.get(family, family.title())
        if family in stale:
            attempt = stale[family]
            date = str(attempt['failed_attempt_at'])[:10]
            reason = ', '.join(attempt.get('failure_codes', [])) or 'transient source failure'
            wording = f'{label}: stale; retained {state.replace("_", " ")} snapshot after the failed refresh on {date} ({reason}).'
        else:
            reason = ', '.join(codes) or {'not_available': 'no supported items in the checked sources',
                      'not_applicable': 'source not applicable', 'ambiguous': 'exact company attribution unproven',
                      'blocked': 'source access refused'}.get(state, 'source request incomplete')
            wording = f'{label}: {STATES.get(state, state)} ({reason}).'
        brief.unknowns.append(Sentence(text=wording, claim_ids=[cid]))
    if not brief.unknowns:
        cid = context('snapshot.coverage', {'sections': envelope.run.sections, 'stale': False})
        brief.unknowns.append(Sentence(text='All enabled sections have supported results; source coverage may still be incomplete.', claim_ids=[cid]))
    return brief


def validate(brief, synthesis, envelope):
    """Recompute all frames, IDs, states and dates; metadata cannot license free text."""
    expected = generate(synthesis, envelope)
    if brief.model_dump() != expected.model_dump():
        raise ValueError('Unsupported company brief sentence or citation')
    return brief
