"""CI tolerates optional-source outages, never registry/evidence failures."""
import json
import pytest
from scripts.verify_output import verify,section_summary
from tests.test_registry import config,execute
from signalpost.models.envelope import Envelope,Error
from signalpost.models.shapes import serialize
from signalpost.synthesis.template import generate

REGISTRY=['identity','roles','accounts','subunits']


def sample(tmp_path,family,state,stale=False,shape='union'):
    cfg=config(tmp_path,['923609016']);_,rows=execute(cfg)
    row=Envelope.model_validate(rows[0]);row.run.sections[family]=state
    row.errors.append(Error(section=family,code='dns_timeout',message='Public source timed out'))
    if stale:row.run.refresh['stale_sections']={family:{'previous_state':state,'attempt_state':'failed','failed_attempt_at':row.completed_at,'failure_codes':['dns_timeout']}}
    row.run.synthesis=generate(row);row.profile.synthesis=row.run.synthesis
    cfg.output.write_text(json.dumps(serialize(row,shape))+'\n',encoding='utf8')
    return cfg


@pytest.mark.parametrize('shape',['union','contract','reference'])
@pytest.mark.parametrize('family',['website','hiring','activity'])
def test_ci_optional_failure_is_reported_but_default_clean_is_strict(tmp_path,shape,family):
    cfg=sample(tmp_path,family,'failed',shape=shape)
    with pytest.raises(AssertionError,match='Incomplete smoke-test section'):
        verify(cfg.output,cfg.state_dir,1,report=cfg.report,require_clean=True)
    result=verify(cfg.output,cfg.state_dir,1,report=cfg.report,require_clean=True,clean_sections=REGISTRY)
    issue=next(i for i in result['failed_or_stale_sections'] if i['section']==family)
    assert issue['state']=='failed' and issue['reasons']==[{'code':'dns_timeout','message':'Public source timed out'}]


@pytest.mark.parametrize('family',REGISTRY)
@pytest.mark.parametrize('stale',[False,True])
def test_registry_failure_or_stale_never_passes_scoped_clean(tmp_path,family,stale):
    cfg=sample(tmp_path,family,'available' if stale else 'failed',stale)
    with pytest.raises(AssertionError,match='Stale required|Incomplete smoke'):
        verify(cfg.output,cfg.state_dir,1,report=cfg.report,require_clean=True,clean_sections=REGISTRY)


def test_optional_stale_preserved_state_is_logged_and_evidence_stays_strict(tmp_path):
    cfg=sample(tmp_path,'website','not_available',True)
    result=verify(cfg.output,cfg.state_dir,1,report=cfg.report,require_clean=True,clean_sections=REGISTRY)
    issue=next(i for i in result['failed_or_stale_sections'] if i['section']=='website')
    assert issue['state']=='not_available' and issue['stale']['failure_codes']==['dns_timeout']
    row=json.loads(cfg.output.read_text(encoding='utf8'))
    sha=next(e['content_sha256'] for e in row['evidence'])
    (cfg.state_dir/'blobs'/sha).write_bytes(b'corrupt')
    with pytest.raises(AssertionError):verify(cfg.output,cfg.state_dir,1,report=cfg.report,require_clean=True,clean_sections=REGISTRY)


def test_required_section_cannot_be_omitted(tmp_path):
    cfg=sample(tmp_path,'website','failed')
    with pytest.raises(AssertionError,match='Required clean sections missing'):
        verify(cfg.output,cfg.state_dir,1,report=cfg.report,require_clean=True,clean_sections=[*REGISTRY,'activity'])


def test_candidate_summary_prints_specific_failure_codes_without_huge_diagnostics():
    row={'organisation_number':'923609016','claims':[],'errors':[{'section':'website','code':'website_candidates','message':json.dumps([{'reason':'dns_unavailable'},{'reason':'website_timeout'},{'reason':'dns_unavailable'}])}],
         'run':{'sections':{'website':'failed'},'refresh':{}}}
    assert section_summary([row])[0]['reasons']==[{'code':'website_candidates','candidate_failure_reasons':['dns_unavailable','website_timeout']}]
