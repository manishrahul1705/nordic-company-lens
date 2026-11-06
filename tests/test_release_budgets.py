from signalpost.budget import Budget
from signalpost.sources.nav import time_cap
from tests.test_registry import config,execute


def test_derived_budget_uses_unique_inputs_and_override(tmp_path):
    cfg=config(tmp_path/'auto',['923609016','923609016','bad'])
    assert Budget(cfg).cap==36 and cfg.time_budget_seconds==2400
    assert time_cap(cfg)==900
    report,rows=execute(cfg)
    assert len(rows)==3 and report['limits']['max_requests']==36
    assert report['request_budget_basis']=='Pooled 18 per unique normalized input globally, up to 40 per company; explicit lower limits honored'
    assert report['measured_request_projection']['projected_http']==12
    assert Budget(config(tmp_path/'override',['923609016'],max_requests=7)).cap==7
