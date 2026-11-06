import asyncio
import io
import json
import time
from types import SimpleNamespace
import httpx
import pytest
from pypdf import PdfWriter
from pypdf.generic import NameObject,DictionaryObject,DecodedStreamObject
from signalpost.web.html import Page
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate
from signalpost.web.names import same_name,proof_context
from signalpost.web.pdftext import extract,domains
from signalpost.web.annual import nominate
from tests.test_recall_step10 import ORG,OTHER,CONTEXT


def page(body,title='Example AS'):
    return Page(f'<html><title>{title}</title><body>{body}</body></html>'.encode(),'https://example.no/')


@pytest.mark.parametrize('name,site,title',[
    ('KN ELEKTRO AS','<footer>All rettigheter reservert - KN Elektro AS</footer>','KN Elektro'),
    ('LOFOTPOSTEN AS','<footer>Utgitt av Lofotposten AS</footer>','Lofotposten'),
    ('CONTROL SOLUTIONS AS',f'<footer>Org.nr {ORG}</footer>','CONTROL SOLUTION AS'),
    ('GS ELEKTRO GJ\ufffdVIK AS',f'<footer>GS ELEKTRO GJØVIK AS Org.nr {ORG} © 2026 GS Elektro Gjøvik AS</footer>','GS Elektro Gjøvik AS'),
])
def test_generic_known_loss_repairs(name,site,title):
    p=page(site,title)
    result=candidate_proof(p,ORG,{**CONTEXT,'name':name},Candidate(p.url,'example.no','registry_website'),[])
    assert result.level=='VERIFIED'


def test_unicode_and_spacing_comparison_never_changes_legal_form_or_guesses_damage():
    assert same_name('ØKONOMI AS','Okonomi AS')
    assert same_name('CONTROL SOLUTIONS AS','ControlSolutions AS')
    assert not same_name('GJ\ufffdVIK AS','GJØVIK AS')
    assert same_name('GJ\ufffdVIK AS','GJØVIK AS',True)
    assert not same_name('Permobil AS','Permobil AB',True,True)
    assert not same_name('Control Solutions AS','Control Solution AS',False,True)
    p=page(f'<main>Our customer {ORG}</main>','Control Solution AS')
    context={**CONTEXT,'name':'Control Solutions AS'}
    assert proof_context(p,ORG,context)==context


def test_own_number_does_not_override_another_copyright_publisher():
    p=page(f'<footer>Org nr {ORG} Copyright Other AB</footer>','Example AS')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_website'),[]).level=='REJECT'


def test_own_as_suffix_in_title_is_not_a_prefix_as_company():
    p=page(f'<footer>Example AS Org.nr {ORG}</footer>','Contact — Example AS Mini Bus Transportation in Norway')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_website'),[]).level=='VERIFIED'


def test_title_prefix_allows_own_number_backed_singular_plural_variant():
    p=page(f'<footer>Org.nr {ORG}</footer>','Ta uforpliktende kontakt! — CONTROL SOLUTION AS')
    assert candidate_proof(p,ORG,{**CONTEXT,'name':'Control Solutions AS'},Candidate(p.url,'example.no','legal_name_slug'),[]).level=='VERIFIED'


def test_first_pdf_429_stops_remaining_downloads_for_the_run():
    class Official:
        calls=0
        async def download_once(self,*args):
            self.calls+=1;return SimpleNamespace(status=429,sha='a'*64)
    official=Official();http=SimpleNamespace(registry_http=official,budget=SimpleNamespace(by_company={}))
    def row():return SimpleNamespace(claims=[SimpleNamespace(family='accounts',reporting_period={'fiscal_year':'2025'})],run=SimpleNamespace(refresh={}))
    first,second=row(),row()
    async def check():
        assert not await nominate(ORG,first,http,set())
        assert not await nominate(OTHER,second,http,set())
    asyncio.run(check());assert official.calls==1
    assert second.run.refresh['recall_round3']['annual']['state']=='run_rate_limited'


def test_split_own_legal_name_in_footer_needs_exact_owner_number():
    p=page(f'<h1>GS ELEKTRO</h1><h1>GJØVIK AS</h1><footer><span>GS ELEKTRO</span><span>GJØVIK AS</span>Org.nr {ORG} © 2026 GS Elektro Gjøvik AS</footer>','')
    result=candidate_proof(p,ORG,{**CONTEXT,'name':'GS ELEKTRO GJ\ufffdVIK AS'},Candidate(p.url,'example.no','registry_email'),[])
    assert result.level=='VERIFIED' and result.proof_type=='orgnr_on_page'
    p=page(f'<h1>Example AS</h1><footer><span>Other</span><span>AB</span>Org.nr {OTHER}</footer>')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_email'),[]).level=='REJECT'


def pdf(text=None):
    writer=PdfWriter();p=writer.add_blank_page(width=612,height=792)
    if text:
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        p[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
        stream=DecodedStreamObject();stream.set_data(('BT /F1 12 Tf 50 700 Td ('+text+') Tj ET').encode())
        p[NameObject('/Contents')]=writer._add_object(stream)
    out=io.BytesIO();writer.write(out);return out.getvalue()


def test_pdf_text_nominates_urls_bare_domains_and_nonprovider_email_only():
    result=extract(pdf('Our company website https://example.no and office@example.com; auditor@gmail.com. Annual report.'))
    assert result['state']=='text' and result['domains']==['example.no','example.com']
    assert domains('www.example.no https://data.brreg.no example.no office@example.no')==['example.no']
    assert extract(pdf())['state']=='scanned_or_empty'
    assert extract(b'%PDF broken')['state']=='unreadable_pdf'
    assert extract(b'not pdf')['domains']==[]


def test_pdf_nomination_is_never_identity_proof():
    p=page('Example AS')
    assert candidate_proof(p,ORG,{**CONTEXT,'phone':None,'email':None,'street':None,'postcode':None},Candidate(p.url,'example.no','annual_report'),[]).level!='VERIFIED'


def test_annual_download_uses_latest_known_year_once_and_nominates_after_parse(monkeypatch):
    calls=[]
    class Official:
        async def download_once(self,url,org):
            calls.append(url);return SimpleNamespace(status=200,body=b'%PDF synthetic',sha='a'*64)
    class Child:
        returncode=0
        async def communicate(self,*args):return json.dumps({'state':'text','domains':['example.no']}).encode(),None
    async def spawn(*args,**kwargs):return Child()
    monkeypatch.setattr(asyncio,'create_subprocess_exec',spawn)
    row=SimpleNamespace(claims=[SimpleNamespace(family='accounts',reporting_period={'fiscal_year':y}) for y in ['2024','2025']],run=SimpleNamespace(refresh={}))
    http=SimpleNamespace(registry_http=Official(),budget=SimpleNamespace(by_company={},deadline=time.monotonic()+30,check=lambda:None))
    async def exercise():
        result=await nominate(ORG,row,http,set())
        assert result==[Candidate('https://example.no','example.no','annual_report')]
        assert not await nominate(ORG,row,http,set())
    asyncio.run(exercise());assert calls==[f'https://data.brreg.no/regnskapsregisteret/regnskap/aarsregnskap/kopi/{ORG}/2025']


def test_single_pdf_request_is_bounded_and_never_retried(tmp_path):
    from signalpost.sources.http import Http
    from signalpost.sources.blobstore import BlobStore
    from signalpost.budget import SourceFailure
    events=[];calls=[]
    def reserve(*args):
        events.append({});return events[-1]
    def handler(request):
        assert request.headers['Accept']=='application/pdf,application/octet-stream'
        calls.append(str(request.url));return httpx.Response(503,content=b'x'*101)
    async def exercise():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            http=Http(client,SimpleNamespace(host_concurrency=1,request_timeout=2),SimpleNamespace(check=lambda:None,reserve=reserve,deadline=time.monotonic()+5),BlobStore(tmp_path))
            with pytest.raises(SourceFailure,match='body_cap'):await http.download_once('https://data.brreg.no/sample',ORG,max_bytes=100)
    asyncio.run(exercise());assert len(calls)==1 and events[0]['status']==503


def test_exact_no_candidate_tries_all_four_authorities_after_http_404():
    from signalpost.web.fetcher import WebsiteHttp
    from signalpost.budget import SourceFailure
    visited=[]
    async def precheck(*args):pass
    async def get(url,*args,**kwargs):
        visited.append(url);return SimpleNamespace(status=200 if len(visited)==4 else 404,url=url)
    http=SimpleNamespace(attempts={},company_names={ORG:'Example AS'},precheck=precheck,get=get)
    result=asyncio.run(WebsiteHttp.candidate(http,Candidate('https://example.no/','example.no','legal_name_slug'),ORG))
    assert result.status==200
    assert visited==['https://example.no/','https://www.example.no/','http://www.example.no/','http://example.no/']
    visited.clear();http.company_names={ORG:'Other AS'}
    with pytest.raises(SourceFailure,match='http_404'):
        asyncio.run(WebsiteHttp.candidate(http,Candidate('https://example.no/','example.no','legal_name_slug'),ORG))
    assert visited==['https://example.no/']


def test_pdf_parser_timeout_kills_child_and_abstains(monkeypatch):
    class Official:
        async def download_once(self,*args):return SimpleNamespace(status=200,body=b'%PDF slow',sha='b'*64)
    class Child:
        killed=False;calls=0
        async def communicate(self,*args):
            self.calls+=1
            if self.calls==1:raise TimeoutError
            return b'',None
        def kill(self):self.killed=True
    child=Child()
    async def spawn(*args,**kwargs):return child
    monkeypatch.setattr(asyncio,'create_subprocess_exec',spawn)
    row=SimpleNamespace(claims=[SimpleNamespace(family='accounts',reporting_period={'fiscal_year':'2025'})],run=SimpleNamespace(refresh={}))
    http=SimpleNamespace(registry_http=Official(),budget=SimpleNamespace(by_company={},deadline=time.monotonic()+30,check=lambda:None))
    assert asyncio.run(nominate(ORG,row,http,set()))==[]
    assert child.killed and row.run.refresh['recall_round3']['annual']['state']=='parse_timeout'
