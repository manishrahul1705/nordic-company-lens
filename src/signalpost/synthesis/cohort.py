"""Cross-company context for the `standing` and `reach` sections.

Built once per run from the run's own finalised envelopes; no source is
fetched. Each brief carries the exact cohort records it relies on, so the
per-envelope validator can recompute its sentences, and verify_output
recomputes the cohort records themselves from every output row.
"""
from ..models.synthesis import Cohort, CohortClaim, Comparable, Standing
from .nace import unspecified

MIN_COMPARABLES = 10


def _available(envelope, field):
    from .validate import permitted
    return next((c for c in envelope.claims if c.field == field and c.availability == 'available'
                 and not c.carried_forward and permitted(c, envelope)), None)


def division(nace_claim):
    """Two-digit NACE division of a registered code, or None when unusable."""
    if nace_claim is None or not isinstance(nace_claim.value, dict) or unspecified(nace_claim.value):
        return None
    code = str(nace_claim.value.get('kode') or '')
    head = code.split('.', 1)[0]
    return head if len(head) == 2 and head.isdigit() else None


def revenue_key(claim):
    """(fiscal year, account type, currency) of an operating-revenue claim, or None."""
    if claim is None or isinstance(claim.value, bool) or not isinstance(claim.value, (int, float)):
        return None
    period = claim.reporting_period or {}
    if not period.get('fiscal_year') or not period.get('currency'):
        return None
    return str(period['fiscal_year']), period.get('account_type'), period['currency']


def comparable_record(envelope):
    """(division, revenue key, revenue claim) for one company, or None."""
    if envelope.run.sections.get('identity') != 'available':
        return None
    group = division(_available(envelope, 'identity.nace1'))
    revenue = _available(envelope, 'accounts.revenue')
    key = revenue_key(revenue)
    if group is None or key is None:
        return None
    return group, key, revenue


def build_index(envelopes):
    """Index the run: comparable revenue records and roles held by entity organisation number."""
    records, holdings = {}, {}
    for envelope in envelopes:
        org = envelope.organisation_number
        if org in records or envelope.run.sections.get('identity') != 'available':
            continue
        records[org] = comparable_record(envelope)
        name = _available(envelope, 'identity.legal_name')
        for claim in envelope.claims:
            if not claim.field.startswith('roles.role.') or claim.availability != 'available' or claim.carried_forward:
                continue
            value = claim.value if isinstance(claim.value, dict) else {}
            holder = value.get('entity_organisation_number')
            if not holder or holder == org or value.get('inactive') is True or name is None:
                continue
            holdings.setdefault(holder, []).append((org, claim, name))
    return {'records': records, 'holdings': holdings}


def copy(org, claim):
    return CohortClaim(organisation_number=org, id=claim.id, field=claim.field, value=claim.value,
                       evidence_ids=list(claim.evidence_ids))


def context(envelope, index):
    """The cohort records one company's brief may cite."""
    if index is None:
        return None
    org = envelope.organisation_number
    cohort = Cohort()
    own = comparable_record(envelope)
    if own is not None:
        group, key, _ = own
        others = sorted((other, record[2]) for other, record in index['records'].items()
                        if other != org and record is not None and record[0] == group and record[1] == key)
        cohort.standing = Standing(division=group, fiscal_year=key[0], account_type=key[1], currency=key[2],
                                   comparables=[Comparable(organisation_number=other, claim_id=claim.id, value=float(claim.value))
                                                for other, claim in others])
    for other, role, name in sorted(index['holdings'].get(org, []), key=lambda item: (item[0], item[1].id)):
        cohort.role_holdings += [copy(other, role), copy(other, name)]
    return cohort

