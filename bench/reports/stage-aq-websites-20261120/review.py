"""Review every recovery and nine withheld controls without additional HTTP."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from signalpost.web.html import Page
from signalpost.web.proof import orgnrs
from signalpost.web.social_universe import index,name_keys

HERE=Path(__file__).resolve().parent


def main():
    out=Path('bench/runs/stage-aq-publisher1000')
    new=json.loads((out/'new-sites.json').read_text(encoding='utf-8'))
    assert len(new)==1 and new[0]['orgnr']=='912492575'
    x=new[0]; c=x['claim']; ev=x['evidence'][0]
    body=(out/'state/blobs'/ev['content_sha256']).read_bytes(); page=Page(body,ev['source_url'])
    assert hashlib.sha256(body).hexdigest()==ev['content_sha256'] and ev['claim_span'] in body.decode()
    assert orgnrs(' '.join(page.brand_parts))=={'912492575'}
    assert 'Haugesund Elektriske AS' in page.title and 'Haugesund Elektriske AS' in ' '.join(page.footer_parts)
    assert 'Skjoldavegen 121' in page.owner_text and '52717711' in page.owner_text
    data=index();assert data is not None
    matches={o for k in name_keys('Haugesund Elektriske AS') for o in data['keys'].get(k,[])}
    assert not matches-{'912492575'}
    x['why_correct']='Exact sole publisher/footer organisation number 912 492 575, not an article/customer mention; registry-nominated domain; registered street/postcode and phone also match. Shortened title/footer name only omits FORRETNING with the same AS form. No other registered company matches that shortened name. Full proof and final cohort/group/entity guards retain this site.'
    x['registry_comparison']={'legal_name':'HAUGESUND ELEKTRISKE FORRETNING AS','street':'Skjoldavegen 121','postcode':'5519','phone':'52717711'}
    x['universe_short_name_matches']=sorted(matches)
    diagnostics=json.loads(Path('bench/runs/stage-aq-1000-v2/diagnostics.json').read_text(encoding='utf-8'))
    controls=[('982410851','MARUN AS','Empty hosting page at .no; unrelated Cristty redirect at .com lacks exact company evidence; withhold.'),
        ('997352572','VISTNES','Redirected publisher is Randaberg Regnskap; different_legal_entity veto; withhold.'),
        ('976746651','BNTV','Wemail publisher is not this company; different_legal_entity veto; withhold.'),
        ('887820082','ARENA HOLDING','HugeDomains marketplace target; no ownership proof; withhold.'),
        ('981391594','TEROB','HugeDomains marketplace target; no ownership proof; withhold.'),
        ('930888923','ZM DRIFT','Webhuset explicitly parked-domain placeholder; withhold.'),
        ('923219137','GREEN4YOU','HugeDomains marketplace target; no ownership proof; withhold.'),
        ('915015743','INVENSYS','Global Schneider Electric page has insufficient exact Norwegian company ownership proof; withhold.'),
        ('833894862','SUPPLYSYNC','Mixo platform terms are a different publisher; withhold.')]
    reviewed=[]
    trial=Path('bench/runs/stage-aq-1000-v2')
    events=json.loads((trial/'extra-requests.json').read_text(encoding='utf-8'))
    # Names below are replaced by the actual saved registry names.
    names={}
    for line in Path('bench/runs/stage-am-live1000/envelopes.jsonl').open(encoding='utf-8'):
        row=json.loads(line)
        names[row['organisation_number']]=next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),'')
    for org,_,why in controls:
        d=next(d for d in diagnostics if d['orgnr']==org)
        pages=[]
        for event in events:
            if event['organisation_number']!=org or event.get('status')!=200 or not event.get('content_sha256') or event['url'].endswith(('robots.txt','.xml')):continue
            raw=(trial/'state/blobs'/event['content_sha256']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==event['content_sha256']
            page=Page(raw,event['url'])
            span=page.span_for(page.title) if page.title else None
            pages.append({'url':event['url'],'sha256':event['content_sha256'],'title':page.title,
                'title_verbatim_span':span,'publisher_orgnrs':sorted(orgnrs(' '.join(page.brand_parts)))})
            break
        reviewed.append({'orgnr':org,'company':names[org],'result':'withheld control, not a newly verified site',
            'why_correct':why,'checked_saved_page':pages,'attempts':d['attempted']})
    (HERE/'ownership-review.json').write_text(json.dumps({'new_sites_reviewed':[x],
        'new_sites_available_to_review':1,'requested_ten_new_sites':'Only one recovered; all recovered sites reviewed. Nine additional controls are explicitly withheld, not invented recoveries.',
        'withheld_controls':reviewed},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Reviewed every recovered site (1) and 9 explicitly withheld controls.')


if __name__=='__main__':main()
