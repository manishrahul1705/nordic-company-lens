"""Additional own-site proof depth never changes ownership or HTTP policy."""
from urllib.parse import urlsplit
import httpx,pytest
from signalpost.web import collector
from signalpost.web.candidates import Candidate
from signalpost.web.html import Page
from tests.test_websites import execute_web,html,OUR,OTHER


def trial(tmp_path,monkeypatch,proof_path=None,*,veto_path=None,existing=('/old1','/old2'),cap=30,home_proved=False):
    monkeypatch.setattr(collector,'generate',lambda context:[Candidate('https://example.no/','example.no','legal_name_slug')])
    monkeypatch.setattr(collector,'proof_page_targets',lambda page,url,limit=3:['https://example.no'+path for path in existing])
    links='<a href="/kontakt-extra">Kontakt</a><a href="/personvern-extra">Personvern</a><a href="/salgsbetingelser">Salgsbetingelser</a><a href="https://other.no/terms">Terms</a>'
    def response(request):
        path=request.url.path
        if path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nAllow: /')
        if request.url.host!='example.no':return httpx.Response(404)
        number=OTHER if path==veto_path else OUR if path==proof_path or path=='/' and home_proved else ''
        return httpx.Response(200,text=html(('Org.nr. '+number) if number else '',extra=links if path=='/' else '',title='Example'))
    report,row,requests,cfg=execute_web(tmp_path,monkeypatch,response=response,website_proof_discovery=False,website_unique_no=False,website_request_cap=cap,website_total_request_cap=40)
    checked=[urlsplit(u).path for u in requests if urlsplit(u).hostname=='example.no' and not urlsplit(u).path.endswith(('robots.txt','.xml')) and urlsplit(u).path not in ('/feed/','/feed.xml','/rss.xml','/blog/feed.xml')]
    return report,row,checked

@pytest.mark.parametrize('path,position',[('/salgsbetingelser',4),('/personvern-extra',5)])
def test_proof_on_fourth_or_fifth_page(tmp_path,monkeypatch,path,position):
    _,row,pages=trial(tmp_path,monkeypatch,path)
    claim=next(c for c in row['claims'] if c['field']=='official_website')
    assert claim['value']['proof_type']=='orgnr_on_page'
    assert claim['value']['proof_page_url']=='https://example.no'+path
    assert pages.index(path)+1==position
    assert len(pages)==position  # Stop immediately after finding proof.


def test_five_page_total_including_homepage(tmp_path,monkeypatch):
    _,row,pages=trial(tmp_path,monkeypatch,existing=('/old1','/old2','/old3'))
    assert pages[:5]==['/','/old1','/old2','/old3','/salgsbetingelser']
    entry=row['run']['refresh']['recall_round2']['candidates'][0]
    assert entry['proof_page_attempts_including_homepage']==5
    assert '/personvern-extra' not in pages


def test_extra_page_foreign_owner_still_vetoes(tmp_path,monkeypatch):
    _,row,pages=trial(tmp_path,monkeypatch,veto_path='/salgsbetingelser')
    assert '/salgsbetingelser' in pages and '/personvern-extra' not in pages
    assert not any(c['field']=='official_website' and c['availability']=='available' for c in row['claims'])
    assert 'foreign_orgnr' in str(row['errors'])


def test_existing_proof_prevents_deeper_links(tmp_path,monkeypatch):
    _,row,pages=trial(tmp_path,monkeypatch,home_proved=True)
    assert any(c['field']=='official_website' for c in row['claims'])
    assert '/salgsbetingelser' not in pages and '/personvern-extra' not in pages


def test_budget_stops_before_extra_page(tmp_path,monkeypatch):
    report,row,pages=trial(tmp_path,monkeypatch,'/salgsbetingelser',cap=4)
    assert '/salgsbetingelser' not in pages
    assert sum(e.get('section')=='website' for e in report['request_log'])<=4
    assert 'website_budget_exhausted' in str(row['errors'])
    assert report['max_requests_per_company']<=40


def test_priority_and_same_host_only():
    p=Page(('<a href="/om">Om</a><a href="/kontakt">Kontakt</a><a href="/privacy">Privacy</a><a href="/kjopsvilkar">Kjøpsvilkår</a><a href="https://other.no/terms">Terms</a>').encode(),'https://example.no/')
    assert collector.extra_proof_targets([p],p.url)==['https://example.no/kjopsvilkar','https://example.no/privacy']
