"""Write the complete manual review ledger from the saved proof/link evidence."""
import json
from pathlib import Path
OUT=Path('bench/reports/r3-benchmark')
website_findings={
'915015743':('doubtful','Exact title/copyright but site gives Gronaasen 6, Tysnes; registry gives Solesvika 136, Austevoll and ebru.no. Name alone cannot resolve this.'),
'925787884':('doubtful','Publisher/author brand fits registry publishing purpose, but only the unique-name/domain rule proves the entity; no exact entity identifier in saved proof.'),
'919086815':('doubtful','Correct-looking name and Stavern metadata but empty JavaScript root; no visible ownership body was captured.'),
'823568002':('doubtful','Andrews lawyer branding and Moss location are plausible; generic occupational label plus surname is insufficient exact-entity evidence.'),
'935829437':('doubtful','AS title and Oslo metadata only; body is an empty JavaScript root.'),
'934407253':('wrong','Hosting placeholder: Her kommer: www.flaveuria.no. No company identity evidence.'),
'915279082':('correct','Exact organisation number NO 915 279 082 MVA and matching Soknedal address on the saved company page.'),
'929481070':('correct','Software business; Kirkenes/Dr Palmstroms vei/Nothing Hill agrees with the registry address. Inspect retained proof after narrowing.'),
'988236756':('wrong','Bygg-Tema site identifies Finnsnes/Midt-Troms, while target BYGGTEMA is Hokksund/Ovre Eiker. Punctuation-collapsed names are not exact company identity.'),
'995654539':('correct','Takst Maleng AS, Folkestadhogda 12, 1592 Valer and registered phone/contact support exact entity.'),
'916800916':('doubtful','Exact legal masthead and alarm business, but AS name alone is insufficient after precision review.'),
'914507812':('wrong','arne@icedrift.no is the named Ice Drift manager on a staff list. Target is Straumsnes Utvikling; domain is registered to four entities. Staff email is not site ownership.'),
'928736032':('doubtful','REBR AS title/copyright and software apps are plausible, but no independent registry contact/number proves exact entity.'),
'923354220':('correct','Saved body explicitly identifies Eidefoss Vannkraft AS, 923 354 220, Vagaa address. Initial localized name proof understates the page evidence.'),
'979973969':('correct','Registered mobile 99092010 is the site contact, alongside Jar Helse and matching Jar postcode/address.'),
'935666481':('doubtful','Hvalen Studio AS footer identifies a different street/postcode from current registry; name-only cannot resolve a move versus another entity.'),
'925273422':('wrong','Hosting placeholder: Her kommer: www.omj-entreprenor.no. No company identity evidence.'),
'993347728':('correct','Exact legal name plus registered mobile 90836811 for Morten Reffhaug in the contact page; LED/event activity agrees.'),
'999516386':('correct','Registered mobile 90873490, legal name Risikokonsulenten AS and named Fred Thomassen corroborate the same business.'),
'980622444':('correct','Exact 980 622 444 and matching Skarersletta 18, Lorenskog retail business.'),
'927441217':('doubtful','Norwegian consultancy branding fits but unique name/domain alone cannot establish the exact registry entity.'),
'921320868':('correct','About page explicitly says owned by Kitchen & Living Group AS with exact 921 320 868, matching Hunndalen address.'),
'998008123':('correct','Registered mobile 97128141 is the site contact; NERE AS and storage/boat services agree with registry business.')}
# Every new profile is reviewed, including additions to already-social companies.
social_doubt={1:'Founder/personal Bjorn Kaupang profiles, not the ObjectFront legal company.',6:'Artist/person Marte Hallem and opaque channel; cannot establish Scene Midt corporate ownership.',8:'Personal Thomas Bech channel; business use is not exact corporate attribution.',10:'Loff brand/channel not independently tied to the exact Lucky View entity in the link excerpt.',16:'Tensio network/group handles may span subsidiaries; exact legal-company attribution is not established.',21:'Scenehuset venue accounts are distinct from the Danseinformasjonen institution; company-specific attribution is not established.',29:'RentHall global/group accounts are not proven specific to the Norwegian AS.'}
social_wrong={15:'Wrong-company website (Finnsnes namesake), so its Facebook is wrong for the Hokksund input.',19:'Wrong site owner inferred from a shared employee email; Ice Drift socials are not Straumsnes Utvikling.',23:'istiaqdesign is a designer/agency handle unrelated to Stillasfordeg.'}
web=json.loads((OUT/'website-review.json').read_text(encoding='utf8'))
for item in web:item['review']={'verdict':website_findings[item['orgnr']][0],'reason':website_findings[item['orgnr']][1],'method':'Manual inspection of saved live page text, ownership excerpt and official registry context; no new social-platform requests.'}
social=json.loads((OUT/'social-review.json').read_text(encoding='utf8'))
for i,item in enumerate(social):
 for profile in item['social']:
  verdict='wrong' if i in social_wrong else 'doubtful' if i in social_doubt else 'correct'
  reason=social_wrong.get(i) or social_doubt.get(i) or 'Profile is explicitly linked from the verified business page and the handle/brand aligns with the named business. Strict runtime name matching may conservatively withhold a genuine alias.'
  profile['review']={'verdict':verdict,'reason':reason,'method':'Manual source-page link and company/brand context review, not fetching the social platform.'}
for name,value in [('website-review.json',web),('social-review.json',social)]:
 (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def safe(value):return str(value).replace('|','/').replace('\n',' ').replace('\r',' ')
lines=['# R3 complete source review','', 'Every gained website (23) and every new social profile (58 across 34 companies, including additions to existing social companies) is listed. Verdicts describe the raw live candidate before narrowing. Removed/doubtful claims are not accepted as final results.','', '## Websites','', '| Company | Orgnr | URL | Proof / candidate source | Exact saved proof excerpt | Verdict | Reason |','|---|---|---|---|---|---|---|']
for r in web:
 w=r['website'];v=w['value'];excerpt=' / '.join(e['claim_span'] for e in w['evidence']);lines.append('| '+' | '.join(map(safe,[r['company'],r['orgnr'],v['final_url'],v['proof_type']+' / '+v['candidate_origin'],excerpt,r['review']['verdict'],r['review']['reason']]))+' |')
lines+=['','## Social profiles','','| Company | Orgnr | Profile URL | Website proof | Link source and exact excerpt | Verdict | Reason |','|---|---|---|---|---|---|---|']
for r in social:
 for s in r['social']:
  excerpt=' / '.join(e['source_url']+' : '+e['claim_span'] for e in s['evidence']);proof=r['website']['value']['proof_type'] if r['website'] else 'registry social';lines.append('| '+' | '.join(map(safe,[r['company'],r['orgnr'],s['value']['url'],proof,excerpt,s['review']['verdict'],s['review']['reason']]))+' |')
lines+=['','## Baseline losses and host changes','','No baseline website company is missing from the raw live candidate. Nuve AS 936094112 changed from https://nuve.no to https://www.nuve.no; the exact same body hash and orgnr proof establish the same site. No wrong-company domain change. Offline post-narrowing losses are reported separately in SCOREBOARD.md.','']
(OUT/'REVIEW.md').write_text('\n'.join(lines),encoding='utf8')
from collections import Counter
print('Website review',dict(Counter(r['review']['verdict'] for r in web)))
print('Social review',dict(Counter(s['review']['verdict'] for r in social for s in r['social'])))
