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

Moteur de score (effets du jeu pondérés), pas la formule exacte du jeu : les gains affichés sont indicatifs.

## Régénérer les fichiers / Rebuild

Python 3 + `openpyxl` et `reportlab` :

```
python generate.py   # build_planner.html + Excel FR/EN
python gen_pdf.py    # guides PDF FR/EN
```

Structure : `data/*.json` (données brutes, oncehumandb.com), `data/details/*.json` (compléments : stats, sets, pièces uniques, déviations, builds préchargés), `template.html` + `optimizer.js` (interface), `lib_data.py` (fusion des données).

## Sources

oncehumandb.com (données extraites des fichiers du jeu), once-human.fandom.com, wikily.gg, guides communautaires. Once Human est une marque de Starry Studio / NetEase ; projet de fan non officiel.
