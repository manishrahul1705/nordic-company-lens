"""Independently compare every published funding value with the original official CSV."""
import csv,json,hashlib,zipfile
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from collections import Counter
root=Path(__file__).parent;cache=Path('bench/cache/aid-snapshots-20261120')
claims=json.loads((root/'new-claims.json').read_text(encoding='utf-8'));by={}
for c in claims:
    k=c['claim']['field'].split('.')[0];v=c['claim']['value'];ident=v.get('project_id',v.get('aid_id'));by.setdefault(k,{}).setdefault(ident,[]).append(c)
checks=Counter();review=[]
for kind in ['research','state_aid']:
    manifest=json.loads(Path(f'src/signalpost/data/{kind}_snapshot_manifest.json').read_text(encoding='utf-8'))
    source=cache/('research.raw' if kind=='research' else 'state-aid.csv')
    with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==manifest['dataset_sha256']
    with source.open(encoding='utf-8-sig' if kind=='research' else 'utf-16-le',newline='') as f:
        rows=csv.DictReader(f,delimiter=',' if kind=='research' else ';',strict=True)
        seen=set()
        for n,row in enumerate(rows,1):
            ident=row['prosjektnummer'] if kind=='research' else row['St\u00f8ttetiltaksnummer']
            for c in by[kind].get(ident,[]):
                v=c['claim']['value'];org=c['orgnr'];ev=next(e for e in c['evidence'] if e['source_url']==manifest['source_url'])
                if kind=='research':
                    assert row['prosjektfase'] in {'Bevilgning','Avsluttet'}
                    assert row['organisasjonsnummer']==org==v['project_responsible_orgnr']
                    assert row['prosjekttittel']==v['title'] and row['prosjektansvarlig_navn']==v['project_responsible_name']
                    assert Decimal(row['tildelt_belop'])==Decimal(v['total_project_award']['amount'])
                    assert datetime.strptime(row['soknadsdato'],'%Y-%m-%d %H:%M:%S').date().isoformat()==v['application_date']
                    assert int(row['prosjektstart'])==v['start_year'] and int(row['prosjektslutt'])==v['end_year']
                    assert v['funder']=='Forskningsr\u00e5det' and v['total_project_award']['currency'] is None
                else:
                    assert row['Status']=='Registrert'
                    assert row['Organisasjonsnummer st\u00f8ttemottaker']==v['recipient_orgnr']
                    assert row['Organisasjonsnummer spesifisert st\u00f8ttemottaker']==(v['specified_subunit_orgnr'] or '')
                    assert row['St\u00f8tteinstrument']==v['instrument']
                    assert row['Navn st\u00f8ttegiver']==v['awarding_body']['name']
                    assert row['Organisasjonsnummer st\u00f8ttegiver']==v['awarding_body']['organisation_number']
                    assert datetime.strptime(row['Tildelingsdato'],'%d.%m.%Y').date().isoformat()==v['award_date']
                    if v['awarded_amount'] is not None:
                        assert Decimal(row['Tildelt bel\u00f8p'].replace(',','.'))==Decimal(v['awarded_amount']['amount'])
                        assert row['Tildelt bel\u00f8p valuta']==v['awarded_amount']['currency']
                    if v['amount_interval'] is not None:
                        assert Decimal(row['Bel\u00f8psintervall fra bel\u00f8p'].replace(',','.'))==Decimal(v['amount_interval']['from'])
                        assert Decimal(row['Bel\u00f8psintervall til bel\u00f8p'].replace(',','.'))==Decimal(v['amount_interval']['to'])
                        assert row['Bel\u00f8psintervall valuta']==v['amount_interval']['currency']
                    assert v['recipient_orgnr']==org or v['matched_via']=='registered recipient subunit '+v['recipient_orgnr']
                assert 'record '+str(n)+';' in ev['source_identifier']
                assert manifest['dataset_sha256'] in ev['source_identifier'] and ev['source_url']==manifest['source_url']
                seen.add(c['claim']['id']);checks[kind]+=1
                review.append({'source':kind,'source_row':n,'orgnr':org,'company':c['company'],'claim':v,'evidence':ev})
        assert len(seen)==sum(map(len,by[kind].values()))
(root/'audit.json').write_text(json.dumps({'checked':dict(checks),'result':'PASS: all published values and source record ordinals match official raw CSVs'},indent=2),encoding='utf-8')
(root/'review-candidates.json').write_text(json.dumps(review,ensure_ascii=False,indent=1),encoding='utf-8');print(dict(checks))
