"""
Tests for Feature F24: Multi-span evidence for dated activity cards.
Covers all 18 adversarial test requirements:
1. Two anchors with identical destination.
2. Three anchors with identical destination.
3. Relative and absolute equivalent destinations.
4. Tracking-query differences where safely normalizable.
5. Different destination URLs (rejected for safety).
6. Two neighboring article cards.
7. Nested unrelated links (rejected as ambiguous).
8. Undated card (rejected).
9. Multiple dates in card (rejected as ambiguous).
10. Company-group news versus company-specific news (foreign domain rejected).
11. Malformed HTML handled gracefully.
12. Missing headline / generic anchors.
13. Duplicate event URL deduplication.
14. Non-Norwegian / Latin-1 encoding handled cleanly.
15. Oversized text spans bounded within limits.
16. Evidence-anchor replay in accuracy_audit.py.
17. External domain link rejected.
18. Single-link card backward compatibility.
"""
from datetime import datetime, timezone
import pytest

from signalpost.web.activity import parse_html
from scripts.accuracy_audit import audit_activity_claim


NOW = datetime(2026, 10, 17, tzinfo=timezone.utc)
SOURCE_URL = 'https://example.no/nyheter'


def test_1_two_anchors_identical_destination():
    """Two anchors (thumbnail + headline) to same article URL are accepted."""
    body = (
        b'<article>'
        b'<a href="/nyheter/opening"><img src="/img/thumb.jpg" alt="Office"></a>'
        b'<h3><a href="/nyheter/opening">New office in Oslo</a></h3>'
        b'<time datetime="2026-10-15">15 October 2026</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    val, locator, span = items[0]
    assert val['title'] == 'New office in Oslo'
    assert val['url'] == 'https://example.no/nyheter/opening'
    assert val['date'] == '2026-10-15'
    assert '2026-10-15' in span


def test_2_three_anchors_identical_destination():
    """Three anchors (image, title, 'Les mer') to same URL choose headline title."""
    body = (
        b'<article>'
        b'<a href="/nyheter/expansion"><img src="/img/ex.jpg"></a>'
        b'<h2><a href="/nyheter/expansion">Nordic expansion announced</a></h2>'
        b'<time datetime="2026-09-20">20.09.2026</time>'
        b'<a href="/nyheter/expansion">Les mer</a>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    val, locator, span = items[0]
    assert val['title'] == 'Nordic expansion announced'
    assert val['url'] == 'https://example.no/nyheter/expansion'
    assert val['date'] == '2026-09-20'


def test_3_relative_and_absolute_equivalent_destinations():
    """Relative and absolute links to identical normalized target are accepted."""
    body = (
        b'<article>'
        b'<a href="/nyheter/merger">Read more</a>'
        b'<h2><a href="https://example.no/nyheter/merger">Merger completed</a></h2>'
        b'<time datetime="2026-08-01">01.08.2026</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    val, locator, span = items[0]
    assert val['title'] == 'Merger completed'
    assert val['url'] == 'https://example.no/nyheter/merger'
    assert val['date'] == '2026-08-01'


def test_4_tracking_query_differences_normalized():
    """Query parameters (e.g. UTM tracking) normalize to the same destination."""
    body = (
        b'<article>'
        b'<h2><a href="/nyheter/quarterly-results?utm_source=homepage">Q3 Results Strong</a></h2>'
        b'<p>Revenue increased by 15 percent.</p>'
        b'<a href="/nyheter/quarterly-results?ref=card">Les mer</a>'
        b'<time datetime="2026-10-10">10.10.2026</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    val, locator, span = items[0]
    assert val['title'] == 'Q3 Results Strong'
    assert val['url'] == 'https://example.no/nyheter/quarterly-results'
    assert val['date'] == '2026-10-10'


def test_5_different_destination_urls_rejected():
    """Cards containing differing destination URLs are rejected as ambiguous."""
    body = (
        b'<article>'
        b'<a href="/nyheter/first">First story</a>'
        b'<a href="/nyheter/second">Second story</a>'
        b'<time datetime="2026-10-15">15 October</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 0, "Conflicting URLs in single article must be rejected"


def test_6_two_neighboring_article_cards():
    """Two adjacent article cards in the same body are extracted as separate items."""
    body = (
        b'<section>'
        b'<article>'
        b'<h3><a href="/nyheter/first">First Story</a></h3>'
        b'<time datetime="2026-10-10">10 Oct</time>'
        b'</article>'
        b'<article>'
        b'<h3><a href="/nyheter/second">Second Story</a></h3>'
        b'<time datetime="2026-10-11">11 Oct</time>'
        b'</article>'
        b'</section>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 2
    assert items[0][0]['url'] == 'https://example.no/nyheter/first'
    assert items[1][0]['url'] == 'https://example.no/nyheter/second'


def test_7_nested_unrelated_link_causes_rejection():
    """Card containing an unrelated anchor (e.g. tag or author link) is rejected."""
    body = (
        b'<article>'
        b'<h2><a href="/nyheter/story">Tech breakthrough</a></h2>'
        b'<p>By <a href="/forfatter/jan">Jan Hansen</a></p>'
        b'<time datetime="2026-10-01">01.10.2026</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 0, "Card with multiple destination URLs must be rejected"


def test_8_undated_card_rejected():
    """Card missing a date tag is rejected."""
    body = (
        b'<article>'
        b'<h2><a href="/nyheter/undated">Undated press release</a></h2>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 0


def test_9_multiple_dates_in_card_rejected():
    """Card with multiple ambiguous date tags is rejected."""
    body = (
        b'<article>'
        b'<h2><a href="/nyheter/multi-date">Conference dates</a></h2>'
        b'<time datetime="2026-09-01">01 Sep</time>'
        b'<time datetime="2026-09-05">05 Sep</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 0


def test_10_foreign_domain_news_rejected():
    """Link pointing outside the company domain is rejected."""
    body = (
        b'<article>'
        b'<h2><a href="https://other-company.com/news/partner">Partner update</a></h2>'
        b'<time datetime="2026-10-01">01.10.2026</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 0


def test_11_malformed_html_handled_gracefully():
    """Malformed HTML with unclosed tags does not crash."""
    body = (
        b'<article>'
        b'<h2><a href="/nyheter/malformed">Broken HTML headline'
        b'<time datetime="2026-10-12">12 Oct 2026'
        b'</article>'
    )
    # Parser should safely parse or skip without throwing
    items = parse_html(body, SOURCE_URL, NOW)
    assert isinstance(items, list)


def test_12_generic_title_selection():
    """If one link is descriptive and another is 'Les mer', the descriptive one is chosen."""
    body = (
        b'<article>'
        b'<a href="/nyheter/award">Annual Innovation Award 2026</a>'
        b'<time datetime="2026-10-05">05.10.2026</time>'
        b'<a href="/nyheter/award">Les mer</a>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    assert items[0][0]['title'] == 'Annual Innovation Award 2026'


def test_13_duplicate_event_url_deduplicated():
    """Multiple article blocks pointing to the exact same URL are deduplicated."""
    body = (
        b'<article>'
        b'<h2><a href="/nyheter/same">Headline once</a></h2>'
        b'<time datetime="2026-10-01">01 Oct</time>'
        b'</article>'
        b'<article>'
        b'<h2><a href="/nyheter/same">Headline repeated</a></h2>'
        b'<time datetime="2026-10-01">01 Oct</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    assert items[0][0]['url'] == 'https://example.no/nyheter/same'


def test_14_non_utf8_encoding_handled_cleanly():
    """Latin-1 encoded HTML with Norwegian characters parses cleanly with replacement."""
    body = (
        b'<article>'
        b'<h2><a href="/nyheter/apning">\xc5pning av nytt kontor i Troms\xf8</a></h2>'
        b'<time datetime="2026-10-14">14.10.2026</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    assert 'kontor' in items[0][0]['title']


def test_15_oversized_text_span_bounded_within_300_chars():
    """Article cards bound evidence span within 300 characters."""
    filler = "A" * 400
    body = (
        f'<article>'
        f'<h2><a href="/nyheter/long">Important announcement</a></h2>'
        f'<p>{filler}</p>'
        f'<time datetime="2026-10-02">02.10.2026</time>'
        f'</article>'
    ).encode('utf-8')
    items = parse_html(body, SOURCE_URL, NOW)
    for val, loc, span in items:
        assert len(span) <= 300


def test_16_evidence_anchor_replay_accuracy_audit():
    """Accuracy audit script validates multi-link card claim as CORRECT."""
    body = (
        '<article>'
        '<a href="/nyheter/opening"><img src="/img/thumb.jpg" alt="Office"></a>'
        '<h3><a href="/nyheter/opening">New office in Oslo</a></h3>'
        '<time datetime="2026-10-15">15 October 2026</time>'
        '</article>'
    )
    claim = {
        'value': {
            'url': 'https://example.no/nyheter/opening',
            'title': 'New office in Oslo',
            'date': '2026-10-15',
            'date_source': 'datetime'
        }
    }
    ev = {
        'extraction_method': 'signalpost.activity.html.v1',
        'locator': '/article/0',
        'source_url': 'https://example.no/nyheter'
    }
    status, msg, dt = audit_activity_claim('999999999', claim, ev, body)
    assert status == 'CORRECT'
    assert 'co-occur' in msg
    assert dt == '2026-10-15'


def test_17_external_redirect_candidate_not_accepted():
    """News URL with external non-company domain is not accepted."""
    body = (
        b'<article>'
        b'<h2><a href="https://external-news.org/press/release">External News</a></h2>'
        b'<time datetime="2026-10-05">05 Oct</time>'
        b'</article>'
    )
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 0


def test_18_single_link_article_backward_compatibility():
    """Existing standard single-link format continues to pass unconditionally."""
    body = b'<article><a href="/nyheter/opening">New office</a><time datetime="2026-10-15">15 October</time></article>'
    items = parse_html(body, SOURCE_URL, NOW)
    assert len(items) == 1
    val, locator, span = items[0]
    assert val['title'] == 'New office'
    assert val['url'] == 'https://example.no/nyheter/opening'
    assert val['date'] == '2026-10-15'
