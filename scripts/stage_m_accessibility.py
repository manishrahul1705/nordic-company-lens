"""Additional offline keyboard, proof, first-screen and text contrast checks."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'bench/cache/stage-m-after';OUT=ROOT/'bench/reports/stage-m'
CONTRAST=r"""() => {
const rgb=s=>{const a=s.match(/[\d.]+/g);return a?a.map(Number):null};
const luminance=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
const failures=[];let checked=0;
for(const el of document.querySelectorAll('h1,h2,h3,p,label,button,a,span,dt,dd,summary')){
 if(!el.getClientRects().length||!el.textContent.trim()||el.closest('[hidden],details:not([open])>:not(summary)'))continue;
 const style=getComputedStyle(el);if(style.visibility==='hidden'||Number(style.opacity)<1)continue;
 let bg;for(let n=el;n;n=n.parentElement){const c=rgb(getComputedStyle(n).backgroundColor);if(c&&c[3]!==0){bg=c;break;}}
 const fg=rgb(style.color);if(!bg||!fg)continue;const a=luminance(fg),b=luminance(bg);const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);checked++;
 if(ratio<4.5)failures.push({text:el.textContent.trim().slice(0,70),ratio:Math.round(ratio*100)/100,color:style.color,background:bg});
}
return {checked,failures};
}"""
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=str(Path(os.environ['LOCALAPPDATA'])/'ms-playwright/chromium-1248/chrome-win64/chrome.exe'))
 results=[]
 for width,height in [(360,812),(1280,900)]:
  for theme in ['light','dark']:
   page=browser.new_page(viewport={'width':width,'height':height},color_scheme=theme);page.goto((SITE/'index.html').as_uri());page.wait_for_timeout(150)
   page.evaluate('(t)=>{localStorage.setItem("signalpost_theme",t);document.documentElement.dataset.theme=t}',theme);page.reload();page.wait_for_timeout(150)
   autofocus=page.locator('#search').evaluate('(e)=>document.activeElement===e')
   counts_visible=page.locator('.hero-stats').evaluate('(e)=>e.getBoundingClientRect().bottom<=innerHeight')
   page.locator('#search').blur();page.keyboard.press('/');page.wait_for_timeout(80);shortcut=page.locator('#global-search-input').evaluate('(e)=>document.activeElement===e');page.keyboard.press('Escape')
   landing=page.evaluate(CONTRAST)
   page.goto((SITE/'c/922828172.html').as_uri());page.wait_for_timeout(120);page.locator('[data-receipt],button[data-toggle^="source-"]').first.click();page.wait_for_timeout(80);proof=page.locator('#evidence-drawer').inner_text();page.keyboard.press('Escape')
   profile=page.evaluate(CONTRAST)
   results.append({'width':width,'theme':theme,'autofocus':autofocus,'headline_counts_above_fold':counts_visible,'slash_shortcut':shortcut,'contrast_landing':landing,'contrast_profile':profile})
   page.close()
 browser.close()
(OUT/'accessibility.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
