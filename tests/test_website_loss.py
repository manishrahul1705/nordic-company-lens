import json
from scripts.website_loss import diagnose


def row(attempts, state='not_available', extra=()):
    return {'organisation_number':'923609016','claims':[], 'run':{'sections':{'website':state}},
            'errors':[{'section':'website','code':'website_candidates','message':json.dumps(attempts)},*extra]}


def test_loss_stages_do_not_confuse_dns_absence_and_proof_failure():
    assert diagnose(row([{'domain':'missing.no','level':'LOW','reason':'no_such_domain'}]))['reason']=='all candidates DNS-missing'
    assert diagnose(row([{'domain':'live.no','level':'LOW','points':0}]))['reason']=='fetched but no proof'
    assert diagnose(row([]))['reason']=='no candidates generated'


def test_loss_retains_full_conflict_and_candidate_evidence():
    attempts=[{'domain':'other.no','level':'REJECT','reason':'foreign_orgnr'}]
    result=diagnose(row(attempts))
    assert result['reason']=='proof conflict (other orgnr)'
    assert result['diagnostics']==attempts and result['candidates']==['other.no']


def test_available_sites_not_counted_as_lost():
    assert diagnose(row([],state='available')) is None
