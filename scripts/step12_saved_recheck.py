"""Recheck changed generic proof guards against captured pages, never crawl."""
import json
from pathlib import Path
from types import SimpleNamespace
from signalpost.models.envelope import Envelope
from signalpost.models.shapes import serialize
from signalpost.config import Config
from signalpost.runner import update
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.sources.extract import Section
from signalpost.web.collector import candidate_proof,publish_result
from signalpost.web.candidates import Candidate
from signalpost.web.round2 import registered_leaders
from signalpost.web.html import Page
from signalpost.web.policy import domain
from signalpost.web.entity_scope import enforce
from signalpost.synthesis.template import generate
from signalpost.profiles import write as write_profiles

RUN=Path('bench/runs/20261106T102032689035Z-f774483')
BASE=Path('bench/cache/s6-step11-kept')
OUT=Path('bench/cache/s6-step12-cleanup-step11-recheck')


def main():
    OUT.mkdir(exist_ok=True)
    rows=[Envelope.model_validate(json.loads(line)) for line in (BASE/'envelopes.jsonl').open(encoding='utf8')]
    before={r.organisation_number:{c.id for c in r.claims if c.availability=='available'} for r in rows}
    report=json.loads((RUN/'report.json').read_text(encoding='utf8'))
    config=Config(organisations=RUN/'inputs/batch.jsonl',output=OUT/'envelopes.jsonl',report=OUT/'report.json',websites=True)
    blobs=BlobStore(RUN/'state');events={}
    for e in report['request_log']:
        if e.get('section')=='website' and e.get('status')==200 and e.get('content_sha256') and '/robots.txt' not in e['url']:
            events.setdefault(e['organisation_number'],[]).append(e)
    assessments=[];baseline_checks=[];missing_baseline=set()
    for row in rows:
        original=next((c for c in row.claims if c.field=='official_website' and c.availability=='available'),None)
        if original:
            values={c.field:c.value for c in row.claims if c.availability=='available'}
            context={'name':values.get('identity.legal_name'),'allowed_orgnrs':{row.organisation_number}}
            evidence={e.id:e for e in row.evidence}
            from signalpost.web.round2 import real_page
            from signalpost.web.names import proof_context
            for ref in original.evidence_ids:
                e=evidence[ref]
                if e.source_class!='company_owned':continue
                if not (blobs.directory/e.content_sha256).exists():
                    missing_baseline.add(row.organisation_number)
                    baseline_checks.append({'organisation_number':row.organisation_number,'url':e.source_url,'sha256':e.content_sha256,'new_common_guard_veto':None,'body_missing':True,'assessment':'historical claim preserved unchanged; not revalidated'})
                    continue
                p=Page((blobs.directory/e.content_sha256).read_bytes(),e.source_url)
                veto=real_page(p,proof_context(p,row.organisation_number,context))
                baseline_checks.append({'organisation_number':row.organisation_number,'url':e.source_url,'sha256':e.content_sha256,'new_common_guard_veto':veto})
            continue
        diagnostics=[]
        for error in row.errors:
            if error.code=='website_candidates':diagnostics+=json.loads(error.message)
        rejected=[d for d in diagnostics if d.get('reason')=='different_legal_entity' and d.get('level')=='REJECT']
        if not rejected:continue
        values={c.field:c.value for c in row.claims if c.availability=='available'};a=values.get('identity.registered_address') or {}
        context={'name':values.get('identity.legal_name'),'street':a.get('adresse'),'postcode':a.get('postnummer'),'city':a.get('poststed'),'municipality':a.get('kommune'),
            'email':values.get('identity.registered_email'),'phone':values.get('identity.registered_phone'),'nace':(values.get('identity.nace1') or {}).get('kode'),
            'subunits':[{'orgnr':c.value['organisation_number'],**c.value} for c in row.claims if c.field.startswith('subunits.unit.') and c.availability=='available']}
        choices=[]
        for d in {d['domain']:d for d in rejected}.values():
            pages=[];best=None;veto=False;seen=set();candidate=Candidate('https://'+d['domain'],d['domain'],d['origin'])
            for e in events.get(row.organisation_number,[]):
                if domain(e['url'])!=d['domain'] or e['content_sha256'] in seen:continue
                body=(blobs.directory/e['content_sha256']).read_bytes()
                if not body.lstrip().startswith((b'<!',b'<html',b'<HTML',b'<head',b'<title',b'\xef\xbb\xbf')):continue
                seen.add(e['content_sha256']);p=Page(body,e['url'])
                if '<urlset' in p.raw[:1000] or '<rss' in p.raw[:1000]:continue
                response=Response(body,200,e['url'],row.run.started_at if hasattr(row.run,'started_at') else '2026-11-06T10:20:32Z',e['content_sha256'])
                existing=next((ref for ref in row.evidence if ref.content_sha256==response.sha),None)
                if existing:response.retrieved_at=existing.retrieved_at
                proof=candidate_proof(p,row.organisation_number,context,candidate,registered_leaders(row.claims),config)
                pages.append((response,p))
                if proof.level=='REJECT':veto=True
                if proof.level=='VERIFIED' and best is None:best=(proof,response,p)
            if best and not veto:choices.append((candidate,*best,pages))
        assessment={'organisation_number':row.organisation_number,'company':context['name'],'changed_guards_rechecked':len(rejected),'verified_hosts':len(choices)}
        if len(choices)==1:
            section=publish_result(row.organisation_number,row,SimpleNamespace(accepted_pages={},attempts={}),Section(),choices,diagnostics,context)
            if any(c.field=='official_website' for c in section.claims):
                # This is an incremental same-snapshot projection. The real
                # runner emits Wikidata after website collection; invoking the
                # collector helper alone must not erase those existing claims.
                prior={c.field:c for c in row.claims if c.family=='website' and c.availability=='available'}
                section.claims=[c for c in section.claims if c.field not in prior]+list(prior.values())
                update(row,'website',section);assessment['recovered_website']=next(c.value for c in section.claims if c.field=='official_website')
        assessments.append(assessment)
    # A missing historical body is not evidence of a company changing. Preserve
    # that pre-existing row, disclose it, and do not pretend it was revalidated.
    enforce([r for r in rows if r.organisation_number not in missing_baseline],blobs,SimpleNamespace(domain_owners={}))
    lost=[{'organisation_number':r.organisation_number,'claim_ids':sorted(before[r.organisation_number]-{c.id for c in r.claims if c.availability=='available'})} for r in rows
          if before[r.organisation_number]-{c.id for c in r.claims if c.availability=='available'}]
    for row in rows:
        row.run.synthesis=generate(row);row.profile.synthesis=row.run.synthesis
    with (OUT/'envelopes.jsonl').open('w',encoding='utf8') as handle:
        for row in rows:handle.write(json.dumps(serialize(row,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
    write_profiles(OUT/'profiles.jsonl',rows)
    Path('bench/reports/s6-step12/cleanup-saved-step11-recheck.json').write_text(json.dumps({'method':'generic veto recheck on reviewed Step 11 envelopes and captured Step 11 pages only; no HTTP, no replacement candidates, no new timing measurement','lost_published_claims':lost,'baseline_website_guards':baseline_checks,'assessments':assessments},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    assert not lost, lost
    assert not any(r['new_common_guard_veto'] for r in baseline_checks),[r for r in baseline_checks if r['new_common_guard_veto']]
    print([a for a in assessments if 'recovered_website' in a],flush=True)


if __name__=='__main__':main()
