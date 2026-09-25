"""Charge les données brutes (data/*.json) et les overlays détaillés (data/details/*.json)
et renvoie un jeu de données unifié pour les générateurs HTML / Excel."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

RARITY_FR = {"legendary": "Légendaire", "epic": "Épique", "rare": "Rare", "uncommon": "Peu commun", "common": "Commun"}
SLOT_FR = {"Helmet": "Casque", "Mask": "Masque", "Top": "Haut", "Gloves": "Gants", "Bottoms": "Bas", "Shoes": "Chaussures", "Weapon": "Arme"}
WTYPE_FR = {"Assault Rifle": "Fusil d'assaut", "SMG": "Pistolet-mitrailleur", "LMG": "Mitrailleuse", "Shotgun": "Fusil à pompe",
            "Sniper Rifle": "Fusil de précision", "Pistol": "Pistolet", "Crossbow": "Arbalète / Arc", "Melee": "Mêlée",
            "Rocket Launcher": "Lance-roquettes", "Flamethrower": "Lance-flammes"}
DEV_FR = {"Combat": "Combat", "Territory": "Territoire", "Crafting": "Fabrication"}


CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean(o):
    if isinstance(o, str):
        return CTRL.sub("", o)
    if isinstance(o, list):
        return [clean(x) for x in o]
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    return o


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return clean(json.load(f))


def load_details(name):
    p = os.path.join(DATA, "details", name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def set_name_from_armor(name):
    """Déduit le nom du set à partir du nom de la pièce (fallback quand l'overlay n'a pas l'info)."""
    base = re.sub(r"\s*-\s*(Cold|Heat)$", "", name)
    words = base.split()
    return " ".join(words[:-1]) if len(words) > 1 else base


def build():
    weapons = load("weapons.json")
    armor = load("armor.json")
    mods = load("mods.json")
    deviations = load("deviations.json")
    cradle = load("cradle.json")
    food = load("food.json")
    calibrations = load("calibrations.json")
    skins = load("animal-skins.json")

    dw, da, dm, dsets = (load_details(n) for n in ("weapons.json", "armor.json", "mods.json", "sets.json"))

    for w in weapons:
        d = dw.get(w["id"], {})
        w["typeFr"] = WTYPE_FR.get(w["type"], w["type"])
        w["rarityFr"] = RARITY_FR.get(w["rarity"], w["rarity"])
        w["effect"] = d.get("effect") or w.get("effect") or ""
        w["effectName"] = d.get("effectName", "")
        for k in ("mag", "critRate", "critDmg", "weakspotDmg", "range", "rangeEff", "reload", "reloadSec", "mobility", "ads", "ammo", "fireMode", "perkSlots", "description", "pellets", "falloff", "note", "effectSource", "effectEn"):
            w[k] = d.get(k)
        w["craft"] = d.get("craft", [])        # [{"name","qty","url"}]
        w["bench"] = d.get("bench", "")
        w["overrides"] = d.get("overrides", [])
        w["source"] = d.get("source", "")
        dmg, rpm = w.get("damage") or 0, w.get("rpm") or 0
        w["dps"] = round(dmg * rpm / 60) if rpm else None
        w["detailed"] = bool(d)

    for a in armor:
        d = da.get(a["id"], {})
        a["slotFr"] = SLOT_FR.get(a["slot"], a["slot"])
        a["rarityFr"] = RARITY_FR.get(a["rarity"], a["rarity"])
        derived = set_name_from_armor(a["name"])
        a["set"] = d.get("set") or (derived if derived in dsets or derived == "Dark Resonance" else "Pièce unique")
        a["hp"] = int(a["hp"]) if str(a.get("hp") or "").isdigit() else a.get("hp")
        a["effect"] = d.get("effect") or a.get("effect") or ""
        for k in ("pollution", "psi", "weight", "durability", "description", "modSlot", "source", "effectEn"):
            a[k] = d.get(k)
        a["craft"] = d.get("craft", [])
        a["bench"] = d.get("bench", "")
        a["detailed"] = bool(d)

    sets = {}
    for a in armor:
        s = sets.setdefault(a["set"], {"name": a["set"], "pieces": [], "bonus": dsets.get(a["set"], {}).get("bonus", []),
                                        "rarity": dsets.get(a["set"], {}).get("rarity", ""), "detailed": a["set"] in dsets})
        s["pieces"].append(a["id"])

    for m in mods:
        d = dm.get(m["id"], {})
        m["slotFr"] = SLOT_FR.get(m["slot"], m["slot"])
        m["categoryFr"] = "Mod d'arme" if m["category"] == "Weapon Mod" else "Mod d'armure"
        m["rarityFr"] = RARITY_FR.get(m["rarity"], m["rarity"])
        m["keywords"] = d.get("keywords", [])
        m["source"] = d.get("source", "")
        m["detailed"] = bool(d)

    ddev = load_details("deviations.json")
    for x in deviations:
        x["typeFr"] = DEV_FR.get(x["type"], x["type"])
        x["rarityFr"] = RARITY_FR.get(x["rarity"], x["rarity"])
        x["effect"] = re.sub(r"^Once Human .*? Deviation\.\s*", "", x.get("effect") or "")
        d = ddev.get(x["name"], {})
        if d.get("effect"):
            x["effect"] = d["effect"]
        x["location"] = d.get("location", "")
        x["note"] = d.get("note", "")
        x["detailed"] = bool(d)
    for x in food:
        x["rarityFr"] = RARITY_FR.get(x["rarity"], x["rarity"])
        x["effect"] = re.sub(r"^Once Human .*? Food\.\s*", "", x.get("effect") or "")
    for x in skins + calibrations:
        x["rarityFr"] = RARITY_FR.get(x["rarity"], x["rarity"])

    presets = load_details("presets.json") or []
    D = {"weapons": weapons, "armor": armor, "sets": list(sets.values()), "mods": mods, "deviations": deviations,
         "cradle": cradle, "food": food, "calibrations": calibrations, "skins": skins, "presets": presets}
    # Mise à jour depuis meta-builds.net (si data/metabuilds/allData.json est présent)
    import mb_merge
    mb_merge.merge(D, os.path.join(DATA, "details"))
    for x in D["weapons"]:
        x["typeFr"] = WTYPE_FR.get(x["type"], x["type"])
    for k in ("weapons", "armor", "deviations", "skins", "calibrations"):
        for x in D[k]:
            if x.get("rarity"):
                x["rarityFr"] = RARITY_FR.get(x["rarity"], x["rarity"])
    for x in D["armor"]:
        x["slotFr"] = SLOT_FR.get(x["slot"], x["slot"])
    for x in D["deviations"]:
        x["typeFr"] = DEV_FR.get(x["type"], x["type"])
    for m in D["mods"]:
        m["slotFr"] = SLOT_FR.get(m["slot"], "Toutes les armures" if m["slot"] == "All" else m["slot"])
        m["categoryFr"] = "Mod d'arme" if m["category"] == "Weapon Mod" else "Mod d'armure"
        m["rarityFr"] = RARITY_FR.get(m.get("rarity"), m.get("rarity"))
    return D


if __name__ == "__main__":
    d = build()
    for k, v in d.items():
        print(k, len(v) if isinstance(v, (list, dict)) else v)
    print(json.dumps(d.get("meta", {}), ensure_ascii=False, indent=1))
