"""Independent saved-output checks; never rewrites an envelope to pass a gate."""
import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from signalpost.models.shapes import validate
from signalpost.io.input_adapter import read
from signalpost.models.claim import Claim
from signalpost.models.evidence import Evidence
from signalpost.models.envelope import Change
from signalpost.models.synthesis import Synthesis
from signalpost.synthesis.validate import sentence_error,SECTIONS
from signalpost.synthesis.catalog import change_claims
from types import SimpleNamespace
from signalpost.sources.text import decode_body


def verify_synthesis(row):
    data=row if 'claims' in row else row['profile']
    raw=row['run'].get('synthesis') if 'run' in row else row['profile'].get('synthesis')
    if raw is None:return 0,0
    synthesis=Synthesis.model_validate(raw)
    from signalpost.models.envelope import Error
    envelope=SimpleNamespace(organisation_number=row['organisation_number'], claims=[Claim.model_validate(c) for c in data['claims']],
        errors=[Error.model_validate(e) for e in data.get('errors', [])],
        evidence=[Evidence.model_validate(e) for e in data['evidence']],changes=[Change.model_validate(c) for c in data['changes']],
        run=SimpleNamespace(refresh=row['run']['refresh'] if 'run' in row else data['refresh'],
                            sections=row['run']['sections'] if 'run' in row else data['sections'],
                            completed_at=row['run']['completed_at'] if 'run' in row else row['completed_at']))
    sentences=[s for key in SECTIONS for s in getattr(synthesis.sections,key)]
    assert all(sentence_error(s,envelope) is None for s in sentences),'Unverified synthesis sentence'
    if synthesis.brief is not None:
        from signalpost.synthesis.company_brief import validate as validate_brief
        validate_brief(synthesis.brief, synthesis, envelope)
    primary=sentences
    if synthesis.generator.version in {'5','6'}:
        assert synthesis.analyst_brief is not None,'Missing analyst brief'
    if synthesis.analyst_brief is not None:
        from signalpost.synthesis.analyst import validate as validate_analyst
        validate_analyst(synthesis.analyst_brief,envelope)
        primary=synthesis.analyst_brief.sentences
    assert synthesis.summary==' '.join(s.text for s in primary),'Summary differs from checked sentences'
    assert synthesis.checks.sentences==synthesis.checks.cited==len(sentences) and synthesis.checks.values_verified
    assert synthesis.change_claims==change_claims(envelope),'Change citations differ from source events'
    if 'run' in row and 'profile' in row:assert row['profile'].get('synthesis')==raw,'Synthesis mirror differs'
    return 1,len(primary)


def load(path):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").split("\n") if line.strip()]
    for row in rows:
        shape = "union" if "profile" in row and "claims" in row else "reference" if "profile" in row else "contract"
        validate(row, shape)
    return rows


def ids(rows):
    return {r["organisation_number"]: sorted(c["id"] for c in (r if "claims" in r else r["profile"])["claims"]) for r in rows}


def section_summary(rows):
    """Report optional-source problems honestly, including preserved stale states."""
    issues=[]
    for row in rows:
        data=row if 'claims' in row else row['profile']
        sections=row['run']['sections'] if 'run' in row else data['sections']
        refresh=row['run']['refresh'] if 'run' in row else data['refresh']
        stale=refresh.get('stale_sections',{})
        for family,state in sections.items():
            if state not in {'failed','blocked'} and family not in stale:continue
            reasons=[]
            for e in data.get('errors',[]):
                if e['section']!=family:continue
                if e['code']=='website_candidates':
                    try:
                        codes=sorted({d['reason'] for d in json.loads(e['message']) if d.get('reason')})
                        reasons.append({'code':e['code'],'candidate_failure_reasons':codes})
                        continue
                    except (TypeError,ValueError):pass
                reasons.append({'code':e['code'],'message':e['message'][:240]})
            issues.append({'organisation_number':row['organisation_number'],'section':family,'state':state,
                           'stale':stale.get(family),'reasons':reasons})
    return issues


def verify(first, state_dir, count, organisations=None, report=None, require_clean=False, second=None, clean_sections=None):
    rows = load(first)
    assert len(rows) == count, f"Expected {count}, got {len(rows)}"
    repeated={}
    for row in rows:
        org=row['organisation_number']
        if org in repeated:assert row==repeated[org], 'Duplicate input rows have inconsistent envelopes'
        repeated[org]=row
    if organisations is not None:
        inputs=read(organisations)
        expected=inputs.rows
        if report is not None and json.loads(report.read_text(encoding='utf8')).get('emit_duplicates') is False:
            expected=inputs.unique
        assert [r['organisation_number'] for r in rows] == expected, 'Membership/order differs from input'
    seen, published = set(), 0
    @lru_cache(maxsize=8)
    def stored_body(sha):
        return decode_body((state_dir/'blobs'/sha).read_bytes())
    synthesis_companies=synthesis_sentences=0
    for row in rows:
        companies,sentences=verify_synthesis(row)
        synthesis_companies+=companies;synthesis_sentences+=sentences
        data = row if "claims" in row else row["profile"]
        evidence = {e["id"]: e for e in data["evidence"]}
        for claim in data["claims"]:
            if claim["availability"] != "available":
                assert claim["value"] is None
                continue
            published += 1
            assert claim["evidence_ids"]
            for ref in claim["evidence_ids"]:
                e = evidence[ref]
                assert e["source_url"] and e["retrieved_at"].endswith("Z") and e["locator"] and e["extraction_method"]
                sha = e["content_sha256"]
                if sha not in seen:
                    assert hashlib.sha256((state_dir / "blobs" / sha).read_bytes()).hexdigest() == sha
                    seen.add(sha)
                body = stored_body(sha)
                assert len(e['claim_span']) <= 300 and e['claim_span'] in body, 'Non-verbatim evidence span'
    result = {"lines": len(rows), "schema_valid": True, "published_claims": published, "source_blobs_verified": len(seen)}
    result.update(synthesis_companies=synthesis_companies,synthesis_sentences=synthesis_sentences,synthesis_unverified_values=0)
    issues=section_summary(rows)
    if require_clean:result['failed_or_stale_sections']=issues
    if report is not None:
        metrics = json.loads(report.read_text(encoding='utf8'))
        assert metrics['emitted_envelopes'] == len(rows)
        assert metrics['schema_validated'] and metrics['membership_validated']
        if require_clean:
            assert metrics['input_readable'] and not metrics['invalid_inputs'] and not metrics['warnings']
            assert metrics['handled_exceptions'] == metrics['unhandled_exceptions'] == metrics['deadline_hits'] == 0
            assert not metrics['output_limit_exceeded']
            for row in rows:
                sections = row['run']['sections'] if 'run' in row else row['profile']['sections']
                selected=set(sections) if clean_sections is None else set(clean_sections)
                assert selected<=set(sections), 'Required clean sections missing from output'
                assert all(sections[family] in {'available', 'not_available', 'not_applicable', 'ambiguous'} for family in selected), 'Incomplete smoke-test section'
                refresh=row['run']['refresh'] if 'run' in row else row['profile']['refresh']
                assert not selected & set(refresh.get('stale_sections',{})), 'Stale required smoke-test section'
    if second is not None:
        rerun = load(second)
        for row in rerun:verify_synthesis(row)
        assert len(rerun) == len(rows)
        assert [r["organisation_number"] for r in rerun] == [r["organisation_number"] for r in rows]
        assert ids(rerun) == ids(rows), "Claim IDs differ"
        changes = sum(len((r if "changes" in r else r["profile"])["changes"]) for r in rerun)
        assert changes == 0, f"Changes={changes}"
        observations = sum(len((r['run']['refresh'] if 'run' in r else r['profile']['refresh']).get('observation_changes', [])) for r in rerun)
        assert observations == 0, f'Observation changes={observations}'
        result.update({'rerun_lines': len(rerun), 'identical_claim_ids': True, 'changes': changes, 'observation_changes': observations})
    return result


def main():
    parser = argparse.ArgumentParser(description='Validate membership, envelope schemas and exact stored source evidence')
    parser.add_argument('--first', type=Path, required=True)
    parser.add_argument('--second', type=Path)
    parser.add_argument('--state-dir', type=Path, required=True)
    parser.add_argument('--count', type=int, default=100)
    parser.add_argument('--organisations', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--require-clean', action='store_true')
    parser.add_argument('--clean-sections', nargs='+', choices=['identity','roles','accounts','subunits','website','hiring','activity'],
                        help='Limit --require-clean section health checks; all schema/evidence and global safety checks remain strict')
    args = parser.parse_args()
    if args.clean_sections and not args.require_clean:parser.error('--clean-sections requires --require-clean')
    print(json.dumps(verify(args.first, args.state_dir, args.count, args.organisations, args.report, args.require_clean, args.second,args.clean_sections)))


if __name__ == "__main__":
    main()
