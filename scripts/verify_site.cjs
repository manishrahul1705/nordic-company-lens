const {chromium}=require('playwright');
const fs=require('fs');const path=require('path');const {pathToFileURL}=require('url');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? {executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE} : {})});
 const root=path.resolve(process.argv[2] || 'out/site');const shots=path.resolve(process.argv[3] || 'bench/reports/s6-step9/screenshots');fs.mkdirSync(shots,{recursive:true});
 const records=JSON.parse(fs.readFileSync(path.join(root,'data/index.json'),'utf8'));const ids=records.slice(0,3).map(r=>r.orgnr);
 const results=[];
 for(const width of [1280,360]){
  const context=await browser.newContext({viewport:{width,height:900},colorScheme:'light'});
  const page=await context.newPage();const errors=[],external=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
  for(const [kind,file] of [['index','index.html'],['company','c/'+ids[0]+'.html'],['compare','compare.html?companies='+ids.join(',')]]){
   await page.goto(pathToFileURL(path.join(root,file.split('?')[0])).href+(file.includes('?')?'?'+file.split('?')[1]:''));await page.waitForTimeout(350);
   if(kind==='index'){
    await page.locator('nav a[href="index.html#directory"]').click();
    await page.locator('#search').fill(records[0].name);await page.waitForTimeout(250);
    if(!(await page.locator('a[href*="'+ids[0]+'"]').count()))throw Error('Name search failed');
    await page.locator('#search').fill(ids[0]);await page.waitForTimeout(250);
   }
   if(kind==='company'){
    await page.screenshot({path:path.join(shots,`summary-${width}.png`),fullPage:false});
    await page.locator('button[data-toggle^="source-"]').first().click();
    if(!(await page.locator('.evidence:not([hidden])').first().innerText()).includes('Retrieved at'))throw Error('Source panel missing retrieval');
   }
   if(kind==='compare'){
    if(await page.locator('.compare-card').count()!==3)throw Error('Shareable compare failed');
    await page.reload();if(await page.locator('.compare-card').count()!==3)throw Error('Compare reload failed');
    await page.locator('#company-2').fill(''); if(await page.locator('.compare-card').count()!==2)throw Error('Two-company comparison failed');
    await page.locator('#company-2').fill(ids[2]); if(await page.locator('.compare-card').count()!==3)throw Error('Three-company comparison failed');
    await page.locator('#share-compare').click();
   }
   const overflow=await page.evaluate(()=>({viewport:innerWidth,page:document.documentElement.scrollWidth,offenders:[...document.querySelectorAll('body *')].filter(e=>!e.closest('[hidden]') && getComputedStyle(e).visibility!=='hidden' && e.getBoundingClientRect().right>innerWidth+1).slice(0,15).map(e=>({tag:e.tagName,cls:e.className,id:e.id,right:e.getBoundingClientRect().right}))}));
   if(overflow.page>width || errors.length || external.length)throw Error(JSON.stringify({kind,width,overflow,errors,external}));
   await page.screenshot({path:path.join(shots,`${kind}-${width}.png`),fullPage:false});
   results.push({width,kind,overflow,errors:[...errors],external:[...external]});
  }
  await context.close();
 }
 await browser.close();fs.writeFileSync(path.join(shots,'../browser-check.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
