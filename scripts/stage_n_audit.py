import json,os,argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--phase',required=True);p.add_argument('--site');a=p.parse_args()
site=Path(a.site) if a.site else root/('bench/cache/stage-m-after' if a.phase=='before' else 'bench/cache/stage-n-after')
out=root/'bench/reports/stage-n'/a.phase;out.mkdir(parents=True,exist_ok=True)
rows=[json.loads(l) for l in (root/'bench/runs/stage-g-run1/envelopes.jsonl').open(encoding='utf8')]
r=next(r for r in rows if r['organisation_number']=='922828172');c=next(c for c in r['claims'] if c['field']=='official_website')
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=str(Path(os.environ['LOCALAPPDATA'])/'ms-playwright/chromium-1248/chrome-win64/chrome.exe'))
 for width in [360,1280]:
  for theme in ['light','dark']:
   page=b.new_page(viewport={'width':width,'height':812 if width==360 else 900});page.goto((site/'c/922828172.html').as_uri());page.evaluate('(t)=>localStorage.setItem("signalpost_theme",t)',theme);page.reload()
   page.locator('#fact-'+c['id'][:16]+' button[data-toggle^="source-"],#fact-'+c['id'][:16]+' [data-receipt]').first.click();page.wait_for_timeout(350)
   page.screenshot(path=str(out/f'{width}-{theme}-drawer.png'),animations='disabled')
   result=page.locator('#evidence-drawer').evaluate('''d=>{const r=d.getBoundingClientRect(),b=d.querySelector('.drawer-close').getBoundingClientRect();return {overflow:d.scrollWidth>d.clientWidth+1,drawerInViewport:r.left>=-1&&r.right<=innerWidth+1,closeVisible:b.left>=0&&b.right<=innerWidth,quoteTop:d.querySelector('blockquote')?.getBoundingClientRect().top,sourceBottom:d.querySelector('a[href^="http"]')?.getBoundingClientRect().bottom,text:d.innerText.slice(0,3500),technical:d.querySelector('details.technical-details')?.open??null}}''')
   result.update(width=width,theme=theme)
   if a.phase=='after':
    assert not result['overflow'] and result['drawerInViewport'] and result['closeVisible']
    assert result['sourceBottom'] < (812 if width==360 else 900)
    assert result['technical'] is False
    assert page.locator('#evidence-drawer .evidence-provenance button').first.get_attribute('data-copy')==page.locator('#evidence-drawer .evidence-provenance a').first.get_attribute('href')
    assert page.locator('.proof-explanation').first.inner_text().startswith('Accepted because')
    exact=page.locator('#evidence-drawer blockquote').first.text_content()
    assert any(e.get('claim_span')==exact for e in r['evidence'])
    assert 'points:' not in page.locator('#evidence-drawer').inner_text()
    page.locator('#evidence-drawer .technical-details').first.locator('summary').click()
    assert c['value']['proof_type'] in page.locator('#evidence-drawer .technical-details').first.inner_text()
    page.keyboard.press('Escape')
    groups=page.locator('.citation-group');result['citationGroups']=groups.count()
    if groups.count():
     group=groups.first;count=group.locator('.citation').count();group.locator('.citation-group-button').click()
     assert page.locator('.citation-choices button').count()==count
     for i in range(count):
      page.locator('.citation-choices button').nth(i).click();assert len(page.locator('dialog[open]').inner_text())>80
     result['allGroupedSourcesReachable']=count;page.keyboard.press('Escape')
    positions=page.locator('body>nav>a:not(.brand)').evaluate_all('(nodes)=>nodes.map(e=>e.getBoundingClientRect().top)')
    assert len(set(positions))==1
    result['headerAligned']=True
   results.append(result);page.close()
 b.close()
(out/'audit.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8');print(json.dumps([{k:v for k,v in r.items() if k!='text'} for r in results]))
