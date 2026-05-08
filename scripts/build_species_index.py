"""
Build species → facilities index from data/zoo-species-raw.json
and merge with data/facilities.json.

For Phase 2 we attach a `species` array to each facility we have data for,
and write data/species_index.json mapping each canonical species name to
the list of facilities that hold it.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def norm_species(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9 -]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


# Coarse taxon classification by keyword; used for filter chips like "monkeys",
# "great apes", "big cats", "bears", etc.
TAXON_RULES = [
    ("Great apes",   r"\b(chimpanzee|bonobo|gorilla|orangutan|siamang|gibbon)\b"),
    ("Monkeys & lemurs", r"\b(monkey|lemur|tamarin|marmoset|baboon|mandrill|gelada|sifaka|colobus|guenon|saki|langur|loris|galago|bushbaby|aye aye|potto)\b"),
    ("Big cats",     r"\b(lion|tiger|leopard|jaguar|cheetah|cougar|puma|snow leopard|clouded leopard|ocelot|serval|caracal|fishing cat|sand cat|black-footed cat|pallas'?s? cat|mountain lion)\b"),
    ("Bears",        r"\b(bear|panda)\b"),
    ("Elephants",    r"\belephant\b"),
    ("Giraffes & rhinos", r"\b(giraffe|rhino|rhinoceros|hippo|hippopotamus)\b"),
    ("Wolves & dogs", r"\b(wolf|painted dog|maned wolf|fox|coyote|dingo|jackal)\b"),
    ("Penguins",     r"\bpenguin\b"),
    ("Reptiles",     r"\b(snake|python|boa|cobra|rattlesnake|alligator|crocodile|tortoise|turtle|lizard|monitor|iguana|gecko|skink|chameleon|gila monster|mamba)\b"),
    ("Birds of prey", r"\b(eagle|hawk|falcon|vulture|condor|owl|kestrel)\b"),
]


def taxon_for(name: str):
    n = name.lower()
    for label, pat in TAXON_RULES:
        if re.search(pat, n):
            return label
    return None


def main():
    raw = json.loads((DATA / "zoo-species-raw.json").read_text())
    facilities_doc = json.loads((DATA / "facilities.json").read_text())
    facilities = facilities_doc["facilities"]

    by_name = {f["name"]: f for f in facilities}

    species_index = {}  # norm_species -> {display, facilities[], taxon}
    facilities_with_species = 0

    for fac_name, sp_list in raw.items():
        if fac_name.startswith("_"):
            continue
        fac = by_name.get(fac_name)
        if not fac:
            print(f"WARN: facility not found in dataset: {fac_name!r}")
            continue
        fac["species"] = sorted(set(sp_list))
        facilities_with_species += 1
        for sp in sp_list:
            key = norm_species(sp)
            if not key:
                continue
            if key not in species_index:
                species_index[key] = {
                    "display": sp,
                    "facilities": [],
                    "taxon": taxon_for(sp),
                }
            if fac_name not in species_index[key]["facilities"]:
                species_index[key]["facilities"].append(fac_name)

    print(f"Facilities with species data: {facilities_with_species}")
    print(f"Unique species: {len(species_index)}")

    # Write back facilities.json with species attached
    facilities_doc["counts"]["facilities_with_species"] = facilities_with_species
    facilities_doc["counts"]["unique_species"] = len(species_index)
    facilities_doc["source_dates"]["zoo_species_scrape"] = "2026-05-07"
    (DATA / "facilities.json").write_text(json.dumps(facilities_doc, indent=1))

    # Write species index
    species_out = sorted(
        [{"key": k, **v} for k, v in species_index.items()],
        key=lambda s: s["display"],
    )
    (DATA / "species_index.json").write_text(json.dumps(species_out, indent=1))
    print(f"Wrote {DATA / 'species_index.json'}")

    # Coverage by taxon
    from collections import Counter
    tx = Counter(s["taxon"] for s in species_out)
    for k, v in tx.most_common():
        print(f"  {v:4d}  {k}")


if __name__ == "__main__":
    main()
