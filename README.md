# U.S. Captive Wildlife Atlas

Interactive map of every zoo and aquarium in the United States accredited by the Association of Zoos and Aquariums (AZA), 215 facilities, with species lists for 137 of them and notes on what's missing and why.

**Live map:** https://joshgreenman1973.github.io/us-captive-wildlife-atlas/

There is no single official registry of wild animals held in captivity in the U.S. This atlas combines public datasets and lists the gaps.

## What's on the map

- **AZA-accredited institutions** (215), each at street-level coordinates hand-curated from the zoo's published address
- **Species lists** for 137 of them, from each zoo's own animal pages or, where the zoo doesn't publish an A–Z list, its Wikipedia article. Every popup says which.
- **Named individuals** (243), from zoos' "meet our animals" pages and Ceta-Base for cetaceans
- **Recent events** (97 births, deaths, hatchings and transfers) from zoos' press and blog pages
- **Species Survival Plan (SSP) and Saving Animals From Extinction (SAFE) programs** for 48 species

## What's NOT on the map (and why)

See [methodology.html](https://joshgreenman1973.github.io/us-captive-wildlife-atlas/methodology.html) for full caveats. Briefly:

- **Non-AZA zoos and roadside facilities.** An earlier version included the 2,500+ exhibitors and dealers licensed by the U.S. Department of Agriculture (USDA). That list was dropped: it is full of regulated pet operations (kennels, catteries, puppy mills), and most non-AZA exhibitors don't publish their inventories.
- **ZIMS (Species360)** data is excluded — institution-level publishing is prohibited by Species360's terms.
- **Privately held exotic animals** are mostly invisible. The 2022 Big Cat Public Safety Act registry is planned for a later phase but not shown.

## Sources

- [AZA Institution Status directory](https://www.aza.org/inst-status)
- Each zoo's own animal pages, with Wikipedia as a fallback
- [2023 U.S. Census Gazetteer Files](https://www.census.gov/geographies/reference-files/2023/geo/gazetter-file.html) — city centroids, used only where no curated coordinate exists

## Reproducing the dataset

Run in this order; each step rewrites `data/facilities.json`:

```
python3 scripts/build_dataset.py
python3 scripts/build_species_index.py
python3 scripts/build_source_links.py
```

`build_dataset.py` reads `data/aza-institutions.txt`, `data/zoo-coordinates.json` and `data/places_gazetteer.txt` and writes `data/facilities.json`. `build_species_index.py` merges `data/zoo-species-raw.json` and `data/wikipedia-supplemental.json` into `data/species_index.json` and attaches species lists to the facilities. `build_source_links.py` adds each facility's source URLs.

## Roadmap

- Big Cat Public Safety Act registry and sanctuaries accredited by the Global Federation of Animal Sanctuaries (GFAS)
