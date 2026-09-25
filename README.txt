ONCE HUMAN — Planificateur de build (version 1.6 — 25 septembre 2026)
=====================================================================
À déposer dans : C:\Users\Moana\Documents\CLAUDE\ONCE_HUMAN

FICHIERS
  build_planner.html      NOUVEAU (v1.6, 25 sept. 2026) : onglet « ⚙ Optimiseur ». Tu choisis une arme et un
                          objectif (DPS, dégâts crit, taux crit, point faible, élémentaire/statut, mécanique de
                          l'arme, survie), tu cliques « Optimiser » : le moteur lit la mécanique de l'arme
                          (Shrapnel, Brûlure, Rebond, Dans le mille, Tireur rapide, Lutte retranchée, Surtension,
                          Vortex de givre, Bombe instable), son type et ses stats de base, et calcule la meilleure
                          combinaison de sets (+ pièce unique), mods + suffixes, peaux, déviation, 8 overrides et
                          nourriture, avec le « pourquoi » de chaque choix, 2 alternatives d'armure, un DPS
                          théorique avant/après et un bouton « Charger dans Mon build ». Si la mécanique d'une arme
                          n'est pas renseignée, tu peux la choisir à la main.
                          Limites : moteur de score (effets du jeu pondérés), pas le calcul exact du jeu ; effets
                          conditionnels comptés partiellement ; peaux = combinaisons relevées en jeu.
                          4e build préchargé : Sniper Rebond — HAMR Brahminy (ton build).
                          Interface interactive BILINGUE (bouton FR/EN en haut à droite). Deux builds
                          recommandés sont préchargés (« Charger un build… ») : Burn / KVD Boom! Boom!
                          et Shrapnel / SOCR The Last Valor.
                          Interface interactive : ouvre-la dans Chrome/Edge/Firefox (double-clic).
                          Onglets Armes / Armures / Mods / Déviations / Overrides / Nourriture /
                          Calibrations / Peaux, recherche, filtres, tri, fiche détaillée, images,
                          et l'onglet "Mon build" (emplacements + résumé DPS / PV / sets / effets).
                          Les builds sont sauvegardés dans le navigateur ; Exporter/Importer en JSON.
                          Connexion internet nécessaire pour afficher les images.
  Once_Human_Builds_FR.xlsx / _EN.xlsx  Même chose en Excel (français / anglais), build Burn pré-rempli : onglet "Build" avec listes déroulantes (cellules
                          jaunes) et calcul automatique, puis un onglet par catégorie (filtrable,
                          liens "ouvrir" vers la fiche et l'image).
  resource_map.html       Carte interactive des ressources (schématique) : régions de Nalcott + Way of Winter,
                          animaux → peaux, minerais → lingots/composants, silos/monoliths, chercheur de ressource,
                          liens vers les points exacts (oncehuman.th.gl). Bilingue FR/EN.
  Once_Human_Guide_FR.pdf / _EN.pdf  Guide imprimable (builds recommandés + toutes les données)
  data\*.json             Données brutes (source : oncehumandb.com, extraites des fichiers du jeu).
  data\details\*.json     Compléments récupérés fiche par fiche (crit, chargeur, recettes, bonus
                          de set…). Se remplissent au fil des étapes suivantes.
  generate.py, gen_pdf.py, lib_data.py, template.html
                          Générateur : "python generate.py" reconstruit le HTML et les Excel, "python gen_pdf.py" les PDF.

ÉTAT DES DONNÉES
  Inclus : nom, type/emplacement, rareté, dégâts, cadence, DPS théorique, PV, effets des mods,
           effets des déviations/overrides/nourriture, images, lien vers chaque fiche.
  Étape 1 faite : 32 armes légendaires (sur 35) avec crit / dég crit / point faible / chargeur /
           recharge / mobilité / portée / chute de dégâts / munitions / mode de tir / recette + atelier /
           overrides compatibles ; 17 armes avec le texte de l'effet spécial (Shrapnel, Burn, Bull's Eye,
           Power Surge, Bounce, Fast Gunner, Fortress Warfare, Unstable Bomber, Frost Vortex…).
           Manquent encore : Kukri, G17 - Cash Only, Star Vortex (fiches non indexées) et les effets
           spéciaux de ~15 légendaires.
  Étape 2 faite : les 20 sets d'armure (Lonewolf, Shelterer, Bastille, Renegade, Falcon, Blackstone ×3,
           Savior, Stormweaver, Agent, Heavy Duty, Blast, Raid, Scout, Gravity Tide, Treacherous Tides,
           Snow Panther, Rustic, Snowland Rustic) avec leurs bonus 1/2/3/4 pièces, vrais noms de set et
           résistance pollution par pièce. Les bonus de set actifs s'affichent dans le résumé du build.
           Nouvel onglet Excel « Sets ».
  Étape 3 faite : 31 pièces uniques (Key Armor) avec leur effet propre en français (Viper Mask, Frost
           Tactical Vest, Doyen's Cloak, Charmed Mag Top, BBQ Gloves…) ; set Dark Resonance (résumé) ;
           4 effets d'armes de plus (Kumawink, Abyss Glance, Silent Anabasis, Critical Pulse) ; 63 déviations
           avec capacités complètes et lieu d'obtention (colonne « Où l'obtenir »).
  Manquent encore : recettes de fabrication des armures ; effets exacts de ~11 légendaires (Chaos Domain,
           Outer Space détaillé, Primal Rage, TEC9, Hannya, Format, Little Jaws, PDW90, Star Vortex, Kukri,
           G17 Cash Only, Conflicting Memories, EBR-14, SKS, Ultra Force, Aurora Fort) ; quelques pièces
           récentes (Bloodstained Tracker Boots, Gilded Palm Shield, Pivot Step Leather Boots, Snowdrift Top) ;
           déviations récentes (Behemoth, Blackback, Chillet, Whalepup, Watcher, Zapamander…).
  À venir : armes épiques/rares, recettes d'armures, mise à jour des données brutes à chaque patch.
  Les noms restent en anglais (comme sur les bases de données), l'interface est en français.
