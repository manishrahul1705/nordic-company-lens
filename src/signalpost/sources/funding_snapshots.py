"""Offline NLOD funding observations; snapshot absence never proves no aid."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime
import zipfile
from ..identity.orgnr import valid
from .extract import Section, Source, add

BASE=Path(__file__).resolve().parents[1]/'data'
SOURCES={
 'research':('https://raw.githubusercontent.com/Forskningsradet/open-data/main/datasets/soknader2/dataset.csv','Forskningsradet'),
 'state_aid':('https://stotte.brreg.no/nb/oppslag/stoettetildeling/totalbestand/csv','Bronnoysundregistrene')}
LICENCE='https://data.norge.no/nlod/en/2.0'
INDEX_SHA={'research': '2b2843dc1318100bdac32602b811f17e198de0729b291c9e3e2b8a4e1f45f0ab', 'state_aid': '886ae1062aaa3e53aafc9355829540e1bbece673c071a4191e2df95309b96866'}


def amount(raw,comma=False):
    try:
        value=Decimal(raw.replace(' ','').replace('\u00a0','').replace(',','.') if comma else raw)
        return str(value) if value.is_finite() and value>=0 else None
    except (InvalidOperation,AttributeError):return None


def date(raw,fmt):
    if not raw:return None
    try:return datetime.strptime(raw,fmt).date().isoformat()
    except ValueError:return None


def value(kind,row):
    """Transform only explicit source cells; no collaborator/parent/name inference."""
    if kind=='research':
        org=row.get('organisasjonsnummer','');phase=row.get('prosjektfase')
        if not valid(org) or phase not in {'Bevilgning','Avsluttet'}:return None
        total=amount(row.get('tildelt_belop',''))
        start=row.get('prosjektstart','');end=row.get('prosjektslutt','')
        if total is None or not row.get('prosjektnummer') or not row.get('prosjekttittel'):return None
        return {'project_id':row['prosjektnummer'],'title':row['prosjekttittel'],
            'project_responsible_orgnr':org,'project_responsible_name':row.get('prosjektansvarlig_navn'),
            'funder':'Forskningsr\u00e5det','total_project_award':{'amount':total,'currency':None,'currency_note':'Currency is not explicit in this CSV; no conversion inferred.'},
            'amount_scope':'Total award for the project, not the organisation exclusive share or cash received; collaborators may share it.',
            'application_date':date(row.get('soknadsdato'),'%Y-%m-%d %H:%M:%S'),
            'start_year':int(start) if start.isdigit() and len(start)==4 else None,
            'end_year':int(end) if end.isdigit() and len(end)==4 else None,'phase':phase}
    org=row.get('recipient_orgnr','');instrument=row.get('instrument','')
    if not valid(org) or row.get('status')!='Registrert' or not instrument or not row.get('id'):return None
    known={'Tilskudd':'grant','L\u00e5n':'loan','Garanti':'guarantee',
        'Skatte- eller avgiftsfritak':'tax benefit','Skatte- eller avgiftsfordel':'tax benefit',
        'Rentesubsidier':'interest subsidy','Egenkapitalinvestering':'equity investment'}
    total=amount(row.get('amount',''),True)
    low=amount(row.get('range_from',''),True);high=amount(row.get('range_to',''),True)
    return {'aid_id':row['id'],'instrument':instrument,'instrument_type':known.get(instrument,'other: '+instrument),
        'recipient_orgnr':org,'recipient_name':row.get('recipient_name'),
        'specified_subunit_orgnr':row.get('subunit_orgnr') or None,
        'specified_subunit_name':row.get('subunit_name') or None,
        'awarding_body':{'organisation_number':row.get('funder_orgnr'),'name':row.get('funder_name')},
        'award_date':date(row.get('award_date'),'%d.%m.%Y'),
        'awarded_amount':{'amount':total,'currency':row.get('currency')} if total is not None else None,
        'amount_interval':{'from':low,'to':high,'currency':row.get('range_currency')} if low is not None and high is not None else None,
        'amount_scope':'Registered aid amount or aid element; not necessarily loan/guarantee face value or cash received.',
        'scheme_id':row.get('scheme_id'),'status':row['status']}


@lru_cache(maxsize=2)
def bundle(kind):
    manifest=json.loads((BASE/(kind+'_snapshot_manifest.json')).read_text(encoding='utf-8'))
    path=BASE/(kind+'_snapshot.zip')
    with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    if sha!=manifest['index_sha256'] or sha!=INDEX_SHA[kind] or manifest['source_url']!=SOURCES[kind][0] or manifest['licence_url']!=LICENCE:
        raise ValueError('Snapshot provenance/hash mismatch')
    return path,manifest


@lru_cache(maxsize=2)
def archive(path):
    # ZIP's shared-file reader serializes reads internally. Parse its central
    # directory once per run, not once per company.
    return zipfile.ZipFile(path)


def publish(envelope,blobs):
    # A valid orgnr alone cannot override failed/foreign registry identity.
    org=envelope.organisation_number
    if not valid(org) or envelope.run.sections.get('identity')!='available':return
    for kind in SOURCES:
        envelope.claims=[c for c in envelope.claims if not c.field.startswith(kind+'.')]
        diagnostic={'mode':'bundled_snapshot','runtime_http_requests':0,'published':0}
        envelope.run.refresh.setdefault('funding_snapshots',{})[kind]=diagnostic
        try:
            path,manifest=bundle(kind)
            from ..web.social_universe import registered_relations
            relations=registered_relations(envelope)
            units={str(c.value['organisation_number']):c for c in envelope.claims
                if c.field.startswith('subunits.unit.') and c.availability=='available' and not c.carried_forward
                and isinstance(c.value,dict) and c.value.get('organisation_number')
                and relations.get(str(c.value['organisation_number']),{}).get('kind')=='subunit'}
            scope=[org]+(sorted(units) if kind=='state_aid' else [])
            records=[]
            z=archive(path)
            for number in scope:
                try:records.extend(json.loads(z.read(number+'.json')))
                except KeyError:pass
            diagnostic.update(dataset_sha256=manifest['dataset_sha256'],snapshot_retrieved_at=manifest['retrieved_at'],
                coverage='lower bound; snapshot absence is not no funding')
            section=Section()
            for record in records:
                raw=record['source_cells'];v=value(kind,raw)
                subject=v.get('project_responsible_orgnr',v.get('recipient_orgnr')) if v else None
                if subject!=org and not(kind=='state_aid' and subject in units):continue
                if subject!=org:
                    v.update(matched_via='registered recipient subunit '+subject,subject_company_orgnr=org)
                # Specified subunit is retained as a distinct source field. Never
                # match a subunit/collaborator by name or promote it to recipient.
                body=json.dumps(raw,ensure_ascii=False,separators=(',',':')).encode('utf-8')
                sha=blobs.put(body)
                source=Source(manifest['source_url'],body,sha,manifest['retrieved_at'],
                    'NLOD 2.0; '+manifest['credit']+'; selected CSV row cells (UTF-8 JSON derivation), record '+str(record['source_row'])+'; full dataset SHA-256 '+manifest['dataset_sha256'])
                ident=v.get('project_id',v.get('aid_id'))
                add(section,source,org,'funding',kind+'.'+ident,v,'/',source_class='official_registry',
                    method='signalpost.funding.csv-selected-row.v1')
                if subject!=org:
                    section.claims[-1].evidence_ids.extend(units[subject].evidence_ids)
                section.claims[-1].reasons.update(label=('Research project (total project award)' if kind=='research' else 'State aid: '+v['instrument']),
                    licence=LICENCE,snapshot='Historical bundled observation; not live-checked',attribution=manifest['credit'])
            fields={c.field for c in section.claims}
            # Replace this snapshot family only; no stale claim may masquerade as current.
            envelope.claims=[c for c in envelope.claims if not c.field.startswith(kind+'.')]+section.claims
            ev={e.id:e for e in envelope.evidence};ev.update({e.id:e for e in section.evidence});envelope.evidence=list(ev.values())
            diagnostic['published']=len(fields)
            diagnostic['state']='available' if fields else 'not_established_in_snapshot'
        except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile) as exc:
            diagnostic.update(state='snapshot_unavailable',error=type(exc).__name__)
