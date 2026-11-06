"""A single latest-year official PDF nominates domains only after site failure."""
import asyncio
import json
import sys
import time
from .candidates import Candidate

URL='https://data.brreg.no/regnskapsregisteret/regnskap/aarsregnskap/kopi/'


async def nominate(org,envelope,http,seen):
    meta=envelope.run.refresh.setdefault('recall_round3',{}).setdefault('annual',{'attempted':False,'domains':[]})
    if meta['attempted']:return []
    years=[str(c.reporting_period.get('fiscal_year','')) for c in envelope.claims if c.family=='accounts' and c.reporting_period]
    years=[y for y in years if y.isdigit() and len(y)==4]
    official=getattr(http,'registry_http',None)
    if not official or not years:meta['state']='no_account_year';return []
    if getattr(http.budget,'by_company',{}).get(org,0)>=36:meta['state']='budget_reserved_for_proof';return []
    meta.update(attempted=True,year=max(years));url=URL+org+'/'+meta['year'];meta['url']=url
    try:
        response=await official.download_once(url,org)
        meta.update(status=response.status,sha256=response.sha)
        if response.status!=200:meta['state']='http_'+str(response.status);return []
        if not response.body.startswith(b'%PDF'):meta['state']='not_pdf';return []
        gate=getattr(http,'pdf_gate',None)
        if gate is None:http.pdf_gate=gate=asyncio.Semaphore(3)
        async with gate:
            http.budget.check();remaining=min(10,max(.001,http.budget.deadline-time.monotonic()))
            child=await asyncio.create_subprocess_exec(sys.executable,'-m','signalpost.web.pdftext',stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL)
            try:
                stdout,_=await asyncio.wait_for(child.communicate(response.body),remaining)
                result=json.loads(stdout) if child.returncode==0 else {'state':'parse_failed','domains':[]}
            except (TimeoutError,asyncio.CancelledError):
                child.kill();await child.communicate();raise
        meta.update(result)
        return [Candidate('https://'+d,d,'annual_report') for d in result['domains'] if d not in seen]
    except asyncio.CancelledError:raise
    except Exception as exc:
        meta['state']=getattr(exc,'code','parse_timeout' if isinstance(exc,TimeoutError) else 'unavailable')
        return []
