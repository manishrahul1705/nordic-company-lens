# Identity resolution

The identity firewall prevents name similarity from authorizing another company's facts.

## Registry and accounts

Organisation numbers remain strings. Input normalization strips BOM, whitespace and embedded spaces, then checks nine ASCII digits and the mod-11 checksum. Invalid numbers make no requests.

Live identity and accounts must explicitly identify the requested company. Roles can identify their parent through the exact registry entity link. Subunits must report the requested `overordnetEnhet`. Accounts publish only exact-company `SELSKAP` records; consolidated `KONSERN` values are excluded.

## Websites

Free discovery considers at most 32 registrable-domain candidates from registry websites/emails, exact-employer NAV homepages, registered subunits, exact-organisation Wikidata nominations and legal-name domains. Registry and Wikidata website claims remain nominations until live website identity is independently established. Social/directory domains are excluded from candidate fetching.

Explicitly opted-in Brave search can nominate up to five additional domains after free discovery fails, only for a company with employees or latest revenue greater than zero. It gets one paid attempt per company within query/cost budgets. Search snippets never authorize facts; every candidate passes the same live ownership proof.

| Level | Publication rule |
|---|---|
| VERIFIED | Exact organisation-number ownership proof, including explicit JSON-LD identifiers; or the full legal name including suffix plus a registered phone, email, street address or postcode and city. A conflicting site-owner number on a checked page rejects the domain. |
| HIGH / REGISTRY_DECLARED | Legacy values; not produced by the current ownership scorer. Declarations alone do not establish ownership. |
| MEDIUM / LOW | Abstain. Several qualifying domains remain ambiguous unless the policy selects a unique exact-verified domain. |

Registry-declared websites use Tier A (link and content) when the legal name, with or without its suffix, appears on the site. Exact parent or registered-subunit org-number proof also establishes ownership. Tier B publishes only the registry-declared link when a registered phone, email, street address or role-holder corroborates it without the name. Other registry/email/subunit nominations need the legal name plus an independent registered contact category. Contact-only combinations were rejected after the Step 10 wrong-company audit. A postcode and street are one category.

The homepage and up to five same-domain contact/about/privacy pages are checked for nominated domains. A different owner, parked/default page, directory, or registry domain nominated by at least two other org numbers vetoes publication. Cross-domain redirects must identify the company. The unique-name-only domain rule was rejected after it accepted a different operator and parked/default sites; name guesses retain stronger ownership proof. Guesses are limited to four, after stronger candidates fail; investment, holding and housing-association names are skipped. Hidden text, arbitrary scripts and page instructions cannot establish ownership.

Social platforms are never fetched. Company profiles require a complete matching legal/registered-subunit name in the handle, excluding legal suffixes and trailing profile IDs. Shared company-path pages exclude template header/footer links. Profiles observed across different companies are suppressed for the whole run. Wikidata social identifiers additionally require the exact P2333 organisation number and retain their CC0 item provenance. Sharing, platform-root and personal links are excluded.

JSON-LD `sameAs` is read only from Organization/LocalBusiness records and supported business subtypes on verified pages. Person, Product and untyped records do not authorize profiles. A named organization object must match a registered company/subunit name. On shared company-path pages, the object URL must identify that same path. Every resulting profile still passes the handle and cross-company sharing checks.

## Job advertisements

NAV header employer names are discovery only. Normalize legal, known brand and subunit names, strip legal suffixes, and require a distinctive token of at least four letters. Distinctive-token overlap ranks candidate details by inverse header-token frequency; Norwegian and ASCII spelling variants converge. Names never authorize publication. The optional unranked reproduction mode uses full-phrase matching. Nameless headers fall back to unfiltered detail discovery within the same cap.

Publication requires detail `employer.orgnr` to equal the company organisation number or a verified subunit number. Record `matched_via` explicitly. A same-name employer with a different identifier is rejected. Only active, non-expired ads with valid dates and matching UUIDs qualify. Unknown trading names and names without distinctive tokens can leave coverage incomplete.

Verified company sites may also nominate individual postings on their own domain or linked Webcruiter, Teamtailor, Jobylon, ReachMee, Recman and Easycruit pages. A single JobPosting must have a title, publication date, future expiry and exact registered employer identifier. Names alone cannot authorize a job. Contradictory identifiers veto it. Multi-ad listings and careers landing pages are never published as jobs.

Registry-declared non-.no Tier A sites cannot rely on the brand/legal-name core alone when the publisher is a different legal entity or no Norwegian entity is identified. Without the company orgnr or a registered Norwegian contact/address on a captured page, publication is ambiguous with reason "group website". A captured About page identifying the exact Norwegian legal entity can supply supporting evidence. This guard also applies to carried-forward websites and derived content.
