"""Retain independent source context for the human adjudication; no network."""
import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import common as C
from signalpost.sources.text import decode_body
rows={r['organisation_number']:r for r in C.read_envelopes()};blobs=C.read_blobs()
items=[json.loads(l) for l in (C.HERE/'sample.jsonl').open(encoding='utf-8')];support=[]
for index,item in enumerate(items):
    ch=item['check']
    if ch.get('span_in_body') and ch.get('org_in_source_url') and ch.get('value_at_locator')==item['value']:continue
    r=rows[item['orgnr']];claim=next(c for c in r['claims'] if c['field']==item['field'] and c['value']==item['value']);ev={e['id']:e for e in r['evidence']};records=[]
    for ref in claim['evidence_ids']:
        e=ev[ref];body=blobs[e['content_sha256']];text=decode_body(body);doc=None;at=None
        try:
            doc=json.loads(text);at=doc if e['locator']=='/' else C.pointer(doc,e['locator'])
        except (ValueError,TypeError,KeyError,IndexError):pass
        record={'evidence':e,'located_value':at}
        if doc is not None and '/endringer/' in e['locator']:
            record['parent_event']=C.pointer(doc,e['locator'].split('/endringer/')[0])
        if doc is not None and item['field'].endswith('.audit_status'):
            record['revision_flags']=C.pointer(doc,e['locator'].rsplit('/',1)[0])
        if doc is not None and item['field'].startswith('roles.role.'):
            path=e['locator'].split('/roller/')[0];record['role_group']=C.pointer(doc,path)
        if doc is None:
            from signalpost.web.html import Page
            page=Page(body,e['source_url']);record['page_title']=page.title;record['page_visible']=page.visible;record['page_meta']=page.meta
        records.append(record)
    related=[]
    if item['field'].startswith(('hiring.','related_company_website.','social_profile.','public_brand','website_description.','contact.','registry_change.')):
        related=[c for c in r['claims'] if c['field']=='official_website' or c['field'].startswith(('subunits.unit.','identity.group_structure.'))]
    support.append({'index':index,'orgnr':item['orgnr'],'field':item['field'],'claim':claim,'source_records':records,'related_published_claims':related})
(C.HERE/'hand-review-support.json').write_text(json.dumps(support,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'manual_items':len(support),'indexes':[x['index']for x in support]}))
