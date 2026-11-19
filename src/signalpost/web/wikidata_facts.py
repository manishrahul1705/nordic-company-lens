"""Attributed, revision-bound Wikidata facts; never replacements for registry facts."""
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from urllib.parse import parse_qs, urlsplit
from ..models.evidence import digest, canonical
from ..sources.extract import Section, Source, add
from .policy import normalize_url, domain, SOCIAL, DIRECTORIES, FREE_MAIL

FIELDS = {'P1448':('identity','official_name'), 'P571':('identity','inception'),
          'P159':('identity','headquarters'), 'P452':('identity','industry'),
          'P1128':('identity','employees'), 'P2139':('accounts','revenue'),
          'P856':('identity','official_website')}
GREGORIAN = 'http://www.wikidata.org/entity/Q1985727'


def checked_records(index, org, blobs):
    """Recheck immutable result rows, rather than trusting a mutable index entry."""
    from .wikidata import parse
    cache = {}
    for record in index.get('records', {}).get(org, []):
        try:
            if record.get('org') != org or not re.fullmatch(r'[1-9]\d*',record.get('revision','')):
                continue
            url = urlsplit(record.get('source_url',''))
            params = parse_qs(url.query)
            query = params.get('query',[''])[0]
            if (url.scheme != 'https' or url.hostname != 'query.wikidata.org' or url.path != '/sparql'
                    or url.username or url.password or url.port not in (None,443)
                    or params.get('format') != ['json'] or 'wdt:P2333 ?org' not in query
                    or json.dumps(org) not in query or '?revision' not in query):
                continue
            sha = record['sha']
            if sha not in cache:
                body = (blobs.directory/sha).read_bytes()
                if hashlib.sha256(body).hexdigest() != sha:
                    continue
                cache[sha] = body, {r['locator']:r for r in parse(body,{org})}
            body, rows = cache[sha]
            raw = rows.get(record['locator'])
            if not raw or any(record.get(key) != value for key,value in raw.items()):
                continue
            yield record, body
        except (OSError,ValueError,KeyError,TypeError):
            continue


def source(record, body):
    item = record['item'].rsplit('/',1)[1]
    revision_url = f"https://www.wikidata.org/w/index.php?title={item}&oldid={record['revision']}"
    return Source(record['source_url'],body,record['sha'],record['retrieved_at'],
                  f"Wikidata {item}, revision {record['revision']}; {revision_url}; CC0")


def stamp(section, record):
    claim = section.claims[-1]
    claim.reasons.update(wikidata_property=record['property'],wikidata_item=record['item'],
                         wikidata_revision=record['revision'],source='Wikidata (CC0)')


def time_value(record, qualifier=False):
    value = record.get('pointInTime' if qualifier else 'value','')
    precision = record.get('pointPrecision' if qualifier else 'precision','')
    calendar = record.get('pointCalendar' if qualifier else 'calendar','')
    if not re.fullmatch(r'\+?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',value):
        return None
    if not str(precision).isdigit() or not 9 <= int(precision) <= 14 or calendar != GREGORIAN:
        return None
    try:
        datetime.fromisoformat(value.lstrip('+').replace('Z','+00:00'))
    except ValueError:
        return None
    return {'time':value, 'precision':int(precision), 'calendar':calendar}


def fact_value(record):
    prop, raw = record['property'],record['value']
    if prop == 'P1448':
        return {'text':raw,'language':record.get('language')} if raw.strip() and record.get('value_type') == 'literal' else None
    if prop == 'P571':
        return time_value(record)
    if prop in {'P159','P452'}:
        if record.get('value_type') != 'uri' or not re.fullmatch(r'https?://www\.wikidata\.org/entity/Q[1-9]\d*',raw):
            return None
        value = {'entity':raw}
        if record.get('valueLabel'):
            value.update(label=record['valueLabel'],label_language=record.get('label_language'))
        return value
    if prop in {'P1128','P2139'}:
        point = time_value(record,True)
        if not point or len(raw) > 64 or record.get('value_type') != 'literal':
            return None
        try:
            amount = Decimal(raw)
        except InvalidOperation:
            return None
        if not amount.is_finite() or amount < 0 or (prop == 'P1128' and amount != amount.to_integral_value()):
            return None
        unit = record.get('unit')
        if prop == 'P1128' and unit not in {'1','http://www.wikidata.org/entity/Q199','https://www.wikidata.org/entity/Q199'}:
            return None
        if prop == 'P2139' and not re.fullmatch(r'https?://www\.wikidata\.org/entity/Q[1-9]\d*',unit or ''):
            return None
        value = {'amount':raw, 'unit':unit, 'point_in_time':point}
        if record.get('currencyCode'):
            value['currency'] = record['currencyCode']
        return value
    if prop == 'P856':
        url = normalize_url(raw)
        if record.get('value_type') == 'uri' and url and domain(url) not in SOCIAL|DIRECTORIES|FREE_MAIL:
            return url
    return None


def date_matches(stamp, date):
    width = {9:4,10:7}.get(stamp['precision'],10)
    return stamp['time'].lstrip('+')[:width] == str(date)[:width]


def url_key(value):
    url = normalize_url(value)
    if not url:
        return None
    p = urlsplit(url)
    return p.hostname.removeprefix('www.'),p.path.rstrip('/'),p.query


def compare(record, value, row):
    """Return an explicit disagreement only for comparable registry facts."""
    registry = {c.field:c for c in row.claims if c.availability == 'available'
                and not c.field.startswith(('identity.wikidata.','accounts.wikidata.'))}
    prop = record['property']
    field = {'P1448':'identity.legal_name','P571':'identity.founding_date','P856':'identity.registered_website',
             'P1128':'identity.employees'}.get(prop)
    current = registry.get(field)
    if prop == 'P2139':
        point = value['point_in_time']
        for candidate in registry.values():
            period = candidate.reporting_period or {}
            if candidate.family != 'accounts' or not candidate.field.endswith('.revenue'):
                continue
            annual = (point['precision']==9 and period.get('period_start')==point['time'][:4]+'-01-01'
                      and period.get('period_end')==point['time'][:4]+'-12-31')
            end_match = point['precision']>=11 and date_matches(point,period.get('period_end'))
            if ((annual or end_match) and value.get('currency') and value.get('currency') == period.get('currency')
                    and period.get('unit') == value.get('currency')):
                current = candidate
                break
    if current is None:
        return None
    comparable = True
    if prop == 'P1448':
        equal = canonical(value['text']) == canonical(current.value)
    elif prop == 'P571':
        equal = date_matches(value,current.value)
    elif prop == 'P856':
        equal = url_key(value) == url_key(current.value)
    else:
        equal = Decimal(value['amount']) == Decimal(str(current.value))
        if prop == 'P1128':
            dates = [registry[k].value for k in ('identity.employee_count_registration_date',
                     'identity.employee_count_nav_registration_date') if k in registry]
            comparable = value['point_in_time']['precision']>=11 and any(date_matches(value['point_in_time'],d) for d in dates)
    if equal:
        return None
    return {'status':'disagreement' if comparable else 'different_values_different_or_unknown_dates',
            'property':prop, 'registry_claim_id':current.id, 'registry_value':current.value,
            'registry_evidence_ids':current.evidence_ids, 'wikidata_value':value}


def publish(index, org, row, blobs):
    section = Section()
    diagnostics = row.run.refresh.setdefault('wikidata',{'disagreements':[],'comparisons':[],'withheld':[]})
    state=index.get('company_states',{}).get(org)
    diagnostics['state']=('checked' if state=='checked' or (state is None and org in index.get('records',{}))
                          else 'disabled' if index.get('metrics',{}).get('status')=='disabled' else 'not_available_fetch_failed')
    # One property/statement/value, with a deterministic label preference. Avoid
    # multiplying facts because the same location has several language labels.
    choices = {}
    order = {'nb':0,'no':1,'nn':2,'en':3,None:4}
    for record, body in checked_records(index,org,blobs):
        if record['property'] not in FIELDS:
            continue
        key = tuple(record.get(k) for k in ('item','property','statement','value','language','pointInTime'))
        previous = choices.get(key)
        if previous is None or order.get(record.get('label_language'),5) < order.get(previous[0].get('label_language'),5):
            choices[key] = record,body
    known = {c.id for c in row.claims}
    for record, body in choices.values():
        value = fact_value(record)
        if value is None:
            diagnostics['withheld'].append({'property':record['property'],'reason':'missing_or_invalid_value_unit_or_time_metadata',
                                            'item':record['item'],'revision':record['revision'],'locator':record['locator']})
            continue
        family,name = FIELDS[record['property']]
        field = f'{family}.wikidata.{name}.'+digest([record['item'],record.get('statement'),record['value'],record.get('language'),record.get('pointInTime')])[:16]
        period = value.get('point_in_time') if isinstance(value,dict) else None
        add(section,source(record,body),org,family,field,value,record['locator'],reporting=period,
            source_class='wikidata',method='signalpost.wikidata.fact.v1')
        stamp(section,record)
        section.claims[-1].reasons['label'] = 'Wikidata: '+name.replace('_',' ')
        comparison = compare(record,value,row)
        if comparison:
            comparison.update(wikidata_evidence_ids=section.claims[-1].evidence_ids,
                              item=record['item'],revision=record['revision'])
            diagnostics['disagreements' if comparison['status']=='disagreement' else 'comparisons'].append(comparison)
        if comparison and comparison['status'] == 'disagreement':
            section.claims.pop()  # Keep its exact evidence for the disagreement record.
        elif section.claims[-1].id in known:
            section.claims.pop()
        else:
            known.add(section.claims[-1].id)
    row.claims.extend(section.claims)
    evidence = {e.id:e for e in row.evidence}
    evidence.update({e.id:e for e in section.evidence})
    row.evidence = list(evidence.values())


def enforce_evidence(row, blobs):
    """Carry-forward and publication must satisfy today's revision/identity rule."""
    from .wikidata import parse, social_url
    evidence={e.id:e for e in row.evidence}
    keep=[]
    for claim in row.claims:
        refs=[evidence[ref] for ref in claim.evidence_ids if ref in evidence]
        is_fact=claim.field.startswith(('identity.wikidata.','accounts.wikidata.'))
        if not is_fact and (not claim.field.startswith('social_profile.') or not any(e.source_class=='wikidata' for e in refs)):
            keep.append(claim);continue
        valid=[]
        for ev in refs:
            if ev.source_class!='wikidata':
                valid.append(ev.id);continue
            try:
                body=(blobs.directory/ev.content_sha256).read_bytes()
                record=next(r for r in parse(body,{row.organisation_number}) if r['locator']==ev.locator)
                record.update(sha=ev.content_sha256,retrieved_at=ev.retrieved_at,source_url=ev.source_url)
                index={'records':{row.organisation_number:[record]}}
                if not list(checked_records(index,row.organisation_number,blobs)):
                    continue
                if is_fact:
                    matches=record['property'] in FIELDS and fact_value(record)==claim.value
                    conflict=compare(record,claim.value,row) if matches else None
                    if conflict and conflict['status']=='disagreement':
                        conflict.update(wikidata_evidence_ids=[ev.id],item=record['item'],revision=record['revision'])
                        row.run.refresh.setdefault('wikidata',{}).setdefault('disagreements',[]).append(conflict)
                        matches=False
                else:
                    matches=social_url(record)==claim.value.get('url')
                if matches:valid.append(ev.id)
            except (OSError,ValueError,KeyError,TypeError,StopIteration):
                continue
        if valid and (not is_fact or any(evidence[ref].source_class=='wikidata' for ref in valid)):
            claim.evidence_ids=valid
            if not any(evidence[ref].source_class=='wikidata' for ref in valid):
                claim.reasons={k:v for k,v in claim.reasons.items() if not k.startswith('wikidata_')}
            keep.append(claim)
    removed={c.field for c in row.claims}-{c.field for c in keep}
    row.claims=keep
    if hasattr(row,'changes'):
        row.changes=[c for c in row.changes if c.field not in removed]
    if hasattr(row.run,'legal_identity'):
        row.run.legal_identity={c.field.removeprefix('identity.'):c.value for c in keep if c.family=='identity'}
    if hasattr(getattr(row,'profile',None),'values'):
        row.profile.values={c.field:c.value for c in keep}
