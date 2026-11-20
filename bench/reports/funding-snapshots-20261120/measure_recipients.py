"""Read-only cohort census, run before state-aid index publication."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib
from signalpost.identity.orgnr import valid

cache=Path('bench/cache/aid-snapshots-20261120');p=cache/'state-aid.csv';metadata=json.loads((cache/'state-aid-csv-download.json').read_text());assert metadata['complete_length']
with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==metadata['dataset_sha256']
wanted={json.loads(l)['organisation_number'] for l in Path('bench/inputs/1000-r3/batch.jsonl').read_text().splitlines()}
units={};own_units=defaultdict(set)
for line in Path('bench/runs/brreg-index-replay-20261120-new/envelopes.jsonl').open(encoding='utf-8'):
    r=json.loads(line);org=r['organisation_number']
    for c in r['claims']:
        if c['field'].startswith('subunits.unit.') and c['availability']=='available':
            number=c['value']['organisation_number'];units[number]=org;own_units[org].add(number)
recipient=set();specified=set();unit_only=set();eligible=set();n=0;matched=Counter();instruments=Counter();statuses=Counter()
with p.open(encoding='utf-16-le',newline='') as f:
    reader=csv.DictReader(f,delimiter=';',strict=True)
    for row in reader:
        n+=1
        if None in row or any(v is None for v in row.values()):raise ValueError('Incomplete CSV')
        party=row['Organisasjonsnummer st\u00f8ttemottaker'];sub=row['Organisasjonsnummer spesifisert st\u00f8ttemottaker'];status=row['Status'];statuses[status]+=1
        if party in wanted:
            recipient.add(party);matched[party]+=1
            if status=='Registrert':eligible.add(party);instruments[row['St\u00f8tteinstrument']]+=1
        if sub in wanted:specified.add(sub)
        if party in units and units[party] not in recipient:unit_only.add(units[party])
unit_only-=recipient
summary={'stage':'Census before state-aid publication','dataset_rows':n,'status_counts':dict(statuses),'exact_recipient_companies':len(recipient),
    'registered_exact_recipient_companies':len(eligible),'specified_subunit_numbers_matching_cohort_directly':len(specified),'additional_parent_companies_via_registered_recipient_subunits':len(unit_only),
    'exact_recipient_records':sum(matched.values()),'matched_instruments':dict(instruments),'recipient_orgnrs':sorted(recipient),'source':metadata}
(Path(__file__).parent/'recipient-census.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k not in ['recipient_orgnrs','source']},indent=2))
