# Identity resolution

The identity firewall prevents name similarity from authorizing another company's facts.

## Registry and accounts

Organisation numbers remain strings. Input normalization strips BOM, whitespace and embedded spaces, then checks nine ASCII digits and the mod-11 checksum. Invalid numbers make no requests.

Live identity and accounts must explicitly identify the requested company. Roles can identify their parent through the exact registry entity link. Subunits must report the requested `overordnetEnhet`. Accounts publish only exact-company `SELSKAP` records; consolidated `KONSERN` values are excluded.

## Websites

At most 32 registrable-domain candidates come from registry websites/emails, exact-employer NAV homepages, registered subunits, exact-organisation Wikidata nominations and legal-name domains. Registry and Wikidata website claims remain nominations until live website identity is independently established. Social/directory domains are excluded from candidate fetching.

| Level | Publication rule |
|---|---|
| VERIFIED | Exact organisation-number ownership proof, including explicit JSON-LD identifiers; or the full legal name including suffix plus a registered phone, email, street address or postcode and city. A conflicting site-owner number on a checked page rejects the domain. |
| HIGH / REGISTRY_DECLARED | Legacy values; not produced by the current ownership scorer. Declarations alone do not establish ownership. |
| MEDIUM / LOW | Abstain. Several qualifying domains remain ambiguous unless the policy selects a unique exact-verified domain. |

The homepage and up to three same-domain contact/about/privacy pages are checked. Name-only matches remain ambiguous. Hidden text, arbitrary scripts, foreign owner numbers and page instructions cannot establish ownership. A matching phone without the full legal name cannot qualify a website.

Social platforms are never fetched. Company profiles require a complete matching legal/registered-subunit name in the handle, excluding legal suffixes and trailing profile IDs. Shared company-path pages exclude template header/footer links. Profiles observed across different companies are suppressed for the whole run. Wikidata social identifiers additionally require the exact P2333 organisation number and retain their CC0 item provenance. Sharing, platform-root and personal links are excluded.

## Job advertisements

NAV header employer names are discovery only. Normalize legal, known brand and subunit names, strip legal suffixes, and require a distinctive token of at least four letters. Distinctive-token overlap ranks candidate details by inverse header-token frequency; Norwegian and ASCII spelling variants converge. Names never authorize publication. The optional unranked reproduction mode uses full-phrase matching. Nameless headers fall back to unfiltered detail discovery within the same cap.

Publication requires detail `employer.orgnr` to equal the company organisation number or a verified subunit number. Record `matched_via` explicitly. A same-name employer with a different identifier is rejected. Only active, non-expired ads with valid dates and matching UUIDs qualify. Unknown trading names and names without distinctive tokens can leave coverage incomplete.
