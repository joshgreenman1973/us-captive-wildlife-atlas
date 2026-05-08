"""
Build the AZA-accredited facility dataset for the US Wildlife Atlas.

Scope: AZA-accredited US zoos and aquariums only. The USDA-licensed exhibitor
and dealer list was dropped because most of those facilities don't publish
their species inventories, and the list is heavily polluted with regulated
pet operations (kennels, catteries, puppy mills).

Inputs:
  data/aza-institutions.txt      — AZA-accredited US institutions (Name|City|ST)
  data/places_gazetteer.txt      — 2023 Census places gazetteer (city centroids)

Output:
  data/facilities.json           — geocoded AZA facility list
"""

import csv
import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def norm_city(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = re.sub(r"[.,]", "", s)
    s = re.sub(r"-", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+(city|town|village|cdp|borough|township|municipality)$", "", s)
    s = re.sub(r"^st ", "saint ", s)
    s = re.sub(r"^ft ", "fort ", s)
    s = re.sub(r"^mt ", "mount ", s)
    return s


MANUAL_GEO = {
    ("brooklyn", "NY"): (40.6782, -73.9442),
    ("bronx", "NY"): (40.8448, -73.8648),
    ("queens", "NY"): (40.7282, -73.7949),
    ("staten island", "NY"): (40.5795, -74.1502),
    ("manhattan", "NY"): (40.7831, -73.9712),
    ("honolulu", "HI"): (21.3099, -157.8581),
    ("la jolla", "CA"): (32.8328, -117.2713),
    ("san pedro", "CA"): (33.7361, -118.2922),
    ("west orange", "NJ"): (40.7987, -74.2390),
}


def load_gazetteer() -> dict:
    g = {}
    with open(DATA / "places_gazetteer.txt", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
            state = row["USPS"]
            name = row["NAME"]
            try:
                lat = float(row["INTPTLAT"])
                lon = float(row["INTPTLONG"])
            except (KeyError, ValueError):
                continue
            key = (norm_city(name), state)
            try:
                aland = float(row.get("ALAND", 0) or 0)
            except ValueError:
                aland = 0
            if key not in g or aland > g[key][2]:
                g[key] = (lat, lon, aland)
    return {k: (v[0], v[1]) for k, v in g.items()}


def geocode(city: str, state: str, gz: dict):
    nc = norm_city(city)
    if (nc, state) in MANUAL_GEO:
        return MANUAL_GEO[(nc, state)]
    if (nc, state) in gz:
        return gz[(nc, state)]
    for v in [nc.replace("saint ", "st "), nc.replace("st ", "saint "),
              nc.replace("mount ", "mt "), nc.replace("mt ", "mount ")]:
        if (v, state) in gz:
            return gz[(v, state)]
    for (gname, gstate), coord in gz.items():
        if gstate == state and gname.startswith(nc) and len(nc) >= 4:
            return coord
    return None


def load_aza():
    out = []
    with open(DATA / "aza-institutions.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 3:
                continue
            name, city, st = parts
            out.append({"name": name.strip(), "city": city.strip(), "state": st.strip()})
    return out


def main():
    print("Loading gazetteer...")
    gz = load_gazetteer()
    print(f"  {len(gz)} places")

    print("Loading AZA...")
    facilities = load_aza()
    print(f"  {len(facilities)} institutions")

    print("Geocoding...")
    geocoded = 0
    for f in facilities:
        coord = geocode(f["city"], f["state"], gz)
        if coord:
            f["lat"], f["lon"] = coord
            geocoded += 1
        else:
            f["lat"], f["lon"] = None, None
            print(f"  unmatched: {f['city']}, {f['state']} ({f['name']})")
    print(f"  {geocoded} / {len(facilities)} geocoded")

    # Spread same-coord facilities on a small ring
    coord_groups = defaultdict(list)
    for f in facilities:
        if f["lat"] is not None:
            coord_groups[(f["lat"], f["lon"])].append(f)
    for (lat, lon), group in coord_groups.items():
        if len(group) <= 1:
            continue
        for i, f in enumerate(sorted(group, key=lambda x: x["name"])):
            angle = 2 * math.pi * i / len(group)
            f["lat"] = round(lat + 0.0015 * math.cos(angle), 6)
            f["lon"] = round(lon + 0.0015 * math.sin(angle), 6)

    mappable = [f for f in facilities if f["lat"] is not None]
    out = {
        "generated": "2026-05-07",
        "source_dates": {"aza": "2026-05-07", "gazetteer": "2023"},
        "counts": {"total": len(facilities), "mapped": len(mappable)},
        "facilities": mappable,
    }
    (DATA / "facilities.json").write_text(json.dumps(out, indent=1))
    print(f"Wrote facilities.json with {len(mappable)} facilities")


if __name__ == "__main__":
    main()
