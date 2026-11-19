import json
import pytest
from signalpost.web.social_universe import assess,index,name_keys,handle_keys,registered_relations,ROWS,ARCHIVE_SHA
from signalpost.web.social_links import veto
from signalpost.runner import placeholder
from signalpost.sources.extract import Section,Source,add
from signalpost.models.evidence import utc_now
from signalpost.web.social import context_for_envelope

ORG='980362779'
OTHER='937920040'


def test_complete_pinned_universe_is_available():
    data=index()
    assert data['rows']==ROWS==411160 and len(data['names'])==411160
    assert data['archive_sha256']==ARCHIVE_SHA
    assert data['names'][OTHER]=='HALLMAKER AS'


@pytest.mark.parametrize('url,org,blocked,match',[
 ('https://instagram.com/hallmakergroup',ORG,True,OTHER),
 ('https://x.com/RentHallGlobal',ORG,False,None),
 ('https://facebook.com/valdresost','996979660',True,'914992605'),
 ('https://instagram.com/scenehuset','971558415',False,None),
])
def test_requested_real_handles_against_all_411160(url,org,blocked,match):
    result=assess(url,{'organisation_number':org})
    assert (result['state']=='withhold')==blocked
    if match:assert match in {r['organisation_number'] for r in result['matches']}


@pytest.mark.parametrize('name', ['HALLMAKER AS','Hallmaker A/S','AS Hallmaker'])
def test_name_normalisation_keeps_order_and_removes_legal_form(name):
    assert 'hallmaker' in name_keys(name)
    assert handle_keys('hallmakergroup')=={'hallmakergroup','hallmaker'}
    assert 'renthall' in handle_keys('renthallglobal')
    assert handle_keys('piano')=={'piano'}  # Do not strip arbitrary two-letter endings.


def relationship(kind,own=True,stale=False,source_class='official_registry'):
    row=placeholder(ORG,'test',utc_now());section=Section()
    target=ORG if own else '991247610'
    if kind=='subunit':
        field='subunits.unit.'+OTHER;family='subunits';value={'organisation_number':OTHER,'name':'Hallmaker AS'}
        url=f'https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet={target}&size=1000&page=0'
    elif kind=='parent':
        field='identity.group_structure.parent';family='identity';value={'parentOrganisasjonsnummer':OTHER,'parentNavn':'Hallmaker AS'}
        url='https://data.brreg.no/enhetsregisteret/api/konsernstruktur/'+target
    else:
        field='identity.group_structure.subsidiary.'+OTHER;family='identity'
        value={'organisasjonsnummer':OTHER,'parentOrganisasjonsnummer':ORG,'navn':'Hallmaker AS'}
        url='https://data.brreg.no/enhetsregisteret/api/konsernstruktur/'+target
    raw=json.dumps(value).encode();src=Source(url,raw,'a'*64,utc_now())
    add(section,src,ORG,family,field,value,'/',source_class=source_class)
    section.claims[0].carried_forward=stale
    row.claims,row.evidence=section.claims,section.evidence
    return row


@pytest.mark.parametrize('kind',['parent','subsidiary','subunit'])
def test_only_explicit_own_registry_relationships_allow_collision(kind):
    row=relationship(kind);context=context_for_envelope(row)
    result=assess('https://instagram.com/hallmakergroup',context)
    assert result['state']=='allow'
    relation=result['matches'][0]['permitted_registry_relationship']
    assert relation['kind']==kind and relation['claim_id']==row.claims[0].id and relation['evidence_ids']


@pytest.mark.parametrize('kind',['parent','subsidiary','subunit'])
@pytest.mark.parametrize('bad', ['wrong_subject','stale','website_only'])
def test_relationship_exceptions_fail_closed(kind,bad):
    row=relationship(kind,own=bad!='wrong_subject',stale=bad=='stale',
                     source_class='company_owned' if bad=='website_only' else 'official_registry')
    assert not registered_relations(row)
    assert assess('https://instagram.com/hallmakergroup',context_for_envelope(row))['state']=='withhold'


def test_one_allowed_collision_does_not_allow_another_unrelated_company(monkeypatch):
    import signalpost.web.social_universe as universe
    monkeypatch.setattr(universe,'index',lambda:{'names':{OTHER:'Hallmaker AS','914992605':'Hallmaker AS'},
        'keys':{'hallmaker':[OTHER,'914992605']},'rows':ROWS,'archive_sha256':ARCHIVE_SHA})
    row=relationship('parent')
    result=assess('https://instagram.com/hallmakergroup',context_for_envelope(row))
    assert result['state']=='withhold' and len(result['matches'])==2


def test_missing_or_corrupt_universe_cannot_authorize_profile(monkeypatch):
    import signalpost.web.social_universe as universe
    monkeypatch.setattr(universe,'index',lambda:None)
    assert veto('https://facebook.com/unrelatedbrand',{'organisation_number':ORG})=='universe_name_index_unavailable'


def test_name_similarity_and_cohort_absence_are_not_relationships():
    result=assess('https://instagram.com/hallmakergroup',{'organisation_number':ORG,'name':'Hallmaker Partner AS','other_company_names':[]})
    assert result['state']=='withhold'
