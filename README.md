# U.S. Captive Wildlife Atlas

Interactive map of every USDA-licensed exhibitor and dealer plus every AZA-accredited zoo and aquarium in the United States — ~2,500 facilities — with full transparency about what's missing and why.

**Live map:** https://joshgreenman1973.github.io/us-captive-wildlife-atlas/

There is no single official registry of wild animals held in captivity in the U.S. This atlas combines the most authoritative public datasets available and is honest about the gaps.

## What's on the map (Phase 1)

- **USDA Class C exhibitors** (~2,100) — zoos, aquariums, roadside zoos, drive-through safaris, educational exhibitors, circuses
- **USDA Class B dealers** (~600) — animal dealers
- **AZA-accredited institutions** (215) — zoos and aquariums meeting AZA's accreditation standards

## What's NOT on the map (and why)

See [methodology.html](https://joshgreenman1973.github.io/us-captive-wildlife-atlas/methodology.html) for full caveats. Briefly:

- **ZIMS (Species360)** data is excluded — institution-level publishing is prohibited by Species360's terms.
- **Privately held exotic animals** are mostly invisible. The 2022 Big Cat Public Safety Act registry (planned Phase 5) is the one exception.
- **Research lab animals** are tracked separately via APHIS annual reports.
- **AWA-excluded animals** (research-bred birds/rats/mice, fish, reptiles, amphibians, invertebrates) aren't itemized in USDA inspection reports.
- **Sanctuaries** that don't exhibit publicly may not require USDA licenses.

Locations are city-centroid only because the USDA's public list redacts street addresses.

## Sources

- [USDA APHIS Public Search Tool](https://www.aphis.usda.gov/awa/public-search) — active licensees & registrants Excel
- [AZA Institution Status directory](https://www.aza.org/inst-status)
- [2023 U.S. Census Gazetteer Files](https://www.census.gov/geographies/reference-files/2023/geo/gazetter-file.html) — city centroids

## Reproducing the dataset

```
python3 scripts/build_dataset.py
```

Reads `data/usda-licensees-raw.xlsx`, `data/aza-institutions.txt`, and `data/places_gazetteer.txt`; writes `data/facilities.json`.

## Roadmap

- **Phase 2** — AZA SSP/studbook participation lists (~500 managed species; highest-confidence species layer)
- **Phase 3** — Scrape "Our Animals" pages from the largest 50–100 zoos
- **Phase 4** — LLM-parse USDA inspection report PDFs for species observed
- **Phase 5** — Big Cat Public Safety Act registry + GFAS-accredited sanctuaries
