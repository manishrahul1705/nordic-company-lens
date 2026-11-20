"""Three short parts grounded in validated facts and explicit snapshot metadata.

`what` reuses the cited analyst sentences, `changes` states the most
significant dated events the run already publishes (registry announcements,
company articles, procurement awards) plus any snapshot differences, and
`unknowns` names each gap with the reason recorded for it. The site renders
exactly these three parts, so the machine-readable brief and the page agree.
"""
import json
import re
from datetime import date

from ..models.evidence import digest
from ..models.synthesis import Brief, ChangeClaim, Sentence

LABELS = {'identity': 'Identity', 'roles': 'People', 'subunits': 'Workplaces',
          'accounts': 'Financials', 'website': 'Website and social media',
          'hiring': 'Job ads', 'activity': 'Registry announcements'}
STATES = {'not_available': 'not found', 'not_applicable': 'not applicable',
          'failed': "couldn't check", 'blocked': 'blocked', 'ambiguous': 'withheld'}
MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
WHAT_TYPES = ('a', 'b', 'c', 'e')
MAX_EVENTS = 3


def plain_reason(code):
    """Presentation only: original codes remain in the cited snapshot context."""
    code = str(code).casefold()
    if code == 'declared_domain_absent':
        return 'the declared domain does not exist'
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


def short_date(value):
    try:
        d = date.fromisoformat(str(value)[:10])
    except ValueError:
        return None
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'


# --- What changed -----------------------------------------------------------

def _address(value):
    if not isinstance(value, dict):
        return None
    lines = [str(x).strip() for x in value.get('adresse') or [] if str(x).strip()]
    place = ' '.join(str(x) for x in (value.get('postnummer'), str(value.get('poststed') or '').title()) if x)
    parts = lines + ([place] if place.strip() else [])
    return ', '.join(parts) or None


def _amount(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    text = format(value, ',.2f').rstrip('0').rstrip('.')
    return text


def registry_event(value):
    """(tier, category, wording) for an explicitly supported registry event.

    Tier 1 is a business change, tier 2 a filing; bare, unspecified and purely
    administrative records return None and are never presented as changes.
    """
    path = value.get('changed_field') or ''
    new = value.get('new_value')
    if path == '/navn':
        return 1, 'name', ('a name change to «' + new + '»') if isinstance(new, str) and new.strip() else 'a registered name change'
    if path == '/kapital/belop':
        amount = _amount(new)
        return 1, 'capital', 'a share capital change to ' + amount if amount else 'a share capital change'
    if path == '/forretningsadresse' or path.startswith('/forretningsadresse/'):
        where = _address(new) if path == '/forretningsadresse' else None
        return 1, 'business_address', 'a new business address' + (' (' + where + ')' if where else '')
    if path == '/postadresse' or path.startswith('/postadresse/'):
        where = _address(new) if path == '/postadresse' else None
        return 1, 'postal_address', 'a new postal address' + (' (' + where + ')' if where else '')
    if path == '/sisteInnsendteAarsregnskap' and new is not None:
        return 2, 'accounts', 'that annual accounts for ' + str(new) + ' were filed'
    if path == '/vedtektsdato':
        when = short_date(new) if new else None
        return 2, 'articles', 'new articles of association' + (' dated ' + when if when else '')
    kind = value.get('event_type')
    unit = value.get('subunit_orgnr')
    if unit and kind == 'Ny':
        start = short_date(value.get('start_date')) if value.get('start_date') else None
        return 1, 'workplace_new', 'a new registered workplace (org. ' + unit + ')' + (', starting ' + start if start else '')
    if unit and kind == 'Sletting':
        return 1, 'workplace_removed', 'the removal of a registered workplace (org. ' + unit + ')'
    if not unit and not path and kind == 'Ny':
        return 1, 'entity_new', 'the registration of the company'
    if not unit and not path and kind == 'Sletting':
        return 1, 'entity_deleted', 'the deletion of the company from the register'
    return None


def dated_events(claims):
    """Most significant dated events, newest first: one per category, at most three."""
    grouped = {}
    for c in claims:
        if not isinstance(c.value, dict) or c.carried_forward:
            continue
        day = short_date(c.value.get('date'))
        if not day:
            continue
        when = str(c.value['date'])[:10]
        if c.field.startswith('registry_change.'):
            found = registry_event(c.value)
            if not found:
                continue
            tier, category, what = found
            key = (category, str(c.value.get('event_id')))
            text = 'A registry announcement on ' + day + ' records ' + what + '.'
        elif c.field.startswith('dated_item.') and c.value.get('title'):
            tier, category, key = 1, 'article', ('article', c.field)
            text = 'The company published «' + str(c.value['title']).strip().rstrip('.') + '» on its website on ' + day + '.'
        elif c.field.startswith('procurement_award.'):
            buyers = c.value.get('buyer') or []
            buyers = [buyers] if isinstance(buyers, str) else buyers
            tier, category, key = 1, 'award', ('award', c.field)
            if c.value.get('matched_role') == 'winner' and buyers:
                text = 'On ' + day + ' it was awarded a public contract by ' + ', '.join(buyers) + ' (TED).'
            elif c.value.get('title'):
                text = 'On ' + day + ' a public procurement award names it as a buyer for «' + str(c.value['title']).strip().rstrip('.') + '» (TED).'
            else:
                continue
        else:
            continue
        entry = grouped.setdefault(key, {'tier': tier, 'category': category, 'date': when, 'text': text, 'ids': [], 'fields': {}, 'day': day})
        entry['ids'].append(c.id)
        path = c.value.get('changed_field') if c.field.startswith('registry_change.') else None
        if path and '/' in path.strip('/') and 'new_value' in c.value:
            entry['fields'][path.strip('/').split('/', 1)[1]] = c.value['new_value']
    for entry in grouped.values():
        # One announcement can report an address as several sub-fields.
        if entry['category'] in {'business_address', 'postal_address'} and '(' not in entry['text'] and entry['fields']:
            where = _address({k: entry['fields'].get(k) for k in ('adresse', 'postnummer', 'poststed')})
            if where:
                label = 'business' if entry['category'] == 'business_address' else 'postal'
                entry['text'] = 'A registry announcement on ' + entry['day'] + ' records a new ' + label + ' address (' + where + ').'
    ranked = sorted(grouped.values(), key=lambda e: (e['tier'], tuple(-ord(ch) for ch in e['date']), e['text']))
    chosen, categories = [], set()
    for entry in ranked:
        if entry['category'] in categories and entry['category'] not in {'article', 'award'}:
            continue
        categories.add(entry['category'])
        chosen.append(entry)
        if len(chosen) == MAX_EVENTS:
            break
    return sorted(chosen, key=lambda e: (e['date'], e['text']), reverse=True)


# --- What remains unknown ---------------------------------------------------

UNREACHABLE = ('timeout', 'tls', 'connect', 'servfail', 'transient', 'http_5', 'budget', 'deadline', 'network')
NOT_OWNED = ('owner', 'insufficient', 'name_without_suffix', 'redirect_without', 'different_legal_entity',
             'foreign_orgnr', 'shared_registry_domain', 'group', 'conflict', 'publisher', 'directory')
PARKED = ('placeholder', 'parked', 'hosting_default', 'for_sale')
MISSING = ('no_such_domain', 'declared_domain_absent', 'nxdomain', 'http_404', 'http_410')


def _category(reason):
    reason = str(reason or '').casefold()
    if 'robots' in reason or reason in {'http_401', 'http_403', 'http_429'}:
        return 'blocked'
    if any(word in reason for word in PARKED):
        return 'parked'
    if any(word in reason for word in MISSING):
        return 'missing'
    if any(word in reason for word in UNREACHABLE):
        return 'unreachable'
    if any(word in reason for word in NOT_OWNED):
        return 'not_owned'
    return 'other' if reason else None


def website_attempts(envelope):
    """Distinct candidate domains with their recorded outcome category."""
    outcome = {}
    for error in envelope.errors:
        if error.section != 'website' or error.code != 'website_candidates':
            continue
        try:
            attempts = json.loads(error.message)
        except (TypeError, ValueError):
            continue
        for item in attempts if isinstance(attempts, list) else []:
            if not isinstance(item, dict) or not item.get('domain'):
                continue
            category = _category(item.get('reason'))
            if category and item['domain'] not in outcome:
                outcome[item['domain']] = category
    return outcome


def website_reason(envelope, state, codes):
    outcome = website_attempts(envelope)
    by = {}
    for domain, category in outcome.items():
        by.setdefault(category, []).append(domain)

    def example(category):
        return ' (' + ', '.join(sorted(by[category])[:2]) + ')'
    parts = []
    if by.get('not_owned'):
        n = len(by['not_owned'])
        parts.append(('a candidate site' if n == 1 else str(n) + ' candidate sites') + example('not_owned')
                     + (" didn't" if n == 1 else " didn't") + ' prove it belongs to this company')
    if by.get('parked'):
        parts.append('a parked or placeholder page' + example('parked'))
    if by.get('blocked'):
        parts.append('a site that blocks automated access' + example('blocked'))
    if by.get('unreachable'):
        parts.append("a site that couldn't be reached" + example('unreachable'))
    if state == 'ambiguous':
        lead = 'withheld: a possible site was found, but it may be shared with other companies or its ownership is unclear'
        return lead + ('. Also checked: ' + '; '.join(parts) if parts else '')
    if parts:
        return 'no website could be proven to belong to this company: ' + '; '.join(parts)
    if by.get('missing') and len(by) == 1:
        return 'none found: no website is registered with Brønnøysund, and none of the ' + str(len(by['missing'])) + ' likely domain names exist'
    return plain_reasons(codes, 'no supported website was found in the checked sources')


def section_reason(family, state, codes, envelope):
    if family == 'website':
        return website_reason(envelope, state, codes)
    if family == 'hiring':
        if state == 'not_available':
            return "no active ads from this company or its registered workplaces in NAV's public job feed"
        return "NAV's job feed could not be fully checked during the run (" + plain_reasons(codes, 'incomplete check') + ')'
    if family == 'subunits' and state == 'not_available':
        return 'no separately registered workplaces besides the company itself'
    if family == 'accounts' and state == 'not_available':
        return 'no annual accounts are on file with the Register of Company Accounts'
    if family == 'roles' and state == 'not_available':
        return 'no roles are registered'
    return plain_reasons(codes, {'not_available': 'no supported items in the checked sources',
                                 'not_applicable': 'source not applicable', 'ambiguous': 'exact company attribution unproven',
                                 'blocked': 'source access refused'}.get(state, 'source request incomplete'))


def generate(synthesis, envelope):
    brief = Brief()

    def context(field, value):
        claim = ChangeClaim(id=digest(['snapshot-context', envelope.organisation_number, field, value]),
                            field=field, value=value, evidence_ids=[])
        brief.context_claims.append(claim)
        return claim.id

    # What: the cited analyst sentences (identity, scale, workplaces, website).
    from .analyst import generate as analyst_generate
    from .validate import permitted
    analyst = analyst_generate(envelope)
    contexts = {c.id: c for c in analyst.context_claims}
    for s in analyst.sentences:
        if s.sentence_type not in WHAT_TYPES:
            continue
        brief.what.append(Sentence(text=s.text, claim_ids=s.claim_ids, value_kind=s.value_kind,
                                   count=s.count, record_type=s.record_type))
        for cid in s.claim_ids:
            if cid in contexts and all(c.id != cid for c in brief.context_claims):
                brief.context_claims.append(contexts[cid])
    if not brief.what:
        cid = context('snapshot.identity', {'state': envelope.run.sections.get('identity', 'failed')})
        brief.what.append(Sentence(text='Company identity could not be established from the checked sources.', claim_ids=[cid]))

    # What changed: snapshot differences first, then dated published events.
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
        brief.changes.append(Sentence(text='Since the previous run, ' + event.field.replace('_', ' ') + ' changed: ' + short(event.old_value) + ' → ' + short(event.new_value) + '.', claim_ids=[cid, *sides]))
    claims = sorted((c for c in envelope.claims if c.availability == 'available' and permitted(c, envelope)), key=lambda c: c.field)
    from .analyst import revenue_change, money
    trend = revenue_change(envelope, claims)
    if trend:
        pct, revenue, prior, currency = trend
        old_year, new_year = prior.reporting_period['fiscal_year'], revenue.reporting_period['fiscal_year']
        brief.changes.append(Sentence(
            text=('Revenue rose ' if pct > 0 else 'Revenue fell ') + format(abs(pct), 'f') + '%, from ' + money(prior.value, currency)
            + ' in FY' + str(old_year) + ' to ' + money(revenue.value, currency) + ' in FY' + str(new_year) + '.',
            claim_ids=[revenue.id, prior.id], value_kind='derived'))
    from .funding_news import news_sentences
    brief.changes.extend(news_sentences(envelope))
    for event in dated_events(claims):
        brief.changes.append(Sentence(text=event['text'], claim_ids=sorted(event['ids'])))
    if not envelope.changes:
        refresh = envelope.run.refresh
        previous = refresh.get('previous_completed_at')
        if refresh.get('mode') == 'baseline':
            if not brief.changes:
                cid = context('snapshot.refresh', {'mode': refresh.get('mode'), 'previous_completed_at': previous,
                                                 'changes': 0, 'dated_events': 0})
                brief.changes.append(Sentence(text='First observation; no previous snapshot and no dated changes in the checked sources.', claim_ids=[cid]))
        else:
            cid = context('snapshot.refresh', {'mode': refresh.get('mode'), 'previous_completed_at': previous,
                                             'changes': len(envelope.changes)})
            wording = ('No changes since the previous run on ' + short_date(previous) + '.' if previous and short_date(previous)
                       else 'No changes since the previous run; its date was not recorded.')
            brief.changes.append(Sentence(text=wording, claim_ids=[cid]))

    # What remains unknown: every gap with its recorded reason.
    stale = envelope.run.refresh.get('stale_sections', {})
    for family, state in sorted(envelope.run.sections.items()):
        if state == 'available' and family not in stale:
            continue
        codes = sorted({e.code for e in envelope.errors if e.section == family and e.code != 'website_candidates'})
        info = {'state': state, 'reasons': codes, 'stale': stale.get(family)}
        if family == 'website':
            info['candidates'] = dict(sorted(website_attempts(envelope).items()))
        cid = context('snapshot.section.' + family, info)
        label = LABELS.get(family, family.title())
        if family in stale:
            attempt = stale[family]
            day = short_date(attempt['failed_attempt_at']) or str(attempt['failed_attempt_at'])[:10]
            reason = plain_reasons(attempt.get('failure_codes', []), "the source couldn't be reached during the run")
            retained = 'found' if state == 'available' else STATES.get(state, 'previous')
            wording = f'{label}: stale; retained {retained} snapshot after the failed refresh on {day} ({reason}).'
        else:
            reason = section_reason(family, state, codes, envelope)
            wording = f'{label}: {reason}.'
        brief.unknowns.append(Sentence(text=wording[:1].upper() + wording[1:], claim_ids=[cid]))
    supported = {c.field for c in claims}
    if not any(f.startswith(('dated_item.','news_item.')) for f in supported) and envelope.run.sections.get('website') is not None:
        has_site = 'official_website' in supported
        cid = context('snapshot.news', {'verified_website': has_site, 'dated_articles': 0})
        brief.unknowns.append(Sentence(text='Company news: ' + ('no dated articles could be confirmed on its verified website.' if has_site
                                       else 'not checked, because no company website could be verified.'), claim_ids=[cid]))
    if 'identity.employees' not in supported and envelope.run.sections.get('identity') == 'available':
        cid = context('snapshot.employees', {'identity.employees': None})
        brief.unknowns.append(Sentence(text='Employee count: not reported to the register.', claim_ids=[cid]))
    years = sorted({str((c.reporting_period or {}).get('fiscal_year')) for c in claims
                    if c.family == 'accounts' and (c.reporting_period or {}).get('fiscal_year')})
    if len(years) == 1:
        cid = context('snapshot.accounts_years', {'fiscal_years': years})
        brief.unknowns.append(Sentence(text='Financial trend: only the ' + years[0] + ' accounts are available, so there is no year-on-year comparison.', claim_ids=[cid]))
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
