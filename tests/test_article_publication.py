from datetime import datetime, timezone

import pytest

from signalpost.web.activity import article


NOW = datetime(2026, 11, 4, tzinfo=timezone.utc)
BODY = '<p>' + 'The company opened its new office and welcomed customers to the opening. ' * 3 + '</p>'


def page(metadata='', title='New office', body=BODY):
    return (f'<html><head><title>{title} | Example</title><meta property="og:site_name" content="Example">'
            f'{metadata}</head><body><article><h1>{title}</h1>{body}</article></body></html>').encode()


@pytest.mark.parametrize('metadata', [
    '<meta property="article:modified_time" content="2026-10-20">',
    '<script type="application/ld+json">{"dateModified":"2026-10-20"}</script>',
    '',
])
def test_modified_or_lastmod_only_is_not_publication(metadata):
    assert article(page(metadata), 'https://example.no/news/opening', NOW) is None


def test_product_under_aktuelt_is_rejected():
    metadata = '<script type="application/ld+json">{"@type":"Product","datePublished":"2026-10-20"}</script>'
    assert article(page(metadata), 'https://example.no/aktuelt/new-chair', NOW) is None


def test_real_article_datepublished_and_page_title():
    metadata = '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-20"}</script>'
    value, span = article(page(metadata), 'https://example.no/news/unrelated-slug', NOW)
    assert value['title'] == 'New office'
    assert value['date_source'] == 'datePublished'
    assert value['date'] == '2026-10-20'
    assert span in page(metadata).decode()


def test_listing_is_not_an_article():
    assert article(page(title='Se flere nyheter', body='<a href="/news/new">New</a>'), 'https://example.no/news', NOW) is None


@pytest.mark.parametrize('path', ['products/chair', 'shop/chair', 'kategori/news', 'tag/office', 'side/2'])
def test_non_news_paths_rejected(path):
    assert article(page('<meta property="article:published_time" content="2026-10-20">'), 'https://example.no/' + path, NOW) is None
