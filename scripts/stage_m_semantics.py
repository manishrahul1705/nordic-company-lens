import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];site=ROOT/'bench/cache/stage-m-after';out=ROOT/'bench/reports/stage-m'
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=str(Path(os.environ['LOCALAPPDATA'])/'ms-playwright/chromium-1248/chrome-win64/chrome.exe'))
 for path in ['index.html','c/922828172.html','c/926077422.html','compare.html?companies=922828172,917998787']:
  page=browser.new_page(viewport={'width':360,'height':812});base,_,query=path.partition('?');page.goto((site/base).as_uri()+('?' +query if query else ''));page.wait_for_timeout(80)
  result=page.evaluate("""() => ({h1:document.querySelectorAll('h1').length,main:document.querySelectorAll('main').length,unlabelledImages:[...document.querySelectorAll('img')].filter(e=>!e.hasAttribute('alt')).length,unlabelledButtons:[...document.querySelectorAll('button')].filter(e=>!e.textContent.trim()&&!e.getAttribute('aria-label')&&!e.getAttribute('title')).length})""");result['path']=path;results.append(result);page.close()
 browser.close()
assert all(r['h1']==1 and r['main']==1 and not r['unlabelledImages'] and not r['unlabelledButtons'] for r in results)
(out/'semantics.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS headings,main,images,button labels')
