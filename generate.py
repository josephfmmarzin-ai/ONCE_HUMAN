"""Génère build_planner.html et Once_Human_Builds.xlsx à partir de data/ + data/details/.
Usage : python generate.py"""
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from lib_data import build, HERE

OUT = HERE
D = build()

# ---------------------------------------------------------------- HTML
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
payload = json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
opt = open(os.path.join(HERE, "optimizer.js"), encoding="utf-8").read()
tpl = tpl.replace("/*__OPTIMIZER__*/", opt)          # moteur de l'optimiseur (source unique : optimizer.js)
open(os.path.join(OUT, "build_planner.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", payload))
print("HTML ok")

def gen_xlsx(LANG):
    L = lambda fr, en: fr if LANG == "fr" else en
    E = lambda x: (x.get("effectEn") or x.get("effect") or "") if LANG == "en" else (x.get("effect") or x.get("effectEn") or "")
    RF = {"legendary": "Legendary", "epic": "Epic", "rare": "Rare", "uncommon": "Uncommon", "common": "Common"}
    R = lambda x: x["rarityFr"] if LANG == "fr" else RF.get(x.get("rarity"), "")
    SH = {fr: (fr if LANG == "fr" else en) for fr, en in [("Armes","Weapons"),("Armures","Armor"),("Sets","Sets"),("Mods","Mods"),("Déviations","Deviations"),("Overrides","Overrides"),("Calibrations","Calibrations"),("Nourriture","Food"),("Peaux","Skins")]}
    SH_Armes = SH["Armes"]
    SH_Armures = SH["Armures"]
    SH_Mods = SH["Mods"]
    SH_Dviations = SH["Déviations"]
    SH_Overrides = SH["Overrides"]
    SH_Nourriture = SH["Nourriture"]
    # ---------------------------------------------------------------- EXCEL
    FONT = "Arial"
    RAR_COL = {"legendary": "E39B2D", "epic": "B06BF0", "rare": "4F9BE8", "uncommon": "6DBE5A", "common": "9AA3AB"}
    HEAD_FILL = PatternFill("solid", fgColor="1C2329")
    HEAD_FONT = Font(name=FONT, bold=True, color="F2C14E", size=10)
    INPUT_FILL = PatternFill("solid", fgColor="FFF7CC")
    thin = Side(style="thin", color="D9D9D9")
    BORDER = Border(bottom=thin)

    wb = Workbook()
    wb.remove(wb.active)


    def sheet(name, headers, rows, widths, rarity_col=None, link_cols=(), freeze="A2"):
        ws = wb.create_sheet(name)
        ws.append(headers)
        for c in ws[1]:
            c.font, c.fill, c.alignment = HEAD_FONT, HEAD_FILL, Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 28
        for r in rows:
            ws.append(r)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font = Font(name=FONT, size=10)
                c.alignment = Alignment(vertical="top", wrap_text=True)
                c.border = BORDER
            if rarity_col is not None:
                v = str(row[rarity_col].value or "").lower()
                key = {"légendaire": "legendary", "épique": "epic", "rare": "rare", "peu commun": "uncommon", "commun": "common", "legendary": "legendary", "epic": "epic", "uncommon": "uncommon", "common": "common"}.get(v)
                if key:
                    row[rarity_col].font = Font(name=FONT, size=10, bold=True, color=RAR_COL[key])
            for lc in link_cols:
                c = row[lc]
                if c.value:
                    c.hyperlink = c.value
                    c.value = "ouvrir"
                    c.font = Font(name=FONT, size=10, color="0563C1", underline="single")
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = freeze
        ws.auto_filter.ref = ws.dimensions
        return ws


    def craft_txt(x):
        return ", ".join(f"{c['name']} x{c['qty']}" for c in x.get("craft") or []) or ""


    W = sorted(D["weapons"], key=lambda x: x["name"])
    sheet(SH["Armes"],
          [L("Nom","Name"), L("Type","Type"), L("Rareté","Rarity"), "Tier", L("Dégâts","Damage"), L("Cadence (cpm)","Fire rate (rpm)"), L("DPS théorique","Theoretical DPS"), L("Chargeur","Magazine"), L("Taux crit","Crit rate"), L("Dég crit","Crit DMG"), L("Dég point faible","Weakspot DMG"),
           L("Portée","Range"), L("Recharge","Reload"), L("Munitions","Ammo"), L("Effet","Effect"), L("Recette de fabrication","Crafting recipe"), L("Atelier","Bench"), L("Fiche","Page"), "Image", L("Nom de l'effet","Effect name"), L("Mobilité","Mobility"), L("Chute de dégâts","Damage falloff"), L("Overrides compatibles","Compatible overrides"), "Note"],
          [[x["name"], L(x["typeFr"], x["type"]), R(x), x["tier"], x["damage"], x["rpm"], x["dps"], x["mag"], x["critRate"], x["critDmg"], x["weakspotDmg"],
            x["rangeEff"] or x["range"], x["reloadSec"] or x["reload"], x["ammo"], E(x), craft_txt(x), x["bench"], x["url"], x["imageUrl"], x["effectName"], x["mobility"], x["falloff"], ", ".join(x["overrides"] or []), x["note"]] for x in W],
          [30, 16, 12, 6, 9, 10, 10, 9, 9, 9, 10, 10, 10, 12, 60, 45, 14, 9, 9, 16, 9, 18, 40, 30], rarity_col=2, link_cols=(17, 18))

    A = sorted(D["armor"], key=lambda x: (x["set"], x["slot"]))
    sets_by = {s["name"]: s for s in D["sets"]}


    def set_bonus_txt(s):
        return " | ".join(f"{b['pieces']}p : {b['effect']}" for b in s.get("bonus", []))


    sheet(SH["Armures"],
          [L("Nom","Name"), "Set", L("Emplacement","Slot"), L("Rareté","Rarity"), L("PV","HP"), L("Résist. pollution","Pollution resist"), L("Effet","Effect"), L("Bonus de set","Set bonus"), L("Recette de fabrication","Crafting recipe"), L("Atelier","Bench"), L("Fiche","Page"), "Image"],
          [[x["name"], x["set"], L(x["slotFr"], x["slot"]), R(x), x["hp"], x["pollution"], E(x), set_bonus_txt(sets_by[x["set"]]), craft_txt(x), x["bench"], x["url"], x["imageUrl"]] for x in A],
          [30, 22, 12, 12, 7, 9, 45, 70, 45, 14, 9, 9], rarity_col=3, link_cols=(10, 11))

    sheet(SH["Sets"], ["Set", L("Rareté","Rarity"), L("Nb pièces","Pieces"), L("1 pièce","1 piece"), L("2 pièces","2 pieces"), L("3 pièces","3 pieces"), L("4 pièces","4 pieces"), L("Pièces","Piece list")],
          [[s["name"], L({"legendary": "Légendaire", "epic": "Épique", "rare": "Rare", "uncommon": "Peu commun"}.get(s["rarity"], ""), RF.get(s["rarity"], "")), len(s["pieces"]),
            *[next((b["effect"] for b in s["bonus"] if b["pieces"] == n), "") for n in (1, 2, 3, 4)],
            ", ".join(next(a["name"] for a in D["armor"] if a["id"] == pid) for pid in s["pieces"])] for s in sorted(D["sets"], key=lambda s: s["name"]) if s["name"] != "Pièce unique"],
          [20, 12, 8, 32, 32, 55, 55, 60], rarity_col=1)

    M = sorted(D["mods"], key=lambda x: (x["category"], x["slot"], x["name"], x["variant"]))
    sheet(SH["Mods"],
          [L("Nom <Variante>","Name <Variant>"), L("Nom","Name"), L("Catégorie","Category"), L("Emplacement","Slot"), L("Variante","Variant"), L("Effet principal","Main effect"), L("Fiche","Page"), "Image"],
          [[f"{x['name']} <{x['variant']}>", x["name"], L(x["categoryFr"], x["category"]), L(x["slotFr"], x["slot"]), x["variant"], x["effect"], x["url"], x["imageUrl"]] for x in M],
          [36, 28, 14, 12, 22, 90, 9, 9], link_cols=(6, 7))

    sheet(SH["Déviations"], [L("Nom","Name"), "Type", L("Rareté","Rarity"), L("Effet","Effect"), L("Où l'obtenir","Where to get"), L("Fiche","Page"), "Image"],
          [[x["name"], L(x["typeFr"], x["type"]), R(x), x["effect"], x["location"], x["url"], x["imageUrl"]] for x in sorted(D["deviations"], key=lambda x: (x["type"], x["name"]))],
          [28, 12, 12, 90, 40, 9, 9], rarity_col=2, link_cols=(5, 6))
    sheet(SH["Overrides"], [L("Nom","Name"), L("Catégorie","Category"), L("Effet","Effect"), L("Fiche","Page"), "Image"],
          [[x["name"], x["style"], x["effect"], x["url"], x["imageUrl"]] for x in sorted(D["cradle"], key=lambda x: (x["style"], x["name"]))],
          [28, 12, 100, 9, 9], link_cols=(3, 4))
    sheet(SH["Calibrations"], [L("Nom","Name"), L("Nom court","Short name"), L("Rareté","Rarity"), L("Fiche","Page"), "Image"],
          [[x["name"], x.get("shortName"), R(x), x["url"], x["imageUrl"]] for x in sorted(D["calibrations"], key=lambda x: x["name"])],
          [36, 18, 12, 9, 9], rarity_col=2, link_cols=(3, 4))
    sheet(SH["Nourriture"], [L("Nom","Name"), L("Catégorie","Category"), L("Rareté","Rarity"), L("Poids (kg)","Weight (kg)"), L("Effet","Effect"), L("Fiche","Page"), "Image"],
          [[x["name"], x["category"], R(x), x.get("weight"), x["effect"], x["url"], x["imageUrl"]] for x in sorted(D["food"], key=lambda x: x["name"])],
          [30, 12, 12, 9, 80, 9, 9], rarity_col=2, link_cols=(5, 6))
    HS = {h["family"]: h for h in D.get("hideSets", [])}
    SL6 = [("Helmet","Casque"),("Mask","Masque"),("Top","Haut"),("Gloves","Gants"),("Bottoms","Bas"),("Shoes","Chaussures")]
    sheet(SH["Peaux"], [L("Nom","Name"), L("Rareté","Rarity"), L("Set de peaux (×4)","Hide set (×4)")] + [L(fr, en) for en, fr in SL6] + [L("Fiche","Page"), "Image", L("Statut","Status")],
          [[x["name"], R(x), (L(HS[x["family"]]["fr"], HS[x["family"]]["name"]) if x.get("family") in HS else "")] + [(x.get("slotEffects") or {}).get(en, "") for en, _ in SL6]
           + [x["url"], x["imageUrl"], L("ancien", "legacy") if x.get("legacy") else ""] for x in sorted(D["skins"], key=lambda x: x["name"])],
          [26, 12, 18, 34, 34, 34, 34, 34, 34, 9, 9, 9], rarity_col=1, link_cols=(9, 10))
    sheet(L("Sets de peaux", "Hide sets"), [L("Set", "Set"), L("Nom en jeu", "In-game name"), L("Famille de peaux", "Hide family"), L("Pièces", "Pieces"), L("Effet", "Effect"), L("Peaux concernées", "Hides")],
          [[L(h["fr"], h["name"]), h["name"], h["families"], h["pieces"], L(h["effect"], h["effectEn"]), ", ".join(sorted(x["name"] for x in D["skins"] if x.get("family") == h["family"] and not x.get("legacy")))] for h in D.get("hideSets", [])],
          [20, 22, 16, 8, 60, 70])

    # ---------------- Feuille Build (interactive, listes déroulantes + formules)
    ws = wb.create_sheet("Build", 0)
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 34
    ws.column_dimensions["C"].width = 34
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 12
    ws.column_dimensions["G"].width = 70
    ws["A1"] = L("ONCE HUMAN — Planificateur de build","ONCE HUMAN — Build planner")
    ws["A1"].font = Font(name=FONT, bold=True, size=16, color="E39B2D")
    ws["A2"] = L("Cellules jaunes = à remplir avec les listes déroulantes. Les stats, PV et sets se calculent automatiquement. Les onglets suivants contiennent toutes les données (filtrables).","Yellow cells = fill in with the dropdown lists. Stats, HP and sets are computed automatically. The other sheets hold all the data (filterable).")
    ws["A2"].font = Font(name=FONT, italic=True, size=9, color="666666")
    ws.merge_cells("A2:G2")

    nW, nA, nM = len(W) + 1, len(A) + 1, len(M) + 1
    hdr = [L("Emplacement","Slot"), L("Objet","Item"), "Mod", L("Dégâts / PV","Damage / HP"), L("Cadence","Fire rate"), "DPS", L("Effet de l'objet","Item effect")]
    ws.append([])
    ws.append(hdr)
    for c in ws[4]:
        c.font, c.fill = HEAD_FONT, HEAD_FILL

    dv_w = DataValidation(type="list", formula1=f"={SH_Armes}!$A$2:$A${nW}", allow_blank=True)
    dv_a = DataValidation(type="list", formula1=f"={SH_Armures}!$A$2:$A${nA}", allow_blank=True)
    dv_m = DataValidation(type="list", formula1=f"={SH_Mods}!$A$2:$A${nM}", allow_blank=True)
    for dv in (dv_w, dv_a, dv_m):
        ws.add_data_validation(dv)

    rows = [(L("Arme principale","Primary weapon"), "w"), (L("Arme secondaire","Secondary weapon"), "w"), (L("Casque","Helmet"), "a"), (L("Masque","Mask"), "a"), (L("Haut","Top"), "a"),
            (L("Gants","Gloves"), "a"), (L("Bas","Bottoms"), "a"), (L("Chaussures","Shoes"), "a")]
    armor_rows = []
    r = 5
    for label, kind in rows:
        ws.cell(r, 1, label).font = Font(name=FONT, bold=True, size=10)
        ws.cell(r, 2).fill = INPUT_FILL
        ws.cell(r, 3).fill = INPUT_FILL
        dv_m.add(ws.cell(r, 3))
        if kind == "w":
            dv_w.add(ws.cell(r, 2))
            ws.cell(r, 4, f'=IF(B{r}="","",INDEX({SH_Armes}!$E$2:$E${nW},MATCH(B{r},{SH_Armes}!$A$2:$A${nW},0)))')
            ws.cell(r, 5, f'=IF(B{r}="","",INDEX({SH_Armes}!$F$2:$F${nW},MATCH(B{r},{SH_Armes}!$A$2:$A${nW},0)))')
            ws.cell(r, 6, f'=IF(B{r}="","",INDEX({SH_Armes}!$G$2:$G${nW},MATCH(B{r},{SH_Armes}!$A$2:$A${nW},0)))')
            ws.cell(r, 7, f'=IF(B{r}="","",INDEX({SH_Armes}!$O$2:$O${nW},MATCH(B{r},{SH_Armes}!$A$2:$A${nW},0))&"")')
        else:
            dv_a.add(ws.cell(r, 2))
            armor_rows.append(r)
            ws.cell(r, 4, f'=IF(B{r}="","",INDEX({SH_Armures}!$E$2:$E${nA},MATCH(B{r},{SH_Armures}!$A$2:$A${nA},0)))')
            ws.cell(r, 7, f'=IF(B{r}="","",INDEX({SH_Armures}!$B$2:$B${nA},MATCH(B{r},{SH_Armures}!$A$2:$A${nA},0))&" — "&INDEX({SH_Armures}!$G$2:$G${nA},MATCH(B{r},{SH_Armures}!$A$2:$A${nA},0)))')
        r += 1

    # Emplacements sans mod
    dv_d = DataValidation(type="list", formula1=f"={SH_Dviations}!$A$2:$A${len(D['deviations'])+1}", allow_blank=True)
    dv_o = DataValidation(type="list", formula1=f"={SH_Overrides}!$A$2:$A${len(D['cradle'])+1}", allow_blank=True)
    dv_f = DataValidation(type="list", formula1=f"={SH_Nourriture}!$A$2:$A${len(D['food'])+1}", allow_blank=True)
    for dv in (dv_d, dv_o, dv_f):
        ws.add_data_validation(dv)
    for label, dv, sh, ncol in ((L("Déviation","Deviation"), dv_d, SH["Déviations"], "D"), ("Cradle override", dv_o, SH["Overrides"], "C"), (L("Nourriture 1","Food 1"), dv_f, SH["Nourriture"], "E"), (L("Nourriture 2","Food 2"), dv_f, SH["Nourriture"], "E")):
        ws.cell(r, 1, label).font = Font(name=FONT, bold=True, size=10)
        ws.cell(r, 2).fill = INPUT_FILL
        dv.add(ws.cell(r, 2))
        n = wb[sh].max_row
        ws.cell(r, 7, f'=IF(B{r}="","",INDEX({sh}!${ncol}$2:${ncol}${n},MATCH(B{r},{sh}!$A$2:$A${n},0)))')
        r += 1

    # Effets des mods (colonne G des lignes 5-12 ne montre que l'objet ; on liste les mods en dessous)
    r += 1
    ws.cell(r, 1, L("Effets des mods équipés","Equipped mod effects")).font = Font(name=FONT, bold=True, size=11, color="E39B2D")
    r += 1
    for rr in range(5, 13):
        ws.cell(r, 1, f'=IF(C{rr}="","",A{rr})')
        ws.cell(r, 2, f'=IF(C{rr}="","",C{rr})')
        ws.cell(r, 7, f'=IF(C{rr}="","",INDEX({SH_Mods}!$F$2:$F${nM},MATCH(C{rr},{SH_Mods}!$A$2:$A${nM},0)))')
        r += 1

    # Résumé
    r += 1
    ws.cell(r, 1, L("Résumé","Summary")).font = Font(name=FONT, bold=True, size=11, color="E39B2D")
    r += 1
    ws.cell(r, 1, L("PV total armure","Total armor HP")); ws.cell(r, 2, f"=SUM(D{armor_rows[0]}:D{armor_rows[-1]})")
    ws.cell(r, 2).font = Font(name=FONT, bold=True, size=12)
    r += 1
    ws.cell(r, 1, L("DPS cumulé (2 armes)","Combined DPS (2 weapons)")); ws.cell(r, 2, "=SUM(F5:F6)")
    ws.cell(r, 2).font = Font(name=FONT, bold=True, size=12)
    r += 1
    ws.cell(r, 1, L("Pièces équipées","Pieces equipped")); ws.cell(r, 2, f'=COUNTA(B{armor_rows[0]}:B{armor_rows[-1]})')
    r += 2
    ws.cell(r, 1, L("Sets (pièces portées)","Sets (pieces worn)")).font = Font(name=FONT, bold=True, size=11, color="E39B2D")
    r += 1
    set_first = r
    for i, ar in enumerate(armor_rows):
        ws.cell(r, 1, f'=IF(B{ar}="","",INDEX({SH_Armures}!$B$2:$B${nA},MATCH(B{ar},{SH_Armures}!$A$2:$A${nA},0)))')
        ws.cell(r, 2, f'=IF(A{r}="","",COUNTIF($A${set_first}:$A${set_first+len(armor_rows)-1},A{r}))')
        ws.cell(r, 3, f'=IF(A{r}="","",IFERROR(INDEX({SH_Armures}!$H$2:$H${nA},MATCH(B{ar},{SH_Armures}!$A$2:$A${nA},0))&"",""))')
        r += 1
    ws.cell(r, 1, L("Note : DPS théorique = dégâts × cadence ÷ 60 (sans crit ni effets). Nom du set répété par pièce ; le nombre indique combien de pièces de ce set tu portes.","Note: theoretical DPS = damage × fire rate ÷ 60 (no crit or effects). Set name repeated per piece; the number shows how many pieces of that set you wear.")).font = Font(name=FONT, italic=True, size=9, color="666666")

    # Exemple pré-rempli (à remplacer)
    ws["B5"] = "KVD - Boom! Boom!"; ws["B6"] = "Recurve Crossbow"
    for cell, nm in zip(["C5","C6","C7","C8","C9","C10","C11","C12"], ["Burning Wrath <Deviant Energy>","Vulnerability Amplifier <Precision>","Deviation Expert <Deviant Energy>","Blaze Amplifier <Deviant Energy>","Resist Advantage <Survival>","Elemental Overload <Deviant Energy>","Status Amplification <Deviant Energy>","Steady Hand <Deviant Energy>"]): ws[cell] = nm
    ws["B13"] = "Pyro Dino"
    for rr, nm in zip(armor_rows, ["Shelterer Hat", "Shelterer Mask", "Shelterer Top", "BBQ Gloves", "Shelterer Pants", "Heavy Duty Shoes"]):
        if any(a["name"] == nm for a in A):
            ws.cell(rr, 2, nm)
    for row in ws.iter_rows(min_row=5, max_row=r):
        for c in row:
            if c.font.name != FONT or c.font.size is None:
                c.font = Font(name=FONT, size=10, bold=c.font.bold, color=c.font.color, italic=c.font.italic)
            c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A5"

    wb.save(os.path.join(OUT, f"Once_Human_Builds_{LANG.upper()}.xlsx"))
    print("XLSX", LANG)


for _l in ("fr", "en"):
    gen_xlsx(_l)
