"""Fusion des données meta-builds.net (data/metabuilds/*.json) dans le jeu de données local.

- data/metabuilds/allData.json   : export de https://meta-builds.net/api/get/allData
- data/metabuilds/gear_stats.json: stats chiffrées des fiches /api/get/catalog/gears/{id}
- data/details/hide_sets.json    : bonus de sets de peaux (x4)

Règles : meta-builds est la source la plus à jour (version de jeu 3.0.5, sept. 2026).
On garde les identifiants locaux (les builds enregistrés et les presets restent valides),
on met à jour noms, effets, stats, sets ; on ajoute ce qui manque ; ce qui n'existe plus
côté meta-builds est conservé mais marqué « legacy »."""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
MB_DIR = os.path.join(HERE, "data", "metabuilds")

RARITY = {5: "legendary", 4: "epic", 3: "epic", 2: "rare", 1: "uncommon", 0: "common"}
WTYPE = {1: "Shotgun", 2: "SMG", 3: "Assault Rifle", 4: "Sniper Rifle", 5: "LMG", 6: "Crossbow", 7: "Rocket Launcher", 8: "Melee", 9: "Pistol"}
ASLOT = {1: "Helmet", 2: "Mask", 3: "Top", 4: "Bottoms", 5: "Gloves", 6: "Shoes"}
MSLOT = {"weapon": "Weapon", "helmet": "Helmet", "mask": "Mask", "top": "Top", "gloves": "Gloves", "bottoms": "Bottoms", "shoes": "Shoes", "all_armor": "All"}
HSLOT = {"helmet": "Helmet", "mask": "Mask", "top": "Top", "pants": "Bottoms", "gloves": "Gloves", "shoes": "Shoes"}
SET_NAME = {"Blackstone Set": "Blackstone", "No set": None}
# noms différents entre l'ancienne base (oncehumandb) et meta-builds (nom actuel en jeu)
W_ALIAS = {"d12rainingcash": "db12rainingcash", "nothernpike": "northernpike"}
A_ALIAS = {"bbqgrillgloves": "bbqgloves", "dustmask": "desertdustmask", "hardtacticalboots": "tacticalcombatboots",
           "yellowpainmask": "yellowpaintedmask", "gildedgloves": "gildedpalmshield", "stealthwalkerwrap": "covertwalkershirt",
           "raidfaceshield": "raidhelmet", "falconhelmet": "falconcap"}
D_ALIAS = {"butterflysemissiary": "butterflysemissary"}
LEGACY_MOD_STATUS = {"legacy_duplicate_alias"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def slug(s):
    s = (s or "").lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def text(h):
    """HTML meta-builds -> texte : les <li> deviennent des phrases séparées."""
    if not h:
        return ""
    h = re.sub(r"</li>\s*", ". ", h)
    h = re.sub(r"<br\s*/?>", " ", h)
    h = html.unescape(re.sub(r"<[^>]+>", " ", h))
    h = re.sub(r"\s+", " ", h).strip()
    h = re.sub(r"\s+\.", ".", h)
    h = re.sub(r"\.\.+", ".", h)
    return h.strip(" .") + ("." if h else "")


def pct(v):
    return None if v is None else f"{v}%"


def available():
    return os.path.exists(os.path.join(MB_DIR, "allData.json"))


def load():
    with open(os.path.join(MB_DIR, "allData.json"), encoding="utf-8") as f:
        mb = json.load(f)
    p = os.path.join(MB_DIR, "gear_stats.json")
    stats = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"weapons": {}, "armor": {}}
    return mb, stats


def merge(D, details_dir):
    """Modifie D (dict retourné par lib_data.build) en place et renvoie un rapport."""
    if not available():
        return {"skipped": True}
    mb, stats = load()
    rep = {}
    set_by_id = {s["id"]: SET_NAME.get(s["title"], s["title"]) for s in mb["sets"]}

    # ------------------------------------------------ Sets (bonus 1 à 4 pièces)
    mb_sets = {}
    for s in mb["sets"]:
        nm = SET_NAME.get(s["title"], s["title"])
        if not nm:
            continue
        bonus = [{"pieces": i, "effect": text(s[k])} for i, k in enumerate(["bonus_one", "bonus_two", "bonus_three", "bonus_four"], 1) if s.get(k)]
        mb_sets[nm] = bonus

    # ------------------------------------------------ Armes
    W = {norm(w["name"]): w for w in D["weapons"]}
    seen, added = set(), 0
    for g in mb["gears"]:
        if g["category"] not in (0, 7):
            continue
        k = W_ALIAS.get(norm(g["title"]), norm(g["title"]))
        w = W.get(k)
        st = stats["weapons"].get(str(g["id"]))
        eff = text(g["description"])
        if not w:
            w = {"id": slug(g["title"]), "slug": slug(g["title"]), "name": re.sub(r"\s+", " ", g["title"]), "type": WTYPE.get(g["weapon_type"], "Melee"),
                 "rarity": RARITY.get(g["rarity"], "rare"), "tier": 5, "damage": None, "rpm": None, "effect": eff, "effectEn": eff, "effectName": "",
                 "imageUrl": "", "url": "https://meta-builds.net/once-human/weapons/", "craft": [], "bench": "", "overrides": [], "source": "meta-builds.net",
                 "detailed": True, "isNew": True}
            for kk in ("mag", "critRate", "critDmg", "weakspotDmg", "range", "rangeEff", "reload", "reloadSec", "mobility", "ads", "ammo", "fireMode", "perkSlots", "description", "pellets", "falloff", "note", "effectSource"):
                w.setdefault(kk, None)
            D["weapons"].append(w); W[k] = w; added += 1
        else:
            if eff:
                w["effectEn"] = eff
                if not w.get("detailed") or not w.get("effect") or not re.search(r"[éèàù]|\b(les|des|du|la|le)\b", w["effect"]):
                    w["effect"] = eff   # pas de traduction FR locale -> texte à jour
            w["name"] = re.sub(r"\s+", " ", g["title"]) if norm(g["title"]) == k else w["name"]
            w["rarity"] = RARITY.get(g["rarity"], w["rarity"])
        if st:
            if st.get("damage") is not None:
                w["damage"] = st["damage"]
            if st.get("rpm"):
                w["rpm"] = st["rpm"]
            for src, dst, f in (("mag", "mag", None), ("critRate", "critRate", pct), ("critDmg", "critDmg", pct), ("weakspotDmg", "weakspotDmg", pct),
                                ("mobility", "mobility", None), ("ammo", "ammo", None)):
                if st.get(src) is not None:
                    w[dst] = f(st[src]) if f else st[src]
            if st.get("reloadSec") is not None:
                w["reloadSec"] = f"{st['reloadSec']}s"
            if st.get("ads") is not None:
                w["ads"] = f"{st['ads']}s"
            if st.get("pellets") and st["pellets"] > 1:
                w["pellets"] = st["pellets"]
            if st.get("fullRange"):
                w["rangeEff"] = f"{st['fullRange']}m"
                if st.get("minRange"):
                    w["falloff"] = f"{st['fullRange']}m / {st['minRange']}m"
        dmg, rpm = w.get("damage") or 0, w.get("rpm") or 0
        w["dps"] = round(dmg * rpm / 60) if rpm else None
        w["mb"] = True
        seen.add(w["id"])
    for w in D["weapons"]:
        if w["id"] not in seen:
            w["legacy"] = True
    rep["weapons"] = f"{len(seen)} à jour, {added} nouvelles, {sum(1 for w in D['weapons'] if w.get('legacy'))} hors meta-builds"

    # ------------------------------------------------ Armures
    A = {norm(a["name"]): a for a in D["armor"]}
    by_set_slot = {}
    for a in D["armor"]:
        by_set_slot.setdefault((a.get("set"), a["slot"]), a)
    seen, added = set(), 0
    for g in mb["gears"]:
        if not 1 <= g["category"] <= 6:
            continue
        slot = ASLOT[g["category"]]
        setn = set_by_id.get(g["linked_set"])
        k = A_ALIAS.get(norm(g["title"]), norm(g["title"]))
        a = A.get(k)
        if not a and setn:
            a = by_set_slot.get((setn, slot))
            if a and a["id"] in seen:
                a = None
        eff = text(g["description"])
        st = stats["armor"].get(str(g["id"]))
        if not a:
            a = {"id": slug(g["title"]), "slug": slug(g["title"]), "name": g["title"], "slot": slot, "rarity": RARITY.get(g["rarity"], "legendary"), "style": "",
                 "hp": None, "effect": eff, "imageUrl": "", "url": "https://meta-builds.net/once-human/armor/", "craft": [], "bench": "", "detailed": True, "isNew": True,
                 "slotFr": slot, "rarityFr": ""}
            for kk in ("pollution", "psi", "weight", "durability", "description", "modSlot", "source", "effectEn"):
                a.setdefault(kk, None)
            D["armor"].append(a); A[k] = a; added += 1
        else:
            if a["name"] != g["title"]:
                a["aka"] = a["name"]
                a["name"] = g["title"]
        a["set"] = setn or "Pièce unique"
        if eff:
            a["effectEn"] = eff
            if not re.search(r"[éèàù]", a.get("effect") or ""):
                a["effect"] = eff
        a["rarity"] = RARITY.get(g["rarity"], a["rarity"])
        if st:
            a["hpMax"] = st.get("hpMax"); a["psiMax"] = st.get("psiMax")
            if st.get("pollution") is not None:
                a["pollution"] = st["pollution"]
            if a.get("hp") in (None, "", "?"):
                a["hp"] = a["hpMax"]
        a["mb"] = True
        seen.add(a["id"])
    for a in D["armor"]:
        if a["id"] not in seen:
            a["legacy"] = True
    rep["armor"] = f"{len(seen)} à jour, {added} nouvelles, {sum(1 for a in D['armor'] if a.get('legacy'))} hors meta-builds"

    # reconstruit les sets à partir des armures
    old = {s["name"]: s for s in D["sets"]}
    sets = {}
    for a in D["armor"]:
        s = sets.setdefault(a["set"], {"name": a["set"], "pieces": [], "bonus": mb_sets.get(a["set"]) or (old.get(a["set"], {}).get("bonus") or []),
                                        "rarity": old.get(a["set"], {}).get("rarity", "legendary"), "detailed": True, "mb": a["set"] in mb_sets})
        s["pieces"].append(a["id"])
    D["sets"] = list(sets.values())
    rep["sets"] = f"{len(mb_sets)} sets meta-builds"

    # ------------------------------------------------ Mods (un objet par mod × suffixe)
    old_mods = {m["id"]: m for m in D["mods"]}
    old_eff = {}
    for m in D["mods"]:
        if re.search(r"\d", m.get("effect") or ""):
            old_eff.setdefault(norm(m["name"]), m["effect"])
    mods, ids = [], set()
    for m in mb["mods"]:
        if m.get("gameplay_status") in LEGACY_MOD_STATUS:
            continue
        slot = MSLOT.get(m["slot"], m["slot"])
        eff = text(m.get("current_description") or m.get("description"))
        if not re.search(r"\d", eff):   # résumé sans chiffres côté meta-builds -> texte chiffré de l'ancienne base
            for a in [m["title"], m.get("legacy_title")] + (m.get("aliases") or []):
                if old_eff.get(norm(a)):
                    eff = old_eff[norm(a)]; break
            if not re.search(r"\d", eff) and re.search(r"\d", text(m.get("legacy_description"))):
                eff = text(m.get("legacy_description"))
        for v in m["variants"]:
            mid = slug(m["title"]) + "-" + slug(v["suffix"])
            if mid in ids:
                continue
            ids.add(mid)
            o = old_mods.get(mid, {})
            mods.append({"id": mid, "slug": mid, "name": m.get("current_title") or m["title"], "category": "Weapon Mod" if slot == "Weapon" else "Armor Mod",
                         "slot": slot, "variant": v["suffix"], "rarity": o.get("rarity", "legendary"), "effect": eff, "imageUrl": o.get("imageUrl", ""),
                         "url": o.get("url") or "https://meta-builds.net/once-human/mods/", "keyword": m.get("build_group") or "Normal", "modType": m.get("mod_type"),
                         "shiny": bool(v.get("is_shiny")), "status": m.get("gameplay_status"), "aliases": m.get("aliases") or [], "mb": True})
    # anciens identifiants (presets, builds enregistrés) : conservés, marqués legacy
    kept = 0
    for mid, o in old_mods.items():
        if mid not in ids:
            o = dict(o); o["legacy"] = True; mods.append(o); kept += 1
    D["mods"] = mods
    rep["mods"] = f"{len(ids)} mods×suffixes meta-builds, {kept} anciens conservés (legacy)"

    # ------------------------------------------------ Déviations
    DV = {norm(x["name"]): x for x in D["deviations"]}
    morphs = {}
    for x in mb["deviations"]:
        if x.get("is_morph"):
            morphs.setdefault(x.get("base_deviation_id"), []).append(x["title"])
    seen, added = set(), 0
    for x in mb["deviations"]:
        if x.get("is_morph"):
            continue
        k = D_ALIAS.get(norm(x["title"]), norm(x["title"]))
        d = DV.get(k)
        eff = text(x["description"])
        if not d:
            d = {"id": slug(x["title"]), "slug": slug(x["title"]), "name": x["title"], "type": x.get("deviation_type") or "Combat", "rarity": "legendary",
                 "effect": eff, "imageUrl": "", "url": "https://meta-builds.net/once-human/deviations/", "location": text(x.get("source")), "note": "", "detailed": True, "isNew": True,
                 "typeFr": x.get("deviation_type") or "Combat", "rarityFr": ""}
            D["deviations"].append(d); DV[k] = d; added += 1
        if eff:
            d["effectEn"] = eff
            if not d.get("detailed"):
                d["effect"] = eff
        if x.get("deviation_type"):
            d["type"] = x["deviation_type"]
        if morphs.get(x["id"]):
            d["morphs"] = morphs[x["id"]]
        d["mb"] = True
        seen.add(d["id"])
    for d in D["deviations"]:
        if d["id"] not in seen:
            d["legacy"] = True
    rep["deviations"] = f"{len(seen)} à jour, {added} nouvelles, {sum(len(v) for v in morphs.values())} variantes (morphs) rattachées"

    # ------------------------------------------------ Cradle
    CR = {norm(c["name"]): c for c in D["cradle"]}
    n = 0
    for c in mb["cradles"]:
        if norm(c["title"]) == "empty":
            continue
        x = CR.get(norm(c["title"]))
        eff = text(c["description"])
        if not x:
            x = {"id": slug(c["title"]), "slug": slug(c["title"]), "name": c["title"], "style": "Combat", "effect": eff, "imageUrl": "", "url": "https://meta-builds.net/once-human/cradle-perks/"}
            D["cradle"].append(x); CR[norm(c["title"])] = x
        x["effect"] = eff or x["effect"]
        x["current"] = True
        x["anomaly"] = c.get("anomaly")
        n += 1
    rep["cradle"] = f"{n} overrides actuels (les {sum(1 for c in D['cradle'] if not c.get('current'))} autres = anciennes saisons)"

    # ------------------------------------------------ Calibrations
    K = {norm(k.get("shortName") or k["name"]): k for k in D["calibrations"]}
    n = 0
    for c in mb["calibrations"]:
        x = K.get(norm(c["title"]))
        eff = text(c["description"])
        if not x:
            if norm(c["title"]) == "default":
                continue
            x = {"id": "calibration-" + slug(c["title"]), "slug": slug(c["title"]), "name": "Calibration Blueprint - " + c["title"], "shortName": c["title"],
                 "category": "Calibration Blueprints", "rarity": "epic", "imageUrl": "", "url": "https://meta-builds.net/", "rarityFr": ""}
            D["calibrations"].append(x)
        x["effect"] = eff; x["style"] = c.get("style"); x["weaponGroup"] = c.get("weapon_group"); x["seasonal"] = bool(c.get("seasonal"))
        n += 1
    rep["calibrations"] = f"{n} à jour"

    # ------------------------------------------------ Peaux (effet par pièce d'armure) + familles
    SK = {norm(s["name"]): s for s in D["skins"]}
    hides = [r for r in mb["resources"] if r.get("armor_material_kind") == "fur_hide"]
    out = []
    for r in hides:
        s = SK.get(norm(r["title"]), {})
        se = {HSLOT[k]: v for k, v in (r.get("armor_slot_effects") or {}).items() if k in HSLOT}
        x = {"id": s.get("id") or slug(r["title"]), "slug": slug(r["title"]), "name": r["title"], "category": "Hide", "rarity": s.get("rarity") or ("legendary" if re.search(r"Lunar|Golden|Starfall|Dreamfused", r["title"]) else "epic"),
             "slotEffects": se, "effect": " · ".join(f"{k} : {v}" for k, v in se.items()), "imageUrl": s.get("imageUrl", ""), "url": s.get("url") or "https://meta-builds.net/",
             "family": hide_family(r["title"]), "lunar": r["title"].startswith("Lunar"), "mb": True, "rarityFr": s.get("rarityFr", "")}
        out.append(x)
    seen = {norm(x["name"]) for x in out}
    for s in D["skins"]:
        if norm(s["name"]) not in seen:
            s = dict(s); s["legacy"] = True; s["family"] = hide_family(s["name"]); s.setdefault("slotEffects", {}); out.append(s)
    D["skins"] = out
    p = os.path.join(details_dir, "hide_sets.json")
    D["hideSets"] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []
    rep["skins"] = f"{len(hides)} peaux avec effet par pièce, {len(D['hideSets'])} sets de peaux"

    D["meta"] = {"source": "meta-builds.net", "gameVersion": max((p.get("game_version") or "" for p in mb.get("metaPicks", [])), default=""),
                 "fetched": mb.get("_fetched", "")[:10], "report": rep}
    return rep


FAMILIES = [("deer", r"Deer Hide|Reindeer"), ("wolf", r"Wolf Skin"), ("bear", r"Bear Skin"), ("rabbit", r"Rabbit Fur"),
            ("croc", r"Crocodile"), ("cow", r"Cowhide"), ("wool", r"Wool"), ("fox", r"Fox Skin")]


def hide_family(name):
    for fam, rx in FAMILIES:
        if re.search(rx, name or "", re.I):
            if fam == "deer" and "Reindeer" in name:
                return None       # le renne n'est pas un cerf dans les sets relevés
            return fam
    return None
