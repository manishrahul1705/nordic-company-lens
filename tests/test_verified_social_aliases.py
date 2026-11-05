import pytest
from signalpost.web.html import Page
from signalpost.web.social import attributed

PROOF = {'identity_level': 'VERIFIED', 'final_url': 'https://northlight.no/'}
CONTEXT = {'name': 'Example Trading AS'}

@pytest.mark.parametrize('metadata,handle', [
    ('', 'northlight'),
    ('<meta property="og:site_name" content="Northern Lights">', 'northernlights'),
    ('<title>Northern Lights | Home</title>', 'northernlights'),
    ('<script type="application/ld+json">{"@type":"Organization","url":"https://northlight.no/","name":"Northern Lights","alternateName":"Aurora Shop"}</script>', 'aurorashop'),
])
def test_verified_site_alias(metadata, handle):
    page = Page(('<head>'+metadata+'</head><footer><a href="https://instagram.com/'+handle+'">Instagram</a></footer>').encode(), PROOF['final_url'])
    assert attributed(page, PROOF, CONTEXT)
    assert not attributed(page, {**PROOF, 'identity_level':'LOW'}, CONTEXT)

@pytest.mark.parametrize('metadata,handle', [
    ('<title>Home</title>', 'home'),
    ('<meta property="og:site_name" content="Parent Group">', 'parentgroup'),
    ('<title>Design Agency</title>', 'designagency'),
    ('<script type="application/ld+json">{"@type":"Organization","url":"https://other.no/","name":"Other"}</script>', 'other'),
    ('<script type="application/ld+json">{"@type":"Organization","url":"https://northlight.no/","name":"Northlight","parentOrganization":{"@type":"Organization","url":"https://northlight.no/","name":"Parent"}}</script>', 'parent'),
])
def test_unrelated_or_generic_alias_rejected(metadata, handle):
    page = Page(('<head>'+metadata+'</head><footer><a href="https://instagram.com/'+handle+'">Instagram</a></footer>').encode(), PROOF['final_url'])
    assert not attributed(page, PROOF, CONTEXT)

def test_shared_branch_cannot_use_parent_domain_alias():
    page = Page(b'<main><a href="https://instagram.com/northlight">Instagram</a></main>', 'https://northlight.no/example')
    assert not attributed(page, {**PROOF, 'proof_page_url':page.url}, CONTEXT)
