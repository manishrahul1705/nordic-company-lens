"""Replay the extended role allowlist without overwriting the prior audit."""
import json,random
import replay_contact_precision as replay


def main():
    previous=replay.OUT
    replay.OUT=replay.ROOT/'bench/reports/contact-role-extension'
    replay.main()
    old=json.loads((previous/'decisions.json').read_text(encoding='utf8'))
    new=json.loads((replay.OUT/'decisions.json').read_text(encoding='utf8'))
    key=lambda x:(x['orgnr'],x['field'],x['value'])
    before={key(x):x for x in old};gains=[]
    for item in new:
        prior=before[key(item)]
        assert not prior['kept'] or item['kept'], 'Extension lost a contact'
        if item['kept'] and not prior['kept']:
            assert item['field'].startswith('contact.email.')
            gains.append(item)
        if item['field'].startswith('contact.phone.'):assert item['kept']==prior['kept']
    sample=random.Random(20261112).sample(sorted(gains,key=key),min(20,len(gains)))
    summary=json.loads((replay.OUT/'summary.json').read_text())
    summary['previous_policy_after']=json.loads((previous/'summary.json').read_text())['after']
    summary['newly_retained']=len(gains);summary['newly_retained_review_sample']=len(sample)
    for name,value in [('summary.json',summary),('newly-retained.json',gains),('new-20-review.json',sample)]:
        (replay.OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
