ONCE HUMAN — Build planner (version 1.6 — September 25, 2026)
==============================================================
Drop the folder in: C:\Users\Moana\Documents\CLAUDE\ONCE_HUMAN

FILES
  build_planner.html        NEW (v1.6): « ⚙ Optimizer » tab. Pick a weapon and a goal (DPS, crit damage, crit rate,
                            weakspot, elemental/status, weapon mechanic, survival) and click « Optimize »: the engine
                            reads the weapon's mechanic, type and base stats and computes the best sets (+ Key Armor),
                            mods + suffixes, skins, deviation, 8 overrides and food, with the reason for each pick,
                            2 armor alternatives, a before/after theoretical DPS and « Load into My build ».
                            Scoring engine, not the exact in-game formula. 4th preset: Sniper Bounce — HAMR Brahminy.
                            Interactive bilingual interface (FR/EN button top right). Open it in Chrome/Edge/Firefox.
                            Tabs Weapons / Armor / Mods / Deviations / Overrides / Food / Calibrations / Skins,
                            search, filters, sort, detail sheet with image, and the "My build" tab (slots + summary:
                            DPS / HP / sets / active effects). Two recommended builds are preloaded ("Load a build…"):
                            Burn / KVD Boom! Boom! and Shrapnel / SOCR The Last Valor. Builds are saved in the browser;
                            export/import as JSON. Internet needed to display images.
  Once_Human_Builds_EN.xlsx Same in Excel (FR version: _FR): "Build" sheet with dropdowns (yellow cells) and automatic
                            calculations, then one sheet per category (filterable, "open" links to page and image).
  resource_map.html         Interactive (schematic) resource map: Nalcott + Way of Winter regions, animals → hides,
                            ores → ingots/components, silos/monoliths, resource finder, links to exact spawn points
                            (oncehuman.th.gl). Bilingual FR/EN.
  Once_Human_Guide_EN.pdf   Printable reference guide (FR version: _FR): recommended builds + all data.
  data\*.json               Raw data (source: oncehumandb.com, extracted from game files).
  data\details\*.json       Enrichments fetched page by page (crit, magazine, recipes, set bonuses, key armor effects,
                            deviation abilities). effectEn = English text, effect = French text.
  generate.py, gen_pdf.py, lib_data.py, template.html
                            Generators: "python generate.py" rebuilds the HTML and both Excel files, "python gen_pdf.py" the PDFs.

DATA STATUS
  Included: name, type/slot, rarity, damage, fire rate, theoretical DPS, HP, mod effects, deviation/override/food effects,
           images, link to each page; 32/35 legendary weapons with full stats (crit, magazine, reload, mobility, range,
           falloff, ammo, fire mode, recipe + bench, compatible overrides); 21 weapons with special effect text;
           20 armor sets with 1/2/3/4-piece bonuses and pollution resist; 31 Key Armor pieces with their own effect;
           63/80 deviations with full abilities and location.
  Still missing: armor crafting recipes; exact effects of ~11 secondary legendaries; a few recent armor pieces;
           ~17 recent deviations. Item names are the in-game (English) names.
