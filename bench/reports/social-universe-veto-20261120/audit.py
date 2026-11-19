"""Check every surviving profile and compare the previously reviewed 46."""
import hashlib
import json
from pathlib import Path
from signalpost.models.envelope import Envelope
from signalpost.web.social import context_for_envelope,profile_key
from signalpost.web.social_universe import assess,index

out=Path(__file__).parent
root=Path('bench/runs/social-universe-veto-20261120')
previous=json.loads(Path('bench/reports/proven-site-socials-20261120/reviewed.json').read_text(encoding='utf-8'))
before={(r['organisation_number'],profile_key(r['claim']['value']['url'])):r for r in previous}
survived=set();count=0;exceptions=[];rows={}
for line in (root/'envelopes.jsonl').open(encoding='utf-8'):
    row=Envelope.model_validate(json.loads(line));org=row.organisation_number
    context=context_for_envelope(row)
    for claim in row.claims:
        if not claim.field.startswith(('social_profile.','registry_social.')) or claim.availability!='available':continue
        result=assess(claim.value['url'],context)
        assert result['state']=='allow',(org,claim.value,result)
        count+=1
        key=org,profile_key(claim.value['url'])
        if key in before:survived.add(key)
        for match in result['matches']:
            relation=match['permitted_registry_relationship'];assert relation and relation['evidence_ids']
            exceptions.append({'organisation_number':org,'url':claim.value['url'],'match':match})
missing=[{'organisation_number':key[0],'company':r['company'],'url':r['claim']['value']['url']}
         for key,r in before.items() if key not in survived]
assert len(survived)==43 and len(missing)==3
measurement=json.loads((out/'measurement.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in measurement['source_sha256'].items())
data=index();assert data['rows']==411160
result={'passed':True,'surviving_profiles_checked':count,'previous_46_retained':len(survived),
        'previous_46_withheld':missing,'permitted_relationship_exceptions_used':exceptions,
        'universe_rows':data['rows'],'source_matches_replay':True,'new_network_requests':0}
(out/'audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
