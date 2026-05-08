"""
Compute per-zoo source URLs (Wikipedia article URL + best-guess animals page
on the zoo's own site) and attach them to each facility in facilities.json.

The Wikipedia URL is computed from the zoo name; we don't fetch to verify, so
some less-prominent institutions may 404 on that link. The zoo's own animals
page is taken from data/zoo-homepages.json where curated; otherwise it falls
back to a Google site-search URL keyed by zoo name.
"""
import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


# Manual overrides for Wikipedia article titles where the zoo name doesn't
# match the article slug.
WIKI_OVERRIDES = {
    "Bronx Zoo/WCS": "Bronx_Zoo",
    "Smithsonian's National Zoo and Conservation Biology Institute": "National_Zoological_Park_(United_States)",
    "Indianapolis Zoological Society, Inc.": "Indianapolis_Zoo",
    "Houston Zoo, Inc.": "Houston_Zoo",
    "Mesker Park Zoo & Botanic Garden, Inc.": "Mesker_Park_Zoo_%26_Botanic_Garden",
    "Detroit Zoological Society": "Detroit_Zoo",
    "Denver Zoo Conservation Alliance": "Denver_Zoo",
    "Saint Louis Zoo": "Saint_Louis_Zoo",
    "Chicago Zoological Society": "Brookfield_Zoo",
    "John G. Shedd Aquarium": "Shedd_Aquarium",
    "Brookfield Zoo Chicago": "Brookfield_Zoo",
    "BREC's Baton Rouge Zoo": "Baton_Rouge_Zoo",
    "Lee G. Simmons Conservation Park & Wildlife Safari": "Lee_G._Simmons_Wildlife_Safari_Park",
    "Omaha's Henry Doorly Zoo & Aquarium": "Henry_Doorly_Zoo_and_Aquarium",
    "Disney's Animal Kingdom": "Disney%27s_Animal_Kingdom",
    "Maryland Zoo in Baltimore": "Maryland_Zoo_in_Baltimore",
    "Cincinnati Zoo and Botanical Garden": "Cincinnati_Zoo_and_Botanical_Garden",
    "Columbus Zoo & Aquarium": "Columbus_Zoo_and_Aquarium",
    "Audubon Aquarium & Insectarium": "Audubon_Aquarium_of_the_Americas",
    "Audubon Zoo": "Audubon_Zoo",
    "Trevor-Lovejoy Zoo": "Trevor_Zoo",
    "Buttonwood Park Zoo": "Buttonwood_Park_Zoo",
    "Walter D. Stone Memorial Zoo": "Stone_Zoo",
    "ZooTampa at Lowry Park": "ZooTampa_at_Lowry_Park",
    "Connecticut's Beardsley Zoo": "Connecticut%27s_Beardsley_Zoo",
    "Saginaw Children's Zoo": "Saginaw_Children%27s_Zoo",
    "ZOOAMERICA NA Wildlife Park": "ZooAmerica",
    "The Maritime Aquarium at Norwalk, Inc.": "The_Maritime_Aquarium_at_Norwalk",
    "Bailey-Matthews National Shell Museum & Aquarium": "Bailey-Matthews_National_Shell_Museum",
    "Brookgreen Gardens": "Brookgreen_Gardens",
    "Northeastern Wisconsin (NEW) Zoo": "NEW_Zoo",
    "Steinhart Aquarium": "Steinhart_Aquarium",
    "Greater Vancouver Zoo": "Greater_Vancouver_Zoo",
    "California Science Center": "California_Science_Center",
    "Living Coast Discovery Center": "Living_Coast_Discovery_Center",
}


def wiki_slug_for(name: str) -> str:
    if name in WIKI_OVERRIDES:
        return WIKI_OVERRIDES[name]
    # Otherwise: replace spaces with underscores, leave punctuation as-is
    return urllib.parse.quote(name.replace(" ", "_"), safe="_,()")


def main():
    fac_path = DATA / "facilities.json"
    fac_doc = json.loads(fac_path.read_text())
    homepages_path = DATA / "zoo-homepages.json"
    homepages = (
        json.loads(homepages_path.read_text())
        if homepages_path.exists()
        else {}
    )
    homepages = {k: v for k, v in homepages.items() if not k.startswith("_")}

    for f in fac_doc["facilities"]:
        name = f["name"]
        sources = []
        src = f.get("species_source")
        if src in ("self", "mixed"):
            hp = homepages.get(name)
            if hp:
                sources.append({"label": "this zoo's site", "url": hp})
            else:
                # Fallback: Google search for the zoo's animal page
                q = urllib.parse.quote(f'"{name}" animals')
                sources.append({"label": "this zoo's site", "url": f"https://www.google.com/search?q={q}"})
        if src in ("wikipedia", "mixed"):
            sources.append({
                "label": "Wikipedia",
                "url": f"https://en.wikipedia.org/wiki/{wiki_slug_for(name)}",
            })
        if sources:
            f["species_source_urls"] = sources

    fac_path.write_text(json.dumps(fac_doc, indent=1))
    print(f"Updated source URLs for {sum(1 for f in fac_doc['facilities'] if f.get('species_source_urls'))} facilities.")


if __name__ == "__main__":
    main()
