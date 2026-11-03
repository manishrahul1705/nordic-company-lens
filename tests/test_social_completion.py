from signalpost.models.evidence import utc_now
from signalpost.runner import placeholder
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section,Source,add
from signalpost.web.html import Page
from signalpost.web.social import drop_shared,matches_profile,mentions_company,observed_profiles,profile_key


def envelope(org,name,url):
    row=placeholder(org,'test',utc_now());s=Section();src=Source('https://example.no',b'body','a'*64,utc_now())
    add(s,src,org,'identity','identity.legal_name',name,'/name')
    add(s,src,org,'website','social_profile.test',{'url':url},'/social')
    row.claims=s.claims;return row


def test_carried_profile_is_rechecked_against_current_registered_name():
    row=envelope('923609016','Example AS','https://facebook.com/othercompany')
    row.claims[-1].carried_forward=True
    drop_shared([row])
    assert not any(c.field.startswith('social_profile.') for c in row.claims)


def test_profile_observed_in_article_is_tracked_even_if_not_publishable():
    page=Page(b'<article><a href="https://facebook.com/example">Customer</a></article>','https://other.no/')
    assert observed_profiles(page)=={'https://facebook.com/example'}


def test_cross_platform_alias_of_shared_handle_is_dropped():
    first=envelope('923609016','Example AS','https://twitter.com/example')
    second=envelope('993578843','Second AS','https://instagram.com/second')
    second.run.refresh['website']={'observed_social_profiles':['https://x.com/example']}
    drop_shared([first,second])
    assert not any(c.field.startswith('social_profile.') for c in first.claims)
    assert any(c.field.startswith('social_profile.') for c in second.claims)


def test_facebook_page_name_is_usable_but_numeric_or_channel_ids_are_not():
    assert matches_profile('https://facebook.com/pages/Example/1234567',['Example AS'])
    assert not matches_profile('https://facebook.com/1234567',['1234567 AS'])
    assert not matches_profile('https://youtube.com/channel/Example',['Example AS'])
    assert profile_key('https://facebook.com/pages/Example/1234567')==profile_key('https://www.facebook.com/Example-1234567')


def test_company_news_name_match_ignores_legal_suffix_only():
    names=['Rolidbakken FUS Barnehage AS']
    assert mentions_company('Nyheter fra Rolidbakken FUS Barnehage',names)
    assert not mentions_company('Nyheter fra Diseth FUS Barnehage',names)


def test_carried_matching_handle_from_shared_footer_is_rejected(tmp_path):
    row=envelope('923609016','Rolidbakken FUS Barnehage AS','https://facebook.com/Rolidbakken-FUS-Barnehage-AS')
    blobs=BlobStore(tmp_path/'state');raw=b'<footer><a href="https://facebook.com/Rolidbakken-FUS-Barnehage-AS">Facebook</a></footer>'
    src=Source('https://fus.no/rolidbakken',raw,blobs.put(raw),utc_now());s=Section()
    add(s,src,'923609016','website','official_website',{'final_url':'https://fus.no','proof_page_url':src.url},'/proof')
    add(s,src,'923609016','website','social_profile.test',{'url':'https://facebook.com/Rolidbakken-FUS-Barnehage-AS'},'/social',source_class='company_owned')
    row.claims=[row.claims[0],*s.claims];row.evidence=s.evidence;row.claims[-1].carried_forward=True
    drop_shared([row],blobs)
    assert not any(c.field.startswith('social_profile.') for c in row.claims)
