"""Build offline NLOD funding indexes from complete local CSV snapshots, never HTTP."""
import argparse
from collections import defaultdict,Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import zipfile
from signalpost.sources.funding_snapshots import SOURCES,LICENCE,value

RESEARCH=('prosjektnummer','prosjekttittel','organisasjonsnummer','prosjektansvarlig_navn','prosjektfase','tildelt_belop','soknadsdato','prosjektstart','prosjektslutt')
AID_KEYS={'id':'St\u00f8ttetiltaksnummer','status':'Status','recipient_orgnr':'Organisasjonsnummer st\u00f8ttemottaker',
 'recipient_name':'Navn st\u00f8ttemottaker','subunit_orgnr':'Organisasjonsnummer spesifisert st\u00f8ttemottaker',
 'subunit_name':'Navn spesifisert st\u00f8ttemottaker','funder_orgnr':'Organisasjonsnummer st\u00f8ttegiver','funder_name':'Navn st\u00f8ttegiver',
 'award_date':'Tildelingsdato','amount':'Tildelt bel\u00f8p','currency':'Tildelt bel\u00f8p valuta',
 'range_from':'Bel\u00f8psintervall fra bel\u00f8p','range_to':'Bel\u00f8psintervall til bel\u00f8p','range_currency':'Bel\u00f8psintervall valuta',
 'instrument':'St\u00f8tteinstrument','scheme_id':'Tilknyttet st\u00f8tteordning'}


def read_records(kind,path):
    codec='utf-8-sig' if kind=='research' else 'utf-16-le'
    delimiter=',' if kind=='research' else ';'
    with Path(path).open(encoding=codec,newline='') as f:
        reader=csv.DictReader(f,delimiter=delimiter,strict=True)
        required=set(RESEARCH if kind=='research' else AID_KEYS.values())
        if not required<=set(reader.fieldnames or []):raise ValueError('Missing CSV columns')
        for n,row in enumerate(reader,1):
            if None in row or any(v is None for v in row.values()):raise ValueError('Incomplete CSV record')
            cells={k:row[k] for k in RESEARCH} if kind=='research' else {k:row[v] for k,v in AID_KEYS.items()}
            yield n,cells


def build(kind,path,download,output):
    metadata=json.loads(Path(download).read_text(encoding='utf-8'))
    with Path(path).open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    if metadata.get('status')!=200 or metadata.get('final_url',metadata['source_url'])!=SOURCES[kind][0]:raise ValueError('Expected direct official HTTP 200')
    if sha!=metadata['dataset_sha256'] or metadata['source_url']!=SOURCES[kind][0]:raise ValueError('Dataset provenance mismatch')
    if Path(path).stat().st_size!=int(metadata['headers'].get('content-length',Path(path).stat().st_size)):raise ValueError('Incomplete bulk transfer')
    by_org=defaultdict(list);total=0;excluded=Counter();instruments=Counter();seen={}
    for n,cells in read_records(kind,path):
        total=n;v=value(kind,cells)
        if v is None:excluded[cells.get('prosjektfase',cells.get('status','invalid'))]+=1;continue
        org=v.get('project_responsible_orgnr',v.get('recipient_orgnr'));ident=v.get('project_id',v.get('aid_id'))
        if ident in seen:raise ValueError('Duplicate record id '+ident)
        seen[ident]=org
        by_org[org].append({'source_row':n,'source_cells':cells})
        if kind=='state_aid':instruments[v['instrument']]+=1
    output=Path(output);output.mkdir(exist_ok=True,parents=True);dest=output/(kind+'_snapshot.zip')
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for org,records in sorted(by_org.items()):
            info=zipfile.ZipInfo(org+'.json',date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,json.dumps(records,ensure_ascii=False,separators=(',',':')),compresslevel=9)
    manifest={'schema_version':1,'source_url':metadata['source_url'],'retrieved_at':metadata['retrieved_at'].replace('+00:00','Z'),
        'dataset_sha256':sha,'dataset_bytes':Path(path).stat().st_size,'dataset_rows':total,'indexed_records':len(seen),
        'indexed_companies':len(by_org),'excluded':dict(excluded),'instruments':dict(instruments),
        'source_encoding':'utf-8-sig' if kind=='research' else 'utf-16-le',
        'source_columns':list(RESEARCH) if kind=='research' else AID_KEYS,
        'index_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'index_bytes':dest.stat().st_size,
        'credit':'Forskningsr\u00e5det' if kind=='research' else 'Br\u00f8nn\u00f8ysundregistrene','licence':'NLOD 2.0','licence_url':LICENCE,
        'transformations':['Decode official CSV; retain selected public cells, preserving their text; omit personal/contact columns.',
            'Research: retain only Bevilgning/Avsluttet with valid responsible organisation number and finite nonnegative total project award.',
            'State aid: retain only Registrert records with exact recipient organisation number and actual instrument; preserve specified subunit separately.',
            'Group selected rows by exact responsible/recipient orgnr; deterministic ZIP with per-company JSON and original data-record ordinal.',
            'Runtime stores selected row cells as UTF-8 JSON evidence extracts, explicitly labelled derived CSV rows with full dataset hash.',
            'No negative absence claim, collaborator allocation, name match, parent inference or live-freshness claim.'],
        'limitations':(['Research excludes newer Tibi system; coverage is a lower bound.'] if kind=='research' else ['Only explicitly registered corporate recipients are indexed; personal recipients and illegal-aid status are excluded.'])+['Snapshot may omit later updates; absence never proves no award.']}
    (output/(kind+'_snapshot_manifest.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('kind',choices=SOURCES);p.add_argument('source',type=Path);p.add_argument('--download-manifest',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('src/signalpost/data'));a=p.parse_args();print(json.dumps(build(a.kind,a.source,a.download_manifest,a.output),indent=2))
