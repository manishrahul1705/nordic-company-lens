import asyncio,json,time
from pathlib import Path
from urllib.parse import urlsplit,unquote
from playwright.async_api import async_playwright
BASE=Path(r'C:\Users\Manish\Downloads\agent-site-new');ROOT=BASE/'polish';ROOT.mkdir(exist_ok=True);SITE=BASE/'site'
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=r'C:\Users\Manish\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe',headless=True)
  context=await browser.new_context(viewport={'width':1366,'height':900},reduced_motion='reduce');page=await context.new_page();requests=[];errors=[];page.on('request',lambda r:requests.append(r.url));page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto((SITE/'index.html').as_uri());await page.locator('#results .company').first.wait_for();await page.evaluate('document.fonts.ready');assert await page.evaluate("Array.from(document.fonts).every(f=>f.status==='loaded')");assert await page.locator('body>nav #global-search-open').count()==1;assert await page.locator('body>nav>a').get_by_text('Search',exact=True).count()==0;await page.locator('#search').fill('Tensio');await page.wait_for_timeout(150);assert await page.locator('#results').get_by_text('TENSIO AS',exact=True).count()==1
  await page.screenshot(path=str(ROOT/'index-search-desktop.png'))
  await page.goto((SITE/'c/922828172.html').as_uri());await page.locator('#briefing').wait_for();assert await page.locator('.company-hero .meta-pill').count()==5
  assert await page.locator('.company-hero .metadata-pills .chip').count()==0
  assert '4 registered workplaces' in await page.locator('.company-hero').inner_text()
  assert 'Checked 7 Nov 2026' in await page.locator('.company-hero').inner_text()
  assert await page.locator('.company-header-actions').get_by_text('Compare',exact=True).count()==1
  await page.screenshot(path=str(ROOT/'company-desktop.png'))
  await page.locator('#briefing .citation').first.click();await page.locator('#evidence-drawer').wait_for(state='visible');await page.screenshot(path=str(ROOT/'drawer-desktop.png'));await page.keyboard.press('Escape')
  await page.locator('#theme-toggle').click();assert await page.locator('html').get_attribute('data-theme')=='dark';await page.reload();assert await page.locator('html').get_attribute('data-theme')=='dark';await page.screenshot(path=str(ROOT/'company-dark.png'))
  await page.goto((SITE/'compare.html').as_uri()+'?companies=922828172,919653477');await page.locator('.compare-card').first.wait_for();assert await page.locator('.compare-card').count()==2;await page.screenshot(path=str(ROOT/'compare-desktop.png'))
  await page.set_viewport_size({'width':375,'height':812})
  for filename,name in [('index.html','index-phone'),('c/922828172.html','company-phone'),('compare.html','compare-phone')]:
   url=(SITE/filename).as_uri()+('?companies=922828172,919653477' if filename=='compare.html' else '')
   await page.goto(url);await page.wait_for_timeout(150)
   widths=await page.evaluate('({scroll:document.documentElement.scrollWidth,view:innerWidth})');assert widths['scroll']<=widths['view'],(filename,widths)
   visible=await page.locator('body').inner_text();assert not __import__('re').search(r'T\d\d:\d\d',visible),(filename,visible[:300])
   await page.screenshot(path=str(ROOT/(name+'.png')))
  await page.goto((SITE/'c/922828172.html').as_uri());await page.locator('#briefing .citation').first.click();await page.screenshot(path=str(ROOT/'drawer-phone.png'))
  # Resolve all local links in the index and twenty company pages, including fragments.
  ids=['922828172']+[f.stem for f in sorted((SITE/'c').glob('*.html')) if f.stem!='922828172'][:19];broken=[];checked=0
  for file in [SITE/'index.html']+[SITE/'c'/f'{i}.html' for i in ids]:
   await page.goto(file.as_uri());links=await page.locator('a[href]').evaluate_all('(nodes)=>nodes.map(n=>n.href)')
   for url in links:
    if not url.startswith('file:'):continue
    parts=urlsplit(url);target=Path(unquote(parts.path).lstrip('/'));checked+=1
    if not target.exists():broken.append(url)
    elif parts.fragment:
     # Parse target HTML locally; deferred fact anchors are emitted in noscript too.
     markup=target.read_text(encoding='utf-8');fragment=unquote(parts.fragment)
     if 'id="'+fragment+'"' not in markup and "id='"+fragment+"'" not in markup:broken.append(url)
  assert not broken,broken[:20]
  await page.goto((SITE/'index.html').as_uri()+'?view=dashboard');await page.wait_for_timeout(100)
  assert not __import__('re').search(r'T\d\d:\d\d',await page.locator('body').inner_text())
  record=next(r for r in __import__('json').loads((SITE/'data/index.json').read_text(encoding='utf-8')) if r['name'][0].isdigit() and any(c.isalpha() for c in r['name']))
  await page.goto((SITE/'c'/(record['orgnr']+'.html')).as_uri());assert await page.locator('.company-hero .avatar').inner_text()==next(c for c in record['name'] if c.isalpha()).upper()
  fonts=await page.evaluate("Array.from(document.fonts).map(f=>({family:f.family,status:f.status}))");assert all(f['status']=='loaded' for f in fonts)

  assert all(url.startswith('file://') for url in requests),[u for u in requests if not u.startswith('file://')]
  assert not errors,errors
  nojs=await browser.new_context(java_script_enabled=False,viewport={'width':375,'height':812});reader=await nojs.new_page();await reader.goto((SITE/'index.html').as_uri());assert await reader.locator('#results .company').count()==1000;await reader.goto((SITE/'c/922828172.html').as_uri());await reader.locator('a[data-receipt]').first.click();assert '/e/' in reader.url;assert await reader.locator('.evidence-record').count()>0
  result={'requests':len(requests),'external_requests':0,'page_errors':errors,'broken_internal_links':broken,'internal_links_checked':checked,'companies_crawled':20,'no_js_reading':True,'fonts':fonts,'font_total_bytes':sum(f.stat().st_size for f in (SITE/'assets/fonts').glob('*.woff2')),'iso_timestamps_outside_drawer':0,'largest_html_bytes':max(f.stat().st_size for f in SITE.rglob('*.html'))};(ROOT/'browser-results.json').write_text(json.dumps(result,indent=2));print(result);await browser.close()
asyncio.run(main())
