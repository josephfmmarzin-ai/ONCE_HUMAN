# ONCE HUMAN — Planificateur de build / Build planner

Outil bilingue (FR/EN) pour préparer ses builds dans **Once Human** : base de données des armes, armures, sets, mods, déviations, overrides et nourriture, planificateur de build, **optimiseur automatique selon l'arme**, carte des ressources, classeurs Excel et guides PDF.

Bilingual (FR/EN) build toolkit for **Once Human**: weapons, armor, sets, mods, deviations, overrides and food database, build planner, **weapon-aware optimizer**, resource map, Excel workbooks and PDF guides.

## Utilisation / Usage

Ouvrir `build_planner.html` dans Chrome, Edge ou Firefox (double-clic). Aucune installation.
Open `build_planner.html` in Chrome, Edge or Firefox. Nothing to install.

| Fichier / File | Contenu / Content |
|---|---|
| `build_planner.html` | Planificateur interactif : onglets de données, « Mon build », **⚙ Optimiseur**, 4 builds préchargés (Burn, Shrapnel, Tank, Sniper Rebond) |
| `resource_map.html` | Carte schématique des ressources (animaux, minerais, régions) |
| `Once_Human_Builds_FR.xlsx` / `_EN.xlsx` | Classeurs avec listes déroulantes et calculs |
| `Once_Human_Guide_FR.pdf` / `_EN.pdf` | Guides imprimables |

## Optimiseur

Choisir une arme et un objectif (DPS, dégâts crit, taux crit, point faible, élémentaire/statut, mécanique de l'arme, survie) puis « Optimiser ». Le moteur lit la mécanique de l'arme (Shrapnel, Brûlure, Rebond, Dans le mille, Tireur rapide, Lutte retranchée, Surtension, Vortex de givre, Bombe instable), son type et ses stats de base, et calcule sets + pièce unique, mods + suffixes, peaux, déviation, overrides et nourriture, avec la justification de chaque choix.

**Style de PV** (v1.7) : Normal, Semi-low life (≤ 50 % PV) ou Low life / Lunar (< 30 % PV). Les effets liés aux PV et les suffixes / peaux Lunar sont pris en compte selon le style — les builds Lunar sont en général les plus destructeurs.

**Sets de peaux** (v1.7) : 4 peaux de la même famille (Soaring Leap, Wolf Pack, Stag…) — source communautaire.

Moteur de score (effets du jeu pondérés), pas la formule exacte du jeu : les gains affichés sont indicatifs.

## Régénérer les fichiers / Rebuild

Python 3 + `openpyxl` et `reportlab` :

```
python generate.py   # build_planner.html + Excel FR/EN
python gen_pdf.py    # guides PDF FR/EN
```

Structure : `data/*.json` (données de base, oncehumandb.com), `data/metabuilds/` (export meta-builds.net, source à jour), `data/details/*.json` (compléments : sets, pièces uniques, déviations FR, sets de peaux, builds préchargés), `template.html` + `optimizer.js` (interface, injectés par `generate.py`), `lib_data.py` + `mb_merge.py` (fusion des données).

Mise à jour : enregistrer https://meta-builds.net/api/get/allData dans `data/metabuilds/allData.json`, puis relancer les deux scripts.

## Sources

meta-builds.net (base à jour, jeu v3.0.5), oncehumandb.com (données extraites des fichiers du jeu), once-human.fandom.com, wikily.gg, guides communautaires. Once Human est une marque de Starry Studio / NetEase ; projet de fan non officiel.
