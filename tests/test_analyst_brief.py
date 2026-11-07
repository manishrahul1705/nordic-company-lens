import pytest
from signalpost.synthesis.analyst import generate, validate, money, major_event, english_list
from tests.test_synthesis import envelope


def test_sparse_stable_cited_brief(tmp_path):
    row, _ = envelope(tmp_path)
    first = generate(row)
    assert first == generate(row)
    assert [s.sentence_type for s in first.sentences] == sorted(s.sentence_type for s in first.sentences)
    assert all(s.claim_ids for s in first.sentences)
    assert 1 <= len(first.sentences) <= 7
    assert validate(first, row) == first
    first.sentences[0].text += ' Leading successful business.'
    with pytest.raises(ValueError): validate(first, row)


@pytest.mark.parametrize('path', ['/datoAntallAnsatte', '/sisteInnsendteAarsregnskap', '/kapital/dato', '/registreringsdatoEnhetsregisteret'])
def test_minor_updates_are_not_news(path):
    assert major_event({'changed_field': path}) is None


@pytest.mark.parametrize('path', ['/navn', '/kapital/belop', '/forretningsadresse/postnummer', '/konkurs', '/roller'])
def test_only_explicit_major_fields(path):
    assert major_event({'changed_field': path})


def test_money_rounding():
    assert money(50400000) == 'NOK 50.4 million'
    assert money(1252) == 'NOK 1,252'
    assert money(100.0) == 'NOK 100'
    assert money(4200000,'EUR') == 'EUR 4.2 million'
    assert money(1000000)=='NOK 1.0 million'
    assert english_list(['Facebook','LinkedIn'])=='Facebook and LinkedIn'
    assert english_list(['Facebook','Instagram','LinkedIn'])=='Facebook, Instagram and LinkedIn'


def test_polished_employee_footprint_and_norwegian_quote(tmp_path,monkeypatch):
    row,_=envelope(tmp_path)
    seed=next(c for c in row.claims if c.field=='identity.legal_name')
    row.claims=[c for c in row.claims if not c.field.startswith('subunits.unit.') and c.field!='identity.employees']
    for field,value,family in [('identity.employees',38,'identity'),
        ('identity.statutory_purpose','Utvikle programvare.','identity'),
        ('subunits.unit.test',{'organisation_number':'988258229','address':{'kommune':'OSLO'}},'subunits')]:
        row.claims.append(seed.model_copy(update={'id':field,'field':field,'value':value,'family':family}))
    row.run.sections['subunits']='available'
    from signalpost.synthesis import validate as gate
    original=gate.permitted
    monkeypatch.setattr(gate,'permitted',lambda c,e: c.id==c.field or original(c,e))
    brief=generate(row)
    assert any(s.text=='It has 38 registered employees.' and s.claim_ids==['identity.employees'] for s in brief.sentences)
    assert any(s.text=='It has one registered workplace, in Oslo.' for s in brief.sentences)
    assert 'its registered purpose (in Norwegian) is \u00abUtvikle programvare\u00bb' in brief.sentences[0].text
    assert brief==generate(row)


@pytest.mark.parametrize('rich', [False, True])
def test_medium_and_rich_templates(tmp_path, monkeypatch, rich):
    from tests.test_websites import execute_web
    from signalpost.models.envelope import Envelope
    _, body, _, _ = execute_web(tmp_path, monkeypatch)
    row = Envelope.model_validate(body)
    if rich:
        seed = next(c for c in row.claims if c.field == 'official_website')
        row.claims.append(seed.model_copy(update={'id':'article', 'field':'dated_item.test', 'family':'activity',
            'value':{'title':'New production line opened', 'date':'2026-10-10', 'url':'https://example.no/news'}}))
    from signalpost.synthesis import validate as gate
    original = gate.permitted
    monkeypatch.setattr(gate, 'permitted', lambda c,e: c.id=='article' or original(c,e))
    brief = generate(row)
    text = ' '.join(s.text for s in brief.sentences)
    assert 'Its verified website is example.no' in text
    assert ('latest company-published article' in text) == rich
    assert not any(word in text.casefold().split() for word in ['leading','successful','strong','growing','forecast','recommend'])
    assert validate(brief,row) == brief


@pytest.mark.parametrize('currency', ['NOK','EUR'])
def test_company_scope_loss_and_prior_year(tmp_path,currency):
    row, _ = envelope(tmp_path)
    seed = next(c for c in row.claims if c.field == 'identity.legal_name')
    for year, revenue, profit in [('2025', 2000000, -500000), ('2024', 1000000, 1)]:
        for field, value in [('revenue', revenue), ('net_result', profit)]:
            row.claims.append(seed.model_copy(update={'id':year+field, 'family':'accounts', 'field':'accounts.year.'+year+'.'+field, 'value':value,
                'reporting_period':{'fiscal_year':year,'period_start':year+'-01-01','period_end':year+'-12-31','currency':currency,'unit':currency,'account_type':'SELSKAP'}}))
    # Reuse the real official accounts evidence to satisfy the source gate.
    accounts = next((c for c in row.claims if c.family=='accounts' and c.evidence_ids), None)
    if accounts:
        for c in row.claims:
            if c.id in {'2025revenue','2025net_result','2024revenue','2024net_result'}: c.evidence_ids=accounts.evidence_ids
    from signalpost.synthesis import validate as gate
    original=gate.permitted
    # Parsing arithmetic is isolated here; production still enforces the source gate.
    from unittest.mock import patch
    with patch.object(gate,'permitted',lambda c,e: True if c.id.startswith(('2024','2025')) else original(c,e)):
        text=' '.join(s.text for s in generate(row).sentences)
        assert 'loss of '+currency+' 500,000' in text and 'rose 100.0%' in text
        prior=next(c for c in row.claims if c.id=='2024revenue')
        prior.value=2000000
        assert '0.0%' not in ' '.join(s.text for s in generate(row).sentences)
        prior.value=4000000
        assert 'fell 50.0%' in ' '.join(s.text for s in generate(row).sentences)
        assert ('NOK' not in text) if currency=='EUR' else ('EUR' not in text)
        row.claims=[c for c in row.claims if not c.id.startswith('2024')]
        assert '%' not in ' '.join(s.text for s in generate(row).sentences)
        for c in row.claims:
            if c.id.startswith('2025'): c.reporting_period['account_type']='KONSERN'
        assert '2.0 million' not in ' '.join(s.text for s in generate(row).sentences)
