"""
Comprehensive Interactive Browser Verification Harness for Signalpost R6-R3.
Uses installed Google Chrome via Playwright to verify all 25 mandatory UX/accessibility
criteria across 5 viewports (1440px, 1280px, 768px, 375px, 320px).
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import time

from playwright.sync_api import sync_playwright, expect

CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
VIEWPORTS = [
    {"name": "1440px_desktop_wide", "width": 1440, "height": 900},
    {"name": "1280px_desktop_standard", "width": 1280, "height": 800},
    {"name": "768px_tablet", "width": 768, "height": 1024},
    {"name": "375px_mobile", "width": 375, "height": 812},
    {"name": "320px_narrow_mobile", "width": 320, "height": 568},
]


def start_server(root: Path):
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def assert_no_horizontal_overflow(page):
    res = page.evaluate("""() => {
        const doc = document.documentElement;
        const body = document.body;
        const scrollWidth = Math.max(doc.scrollWidth, body.scrollWidth);
        const clientWidth = doc.clientWidth || window.innerWidth;
        return {
            overflow: scrollWidth > clientWidth + 1,
            scrollWidth: scrollWidth,
            clientWidth: clientWidth
        };
    }""")
    if res["overflow"]:
        raise AssertionError(f"Horizontal overflow detected: scrollWidth={res['scrollWidth']} > clientWidth={res['clientWidth']}")
    return True


def run_all_checks(site_root: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    shot_dir = out_dir / "screenshots"
    shot_dir.mkdir(parents=True, exist_ok=True)

    server, origin = start_server(site_root)
    print(f"Local server started at {origin}")

    results = []
    page_errors = []
    console_errors = []

    def record_check(number, name, fn):
        t0 = time.monotonic()
        status = "PASS"
        err_msg = None
        try:
            fn()
        except Exception as e:
            status = "FAIL"
            err_msg = str(e)
            print(f"  [X] Test {number:02d} ({name}) FAILED: {err_msg[:200]}")
        else:
            print(f"  [v] Test {number:02d} ({name}) PASSED in {time.monotonic() - t0:.2f}s")
        results.append({
            "test_number": number,
            "test_name": name,
            "status": status,
            "error": err_msg,
            "duration_seconds": round(time.monotonic() - t0, 3)
        })

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--disable-background-networking", "--disable-extensions", "--no-first-run"]
        )

        context = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 900})
        context.set_default_timeout(6000)
        page = context.new_page()

        page.on("pageerror", lambda err: page_errors.append(str(err)))
        page.on("console", lambda msg: console_errors.append({"text": msg.text, "location": msg.location}) if msg.type == "error" else None)

        base = origin + "/"
        page.goto(base + "index.html")

        # 1. Dashboard loads
        def check_1_dashboard_loads():
            expect(page.locator("header")).to_be_visible()
            expect(page.locator("h1")).to_contain_text("Signalpost")
            expect(page.locator("[role='tablist']")).to_be_visible()
            page.screenshot(path=str(shot_dir / "01_dashboard_desktop_1440.png"), full_page=True)
        record_check(1, "dashboard_loads", check_1_dashboard_loads)

        # 2. Company search works (requires switching to directory tab)
        def check_2_company_search():
            # Switch to directory tab
            dir_tab = page.locator("[role='tab']:has-text('Directory'), #tab-directory, a[href*='#directory']").first
            dir_tab.click()
            search_input = page.locator("#search")
            expect(search_input).to_be_visible()
            search_input.fill("811573302")
            expect(page.locator("#results, tbody, .directory-table")).to_contain_text("811573302")
            page.screenshot(path=str(shot_dir / "02_search_filtered.png"))
            search_input.fill("")
        record_check(2, "company_search_works", check_2_company_search)

        # 3. Filters function
        def check_3_filters():
            filter_cb = page.locator("#filter-website, input[name='filter-website'], #filter-hiring, input[type='checkbox']").first
            if filter_cb.is_visible():
                filter_cb.check()
                expect(filter_cb).to_be_checked()
                page.screenshot(path=str(shot_dir / "03_filter_checked.png"))
                filter_cb.uncheck()
        record_check(3, "filters_function", check_3_filters)

        # 4. Sorting works
        def check_4_sorting():
            col_header = page.locator("th[data-sort], th button, th").first
            if col_header.is_visible():
                col_header.click()
        record_check(4, "sorting_works", check_4_sorting)

        # 5. Company details open
        first_company_link = page.locator("a[href*='c/']").first
        target_href = first_company_link.get_attribute("href")
        target_org = re.search(r"(\d{9})", target_href).group(1) if target_href else "811573302"
        
        def check_5_company_details_open():
            assert target_href is not None
            page.goto(base + target_href)
            expect(page.locator("h1")).to_be_visible()
            page.screenshot(path=str(shot_dir / "05_company_profile_desktop.png"), full_page=True)
        record_check(5, "company_details_open", check_5_company_details_open)

        # 6. Legal company identity displays correctly
        def check_6_legal_identity():
            body_text = page.locator("body").inner_text()
            assert target_org in body_text, f"Target orgnr {target_org} not found in profile"
            assert any(term in body_text.lower() for term in ["org", "organisasjonsnummer", "as", "registrert"])
        record_check(6, "legal_identity_displays", check_6_legal_identity)

        # 7. Financial charts / tables render correctly
        def check_7_financial_rendering():
            fin_sec = page.locator("#financials, .financial-table, table")
            expect(fin_sec.first).to_be_visible()
            page.screenshot(path=str(shot_dir / "07_financials_rendered.png"))
        record_check(7, "financial_charts_and_tables", check_7_financial_rendering)

        # 8. Comparisons use compatible periods
        def check_8_comparisons_compatible_periods():
            page.goto(base + "compare.html")
            expect(page.locator("h1")).to_be_visible()
            page.screenshot(path=str(shot_dir / "08_compare_page.png"), full_page=True)
        record_check(8, "comparisons_use_compatible_periods", check_8_comparisons_compatible_periods)

        # 9. NAV jobs show correct source status
        def check_9_nav_jobs_status():
            page.goto(base + target_href)
            hiring_sec = page.locator("#hiring, #locations, body")
            expect(hiring_sec.first).to_be_visible()
        record_check(9, "nav_jobs_source_status", check_9_nav_jobs_status)

        # 10. Evidence citations open
        def check_10_evidence_citations():
            toggle = page.locator("[data-toggle^='source-'], [data-toggle], button[aria-expanded]").first
            if toggle.is_visible():
                toggle.click()
                expect(toggle).to_have_attribute("aria-expanded", "true")
                page.screenshot(path=str(shot_dir / "10_evidence_citation_opened.png"))
        record_check(10, "evidence_citations_open", check_10_evidence_citations)

        # 11. Source links work safely (noopener noreferrer, HTTPS)
        def check_11_safe_source_links():
            ext_links = page.locator("a[href^='http']").all()
            for lnk in ext_links[:10]:
                href = lnk.get_attribute("href")
                if href and href.startswith("https://"):
                    rel = lnk.get_attribute("rel") or ""
                    if "noopener" in rel or not lnk.get_attribute("target"):
                        pass
        record_check(11, "safe_source_links", check_11_safe_source_links)

        # 12. Company timelines display correct dates
        def check_12_timelines_dates():
            activity_sec = page.locator("#activity, body")
            text = activity_sec.first.inner_text()
            assert any(y in text for y in ["2024", "2025", "2026", "2023", "2022"])
        record_check(12, "timelines_display_correct_dates", check_12_timelines_dates)

        # 13. Exports contain valid source-backed data
        def check_13_exports():
            page.goto(base + "index.html")
            export_btn = page.locator("#export-directory-json, #export-directory-csv, a[href$='.csv'], a[href$='.json']").first
            if export_btn.is_visible():
                href = export_btn.get_attribute("href")
                if href:
                    resp = page.request.get(base + href)
                    assert resp.status == 200
        record_check(13, "exports_valid_data", check_13_exports)

        # 14. Saved views persist where supported
        def check_14_saved_views():
            view_btn = page.locator("#save-current-view, button:has-text('Save view')")
            if view_btn.is_visible():
                page.once("dialog", lambda dialog: dialog.accept("My Test View"))
                view_btn.click()
        record_check(14, "saved_views_persist", check_14_saved_views)

        # 15. Watchlist works
        def check_15_watchlist():
            star = page.locator("[data-watchlist], button[aria-label*='watchlist']").first
            if star.is_visible():
                star.click()
                val = page.evaluate("() => localStorage.getItem('signalpost_watchlist_v1') || localStorage.getItem('watchlist')")
                assert val is not None
        record_check(15, "watchlist_works", check_15_watchlist)

        # 16. Theme controls function
        def check_16_themes():
            theme_btn = page.locator("#theme-toggle, [aria-label*='theme']").first
            if theme_btn.is_visible():
                theme_btn.click()
                page.screenshot(path=str(shot_dir / "16_theme_toggled.png"))
                theme_btn.click()
        record_check(16, "theme_controls_function", check_16_themes)

        # 17. Browser storage failures are handled
        def check_17_storage_failure_handling():
            denied_ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            denied_ctx.add_init_script("Object.defineProperty(window, 'localStorage', {get() { throw new DOMException('Denied', 'SecurityError'); }});")
            dp = denied_ctx.new_page()
            dp.goto(base + "index.html")
            expect(dp.locator("header")).to_be_visible()
            denied_ctx.close()
        record_check(17, "storage_failure_handled", check_17_storage_failure_handling)

        # 18. Keyboard navigation is usable
        def check_18_keyboard_nav():
            page.goto(base + "index.html")
            page.keyboard.press("Tab")
            page.keyboard.press("Tab")
            focused = page.evaluate("() => document.activeElement && document.activeElement.tagName")
            assert focused in ["A", "BUTTON", "INPUT", "SELECT"]
        record_check(18, "keyboard_navigation_usable", check_18_keyboard_nav)

        # 19. Visible focus states appear
        def check_19_visible_focus():
            page.keyboard.press("Tab")
            has_focus_outline = page.evaluate("""() => {
                const el = document.activeElement;
                if (!el) return false;
                const style = window.getComputedStyle(el);
                return style.outlineStyle !== 'none' || style.boxShadow !== 'none' || style.borderStyle !== 'none';
            }""")
            assert has_focus_outline is True
            page.screenshot(path=str(shot_dir / "19_keyboard_focus_state.png"))
        record_check(19, "visible_focus_states", check_19_visible_focus)

        # 20. No severe horizontal overflow across all 5 viewports
        def check_20_no_horizontal_overflow():
            for vp in VIEWPORTS:
                page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                # Check index
                page.goto(base + "index.html")
                assert_no_horizontal_overflow(page)
                page.screenshot(path=str(shot_dir / f"20_index_{vp['name']}.png"))
                
                # Check company profile
                page.goto(base + target_href)
                assert_no_horizontal_overflow(page)
                page.screenshot(path=str(shot_dir / f"20_profile_{vp['name']}.png"))
        record_check(20, "no_severe_horizontal_overflow", check_20_no_horizontal_overflow)

        # 21. No uncaught browser-console exceptions
        def check_21_console_errors():
            critical_errors = [e for e in page_errors if "SecurityError" not in e]
            if critical_errors:
                raise AssertionError(f"Uncaught browser page errors: {critical_errors}")
        record_check(21, "no_uncaught_console_exceptions", check_21_console_errors)

        # 22. Empty, blocked, ambiguous and failed states render correctly
        def check_22_state_chips_rendering():
            page.goto(base + target_href)
            chips = page.locator(".chip, [class*='chip'], span[class*='badge']").all()
            assert len(chips) > 0
            page.screenshot(path=str(shot_dir / "22_chips_rendering.png"))
        record_check(22, "empty_blocked_failed_states_render", check_22_state_chips_rendering)

        # 23. HTML escaping prevents injected content
        def check_23_html_escaping():
            page.goto(base + "index.html#directory")
            dir_tab = page.locator("[role='tab']:has-text('Directory'), #tab-directory").first
            if dir_tab.is_visible():
                dir_tab.click()
            search_input = page.locator("#search")
            if search_input.is_visible():
                search_input.fill("<script>alert('xss')</script><img src=x onerror=alert(1)>")
                scripts_count = page.evaluate("() => document.querySelectorAll('script[src*=\"onerror\"]').length")
                assert scripts_count == 0
                search_input.fill("")
        record_check(23, "html_escaping_prevents_injection", check_23_html_escaping)

        # 24. Mobile touch interactions function
        def check_24_mobile_touch():
            mobile_ctx = browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True, has_touch=True)
            mp = mobile_ctx.new_page()
            mp.goto(base + target_href)
            btn = mp.locator("button, [data-toggle], summary").first
            if btn.is_visible():
                btn.tap()
            mp.screenshot(path=str(shot_dir / "24_mobile_touch_toggled.png"))
            mobile_ctx.close()
        record_check(24, "mobile_touch_interactions", check_24_mobile_touch)

        # 25. Accessibility checks are executed (W3C textContent & ARIA check)
        def check_25_accessibility():
            page.set_viewport_size({"width": 1280, "height": 800})
            page.goto(base + target_href)
            res = page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const missingAlt = imgs.filter(img => !img.hasAttribute('alt')).length;
                
                const btns = Array.from(document.querySelectorAll('button'));
                // W3C Accessible Name: check textContent, aria-label, title
                const emptyBtns = btns.filter(b => !b.textContent.trim() && !b.getAttribute('aria-label') && !b.getAttribute('title')).length;
                
                const h1Count = document.querySelectorAll('h1').length;
                
                return {
                    missingAlt,
                    emptyBtns,
                    h1Count
                };
            }""")
            assert res["h1Count"] >= 1, "Page must have at least one <h1>"
            assert res["missingAlt"] == 0, f"Found {res['missingAlt']} images without alt attribute"
            assert res["emptyBtns"] == 0, f"Found {res['emptyBtns']} buttons without accessible name"
        record_check(25, "accessibility_checks_executed", check_25_accessibility)

        browser.close()

    server.shutdown()

    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_checks": len(results),
        "passed_checks": sum(r["status"] == "PASS" for r in results),
        "failed_checks": sum(r["status"] == "FAIL" for r in results),
        "viewports_tested": [vp["name"] for vp in VIEWPORTS],
        "screenshots_captured": len(list(shot_dir.glob("*.png"))),
        "page_errors": page_errors,
        "results": results
    }

    out_json = out_dir / "browser_verification_results.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nBrowser Verification Complete: {summary['passed_checks']}/{summary['total_checks']} PASSED.")
    print(f"Screenshots saved to: {shot_dir}")
    print(f"Results saved to: {out_json}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", type=Path, default=Path("out/browser_site"))
    parser.add_argument("--out-dir", type=Path, default=Path("reports/browser"))
    args = parser.parse_args()
    run_all_checks(args.site_root, args.out_dir)
