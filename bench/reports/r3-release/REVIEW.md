# Every gained and lost website/social URL

Final source-data output from the detached release benchmark. No new social URLs. All gained URLs below were reviewed against saved sources; 3 correct, 0 wrong, 0 doubtful. Closva is a host alias, not an additional company. Istad retains the existing explicitly link-only Tier B semantics, not an assertion that its legal orgnr appears on the page.

| Orgnr | Legal name | URL | Exact proof type | Exact page text | Verdict / basis |
|---|---|---|---|---|---|
| 936629466 | CLOSVA AS | https://www.closva.com | jsonld_vatid | Owned by Closva AS · Org. no. 936 629 466 | correct: Same company/domain as baseline; www alias only. Footer explicitly identifies the exact legal owner and orgnr. |
| 911691248 | ISTAD ART SOLUTION NORWAY NUF | https://www.pederistad.no | registry_declared_hard_contact_tier_b | peder istad - Nyheter | correct: Exact registry-declared website; page identifies the registered role-holder Peder Istad. Existing Tier B declared link only: content_allowed=false, no inherited website facts/social/news published. This is not presented as orgnr/full-company-name ownership proof. |
| 936010695 | SIGMUND OLSEN AGENTUR AS | https://www.soa.no | orgnr_on_page | Sigmund Olsen Agentur AS; Org. nr: 936 010 695 | correct: Exact legal name and orgnr in the company footer, with registered street/phone corroboration. Common Crawl supplied only the candidate. |

## Every lost baseline URL

| Kind | Orgnr | Legal name | Baseline URL | Current outcome / reason |
|---|---|---|---|---|
| website_alias | 936629466 | CLOSVA AS | https://closva.com | Still available at https://www.closva.com; host alias only. |
| website | 934620011 | ENSURE IT AS | https://ensure-it.eu | Real declared website repeatedly returned website_timeout; final website failed. Not an ownership-rule rejection. |
| website | 979973969 | JAR HELSE AS | https://www.jarhelse.no | Ambiguous: full legal name absent for the old phone-only rule; suffix-free proof still enabled but requires two independent contacts and did not qualify. This earlier precision restriction is unchanged. |
| social | 979973969 | JAR HELSE AS | https://www.facebook.com/jarhelse | Ambiguous: full legal name absent for the old phone-only rule; suffix-free proof still enabled but requires two independent contacts and did not qualify. This earlier precision restriction is unchanged. |
| social | 979973969 | JAR HELSE AS | https://www.instagram.com/jarhelse | Ambiguous: full legal name absent for the old phone-only rule; suffix-free proof still enabled but requires two independent contacts and did not qualify. This earlier precision restriction is unchanged. |
| website | 999516386 | RISIKOKONSULENTEN AS | https://risikokonsulenten.no | Ambiguous: full legal name absent for the old phone-only rule; suffix-free proof still enabled but requires two independent contacts and did not qualify. This earlier precision restriction is unchanged. |
