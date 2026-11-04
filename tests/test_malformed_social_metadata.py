import json

import pytest

from signalpost.web.html import Page
from signalpost.web.social import observed_profiles, organization_social, profile_url
from tests.test_websites import execute_web, html, OUR


@pytest.mark.parametrize('url', ['https://[object Object]', 'https://[invalid',
                               'https://[not-an-ip]/profile'])
def test_invalid_bracketed_social_url_is_ignored(url):
    assert profile_url(url) is None


def test_observation_ledger_keeps_real_profiles_beside_broken_sameas():
    body={'@context':'https://schema.org','@type':'Organization','name':'Example AS',
          'sameAs':['https://[object Object]', 'https://facebook.com/example']}
    page=Page(('<script type="application/ld+json">'+json.dumps(body)+'</script>').encode(),
              'https://example.no/')
    assert observed_profiles(page)=={'https://facebook.com/example'}
    assert set(organization_social(page,{'name':'Example AS'}))=={'https://facebook.com/example'}


def test_broken_sameas_does_not_fail_verified_website(tmp_path,monkeypatch):
    metadata={'@context':'https://schema.org','@type':'Organization','name':'Example AS',
              'sameAs':['https://[object Object]','https://facebook.com/example']}
    body=html('Org.nr '+OUR,extra='<script type="application/ld+json">'+json.dumps(metadata)+'</script>')
    _,row,_,_=execute_web(tmp_path,monkeypatch,body=body)
    assert row['run']['sections']['website']=='available'
    assert not any(e['code']=='section_exception' for e in row['errors'])
    profiles=[c['value']['url'] for c in row['claims'] if c['field'].startswith('social_profile.') and c['availability']=='available']
    assert profiles==['https://facebook.com/example']
