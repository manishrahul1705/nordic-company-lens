"""The `reach`, `standing` and `not_established` brief sections.

Every sentence is a fixed template over published claims or the cohort
records carried in the synthesis, and is validated by exact recomputation.
`not_established` (and the empty-section fallback for the original four
sections) cites the published *non-available* claim the run recorded for the
gap; its wording is derived only from recorded run state (section states,
error codes and website candidate outcomes).
"""
import json
from decimal import Decimal, ROUND_FLOOR

from ..models.synthesis import Sentence
from .cohort import MIN_COMPARABLES, division, revenue_key
from .company_brief import LABELS, section_reason, _address
from .readability import money

EXTRA_SECTIONS = ('reach', 'standing', 'not_established')
MAX_WORKPLACES = 5
MAX_MUNICIPALITIES = 8
SECTION_CLAIMS = {'subunits': ('subunits.units',), 'accounts': ('accounts.section', 'accounts.latest')}
FIELD_LABELS = {'identity.employees': 'Employee count', 'accounts.revenue': 'Operating revenue',
                'identity.nace1': 'Industry code', 'identity.registered_address': 'Business address',
                'identity.registered_website': 'Registered homepage'}
FIELD_ABSENT = {'identity.employees': 'not reported to the register',
                'accounts.revenue': 'the filed annual accounts state no operating revenue figure',
                'identity.nace1': 'none registered', 'identity.registered_address': 'none registered',
                'identity.registered_website': 'none registered with Brønnøysund'}


# --- Shared helpers -----------------------------------------------------------

def _claims(envelope, available=True):
    from .validate import permitted
    if available:
        return [c for c in envelope.claims if c.availability == 'available' and permitted(c, envelope)]
    return [c for c in envelope.claims if c.availability != 'available']


def _field(envelope, field, available=True):
    return next((c for c in _claims(envelope, available) if c.field == field), None)


def section_claim(envelope, family):
    """The published placeholder claim recording a section's non-available state."""
    state = envelope.run.sections.get(family)
    fields = SECTION_CLAIMS.get(family, (family + '.section',))
    return next((c for c in envelope.claims if c.field in fields and c.availability == state and state != 'available'), None)


def codes(envelope, family):
    return sorted({e.code for e in envelope.errors if e.section == family and e.code != 'website_candidates'})


def section_text(envelope, family):
    state = envelope.run.sections.get(family)
    wording = LABELS.get(family, family.title()) + ': ' + section_reason(family, state, codes(envelope, family), envelope) + '.'
    return wording[:1].upper() + wording[1:]


def absence_text(claim, envelope):
    """Fixed wording for a published non-available claim, from recorded state only."""
    if claim is None or claim.availability == 'available':
        return None
    family = claim.field.split('.', 1)[0]
    if claim.field in SECTION_CLAIMS.get(family, (family + '.section',)):
        if envelope.run.sections.get(family) != claim.availability:
            return None
        return section_text(envelope, family)
    if claim.field in FIELD_LABELS:
        reason = FIELD_ABSENT[claim.field] if claim.availability == 'not_available' else "couldn't be checked during the run"
        return FIELD_LABELS[claim.field] + ': ' + reason + '.'
    return None


def absence(claim, envelope):
    text = absence_text(claim, envelope)
    return Sentence(text=text, claim_ids=[claim.id]) if text else None


def municipality(address):
    return str((address or {}).get('kommune') or '').strip() or None


# --- Reach ---------------------------------------------------------------------

def reach(envelope, cohort):
    out = []
    address = _field(envelope, 'identity.registered_address')
    where = _address(address.value) if address else None
    if where:
        place = municipality(address.value)
        out.append(Sentence(text='Registered business address: ' + where + (', in ' + place + ' municipality' if place else '') + '.',
                            claim_ids=[address.id]))
    units = sorted((c for c in _claims(envelope) if c.field.startswith('subunits.unit.') and isinstance(c.value, dict)
                    and _address(c.value.get('address'))), key=lambda c: (str(c.value.get('name') or ''), str(c.value.get('organisation_number') or ''), c.id))
    if len(units) == 1 and where and _address(units[0].value.get('address')) == where:
        units = []  # the only workplace is the company itself, at its business address
    for unit in units[:MAX_WORKPLACES]:
        value = unit.value
        place = municipality(value.get('address'))
        label = str(value.get('name') or 'Unnamed workplace') + (' (org. ' + str(value['organisation_number']) + ')' if value.get('organisation_number') else '')
        out.append(Sentence(text='Registered workplace: ' + label + ', ' + _address(value.get('address'))
                            + (', in ' + place + ' municipality' if place else '') + '.', claim_ids=[unit.id]))
    placed = [u for u in units if municipality(u.value.get('address'))]
    if len(units) > 1 and placed:
        counts = {}
        for unit in placed:
            counts[municipality(unit.value['address'])] = counts.get(municipality(unit.value['address']), 0) + 1
        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        listed = '; '.join(name + ' (' + str(n) + ')' for name, n in ranked[:MAX_MUNICIPALITIES])
        more = '; ' + str(len(ranked) - MAX_MUNICIPALITIES) + ' more' if len(ranked) > MAX_MUNICIPALITIES else ''
        out.append(Sentence(text='Registered workplaces with an address: ' + str(len(units)) + ', in ' + str(len(ranked))
                            + (' municipality' if len(ranked) == 1 else ' municipalities') + ': ' + listed + more + '.',
                            claim_ids=sorted(u.id for u in units), value_kind='derived'))
    holdings = (cohort.role_holdings if cohort is not None else [])
    for role, name in zip(holdings[0::2], holdings[1::2]):
        title = str(((role.value or {}).get('role_type') or {}).get('beskrivelse') or 'Registered role')
        out.append(Sentence(text='Registered role at another company in this run: ' + title + ' for ' + str(name.value)
                            + ' (org. ' + role.organisation_number + ').', claim_ids=[role.id, name.id]))
    # No separately registered workplace is a recorded fact about where it operates.
    # A missing business address is stated once, in not_established.
    if envelope.run.sections.get('subunits') != 'available':
        sentence = absence(section_claim(envelope, 'subunits'), envelope)
        if sentence:
            out.append(sentence)
    if not out:
        sentence = absence(section_claim(envelope, 'identity'), envelope)
        if sentence:
            out.append(sentence)
    return out


# --- Standing ------------------------------------------------------------------

def percentile(value, others):
    """Share of the compared companies with strictly lower operating revenue, rounded down."""
    below = sum(1 for v in others if v < value)
    return int((Decimal(below) * 100 / Decimal(len(others))).to_integral_value(rounding=ROUND_FLOOR))


RUN_ONLY = 'other companies in this run'


def _standing(envelope, cohort):
    """Every wording names the comparison basis: companies in this run only, NACE division, fiscal year."""
    nace = _field(envelope, 'identity.nace1')
    revenue = _field(envelope, 'accounts.revenue')
    revenue = revenue if revenue is not None and not revenue.carried_forward else None
    if revenue is None or revenue_key(revenue) is None:
        missing = _field(envelope, 'accounts.revenue', available=False)
        if missing is not None and envelope.run.sections.get('accounts') == 'available':
            return [Sentence(text='Not compared with ' + RUN_ONLY + ': the filed annual accounts state no operating revenue figure.',
                             claim_ids=[missing.id])]
        placeholder = section_claim(envelope, 'accounts')
        if placeholder is not None:
            return [Sentence(text='Not compared with ' + RUN_ONLY + ': no operating revenue is published. '
                             + section_text(envelope, 'accounts'), claim_ids=[placeholder.id])]
        return [s for s in [absence(missing, envelope)] if s]
    year, _, currency = revenue_key(revenue)
    amount = currency + ' ' + money(revenue.value)
    group = division(nace)
    if nace is None:
        missing = _field(envelope, 'identity.nace1', available=False)
        return [Sentence(text='Its FY' + year + ' operating revenue of ' + amount + ' is not compared with ' + RUN_ONLY
                         + ', because no industry code is registered.', claim_ids=[revenue.id] + ([missing.id] if missing else []))]
    if group is None:
        return [Sentence(text='Its FY' + year + ' operating revenue of ' + amount + ' is not compared with ' + RUN_ONLY
                         + ', because the registered industry code is unspecified.', claim_ids=[revenue.id, nace.id])]
    record = cohort.standing if cohort is not None else None
    others = [c.value for c in record.comparables] if record is not None else []
    n = len(others)
    # The division is named only as the comparison group, never as the company's activity.
    from .nace import division_title
    title = division_title(nace.value)
    label = 'NACE division ' + group + (' (' + title[:1].lower() + title[1:] + ')' if title else '')
    basis = 'in the comparison group ' + label + ' with FY' + year + ' accounts'
    if n == 0:
        return [Sentence(text='No other company in this run is ' + basis + ', so its FY' + year + ' operating revenue of '
                         + amount + ' is not compared.', claim_ids=[revenue.id, nace.id], value_kind='derived')]
    if n < MIN_COMPARABLES:
        return [Sentence(text='Only ' + str(n) + (' other company' if n == 1 else ' other companies') + ' in this run '
                         + ('is ' if n == 1 else 'are ') + basis + ', fewer than the ' + str(MIN_COMPARABLES)
                         + ' needed for a comparison, so its FY' + year + ' operating revenue of ' + amount + ' is not ranked.',
                         claim_ids=[revenue.id, nace.id], value_kind='derived')]
    return [Sentence(text='Among the ' + str(n) + ' other companies in this run ' + basis + ', its FY' + year
                     + ' operating revenue of ' + amount + ' is higher than ' + str(percentile(float(revenue.value), others)) + '% of them.',
                     claim_ids=[revenue.id, nace.id], value_kind='derived')]


def standing(envelope, cohort):
    from .funding_news import funding_sentence
    funding = funding_sentence(envelope)
    return _standing(envelope, cohort) + ([funding] if funding else [])


# --- Not established ---------------------------------------------------------------

def _candidates(envelope):
    out = []
    for error in envelope.errors:
        if error.section != 'website' or error.code != 'website_candidates':
            continue
        try:
            items = json.loads(error.message)
        except (TypeError, ValueError):
            continue
        out += [i for i in items if isinstance(i, dict) and i.get('domain')] if isinstance(items, list) else []
    return out


def _host(url):
    from urllib.parse import urlsplit
    text = str(url or '').strip()
    host = urlsplit(text if '://' in text else 'https://' + text).hostname or ''
    return host.removeprefix('www.')


def not_established(envelope):
    out = []
    state = envelope.run.sections.get('website')
    declared = _field(envelope, 'identity.registered_website')
    website = _field(envelope, 'official_website')
    if state is not None and state != 'available':
        cited = section_claim(envelope, 'website') or declared or _field(envelope, 'identity.registered_website', available=False)
        if cited is not None:
            out.append(Sentence(text=section_text(envelope, 'website'), claim_ids=[cited.id]))
    if website is not None and isinstance(website.value, dict) and (website.reasons or {}).get('relationship') == 'group_site':
        out.append(Sentence(text='Own website: not established; the published site ' + str(website.value.get('final_url'))
                            + ' is recorded as a shared group site.', claim_ids=[website.id]))
    if declared is not None and isinstance(declared.value, str):
        host = _host(declared.value)
        rejected = sorted({str(i.get('reason')) for i in _candidates(envelope)
                           if _host(i['domain']) == host and any(w in str(i.get('reason') or '').casefold() for w in ('group', 'shared'))})
        if host and rejected and not any(host in s.text for s in out):
            out.append(Sentence(text='Declared homepage ' + declared.value + ': not used as company website; recorded as a shared or group site ('
                                + ', '.join(rejected) + ').', claim_ids=[declared.id]))
    for family in sorted(envelope.run.sections):
        if family in ('website', 'subunits') or envelope.run.sections[family] == 'available':
            continue
        sentence = absence(section_claim(envelope, family), envelope)
        if sentence:
            out.append(sentence)
    for field in ('identity.employees', 'identity.nace1', 'identity.registered_address'):
        sentence = absence(_field(envelope, field, available=False), envelope)
        if sentence:
            out.append(sentence)
    if envelope.run.sections.get('accounts') == 'available':
        sentence = absence(_field(envelope, 'accounts.revenue', available=False), envelope)
        if sentence:
            out.append(sentence)
    homepage = absence(_field(envelope, 'identity.registered_website', available=False), envelope)
    if homepage and not any('Brønnøysund' in s.text for s in out):
        out.append(homepage)
    return out


def generate(envelope, cohort):
    return {'reach': reach(envelope, cohort), 'standing': standing(envelope, cohort),
            'not_established': not_established(envelope)}


def fallback(section, envelope):
    """Cited absence wording for an original section that would otherwise be empty."""
    if section == 'leadership':
        placeholder = section_claim(envelope, 'roles')
        if placeholder is not None:
            return [s for s in [absence(placeholder, envelope)] if s]
        roles = sorted((c for c in _claims(envelope) if c.field.startswith('roles.role.') and isinstance(c.value, dict)
                        and c.value.get('inactive') is not True and c.value.get('name')
                        and (c.value.get('role_type') or {}).get('beskrivelse')), key=lambda c: c.field)
        out = []
        for claim in roles[:3]:
            name = claim.value['name']
            name = '; '.join(str(x) for x in name) if isinstance(name, list) else str(name)
            out.append(Sentence(text='Registered role (' + str(claim.value['role_type']['beskrivelse']) + '): ' + name + '.',
                                claim_ids=[claim.id]))
        return out
    if section == 'scale':
        for candidate in (section_claim(envelope, 'accounts'), _field(envelope, 'identity.employees', available=False)):
            sentence = absence(candidate, envelope)
            if sentence:
                return [sentence]
    return []
