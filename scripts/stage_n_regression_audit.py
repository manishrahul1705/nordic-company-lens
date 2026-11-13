"""Offline file:// UX tasks and layout audit using ephemeral Playwright."""
import argparse,json,re,os
from pathlib import Path
from urllib.parse import urlsplit,unquote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
JS=r'''() => {
const visible=e=>!!(e.getClientRects().length)&&getComputedStyle(e).visibility!=='hidden'&&!e.closest('.visually-hidden,[hidden],details:not([open])>:not(summary)');
const targets=[...document.querySelectorAll('a,button,input,select,summary')].filter(visible).map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,id:e.id,cls:e.className,text:(e.innerText||e.getAttribute('aria-label')||'').slice(0,65),w:r.width,h:r.height}}).filter(x=>x.w<43.5||x.h<43.5);
const text=document.body.innerText;
const clipped=[...document.querySelectorAll('h1,h2,h3,p,dt,dd,label,button,summary')].filter(visible).filter(e=>e.clientWidth>0&&e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflowX!=='auto').slice(0,20).map(e=>({tag:e.tagName,text:e.innerText.slice(0,100),width:e.clientWidth,scroll:e.scrollWidth}));
const narrow=[...document.querySelectorAll('p,span,a,dt,dd')].filter(visible).filter(e=>e.innerText?.trim().length>8&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().width<18&&e.getBoundingClientRect().height>70).slice(0,10).map(e=>e.innerText.slice(0,80));
const overlaps=[];
for(const selector of ['nav','dialog[open]','.compare-card']) {
 const container=document.querySelector(selector);if(!container)continue;
 const nodes=[...container.querySelectorAll('button,a,h1,h2,h3,.eyebrow')].filter(visible);
 for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++) {
  const a=nodes[i],b=nodes[j];if(a.contains(b)||b.contains(a))continue;
  const bounds=e=>{if(e.matches('h1,h2,h3,.eyebrow')){const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect();}return e.getBoundingClientRect();};const ar=bounds(a),br=bounds(b);
  if(Math.min(ar.right,br.right)-Math.max(ar.left,br.left)>3&&Math.min(ar.bottom,br.bottom)-Math.max(ar.top,br.top)>3)overlaps.push([a.innerText.slice(0,60),b.innerText.slice(0,60)]);
 }
}
return {overlaps,overflow:document.documentElement.scrollWidth>innerWidth,scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,smallTargets:targets,clipped,narrow,rawJSON:/\{\s*\}|\{\s*"[\w_]+"\s*:/.test(text),isoDates:(text.match(/\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}[^\s]*)?/g)||[]).slice(0,10)};
}'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--site',type=Path,default=ROOT/'bench/runs/proof-depth-live/site');ap.add_argument('--phase',required=True);a=ap.parse_args();site=a.site.resolve();out=ROOT/'bench/reports/stage-n/regression'/a.phase;out.mkdir(parents=True,exist_ok=True)
 records=json.loads((site/'data/index.json').read_text(encoding='utf8'));chosen=['922828172','917998787','926077422'];byid={r['orgnr']:r for r in records};results=[];broken=[];external=[];errors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=str(Path(os.environ['LOCALAPPDATA'])/'ms-playwright/chromium-1248/chrome-win64/chrome.exe'))
  for width,height in [(360,812),(1280,900)]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':height},color_scheme=theme)
    page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:external.append(r.url) if r.url.startswith(('https:','http:')) else None)
    def visit(rel):page.goto((site/rel.split('?')[0]).as_uri()+('?' + rel.split('?',1)[1] if '?' in rel else ''));page.wait_for_timeout(180)
    def capture(kind,tasks=None):
     row={'width':width,'height':height,'theme':theme,'page':kind,'tasks':tasks or {},**page.evaluate(JS)};results.append(row);page.screenshot(path=str(out/f'{width}-{theme}-{kind}.png'),full_page=False);return row
    visit('index.html');page.evaluate('(t)=>{localStorage.setItem("signalpost_theme",t);document.documentElement.dataset.theme=t}',theme);page.reload();page.wait_for_timeout(150)
    persistence=page.locator('html').get_attribute('data-theme')==theme
    searches={}
    capture('landing-before-search',{'autofocus':page.locator('#search').evaluate('(e)=>document.activeElement===e')})
    for term in [byid[chosen[0]]['name'],chosen[0]]:
     page.locator('#search').fill(term);page.wait_for_timeout(250);searches[term]=page.locator(f'a[href*="{chosen[0]}"]:visible').count()>0
    capture('index',{'searchName':list(searches.values())[0],'searchOrgnr':list(searches.values())[1],'themeReload':persistence})
    for i,org in enumerate(chosen):
     visit('c/'+org+'.html');summary=page.locator('.summary').first;tasks={'briefingPresent':summary.count()>0,'company':byid[org]['name'],'type':['large','medium','sparse'][i]};capture(org,tasks)
     button=page.locator('button[data-toggle^="source-"]:visible, a.citation[href^="#fact-"]:visible, [data-receipt]:visible').first
     if button.count():
      button.click();page.wait_for_timeout(350);dialog=page.locator('#evidence-drawer');text=dialog.inner_text();evidence={'dialogNonempty':len(text)>80,'sourceURL':dialog.locator('a[href^="http"]').count()>0,'date':bool(re.search(r'\d{4}|Retrieved',text)),'quote':dialog.locator('blockquote').count()>0,'text':text[:900]};capture(org+'-evidence',evidence);original=dialog.locator('.evidence-original').first;
      if original.count():
       technical=dialog.locator('.technical-details').first
       if technical.count():technical.locator('summary').first.click()
       original.locator('summary').click();assert len(original.locator('blockquote').inner_text())>0;original.locator('summary').click()
       if technical.count():technical.locator('summary').first.click()
      dialog.locator('blockquote').first.scroll_into_view_if_needed();page.screenshot(path=str(out/f'{width}-{theme}-{org}-quote.png'),full_page=False);page.keyboard.press('Escape')
    visit('compare.html?companies='+','.join(chosen[:2]));capture('compare',{'twoCompanies':page.locator('.compare-card').count()==2});page.reload();page.wait_for_timeout(150);results[-1]['tasks']['comparisonReload']=page.locator('.compare-card').count()==2
    context.close()
  # Crawl index + 30 profiles, checking every internal file/fragment target.
  context=browser.new_context();page=context.new_page();sample=list(dict.fromkeys(chosen+[r['orgnr'] for r in records]))[:30];cache={}
  for rel in ['index.html']+['c/'+org+'.html' for org in sample]:
   page.goto((site/rel).as_uri());page.wait_for_timeout(40)
   for href in page.locator('a[href]').evaluate_all('(nodes)=>nodes.map(e=>e.href)'):
    parsed=urlsplit(href)
    if parsed.scheme!='file':continue
    raw=unquote(parsed.path);raw=raw[1:] if re.match(r'^/[A-Za-z]:',raw) else raw;target=Path(raw)
    if not target.is_file():broken.append({'from':rel,'href':href,'reason':'missing file'});continue
    if parsed.fragment:
     if target not in cache:cache[target]=target.read_text(encoding='utf8')
     if not any(re.search(r'\bid\s*=\s*'+re.escape(marker+unquote(parsed.fragment)+marker),cache[target]) for marker in (chr(34),chr(39))):broken.append({"from":rel,"href":href,"reason":"missing fragment"})
  context.close();browser.close()
 sizes={str(p.relative_to(site)):p.stat().st_size for p in site.rglob('*.html')};largest=max(sizes.values());data={'phase':a.phase,'site':str(site),'companies':{x:byid[x]['name'] for x in chosen},'results':results,'brokenLinks':broken,'externalRequests':external,'pageErrors':errors,'htmlFiles':len(sizes),'largestHTMLBytes':largest,'oversizeHTML':[{'file':k,'bytes':v} for k,v in sizes.items() if v>=250000],'crawlCompanyPages':30}
 (out/'audit.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'phase':a.phase,'overflow':sum(r['overflow'] for r in results),'smallTargetPages':sum(bool(r['smallTargets']) for r in results),'overlapPages':sum(bool(r['overlaps']) for r in results),'clippedPages':sum(bool(r['clipped']) for r in results),'narrowPages':sum(bool(r['narrow']) for r in results),'rawJSONPages':sum(r['rawJSON'] for r in results),'isoDatePages':sum(bool(r['isoDates']) for r in results),'brokenLinks':len(broken),'externalRequests':len(external),'pageErrors':errors,'largestHTMLBytes':largest},indent=2))
if __name__=='__main__':main()
