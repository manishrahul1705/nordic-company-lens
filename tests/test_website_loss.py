import json
from scripts.website_loss import diagnose


def row(attempts, state='not_available', extra=()):
    return {'organisation_number':'923609016','claims':[], 'run':{'sections':{'website':state}},
            'errors':[{'section':'website','code':'website_candidates','message':json.dumps(attempts)},*extra]}


def test_loss_stages_do_not_confuse_dns_absence_and_proof_failure():
    assert diagnose(row([{'domain':'missing.no','level':'LOW','reason':'no_such_domain'}]))['reason']=='all candidates DNS-missing'
    assert diagnose(row([{'domain':'live.no','level':'LOW','points':0}]), [{'url':'https://live.no/','sha256':'retained'}])['reason']=='fetched but no proof'
    assert diagnose(row([]))['reason']=='no candidates generated'


def test_loss_retains_full_conflict_and_candidate_evidence():
    attempts=[{'domain':'other.no','level':'REJECT','reason':'foreign_orgnr'}]
    result=diagnose(row(attempts))
    assert result['reason']=='proof conflict (other orgnr)'
    assert result['diagnostics']==attempts and result['candidates']==['other.no']


def test_available_sites_not_counted_as_lost():
    assert diagnose(row([],state='available')) is None


def test_furthest_proof_stage_retained_when_later_candidate_connect_fails():
    result=diagnose(row([{'domain':'live.no','level':'LOW','points':0}, {'domain':'other.no','reason':'website_connect_error'}]), [{'url':'https://live.no/','sha256':'retained'}])
    assert result['furthest_stage']=='ownership proof'
    assert result['reason']=='TLS-connect failure'


def test_scoring_or_status_without_retained_page_is_not_a_fetch():
    for attempt in ({'domain':'live.no','level':'LOW','points':0},
                    {'domain':'live.no','url':'https://live.no/','status':200},
                    {'domain':'live.no','reason':'http_404'}):
        result=diagnose(row([attempt]))
        assert result['reason']=='no retained successful company page'
        assert result['furthest_stage']!='ownership proof'


def test_analysis_requires_successful_nonrobots_retained_body(tmp_path):
    from scripts.website_loss import analyze
    (tmp_path/'envelopes.jsonl').write_text(json.dumps(row([{'domain':'live.no','points':0}]))+'\n')
    blobs=tmp_path/'state/blobs';blobs.mkdir(parents=True);(blobs/'body').write_text('<h1>Unproven</h1>')
    event={'organisation_number':'923609016','section':'website','url':'https://live.no/','status':200,'content_sha256':'body'}
    for changes in ({'url':'https://live.no/robots.txt'}, {'content_sha256':'missing'},
                    {'status':404}, {'error':'TimeoutError'}, {'truncated':True}):
        (tmp_path/'report.json').write_text(json.dumps({'request_log':[{**event,**changes}]}))
        assert 'fetched but no proof' not in analyze(tmp_path)['counts']
    (tmp_path/'report.json').write_text(json.dumps({'request_log':[event]}))
    assert analyze(tmp_path)['counts']=={'fetched but no proof':1}
