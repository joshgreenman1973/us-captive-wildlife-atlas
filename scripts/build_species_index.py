"""
Build species → facilities index from data/zoo-species-raw.json
and merge with data/facilities.json.

Each species gets two taxonomy tags:
  taxon_class — Mammals / Birds / Reptiles / Amphibians / Fish / Invertebrates
  taxon_group — finer "browse" group (Great apes, Big cats, Bears, ...)
"""
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def norm_species(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9 -]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


# Coarse vertebrate-class assignment by keyword. The first match wins, so
# more specific patterns precede broader ones.
CLASS_RULES = [
    # Invertebrates
    ("Invertebrates", r"\b(beetle|butterfly|moth|tarantula|spider|scorpion|millipede|centipede|ant|bee|wasp|cockroach|roach|katydid|grasshopper|stick insect|mantis|crab|lobster|shrimp|crayfish|jellyfish|sea star|starfish|sea urchin|coral|anemone|octopus|squid|cuttlefish|nautilus|snail|slug|mussel|clam|oyster|earthworm|leech|sea cucumber|horseshoe crab|water strider|water bug|water scorpion|firefly|cicada|whipspider|assassin bug|goliath beetle)\b"),
    # Fish (and fishlike vertebrates)
    ("Fish",   r"\b(fish|shark|ray|stingray|skate|eel|seahorse|cichlid|tetra|piranha|gar|salmon|trout|bass|cod|grouper|tuna|cardinalfish|wrasse|tang|angelfish|clownfish|lungfish|coelacanth|guppy|mosquitofish|seadragon|pipefish|sardine|herring|catfish|sturgeon|paddlefish|gar|barracuda|moray|chub|minnow|killifish|flounder|sole|halibut)\b"),
    # Amphibians
    ("Amphibians", r"\b(frog|toad|salamander|newt|axolotl|caecilian|hellbender|mudpuppy|amphiuma|siren)\b"),
    # Reptiles
    ("Reptiles", r"\b(snake|python|boa|cobra|rattlesnake|mamba|adder|viper|kingsnake|gartersnake|ratsnake|copperhead|coral snake|sidewinder|whipsnake|alligator|crocodile|caiman|gharial|tortoise|turtle|terrapin|matamata|lizard|monitor|iguana|gecko|skink|chameleon|anole|gila monster|tegu|basilisk|chuckwalla|sheltopusik|crocodilian)\b"),
    # Birds
    ("Birds",  r"\b(eagle|hawk|falcon|kestrel|osprey|kite|harrier|vulture|condor|owl|bird|crane|stork|heron|egret|ibis|spoonbill|flamingo|pelican|cormorant|gannet|booby|frigatebird|albatross|shearwater|petrel|penguin|puffin|murre|guillemot|tern|gull|skua|jaeger|sandpiper|plover|avocet|stilt|oystercatcher|jacana|lapwing|kingfisher|hornbill|toucan|barbet|woodpecker|hummingbird|swift|nightjar|trogon|motmot|roller|bee-eater|cuckoo|coucal|turaco|cuckoo-roller|hoopoe|cassowary|emu|ostrich|kiwi|tinamou|rhea|brush-turkey|megapode|guan|curassow|chachalaca|grouse|ptarmigan|pheasant|partridge|quail|peafowl|peacock|guineafowl|chicken|jungle\s?fowl|duck|goose|swan|teal|wigeon|pintail|shoveler|pochard|eider|merganser|smew|shelduck|whistling-duck|magpie goose|coot|moorhen|gallinule|rail|crake|swamphen|finfoot|sungrebe|trumpeter|seriema|sunbittern|kagu|bustard|button-quail|pigeon|dove|sandgrouse|parrot|parakeet|cockatoo|macaw|conure|amazon|lory|lorikeet|lovebird|cockatiel|budgerigar|kakapo|kea|kaka|nicobar|songbird|thrush|robin|warbler|finch|sparrow|cardinal|oriole|tanager|grackle|cowbird|blackbird|magpie|jay|crow|raven|nutcracker|chickadee|tit|bushtit|nuthatch|treecreeper|wren|kinglet|gnatcatcher|swallow|martin|lark|pipit|wagtail|starling|myna|mockingbird|catbird|thrasher|babbler|fairywren|honeyeater|sunbird|flowerpecker|whiteye|silvereye|weaver|bishop|widowbird|whydah|firefinch|waxbill|munia|mannikin|bunting|seedeater|grosbeak|towhee|junco|longspur|redpoll|siskin|crossbill|bullfinch|euphonia|tanager|honeycreeper|cacique|hamerkop|frogmouth|smew|trumpeter swan|trumpeter|saddle-billed|pied imperial|laughing kookaburra|kookaburra|whooping crane|songbirds?)\b"),
    # Mammals — broadest catch; placed last
    ("Mammals", r"\b(monkey|ape|lemur|tamarin|marmoset|baboon|mandrill|gelada|sifaka|colobus|guenon|saki|langur|loris|galago|bushbaby|aye aye|aye-aye|potto|chimpanzee|bonobo|gorilla|orangutan|siamang|gibbon|lion|tiger|leopard|jaguar|cheetah|cougar|puma|ocelot|serval|caracal|fishing cat|sand cat|black-footed cat|pallas'?s? cat|mountain lion|wildcat|lynx|bobcat|bear|panda|elephant|rhino|rhinoceros|hippopotamus|hippo|giraffe|okapi|zebra|donkey|horse|wolf|fox|coyote|dingo|jackal|painted dog|wild dog|hyena|aardwolf|civet|genet|mongoose|fossa|binturong|bearcat|meerkat|otter|weasel|stoat|ferret|mink|badger|wolverine|marten|fisher|sable|skunk|raccoon|coati|kinkajou|ringtail|olingo|cacomistle|sloth|anteater|tamandua|armadillo|aardvark|pangolin|bat|bats|fruit bat|flying fox|vampire bat|colugo|opossum|marsupial|kangaroo|wallaby|wallaroo|pademelon|quokka|bettong|potoroo|bandicoot|wombat|koala|tasmanian devil|bilby|cuscus|possum|sugar glider|tenrec|hedgehog|shrew|mole|elephant shrew|treeshrew|moonrat|gymnure|hyrax|capybara|porcupine|guinea pig|chinchilla|degu|mara|paca|agouti|squirrel|chipmunk|marmot|prairie dog|gopher|beaver|muskrat|nutria|coypu|rat|mouse|vole|hamster|gerbil|jerboa|dormouse|naked mole-rat|mole-rat|mole rat|deer|elk|moose|caribou|reindeer|antelope|gazelle|impala|wildebeest|bongo|kudu|nyala|sitatunga|bushbuck|eland|oryx|gemsbok|addax|hartebeest|topi|tsessebe|blesbok|bontebok|springbok|gerenuk|dik-dik|duiker|klipspringer|oribi|reedbuck|waterbuck|puku|lechwe|saola|buffalo|bison|gaur|banteng|takin|musk ox|muskox|sheep|goat|ibex|markhor|chamois|argali|mouflon|tahr|aoudad|barbary sheep|serow|goral|tapir|peccary|warthog|babirusa|red river hog|wild boar|pygmy hippo|camel|llama|alpaca|guanaco|vicuna|tarsier|colugo|whale|dolphin|porpoise|narwhal|beluga|orca|seal|sea lion|walrus|sea otter|river otter|manatee|dugong|fennec|pudu|huemul|brocket|muntjac|cattle|ankole|cow|sheep|alpaca|goat|llama|ass|burro|mule|pony|tahr|saola|tamandua)\b"),
]


# Finer "browse" groups — chips users will likely click.
GROUP_RULES = [
    ("Great apes",       r"\b(chimpanzee|bonobo|gorilla|orangutan|siamang|gibbon)\b"),
    ("Monkeys & lemurs", r"\b(monkey|lemur|tamarin|marmoset|baboon|mandrill|gelada|sifaka|colobus|guenon|saki|langur|loris|galago|bushbaby|aye aye|aye-aye|potto|tarsier)\b"),
    ("Big cats",         r"\b(lion|tiger|leopard|jaguar|cheetah|cougar|puma|snow leopard|clouded leopard|ocelot|serval|caracal|fishing cat|sand cat|black-footed cat|pallas'?s? cat|mountain lion|lynx|bobcat|wildcat)\b"),
    ("Bears & pandas",   r"\b(bear|panda)\b"),
    ("Elephants",        r"\belephant\b"),
    ("Rhinos & hippos",  r"\b(rhino|rhinoceros|hippopotamus|hippo)\b"),
    ("Giraffe & okapi",  r"\b(giraffe|okapi)\b"),
    ("Wolves, dogs & foxes", r"\b(wolf|painted dog|maned wolf|fox|coyote|dingo|jackal|wild dog)\b"),
    ("Hoofstock",        r"\b(zebra|antelope|gazelle|impala|wildebeest|bongo|kudu|nyala|sitatunga|bushbuck|eland|oryx|gemsbok|addax|hartebeest|topi|tsessebe|blesbok|bontebok|springbok|gerenuk|dik-dik|duiker|klipspringer|oribi|reedbuck|waterbuck|puku|lechwe|saola|buffalo|bison|gaur|banteng|takin|musk ox|muskox|ibex|markhor|chamois|argali|mouflon|tahr|aoudad|barbary sheep|serow|goral|tapir|peccary|warthog|babirusa|red river hog|wild boar|camel|llama|alpaca|guanaco|vicuna|deer|elk|moose|caribou|reindeer|brocket|muntjac|pudu|huemul|pronghorn|ankole|donkey|sheep|goat|ass|burro|cattle)\b"),
    ("Marine mammals",   r"\b(whale|dolphin|porpoise|narwhal|beluga|orca|seal|sea lion|walrus|sea otter|manatee|dugong)\b"),
    ("Penguins",         r"\bpenguin\b"),
    ("Birds of prey",    r"\b(eagle|hawk|falcon|kestrel|osprey|kite|harrier|vulture|condor|owl)\b"),
    ("Parrots & macaws", r"\b(parrot|parakeet|cockatoo|macaw|conure|amazon|lory|lorikeet|lovebird|cockatiel|budgerigar|kakapo|kea|kaka)\b"),
    ("Flamingos & wading birds", r"\b(flamingo|stork|heron|egret|ibis|spoonbill|crane|hamerkop)\b"),
    ("Ducks, geese & swans",     r"\b(duck|goose|swan|teal|wigeon|pintail|shoveler|pochard|eider|merganser|smew|shelduck|whistling-duck|magpie goose)\b"),
    ("Snakes",           r"\b(snake|python|boa|cobra|rattlesnake|mamba|adder|viper|kingsnake|gartersnake|ratsnake|copperhead|whipsnake|sidewinder)\b"),
    ("Crocodilians",     r"\b(alligator|crocodile|caiman|gharial|crocodilian)\b"),
    ("Tortoises & turtles", r"\b(tortoise|turtle|terrapin|matamata)\b"),
    ("Lizards",          r"\b(lizard|monitor|iguana|gecko|skink|chameleon|anole|gila monster|tegu|basilisk|chuckwalla|sheltopusik)\b"),
    ("Frogs & salamanders", r"\b(frog|toad|salamander|newt|axolotl|caecilian|hellbender|mudpuppy|amphiuma|siren)\b"),
    ("Sharks & rays",    r"\b(shark|ray|stingray|skate)\b"),
    ("Marsupials",       r"\b(kangaroo|wallaby|wallaroo|pademelon|quokka|bettong|potoroo|bandicoot|wombat|koala|tasmanian devil|bilby|cuscus|possum|sugar glider|opossum|marsupial)\b"),
    ("Otters & weasels", r"\b(otter|weasel|stoat|ferret|mink|badger|wolverine|marten|fisher|sable|skunk)\b"),
    ("Sloths & anteaters", r"\b(sloth|anteater|tamandua|armadillo|aardvark|pangolin)\b"),
    ("Rodents",          r"\b(capybara|porcupine|guinea pig|chinchilla|degu|mara|paca|agouti|squirrel|chipmunk|marmot|prairie dog|gopher|beaver|muskrat|nutria|coypu|rat|mouse|vole|hamster|gerbil|jerboa|dormouse|naked mole-rat|mole-rat|mole rat)\b"),
    ("Bats",             r"\b(bat|bats|fruit bat|flying fox|vampire bat)\b"),
]


def classify(name: str):
    n = name.lower()
    cls = None
    for label, pat in CLASS_RULES:
        if re.search(pat, n):
            cls = label
            break
    grp = None
    for label, pat in GROUP_RULES:
        if re.search(pat, n):
            grp = label
            break
    return cls, grp


def main():
    raw = json.loads((DATA / "zoo-species-raw.json").read_text())
    facilities_doc = json.loads((DATA / "facilities.json").read_text())
    facilities = facilities_doc["facilities"]
    by_name = {f["name"]: f for f in facilities}

    species_index = {}
    facilities_with_species = 0
    unmatched_zoos = []

    for fac_name, sp_list in raw.items():
        if fac_name.startswith("_"):
            continue
        fac = by_name.get(fac_name)
        if not fac:
            unmatched_zoos.append(fac_name)
            continue
        # Deduplicate species at the source level
        seen = set()
        clean_list = []
        for s in sp_list:
            ks = norm_species(s)
            if ks and ks not in seen:
                seen.add(ks)
                clean_list.append(s.strip())
        fac["species"] = sorted(clean_list)
        facilities_with_species += 1
        for sp in clean_list:
            key = norm_species(sp)
            if key not in species_index:
                cls, grp = classify(sp)
                species_index[key] = {
                    "key": key,
                    "display": sp,
                    "facilities": [],
                    "taxon_class": cls,
                    "taxon_group": grp,
                }
            if fac_name not in species_index[key]["facilities"]:
                species_index[key]["facilities"].append(fac_name)

    print(f"Facilities with species data: {facilities_with_species}")
    print(f"Unique species: {len(species_index)}")
    if unmatched_zoos:
        print(f"WARN: {len(unmatched_zoos)} zoo names in raw not matched to facility list:")
        for z in unmatched_zoos[:10]:
            print(f"  - {z!r}")

    facilities_doc["counts"]["facilities_with_species"] = facilities_with_species
    facilities_doc["counts"]["unique_species"] = len(species_index)
    facilities_doc["source_dates"]["zoo_species_scrape"] = "2026-05-07"
    (DATA / "facilities.json").write_text(json.dumps(facilities_doc, indent=1))

    species_out = sorted(species_index.values(), key=lambda s: s["display"])
    (DATA / "species_index.json").write_text(json.dumps(species_out, indent=1))
    print(f"Wrote {DATA / 'species_index.json'}")

    print("\nTaxon class breakdown:")
    for k, v in Counter(s["taxon_class"] for s in species_out).most_common():
        print(f"  {v:5d}  {k}")
    print("\nTop taxon groups:")
    for k, v in Counter(s["taxon_group"] for s in species_out).most_common(15):
        print(f"  {v:5d}  {k}")


if __name__ == "__main__":
    main()
