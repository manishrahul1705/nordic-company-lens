"""Dated registry observations from published claims and their existing proof."""
from datetime import date

from ..models.claim import Claim
from ..models.evidence import digest


def publish(envelope):
    evidence = {e.id: e for e in envelope.evidence}
    known = {c.id for c in envelope.claims}
    for original in list(envelope.claims):
        if original.family != 'identity' or original.availability != 'available':
            continue
        name = original.field.removeprefix('identity.')
        year_only = name == 'latest_submitted_accounts'
        if not name.endswith('_date') and not year_only:
            continue
        value = original.value
        if not isinstance(value, str):
            continue
        try:
            if year_only:
                if len(value) != 4 or not value.isdigit() or not 1 <= int(value) <= 9999:
                    continue
            else:
                date.fromisoformat(value)
        except ValueError:
            continue
        if not original.evidence_ids or any(ref not in evidence for ref in original.evidence_ids):
            continue
        field = 'registry_dated_activity.' + name
        ident = digest([envelope.organisation_number, field, value])
        if ident in known:
            continue
        envelope.claims.append(Claim(
            id=ident, field=field, family='activity', value=value,
            availability='available', confidence=original.confidence,
            evidence_ids=list(original.evidence_ids),
            first_observed_at=original.first_observed_at,
            last_observed_at=original.last_observed_at,
            reasons={'label': 'Registry ' + name.replace('_', ' '),
                     'date_precision': 'year' if year_only else 'day',
                     'date_basis': original.field},
        ))
        known.add(ident)
