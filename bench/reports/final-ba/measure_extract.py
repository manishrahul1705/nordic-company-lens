"""Recount information views from the committed final-run population extract."""
import collections,json,sys
from pathlib import Path
HERE=Path(__file__).parent
sys.path.insert(0,str(HERE/'accuracy'))
import common as C
stats=collections.defaultdict(lambda:{'companies':set(),'claims':0})
for r in C.read_envelopes():
    for c in r['claims']:
        f=c['field'];tags=[]
        for k,pre in [('identity','identity.'),('roles','roles.'),('accounts','accounts.'),('registry_date_activity','registry_dated_activity.'),('previous_names','identity.historical_name.'),('subunits','subunits.'),('group_structure','identity.group_structure.'),('signatur','roles.signatur'),('prokura','roles.prokura'),('registry_changes','registry_change.'),('GLEIF','identity.gleif'),('TED','procurement_award.'),('brands','public_brand'),('social','social_profile.'),('news','news_item.'),('hiring','hiring.job.'),('research','research.'),('state_aid','state_aid.'),('SkatteFUNN','skattefunn.'),('DiBK','central_approval.'),('cleaning_approval','cleaning_approval.'),('workshop_approval','workshop_approval.'),('related_company_websites','related_company_website.')]:
            if f.startswith(pre):tags.append(k)
        if f.endswith('.audit_status'):tags.append('audit_status')
        if '.historical_name.'in f:tags.append('historical_names_all_scopes')
        if f.startswith('subunits.') and '.historical_name.'in f:tags.append('subunit_historical_names')
        if f=='official_website':tags.append('websites')
        if '.wikidata'in f:tags.append('Wikidata')
        for k in tags:stats[k]['companies'].add(r['organisation_number']);stats[k]['claims']+=1
for k in ['previous_names','TED']:stats[k]
result={k:{'companies':len(v['companies']),'claims':v['claims']}for k,v in stats.items()}
p=HERE/'measurement.json';m=json.loads(p.read_text(encoding='utf-8'))
if '--write'in sys.argv:m['families']=result;p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
else:assert m['families']==result
print(json.dumps(result,indent=2))
