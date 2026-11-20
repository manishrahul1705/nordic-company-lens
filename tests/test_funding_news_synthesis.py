import pytest
from signalpost.models.synthesis import Sentence
from signalpost.synthesis.funding_news import funding_sentence,news_sentences
from signalpost.synthesis.validate import sentence_error
from signalpost.models.evidence import digest,canonical
from tests.test_funding_snapshots import envelope,research,aid,install
from signalpost.sources.funding_snapshots import publish
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section,Source,add
from signalpost.models.evidence import utc_now


def funded(tmp_path,monkeypatch):
    install(tmp_path,monkeypatch,[{'source_row':1,'source_cells':research()}]);e=envelope();publish(e,BlobStore(tmp_path/'state'));return e


def test_funding_sentence_binds_published_evidence_and_total_project_award(tmp_path,monkeypatch):
    e=funded(tmp_path,monkeypatch);s=funding_sentence(e)
    assert 'total project award' in s.text and 'shared with collaborators' in s.text
    assert all(w not in s.text.lower() for w in ['received','cash','exclusive share'])
    assert sentence_error(s,e) is None
    assert all(any(c.id==cid and c.availability=='available' and c.evidence_ids for c in e.claims) for cid in s.claim_ids)


def test_absence_of_funding_adds_no_negative_sentence():assert funding_sentence(envelope()) is None


@pytest.mark.parametrize('instrument',['tax benefit','grant','guarantee'])
@pytest.mark.parametrize('subunit',[False,True])
def test_instrument_and_recipient_scope_retained(tmp_path,monkeypatch,instrument,subunit):
    e=funded(tmp_path,monkeypatch);section=Section();v={'aid_id':'test','instrument_type':instrument,'recipient_orgnr':'912845575' if subunit else e.organisation_number,'specified_subunit_orgnr':'912845575'}
    if subunit:v['matched_via']='registered recipient subunit 912845575'
    raw=b'{}';add(section,Source('https://stotte.brreg.no/example',raw,'a'*64,utc_now()),e.organisation_number,'funding','state_aid.test',v,'/')
    e.claims.extend(section.claims);e.evidence.extend(section.evidence);s=funding_sentence(e)
    assert instrument in s.text and ('registered recipient subunit' if subunit else 'legal recipient this company') in s.text
    assert 'specified recipient subunit' in s.text and sentence_error(s,e) is None


def news_row(kind='feed publication',n=5):
    e=envelope();section=Section();source=Source('https://example.no/feed',b'news','a'*64,utc_now())
    add(section,source,e.organisation_number,'website','official_website',{'identity_level':'VERIFIED','final_url':'https://example.no/'},'/');proof=section.claims[0]
    for i in range(n):add(section,source,e.organisation_number,'activity','news_item.'+str(i),{'title':'Story '+str(i),'date':'2026-11-'+str(i+1).zfill(2),'url':'https://example.no/news/'+str(i),'date_kind':kind,'identity_claim_id':proof.id},'/')
    e.claims.extend(section.claims);e.evidence.extend(section.evidence);return e


def test_latest_three_news_are_attributed_and_dated():
    e=news_row();sentences=news_sentences(e)
    assert len(sentences)==3 and 'Story 4' in sentences[0].text
    assert all('published by the company' in s.text and sentence_error(s,e) is None for s in sentences)


@pytest.mark.parametrize('kind,label',[('sitemap last modification (not publication date)','last modification date'),('feed update','update date'),('page explicit date','publication date')])
def test_date_kind_is_not_strengthened(kind,label):
    e=news_row(kind,1);s=news_sentences(e)[0];assert label in s.text and sentence_error(s,e) is None


def test_news_without_verified_published_identity_is_excluded():
    e=news_row();e.claims=[c for c in e.claims if c.field!='official_website'];assert news_sentences(e)==[]


def test_unchanged_validator_rejects_unbacked_date():
    e=news_row(n=1);s=news_sentences(e)[0];s.text=s.text.replace('2026-11-01','2026-11-02');assert sentence_error(s,e)=='unverified_date'


def test_unchanged_validator_rejects_unavailable_citation():
    e=news_row(n=1);s=news_sentences(e)[0];s.claim_ids=['nonexistent'];assert sentence_error(s,e)=='missing_or_unavailable_claim'


def test_no_funding_gap_introduced():
    from signalpost.synthesis.sections_extra import not_established
    assert not any('grant' in s.text.lower() or 'funding' in s.text.lower() for s in not_established(envelope()))
