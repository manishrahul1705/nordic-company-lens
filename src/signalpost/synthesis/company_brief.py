"""Three short parts grounded in validated facts and explicit snapshot metadata."""
from ..models.evidence import digest
from ..models.synthesis import Brief, ChangeClaim, Sentence

LABELS = {'identity': 'Identity', 'roles': 'People', 'subunits': 'Locations',
          'accounts': 'Financials', 'website': 'Website and social',
          'hiring': 'Jobs', 'activity': 'News and activity'}
STATES = {'not_available': 'not found', 'not_applicable': 'not applicable',
          'failed': "couldn't check", 'blocked': 'blocked', 'ambiguous': 'withheld'}


def plain_reason(code):
    """Presentation only: original codes remain in the cited snapshot context."""
    code = str(code).casefold()
    if code == 'no_verified_website':
        return 'no verified company website was found'
    if 'robots' in code:
        return 'the website blocks automated access (robots.txt)'
    if code == 'no_such_domain' or any(word in code for word in ('timeout', 'dns', 'connect', 'reset', 'servfail', 'tls')):
        return "the source couldn't be reached during the run"
    if any(word in code for word in ('group', 'shared')):
        return 'only a shared group website was found'
    if any(word in code for word in ('ambiguous', 'attribution', 'owner', 'identity', 'foreign_orgnr')):
        return "a match couldn't be confirmed for this exact company"
    if any(word in code for word in ('blocked', 'refused', 'http_403', 'http_401', 'http_429')):
        return 'the source blocks automated access'
    if any(word in code for word in ('budget', 'deadline', 'cap', 'incomplete', 'not_started')):
        return 'the source could not be fully checked during the run'
    if 'not_applicable' in code or code == 'website_link_only':
        return 'this source does not apply to the available company evidence'
    if any(word in code for word in ('not_found', 'not_available', 'no_items', 'no_candidates')):
        return 'no supported items were found in the checked sources'
    return 'the source did not provide a supported result'


def plain_reasons(codes, fallback):
    return '; '.join(dict.fromkeys(plain_reason(code) for code in codes)) or fallback


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
            reason = plain_reasons(attempt.get('failure_codes', []), "the source couldn't be reached during the run")
            retained = 'found' if state == 'available' else STATES.get(state, 'previous')
            wording = f'{label}: stale; retained {retained} snapshot after the failed refresh on {date} ({reason}).'
        else:
            reason = plain_reasons(codes, {'not_available': 'no supported items in the checked sources',
                      'not_applicable': 'source not applicable', 'ambiguous': 'exact company attribution unproven',
                      'blocked': 'source access refused'}.get(state, 'source request incomplete'))
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
