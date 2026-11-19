"""Explicit relationships and registered mandates from the company's BRREG lookup.

The group endpoint returns a whole tree. Only edges naming the requested company
are used. Possible signers and statutory/interpreted combinations are not grants.
"""
import asyncio
import json
from ..budget import SourceFailure
from ..workers import offload
from .extract import Section, add, response_source
from .fact_depth import label

GROUP = 'https://data.brreg.no/enhetsregisteret/api/konsernstruktur/'
MANDATE = 'https://data.brreg.no/fullmakt/enheter/'


def nodes(node, path=''):
    if not isinstance(node, dict):
        return
    yield node, path
    for i, child in enumerate(node.get('children', [])):
        yield from nodes(child, f'{path}/children/{i}')


def group_extract(org, data, source):
    entries = list(nodes(data))
    own = [(node, path) for node, path in entries if str(node.get('organisasjonsnummer')) == org]
    if len(own) != 1:
        raise SourceFailure('wrong_company', 'Requested company must occur exactly once in its group record')
    section = Section()
    node, path = own[0]
    parent = node.get('parentOrganisasjonsnummer')
    if parent and str(parent) != org:
        value = {key: node[key] for key in ('parentOrganisasjonsnummer', 'parentNavn', 'grunnlag', 'dato', 'knytningsform') if key in node}
        add(section, source, org, 'identity', 'identity.group_structure.parent', value, path or '/')
        label(section, 'Registered group parent')
    for child, child_path in entries:
        number = str(child.get('organisasjonsnummer', ''))
        if str(child.get('parentOrganisasjonsnummer')) != org or not number or number == org:
            continue
        value = {key: child[key] for key in ('organisasjonsnummer', 'navn', 'parentOrganisasjonsnummer', 'parentNavn', 'grunnlag', 'dato', 'knytningsform') if key in child}
        add(section, source, org, 'identity', f'identity.group_structure.subsidiary.{number}', value, child_path or '/')
        label(section, 'Registered group subsidiary')
    return section


def public_basis(value):
    """Retain registered wording and joint conditions, without personal birth dates."""
    if isinstance(value, dict):
        return {key: public_basis(item) for key, item in value.items()
                if key not in {'fodselsdato', 'fodselsnummer', 'dNummer'}}
    if isinstance(value, list):
        return [public_basis(item) for item in value]
    return value


def mandate_extract(org, kind, data, source):
    if str(data.get('enhet', {}).get('organisasjonsnummer')) != org:
        raise SourceFailure('wrong_company')
    section = Section()
    # This is the actually registered basis, not muligeSigneringsRoller or
    # signeringsKombinasjon (which can include statutory rights inferred by BRREG).
    basis = data.get('signeringsGrunnlag', {}).get('signaturProkuraRoller')
    if isinstance(basis, dict) and (basis.get('signaturProkuraFritekst') or basis.get('personRolleGrunnlag')):
        value = public_basis(basis)
        if value:
            add(section, source, org, 'roles', f'roles.{kind}.registered_basis', value,
                '/signeringsGrunnlag/signaturProkuraRoller')
            label(section, 'Registered signature rights' if kind == 'signatur' else 'Registered procuration')
    return section


def extract_response(org, kind, response):
    if response.status != 200:
        raise SourceFailure('extended_http_' + str(response.status))
    data = json.loads(response.body)
    source = response_source(response)
    return group_extract(org, data, source) if kind == 'group_structure' else mandate_extract(org, kind, data, source)


async def enrich(org, row, http, config):
    requests = []
    if config.group_structure and any(c.field == 'identity.part_of_group' and c.value is True and c.availability == 'available' for c in row.claims):
        requests.append(('group_structure', GROUP + org))
    if config.signature_rights:
        requests += [(kind, MANDATE + org + '/' + kind) for kind in ('signatur', 'prokura')]
    states = row.run.refresh.setdefault('brreg_extended', {})

    async def fetch(kind, url):
        states[kind] = {'state': 'not_available_fetch_failed', 'reason': 'request_incomplete', 'url': url}
        try:
            response = await http.get(url, org)
            section = await offload(extract_response, org, kind, response)
            states[kind] = {'state': 'available' if section.claims else 'not_available',
                            'reason': None if section.claims else 'no_explicit_registered_basis', 'url': url}
            row.claims.extend(section.claims)
            known = {e.id for e in row.evidence}
            row.evidence.extend(e for e in section.evidence if e.id not in known)
        except SourceFailure as exc:
            states[kind] = {'state': 'not_available_fetch_failed', 'reason': exc.code, 'url': url}
        except TimeoutError:
            # A transport can surface a native asyncio timeout rather than an
            # httpx timeout. Keep it scoped to this optional registry lookup.
            states[kind] = {'state': 'not_available_fetch_failed', 'reason': 'timeout', 'url': url}
        except (ValueError, TypeError, KeyError):
            states[kind] = {'state': 'not_available_fetch_failed', 'reason': 'invalid_response', 'url': url}
        return Section()

    await asyncio.gather(*(fetch(kind, url) for kind, url in requests))
