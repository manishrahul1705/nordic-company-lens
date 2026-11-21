import asyncio
import time
from types import SimpleNamespace

import pytest

from signalpost.budget import SourceFailure
from signalpost.web.candidates import Candidate
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web.policy import normalize_url


def test_webvia_candidate_dns_encoding_failure_is_contained():
    # The mixed jury run failed the entire WEBVIA website section after a DNS
    # IDNA encoding error on a candidate. A malformed candidate is rejected.
    async def invalid_dns(host, port):
        raise UnicodeEncodeError('idna', host, 0, 1, 'bad label')

    async def check():
        http = WebsiteHttp(None, SimpleNamespace(dns_precheck=True, website_transient_retry=False),
                           SimpleNamespace(deadline=time.monotonic() + 10, check=lambda: None),
                           None, resolver=invalid_dns)
        with pytest.raises(SourceFailure) as exc:
            await http.precheck(Candidate('https://webvia.no/', 'webvia.no', 'legal_name_slug'), '935389232')
        assert exc.value.code == 'url_refused'

    asyncio.run(check())


def test_oversized_dns_label_is_not_nominated():
    # The descriptive page title produced this overlong WEBVIA name guess.
    assert normalize_url('https://webvia-norges-rimeligste-aktor-innen-skreddersydd-design-til-bedrifter.no/') is None
