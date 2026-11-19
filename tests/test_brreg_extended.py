import asyncio
import hashlib
import json
from types import SimpleNamespace
import pytest
from signalpost.budget import Budget, SourceFailure
from signalpost.config import Config
from signalpost.sources.brreg_extended import GROUP, MANDATE, enrich, group_extract, mandate_extract
from signalpost.sources.extract import Source
from signalpost.sources.http import Http, Response

ORG = '991247610'
OTHER = '938641862'


def source(data, url='https://data.brreg.no/example'):
    body = json.dumps(data, ensure_ascii=False).encode()
    return Source(url, body, hashlib.sha256(body).hexdigest(), '2026-11-19T00:00:00Z')


def test_group_only_explicit_edges_of_requested_company():
    data = {'organisasjonsnummer': OTHER, 'children': [
        {'organisasjonsnummer': ORG, 'parentOrganisasjonsnummer': OTHER, 'parentNavn': 'Parent',
         'children': [{'organisasjonsnummer': '976645677', 'navn': 'Child', 'parentOrganisasjonsnummer': ORG}]},
        {'organisasjonsnummer': '934500644', 'parentOrganisasjonsnummer': OTHER}]}
    section = group_extract(ORG, data, source(data))
    assert [c.field for c in section.claims] == ['identity.group_structure.parent', 'identity.group_structure.subsidiary.976645677']
    assert section.claims[0].value['parentOrganisasjonsnummer'] == OTHER
    assert section.evidence[0].locator == '/children/0'
    assert section.evidence[1].locator == '/children/0/children/0'


@pytest.mark.parametrize('data', [{'organisasjonsnummer': OTHER}, {'organisasjonsnummer': ORG, 'children': [{'organisasjonsnummer': ORG}]}])
def test_group_requires_unique_own_node(data):
    with pytest.raises(SourceFailure, match='Requested company'):
        group_extract(ORG, data, source(data))


def test_group_does_not_infer_parent_from_tree_nesting():
    data = {'organisasjonsnummer': OTHER, 'children': [{'organisasjonsnummer': ORG}]}
    assert not group_extract(ORG, data, source(data)).claims


@pytest.mark.parametrize('kind', ['signatur', 'prokura'])
def test_registered_basis_keeps_joint_conditions_and_omits_birthdates(kind):
    basis = {'signaturProkuraFritekst': ['To styremedlemmer i fellesskap'], 'personRolleGrunnlag': [
        {'navn': 'A Person', 'fodselsdato': '01.01.1980', 'rolle': {'kode': 'SIGN'}}]}
    data = {'enhet': {'organisasjonsnummer': ORG}, 'signeringsGrunnlag': {'signaturProkuraRoller': basis}}
    section = mandate_extract(ORG, kind, data, source(data))
    assert len(section.claims) == 1
    value = section.claims[0].value
    assert value['signaturProkuraFritekst'] == basis['signaturProkuraFritekst']
    assert 'fodselsdato' not in value['personRolleGrunnlag'][0]
    assert value['personRolleGrunnlag'][0]['navn'] == 'A Person'
    assert section.evidence[0].locator == '/signeringsGrunnlag/signaturProkuraRoller'


def test_possible_and_interpreted_signers_are_not_registered_grants():
    data = {'enhet': {'organisasjonsnummer': ORG}, 'signeringsGrunnlag': {'muligeSigneringsRoller': {'personRolleGrunnlag': [{'navn': 'Director'}]}},
            'signeringsKombinasjon': {'kombinasjon': [{'tekstforklaring': 'Styret i fellesskap'}]}}
    assert not mandate_extract(ORG, 'signatur', data, source(data)).claims


def test_mandate_wrong_company_rejected():
    data = {'enhet': {'organisasjonsnummer': OTHER}}
    with pytest.raises(SourceFailure, match='wrong_company'):
        mandate_extract(ORG, 'signatur', data, source(data))


def test_empty_registered_basis_is_not_a_grant():
    data = {'enhet': {'organisasjonsnummer': ORG}, 'signeringsGrunnlag': {
        'signaturProkuraRoller': {'signaturProkuraFritekst': [], 'personRolleGrunnlag': []}}}
    assert not mandate_extract(ORG, 'signatur', data, source(data)).claims


def test_site_keeps_signature_rights_label():
    from signalpost.site import fact
    data = {'enhet': {'organisasjonsnummer': ORG}, 'signeringsGrunnlag': {
        'signaturProkuraRoller': {'signaturProkuraFritekst': ['Styrets leder alene']}}}
    section = mandate_extract(ORG, 'signatur', data, source(data))
    html = fact(section.claims[0].model_dump(), {e.id:e.model_dump() for e in section.evidence})
    assert 'Registered signature rights' in html
    assert 'Styrets leder alene' in html


@pytest.mark.parametrize('flag,group_calls', [(False, 0), (True, 1)])
def test_requests_are_gated_and_failures_do_not_erase_existing_claims(flag, group_calls):
    row = SimpleNamespace(claims=[SimpleNamespace(field='identity.part_of_group', value=flag, availability='available')],
                          evidence=[], run=SimpleNamespace(refresh={}))
    calls = []
    class Fake:
        async def get(self, url, org):
            calls.append(url)
            raise SourceFailure('extended_http_503')
    asyncio.run(enrich(ORG, row, Fake(), SimpleNamespace(group_structure=True, signature_rights=True)))
    assert len(calls) == 2 + group_calls
    assert sum(url.startswith(GROUP) for url in calls) == group_calls
    assert set(row.run.refresh['brreg_extended']) == ({'group_structure'} if flag else set()) | {'signatur', 'prokura'}
    assert all(s['state'] == 'not_available_fetch_failed' for s in row.run.refresh['brreg_extended'].values())
    assert len(row.claims) == 1


def test_mandates_requested_even_without_available_identity():
    row = SimpleNamespace(claims=[], evidence=[], run=SimpleNamespace(refresh={}))
    calls = []
    class Fake:
        async def get(self, url, org):
            calls.append(url)
            body = json.dumps({'enhet': {'organisasjonsnummer': org}}).encode()
            return Response(body, 200, url, '2026-11-19T00:00:00Z', hashlib.sha256(body).hexdigest())
    asyncio.run(enrich(ORG, row, Fake(), SimpleNamespace(group_structure=True, signature_rights=True)))
    assert calls == [MANDATE + ORG + '/signatur', MANDATE + ORG + '/prokura']
    assert not row.claims


def test_native_timeout_is_scoped_to_one_mandate():
    row = SimpleNamespace(claims=[], evidence=[], run=SimpleNamespace(refresh={}))
    class Fake:
        async def get(self, url, org):
            if url.endswith('/signatur'):
                raise TimeoutError('native transport timeout')
            body = json.dumps({'enhet': {'organisasjonsnummer': org}, 'signeringsGrunnlag': {
                'signaturProkuraRoller': {'signaturProkuraFritekst': 'Daglig leder alene.'}}}).encode()
            return Response(body, 200, url, '2026-11-19T00:00:00Z', hashlib.sha256(body).hexdigest())
    asyncio.run(enrich(ORG, row, Fake(), SimpleNamespace(group_structure=False, signature_rights=True)))
    assert row.run.refresh['brreg_extended']['signatur']['reason'] == 'timeout'
    assert row.run.refresh['brreg_extended']['prokura']['state'] == 'available'
    assert [c.field for c in row.claims] == ['roles.prokura.registered_basis']


def test_added_requests_obey_company_cap(tmp_path):
    inputs = tmp_path / 'inputs.jsonl'
    inputs.write_text(json.dumps({'organisation_number': ORG}) + '\n', encoding='utf-8')
    config = Config(organisations=inputs, output=tmp_path/'out', report=tmp_path/'report')
    budget = Budget(config)
    budget.by_company[ORG] = 40
    class Client:
        async def get(self, *args, **kwargs):
            raise AssertionError('No network request allowed beyond the cap')
    row = SimpleNamespace(claims=[], evidence=[], run=SimpleNamespace(refresh={}))
    asyncio.run(enrich(ORG, row, Http(Client(), config, budget, None), SimpleNamespace(group_structure=True, signature_rights=True)))
    assert len(budget.events) == 0
    assert all(s['reason'] == 'company_budget_exhausted' for s in row.run.refresh['brreg_extended'].values())


@pytest.mark.parametrize('identity_available', [True, False])
def test_runner_retains_enrichment_after_primary_sections(tmp_path, identity_available):
    import httpx
    from signalpost.runner import run
    inputs = tmp_path/'inputs.txt'
    inputs.write_text(ORG, encoding='utf-8')
    calls = []
    def respond(request):
        path = request.url.path
        calls.append(path)
        if '/fullmakt/' in path:
            return httpx.Response(200, json={'enhet': {'organisasjonsnummer': ORG}, 'signeringsGrunnlag': {
                'signaturProkuraRoller': {'signaturProkuraFritekst': ['Styrets leder alene']}}})
        if '/konsernstruktur/' in path:
            return httpx.Response(200, json={'organisasjonsnummer': ORG, 'parentOrganisasjonsnummer': OTHER, 'parentNavn': 'Parent'})
        if path.endswith('/roller'):
            return httpx.Response(200, json={'organisasjonsnummer': ORG, 'rollegrupper': []})
        if '/underenheter' in path:
            return httpx.Response(200, json={'_embedded': {'underenheter': []}, 'page': {'totalPages': 1}})
        if '/regnskapsregisteret/' in path:
            return httpx.Response(200, json=[])
        return httpx.Response(200 if identity_available else 404, json={
            'organisasjonsnummer': ORG, 'navn': 'Example AS', 'erIKonsern': True})
    cfg = Config(organisations=inputs, output=tmp_path/'out.jsonl', report=tmp_path/'report.json',
                 state_dir=tmp_path/'state', wikidata=False, registry_changes=False,
                 group_structure=True, signature_rights=True, prevent_system_sleep=False)
    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await run(cfg, client=client)
    report = asyncio.run(execute())
    row = json.loads(cfg.output.read_text(encoding='utf-8'))
    fields = {c['field'] for c in row['claims'] if c['availability'] == 'available'}
    assert {'roles.signatur.registered_basis', 'roles.prokura.registered_basis'} <= fields
    assert ('identity.group_structure.parent' in fields) == identity_available
    assert sum('/fullmakt/' in path for path in calls) == 2
    assert report['max_requests_per_company'] <= 40


def test_failed_group_refresh_does_not_claim_relationship_removed():
    from signalpost.runner import placeholder
    from signalpost.refresh.diff import apply
    old = placeholder(ORG, 'old', '2026-11-18T00:00:00Z')
    old.run.sections = {family: 'available' for family in old.run.sections}
    old.errors = []
    data = {'organisasjonsnummer': ORG, 'parentOrganisasjonsnummer': OTHER, 'parentNavn': 'Parent'}
    section = group_extract(ORG, data, source(data))
    old.claims, old.evidence = section.claims, section.evidence
    row = old.model_copy(deep=True)
    row.claims, row.evidence = [], []
    row.run.completed_at = '2026-11-19T00:00:00Z'
    row.run.refresh = {'brreg_extended': {'group_structure': {'state': 'not_available_fetch_failed', 'reason': 'extended_http_503'}}}
    apply(row, old.model_dump(), None)
    assert not row.changes
    assert len(row.claims) == 1
    assert row.claims[0].carried_forward
    assert row.claims[0].stale_since == row.run.completed_at
    assert row.evidence[0].id == old.evidence[0].id
    assert row.run.refresh['observation_changes'][0]['current_state'] == 'fetch_failed'
