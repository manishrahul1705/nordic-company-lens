"""Final cited briefing frames never infer parents or confuse buyer and winner."""
import pytest
from signalpost.synthesis.analyst import generate,validate
from tests.test_synthesis import envelope


def add(row,field,value,family='identity'):
    seed=next(c for c in row.claims if c.field=='identity.legal_name')
    claim=seed.model_copy(update={'id':'polish-'+field,'field':field,'value':value,'family':family})
    row.claims.append(claim);return claim

@pytest.fixture
def permit(monkeypatch):
    from signalpost.synthesis import validate as gate
    original=gate.permitted
    monkeypatch.setattr(gate,'permitted',lambda c,e:c.id.startswith('polish-') or original(c,e))

@pytest.mark.parametrize('kind',['direct_parent','ultimate_parent'])
def test_gleif_parent_clause_bound_to_claim(tmp_path,permit,kind):
    row,_=envelope(tmp_path);parent=add(row,'identity.gleif.'+kind,{'name':'Recorded Parent ASA','lei':'PARENT'})
    brief=generate(row);sentence=next(s for s in brief.sentences if '(GLEIF)' in s.text)
    assert 'It is owned by Recorded Parent ASA (GLEIF).' in sentence.text
    assert parent.id in sentence.claim_ids
    assert validate(brief,row)==brief


def test_name_only_never_implies_parent(tmp_path):
    row,_=envelope(tmp_path);assert 'owned by' not in ' '.join(s.text for s in generate(row).sentences)

@pytest.mark.parametrize('role',['winner','buyer'])
def test_award_role_and_exact_buyer_frame(tmp_path,permit,role):
    row,_=envelope(tmp_path);c=add(row,'procurement_award.test',{'date':'2026-11-01','buyer':['Oslo Municipality'],'matched_role':role,'title':'Contract services'},'activity')
    sentence=next(s for s in generate(row).sentences if s.sentence_type=='d')
    assert sentence.claim_ids==[c.id]
    assert ('It won a public contract from Oslo Municipality (1 Nov 2026, TED).'==sentence.text)==(role=='winner')
    assert 'NOK' not in sentence.text


def test_newest_major_event_wins_over_article(tmp_path,permit):
    row,_=envelope(tmp_path)
    add(row,'dated_item.old',{'date':'2026-01-01','title':'Old article'},'activity')
    add(row,'procurement_award.new',{'date':'2026-11-01','buyer':['Buyer AS'],'matched_role':'winner','title':'Award'},'activity')
    assert 'It won a public contract' in next(s.text for s in generate(row).sentences if s.sentence_type=='d')
    add(row,'registry_change.newest',{'date':'2026-11-02','changed_field':'/navn'},'activity')
    assert 'registered name change' in next(s.text for s in generate(row).sentences if s.sentence_type=='d')


def test_sparse_two_or_three_cited_sentences_and_refresh_stability(tmp_path):
    row,_=envelope(tmp_path);row.claims=[c for c in row.claims if c.family in {'identity','roles'} and c.field!='identity.employees']
    first=generate(row);assert 2<=len(first.sentences)<=3
    assert all(s.claim_ids for s in first.sentences)
    row.run.refresh.update(mode='refresh',previous_completed_at='2026-11-11T00:00:00Z')
    assert first==generate(row)
    assert validate(first,row)==first
