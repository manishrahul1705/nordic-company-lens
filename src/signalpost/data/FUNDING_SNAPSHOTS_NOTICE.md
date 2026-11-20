# Public funding snapshots ? NLOD 2.0

Contains data under [NLOD 2.0](https://data.norge.no/nlod/en/2.0) distributed by **Forskningsrådet** (research) and **Brønnøysundregistrene** (state aid).

- Research source: https://raw.githubusercontent.com/Forskningsradet/open-data/main/datasets/soknader2/dataset.csv
- State-aid source: https://stotte.brreg.no/nb/oppslag/stoettetildeling/totalbestand/csv

Each adjacent manifest records the original source URL/hash, retrieval date, row counts, selected columns, encoding and transformations. Our changes: select public corporate records/cells, filter funded/registered phases, group by exact organisation number, serialize selected cells as JSON in ZIP entries. These are derived indexes, not raw full downloads. Runtime evidence extracts identify their CSV data-record ordinal and full-dataset hash; no live freshness is asserted. Repository MIT does not replace the source data's NLOD terms.

Research excludes the newer Tibi system; coverage is a lower bound. Project amounts are whole-project awards, not exclusive company allocations or cash received. No collaborator attribution. Currency is not explicit in the CSV and is not inferred.

State aid retains actual instruments and recipient/subunit roles, not a blanket grants label. Registered aid elements are not necessarily loan/guarantee face values. No parseable robots file is served by the state-aid site; the official NLOD bulk distribution was explicitly authorized for development-only acquisition, not crawling. Missing or corrupt indexes and no matches do not prove no funding.
