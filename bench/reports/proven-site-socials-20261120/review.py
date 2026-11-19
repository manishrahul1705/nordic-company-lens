"""Case-specific notes after reading every newly proposed profile and source span."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from signalpost.web.html import Page
from signalpost.web.social import attributed,context_for_envelope,profile_key
from signalpost.web.social_links import veto
from signalpost.models.envelope import Envelope

out=Path(__file__).parent
base=Path('bench/runs/stage-ag-20261119')
run=Path('bench/runs/proven-site-socials-20261120')
new=json.loads((out/'new-profiles.json').read_text(encoding='utf-8'))
by_org=defaultdict(list)
for row in new:by_org[row['organisation_number']].append(row)
names={};owners=defaultdict(set);contexts={};proofs={};groups={}
for line in (run/'envelopes.jsonl').open(encoding='utf-8'):
    raw=json.loads(line);org=raw['organisation_number']
    names[org]=next((c['value'] for c in raw['claims'] if c['field']=='identity.legal_name'),'')
    for url in raw['run']['refresh'].get('website',{}).get('observed_social_profiles',[]):owners[profile_key(url)].add(org)
    if org in by_org:
        row=Envelope.model_validate(raw);contexts[org]=context_for_envelope(row)
        proofs[org]=next(c.value for c in row.claims if c.field=='official_website' and c.availability=='available')
        groups[org]=row.run.refresh.get('website',{}).get('entity_scope',{}).get('group_site',False)
notes={
 '995748983':'All three profiles are explicitly listed in repeated og:see_also metadata on MAAEMO’s proven homepage. They are restaurant handles, not role-person names; repeated metadata is retained rather than overwritten by the last meta tag.',
 '914248906':'The proven homepage presents Instagram/Facebook icon links with platform aria labels. Their ordinary Wix layout did not mark them as a footer, causing the former false exclusion. Neither is a personal role-holder handle.',
 '991368000':'The page links the studio account studioralstonbau. The handle names the studio, not either individual Ralston-Bau role holder. The CSS class jssocials-share-link does not turn a direct Instagram profile URL into a share/intent URL.',
 '987564911':'The proven homepage labels the numeric Facebook URL “Facebook” and records it as a social_link click. The identity-bearing id is preserved; it is not accepted from name matching or treated as a platform homepage.',
 '931069373':'The homepage links the Facebook page-form slug Fjelde-Teknikk-As plus page ID. It names the company, not role-holder Alexander Fjelde. The new /p/ form is preserved with its numeric identity.',
 '932448459':'The proven ROMERIKE VVS homepage directly links the Romerike-VVS Facebook /p/ page and ID. It is a company page form, not a personal LinkedIn or share URL.',
 '893948112':'The proven organisation homepage directly lists its Audiences Norway/Norsk Publikumsutvikling accounts and YouTube channel. The translated brand handles and opaque channel ID are supported by the site links, with no platform request or invented name match.',
 '936855865':'The proven JAKI.I homepage presents this exact Facebook profile.php id with aria-label Facebook. Identity is the numeric id, retained in the canonical URL; neither registered individual’s name is used as the handle.',
 '926490060':'The proven homepage explicitly labels LinkedIn and Twitter icons. The numeric LinkedIn /company/ ID and abbreviated ControlSolutio7 are company-linked identifiers, distinct from Richard Giske and Thomas Høybakk Nybø.',
 '987895276':'The company footer explicitly says Følg oss på Facebook and names Conplan in the page URL. It also appears on /kontakt. The body-level Squarespace tweak-share-buttons setting is not a local share widget and no longer excludes the footer.',
 '934982762':'ARKIDAL’s proven homepage labels this Facebook numeric-id URL as a footer-social-link. The URL is retained as a page identifier; it is not attributed through any person’s name.',
 '998236002':'The proven company homepage’s own Organization sameAs block supplies this YouTube channel. Its opaque ID is accepted only as a proven-site declaration. The separate Instagram martehallem is rejected against Marte Heie Hallem’s role record, including the omitted-middle-name variant.',
 '924458100':'The homepage’s own Organization sameAs declaration identifies Cannonball DMC Instagram and YouTube accounts. The DMC brand differs from the legal suffix but the proven-site declaration is the evidence. Neither handle matches a company role person.',
 '993014591':'STØREN DYREKLINIKK’s proven homepage explicitly labels the numeric Facebook link Besøk vår Facebook-side. Query id is retained, and tracking parameters do not become identity.',
 '811888672':'The proven Fusa homepage exposes facebook.com/fusamek as its Facebook social icon. The abbreviated handle is no longer rejected for failing the full legal name. It does not match a Groth/Kirkhorn role holder.',
 '977107385':'The proven ISOK homepage lists Facebook IndreSaltenOK, Instagram isok_as and TikTok isok2312 with Follow labels. These are organisation abbreviations linked by the company, not the listed role-person names.',
 '912189465':'LUCKY VIEW’s proven homepage directly links the YouTube @Loff account in its footer/navigation. This is a brand-channel link from the proven site; no handle/legal-name equality is assumed.',
 '996979660':'The proven dairy homepage lists Valdresost Facebook and Instagram links in its menu-some region. The product brand is established as a site-linked social account, not inferred from legal-name similarity.',
 '922828172':'The proven TENSIO homepage explicitly labels tensionett links Besøk vår facebook/instagram/x. None matches a role-person or another cohort company name, and the frozen cohort observation ledger finds no second owner for these profile keys. The old legal-handle test is intentionally replaced here.',
 '989145509':'The /contact/ page explicitly labels the LinkedIn company link Linkedin. WordPress wraps this ordinary contact page in article.page.type-page; that wrapper is not an editorial article or share control.',
 '936010695':'The proven SOA homepage declares facebook.com/soa.no in its own Organization/social metadata and page content. The acronym is supported by the proven site rather than matched to Sigmund Olsen Agentur’s full name.',
 '930166030':'The proven PLUMP homepage links plumposlo through its list-social element. The Oslo brand suffix does not invalidate a company-owned-site declaration; no role-person name matches.',
 '918486666':'The proven ANTISINK homepage labels the Antisink-Systems Facebook /p/ URL as a footer social link. Its page ID and company-labelled slug are retained.',
 '971558415':'DANSEINFORMASJONEN’s proven homepage directly links the Scenehuset Facebook and Instagram accounts. Under the requested rule these are site-declared brand/venue accounts, not claims that the handle equals the legal company name. Both survive cohort/group and person vetoes.',
 '935861144':'The proven D-PRODUCTION homepage presents this numeric Facebook URL through an aria-labelled Facebook social icon. The id identifies the declared profile without inferring it from Didrik Damm or Ask Jul-Andersen.',
 '952785052':'The proven horse centre homepage directly links facebook.com/nsnl2. The abbreviation is supported by the company-site link, not a legal-name expansion guessed by the extractor.',
 '993347728':'The proven TO-BE-MORE homepage’s own Organization sameAs lists the YouTube channel. The view_as query is non-identifying and removed; the channel ID is retained. No platform visit is needed.',
 '971492325':'The proven museum homepage labels this numeric Facebook id Gå til facebook. This own-site source is independent of its conflicting Wikidata website/date facts; those earlier disagreements remain recorded.',
 '980362779':'RENTHALL’s proven homepage links its Renthallgroup LinkedIn and declares RentHallGlobal X / hallmakergroup Instagram in its own Organization sameAs block. These are site-declared brand/group-named handles. Existing group-site and shared-cohort vetoes were evaluated and did not flag this proven site; this does not assert exclusivity beyond the cohort.',
 '984133715':'The proven OsloBilutleie homepage explicitly labels the OsloBilutleieAlna Facebook link. The location suffix is a site-declared account label, not a different person’s profile.',
 '981058771':'The homepage embeds Facebook’s versioned page plugin with an encoded href to facebook.com/storhamarsenteret. The retained verbatim iframe span contains that encoded identity. The plugin is a page widget, not a share button, video or tracking pixel.',
}
reviewed=[];lines=['# Proven-site social links: every new profile reviewed','',
    'Controlled replay of the frozen 1,000, using the same 302 accepted saved pages and zero HTTP. Every newly published profile is listed below. '
    'Each source hash and verbatim span is checked against the retained Stage AG blob; the website ownership proof is preserved. '
    'The acceptance decision uses the requested proven-site-link rule plus role-person, cohort-company, shared-profile and group-site vetoes. '
    'This verifies a company-site declaration, not live platform availability or exclusive legal ownership of a brand account outside the cohort.','',
    '| Company | Published profile | Cited page and evidence | Review |','|---|---|---|---|']
cache={}
for item in new:
    org=item['organisation_number'];url=item['claim']['value']['url']
    context=contexts[org];context['other_company_names']=[name for n,name in names.items() if n!=org]
    assert not veto(url,context),(org,url,'person/cohort veto')
    assert len(owners[profile_key(url)])<=1,(org,url,'shared')
    assert not groups[org],(org,url,'group site')
    citations=[]
    for ev in item['evidence']:
        sha=ev['content_sha256']
        if sha not in cache:cache[sha]=(base/'state/blobs'/sha).read_bytes()
        body=cache[sha]
        assert hashlib.sha256(body).hexdigest()==sha
        page=Page(body,ev['source_url'])
        assert ev['claim_span'] in page.raw and len(ev['claim_span'])<=300
        assert url in attributed(page,proofs[org],context),(org,url,'not actually linked')
        citations.append(f"[Saved page]({ev['source_url']})<br>SHA-256 `{sha}`<br>`{ev['locator']}`")
    note=notes[org]
    item={**item,'verdict':'correct_under_proven_site_link_rule','why_correct':note,
          'veto_checks':{'role_person':False,'other_cohort_company':False,'shared_profile':False,'group_site':False},
          'reviewed_against_retained_bytes':True}
    reviewed.append(item)
    cell=lambda s:str(s).replace('|','&#124;').replace('\n','<br>')
    lines.append('| '+' | '.join(cell(x) for x in (f"{item['company']} ({org})",f'[{url}]({url})','<br>'.join(citations),note))+' |')
assert len(reviewed)==json.loads((out/'measurement.json').read_text(encoding='utf-8'))['new_profiles']
(out/'REVIEW.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')
(out/'reviewed.json').write_text(json.dumps(reviewed,indent=2,ensure_ascii=False),encoding='utf-8')
print('Reviewed',len(reviewed),'new profiles across',len(by_org),'companies; all source/veto assertions passed')
