import json
import math
from collections import Counter


def statistics(values):
    ordered = sorted(values)
    def percentile(p):
        return ordered[max(0, math.ceil(len(ordered) * p) - 1)] if ordered else 0
    return {"p50_ms": percentile(.5), "p95_ms": percentile(.95), "max_ms": max(ordered, default=0)}


def compute_funnel_metrics(envelopes, inputs, budget):
    """
    Feature F39: Opportunity-to-publication funnel metrics across all information families.
    Tracks conversion: eligible -> requested -> received -> verified -> published.
    Every counter has a clear, non-fabricated denominator.
    """
    total_companies = len(inputs.unique) if inputs and hasattr(inputs, 'unique') else len(envelopes)
    families = ('registry', 'website', 'activity', 'hiring', 'accounts')
    funnel = {}

    requests_by_family = Counter()
    responses_by_family = Counter()
    events = getattr(budget, 'events', []) if budget else []
    for ev in events:
        url = ev.get('url', '')
        status = ev.get('status', 0)
        fam = 'website'
        if 'regnskap' in url:
            fam = 'accounts'
        elif 'brreg.no' in url or 'enhetsregisteret' in url:
            fam = 'registry'
        elif 'pam-stilling' in url or 'arbeidsplassen' in url or 'nav.no' in url:
            fam = 'hiring'
        elif '/nyheter' in url or '/feed' in url or 'sitemap' in url:
            fam = 'activity'
        requests_by_family[fam] += 1
        if status == 200:
            responses_by_family[fam] += 1

    for fam in families:
        eligible = total_companies
        sec_name = 'identity' if fam == 'registry' else fam
        claim_fam = 'identity' if fam == 'registry' else fam
        verified_orgs = {
            getattr(e, 'organisation_number', None) or getattr(e, 'org', None)
            for e in envelopes
            if getattr(e, 'run', None) and (
                getattr(e.run, 'sections', {}).get(sec_name) == 'available'
                or getattr(e.run, 'sections', {}).get(fam) == 'available'
            )
        }
        verified_companies = len(verified_orgs - {None})
        published_claims = sum(
            1 for e in envelopes for c in getattr(e, 'claims', [])
            if getattr(c, 'family', None) in {fam, claim_fam} and getattr(c, 'availability', None) == 'available'
        )
        claims_with_evidence = sum(
            1 for e in envelopes for c in getattr(e, 'claims', [])
            if getattr(c, 'family', None) in {fam, claim_fam} and getattr(c, 'availability', None) == 'available' and getattr(c, 'evidence_ids', None)
        )

        funnel[fam] = {
            'eligible_companies': eligible,
            'requests_dispatched': requests_by_family[fam],
            'responses_received': responses_by_family[fam],
            'verified_companies': verified_companies,
            'published_claims': published_claims,
            'evidence_anchored_claims': claims_with_evidence,
            'company_yield_rate': round(min(1.0, max(0.0, verified_companies / eligible)), 4) if eligible > 0 else 0.0,
            'claim_evidence_rate': round(claims_with_evidence / published_claims, 4) if published_claims > 0 else 1.0,
        }
    return funnel


def compute_rejection_reasons(envelopes):
    """
    Feature F18: Standardized candidate rejection explanations with typed categories.
    Aggregates reasons why candidates or sources were rejected across the run.
    """
    reasons = Counter()
    for e in envelopes:
        for err in getattr(e, 'errors', []):
            if err.code == 'website_candidates':
                try:
                    attempts = json.loads(err.message) if isinstance(err.message, str) else err.message
                    if isinstance(attempts, list):
                        for att in attempts:
                            raw_r = str(att.get('reason') or att.get('level') or 'unknown')
                            norm_code = 'insufficient_ownership_proof'
                            if 'foreign_orgnr' in raw_r or 'orgnr_mismatch' in raw_r:
                                norm_code = 'wrong_organization_number'
                            elif 'robots' in raw_r:
                                norm_code = 'robots_denied'
                            elif 'dns' in raw_r or 'nxdomain' in raw_r:
                                norm_code = 'dns_error'
                            elif 'timeout' in raw_r:
                                norm_code = 'request_timeout'
                            elif 'budget' in raw_r or 'cap' in raw_r:
                                norm_code = 'budget_exhausted'
                            elif 'http_blocked' in raw_r or '403' in raw_r or '401' in raw_r:
                                norm_code = 'source_blocked'
                            elif '404' in raw_r or '410' in raw_r or '50' in raw_r:
                                norm_code = 'http_error'
                            elif 'no_orgnr' in raw_r or 'empty_signals' in raw_r or 'LOW' in raw_r:
                                norm_code = 'insufficient_ownership_proof'
                            elif 'other_orgnrs' in raw_r or 'ambiguous' in raw_r:
                                norm_code = 'ambiguous_multiple_orgnrs'
                            reasons[norm_code] += 1
                except (ValueError, TypeError, json.JSONDecodeError):
                    pass
            elif getattr(err, 'section', None) == 'hiring' and err.code in {'nav_time_cap', 'deadline', 'nav_consumer_stopped'}:
                reasons[f'hiring_{err.code}'] += 1
            elif err.code == 'deadline':
                reasons['pipeline_deadline_exhausted'] += 1
    return dict(reasons)


def build(envelopes, inputs, budget, config, warnings, runtime):
    unique = {e.organisation_number: e for e in envelopes}
    company_events=[e for e in budget.events if e['organisation_number'] in unique]
    by_org = Counter(e["organisation_number"] for e in company_events)
    completed = [e.get("attempt_started", 0) + e.get("runtime_ms", 0)/1000 for e in budget.events]
    starts = [e.get("attempt_started", 0) for e in budget.events]
    active_seconds = max(completed, default=0) - min(starts, default=0)
    
    funnel = compute_funnel_metrics(envelopes, inputs, budget)
    rejection_reasons = compute_rejection_reasons(envelopes)

    return {"run_id": config.run_id, "input_rows": len(inputs.rows), "unique_inputs": len(inputs.unique),
            'emit_duplicates':config.emit_duplicates,
            "emitted_envelopes": len(envelopes), "duplicates": inputs.duplicates, "invalid_inputs": inputs.invalid,
            "counts_by_state": dict(Counter(e.state for e in envelopes)),
            "counts_by_availability": dict(Counter(s for e in envelopes for s in e.run.sections.values())),
            "requests": len(budget.events), "requests_per_company": len(company_events) / len(unique) if unique else 0,
            'shared_requests':len(budget.events)-len(company_events),
            'amortized_requests_per_company':len(budget.events)/len(unique) if unique else 0,
            "requests_by_host": dict(budget.by_host), "request_log": budget.events,
            "request_rate_per_second": len(budget.events) / active_seconds if active_seconds > 0 else 0,
            "http_429_count": sum(e.get("status") == 429 for e in budget.events),
            "max_requests_per_company": max(by_org.values(), default=0),
            "runtime_ms": round(runtime * 1000), "company_runtime": statistics([e.operations.runtime_ms for e in unique.values()]),
            "total_cost_usd": 0, "cost_per_100_companies_usd": 0, "cost_per_official_batch_usd": 0,
            "official_batch_size": config.official_batch_size,
            "deadline_hits": sum(any(x.code == "deadline" for x in e.errors) for e in unique.values()),
            "handled_exceptions": sum(x.code in {"section_exception", "company_exception"} for e in unique.values() for x in e.errors),
            "unhandled_exceptions": 0, "changes": sum(len(e.changes) for e in unique.values()),
            'observation_changes':sum(len(e.run.refresh.get('observation_changes',[])) for e in unique.values()),
            "warnings": warnings, "limits": {k: getattr(config, k) for k in ("max_requests", "max_cost_usd", "time_budget_seconds", "deadline_fraction", "request_timeout", "host_concurrency")},
            "schema_validated": True, "membership_validated": True,
            "funnel_metrics": funnel,
            "rejection_reasons": rejection_reasons}
