"""Layout numbers must neither veto ownership nor establish an entity card."""
import pytest
from signalpost.web.html import Page
from signalpost.web.proof import score, extract_entity_cards, owner_identifier_markup

ORG='990412375'
OTHER='943737207'
CONTEXT={'name':'Bergen Vaktmestertjenester AS'}
def prove(body):
    page=Page(('<html><body>'+body+'</body></html>').encode(),'https://bnv.no/personvernerklaering/')
    return score(page,ORG,CONTEXT,'registry_email',[])

@pytest.mark.parametrize('layout',[
 '<div id="gap-943737207"></div>',
 '<div class="gap-943737207"></div>',
 '<div data-owner="943737207"></div>',
 '<div ID=gap-943737207 DATA-orgnr=943737207></div>',
 '<style>#gap-943737207 { height: 943737207px; }</style>',
 '<div style="--owner:943737207"></div>',
])
def test_bnv_footer_layout_number_is_not_a_foreign_owner(layout):
    result=prove('<footer>Bergen Vaktmestertjenester AS Org.nr.: 990 412 375'+layout+'</footer>')
    assert result.level=='VERIFIED'
    assert not result.other_orgnrs

@pytest.mark.parametrize('identifier',[
 '<footer>Other owner Org.nr. 943737207</footer>',
 '<meta name="orgnr" content="943737207">',
 '<script type="application/ld+json">{"@type":"Organization","name":"Other Owner AS","vatID":"NO943737207MVA"}</script>',
])
def test_real_foreign_identifiers_still_veto(identifier):
    result=prove('<footer>Bergen Vaktmestertjenester AS Org.nr. 990412375</footer>'+identifier)
    assert OTHER in result.other_orgnrs
    if not identifier.startswith('<meta'):assert result.reason=='foreign_orgnr'

@pytest.mark.parametrize('identifier',[
 '<footer>Bergen Vaktmestertjenester AS Org.nr. 990412375</footer>',
 '<meta name="orgnr" content="990412375">',
 '<script type="application/ld+json">{"@type":"Organization","name":"Bergen Vaktmestertjenester AS","vatID":"NO990412375MVA"}</script>',
])
def test_real_own_identifiers_still_prove(identifier):
    assert prove(identifier).level=='VERIFIED'


def test_entity_card_layout_number_cannot_prove_ownership():
    cards=extract_entity_cards('<section id="gap-990412375"><style>#gap-990412375{}</style>Unrelated</section>')
    assert cards and not cards[0].matches_org(ORG)


def test_mask_preserves_offsets_and_json_strings():
    raw='<div id="gap-943737207">Org.nr. 990412375</div><script type="application/json">{"orgnr":"990412375","name":"id=943737207"}</script>'
    masked=owner_identifier_markup(raw)
    assert len(raw)==len(masked)
    assert 'id="gap-943737207"' not in masked
    assert '"orgnr":"990412375"' in masked
    assert '"name":"id=943737207"' in masked


def test_entity_card_visible_digits_with_nested_tags_still_match():
    cards=extract_entity_cards('<section>Org.nr. <b>990</b> <span>412</span> 375</section>')
    assert cards and cards[0].matches_org(ORG)
