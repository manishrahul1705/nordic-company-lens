from ..models.claim import Claim
from ..models.evidence import Evidence, canonical, utc_now
from ..models.envelope import Change

CHECKED={'available','not_available','not_applicable'}
TRANSIENT_FAILURES={'website_timeout','website_connect_error','website_tls_error','dns_timeout','dns_servfail','dns_error','dns_unavailable','no_such_domain','timeout','network_error','connection_reset','connection_refused'}


def transient_sections(envelope, old_claims):
    """Read transport diagnostics without treating HTTP/ownership proof as a timeout."""
    import json
    from ..web.policy import domain
    reasons = {}
    attempts = []
    for error in envelope.errors:
        if error.section == 'activity' and error.code in {'registry_change_http_429', 'registry_change_http_500', 'registry_change_http_502', 'registry_change_http_503', 'registry_change_http_504'}:
            reasons.setdefault('activity', set()).add(error.code)
        if error.code in TRANSIENT_FAILURES:
            reasons.setdefault(error.section, set()).add(error.code)
        if error.section == 'website' and error.code == 'website_candidates':
            try:
                records = json.loads(error.message)
            except (ValueError, TypeError):
                continue
            if isinstance(records, list):
                attempts.extend(r for r in records if isinstance(r, dict))
    for attempt in attempts:
        if attempt.get('reason') in TRANSIENT_FAILURES:
            reasons.setdefault('website', set()).add(attempt['reason'])
    old_site = old_claims.get('official_website')
    old_domain = domain(old_site.value['final_url']) if old_site and old_site.availability == 'available' else None
    gone = any(a.get('reason') in {'http_404', 'http_410', 'gone'} and
               old_domain is not None and domain(a.get('page') or a.get('url') or a.get('domain', '')) == old_domain and
               not str(a.get('page') or a.get('url', '')).endswith('/robots.txt') for a in attempts)
    refuted = envelope.run.refresh.get('website', {}).get('refuted_previous_website')
    if gone or refuted or any(e.section == 'website' and e.code == 'foreign_orgnr_on_previous_domain' for e in envelope.errors):
        reasons.pop('website', None)
    if 'website' in reasons and any(e.section == 'activity' and e.code == 'website_check_incomplete' for e in envelope.errors):
        reasons.setdefault('activity', set()).update(reasons['website'])
    return reasons

def newly_supported_field(field):
    from ..sources.registry_fields import EXTRA,GROUPS
    from ..sources.fact_depth import IDENTITY_EXTRA
    from ..sources.regnskap import PATHS
    legacy={'revenue','operating_result','result_before_tax','net_result','equity','total_assets','total_liabilities'}
    return (field.startswith(('roles.detail.','subunits.detail.','accounts.history.','accounts.statement.','accounts.additional.','accounts.consolidated.','identity.historical_name.')) or
            field in {'identity.'+k for k in (*EXTRA,*GROUPS,*IDENTITY_EXTRA,'employee_count_disclosure','founding_date','vat_registration_date')} or
            field in {'accounts.'+k for k in PATHS.keys()-legacy})


def meaning(claim):
    if claim is None or claim.availability!='available': return None
    if claim.field=='official_website':
        from ..web.policy import domain
        # Proof strength/location and www/HTTPS variants describe observation,
        # rather than a move to another company website domain.
        return domain(claim.value['final_url'])
    if claim.field.startswith('website_description.'):
        return canonical({k:v for k,v in claim.value.items() if k not in {'identity_level','identity_claim_id'}})
    if claim.family=='accounts' and claim.reporting_period:
        period=claim.reporting_period
        return {'value':canonical(claim.value),'period':{k:period.get(k) for k in ('fiscal_year','period_start','period_end','currency','account_type')},
                'source_unit':period.get('source_unit',period.get('unit'))}
    return canonical(claim.value)


def apply(envelope, previous, blobs):
    envelope.run.refresh = {**envelope.run.refresh,"mode": "baseline" if previous is None else "refresh", "previous_run_id": None,'observation_changes':[]}
    if previous is None:
        envelope.run.refresh['observed_claim_ids'] = sorted(c.id for c in envelope.claims if c.availability == 'available')
        return
    old = previous.get("profile", previous) if "claims" not in previous else previous
    old_claims = {x["field"]: Claim.model_validate(x) for x in old.get("claims", [])}
    previous_refresh = previous.get('run', {}).get('refresh', old.get('refresh', {}))
    known_ids = set(previous_refresh.get('observed_claim_ids', []))
    known_ids.update(c.id for c in old_claims.values() if c.availability == 'available')
    envelope.run.refresh['observed_claim_ids'] = sorted(known_ids | {
        c.id for c in envelope.claims if c.availability == 'available'})
    old_evidence = {x["id"]: Evidence.model_validate(x) for x in old.get("evidence", [])}
    for item in old_evidence.values():
        if item.snapshot_body_base64:
            import base64
            from ..sources.excerpt import excerpt
            item.claim_span = excerpt(base64.b64decode(item.snapshot_body_base64), locator=item.locator)
            item.snapshot_body_base64 = None
    new_evidence = {x.id: x for x in envelope.evidence}
    envelope.run.refresh["previous_run_id"] = previous.get("run_id", previous.get("run", {}).get("run_id"))
    envelope.run.refresh["mode"] = "refresh"
    envelope.run.refresh['previous_completed_at'] = previous.get('run', {}).get('completed_at', previous.get('completed_at'))
    old_sections=previous.get('run',{}).get('sections',old.get('sections',{}))
    identity_conflict = any(e.section == 'identity' and e.code == 'wrong_company' for e in envelope.errors)
    transient_reasons = transient_sections(envelope, old_claims)
    restored = set()
    envelope.run.refresh['stale_sections'] = {}
    for family, reasons in transient_reasons.items():
        before = old_sections.get(family)
        attempted = envelope.run.sections.get(family)
        if identity_conflict or before not in {'available', 'not_available', 'ambiguous'} or attempted not in {'failed', 'blocked'}:
            continue
        if before == 'available' and not any(c.family == family and c.availability == 'available' for c in old_claims.values()):
            continue  # Strict identity validation may deliberately remove prior claims.
        restored.add(family)
        envelope.run.refresh['stale_sections'][family] = {
            'previous_state': before, 'attempt_state': attempted,
            'failed_attempt_at': envelope.run.completed_at, 'failure_codes': sorted(reasons),
            'attempt_refresh': envelope.run.refresh.get(family, {})}
        envelope.run.sections[family] = before
        envelope.claims = [c for c in envelope.claims if c.family != family] + [
            c.model_copy(update={'carried_forward': True, 'stale_since': envelope.run.completed_at})
            for c in old_claims.values() if c.family == family]
        if family in previous_refresh:
            import copy
            envelope.run.refresh[family] = copy.deepcopy(previous_refresh[family])
    envelope.run.refresh['observed_claim_ids'] = sorted(known_ids | {
        c.id for c in envelope.claims if c.availability == 'available'})
    failed = {family for family,state in envelope.run.sections.items() if state not in CHECKED or old_sections.get(family) not in CHECKED}
    transient_failed = restored | {family for family in transient_reasons
                                   if envelope.run.sections.get(family) in {'failed', 'blocked'}}
    failed |= transient_failed
    for family in failed:
        before=old_sections.get(family); after=envelope.run.sections.get(family)
        old_values=canonical([c.value for c in old_claims.values() if c.family==family and c.availability=='available'])
        new_values=canonical([c.value for c in envelope.claims if c.family==family and c.availability=='available'])
        if (before!=after or old_values!=new_values) and family not in transient_failed:
            reasons=sorted({e.code for e in envelope.errors if e.section==family})
            envelope.run.refresh['observation_changes'].append({'section':family,'previous_state':before,'current_state':after,'reason':','.join(reasons) or 'section_not_successfully_checked_in_both_runs'})
    for family in failed:
        if family in restored:
            continue
        if identity_conflict or (family == 'identity' and any(e.section == 'identity' and e.code == 'wrong_company' for e in envelope.errors)):
            continue
        available = {c.field: c for c in envelope.claims if c.family == family and c.availability == "available"}
        for claim in old_claims.values():
            if claim.family == family and claim.availability == "available":
                if family=='hiring':
                    from ..sources.nav import timestamp
                    from datetime import datetime,timezone
                    if claim.field.startswith('hiring.site_job.'):
                        from ..web.jobs import job_date
                        expires=job_date(claim.value.get('expires'), expiry=True)
                    else:
                        expires=timestamp(claim.value.get('expires'))
                    if expires is None or expires<=datetime.now(timezone.utc) or claim.value.get('uuid') in envelope.run.refresh.get('hiring',{}).get('known_closed_jobs',[]):
                        continue
                    if envelope.run.refresh.get('hiring',{}).get('closure_requires_live_detail'):
                        continue  # Current-run live proof is mandatory for every ad.
                if family == 'website' and envelope.run.refresh.get('website', {}).get('refuted_previous_website'):
                    continue  # Do not carry forward a discredited website that was refuted with foreign orgnr.
                carried = claim.model_copy(update={"carried_forward": True,
                    "stale_since": envelope.run.completed_at if family in transient_failed else claim.stale_since})
                available.setdefault(carried.field,carried)
        retained = list(available.values())
        if retained:
            envelope.claims = [c for c in envelope.claims if c.family != family] + retained
    new_claims = {c.field: c for c in envelope.claims}
    # A rolling annual-response window does not withdraw an older supported statement.
    # Retain only dated historical facts, with their original values and evidence;
    # current-period values still replace them normally when actually returned.
    if 'accounts' not in failed and not identity_conflict:
        returned={(c.reporting_period.get('account_type'),c.reporting_period.get('fiscal_year'))
                  for c in envelope.claims if c.family=='accounts' and c.availability=='available' and c.reporting_period}
        for field,c in old_claims.items():
            if field in new_claims or c.availability!='available' or not field.startswith(('accounts.statement.','accounts.additional.','accounts.consolidated.','accounts.history.')):continue
            period=c.reporting_period or {};scope=(period.get('account_type'),period.get('fiscal_year'))
            if not scope[1] or scope in returned or not any(kind==scope[0] for kind,year in returned):continue
            carried=c.model_copy(update={'carried_forward':True,'reasons':{**c.reasons,'history':'Previously supported period outside current response window; original evidence retained'}})
            envelope.claims.append(carried);new_claims[field]=carried
    for scoped_family in ('website','activity'):
        if scoped_family in restored:continue
        checked_urls = envelope.run.refresh.get(scoped_family, {}).get('checked_urls')
        if checked_urls is None or envelope.run.sections.get(scoped_family) not in {'available','not_available'}:continue
        for field, claim in old_claims.items():
            if claim.family != scoped_family or claim.availability != 'available' or field in new_claims or field == 'official_website': continue
            source_urls = {old_evidence[eid].source_url for eid in claim.evidence_ids if old_evidence[eid].source_class == 'company_owned'}
            if source_urls and not source_urls <= set(checked_urls):
                carried = claim.model_copy(update={'carried_forward': True})
                envelope.claims.append(carried);new_claims[field]=carried
                envelope.run.refresh['observation_changes'].append({'section':scoped_family,'field':field,
                    'previous_state':'available','current_state':'unchecked_page','reason':'supporting_'+scoped_family+'_page_not_checked'})
    for field in sorted(set(old_claims) | set(new_claims)):
        before, after = old_claims.get(field), new_claims.get(field)
        family = (after or before).family
        if family not in envelope.run.sections or family in failed:
            continue
        if family=='hiring' and before and before.availability=='available' and meaning(after) is None:
            hiring=envelope.run.refresh.get('hiring',{})
            if hiring.get('closure_requires_live_detail') and before.value.get('uuid') not in hiring.get('known_closed_jobs',[]):
                envelope.run.refresh['observation_changes'].append({'section':'hiring','field':field,
                    'previous_state':'available','current_state':'closure_not_verified','reason':'live_detail_did_not_prove_inactive_or_expired'})
                continue
        if before is None and newly_supported_field(field):
            envelope.run.refresh['observation_changes'].append({'section': family, 'field': field,
                'previous_state': 'unchecked_field', 'current_state': after.availability,
                'reason': 'dated_field_not_checked_in_previous_extractor'})
            continue
        if family == "roles":
            if before and after:
                after.first_observed_at = before.first_observed_at
            continue
        if before and after:
            after.first_observed_at = before.first_observed_at
            # Source retrieval time/hash/locator ordering is not material content.
            if meaning(before) == meaning(after):
                continue
        if meaning(before)==meaning(after): continue
        if after and after.availability == 'available' and after.id in known_ids and meaning(before) is None:
            envelope.run.refresh['observation_changes'].append({
                'section': family, 'field': field, 'claim_id': after.id,
                'previous_state': before.availability if before else 'not_observed',
                'current_state': 'available', 'reason': 'previously_observed_claim_recovered'})
            continue
        if before is None and after and family in {'website', 'activity'} and after.availability == 'available':
            checked_before = previous_refresh.get(family, {}).get('checked_urls')
            source_urls = {new_evidence[eid].source_url for eid in after.evidence_ids
                           if eid in new_evidence and new_evidence[eid].source_class == 'company_owned'}
            old_site = old_claims.get('official_website')
            new_site = new_claims.get('official_website')
            same_site = meaning(old_site) is not None and meaning(old_site) == meaning(new_site)
            if same_site and checked_before is not None and source_urls and not source_urls <= set(checked_before):
                envelope.run.refresh['observation_changes'].append({
                    'section': family, 'field': field, 'claim_id': after.id,
                    'previous_state': 'unchecked_page', 'current_state': 'available',
                    'reason': 'newly_checked_supporting_page'})
                continue
        if before is None and after and after.availability != "available":
            continue
        if after is None and before and before.availability != "available":
            continue
        old_ids = before.evidence_ids if before else []
        new_ids = after.evidence_ids if after else []
        if family=='hiring' and before and meaning(after) is None:
            new_ids=envelope.run.refresh.get('hiring',{}).get('closure_evidence',{}).get(before.value.get('uuid'),new_ids)
        newest = new_evidence.get(new_ids[0]) if new_ids else None
        oldest = old_evidence.get(old_ids[0]) if old_ids else None
        envelope.changes.append(Change(
            organisation_number=envelope.organisation_number, type="closed_job" if family=='hiring' and meaning(before) is not None and meaning(after) is None else "added" if meaning(before) is None else "removed" if meaning(after) is None else "changed",
            field=field, old_value=before.value if before else None, new_value=after.value if after else None,
            old_evidence_ids=old_ids, new_evidence_ids=new_ids,
            materiality="minor" if field == "identity.registered_website" or family=='activity' else "material",
            first_observed_at=(before or after).first_observed_at, last_observed_at=utc_now(),
            source_url=newest.source_url if newest else None, retrieved_at=newest.retrieved_at if newest else None,
            effective_at=newest.effective_at if newest else None, source_class=newest.source_class if newest else None,
            old_locator=oldest.locator if oldest else None, new_locator=newest.locator if newest else None,
            old_content_sha256=oldest.content_sha256 if oldest else None, new_content_sha256=newest.content_sha256 if newest else None,
            status=after.availability if after else "not_available"))
    if "roles" not in failed:
        before_roles = [c for c in old_claims.values() if c.field.startswith('roles.role.') and c.availability == "available"]
        after_roles = [c for c in new_claims.values() if c.field.startswith('roles.role.') and c.availability == "available"]
        before_values = [c.value for c in before_roles]
        after_values = [c.value for c in after_roles]
        if canonical(before_values) != canonical(after_values):
            old_ids = list(dict.fromkeys(ref for c in before_roles for ref in c.evidence_ids))
            new_ids = list(dict.fromkeys(ref for c in after_roles for ref in c.evidence_ids))
            oldest = old_evidence.get(old_ids[0]) if old_ids else None
            newest = new_evidence.get(new_ids[0]) if new_ids else None
            envelope.changes.append(Change(organisation_number=envelope.organisation_number, type="changed", field="roles.roles",
                                           old_value=before_values or None, new_value=after_values or None,
                                           old_evidence_ids=old_ids, new_evidence_ids=new_ids, materiality="material",
                                           first_observed_at=(before_roles or after_roles)[0].first_observed_at, last_observed_at=utc_now(),
                                           source_url=newest.source_url if newest else None, retrieved_at=newest.retrieved_at if newest else None,
                                           effective_at=newest.effective_at if newest else None, source_class=newest.source_class if newest else None,
                                           old_locator=oldest.locator if oldest else None, new_locator=newest.locator if newest else None,
                                           old_content_sha256=oldest.content_sha256 if oldest else None, new_content_sha256=newest.content_sha256 if newest else None,
                                           status="available" if after_roles else "not_available"))
    # Preserve prior source metadata even when the current source changes;
    # a fresh state directory needs no historical blobs or refetch.
    for evid in old_evidence.values():
        new_evidence.setdefault(evid.id, evid)
    envelope.evidence = list(new_evidence.values())
