"""Génère Once_Human_Guide.pdf : guide de référence imprimable (armes, sets, pièces uniques, déviations, overrides, nourriture)."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from lib_data import build, HERE

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FD + "DejaVuSansCondensed.ttf"))
pdfmetrics.registerFont(TTFont("DVB", FD + "DejaVuSansCondensed-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI", FD + "DejaVuSansCondensed-Oblique.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVB")

def gen(LANG):
    L = lambda fr, en: fr if LANG == "fr" else en
    E = lambda x: (x.get("effectEn") or x.get("effect") or "") if LANG == "en" else (x.get("effect") or x.get("effectEn") or "")
    RL = lambda r: {"legendary": L("Légendaire","Legendary"), "epic": L("Épique","Epic"), "rare": "Rare", "uncommon": L("Peu commun","Uncommon"), "common": L("Commun","Common")}.get(r, "")
    D = build()
    BG = colors.HexColor("#141a1f"); STAR = colors.HexColor("#f2c14e"); TEAL = colors.HexColor("#2f8f85"); INK2 = colors.HexColor("#555f68")
    RAR = {"legendary": "#c9861f", "epic": "#8e4fd1", "rare": "#2f7fd0", "uncommon": "#4f9a42", "common": "#7a848c"}

    S = {
        "h1": ParagraphStyle("h1", fontName="DVB", fontSize=22, leading=26, textColor=BG, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName="DVB", fontSize=13, leading=16, textColor=TEAL, spaceBefore=8, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName="DVB", fontSize=10.5, leading=13, textColor=BG, spaceBefore=4),
        "p": ParagraphStyle("p", fontName="DV", fontSize=8.6, leading=11),
        "small": ParagraphStyle("small", fontName="DV", fontSize=7.4, leading=9.2),
        "smallb": ParagraphStyle("smallb", fontName="DVB", fontSize=7.4, leading=9.2),
        "muted": ParagraphStyle("muted", fontName="DVI", fontSize=8, leading=10, textColor=INK2),
        "cover1": ParagraphStyle("c1", fontName="DVB", fontSize=34, leading=40, textColor=STAR, alignment=TA_CENTER),
        "cover2": ParagraphStyle("c2", fontName="DV", fontSize=14, leading=18, textColor=colors.white, alignment=TA_CENTER),
        "cover3": ParagraphStyle("c3", fontName="DV", fontSize=9, leading=12, textColor=colors.HexColor("#a7b0b8"), alignment=TA_CENTER),
    }


    def esc(s):
        return str(s if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


    def P(t, st="small"):
        return Paragraph(esc(t), S[st])


    def rar(x):
        return f'<font color="{RAR.get(x.get("rarity"), "#000")}"><b>{esc(RL(x.get("rarity")))}</b></font>'


    def table(head, rows, widths, font=7.2):
        data = [[Paragraph(f"<font color='#f2c14e'><b>{esc(h)}</b></font>", S["smallb"]) for h in head]] + rows
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG), ("TEXTCOLOR", (0, 0), (-1, 0), STAR),
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTNAME", (0, 0), (-1, -1), "DV"), ("FONTSIZE", (0, 0), (-1, -1), font),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#d5d9de")),
            ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t


    def on_page(canv, doc):
        canv.saveState()
        canv.setFillColor(BG); canv.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
        canv.setFillColor(STAR); canv.setFont("DVB", 9); canv.drawString(14 * mm, A4[1] - 8 * mm, L("ONCE HUMAN — Guide de référence des builds", "ONCE HUMAN — Build reference guide"))
        canv.setFillColor(colors.HexColor("#a7b0b8")); canv.setFont("DV", 8); canv.drawRightString(A4[0] - 14 * mm, A4[1] - 8 * mm, doc.section)
        canv.setFillColor(INK2); canv.drawCentredString(A4[0] / 2, 8 * mm, L(f"Page {doc.page}  ·  données meta-builds.net (jeu v3.0.5) / oncehumandb.com / fandom  ·  v1.7 — 24 sept. 2026", f"Page {doc.page}  ·  data meta-builds.net (game v3.0.5) / oncehumandb.com / fandom  ·  v1.7 — Sep 24, 2026"))
        canv.restoreState()


    class Doc(BaseDocTemplate):
        section = ""

        def afterFlowable(self, f):
            if isinstance(f, Paragraph) and f.style.name == "h1":
                self.section = f.getPlainText()


    def cover(canv, doc):
        canv.saveState(); canv.setFillColor(BG); canv.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canv.setStrokeColor(STAR); canv.setLineWidth(2); canv.line(40 * mm, 150 * mm, A4[0] - 40 * mm, 150 * mm)
        canv.restoreState()


    doc = Doc(os.path.join(HERE, f"Once_Human_Guide_{LANG.upper()}.pdf"), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=18 * mm, bottomMargin=14 * mm,
              title=L("Once Human — Guide de référence des builds", "Once Human — Build reference guide"), author="Once Human planner")
    W = A4[0] - 28 * mm
    frame = Frame(doc.leftMargin, doc.bottomMargin, W, A4[1] - doc.topMargin - doc.bottomMargin, id="f")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=cover), PageTemplate(id="body", frames=[frame], onPage=on_page)])

    st = []
    # ---------------- Couverture
    st += [Spacer(1, 70 * mm), Paragraph("ONCE HUMAN", S["cover1"]), Paragraph(L("Guide de référence des builds", "Build reference guide"), S["cover2"]), Spacer(1, 30 * mm),
           Paragraph(L("Builds recommandés · Armes légendaires · Sets d'armure · Pièces uniques · Déviations · Overrides · Nourriture", "Recommended builds · Legendary weapons · Armor sets · Key Armor · Deviations · Overrides · Food"), S["cover3"]), Spacer(1, 4 * mm),
           Paragraph(L(f"{len(D['weapons'])} armes · {len(D['armor'])} pièces d'armure · {len(D['sets'])-1} sets · {len(D['mods'])} mods · {len(D['deviations'])} déviations · {len(D['cradle'])} overrides", f"{len(D['weapons'])} weapons · {len(D['armor'])} armor pieces · {len(D['sets'])-1} sets · {len(D['mods'])} mods · {len(D['deviations'])} deviations · {len(D['cradle'])} overrides"), S["cover3"]),
           Spacer(1, 4 * mm), Paragraph(L("Version 1.7 — 24 septembre 2026 — compagnon papier de build_planner.html et Once_Human_Builds_FR.xlsx", "Version 1.7 — September 24, 2026 — paper companion of build_planner.html and Once_Human_Builds_EN.xlsx"), S["cover3"])]
    from reportlab.platypus import NextPageTemplate
    st.insert(0, NextPageTemplate("body"))
    st.append(PageBreak())

    # ---------------- Sommaire
    st += [Paragraph(L("Sommaire", "Contents"), S["h1"])]
    toc = L(["0. Builds recommandés", "1. Armes légendaires — fiches détaillées", "2. Toutes les armes — tableau comparatif (dégâts, cadence, DPS)", "3. Sets d'armure — bonus 1/2/3/4 pièces",
           "4. Pièces uniques (Key Armor) — effet propre", "5. Déviations — capacités et lieux d'obtention", "6. Cradle Overrides", "7. Nourriture et peaux d'animaux utiles au combat", "8. Lexique des effets spéciaux"],
          ["0. Recommended builds", "1. Legendary weapons — detailed sheets", "2. All weapons — comparison table (damage, fire rate, DPS)", "3. Armor sets — 1/2/3/4-piece bonuses", "4. Key Armor — own effect", "5. Deviations — abilities and where to get them", "6. Cradle Overrides", "7. Combat-useful food and animal skins", "8. Glossary of special effects"])
    for t in toc:
        st.append(Paragraph(t, S["p"]))
    st += [Spacer(1, 6), Paragraph(L("Les noms d'objets sont ceux du jeu (anglais) pour rester cohérents avec les bases de données ; les effets sont en français lorsqu'ils ont été traduits. DPS théorique = dégâts × cadence ÷ 60, sans crit ni effets : c'est un repère de comparaison, pas une valeur du jeu. Les mentions « résumé » signalent un texte reconstitué depuis des guides plutôt que le texte exact du jeu.", "Item names are the in-game (English) names. Theoretical DPS = damage × fire rate ÷ 60, without crit or effects: a comparison hint, not an in-game value. « summary » marks text reconstructed from guides rather than the exact in-game text."), S["muted"]), PageBreak()]


    # ---------------- 0. Builds recommandés
    st.append(Paragraph(L("0. Builds recommandés", "0. Recommended builds"), S["h1"]))
    st.append(Paragraph(L("Quatre builds PvE. Le premier est le plus destructeur ; le second sert contre les boss immunisés aux statuts (Forsaken Giant) ; le troisième est un tank de soutien pour laisser les coéquipiers faire les dégâts ; le quatrième est un sniper à ricochets (Bounce) pour le point faible. Ils sont préchargés dans l'onglet « Mon build » du planificateur et dans l'onglet Build de l'Excel.",
                           "Four PvE builds. The first is the most destructive; the second is for status-immune bosses (Forsaken Giant); the third is a support tank that lets teammates deal the damage; the fourth is a Bounce sniper built around weakspot hits. All are preloaded in the planner's « My build » tab and in the Excel Build sheet."), S["muted"]))
    SLOT_L = {"w1": L("Arme principale","Primary weapon"), "w2": L("Arme secondaire","Secondary weapon"), "Helmet": L("Casque","Helmet"), "Mask": L("Masque","Mask"), "Top": L("Haut","Top"), "Gloves": L("Gants","Gloves"), "Bottoms": L("Bas","Bottoms"), "Shoes": L("Chaussures","Shoes"), "dev": L("Déviation","Deviation")}
    MODK = {"w1": "wm1", "w2": "wm2", "Helmet": "m_Helmet", "Mask": "m_Mask", "Top": "m_Top", "Gloves": "m_Gloves", "Bottoms": "m_Bottoms", "Shoes": "m_Shoes"}
    BYID = {x["id"]: x for k in ("weapons", "armor", "mods", "deviations") for x in D[k]}
    NOTES = {
     0: L("Mods : un par emplacement, variante <Deviant Energy> (Intensité PSI) partout sauf le haut <Survival>. Alternatives arme : Flame Resonance (+2 stacks max) ou Embers. Overrides : Automatic Weapon Enhancement, LMG Reload Boost, Heat Agglutination, Blazing Detonation, Prairie Fire Inferno, Sustained Suppression, Elemental Sense. Calibration : dég de statut / Intensité PSI puis crit. Pyro Dino déclenche les explosions sur les cibles enflammées : c'est lui qui fait le gros des dégâts sur boss. Alternative gants : Hardy Gloves (explosion 300% PSI à stacks max). Budget ≈ 16 500 Starchrom.",
           "Mods: one per slot, <Deviant Energy> variant (Psi Intensity) everywhere except the top <Survival>. Weapon alternatives: Flame Resonance (+2 max stacks) or Embers. Overrides: Automatic Weapon Enhancement, LMG Reload Boost, Heat Agglutination, Blazing Detonation, Prairie Fire Inferno, Sustained Suppression, Elemental Sense. Calibration: Status DMG / Psi Intensity then crit. Pyro Dino triggers explosions on burning targets and does most of the boss damage. Glove alternative: Hardy Gloves (300% Psi explosion at max stacks). Budget ≈ 16,500 Starchrom."),
     1: L("Mods : variante <Precision> (dég point faible) partout sauf le haut <Survival>. Alternative masque : Explosive Shrapnel (le 20e Shrapnel explose, +300%). Overrides : Rifle Amplify, Precise Shot, Automatic Weapon Enhancement. Lonewolf 5 pièces = crit universel ; Cage Helmet = Shrapnel Trigger Count +1. Lonewolf's Whisper attire l'aggro et augmente les dég d'arme subis par la cible (+21,6%). Build universel n°2, réutilise la Recurve Crossbow.",
           "Mods: <Precision> variant (Weakspot DMG) everywhere except the top <Survival>. Mask alternative: Explosive Shrapnel (20th Shrapnel explodes, +300%). Overrides: Rifle Amplify, Precise Shot, Automatic Weapon Enhancement. Lonewolf 5 pieces = universal crit; Cage Helmet = Shrapnel Trigger Count +1. Lonewolf's Whisper draws aggro and increases Weapon DMG taken by the target (+21.6%). Universal build #2, reuses the Recurve Crossbow."),
    
     2: L("Mods : variante <Survival> (PV) partout. Fortress Warfare (rechargement de la DB12) : réduction de dégâts +30% et dég d'arme +20% pour les alliés dans la zone ; Leather Boots régénère 2,5% PV/s dedans (5%/s sous 50% PV). Savior 3 pièces = bouclier permanent de 6% PV à chaque coup, 4 pièces = soin automatique sous 30%. Ardent Shield = -15% dégâts tant que le bouclier est actif. Festering Gel pose un abri qui soigne 6% PV/s et 3% Santé mentale/s aux alliés (alternative : Dr. Teddy pour relever). Overrides : Shield Protection, Resilience (bouclier -30% dégâts), Deviant Energy Defense, Dexterity, Rapid Aid, Deadly Combo. Peau : Hide (PV max) ou Mountain Cowhide (réduction des crit). Budget ≈ 8 000 (DB12) + 4 × 2 000 (Savior) + Leather Boots.",
          "Mods: <Survival> variant (HP) everywhere. Fortress Warfare (DB12 reload): DMG Reduction +30% and Weapon DMG +20% for allies inside the zone; Leather Boots regenerates 2.5% HP/s inside (5%/s below 50% HP). Savior 3 pieces = permanent 6% HP shield on every hit, 4 pieces = auto-heal below 30%. Ardent Shield = -15% damage while shielded. Festering Gel builds a shelter healing allies 6% HP/s and 3% Sanity/s (alternative: Dr. Teddy to revive). Overrides: Shield Protection, Resilience (shield takes 30% less), Deviant Energy Defense, Dexterity, Rapid Aid, Deadly Combo. Skin: Hide (Max HP) or Mountain Cowhide (Crit DMG reduction). Budget ≈ 8,000 (DB12) + 4 × 2,000 (Savior) + Leather Boots."),
     3: L("Mods : variante <Precision> partout sauf le haut <Survival> : Multi-Bounce (arme), Momentum Up, Break Bounce, Weapon Amplifier, Reload Rampage, Covered Advance. HAMR – Brahminy : 80% de chance de Bounce sur un coup au point faible (ricochet à 60% de l'Attaque, 35% de chance de ricocher encore) ; chaque Bounce raté donne +20% dég d'arme à la balle suivante (max 5). Viser le point faible en permanence. Arme secondaire : Recurve Crossbow (Vulnerability Amplifier) ou AWS.338 – Bullseye pour poser des marques sur le boss. Calibration : dég point faible. Nourriture : Mixed Fried Hot Dog. Peau : Golden Wool. Les réglages fins (mods, calibration) se testent dans l'onglet « ⚙ Optimiseur » du planificateur.",
          "Mods: <Precision> variant everywhere except the top <Survival>: Multi-Bounce (weapon), Momentum Up, Break Bounce, Weapon Amplifier, Reload Rampage, Covered Advance. HAMR – Brahminy: 80% chance to Bounce on a weakspot hit (ricochet at 60% of Attack, 35% chance to bounce again); each missed Bounce gives the next bullet +20% Weapon DMG (max 5). Always aim for the weakspot. Secondary weapon: Recurve Crossbow (Vulnerability Amplifier) or AWS.338 – Bullseye to mark the boss. Calibration: Weakspot DMG. Food: Mixed Fried Hot Dog. Skin: Golden Wool. Fine-tune mods and calibration in the planner's « ⚙ Optimizer » tab."),
    }
    for i, p in enumerate(D["presets"]):
        rows = []
        for k, lab in SLOT_L.items():
            x = BYID.get(p.get(k))
            if not x: continue
            m = BYID.get(p.get(MODK.get(k, ""), ""))
            info = ""
            if x.get("_kind") == "weapons" or k in ("w1", "w2"): info = f'{x["damage"]} {L("dég","dmg")} · {x.get("rpm") or "—"} {L("cpm","rpm")} · {(str(x.get("mag")) + " " + L("balles","rounds")) if x.get("mag") else ""}'
            elif k == "dev": info = ""
            else: info = f'{x["hp"]} {L("PV","HP")} · {x["set"] if x["set"] != "Pièce unique" else L("pièce unique","Key Armor")}'
            rows.append([P(lab), P(x["name"]), P(info), P(f'{m["name"]} <{m["variant"]}>' if m else "—"), P(E(x) or (x.get("effect") or ""))])
        block = [Paragraph(esc(L(p["name"], p.get("name_en", p["name"]))), S["h2"]),
                 table(L(["Emplacement", "Objet", "Stats", "Mod", "Effet"], ["Slot", "Item", "Stats", "Mod", "Effect"]), rows, [24 * mm, 34 * mm, 28 * mm, 34 * mm, W - 120 * mm]),
                 Paragraph(esc(NOTES.get(i, "")), S["p"]), Spacer(1, 6)]
        st.append(KeepTogether(block))
    st.append(PageBreak())

    # ---------------- 1. Armes légendaires
    st.append(Paragraph(L("1. Armes légendaires", "1. Legendary weapons"), S["h1"]))
    leg = sorted([w for w in D["weapons"] if w["rarity"] == "legendary"], key=lambda w: (w["type"], w["name"]))
    for w in leg:
        rows = []
        stats = [(L("Dégâts","Damage"), w["damage"]), (L("Cadence","Fire rate"), f'{w["rpm"]} {L("cpm","rpm")}' if w["rpm"] else None), (L("DPS théorique","Theoretical DPS"), w["dps"]), (L("Chargeur","Magazine"), w["mag"]),
                 (L("Taux crit","Crit rate"), w["critRate"]), (L("Dég crit","Crit DMG"), w["critDmg"]), (L("Point faible","Weakspot"), w["weakspotDmg"]), (L("Portée eff.","Eff. range"), w["rangeEff"]), (L("Recharge","Reload"), w["reloadSec"]),
                 (L("Mobilité","Mobility"), w["mobility"]), (L("Visée","ADS"), w["ads"]), (L("Munitions","Ammo"), w["ammo"])]
        stats = [(k, v) for k, v in stats if v not in (None, "")]
        cells = [Paragraph(f"<font color='#555f68'>{esc(k)}</font><br/><b>{esc(v)}</b>", S["small"]) for k, v in stats]
        if not cells:
            cells = [Paragraph(L("Stats non publiées", "Stats not published"), S["small"])]
        while len(cells) % 6:
            cells.append("")
        grid = Table([cells[i:i + 6] for i in range(0, len(cells), 6)], colWidths=[W / 6] * 6)
        grid.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#d5d9de")), ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e6e9ec")),
                                  ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        block = [Paragraph(f"{esc(w['name'])} <font size=8 color='#555f68'>— {esc(L(w['typeFr'], w['type']))} · {rar(w)}</font>", S["h3"]), grid]
        if E(w):
            block.append(Paragraph(f"<b>{L('Effet','Effect')}{(' — ' + esc(w['effectName'])) if w.get('effectName') else ''} :</b> {esc(E(w))}", S["p"]))
        else:
            block.append(Paragraph(L("Effet spécial : non récupéré (voir la fiche en ligne).", "Special effect: not fetched (see online page)."), S["muted"]))
        if w["craft"]:
            block.append(Paragraph(f"<b>{L('Fabrication','Crafting')}</b> (" + esc(w["bench"]) + ") : " + esc(", ".join(f"{c['name']} ×{c['qty']}" for c in w["craft"])), S["small"]))
        elif w.get("description") and "non craftable" in w["description"]:
            block.append(Paragraph(L("Non fabricable (obtenue en jeu).", "Not craftable (obtained in game)."), S["muted"]))
        if w["overrides"]:
            block.append(Paragraph(f"<b>{L('Overrides compatibles','Compatible overrides')} :</b> " + esc(", ".join(w["overrides"])), S["small"]))
        if w.get("note"):
            block.append(Paragraph(esc(w["note"]), S["muted"]))
        block.append(Spacer(1, 5))
        st.append(KeepTogether(block))
    st.append(PageBreak())

    # ---------------- 2. Tableau de toutes les armes
    st.append(Paragraph(L("2. Toutes les armes — tableau comparatif", "2. All weapons — comparison table"), S["h1"]))
    st.append(Paragraph(L("Trié par type puis par DPS théorique décroissant.", "Sorted by type then by decreasing theoretical DPS."), S["muted"]))
    rows = []
    for w in sorted(D["weapons"], key=lambda w: (w["type"], -(w["dps"] or w["damage"] or 0))):
        rows.append([P(w["name"]), P(L(w["typeFr"], w["type"])), Paragraph(rar(w), S["small"]), P(w["tier"]), P(w["damage"]), P(w["rpm"] or "—"), P(w["dps"] or "—"), P(w["mag"] or "—"), P(w["critRate"] or "—"), P((w.get("effectName") or (E(w)[:60] + "…" if E(w) else "")))])
    st.append(table(L(["Arme", "Type", "Rareté", "T", "Dég", "Cad", "DPS", "Chg", "Crit", "Effet"], ["Weapon", "Type", "Rarity", "T", "Dmg", "Rate", "DPS", "Mag", "Crit", "Effect"]), rows, [44 * mm, 22 * mm, 17 * mm, 6 * mm, 10 * mm, 10 * mm, 11 * mm, 9 * mm, 10 * mm, W - 139 * mm]))
    st.append(PageBreak())

    # ---------------- 3. Sets d'armure
    st.append(Paragraph(L("3. Sets d'armure", "3. Armor sets"), S["h1"]))
    byid = {a["id"]: a for a in D["armor"]}
    for s in sorted([s for s in D["sets"] if s["name"] != "Pièce unique"], key=lambda s: ({"legendary": 0, "epic": 1, "rare": 2, "uncommon": 3}.get(s["rarity"], 9), s["name"])):
        pieces = [byid[i] for i in s["pieces"]]
        hp = sum(int(a["hp"] or 0) for a in pieces)
        block = [Paragraph(f"{esc(s['name'])} <font size=8 color='#555f68'>— {len(pieces)} {L('pièces','pieces')} · {L('PV total','Total HP')} {hp} · <font color='{RAR.get(s['rarity'], '#000')}'><b>{esc(RL(s['rarity']))}</b></font></font>", S["h3"])]
        if s["bonus"]:
            block.append(table([L("Pièces","Pieces"), "Bonus"], [[P(f"{b['pieces']}"), P(b["effect"])] for b in s["bonus"]], [14 * mm, W - 14 * mm]))
        else:
            block.append(Paragraph(L("Bonus non récupérés.", "Bonuses not fetched."), S["muted"]))
        block.append(Paragraph(L("Pièces : ","Pieces: ") + esc(", ".join(f"{a['name']} ({a['hp']} {L('PV','HP')})" for a in sorted(pieces, key=lambda a: a['slot']))), S["small"]))
        block.append(Spacer(1, 5))
        st.append(KeepTogether(block))
    st.append(PageBreak())

    # ---------------- 4. Pièces uniques
    st.append(Paragraph(L("4. Pièces uniques (Key Armor)", "4. Key Armor"), S["h1"]))
    st.append(Paragraph(L("Une seule pièce unique active à la fois. Elles n'ont pas de bonus de set mais un effet propre qui renforce un effet d'arme précis.", "Only one Key Armor piece is active at a time. They have no set bonus but an own effect that boosts a specific weapon effect."), S["muted"]))
    uniq = sorted([a for a in D["armor"] if a["set"] == "Pièce unique"], key=lambda a: (a["slot"], a["name"]))
    st.append(table(L(["Pièce", "Emplacement", "Rareté", "PV", "Effet"], ["Piece", "Slot", "Rarity", "HP", "Effect"]), [[P(a["name"]), P(L(a["slotFr"], a["slot"])), Paragraph(rar(a), S["small"]), P(a["hp"]), P(E(a) or L("non récupéré","not fetched"))] for a in uniq],
                    [40 * mm, 20 * mm, 18 * mm, 9 * mm, W - 87 * mm]))
    st.append(PageBreak())

    # ---------------- 5. Déviations
    st.append(Paragraph(L("5. Déviations", "5. Deviations"), S["h1"]))
    for typ, label in (("Combat", L("Déviations de combat","Combat deviations")), ("Territory", L("Déviations de territoire","Territory deviations")), ("Crafting", L("Déviations de fabrication","Crafting deviations"))):
        LL = sorted([d for d in D["deviations"] if d["type"] == typ], key=lambda d: d["name"])
        st.append(Paragraph(label, S["h2"]))
        st.append(table(L(["Déviation", "Rareté", "Capacités", "Où l'obtenir"], ["Deviation", "Rarity", "Abilities", "Where to get"]), [[P(d["name"]), Paragraph(rar(d), S["small"]), P(d["effect"]), P(d.get("location") or "—")] for d in LL],
                        [34 * mm, 18 * mm, W - 92 * mm, 40 * mm]))
    st.append(PageBreak())

    # ---------------- 6. Overrides
    st.append(Paragraph("6. Cradle Overrides", S["h1"]))
    for sty in sorted(set(c["style"] for c in D["cradle"])):
        LL = sorted([c for c in D["cradle"] if c["style"] == sty and (c.get("current") or not any(x.get("current") for x in D["cradle"]))], key=lambda c: c["name"])
        st.append(Paragraph(f"{sty} ({len(LL)})", S["h2"]))
        st.append(table(["Override", L("Effet","Effect")], [[P(c["name"]), P(c["effect"])] for c in LL], [45 * mm, W - 45 * mm]))
    st.append(PageBreak())

    # ---------------- 7. Nourriture & peaux
    st.append(Paragraph(L("7. Nourriture et peaux d'animaux", "7. Food and animal skins"), S["h1"]))
    kw = ("dmg", "crit", "weakspot", "hp", "attack", "psi", "fire rate", "reload", "shrapnel", "burn", "bounce", "surge", "vortex", "bull", "bomber", "gunner", "fortress")
    food = sorted([f for f in D["food"] if f["rarity"] in ("legendary", "epic", "rare") and any(k in (f["effect"] or "").lower() for k in kw)], key=lambda f: ({"legendary": 0, "epic": 1, "rare": 2}[f["rarity"]], f["name"]))
    st.append(Paragraph(L(f"Plats à effet de combat (rares, épiques, légendaires) — {len(food)} sur {len(D['food'])}", f"Combat-effect dishes (rare, epic, legendary) — {len(food)} of {len(D['food'])}"), S["h2"]))
    st.append(table(L(["Plat", "Rareté", "Effet"], ["Dish", "Rarity", "Effect"]), [[P(f["name"]), Paragraph(rar(f), S["small"]), P(f["effect"])] for f in food], [40 * mm, 18 * mm, W - 58 * mm]))
    st.append(Paragraph(L("Peaux d'animaux (attribut ajouté à l'armure fabriquée)", "Animal skins (attribute added to crafted armor)"), S["h2"]))
    SLF = {"Helmet": L("Casque", "Helmet"), "Mask": L("Masque", "Mask"), "Top": L("Haut", "Top"), "Gloves": L("Gants", "Gloves"), "Bottoms": L("Bas", "Bottoms"), "Shoes": L("Chaussures", "Shoes")}
    HS = {h["family"]: h for h in D.get("hideSets", [])}
    skins = sorted([s for s in D["skins"] if not s.get("legacy")], key=lambda s: s["name"])
    st.append(Paragraph(L("L'effet d'une peau dépend de la pièce d'armure où elle est utilisée. Les peaux Lunar doublent leur effet sous 30 % de PV (builds low life).",
                          "A hide's effect depends on the armor piece it is used on. Lunar hides double their effect below 30% HP (low-life builds)."), S["muted"]))
    st.append(table(L(["Peau", "Set ×4", "Effet selon la pièce"], ["Hide", "Set ×4", "Effect by armor piece"]),
                    [[P(s["name"]), P(L(HS[s["family"]]["fr"], HS[s["family"]]["name"]) if s.get("family") in HS else "—"), Paragraph("<br/>".join(f"<b>{SLF.get(k, k)}</b> : {esc(v)}" for k, v in (s.get("slotEffects") or {}).items()) or esc(s["effect"]), S["small"])] for s in skins],
                    [36 * mm, 24 * mm, W - 60 * mm]))
    st.append(Paragraph(L("Sets de peaux (4 pièces de la même famille)", "Hide sets (4 pieces of the same family)"), S["h2"]))
    st.append(table(L(["Set", "Famille", "Effet"], ["Set", "Family", "Effect"]), [[P(L(f"{h['fr']} ({h['name']})", h["name"])), P(h["families"]), P(L(h["effect"], h["effectEn"]))] for h in D.get("hideSets", [])], [45 * mm, 30 * mm, W - 75 * mm]))
    st.append(Paragraph(L("Source : relevés communautaires (sept. 2026), non publiés dans les notes de mise à jour officielles — à vérifier en jeu. On suppose que les variantes (Lunar, Dreamfused, Forest…) comptent pour leur famille.",
                          "Source: community findings (Sept 2026), not published in the official patch notes — check in game. Variants (Lunar, Dreamfused, Forest…) are assumed to count for their family."), S["muted"]))
    st.append(PageBreak())

    # ---------------- 8. Lexique
    st.append(Paragraph(L("8. Lexique des effets spéciaux", "8. Glossary of special effects"), S["h1"]))
    lex = [
        ("Shrapnel", "À l'impact, inflige une part de l'Attaque en dég d'arme sur une autre partie du corps de l'ennemi. Peut critiquer et toucher les points faibles. Armes : SOCR - The Last Valor. Pièces : Beret, Cage Helmet, Gas-tight Helmet."),
        ("Burn", "Brûlure : dég de Blaze sur la durée, cumulable. Armes : KVD - Boom! Boom!, ACS12 - Pyroclasm Starter. Pièces : BBQ Gloves, Hardy Gloves, Drifter Gauntlets, Fire Rune Boots. Déviation : Pyro Dino, Invincible Sun."),
        ("Power Surge", "Décharge de Shock : dég de statut basés sur l'Intensité PSI, réduit la précision de la cible. Armes : MPS7 - Outer Space, ACS12 - Corrosion, SOCR - Outsider, Critical Pulse. Pièces : Gas Mask Hood, Mayfly Goggles, Overloaded Pants, Yellow Painted Mask."),
        ("The Bull's Eye", "Marque la cible (Vulnérabilité +8% pendant 12 s). Armes : AWS.338 - Bullseye, DBSG - Doombringer, DE.50 - Wildfire, Recurve Crossbow. Pièces : Earthly Boots, Old Huntsman Boots, Tactical Combat Shoes. Déviation : Mr. Wish."),
        ("Bounce", "La balle ricoche sur un ennemi proche (part de l'Attaque en dég d'arme). Armes : HAMR - Brahminy, MPS5 - Kumawink. Pièces : Hot Dog Shorts, Sharp Blade Pants, Tattoo Pants. Déviation : Mini Feaster."),
        ("Fast Gunner", "Stacks de cadence/Attaque à chaque coup, munitions infinies par paliers. Armes : MG4 - Predator. Pièces : Charmed Mag Top, Desert Dust Mask, Oasis Mask, Precise Shot Mask."),
        ("Fortress Warfare", "Zone déclenchée au rechargement : armure lourde, dég d'arme +20%, crit et réduction de dég. Armes : DB12 - Raining Cash. Pièces : Cowboy Boots, Tactical Combat Boots, Leather Boots."),
        ("Unstable Bomber", "Explosion de statut basée sur l'Intensité PSI dans une petite zone. Armes : DE.50 - Jaws, G17 - Hazardous Object. Pièces : Viper Mask, Explosive Front Top, Sleek Leather Jacket."),
        ("Frost Vortex", "Zone de 4,5 m qui piège et gèle, dég de Frost par seconde. Armes : KAM - Abyss Glance, M416 - Silent Anabasis, DB12 - Backfire. Pièces : Frost Tactical Vest, Doyen's Cloak, Snow Camo Gloves, Covert Walker Shirt. Déviations : Polar Jelly, Snowsprite."),
        ("Sets à retenir", "Lonewolf (crit universel), Shelterer (élémentaire, on-hit), Renegade (point faible), Falcon (dég crit, accessible), Bastille (dég d'arme immobile), Agent (point faible/rechargement), Heavy Duty (élémentaire on-kill), Savior (survie)."),
    ]
    lex_en = [
        ("Shrapnel", "On hit, deals part of Attack as Weapon DMG to another body part of the enemy. Can Crit and hit Weakspots. Weapons: SOCR - The Last Valor. Pieces: Beret, Cage Helmet, Gas-tight Helmet."),
        ("Burn", "Blaze damage over time, stackable. Weapons: KVD - Boom! Boom!, ACS12 - Pyroclasm Starter. Pieces: BBQ Gloves, Hardy Gloves, Drifter Gauntlets, Fire Rune Boots. Deviations: Pyro Dino, Invincible Sun."),
        ("Power Surge", "Shock discharge: Status DMG based on Psi Intensity, reduces target accuracy. Weapons: MPS7 - Outer Space, ACS12 - Corrosion, SOCR - Outsider, Critical Pulse. Pieces: Gas Mask Hood, Mayfly Goggles, Overloaded Pants, Yellow Painted Mask."),
        ("The Bull's Eye", "Marks the target (Vulnerability +8% for 12s). Weapons: AWS.338 - Bullseye, DBSG - Doombringer, DE.50 - Wildfire, Recurve Crossbow. Pieces: Earthly Boots, Old Huntsman Boots, Tactical Combat Shoes. Deviation: Mr. Wish."),
        ("Bounce", "The bullet ricochets to a nearby enemy (part of Attack as Weapon DMG). Weapons: HAMR - Brahminy, MPS5 - Kumawink. Pieces: Hot Dog Shorts, Sharp Blade Pants, Tattoo Pants. Deviation: Mini Feaster."),
        ("Fast Gunner", "Fire rate/Attack stacks on each hit, infinite ammo at thresholds. Weapons: MG4 - Predator. Pieces: Charmed Mag Top, Desert Dust Mask, Oasis Mask, Precise Shot Mask."),
        ("Fortress Warfare", "Zone triggered on reload: heavy armor, Weapon DMG +20%, crit and DMG reduction. Weapons: DB12 - Raining Cash. Pieces: Cowboy Boots, Tactical Combat Boots, Leather Boots."),
        ("Unstable Bomber", "Psi-Intensity-based status explosion in a small area. Weapons: DE.50 - Jaws, G17 - Hazardous Object. Pieces: Viper Mask, Explosive Front Top, Sleek Leather Jacket."),
        ("Frost Vortex", "4.5m area that traps and freezes, Frost DMG per second. Weapons: KAM - Abyss Glance, M416 - Silent Anabasis, DB12 - Backfire. Pieces: Frost Tactical Vest, Doyen's Cloak, Snow Camo Gloves, Covert Walker Shirt. Deviations: Polar Jelly, Snowsprite."),
        ("Sets to remember", "Lonewolf (universal crit), Shelterer (elemental, on-hit), Renegade (weakspot), Falcon (crit DMG, accessible), Bastille (weapon DMG while still), Agent (weakspot/reload), Heavy Duty (elemental on-kill), Savior (survival)."),
    ]
    for k, v in L(lex, lex_en):
        st.append(Paragraph(f"<b>{esc(k)}</b> — {esc(v)}", S["p"]))

    doc.build(st)
    print("PDF", LANG)


for _l in ("fr", "en"):
    gen(_l)
