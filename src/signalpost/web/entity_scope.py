"""Publication boundaries for shared sites and foreign legal entities."""
import re
import gzip
import json
from pathlib import Path
from urllib.parse import urlsplit
from .candidates import legal_name
from .proof import orgnrs
from .policy import domain


def foreign_entity_page(page, org, name, check_ids=True):
    """Abstain on foreign identifiers or explicit foreign legal-form names.

    A shared email domain is deliberately never an entity identity signal.
    """
    if check_ids and orgnrs(page.owner_text) - {org}:
        return True
    own = ' '.join(re.findall(r'\w+', str(name).casefold()))
    stem = legal_name(name)
    text = ' '.join((page.title, page.visible, ' '.join(str(v) for v in page.meta.values())))
    # Same brand, different legal form is the particularly dangerous AS/AB case.
    if stem:
        for match in re.finditer(r'(?<!\w)' + re.escape(stem) + r'\s+(?:AB|ASA|Ltd\.?|GmbH|Oy)\b', text, re.I):
            if ' '.join(re.findall(r'\w+', match.group().casefold())) != own:
                return True
    # Other named legal entities in page identity metadata/headings are also
    # unsafe sources of this company's descriptions and generic contacts.
    identity = ' '.join((page.title, str(page.meta.get('description', '')),
                         str(page.meta.get('og:description', ''))))
    for match in re.finditer(r'\b[A-ZÆØÅ][\wÆØÅæøå&-]*(?:\s+[A-ZÆØÅ][\wÆØÅæøå&-]*){0,5}\s+(?:AB|ASA|Ltd\.?|GmbH|Oy)\b', identity):
        if ' '.join(re.findall(r'\w+', match.group().casefold())) != own:
            return True
    return False


def enforce(envelopes, blobs, bulk):
    """Recheck final output, including carried-forward claims, without requests."""
    from .html import Page
    owners = {host: set(orgs) for host, orgs in getattr(bulk, 'domain_owners', {}).items()}
    # Historical nominations only tighten publication boundaries. They cannot
    # establish a site's ownership or change registry identity claims.
    try:
        with gzip.open(Path(__file__).resolve().parents[1] / 'data/registry_domains.json.gz', 'rt', encoding='utf8') as handle:
            nominations = json.load(handle)['domains']
    except (OSError, ValueError, KeyError):
        nominations = None  # Withhold derived site content, preserve output.
    for row in envelopes:
        for claim in row.claims:
            if claim.field == 'identity.registered_website' and claim.availability == 'available':
                host = domain(str(claim.value))
                if host:
                    owners.setdefault(host, set()).add(row.organisation_number)
    cache = {}
    for row in envelopes:
        org = row.organisation_number
        name = next((c.value for c in row.claims if c.field == 'identity.legal_name'), '')
        proof = next((c for c in row.claims if c.field == 'official_website' and c.availability == 'available'), None)
        if proof is None:
            continue
        value = proof.value
        host = domain(value.get('final_url', ''))
        nominated_others = sorted(set((nominations or {}).get(host, [])) - {org})
        group = nominations is None or value.get('relationship_note') == 'group_site' or bool(owners.get(host, set()) - {org}) or bool(nominated_others)
        evidence = {e.id: e for e in row.evidence}
        def pages(claim):
            for ref in claim.evidence_ids:
                e = evidence.get(ref)
                if not e or e.source_class != 'company_owned':
                    continue
                key = (e.content_sha256, e.source_url)
                if key not in cache:
                    try:
                        cache[key] = Page((blobs.directory / e.content_sha256).read_bytes(), e.source_url)
                    except (OSError, ValueError):
                        cache[key] = None
                if cache[key] is not None:
                    yield cache[key]
        proof_pages = list(pages(proof))
        for e in row.evidence:
            path = urlsplit(e.source_url).path.rstrip('/')
            if e.source_class != 'company_owned' or domain(e.source_url) != host:
                continue
            if path and not re.search(r'kontakt|contact|about|/om(?:-|/|$)|impressum|privacy|personvern|vilkar|faktura', path, re.I):
                continue
            key = (e.content_sha256, e.source_url)
            if key not in cache:
                try: cache[key] = Page((blobs.directory / e.content_sha256).read_bytes(), e.source_url)
                except (OSError, ValueError): cache[key] = None
            if cache[key] is not None:
                proof_pages.append(cache[key])
        group = group or any(len(orgnrs(p.visible + ' ' + json.dumps(p.jsonld))) >= 3 for p in proof_pages)
        if group:
            # Do not mutate proof.value: claim IDs hash the supported value.
            proof.reasons['relationship'] = 'group_site'
        removed = []
        for claim in row.claims:
            source_pages = None
            if group and claim.field.startswith(('social_profile.', 'registry_social.', 'website_description.', 'public_brand')):
                removed.append(claim)
            elif claim.field.startswith(('contact.', 'website_description.', 'public_brand')):
                source_pages = list(pages(claim))
                if any(foreign_entity_page(p, org, name, check_ids=not group) for p in source_pages):
                    removed.append(claim)
                elif group and claim.field.startswith('contact.'):
                    from .proof import extract_entity_cards, find_containing_card
                    scoped = False
                    for page in source_pages:
                        pos = page.raw.find(str(claim.value))
                        card = find_containing_card(extract_entity_cards(page.raw), pos) if pos >= 0 else None
                        if card and org in card.orgnrs and not (card.orgnrs - {org}):
                            scoped = True
                    if not scoped:
                        removed.append(claim)
            elif group and claim.family in {'activity', 'hiring'}:
                if any(evidence[r].source_class == 'company_owned' for r in claim.evidence_ids if r in evidence):
                    removed.append(claim)
        if not removed and not group:
            continue
        ids = {c.id for c in removed}
        fields = {c.field for c in removed}
        row.claims = [c for c in row.claims if c.id not in ids]
        # Policy suppression is not evidence of a company changing its business.
        row.changes = [c for c in row.changes if c.field not in fields]
        row.run.refresh.setdefault('website', {})['entity_scope'] = {
            'group_site': group, 'other_registry_owners': sorted(owners.get(host, set()) - {org}),
            'historical_shared_domain_nominations': nominated_others,
            'shared_domain_index_available': nominations is not None,
            'withheld_fields': sorted(fields)}
        for family in {'activity', 'hiring'}:
            if any(c.family == family for c in removed) and not any(c.family == family and c.availability == 'available' for c in row.claims):
                row.run.sections[family] = 'not_applicable'
                if family in row.modules:
                    row.modules[family].state = 'not_applicable'
        if hasattr(row.profile, 'values'):
            row.profile.values = {c.field: c.value for c in row.claims}
        else:
            row.profile.claims = row.claims
