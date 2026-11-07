"""Offline, deterministic profile presentation. Never modifies source envelopes."""
import html
import hashlib
import base64
from html.parser import HTMLParser
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from .models.shapes import validate
from .synthesis.nace import english_title

THEME_BOOT = "document.documentElement.classList.add('js');try{document.documentElement.dataset.theme=localStorage.getItem('signalpost_theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}catch(e){document.documentElement.dataset.theme='light'}"
THEME_HASH = base64.b64encode(hashlib.sha256(THEME_BOOT.encode()).digest()).decode()
DATE_BOOT = "document.addEventListener('DOMContentLoaded',()=>{const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];const pattern=/(?<![\\d-])(\\d{4})-(\\d{2})-(\\d{2})(?:T\\d{2}:\\d{2}(?::\\d{2}(?:\\.\\d+)?)?(?:Z|[+-]\\d{2}:?\\d{2})?)?/g;function visit(root){if(root.nodeType===3){if(root.parentElement?.closest('script,style,textarea,#evidence-drawer'))return;const old=root.data,next=old.replace(pattern,(whole,y,m,d)=>+m>0&&+m<13?+d+' '+months[+m-1]+' '+y:whole);if(next!==old)root.data=next;return;}if(root.nodeType===1&&root.matches('script,style,textarea,#evidence-drawer'))return;for(const child of root.childNodes)visit(child);}visit(document.body);new MutationObserver(changes=>{for(const change of changes){if(change.type==='characterData')visit(change.target);else for(const node of change.addedNodes)visit(node);}}).observe(document.body,{childList:true,subtree:true,characterData:true});});"
DATE_HASH = base64.b64encode(hashlib.sha256(DATE_BOOT.encode()).digest()).decode()
CSP = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self' 'sha256-" + THEME_HASH + "' 'sha256-" + DATE_HASH + "'; base-uri 'none'; form-action 'none'"
ASSETS = Path(__file__).with_name('site_assets')
GROUPS = [('what-it-does', 'Overview', 'identity'), ('people', 'People', 'roles'),
          ('financials', 'Financials', 'accounts'), ('locations', 'Locations', 'subunits'),
          ('online', 'Website & social', 'website'), ('hiring', 'Jobs', 'hiring'),
          ('activity', 'Activity', 'activity')]
UNKNOWN = {'not_available': 'Checked; no information found within the source scope.',
           'failed': 'Check incomplete because a source or request budget was unavailable.',
           'blocked': 'Source access was refused by policy or robots.txt.',
           'not_applicable': 'This source is not applicable or was not enabled.',
           'ambiguous': 'Information could not be safely attributed to this company.'}


def esc(value):
    return html.escape(str(value), quote=True)


def safe_url(value):
    try:
        value = str(value)
        p = urlsplit(value)
        if p.scheme.lower() in {'http', 'https'} and p.hostname and not p.username and not p.password and not any(ord(c) < 32 for c in value):
            return value
    except ValueError:
        pass
    return None


def link(value, label=None):
    url = safe_url(value)
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer nofollow">{esc(label if label is not None else value)}</a>' if url else esc(label if label is not None else value)


def chip(state):
    labels = {'available': 'Found', 'not_available': 'Not found', 'failed': "Couldn't check",
              'ambiguous': 'Withheld', 'blocked': 'Blocked', 'not_applicable': 'Not applicable'}
    return f'<span class="chip {esc(state)}">{esc(labels.get(state, state.replace("_", " ")))}</span>'


def anchor(claim):
    # IDs come from validated claims, but prefix/hash conversion also prevents attribute injection.
    return 'fact-' + claim['id'][:16]


def normalize(raw):
    shape = 'union' if 'profile' in raw and 'claims' in raw else 'reference' if 'profile' in raw else 'contract'
    validate(raw, shape)
    if shape == 'reference':
        p = raw['profile']
        return {'organisation_number': raw['organisation_number'], 'claims': p['claims'], 'evidence': p['evidence'],
                'changes': p['changes'], 'run': {'sections': p['sections'], 'refresh': p['refresh'],
                'synthesis': p.get('synthesis'), 'completed_at': raw['completed_at']}}
    return raw


def registry_events(row):
    from types import SimpleNamespace
    from .registry_activity import recent
    from .models.claim import Claim
    from .models.evidence import Evidence
    obj = SimpleNamespace(run=SimpleNamespace(completed_at=row['run']['completed_at']),
                          claims=[Claim.model_validate(c) for c in row['claims']],
                          evidence=[Evidence.model_validate(e) for e in row['evidence']])
    return recent(obj)


def value_text(value):
    if value is None:
        return 'Unknown'
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, dict):
        return '; '.join(k.replace('_',' ').capitalize()+': '+value_text(v) for k,v in value.items() if k!='birth_date')
    if isinstance(value, list):
        return ', '.join(value_text(v) for v in value)
    return str(value)


MONTH_NAMES=('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
DATE_PATTERN=re.compile(r'(?<![\d-])(\d{4}-\d{2}-\d{2})(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?')


def display_time(value):
    try:
        d=datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return str(d.day)+' '+MONTH_NAMES[d.month-1]+' '+str(d.year)
    except (ValueError,AttributeError,TypeError):return str(value)


def display_dates(text):
    formatted=DATE_PATTERN.sub(lambda match:display_time(match.group(0)),str(text))
    # Excerpts may split a timestamp across HTML nodes; times belong in the drawer.
    return re.sub(r'T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?', '', formatted)


def display_markup_dates(markup):
    # Change only presentation text, never attributes, source URLs or source data.
    class Dates(HTMLParser):
        def __init__(self):super().__init__(convert_charrefs=False);self.output=[];self.raw=0
        def handle_starttag(self,tag,attrs):
            self.output.append(self.get_starttag_text())
            if tag in {'script','style'}:self.raw+=1
        def handle_endtag(self,tag):
            self.output.append('</'+tag+'>')
            if tag in {'script','style'}:self.raw-=1
        def handle_startendtag(self,tag,attrs):self.output.append(self.get_starttag_text())
        def handle_data(self,data):self.output.append(data if self.raw else display_dates(data))
        def handle_entityref(self,name):self.output.append('&'+name+';')
        def handle_charref(self,name):self.output.append('&#'+name+';')
        def handle_comment(self,data):self.output.append('<!--'+data+'-->')
    parser=Dates();parser.feed(markup);return ''.join(parser.output)


def avatar_letter(name):
    return next((c for c in str(name) if c.isalpha()),next((c for c in str(name) if c.isdigit()),'?')).upper()




def value_html(value):
    if isinstance(value, dict):
        return '<dl class="values">' + ''.join(f'<dt>{esc(k.replace("_", " "))}</dt><dd>{value_html(v)}</dd>' for k, v in sorted(value.items()) if k != 'birth_date') + '</dl>'
    if isinstance(value, list):
        return '<ul>' + ''.join('<li>' + value_html(v) + '</li>' for v in value) + '</ul>'
    return link(value) if isinstance(value, str) and safe_url(value) else esc(value_text(value))


def excerpt_html(span, value):
    # Highlight an exact leaf only, never markup from a source.
    leaves = []
    def walk(v):
        if isinstance(v, dict):
            for item in v.values(): walk(item)
        elif isinstance(v, list):
            for item in v: walk(item)
        elif v is not None: leaves.append(str(v))
    walk(value)
    match = next((v for v in sorted(leaves, key=len, reverse=True) if v and v in span), None)
    if not match:
        return esc(span)
    before, _, after = span.partition(match)
    return esc(before) + '<mark>' + esc(match) + '</mark>' + esc(after)


def evidence_panel(claim, records, shared=False):
    parts = []
    ids = claim.get('evidence_ids', [])
    for i, eid in enumerate(ids):
        e = records[eid]
        if not (e.get('source_url') or e.get('source_identifier')) or not e.get('retrieved_at') or not e.get('claim_span') or len(e['claim_span']) > 300 or not e.get('content_sha256') or not e.get('extraction_method'):
            raise ValueError('Incomplete evidence for displayed claim')
        if shared and i > 0:
            parts.append(f'<p><a href="#evidence-{esc(eid)}">Additional supporting source {i + 1}</a></p>')
            continue
        sha = e['content_sha256']
        scheme_note = ''
        if claim['field'] == 'official_website' and e['source_class'] == 'company_owned':
            scheme = urlsplit(e['source_url']).scheme.upper()
            scheme_note = f'<span class="transport-scheme">[{esc(scheme)}]</span> '
        parts.append('<div class="evidence-record"><dl class="values">'
                     f'<dt>Source / class</dt><dd>{esc(e["source_class"])}</dd>'
                     f'<dt>Source link</dt><dd>{link(e["source_url"])}</dd>'
                     f'<dt>Registry identifier</dt><dd>{esc(e.get("source_identifier") or "Not supplied")}</dd>'
                     f'<dt>Retrieved at (UTC)</dt><dd>{esc(e["retrieved_at"])}</dd>'
                     f'<dt>Effective / reporting date</dt><dd>{esc(value_text(e.get("effective_at") or e.get("reporting_period") or claim.get("reporting_period")))}</dd>'
                     f'<dt>SHA-256</dt><dd><code title="{esc(sha)}">{esc(sha[:16])}…</code> '
                     f'<button type="button" data-copy="{esc(sha)}">Copy full hash</button></dd>'
                     f'<dt>Extraction method / version</dt><dd>{esc(e["extraction_method"])}</dd>'
                     f'<dt>Locator</dt><dd>{esc(e["locator"])}</dd></dl>'
                     f'<blockquote class="excerpt">{scheme_note}{excerpt_html(e["claim_span"], claim["value"])}</blockquote></div>')
    if claim['availability'] == 'available' and not parts:
        raise ValueError('Available fact has no evidence')
    v = claim.get('value')
    identity = v.get('identity_level') if isinstance(v, dict) else None
    if identity:
        parts.append('<p>Website identity level: ' + esc(identity) + '</p>')
    return ''.join(parts)


def fact(claim, records, fallback=None):
    local_id = claim['id'][:16]
    available = claim['availability'] == 'available'
    label = claim.get('reasons',{}).get('label') or claim['field'].replace('identity.', '').replace('accounts.', '').replace('_', ' ')
    if claim['field'] == 'identity.registered_address':
        label = 'Registered business address'
    if claim['family'] in {'roles', 'subunits', 'hiring'} and isinstance(claim['value'], dict):
        v = claim['value']
        label = v.get('title') or v.get('name') or {'roles': 'Registered role', 'subunits': 'Registered workplace', 'hiring': 'Job advertisement'}[claim['family']]
    if claim['field'].startswith('website_description.'):
        label = "Company's own description"
    if claim['field'].startswith('identity.gleif.'):
        label=claim.get('reasons',{}).get('label','GLEIF '+claim['field'].rsplit('.',1)[-1].replace('_',' '))
    if claim['field'].startswith('procurement_award.'):
        label='Public procurement award'
    v = claim.get('value')
    title = english_title(v) if claim['field'].startswith('identity.nace') and isinstance(v, dict) else None
    content = value_html(v) if available else '<p>' + esc(UNKNOWN.get(claim['availability'], 'Unknown.')) + '</p>'
    if available and claim['field'].startswith('registry_change.'):
        from .sources.registry_changes import sentence as registry_sentence
        label = 'Registry announcement: ' + v['title']
        wording = registry_sentence(v)
        original_time = 'Registry publication time: ' + v['date'] + ' (not effective date).'
        if v.get('date_source') and original_time in wording:
            wording = wording.replace(original_time, v['date_source'] + ': ' + v['date'] + '.')
        content = '<p>' + esc(wording) + '</p><p>' + link(v['url'], 'Registry announcement') + '</p>'
    if available and claim['field'] == 'official_website' and isinstance(v, dict) and v.get('matched_via_subunit'):
        content = '<p class="relationship-note">Website of registered subunit ' + esc(v['matched_via_subunit']) + '</p>' + content
    if title:
        content = '<p>English industry title: ' + esc(title) + '</p>' + content
    if claim.get('carried_forward'):
        content = '<p class="stale">Previously supported; not freshly checked. Last successfully checked: ' + '<time datetime="'+esc(claim.get('last_observed_at') or '')+'">'+esc(display_time(claim.get('last_observed_at'))) + '</time>.</p>' + content
    period = claim.get('reporting_period')
    if period:
        parts = []
        if period.get('fiscal_year'): parts.append(f"Fiscal year: {period['fiscal_year']}")
        if period.get('period_start') and period.get('period_end'): parts.append(f"Accounting period: {period['period_start']} to {period['period_end']}")
        parts.append(f"Currency: {period.get('currency') or 'Unknown'}")
        if period.get('unit'): parts.append(f"Unit: {period['unit']}")
        content += '<p class="financial-meta muted">' + esc(' · '.join(parts)) + '</p>'
    panel = True
    if panel:
        content += f'<button type="button" aria-expanded="false" aria-controls="source-{esc(local_id)}" data-toggle="source-{esc(local_id)}">Check the evidence</button><div id="source-{esc(local_id)}" data-source="{esc(local_id)}" class="evidence" hidden></div>'
    if fallback:
        old=f'<button type="button" aria-expanded="false" aria-controls="source-{esc(local_id)}" data-toggle="source-{esc(local_id)}">Check the evidence</button>'
        content=content.replace(old,f'<a class="source-button" data-receipt="{esc(local_id)}" href="{esc(fallback)}">Source <span aria-hidden="true">&#8599;</span></a>')
        content=content.replace(f'<div id="source-{esc(local_id)}" data-source="{esc(local_id)}" class="evidence" hidden></div>','')
    if claim['family'] == 'accounts':
        return f'<tr id="{esc(anchor(claim))}"><th scope="row">{esc(label)} {chip(claim["availability"])}</th><td>{content}</td></tr>'
    return f'<article class="fact" id="{esc(anchor(claim))}"><h3>{esc(label)} {chip(claim["availability"])}</h3>{content}</article>'


def sentence_html(sentence, claim_map, change_ids):
    cites = []
    for n, cid in enumerate(sentence.get('claim_ids', []), 1):
        target = anchor(claim_map[cid]) if cid in claim_map else 'change-' + cid if cid in change_ids else None
        if target is None:
            raise ValueError('Unresolved synthesis citation')
        cites.append(f'<a href="#{esc(target)}" aria-label="Source fact {n}">[{n}]</a>')
    return '<p>' + esc(sentence['text']) + ' ' + ' '.join(cites) + '</p>'


def page(title, body, prefix='', kind='profile', company_data=None):
    body=display_markup_dates(body)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta http-equiv="Content-Security-Policy" content="{esc(CSP)}">'
            f'<title>{esc(title)}</title><script id="theme-boot">{THEME_BOOT}</script><script id="date-presentation">{DATE_BOOT}</script><link rel="stylesheet" href="{prefix}assets/site.css">'
            f'<script src="{prefix}data/index.js" defer></script>'
            + (f'<script src="{esc(company_data)}" defer></script>' if company_data else '') +
            f'<script src="{prefix}assets/site.js" defer></script>'
            f'</head><body data-page="{kind}"><a class="skip" href="#main">Skip to content</a>'
            f'<nav aria-label="Main"><a class="brand" href="{prefix}index.html"><svg aria-hidden="true" width="34" height="24" viewBox="0 0 34 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="9"/><circle cx="23" cy="12" r="9"/></svg>Nordic Company Lens</a>'
            f'<a href="{prefix}index.html?view=dashboard">Explore</a>'
            f'<a href="{prefix}compare.html" id="nav-compare">Compare <span id="compare-count"></span></a>'
            '<button type="button" id="global-search-open">Search <kbd>Ctrl/K</kbd></button>'
            f'<button type="button" id="status-toggle" class="status-toggle" aria-label="Toggle update status panel" aria-expanded="false" aria-controls="status-panel">'
            '<span id="status-dot" class="status-dot"></span> Update status</button>'
            f'<button type="button" id="theme-toggle" class="theme-toggle" aria-label="Toggle dark mode">Light / Dark</button></nav>'
            '<dialog id="global-search-dialog" aria-labelledby="global-search-heading">'
            '<h2 id="global-search-heading">Find a company</h2><label>Name or organisation number'
            '<input type="search" id="global-search-input" autocomplete="off"></label>'
            '<button type="button" id="global-search-close">Close</button>'
            '<ul id="global-search-results" aria-live="polite"></ul></dialog>'
            '<div id="status-panel" class="status-panel" role="dialog" aria-modal="true" aria-label="Update status" hidden>'
            '<div class="status-panel-inner">'
            '<div class="status-panel-header">'
            '<h2>Update status <span id="status-badge" class="chip"></span></h2>'
            '<button type="button" id="status-close" class="status-close" aria-label="Close update status panel">&times;</button>'
            '</div>'
            '<div class="status-progress-section">'
            '<div class="status-progress-bar-wrap"><progress id="status-progress" max="100" value="0"></progress></div>'
            '<p id="status-progress-text" class="status-progress-text"></p>'
            '</div>'
            '<div class="status-section">'
            '<h3>Companies</h3>'
            '<div id="status-counters" class="status-counters"></div>'
            '</div>'
            '<div class="status-section">'
            '<h3>Pipeline stages</h3>'
            '<div id="status-stages" class="status-stages"></div>'
            '</div>'
            '<div class="status-section">'
            '<h3>Timing &amp; resources</h3>'
            '<dl id="status-timing" class="values status-timing"></dl>'
            '</div>'
            '<div class="status-section">'
            '<h3>Recent events</h3>'
            '<div id="status-events" class="status-events"></div>'
            '</div>'
            '<p id="status-snapshot-note" class="status-snapshot-note muted" hidden></p>'
            '</div></div>'
            f'<main id="main">{body}</main><footer><a class="brand" href="{prefix}index.html">Nordic Company Lens</a><p>Norwegian company research. Every fact, traced to its source.</p><p>Evidence first. Unknown values remain unknown.</p><a href="{prefix}index.html#sources">Sources &amp; licences</a></footer></body></html>\n')


EXPLORER_VISIBLE_ROWS = 50


def explorer_cells(c, records):
    """Plain-text cells for one Evidence Explorer row (page and data file share this)."""
    f = c.get('field', '')
    v_str = value_text(c.get('value'))
    if len(v_str) > 80: v_str = v_str[:77] + '…'
    eids = c.get('evidence_ids', [])
    e = records.get(eids[0]) if eids else None
    span = e.get('claim_span', '—') if e else '—'
    if len(span) > 100: span = span[:97] + '…'
    return [f.replace('identity.', '').replace('accounts.', '').replace('_', ' '), c.get('availability', 'unknown'), v_str,
            e.get('source_class', '—') if e else '—', e.get('locator', '—') if e else '—',
            e.get('content_sha256', '') if e else '', span]


def deferred_registry_ids(row):
    items=[c for c in row['claims'] if c['field'].startswith('registry_change.')]
    items.sort(key=lambda c:(str((c.get('value') or {}).get('date','')),c['field']),reverse=True)
    awards=[c for c in row['claims'] if c['field'].startswith('procurement_award.')]
    awards.sort(key=lambda c:(str(c['value'].get('date','')),c['field']),reverse=True)
    return {c['id'] for c in items[10:]+awards[2:]}


def profile(row, title, source_routes=None):
    claims = row['claims']
    claim_map = {c['id']: c for c in claims}
    records = {e['id']: e for e in row['evidence']}
    by_field = {c['field']: c['value'] for c in claims if c['availability'] == 'available'}
    fields_map = {c['field']: c for c in claims if c['availability'] == 'available'}
    org = row['organisation_number']
    synthesis = row['run'].get('synthesis') or {}
    support = synthesis.get('change_claims') or []
    change_ids = {c['id'] for c in support}
    name = by_field.get('identity.legal_name', org)
    colour=int(hashlib.sha256(str(org).encode()).hexdigest()[:8],16)%8
    body=f'<header class="company-hero colour-{colour}"><div class="avatar" aria-hidden="true">{esc(avatar_letter(name))}</div><p class="eyebrow">Company profile</p><h1>{esc(name)}</h1><div class="metadata-pills">'
    body+=f'<span class="meta-pill">Org. {esc(org)} <button type="button" class="copy-icon" data-copy="{esc(org)}" aria-label="Copy organisation number"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true"><rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/></svg></button></span>'
    form=by_field.get('identity.organisation_form',by_field.get('identity.legal_form'))
    if form:
        label=(str(form.get('beskrivelse') or '')+' ('+str(form.get('kode') or '')+')') if isinstance(form,dict) else value_text(form)
        body+='<span class="meta-pill">'+esc(label)+'</span>'
    if by_field.get('identity.municipality'):body+='<span class="meta-pill">'+esc(str(by_field['identity.municipality']).title())+'</span>'
    workplace_count=sum(c['field'].startswith('subunits.unit.') and c['availability']=='available' for c in claims)
    body+='<a class="meta-pill" href="#locations">'+str(workplace_count)+(' registered workplace' if workplace_count==1 else ' registered workplaces')+'</a>'
    body+='<span class="meta-pill">Checked '+esc(display_time(row['run']['completed_at']))+'</span></div>'
    for flag,label,date_field in [('identity.bankrupt','Bankrupt','identity.bankruptcy_date'),('identity.under_liquidation','Under liquidation','identity.liquidation_date'),('identity.forced_dissolution','Under forced liquidation',None)]:
        if by_field.get(flag) is True:
            when=by_field.get(date_field) if date_field else None
            body+='<p class="status-danger">'+label+(' since '+esc(display_time(when)) if when else '')+'</p>'
            break
    body+=f'<div class="company-header-actions"><a class="source-button" href="../compare.html?companies={esc(org)}">Compare</a><button type="button" class="btn-watchlist" data-watchlist="{esc(org)}">Add to Watchlist</button></div></header><div class="profile-grid"><div class="profile-main">'
    sentences = [s for key in ('what_it_does', 'scale', 'leadership', 'changes') for s in synthesis.get('sections', {}).get(key, [])]
    from .synthesis.brief import select
    overview = select(synthesis, claims)
    body += '<section class="summary ledger-section" id="briefing"><h2>Company briefing</h2>'
    analyst = synthesis.get('analyst_brief')
    brief = ({'context_claims':analyst['context_claims'],'what':analyst['sentences'],'changes':[],'unknowns':[]} if analyst else synthesis.get('brief'))
    if brief:
        contexts = {c['id']: c for c in brief.get('context_claims', [])}
        for key, heading in [('what', 'What the company is and does'), ('changes', 'What changed since the previous run'), ('unknowns', "What's still unknown")]:
            if analyst and key!='what':continue
            body += '<div class="brief-part"><h3>' + esc(heading) + '</h3>'
            for s in brief[key]:
                cites = []
                for cid in s['claim_ids']:
                    if cid in contexts:
                        ident = 'context-' + cid[:16]
                        cites.append(f'<button class="citation" data-toggle="{ident}" aria-controls="{ident}" aria-expanded="false">[source]</button>')
                    else:
                        target = anchor(claim_map[cid]) if cid in claim_map else 'change-' + cid
                        cites.append(f'<a class="citation" href="#{esc(target)}">[source]</a>')
                body += '<p>' + esc(s['text']) + ' ' + ' '.join(cites) + '</p>'
                for cid in s['claim_ids']:
                    if cid in contexts:
                        context = contexts[cid]
                        body += f'<div class="evidence" id="context-{cid[:16]}" hidden><p>Run metadata (not an external source)</p><p>Claim ID: <code>{cid}</code></p><pre>{esc(value_text(context["value"]))}</pre></div>'
            body += '</div>'
    else:
        body += ''.join(sentence_html(s, claim_map, change_ids) for s in overview)
    remaining = [s for s in sentences if s not in overview]
    if remaining:
        body += '<details id="full-summary"><summary>Supporting detail: full cited summary</summary>'
        body += ''.join(sentence_html(s, claim_map, change_ids) for s in remaining) + '</details>'
    unknowns = synthesis.get('sections', {}).get('unknowns', [])
    if unknowns:
        if brief:
            body += '<details class="additional-unknowns"><summary>More detail on missing fields</summary>'
        targets = {'identity': 'what-it-does', 'what_it_does': 'what-it-does',
                   'scale': 'financials', 'accounts': 'financials',
                   'leadership': 'people', 'roles': 'people',
                   'subunits': 'locations', 'hiring': 'hiring',
                   'website': 'online', 'activity': 'activity', 'refresh': 'changes'}
        labels = {'not_available': 'Not found', 'not_applicable': 'Not applicable',
                  'blocked': 'Blocked', 'ambiguous': 'Ambiguous', 'failed': 'Failed'}
        body += '<div class="unknowns" role="region" aria-labelledby="unknowns-heading"><h3 id="unknowns-heading">What remains unknown</h3><ul>'
        for item in unknowns:
            state = item.get('state') or 'not_available'
            label = labels.get(state, state.replace('_', ' ').title())
            note = item.get('text') or item['reason']
            reason = item.get('reason')
            target = targets.get(item.get('family'), 'main')
            body += '<li><p><span class="chip ' + esc(state) + '">' + esc(label) + '</span> ' + esc(note) + '</p>'
            if reason and reason != note:
                body += '<p class="muted">Reason: ' + esc(reason) + '</p>'
            body += '<a href="#' + esc(target) + '">Review source status</a></li>'
        body += '</ul></div>'
        if brief:
            body += '</details>'
    body += '</section>'
    for family, meta in row['run'].get('refresh', {}).get('stale_sections', {}).items():
        body += '<aside class="stale stale-refresh"><strong>Stale refresh · ' + esc(family) + '</strong><p>Kept the previous ' + esc(meta['previous_state'].replace('_', ' ')) + ' snapshot. Refresh failed on ' + esc(meta['failed_attempt_at']) + ': ' + esc(', '.join(meta.get('failure_codes', []))) + '.</p></aside>'
    gleif=[c for c in claims if c['field'].startswith('identity.gleif.')]
    render=lambda c:fact(c,records,(source_routes or {}).get(c['id']))
    if gleif:
        body += '<section id="ownership" class="ledger-section"><h2>Ownership &amp; identifiers (GLEIF)</h2>'+''.join(render(c) for c in gleif)+'</section>'
    headline=[('accounts.revenue','Revenue'),('accounts.net_result','Annual result'),('identity.employees','Registered employees')]
    body += '<section class="overview-metrics" aria-label="Overview">'
    for field,label in headline:
        c=fields_map.get(field)
        if c:body += '<div class="overview-card"><span class="eyebrow">'+label+'</span><p><a href="#'+anchor(c)+'">'+esc(value_text(c['value']))+'</a></p><small>'+esc(value_text((c.get('reporting_period') or {}).get('fiscal_year') or row['run']['completed_at'][:10]))+'</small></div>'
    body += '</section>'
    buckets = {key: [] for key, _, _ in GROUPS}
    for c in claims:
        if c['field'].startswith('identity.gleif.'):continue
        f = c['field']; family = c['family']
        key = ('what-it-does' if f.startswith('website_description.') else
               'locations' if family == 'subunits' else
               'hiring' if f == 'identity.employees' else
               'online' if family == 'website' or f == 'identity.registered_website' else
               'financials' if family == 'accounts' else 'people' if family == 'roles' else
               'hiring' if family == 'hiring' else 'activity' if family == 'activity' else 'what-it-does')
        buckets[key].append(c)
    from .locations import registered_location
    from .models.claim import Claim
    business_location = registered_location([Claim.model_validate(c) for c in claims])
    if business_location:
        buckets['what-it-does'] = [c for c in buckets['what-it-does'] if c['id'] != business_location.id]
        buckets['locations'].append(claim_map[business_location.id])
    for key, label, family in GROUPS:
        areas = {'what-it-does': ('brief', 'Company brief'),
                 'financials': ('financials', 'Latest financials'),
                 'people': ('leadership', 'Who runs it?'),
                 'hiring': ('workforce', 'Working here'),
                 'activity': ('activity', 'Recent activity')}
        if key in areas:
            area, heading = areas[key]
            body += f'<section class="company-area" data-area="{area}"><h2>{heading}</h2>'
        items = buckets[key]
        deferred=deferred_registry_ids(row) if key=='activity' else set()
        details=[c for c in items if c['field'].startswith(('roles.detail.','subunits.detail.')) or c['id'] in deferred]
        items=[c for c in items if not c['field'].startswith(('roles.detail.','subunits.detail.')) and c['id'] not in deferred]
        if key == 'activity': items.sort(key=lambda c: str((c['value'] or {}).get('date', '')) if isinstance(c['value'], dict) else '', reverse=True)
        state = row['run']['sections'].get(family, 'not_applicable')
        if key == 'locations' and business_location and state in {'not_available','not_applicable'}:
            state = 'available'
        dated_registry = registry_events(row) if key == 'activity' else []
        public_state = 'available' if dated_registry and state in {'not_applicable','not_available'} else state
        body += f'<section id="{key}"><h2>{label} {chip(public_state)}</h2>'
        if key == 'activity':
            if dated_registry: body += '<h3>Recent registry dates</h3>'
            for day, label, c in dated_registry:
                body += '<p>' + esc(label + ': ' + day) + f' <a href="#fact-{esc(c.id[:16])}">Registry source</a></p>'
            body += '<h3>Published updates ' + chip(state) + '</h3>'
            if state == 'not_available' and not dated_registry:
                body += '<p>No dated changes found in sources checked.</p>'
        if key == 'financials':
            body += '<p>Reported values from Regnskapsregisteret; no figures or growth ratios are calculated.</p>'
            years = sorted({(c.get('reporting_period') or {}).get('fiscal_year') for c in items if (c.get('reporting_period') or {}).get('fiscal_year')}, reverse=True)
            currencies = sorted({(c.get('reporting_period') or {}).get('currency') for c in items if (c.get('reporting_period') or {}).get('currency')})
            curr_str = ", ".join(currencies) if currencies else "Unspecified"
            if len(years) > 1:
                from .sources.financial_comparability import compare_periods
                curr_c = next((c for c in items if (c.get('reporting_period') or {}).get('fiscal_year') == years[0] and c.get('field', '').endswith('.revenue')), None)
                prior_c = next((c for c in items if (c.get('reporting_period') or {}).get('fiscal_year') == years[1] and c.get('field', '').endswith('.revenue')), None)
                if not curr_c:
                    curr_c = next((c for c in items if (c.get('reporting_period') or {}).get('fiscal_year') == years[0]), None)
                if not prior_c:
                    prior_c = next((c for c in items if (c.get('reporting_period') or {}).get('fiscal_year') == years[1]), None)
                comp_info = ""
                if curr_c and prior_c:
                    res = compare_periods(curr_c, prior_c, org=row.get('organisation_number'), metric='revenue')
                    if res.comparable:
                        if res.growth_rate is not None:
                            pct = f"{res.growth_rate * 100:+.1f}%"
                            comp_info = f' <span class="chip chip-verified">Comparable</span> Revenue trend ({years[1]} → {years[0]}): {pct}.'
                        else:
                            comp_info = f' <span class="chip chip-verified">Comparable</span> Raw values comparable; growth rate withheld.'
                    else:
                        reasons_str = ", ".join(res.reason_codes)
                        comp_info = f' <span class="chip chip-gated">Comparability gated: {reasons_str}</span> No derived growth calculated.'
                body += f'<div class="financial-trend-banner"><p><strong>Multi-year filing trend:</strong> Accounts filed across {len(years)} fiscal years ({", ".join(str(y) for y in years)}). Reporting currency: {esc(curr_str)}.{comp_info}</p></div>'
            elif len(years) == 1:
                body += f'<div class="financial-trend-banner"><p><strong>Reporting period:</strong> Fiscal year {years[0]} filed in Regnskapsregisteret ({esc(curr_str)}). Single-year reported values.</p></div>'
        if key == 'online': body += '<p>Website proof types: orgnr = exact registered number; registry_declared = registered site with corroboration; signals = accepted identity signals.</p>'
        if not items or state != 'available': body += '<p>' + esc(UNKNOWN.get(state, 'No facts published in this section.')) + '</p>'
        if key == 'financials' and items:
            chart=[c for c in items if c['availability']=='available' and isinstance(c['value'],(int,float)) and not isinstance(c['value'],bool) and c['field'].endswith(('.revenue','.net_result')) and not c['field'].startswith('accounts.consolidated.')]
            if chart:
                ceiling=max([abs(c['value']) for c in chart]+[1])
                body += '<div class="financial-chart"><h3>Reported revenue and annual result</h3>'
                for c in chart:
                    period=c.get('reporting_period') or {};metric='Revenue' if c['field'].endswith('.revenue') else 'Annual result'
                    body += '<div class="chart-row '+('result' if metric=='Annual result' else 'revenue')+'"><span>'+esc(metric+' '+str(period.get('fiscal_year','')))+'</span><meter min="0" max="'+str(ceiling)+'" value="'+str(abs(c['value']))+'" aria-label="'+esc(metric+' '+str(period.get('fiscal_year','')))+'"></meter><span><a href="#'+anchor(c)+'">'+esc(value_text(c['value'])+' '+str(period.get('currency') or ''))+'</a></span></div>'
                body += '</div>'
        if key == 'financials' and items:
            body += '<table class="financial-table"><caption>Reported financial facts</caption><thead><tr><th scope="col">Metric</th><th scope="col">Value and evidence</th></tr></thead><tbody>'
        if key=='activity':
            items.sort(key=lambda c: (0 if not c['field'].startswith(('registry_change.','procurement_award.')) else 1 if c['field'].startswith('registry_change.') else 2))
        last_activity_group=None
        for i, c in enumerate(items):
            if key=='activity':
                group='Registry announcements' if c['field'].startswith('registry_change.') else 'Public procurement awards' if c['field'].startswith('procurement_award.') else 'Company-published news'
                if group!=last_activity_group:body += '<h3 class="activity-group">'+group+'</h3>';last_activity_group=group
            if key == 'locations' and i == 10:
                body += '<button type="button" aria-expanded="false" aria-controls="more-locations" data-toggle="more-locations">Show remaining workplaces</button><div id="more-locations" hidden>'
            body += render(c)
        if key == 'locations' and len(items) > 10: body += '</div>'
        if key == 'financials' and items: body += '</tbody></table>'
        if details:
            if source_routes:
                body += '<noscript><p>Additional sourced facts: '+''.join('<a id="'+anchor(c)+'" href="'+esc(source_routes[c['id']])+'">'+esc(c['field'])+'</a> ' for c in details)+'</p></noscript>'
            body += '<details><summary>'+(('Additional sourced activity (' if any(c['field'].startswith('procurement_award.') for c in details) else 'Additional registry announcements (') if key=='activity' else 'Additional official attributes (')+str(len(details))+')</summary><div data-registry-details="'+esc(key)+'"></div></details>'
        body += '</section>'
        if key in areas:
            body += '</section>'

    body += '<section id="gaps"><h2>What we could not find</h2>'
    for family,state in row['run']['sections'].items():
        if state!='available':body += '<p>'+esc(family.replace('_',' ').capitalize())+': '+chip(state)+' Checked '+esc(row['run']['completed_at'][:10])+' - '+esc(UNKNOWN.get(state,'No supported value.'))+'</p>'
    body += '</section><details class="technical-audit"><summary>Full timeline, refresh and audit trail</summary>'
    # 5. Verified Company Timeline (Dated business events)
    timeline_events = []
    founding_items = [
        ('identity.founding_date', 'Company founded', 'Founding'),
        ('identity.registration_date', 'Registered in Enhetsregisteret', 'Registry'),
        ('identity.vat_registration_date', 'Registered for VAT', 'Registry')
    ]
    for fld, lbl, tlabel in founding_items:
        if fld in fields_map:
            c = fields_map[fld]
            val = str(c.get('value', ''))
            if val:
                timeline_events.append({
                    'date': val[:10],
                    'label': lbl,
                    'detail': f'Official date in Brønnøysundregistrene: {val}',
                    'type_class': 'available',
                    'type_label': tlabel,
                    'anchor': anchor(c)
                })

    seen_fiscal_years = set()
    for c in claims:
        if c['family'] == 'accounts' and c['availability'] == 'available' and c.get('reporting_period'):
            period = c['reporting_period']
            f_year = period.get('fiscal_year')
            p_end = period.get('period_end') or (f'{f_year}-12-31' if f_year else None)
            if f_year and f_year not in seen_fiscal_years and p_end:
                seen_fiscal_years.add(f_year)
                rev = by_field.get('accounts.revenue')
                res = by_field.get('accounts.net_result')
                details_parts = []
                curr = period.get('currency') or 'Unknown currency'
                if rev is not None: details_parts.append(f'Revenue: {value_text(rev)} {esc(curr)}')
                if res is not None: details_parts.append(f'Net result: {value_text(res)} {esc(curr)}')
                detail_str = f'Fiscal year {f_year} filed in Regnskapsregisteret' + (f' ({", ".join(details_parts)})' if details_parts else '')
                timeline_events.append({
                    'date': str(p_end)[:10],
                    'label': f'Financial accounts ({f_year})',
                    'detail': detail_str,
                    'type_class': 'available',
                    'type_label': 'Financials',
                    'anchor': anchor(c)
                })

    for c in claims:
        if c['family'] == 'hiring' and c['availability'] == 'available' and isinstance(c.get('value'), dict):
            j = c['value']
            pub = j.get('published')
            if pub:
                title_ad = j.get('title') or 'Job advertisement'
                via = f" (matched via {j['matched_via']})" if j.get('matched_via') else ''
                timeline_events.append({
                    'date': str(pub)[:10],
                    'label': f'Job posted: {title_ad}',
                    'detail': f'Active job advertisement on Arbeidsplassen (NAV){via}',
                    'type_class': 'available',
                    'type_label': 'Hiring',
                    'anchor': anchor(c)
                })

    dated_reg = registry_events(row)
    for day, lbl, c in dated_reg:
        c_anchor = f'fact-{c.id[:16]}' if hasattr(c, 'id') else anchor(c)
        if not any(e['date'] == day and lbl in e['label'] for e in timeline_events):
            timeline_events.append({
                'date': day,
                'label': f'Registry event: {lbl}',
                'detail': 'Filing recorded in Norwegian business registry',
                'type_class': 'available',
                'type_label': 'Registry',
                'anchor': c_anchor
            })

    changes = sorted(row['changes'], key=lambda c: c['last_observed_at'], reverse=True)
    for event in changes:
        if event.get('last_observed_at'):
            timeline_events.append({
                'date': event['last_observed_at'][:10],
                'label': f"Verified change: {event.get('field', 'Attribute').replace('_', ' ')}",
                'detail': 'Previous verified value updated in registry refresh',
                'type_class': 'available',
                'type_label': 'Change',
                'anchor': None
            })

    timeline_events.sort(key=lambda e: (e['date'], e['label']), reverse=True)

    body += '<section id="timeline" class="company-timeline"><h2>Company timeline</h2>'
    body += '<p class="timeline-note muted">Verified dates from official registry filings, financial accounts, and job postings. Retrieval and observation timestamps are excluded. Timeline does not represent an exhaustive company history.</p>'
    if timeline_events:
        body += '<div class="timeline-container">'
        for ev in timeline_events:
            body += '<div class="timeline-item"><div class="timeline-node" aria-hidden="true"></div><div class="timeline-body">'
            body += f'<div class="timeline-meta"><time class="timeline-date">{esc(ev["date"])}</time><span class="chip {esc(ev["type_class"])}">{esc(ev["type_label"])}</span></div>'
            body += f'<h3 class="timeline-title">{esc(ev["label"])}</h3>'
            if ev.get('detail'):
                body += f'<p class="timeline-detail">{esc(ev["detail"])}</p>'
            if ev.get('anchor'):
                body += f'<p class="timeline-link"><a href="#{esc(ev["anchor"])}">View source evidence</a></p>'
            body += '</div></div>'
        body += '</div>'
    else:
        body += '<p class="timeline-empty">No dated business events verified for this entity.</p>'
    body += '</section>'

    body += '<section id="changes" class="changes-section"><h2>Verified changes &amp; freshness</h2>'
    body += f'<div class="freshness-banner"><p><strong>Last verified:</strong> <time class="verified-time">{esc(display_time(row["run"]["completed_at"]))}</time> <span class="chip available">{esc(row["run"].get("refresh", {}).get("mode", "baseline"))}</span></p></div>'

    # Business changes subsection
    body += '<h3>Verified business changes</h3>'
    if changes:
        body += '<div class="changes-list">'
        for event in changes:
            field_name = event.get('field', 'Attribute').replace('identity.', '').replace('accounts.', '').replace('_', ' ')
            ch_type = event.get('type', 'changed')
            mat = event.get('materiality', 'material')
            old_ids = event.get('old_evidence_ids', [])
            new_ids = event.get('new_evidence_ids', [])
            old_ev = records.get(old_ids[0]) if old_ids else None
            new_ev = records.get(new_ids[0]) if new_ids else None
            old_loc = event.get('old_locator') or (old_ev.get('locator') if old_ev else '—')
            new_loc = event.get('new_locator') or (new_ev.get('locator') if new_ev else '—')
            old_sha = event.get('old_content_sha256') or (old_ev.get('content_sha256') if old_ev else '')
            new_sha = event.get('new_content_sha256') or (new_ev.get('content_sha256') if new_ev else '')
            old_val_html = value_html(event.get('old_value')) if event.get('old_value') is not None else '<span class="muted">None (added)</span>'
            new_val_html = value_html(event.get('new_value')) if event.get('new_value') is not None else '<span class="muted">None (removed)</span>'
            old_sha_disp = f'<code title="{esc(old_sha)}">{esc(old_sha[:12])}…</code>' if old_sha else '—'
            new_sha_disp = f'<code title="{esc(new_sha)}">{esc(new_sha[:12])}…</code>' if new_sha else '—'

            body += f'<article class="change-card"><div class="change-card-header"><h4>Change in: {esc(field_name)}</h4><div><span class="chip available">{esc(ch_type)}</span> <span class="chip not_applicable">{esc(mat)}</span></div></div>'
            body += f'<p class="change-time muted">Observed: <time>{esc(display_time(event.get("last_observed_at")))}</time></p>'
            body += '<div class="change-comparison-grid">'
            body += f'<div class="change-col change-col-prev"><h5>Previous value</h5><div class="change-val">{old_val_html}</div><dl class="values values-compact"><dt>Locator</dt><dd><code>{esc(old_loc)}</code></dd><dt>SHA-256</dt><dd>{old_sha_disp}</dd></dl></div>'
            body += f'<div class="change-col change-col-curr"><h5>Current value</h5><div class="change-val">{new_val_html}</div><dl class="values values-compact"><dt>Locator</dt><dd><code>{esc(new_loc)}</code></dd><dt>SHA-256</dt><dd>{new_sha_disp}</dd></dl></div>'
            body += '</div></article>'
        body += '</div>'
    else:
        mode_note = 'First observation (baseline run).' if row['run'].get('refresh', {}).get('mode') == 'baseline' else 'No business changes detected since the previous verification run.'
        body += f'<p class="muted">{esc(mode_note)}</p>'

    for c in support:
        body += f'<details id="change-{esc(c["id"])}"><summary>{esc(c["field"])}: {esc(value_text(c["value"]))}</summary>'
        for eid in c.get('evidence_ids', []):
            e = records[eid]
            body += '<div class="evidence-record"><p>' + link(e['source_url']) + '</p><p>Retrieved: ' + esc(e['retrieved_at']) + '</p><p>Reporting period: ' + esc(value_text(e.get('reporting_period'))) + '</p><blockquote>' + esc(e['claim_span']) + '</blockquote></div>'
        body += '</details>'

    # Source availability & observation changes subsection
    observations = row['run'].get('refresh', {}).get('observation_changes', [])
    body += '<div class="observation-changes-section"><h3>Source availability &amp; observation changes</h3>'
    body += '<p class="muted">Operational shifts in source availability (e.g. rate limits, timeouts, schema updates) tracked separately from business modifications.</p>'
    if observations:
        body += '<div class="table-responsive"><table class="observation-table"><thead><tr><th scope="col">Section / Source</th><th scope="col">Previous State</th><th scope="col">Current State</th><th scope="col">Reason / Detail</th></tr></thead><tbody>'
        for ob in observations:
            sec = ob.get('section', 'general')
            prev_st = ob.get('previous_state', '—')
            curr_st = ob.get('current_state', '—')
            rsn = ob.get('reason', '—')
            fld = ob.get('field')
            sec_lbl = f'{sec}.{fld}' if fld else sec
            body += f'<tr><td><strong>{esc(sec_lbl)}</strong></td><td>{chip(prev_st)}</td><td>{chip(curr_st)}</td><td>{esc(rsn)}</td></tr>'
        body += '</tbody></table></div>'
    else:
        body += '<p class="muted">No source observation or availability transitions occurred during this verification run.</p>'
    body += '</div></section>'

    # Evidence Explorer Section
    body += '<section id="evidence-explorer" class="evidence-explorer">'
    body += '<div class="evidence-explorer-header">'
    body += '<h2>Evidence Explorer</h2>'
    body += '<div class="export-actions">'
    body += '<button type="button" id="export-profile-json" class="btn-export">Export Provenance (JSON)</button> '
    body += '<button type="button" id="export-profile-csv" class="btn-export">Export Summary (CSV)</button>'
    body += '</div></div>'
    body += '<p class="muted">Audit trail of verified company facts with complete supporting provenance, exact source locators, cryptographic SHA-256 receipts, and verbatim source excerpts.</p>'
    body += '<div class="table-responsive"><table class="evidence-explorer-table" aria-label="Evidence Explorer audit trail">'
    body += '<thead><tr><th scope="col">Fact / Claim</th><th scope="col">Status</th><th scope="col">Value</th><th scope="col">Source Class</th><th scope="col">Locator</th><th scope="col">SHA-256</th><th scope="col">Verbatim Excerpt</th></tr></thead><tbody>'
    for c in claims[:EXPLORER_VISIBLE_ROWS]:
        lbl, avail, v_str, s_class, loc, sha, span = explorer_cells(c, records)
        sha_disp = f'<code title="{esc(sha)}">{esc(sha[:12])}…</code>' if sha else '—'
        body += f'<tr><th scope="row">{esc(lbl)}</th><td>{chip(avail)}</td><td>{esc(v_str)}</td><td>{esc(s_class)}</td><td><code>{esc(loc)}</code></td><td>{sha_disp}</td><td><blockquote class="table-excerpt">{esc(span)}</blockquote></td></tr>'
    body += '</tbody></table></div>'
    hidden = len(claims) - EXPLORER_VISIBLE_ROWS
    if hidden > 0:
        body += (f'<p class="muted" id="explorer-more-note">Showing {EXPLORER_VISIBLE_ROWS} of {len(claims)} claims; every claim stays in the exports and the company data file.</p>'
                 f'<button type="button" id="explorer-show-all" data-hidden="{hidden}">Show the remaining {hidden} claims</button>')
    body += '</section>'

    body += f'<p><a href="../index.html">Back to search</a> · <a href="../compare.html?companies={esc(org)}">Compare with…</a></p>'
    body += '</details></div><aside class="profile-sidebar"><h2>On this page</h2><nav aria-label="Company sections">'+''.join('<a href="#'+key+'">'+label+'</a>' for key,label in [('briefing','Company briefing')]+([('ownership','Ownership & identifiers (GLEIF)')] if gleif else [])+[(key,label) for key,label,_ in GROUPS]+[('gaps','Gaps')])+'</nav><h3>Data coverage</h3>'+''.join('<p>'+esc(f)+': '+chip(state)+'</p>' for f,state in row['run']['sections'].items())+'</aside></div>'
    return page(str(name) + ' · ' + title, body, '../', company_data=org+'.data.js')


def company_payload(row):
    evidence={e['id']:e for e in row['evidence']}
    referenced=set()
    facts=[]
    def leaves(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key!='birth_date':yield from leaves(item)
        elif isinstance(value,list):
            for item in value:yield from leaves(item)
        elif value is not None:yield str(value)
    for claim in row['claims']:
        # Validate the entire evidence set before writing any file.
        evidence_panel(claim,evidence)
        referenced.update(claim['evidence_ids'])
        v=claim.get('value')
        facts.append({'id':claim['id'][:16],'evidence_ids':claim['evidence_ids'],
                      'field':claim.get('field'),'family':claim.get('family'),'availability':claim.get('availability'),
                      'values':list(leaves(v)), 'value':v, 'reporting_period':claim.get('reporting_period'),
                      'identity_level':v.get('identity_level') if isinstance(v,dict) else None})
        facts[-1]['confidence'] = claim.get('confidence')
        facts[-1]['reasons'] = sorted({e.get('code') for e in row.get('errors', []) if e.get('section') == claim['family'] and e.get('code') != 'website_candidates'})
        facts[-1]['stale_since'] = claim.get('stale_since')
    if len({c['id'][:16] for c in row['claims']}) != len(row['claims']):
        raise ValueError('Conflicting local fact anchors')
    # Records from one response share source metadata. Store it once without losing fields.
    source_fields=['source_url','source_class','retrieved_at','content_sha256',
                   'extraction_method','source_identifier','reporting_period']
    evidence_fields=['id','claim_span','locator','effective_at']
    sources=[]; source_lookup={}; records=[]
    for eid in sorted(referenced):
        e=evidence[eid]
        shared=[e.get(k) for k in source_fields]
        key=json.dumps(shared,sort_keys=True,ensure_ascii=False)
        if key not in source_lookup:
            source_lookup[key]=len(sources);sources.append(shared)
        records.append([source_lookup[key]]+[e.get(k) for k in evidence_fields])
    details=[{'id':c['id'][:16],'field':c['field'],'value':c['value'],'availability':c['availability'],
              'group':'people' if c['family']=='roles' else 'locations'} for c in row['claims']
             if c['field'].startswith(('roles.detail.','subunits.detail.'))]
    from .sources.registry_changes import sentence as registry_sentence
    deferred=deferred_registry_ids(row)
    details.extend({'id':c['id'][:16],'field':('Public procurement award: ' if c['field'].startswith('procurement_award.') else 'Registry announcement: ')+c['value']['title'],
                    'value':(c['value'] if c['field'].startswith('procurement_award.') else registry_sentence(c['value'])),'availability':c['availability'],'group':'activity'}
                   for c in row['claims'] if c['id'] in deferred)
    name = next((c['value'] for c in row['claims'] if c['field'] == 'identity.legal_name' and c['availability'] == 'available'), row['organisation_number'])
    all_records = {e['id']: e for e in row['evidence']}
    payload = {'orgnr': row['organisation_number'], 'name': name,
               'source_fields':source_fields,'sources':sources,'evidence_fields':evidence_fields,
               'records':records,'facts':facts,'registry_details':details}
    if len(row['claims']) > EXPLORER_VISIBLE_ROWS:
        payload['explorer_rows'] = [explorer_cells(c, all_records) for c in row['claims'][EXPLORER_VISIBLE_ROWS:]]
    return payload


def index_record(row):
    available = [c for c in row['claims'] if c['availability'] == 'available']
    fields = {c['field']: c for c in available}
    def get(field): return fields.get(field, {}).get('value')
    industry = next((c for c in available if c['field'].startswith('identity.nace')), None)
    iv = industry['value'] if industry else {}
    website = get('official_website')
    roles = [c for c in available if c['field'].startswith('roles.role.') and isinstance(c['value'],dict)]
    def role(code):
        return next((c for c in roles if (c['value'].get('role_type') or {}).get('kode') == code and not c['value'].get('inactive')), None)
    ceo, chair, auditor = role('DAGL'), role('LEDE'), role('REVI')

    emp = get('identity.employees')
    if emp is None:
        size_band = 'unknown'
    else:
        try:
            n = int(emp)
            if n == 0: size_band = 'zero'
            elif 1 <= n <= 9: size_band = 'micro'
            elif 10 <= n <= 49: size_band = 'small'
            elif 50 <= n <= 249: size_band = 'medium'
            elif n >= 250: size_band = 'large'
            else: size_band = 'unknown'
        except (ValueError, TypeError):
            size_band = 'unknown'

    founding_date = get('identity.founding_date') or get('identity.registration_date')
    web_origin = website.get('candidate_origin') if isinstance(website, dict) else None
    web_proof = website.get('proof_type') if isinstance(website, dict) else None

    job_postings = []
    for c in available:
        if c['family'] == 'hiring' and isinstance(c.get('value'), dict):
            j = c['value']
            job_postings.append({
                'title': j.get('title') or 'Job advertisement',
                'published': str(j.get('published'))[:10] if j.get('published') else None,
                'expires': str(j.get('expires'))[:10] if j.get('expires') else None,
                'matched_via': j.get('matched_via'),
                'anchor': anchor(c),
                'uuid': j.get('uuid')
            })
    job_titles = [j['title'] for j in job_postings if j.get('title')]
    job_dates = [j['published'] for j in job_postings if j.get('published')]

    reg_events = registry_events(row)
    published = [(c['value']['date'], c['value']['title'], c) for c in available
                 if c['family'] == 'activity' and isinstance(c.get('value'), dict)
                 and c['value'].get('date') and c['value'].get('title') and not c.get('carried_forward')]
    all_events = sorted(list(reg_events) + published, key=lambda event: event[0], reverse=True)
    latest_event = all_events[0] if all_events else None
    recent_events = ([{'date': latest_event[0], 'label': latest_event[1],
                       'anchor': 'fact-' + (getattr(latest_event[2], 'id', None) or latest_event[2]['id'])[:16]}]
                     if latest_event else [])

    result = {'orgnr': row['organisation_number'], 'name': get('identity.legal_name') or row['organisation_number'],
              'municipality': get('identity.municipality'), 'nace': iv.get('kode'), 'industry_en': english_title(iv) if iv else None,
              'industry_no': iv.get('beskrivelse'), 'employees': emp, 'size_band': size_band,
              'revenue': get('accounts.revenue'),
              'annual_result': get('accounts.net_result'), 'fiscal_year': next(((c.get('reporting_period') or {}).get('fiscal_year') for c in available if c['family'] == 'accounts' and (c.get('reporting_period') or {}).get('fiscal_year')), None),
              'currency': next(((c.get('reporting_period') or {}).get('currency') for c in available if c['family'] == 'accounts' and (c.get('reporting_period') or {}).get('currency')), None) if (get('accounts.revenue') is not None or get('accounts.net_result') is not None) else None,
              'unit': next(((c.get('reporting_period') or {}).get('unit') for c in available if c['family'] == 'accounts' and (c.get('reporting_period') or {}).get('unit')), None) if (get('accounts.revenue') is not None or get('accounts.net_result') is not None) else None,
              'founding_date': str(founding_date) if founding_date else None,
              'ceo': ceo['value'].get('name') if ceo else None, 'chair': chair['value'].get('name') if chair else None,
              'auditor': auditor['value'].get('name') if auditor else None,
              'workplaces': sum(c['field'].startswith('subunits.unit.') for c in available) if row['run']['sections'].get('subunits') == 'available' else None,
              'website': website.get('final_url') if isinstance(website, dict) else None,
              'website_origin': web_origin,
              'website_proof': web_proof,
              'social': sum(c['family'] == 'website' and 'social' in c['field'] for c in available),
              'jobs': sum(c['family'] == 'hiring' and not c.get('carried_forward') for c in available),
              'job_titles': job_titles[:3],
              'job_dates': job_dates,
              'job_postings': job_postings,
              'activity': sum(c['family'] == 'activity' for c in available) + len(reg_events),
              'latest_activity_date': latest_event[0] if latest_event else None,
              'latest_activity_label': latest_event[1] if latest_event else None,
              'recent_events': recent_events,
              'sections': dict(row['run']['sections']),
              'claim_count': len(available), 'last_checked': row['run']['completed_at'], 'anchors': {}}
    mapping = {'name': 'identity.legal_name', 'municipality': 'identity.municipality', 'employees': 'identity.employees',
               'revenue': 'accounts.revenue', 'annual_result': 'accounts.net_result', 'website': 'official_website'}
    if founding_date and 'identity.founding_date' in fields: mapping['founding_date'] = anchor(fields['identity.founding_date'])
    elif founding_date and 'identity.registration_date' in fields: mapping['founding_date'] = anchor(fields['identity.registration_date'])
    for key, field in mapping.items():
        if field in fields and key not in result['anchors']: result['anchors'][key] = anchor(fields[field])
    if industry: result['anchors']['industry'] = anchor(industry)
    for key, c in [('ceo', ceo), ('chair', chair), ('auditor', auditor)]:
        if c: result['anchors'][key] = anchor(c)
    result['flags'] = {key: bool(result[key]) for key in ('website', 'jobs', 'social', 'activity')}
    result['areas'] = {'brief': any(c['family'] == 'identity' for c in available),
                       'financials': any(c['family'] == 'accounts' for c in available),
                       'leadership': any(c['family'] == 'roles' for c in available),
                       'workforce': any(c['family'] in {'subunits', 'hiring'} or c['field'] == 'identity.employees' for c in available),
                       'activity': bool(result['activity'])}
    result['areas_found'] = sum(result['areas'].values())
    if result['activity'] and result['sections'].get('activity','not_applicable') in {'not_available','not_applicable'}:
        result['sections']['activity']='available'
    return result


def index_page(records, title, skipped=()):
    n = len(records)
    summary = f'{n} companies'
    for key in ('website', 'jobs', 'activity'):
        summary += f' · {sum(r["flags"][key] for r in records) / n * 100 if n else 0:.1f}% with {key}'
    summary += ' · Run date: ' + max((r['last_checked'] for r in records), default='Unknown')
    verified=sum(r['claim_count'] for r in records)
    websites=sum(r['flags']['website'] for r in records)
    activity=sum(r['flags']['activity'] for r in records)
    body = '<section class="home-hero"><div class="hero-copy"><p class="eyebrow">Norwegian company research</p><h1>Every fact, traced to its source.</h1><p>Search '+str(n)+' Norwegian companies, compare them side by side, and check the original source behind every number.</p><p id="cohort-summary">'+esc(summary)+'</p>'
    body += '<div class="hero-search"><label class="visually-hidden" for="search">Search by name, organisation number, municipality or industry</label><input id="search" type="search" autocomplete="off" placeholder="Search by name, org. number, town or industry" aria-controls="search-autocomplete"><div id="search-autocomplete" class="autocomplete-dropdown" hidden></div></div><div class="try-chips"><span>Try:</span>'
    for r in sorted(records,key=lambda r:r['claim_count'],reverse=True)[:3]:body += '<button type="button" data-search="'+esc(r['name'])+'">'+esc(r['name'])+'</button>'
    body += '</div></div><div class="hero-stats">'
    for number,label in [(n,'companies'),(verified,'verified claims'),(websites,'verified websites'),(activity,'companies with activity')]:body += '<div class="hero-stat"><strong>'+format(number,',')+'</strong><span>'+label+'</span></div>'
    body += '</div></section>'

    if skipped:
        shown = ', '.join('<code>' + esc(str(x)[:40]) + '</code>' for x in skipped[:20])
        more = f' and {len(skipped) - 20} more' if len(skipped) > 20 else ''
        body += (f'<aside id="invalid-inputs" class="notice" role="note"><strong>{len(skipped)} input record(s) have no company page</strong> '
                 f'because the organisation number is not valid: {shown}{more}. They keep an explicit terminal envelope in the JSON output.</aside>')

    # View switcher tabs
    body += '<div class="view-switcher" role="tablist" aria-label="View selection">'
    body += '<button type="button" id="tab-dashboard" class="tab-btn active" role="tab" aria-selected="true" aria-controls="view-dashboard">📊 Dashboard</button>'
    body += '<button type="button" id="tab-directory" class="tab-btn" role="tab" aria-selected="false" aria-controls="view-directory">🏢 Company Directory</button>'
    body += '<button type="button" id="tab-hiring" class="tab-btn" role="tab" aria-selected="false" aria-controls="view-hiring">💼 Hiring Explorer</button>'
    body += '</div>'

    # 1. Dashboard View
    body += '<section id="view-dashboard" class="dashboard-view" role="tabpanel" aria-labelledby="tab-dashboard">'
    body += '<div class="scope-banner" id="dashboard-scope-banner">'
    body += f'<div class="scope-text-wrap"><span class="scope-tag">Cohort Scope</span> <span id="scope-text">Full evaluated cohort: {n} companies in Norwegian corporate dataset</span></div>'
    body += '<div class="export-bar" aria-label="Export cohort data"><span class="export-label">Export Cohort:</span> <button type="button" id="export-dashboard-csv" class="btn-export">Export CSV</button> <button type="button" id="export-dashboard-json" class="btn-export">Export JSON</button></div>'
    body += '<div id="filter-scope-warning" class="filter-warning" hidden>⚠️ Filters active: metrics reflect <strong id="filter-scope-count">0</strong> matching companies. <button type="button" class="btn-link" id="reset-dashboard-filters">Clear filters to view full dataset</button></div>'
    body += '</div>'

    # Summary KPI cards
    web_count = sum(r['flags']['website'] for r in records)
    job_count = sum(r['jobs'] for r in records)
    hiring_comp = sum(r['flags']['jobs'] for r in records)
    act_count = sum(r['flags']['activity'] for r in records)

    body += '<div class="dashboard-metrics-grid">'
    body += f'<div class="metric-card" id="dash-card-companies"><div class="metric-header"><span class="metric-title">Evaluated Companies</span><span class="chip available">100% Cohort</span></div><div class="metric-value" id="dash-total-companies">{n}</div><div class="metric-desc">Total corporate entities evaluated in dataset</div></div>'
    body += f'<div class="metric-card" id="dash-card-websites"><div class="metric-header"><span class="metric-title">Verified Websites</span><span class="chip available" id="dash-websites-pct">{web_count / n * 100 if n else 0:.1f}%</span></div><div class="metric-value" id="dash-total-websites">{web_count}</div><div class="metric-desc">Official company sites verified by identity rules</div></div>'
    body += f'<div class="metric-card" id="dash-card-hiring"><div class="metric-header"><span class="metric-title">Active Hiring</span><span class="chip available" id="dash-hiring-companies">{hiring_comp} companies</span></div><div class="metric-value" id="dash-total-jobs">{job_count}</div><div class="metric-desc">Active job postings recalled from NAV stream</div></div>'
    body += f'<div class="metric-card" id="dash-card-activity"><div class="metric-header"><span class="metric-title">Recent Public Activity</span><span class="chip available" id="dash-activity-pct">{act_count / n * 100 if n else 0:.1f}%</span></div><div class="metric-value" id="dash-total-activity">{act_count}</div><div class="metric-desc">Entities with official filings or activity within 2 years</div></div>'
    body += '</div>'

    # Analytics grid
    body += '<div class="dashboard-analytics-grid">'
    body += '<div class="analytics-card">'
    body += '<h3>Website Source Provenance</h3>'
    body += '<p class="card-subtitle">Verified domains broken down by corroboration provenance category</p>'
    body += '<div id="provenance-breakdown" class="provenance-breakdown"></div>'
    body += '<p class="card-footer-note">All websites corroborated under strict identity resolution (organisation number, registry declared, or identity signals).</p>'
    body += '</div>'

    body += '<div class="analytics-card">'
    body += '<h3>Hiring Activity Timeline</h3>'
    body += '<p class="card-subtitle">Active job advertisements by publication date from official NAV stream</p>'
    body += '<div id="hiring-timeline" class="hiring-timeline-chart"></div>'
    body += '<p class="card-footer-note">Based on active NAV postings. Unlisted entities have no active jobs in the evaluation scope, not zero employment.</p>'
    body += '</div>'
    body += '</div>'

    body += '<div class="analytics-card full-width">'
    body += '<h3>Recent Verified Company Activity</h3>'
    body += '<p class="card-subtitle">Dated registry and verified company updates (most recent first)</p>'
    body += '<div id="recent-activity-list" class="recent-activity-list"></div>'
    body += '<p class="card-footer-note">Fetch failures and observation changes are excluded. Open a company receipt to inspect each dated source.</p>'
    body += '</div>'
    body += '</section>'

    # 2. Company Directory View
    body += '<section id="view-directory" class="directory-view" role="tabpanel" aria-labelledby="tab-directory" hidden>'
    body += '<div id="directory"></div>'
    body += '<div class="export-bar" aria-label="Export directory data"><span class="export-label">Export Directory:</span> <button type="button" id="export-directory-csv" class="btn-export">Export CSV</button> <button type="button" id="export-directory-json" class="btn-export">Export JSON</button></div>'
    body += '<div class="saved-views-bar" aria-label="Saved views and watchlist"><span class="saved-views-label">Saved Views:</span><div id="saved-views-list" class="saved-views-list"></div><button type="button" id="save-current-view" class="btn-sm">💾 Save view</button><button type="button" id="clear-watchlist" class="btn-sm">Clear watchlist</button><span class="storage-notice muted">Stored locally in your browser.</span></div>'
    body += '<section class="filters" aria-label="Company filters">'
    values_muni = sorted({str(r['municipality']) for r in records if r['municipality']})
    body += '<label>Municipality<select id="municipality"><option value="">All municipalities</option>' + ''.join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in values_muni) + '<option value="Unknown">Unknown municipality</option></select></label>'

    values_div = sorted({r['nace'][:2] for r in records if r['nace']})
    body += '<label>Industry (NACE)<select id="division"><option value="">All industries</option>' + ''.join(f'<option value="{esc(v)}">Division {esc(v)}</option>' for v in values_div) + '<option value="Unknown">Unknown industry</option></select></label>'

    body += '<label>Company size<select id="size-band"><option value="">All sizes</option>'
    body += '<option value="micro">Micro (1–9 employees)</option>'
    body += '<option value="small">Small (10–49 employees)</option>'
    body += '<option value="medium">Medium (50–249 employees)</option>'
    body += '<option value="large">Large (250+ employees)</option>'
    body += '<option value="zero">Zero (0 employees)</option>'
    body += '<option value="unknown">Unknown / Unreported</option>'
    body += '</select></label>'

    body += '<label>Sort<select id="sort"><option value="areas_found">Most data found</option><option value="name">Name A–Z</option><option value="claim_count">By claims</option><option value="score">By score</option><option value="revenue">Revenue</option><option value="employees">Employees</option></select></label>'
    body += '<label>Areas available<select id="area-filter"><option value="">Any area</option><option value="all">All five areas</option>'
    body += ''.join(f'<option value="{key}">{label}</option>' for key, label in [('brief','Company brief'),('financials','Latest financials'),('leadership','Who runs it?'),('workforce','Working here'),('activity','Recent activity')]) + '</select></label>'

    for key, label in [('website', 'Verified website'), ('jobs', 'Job ads'), ('social', 'Social profiles'), ('activity', 'Public activity'), ('incomplete', 'Failed or blocked sections')]:
        body += f'<label class="check"><input id="filter-{key}" type="checkbox">{label}</label>'
    body += '<label class="check"><input id="filter-watchlist" type="checkbox">⭐ Watchlist (<span id="watchlist-count">0</span>)</label>'
    body += '</section>'

    body += '<div id="active-filters-bar" class="active-filters-bar" hidden>'
    body += '<span class="filter-chips-label">Active filters:</span>'
    body += '<div id="active-filter-chips" class="active-filter-chips"></div>'
    body += '<button type="button" id="clear-filters" class="btn-clear-filters">Clear all filters</button>'
    body += '</div>'

    body += '<p id="result-count" role="status" aria-live="polite" class="result-count"></p>'

    body += '<div id="empty-results" class="empty-state" hidden>'
    body += '<h3>No companies match your search and filters</h3>'
    body += '<p>Try adjusting your search terms, searching for a 9-digit organisation number, or clearing active filters.</p>'
    body += '<button type="button" id="reset-empty-filters" class="btn-primary">Clear all filters</button>'
    body += '</div>'

    body += '<div id="results" class="results">'
    for r in records:
        body += '<article class="company no-js-company"><a href="c/'+esc(r['orgnr'])+'.html">'+esc(r['name'])+'</a> <small>'+esc(r['orgnr'])+'</small></article>'
    body += '</div><div class="pagination"><button id="previous" type="button">Previous</button><span id="page-label"></span><button id="next" type="button">Next</button></div>'
    body += '</section>'

    # 3. Hiring Explorer View
    body += '<section id="view-hiring" class="hiring-view" role="tabpanel" aria-labelledby="tab-hiring" hidden>'
    body += '<div class="hiring-header">'
    body += '<h2>Hiring Explorer</h2>'
    body += '<p class="muted">Active job postings recalled from Arbeidsplassen (NAV) public stream with verified company matching.</p>'
    body += '<div class="hiring-scope-box"><p><strong>Recalled job postings:</strong> Evaluated from NAV public stream. Unlisted companies have no active job postings recalled within this scope, which does not imply zero employment.</p></div>'
    body += '</div>'
    body += '<div class="hiring-filters-grid">'
    body += '<label>Job title keyword<input type="search" id="hiring-search-title" placeholder="Search job title (e.g. Utvikler, Konsulent)..." autocomplete="off"></label>'
    body += '<label>Company<input type="search" id="hiring-search-company" placeholder="Search company name or orgnr..." autocomplete="off"></label>'
    body += '<label>Published within<select id="hiring-filter-date"><option value="all">All publication dates</option><option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="90">Last 90 days</option></select></label>'
    body += '</div>'
    body += '<p id="hiring-count" class="result-count" role="status" aria-live="polite"></p>'
    body += '<div id="hiring-results" class="hiring-results"></div>'
    body += '<div id="hiring-empty" class="empty-state" hidden>'
    body += '<h3>No job postings match active filters</h3>'
    body += '<p>Zero results indicates no active job ads match your criteria in the evaluated cohort. This does not indicate zero employment.</p>'
    body += '</div>'
    body += '</section>'
    body += '<section id="sources" class="sources-note"><h2>Sources &amp; licences</h2><p>BRREG: NLOD 2.0. NAV: public feed terms. Wikidata and GLEIF: CC0. TED: EU Publications Office reuse terms. Company websites: access under robots.txt; no open licence assumed.</p><p>Data checked '+esc(max((r['last_checked'][:10] for r in records),default='Unknown'))+'. No language model or search engine was used.</p></section>'
    return page(title, body, kind='index')


def compare_page(title, records=()):
    body = '<header><p class="eyebrow">Side by side</p><h1>Compare companies</h1><p>Select up to four companies for side-by-side comparison across verified facts, scale, financials, and online presence.</p></header>'
    body += '<section class="filters compare-inputs-grid" aria-label="Company selectors">'
    for i in range(4):
        body += f'<label>Company {i + 1}<input type="search" id="company-{i}" list="company-options" autocomplete="off" placeholder="Enter company name or orgnr..."></label>'
    body += '<div class="compare-actions"><button type="button" id="clear-compare" class="btn-clear-filters">Clear all</button><button type="button" id="share-compare">Copy comparison link</button></div>'
    body += '</section><datalist id="company-options"></datalist>'
    body += '<p id="compare-status" role="status" class="compare-status"></p>'
    body += '<div id="comparison" class="comparison"></div>'
    if records:
        selected=[r for r in records if r['orgnr'] in {'922828172','919653477'}] or list(records[:2])
        body += '<noscript><section><h2>Company comparison</h2><p>JavaScript enhances company selection; all company facts and receipts remain readable below.</p><div class="comparison">'
        for r in selected:body += '<article class="compare-card"><h2><a href="c/'+esc(r['orgnr'])+'.html">'+esc(r['name'])+'</a></h2><p>'+esc(r['orgnr'])+'</p><p>Revenue: '+esc(value_text(r['revenue']))+'</p><p>Annual result: '+esc(value_text(r['annual_result']))+'</p><p>Employees: '+esc(value_text(r['employees']))+'</p></article>'
        body += '</div></section></noscript>'
    return page('Compare · ' + title, body, kind='compare')


def receipt_pages(row, title):
    """Readable, bounded source receipts with every evidence record retained."""
    org=row['organisation_number'];records={e['id']:e for e in row['evidence']}
    chunks=[];current=[];size=0;parts_by_claim={}
    for c in row['claims']:
        label=c.get('reasons',{}).get('label') or c['field'].replace('_',' ')
        fragments=[];part=''
        for eid in c.get('evidence_ids',[]):
            single={**c,'evidence_ids':[eid]}
            fragment=evidence_panel(single,records)
            if part and len((part+fragment).encode('utf-8'))>155000:fragments.append(part);part=''
            part+=fragment
        fragments.append(part)
        for n,fragment in enumerate(fragments):
            suffix='' if n==0 else '-'+str(n+1)
            key=c['id']+suffix
            entry='<article class="receipt" id="receipt-'+c['id'][:16]+suffix+'"><p class="eyebrow">The evidence behind the fact</p><h2>'+esc(label)+'</h2>'+value_html(c['value'])+fragment+'<p data-continuation="'+key+'"></p></article>'
            length=len(entry.encode('utf-8'))
            if current and size+length>200000:chunks.append(current);current=[];size=0
            current.append((key,entry));size+=length
            parts_by_claim.setdefault(c['id'],[]).append(key)
    if current:chunks.append(current)
    targets={key:'../e/'+org+'-'+str(i+1)+'.html#receipt-'+key[:16]+key[64:] for i,chunk in enumerate(chunks) for key,_ in chunk}
    files={}
    for i,chunk in enumerate(chunks):
        body='<p><a href="../c/'+org+'.html">Back to company</a></p>'
        for key,entry in chunk:
            parts=parts_by_claim[key[:64]]
            links=''.join('<a href="'+esc(targets[k])+'">Supporting sources '+str(n+1)+'</a> ' for n,k in enumerate(parts) if k!=key)
            body+=entry.replace('<p data-continuation="'+key+'"></p>','<p>'+links+'</p>')
        files['e/'+org+'-'+str(i+1)+'.html']=page('Sources - '+title,body,'../',kind='evidence')
    return files,{cid:targets[keys[0]] for cid,keys in parts_by_claim.items()}


def generate_site(input_path, out, title='Signalpost'):
    input_path, out = Path(input_path), Path(out)
    if input_path.resolve().is_relative_to(out.resolve()):
        raise ValueError('Site directory must not contain its source envelopes')
    input_rows = [normalize(json.loads(line)) for line in input_path.read_text(encoding='utf-8-sig').split('\n') if line.strip()]
    unique={}
    for row in input_rows:
        org=row['organisation_number']
        if org in unique and unique[org]!=row:raise ValueError('Conflicting duplicate company envelopes')
        unique[org]=row
    # A malformed identifier must not abort the whole site, and never becomes a filename.
    # Its terminal envelope stays in the JSON output; the site lists it in a batch notice.
    skipped=[r['organisation_number'] for r in unique.values() if not re.fullmatch(r'\d{9}', r['organisation_number'])]
    rows=[r for r in unique.values() if re.fullmatch(r'\d{9}', r['organisation_number'])]
    records = [index_record(r) for r in rows]
    payload = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    js_payload = payload.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    files = {'index.html': index_page(records, title, skipped), 'compare.html': compare_page(title,records),
             'data/index.json': payload + '\n', 'data/index.js': 'window.SIGNALPOST_INDEX = ' + js_payload + ';\n'}
    for row in rows:
        org=row['organisation_number']
        receipts,routes=receipt_pages(row,title)
        files.update(receipts)
        files['c/' + org + '.html'] = profile(row, title,routes)
        data=json.dumps(company_payload(row),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
        data=data.replace('</','<\\/').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
        files['c/'+org+'.data.js']='window.SIGNALPOST_EVIDENCE = '+data+';\n'
    for filename in ('site.css', 'site.js'): files['assets/' + filename] = (ASSETS / filename).read_text(encoding='utf8')
    for asset in (ASSETS/'fonts').iterdir():
        if asset.is_file():files['assets/fonts/'+asset.name]=asset.read_bytes()
    # Render everything before writes: template errors cannot leave half a new site.
    if any(len(content.encode('utf8')) >= 250_000 for path, content in files.items() if path.endswith('.html')):
        raise ValueError('Profile page exceeds 250 KB gate')
    for filename, content in files.items():
        target = out / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content,bytes):target.write_bytes(content)
        else:target.write_text(content, encoding='utf8', newline='\n')
    sizes = {filename: len(content if isinstance(content,bytes) else content.encode('utf8')) for filename, content in files.items()}
    return {'companies': len(rows), 'input_records':len(input_rows), 'pages': len(rows) + 2, 'skipped_invalid_identifiers': len(skipped), 'total_bytes': sum(sizes.values()),
            'evidence_pages':sum(path.startswith('e/') and path.endswith('.html') for path in files),
            'largest_page_bytes':max((size for path,size in sizes.items() if path.endswith('.html')),default=0),
            'largest_profile_data_bytes':max((size for path,size in sizes.items() if path.endswith('.data.js')),default=0),
            'largest_profile_bytes': max((size for path, size in sizes.items() if path.endswith('.html')), default=0)}
