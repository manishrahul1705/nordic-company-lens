"""
Regression tests for:
- V6-07: Distinguish cookie consent metadata from active captcha blocks in website proof scoring.
- V6-08: NAV employer homepage handoff into website discovery.
"""
import pytest

from signalpost.web.html import Page
from signalpost.web.proof import score, Proof


def test_v6_07_cookie_consent_with_recaptcha_is_not_blocked():
    """
    V6-07: A page with under 1,000 visible characters mentioning googleRecaptcha
    in cookie consent scripts must not be falsely marked BLOCKED.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Wågnes Legekontor - Fastlege i Ålesund</title>
      <script>
        var cookieConsent = { services: ["googleAnalytics", "googleRecaptcha"] };
      </script>
    </head>
    <body>
      <header><h1>Wågnes Legekontor</h1></header>
      <main>
        <p>Velkommen til vårt legekontor. Vi tilbyr allmennmedisinske tjenester.</p>
        <p>Åpningstider: Mandag - Fredag 08:00 - 15:30.</p>
        <p>Adresse: Notenesgata 1, 6002 Ålesund.</p>
        <p>Org.nr: 971 117 826</p>
      </main>
      <footer>
        <p>Copyright 2026 Wågnes Legekontor. Org nr 971 117 826 MVA</p>
      </footer>
    </body>
    </html>
    """
    page = Page(html.encode("utf-8"), "https://waagnes.no/")
    context = {"name": "WÅGNES LEGEKONTOR AS"}

    # Visible text is ~350 characters (well under 1,000 characters)
    assert len(page.visible.strip()) < 1000
    assert "googlerecaptcha" in page.raw.lower()

    proof = score(page, "971117826", context, "seed", [])

    # Must NOT be BLOCKED
    assert proof.level != "BLOCKED"
    assert proof.reason != "block_page"
    assert proof.level in {"VERIFIED", "HIGH", "STRUCTURED"}


def test_v6_07_real_active_captcha_interstitial_is_blocked():
    """
    An active challenge page (e.g. Cloudflare Turnstile, captcha challenge title, or challenge instructions)
    must still be strictly marked BLOCKED.
    """
    # Cloudflare challenge
    cf_html = """
    <html><head><title>Just a moment...</title></head>
    <body>
      <div id="cf-chl-widget">Please wait while we verify your browser...</div>
    </body></html>
    """
    p1 = Page(cf_html.encode("utf-8"), "https://blocked.no/")
    res1 = score(p1, "923609016", {"name": "Test"}, "seed", [])
    assert res1.level == "BLOCKED"
    assert res1.reason == "block_page"

    # Captcha title challenge
    cap_html = """
    <html><head><title>Bot Check - Captcha Challenge</title></head>
    <body>
      <form action="/verify">
        <p>Complete the captcha to proceed to website.</p>
      </form>
    </body></html>
    """
    p2 = Page(cap_html.encode("utf-8"), "https://challenge.no/")
    res2 = score(p2, "923609016", {"name": "Test"}, "seed", [])
    assert res2.level == "BLOCKED"
    assert res2.reason == "block_page"
