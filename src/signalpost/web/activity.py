"""Bounded dated news discovery on an already accepted company domain."""
from ..workers import offload

import html
import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlsplit, unquote

from ..budget import SourceFailure
from ..models.evidence import digest
from ..sources.extract import Section, add, response_source, missing
from .policy import domain, normalize_url
from .html import Page, json_values
from .social import path_scope, company_names, mentions_company

NEWS = re.compile(r'(?:nyheter|news|aktuelt|presse|blogg|blog|artikler|artikkel|arkiv)', re.I)
NON_ITEM = re.compile(r'/(?:author|authors|forfatter|kirjoittaja|category|kategori|tag|tags|page|feed)(?:/|$)', re.I)
GENERIC_TITLES = {'les mer', 'read more', 'se mer', 'mer', 'apne', 'vis mer', 'lenke', 'link', 'klikk her'}


def article(body, url, now, feed_date=None):
    """Validate the fetched article; discovery metadata is never publication proof."""
    if re.search(r'/(?:produkt\w*|products?|shop|kategori|category|tags?|archive|arkiv|side|page)(?:/|$)', urlsplit(url).path, re.I):
        return None
    page = Page(body, url)
    raw = page.raw
    if any(str(t).casefold() == 'product' for obj in page.jsonld for t in json_values(obj, '@type')):
        return None
    if re.search(r'add.to.cart|legg.{0,10}handlekurv|class=[\'\"][^\'\"]*(?:product-price|woocommerce)', raw, re.I):
        return None
    containers = re.findall(r'<(?:article|main)\b[^>]*>(.*?)</(?:article|main)\s*>', raw, re.I | re.S)
    if not containers or len(re.findall(r'<article\b', raw, re.I)) > 1:
        return None
    content = max(containers, key=len)
    paragraphs = re.findall(r'<p\b[^>]*>(.*?)</p\s*>', content, re.I | re.S)
    text = html.unescape(re.sub('<[^>]+>', ' ', ' '.join(paragraphs))).strip()
    if len(text) < 80:
        return None
    heading = re.search(r'<h1\b[^>]*>(.*?)</h1\s*>', content, re.I | re.S)
    title = page.meta.get('og:title') or (re.sub('<[^>]+>', '', heading[1]) if heading else '') or page.title
    site = page.meta.get('og:site_name', '')
    if site:
        title = re.sub(r'\s*[-|–:]\s*' + re.escape(site) + r'\s*$', '', title, flags=re.I)
    title = html.unescape(title).strip()
    if not title or len(title) > 200 or re.search(r'^(?:se flere nyheter|see more news|nyheter|news|aktuelt|arkiv|archive)$', title, re.I):
        return None
    candidates = [(v, 'datePublished') for obj in page.jsonld for v in json_values(obj, 'datePublished') if isinstance(v, str)]
    candidates.extend((v, 'article_time') for v in re.findall(r'<time\b[^>]*datetime\s*=\s*[\'\"]([^\'\"]+)', content, re.I))
    for token, origin in candidates:
        date = dated(token, now)
        if not date:
            continue
        # Publication dates must occur in the fetched article itself.
        position = raw.find(token) if token else -1
        if position < 0:
            continue
        span = raw[max(0, position - 40):position + len(token) + 40] if position >= 0 else None
        return ({'title': title, 'title_source': 'article_page', 'url': url, 'date': date,
                 'date_source': origin, 'identity_level': None}, span)
    return None


async def publish_articles(section, items, org, proof, http, checked, discovery_response=None):
    root = domain(proof.value['final_url'])
    for value, locator, span in items:
        scope = proof.value.get('company_path_scope')
        if scope and not (urlsplit(value['url']).path.startswith(scope+'/')):
            continue
        response = await http.get(value['url'], org, root)
        if response.status in {200, 404, 410}:
            checked.add(response.url)
        if response.status != 200 or domain(response.url) != root:
            continue
        checked.add(response.url)
        result = await offload(article, response.body, response.url, datetime.now(timezone.utc))
        if not result:
            continue
        actual, article_span = result
        if scope and not mentions_company(actual['title'],proof.value.get('company_scope_names', [])):
            continue
        actual.update(identity_level=proof.value['identity_level'], identity_claim_id=proof.id)
        if article_span is None:
            continue
        add(section, response_source(response), org, 'activity', 'dated_item.' + digest(actual['url'])[:20],
            actual, '/article', span=article_span, effective=actual['date'], source_class='company_owned', method='signalpost.activity.article.v1')
    if section.claims:
        section.state = 'available'


def local(tag):
    return tag.rsplit('}', 1)[-1].split(':')[-1]


def dated(value, now):
    try:
        try: date = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
        except ValueError: date = parsedate_to_datetime(value)
        if date.tzinfo is None: date = date.replace(tzinfo=timezone.utc)
        date = date.astimezone(timezone.utc)
        return date.date().isoformat() if datetime(2000, 1, 1, tzinfo=timezone.utc) <= date <= now + timedelta(days=2) else None
    except (ValueError, TypeError, OverflowError, AttributeError):
        return None


def parse(body, source_url, now):
    raw = body.decode('utf8', errors='replace')
    if re.search(r'<!\s*(?:DOCTYPE|ENTITY)', raw, re.I):
        raise ValueError('XML declarations refused')
    root = ET.fromstring(raw)
    kind = local(root.tag)
    if kind not in {'urlset', 'sitemapindex', 'rss', 'feed'}: raise ValueError('Unknown activity XML')
    items, children = [], []
    if kind == 'sitemapindex':
        for child in root:
            url = next((e.text for e in child if local(e.tag) == 'loc'), None)
            url = normalize_url(urljoin(source_url, url or '')) if url else None
            if url and domain(url) == domain(source_url): children.append(url)
        return [], sorted(set(children))
    tag = 'url' if kind == 'urlset' else 'item' if kind == 'rss' else 'entry'
    blocks = re.findall(r'<(?:[\w.-]+:)?' + tag + r'\b[^>]*>.*?</(?:[\w.-]+:)?' + tag + r'\s*>', raw, re.S)
    elements = [e for e in root.iter() if local(e.tag) == tag]
    # Unknown namespace/layout cannot invent a locator or snippet.
    if len(blocks) != len(elements): return [], []
    for n, (entry, block) in enumerate(zip(elements, blocks)):
        values = {local(e.tag): (e.text or '').strip() for e in entry}
        url = values.get('loc') if tag == 'url' else values.get('link')
        if tag == 'entry':
            url = next((e.get('href') for e in entry if local(e.tag) == 'link' and e.get('rel', 'alternate') == 'alternate'), None)
        url = normalize_url(urljoin(source_url, url or '')) if url else None
        if not url or domain(url) != domain(source_url) or not NEWS.search(urlsplit(url).path) or NON_ITEM.search(urlsplit(url).path): continue
        if re.fullmatch(r'/(?:[a-z]{2}/)?(?:nyheter|news|aktuelt|presse|blogg|blog|artikler|artikkel|arkiv)/?', urlsplit(url).path, re.I): continue
        field = next((f for f in ('lastmod', 'pubDate', 'published', 'updated') if values.get(f)), None)
        date = dated(values.get(field), now) if field else None
        # Sitemap/feed dates rank nominations only; the fetched article must
        # carry datePublished or a time tag before anything is published.
        if date is None: date = ''
        title = values.get('title')
        origin = 'feed title'
        if tag == 'url':
            title = re.sub(r'[-_]+', ' ', unquote(urlsplit(url).path.rstrip('/').rsplit('/', 1)[-1]))
            origin = 'title from URL'
        if not title or len(title) > 200: continue
        # Conservatively require one bounded verbatim span containing every
        # reported item token. Long or transformed values are abstentions.
        needles = [html.escape(url, quote=False)] + ([values[field]] if field else [])
        if tag != 'url': needles.append(html.escape(title, quote=False))
        ranges = []
        for token in needles:
            position = block.find(token)
            if position < 0: break
            ranges.append((position, position + len(token)))
        if len(ranges) != len(needles): continue
        start, end = min(a for a, _ in ranges), max(b for _, b in ranges)
        if end-start > 300: continue
        span = block[start:end]
        items.append(({'title': title, 'title_source': origin, 'url': url, 'date': date,
                       'date_source': field, 'identity_level': None}, f'/{tag}/{n}', span))
    unique = {item[0]['url']: item for item in sorted(items, key=lambda x: (x[0]['date'], x[0]['url']))}
    return sorted(unique.values(), key=lambda x: (x[0]['date'], x[0]['url']), reverse=True)[:10], []


async def fetch(org, envelope, http, pages):
    proof = next((c for c in envelope.claims if c.field == 'official_website' and c.availability == 'available'), None)
    if proof and proof.value.get('content_allowed') is False:
        return missing('activity', 'website_link_only', state='not_applicable')
    if not proof or proof.carried_forward or proof.value.get('identity_level') not in {'VERIFIED', 'HIGH', 'REGISTRY_DECLARED'}:
        website_state=envelope.run.sections.get('website')
        if website_state in {'failed','blocked','ambiguous'}:
            envelope.run.refresh.setdefault('activity', {})['website_news'] = {
                'state': website_state, 'complete': False, 'reason': 'website_check_incomplete'}
            return missing('activity','website_check_incomplete',state=website_state)
        envelope.run.refresh.setdefault('activity', {})['website_news'] = {
            'state': 'not_applicable', 'complete': False, 'reason': 'no_verified_website'}
        return missing('activity', 'no_verified_website', state='not_applicable')
    homepage = proof.value['final_url']
    context = {'name': next((c.value for c in envelope.claims if c.field == 'identity.legal_name' and c.availability == 'available'), ''),
               'subunits': [c.value for c in envelope.claims if c.field.startswith('subunits.unit.') and c.availability == 'available']}
    scope = path_scope(proof.value, context)
    # Local copy: diagnostics for news do not mutate the website identity claim.
    proof = proof.model_copy(deep=True)
    if scope:
        proof.value.update(company_path_scope=scope, company_scope_names=company_names(context))
    root = domain(homepage)
    feeds = []
    for response, page in pages:
        if domain(response.url) != root: continue
        head = re.search(r'<head\b[^>]*>(.*?)</head\s*>', page.raw, re.I | re.S)
        if not head: continue
        for tag in re.findall(r'<link\b[^>]*>', head.group(1), re.I):
            attrs = dict((k.lower(), html.unescape(v)) for k, _, v in re.findall(r'([\w-]+)\s*=\s*([\'"])(.*?)\2', tag, re.S))
            if attrs.get('type', '').lower() in {'application/rss+xml', 'application/atom+xml'} and 'alternate' in attrs.get('rel', '').lower():
                url = normalize_url(urljoin(response.url, attrs.get('href', '')))
                if url and domain(url) == root: feeds.append(url)
    maps = []
    for origin, parser in sorted(http.robots.items()):
        if domain(origin) == root:
            maps.extend(url for url in parser.site_maps() or [] if domain(url) == root)
    fallback_maps = [
        homepage.rstrip('/') + '/sitemap.xml',
        homepage.rstrip('/') + '/sitemap_index.xml',
        homepage.rstrip('/') + '/news-sitemap.xml',
        homepage.rstrip('/') + '/feed/'
    ]
    urls = [(url,0) for url in dict.fromkeys(sorted(set(maps))[:1] + sorted(set(feeds))[:1] +
            ([fallback_maps[0]] if not maps else []) + ([fallback_maps[-1]] if not feeds else []))]
    section = Section(state='not_available')
    checked=set()
    maximum = http.config.website_request_cap + 1
    http.activity_extra.add(org)
    try:
        seen = set()
        for _ in range(4):
            if not urls: break
            target,level = urls.pop(0)
            if target in seen:continue
            seen.add(target)
            if http.counts.get(org, 0) >= maximum: raise SourceFailure('website_budget_exhausted')
            response = await http.get(target, org, root, xml=True)
            if response.status in {200,404,410}:checked.add(response.url)
            if response.status in {404, 410}: continue
            if response.status in {401, 403, 429}: raise SourceFailure('http_blocked')
            if response.status != 200: raise SourceFailure('activity_fetch_error')
            try:
                items, children = await offload(parse,response.body,response.url,datetime.now(timezone.utc))
            except (ValueError, ET.ParseError):
                continue
            if children:
                if level == 0: urls.extend((child,1) for child in children[:1])
                continue
            await publish_articles(section, items[:2], org, proof, http, checked, response)
            if section.claims: section.state = 'available'
        if not section.claims:
            return await fetch_html(org, proof, http, pages, checked)
        return section
    except SourceFailure as exc:
        return missing('activity', exc.code, state='blocked' if exc.code in {'robots', 'robots_unavailable', 'http_blocked'} else 'failed')
    except (ValueError, ET.ParseError):
        return await fetch_html(org, proof, http, pages, checked)
    finally:
        http.activity_extra.discard(org)
        envelope.run.refresh.setdefault('activity', {})['checked_urls'] = sorted(checked)


def parse_html(body, source_url, now):
    """Accept only a dated, single-topic article card with a bounded verbatim span."""
    raw = body.decode('utf8', errors='replace')
    items = []
    seen = set()
    for n, match in enumerate(re.finditer(r'<article\b[^>]*>.*?</article\s*>', raw, re.I | re.S)):
        block = match.group()
        dates = re.findall(r'<time\b[^>]*\bdatetime\s*=\s*[\'"]([^\'"]+)[\'"]', block, re.I)
        if len(dates) != 1:
            continue
        links = re.findall(r'<a\b[^>]*\bhref\s*=\s*[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a\s*>', block, re.I | re.S)
        if not links:
            continue

        normalized_pairs = []
        for href, title_raw in links:
            u = normalize_url(urljoin(source_url, html.unescape(href)))
            if u:
                normalized_pairs.append((u, href, title_raw))

        if not normalized_pairs:
            continue

        unique_urls = {u for u, _, _ in normalized_pairs}
        if len(unique_urls) != 1:
            continue

        url = next(iter(unique_urls))
        date = dated(dates[0], now)
        if not date or not url or domain(url) != domain(source_url) or not NEWS.search(urlsplit(url).path) or NON_ITEM.search(urlsplit(url).path):
            continue
        if re.fullmatch(r'/(?:[a-z]{2}/)?(?:nyheter|news|aktuelt|presse|blogg|blog)/?', urlsplit(url).path, re.I):
            continue

        candidate_titles = []
        for u, href, title_raw in normalized_pairs:
            cleaned = html.unescape(title_raw.strip())
            if cleaned and '<' not in cleaned and len(cleaned) <= 200:
                if cleaned.casefold() not in GENERIC_TITLES:
                    candidate_titles.append((cleaned, href, title_raw.strip()))

        if not candidate_titles:
            if len(normalized_pairs) == 1:
                cleaned = html.unescape(normalized_pairs[0][2].strip())
                if cleaned and '<' not in cleaned and len(cleaned) <= 200:
                    candidate_titles.append((cleaned, normalized_pairs[0][1], normalized_pairs[0][2].strip()))
            if not candidate_titles:
                continue

        candidate_titles.sort(key=lambda x: len(x[0]), reverse=True)
        title, href_used, title_raw_used = candidate_titles[0]

        needles = [href_used, title_raw_used, dates[0]]
        ranges = [(block.find(t), block.find(t)+len(t)) for t in needles if block.find(t) >= 0]
        if len(ranges) != len(needles):
            continue
        start, end = min(a for a, _ in ranges), max(b for _, b in ranges)
        if end - start > 300:
            sub_needles = [title_raw_used, dates[0]]
            sub_ranges = [(block.find(t), block.find(t)+len(t)) for t in sub_needles if block.find(t) >= 0]
            if len(sub_ranges) == 2:
                s_start, s_end = min(a for a, _ in sub_ranges), max(b for _, b in sub_ranges)
                if s_end - s_start <= 300:
                    start, end = s_start, s_end
                else:
                    continue
            else:
                continue

        if url in seen:
            continue
        seen.add(url)
        items.append(({'title': title, 'title_source': 'article link', 'url': url,
                       'date': date, 'date_source': 'datetime', 'identity_level': None},
                      f'/article/{n}', block[start:end]))
    return items[:10]


async def fetch_html(org, proof, http, pages, checked):
    root = domain(proof.value['final_url'])
    section = Section(state='not_available')
    if proof.value.get('identity_level') != 'VERIFIED' or proof.value.get('other_orgnrs'):
        return section
    targets = []
    for response, page in pages:
        if domain(response.url) == root:
            targets.extend(link.href for link in page.links if NEWS.search(urlsplit(link.href).path))
    targets.extend(urljoin(proof.value['final_url']+'/', path) for path in ('nyheter', 'aktuelt', 'news', 'presse', 'blogg'))
    targets = [u for u in dict.fromkeys(map(normalize_url, targets)) if u and domain(u) == root]
    try:
        for target in targets[:2]:
            response = await http.get(target, org, root)
            if response.status != 200:
                continue
            checked.add(response.url)
            items = await offload(parse_html, response.body, response.url, datetime.now(timezone.utc))
            await publish_articles(section, items, org, proof, http, checked)
            if section.claims:
                section.state = 'available'
                break
        return section
    except SourceFailure as exc:
        return missing('activity', exc.code, state='blocked' if exc.code in {'robots', 'robots_unavailable', 'http_blocked'} else 'failed')
