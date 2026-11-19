"""Publish case-specific notes after reading the ten final raw result bindings."""
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
import httpx
from signalpost.io.input_adapter import read
from signalpost.identity.orgnr import valid
from signalpost.web.wikidata import query,ENDPOINT

out=Path(__file__).parent
root=Path('bench/runs/stage-ag-20261119')
rows=json.loads((out/'review-candidates.json').read_text(encoding='utf-8'))
assert len(rows)==10 and len({r['organisation_number'] for r in rows})==10
notes={
 ('922828172','P1448'):'The raw row binds 922828172 to Q111605409 and states the Norwegian official name “Tensio AS”. This agrees with the registry name TENSIO AS after case/whitespace normalization; the primary registry name remains unchanged.',
 ('923354220','P1128'):'The statement reports 18 employees with unit Q199 (one) and P585 in 2023 at YEAR precision (9). It is a dated 2023 observation, not an assertion of 18 employees today or specifically on 1 January. The current registry count remains primary.',
 ('980910857','P571'):'The row identifies this exact organisation number on Q23878247 and reports inception in 1999 with precision 9. Only the year is established; the padded 1 January timestamp is not promoted to a day-precise founding date. The registry founding date retains precedence.',
 ('938092516','P159'):'The own-item P159 statement explicitly names Q5245991, Oslo kommune. The municipality identifier and Norwegian label are retained. No street address is invented, and a registry contact address is not used to infer headquarters.',
 ('968386085','P452'):'The own-item P452 statement names Q29585660, “utgivelse av aviser”. The industry class is taken directly from Wikidata, not guessed from the company name or silently converted to a NACE code.',
 ('971558415','P2003'):'The result binds the exact orgnr and Instagram identifier danseinformasjonen. The existing website-discovered profile passes the same handle/site-link rules and receives this revision-bound citation without a duplicate profile or changed fact ID. No Instagram request is made.',
 ('975569306','P856'):'The exact-orgnr item explicitly reports https://glassverketif.no/. It is published as an attributed Wikidata website assertion; that fact alone does not establish website ownership or create a VERIFIED website claim.',
 ('935189365','P571'):'The row binds HESTENES KRAFTVERK AS’s orgnr to Q136446847 and reports 11 February 2025 with day precision (11), Gregorian calendar. This is compatible with the registry founding date, so the separately attributed date is retained.',
 ('939882480','P159'):'The P159 row on the exact-orgnr item names Q10428388, Bergen kommune. This supports a headquarters location at municipality granularity; it does not support a more specific office address.',
 ('971492325','P159'):'The own-item P159 statement explicitly names Q42293305, Indre Østfold. This is an attributed location statement, independent of the museum’s conflicting inception and website properties, which are withheld separately.',
}
snapshots=out/'sparql';snapshots.mkdir(exist_ok=True)
report=json.loads((root/'report.json').read_text(encoding='utf-8'))
index=json.loads((root/'state/wikidata-index.json').read_text(encoding='utf-8'))
observed={record['sha']:record['source_url'] for records in index['records'].values() for record in records}
numbers=sorted(org for org in read(Path('bench/inputs/1000-r3/batch.jsonl')).unique if valid(org))
requests=[e for e in report['request_log'] if e.get('section')=='wikidata']
manifest=[]
for i,event in enumerate(requests):
    sha=event['content_sha256'];raw=(root/'state/blobs'/sha).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==sha
    (snapshots/(sha+'.json')).write_bytes(raw)
    # Nonempty results retain the actual response URL in the run-local index.
    # The empty batch has no record; reconstruct that URL from measured source
    # code, the frozen input and the recorded batch order, without any HTTP.
    url=observed.get(sha) or str(httpx.URL(ENDPOINT,params={'query':query(numbers[i*200:(i+1)*200]),'format':'json'}))
    text=parse_qs(urlsplit(url).query)['query'][0]
    (snapshots/f'batch-{i+1}.rq').write_text(text+'\n',encoding='utf-8')
    manifest.append({'batch':i+1,'method':'GET','url':url,'status':event['status'],'sha256':sha,
                     'response_file':sha+'.json','query_file':f'batch-{i+1}.rq',
                     'url_from_live_response_index':sha in observed})
(snapshots/'requests.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
lines=['# Stage AG: ten hand reviews','',
       'Ten published claims across ten companies and seven requested properties. The full values and raw result rows were inspected. '
       'These are deliberately chosen examples, not a random precision estimate. Revenue P2139 and LinkedIn P4264 have no matching cohort statements, so no live claims for those properties can be reviewed.','',
       'Each source response below is an exact retained byte snapshot. [Request URLs, hashes and query texts](sparql/requests.json) cover all five batches. '
       'The empty-result batch URL is reconstructed from the measured code/input/order; URLs for every cited nonempty result are retained from the live response index. '
       'No extra entity, label, revision or social-platform request was made during the measured run.','',
       '| Company | Property and published value | Cited evidence | Why correct |','|---|---|---|---|']
reviewed=[]
def cell(value):return str(value).replace('|','&#124;').replace('\n','<br>')
for row in rows:
    org,prop=row['organisation_number'],row['property'];ev=row['evidence'];b=row['binding']
    assert b['org']['value']==org
    revision=b['revision']['value'];item=b['item']['value'].rsplit('/',1)[1]
    revurl=f'https://www.wikidata.org/w/index.php?title={item}&oldid={revision}'
    assert revurl in ev['source_identifier']
    note=notes[(org,prop)]
    row={**row,'verdict':'correct','why_correct':note};reviewed.append(row)
    citation=f"[SPARQL snapshot](sparql/{ev['content_sha256']}.json), `{ev['locator']}`<br>[{item} revision {revision}]({revurl})<br>SHA-256 `{ev['content_sha256']}`"
    value=prop+' · `'+json.dumps(row['claim']['value'],ensure_ascii=False)+'`'
    lines.append('| '+' | '.join(cell(x) for x in (f"{row['company']} ({org})",value,citation,note))+' |')
(out/'REVIEW.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')
(out/'reviewed.json').write_text(json.dumps(reviewed,indent=2,ensure_ascii=False),encoding='utf-8')
print('10 claims reviewed across 10 companies; five exact SPARQL response snapshots saved')
