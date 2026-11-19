"""Catalogue du skin : catégories (= endroits du jeu, un dossier de outils\\ chacune) et fonctions (= un script chacune,
activable seule). Données seulement : lues par lancer.py (menu de Outils FM.bat, choix 1, statut) et, plus tard, par
la vraie app.

Ajouter une fonction : son script dans le dossier de sa catégorie (marqueur backups\\<marqueur>.actif), une entrée dans
FONCTIONS (dans sa catégorie, ordre affiché), et son nom dans ORDRE_SKIN (ordre du choix 1).
"""

# (dossier, titre fr, titre en) ; numéro du menu = 11 + rang
CATEGORIES = [
    ("joueur_entete", "Joueur : en-tête de la fiche", "Player: profile header"),
    ("joueur_fiche", "Joueur : fiche (infos, attributs, Pour / Contre)", "Player: profile (info, attributes, pros / cons)"),
    ("joueur_infobulle", "Joueur : infobulle (survol d'un joueur)", "Player: tooltip (hovering a player)"),
    ("joueur_progression", "Joueur : progression", "Player: development"),
    ("staff", "Staff", "Staff"),
    ("club", "Club : page du club et installations", "Club: club page and facilities"),
    ("finances", "Finances", "Finances"),
    ("effectif", "Effectif et dynamique de groupe", "Squad and dynamics"),
    ("entrainement", "Entraînement", "Training"),
    ("tactiques", "Tactiques", "Tactics"),
    ("match", "Match", "Match"),
    ("calendrier", "Calendrier", "Calendar"),
    ("tableaux", "Tableaux de joueurs (colonnes)", "Player tables (columns)"),
    ("haut_du_jeu", "Haut de l'écran", "Top of the screen"),
    ("theme", "Couleurs (fond, barres du haut, accent)", "Colours (background, top bars, accent)"),
    # ajouts de Kinito (outils\kinito\, scripts gardés tels quels) : app = section Kinito de la page « Features
    # additionnelles » (ex-Options), pas dans « Fonctions du skin ». De base (2026-11-12) : tous activés sauf les
    # facultatifs (26.1, 26.3 ; 26.13 depuis le 2026-11-12 ; 26.17 de base, 2026-11-12) ; ses Rencontres
    # (26.2, 26.9) : option « rencontres », version Kinito de base
    ("kinito", "Kinito", "Kinito"),
    # 2026-11-12 : après Kinito pour ne pas décaler les numéros du menu (27)
    ("recrutement", "Recrutement", "Scouting"),
    # 2026-11-12 : vues de tableaux d'AlexJeuVideal (app : section en haut de « Features additionnelles », au-dessus
    # de Kinito ; fichiers .json copiés dans LocalLow, aucun fichier du jeu touché)
    ("vues", "Vues de tableaux d'AlexJeuVideal", "AlexJeuVideal's table views"),
    # 2026-11-07 : à la fin pour ne pas décaler les numéros du menu (29)
    ("separateur", "Séparateurs (tableaux)", "Separators (tables)"),
    # 2026-11-12 : patch du code de FM (GameAssembly.dll), pas des bundles (30). 2026-11-14 (le joueur) : app = toutes
    # les fonctions qui touchent au jeu lui-même (DLL, données du moteur de match : CAT_APP de page.html), facultatives
    ("affichage", "Modifications du jeu (code et données de FM)", "Game changes (FM's code and data)"),
]
PREMIER_NUMERO = 11

# script (= nom du fichier sans .py, unique) : catégorie, titre fr, titre en, et au besoin :
#   marqueur (défaut = script), textes (textes fixes fr / en : refait au changement de langue), facultatif (pas
#   activé = choix de la personne), toujours (réécrit à chaque passage : le statut ne regarde que le marqueur)
# rappel des fonctions qui touchent des tuiles / dispositions de page (le joueur, 2026-11-01, pour la release) : une
# disposition gardée par FM (CustomGridCompositions) passe avant le skin
RESET_DISPOSITIONS = ("Changement pas visible ? Une disposition de la page gardée par FM passe avant le skin : "
                      "réinitialiser les dispositions dans les Préférences de FM (ou dans le menu des tuiles de la page).",
                      "Change not showing? A page layout kept by FM takes priority over the skin: reset the layouts "
                      "in FM's Preferences (or in the page's tiles menu).")

FONCTIONS = {
    # --- Joueur : en-tête de la fiche ---
    "entete_fiche": dict(cat="joueur_entete",
                         fr="2e nationalité, Pour / Contre en pastilles, bouton Actions sous l'âge et nationalités "
                            "en 3 lettres (mode Large), "
                            "Niveau / Potentiel serrés",
                         en="2nd nationality, Pros / Cons badges, Actions button under the age and 3-letter "
                            "nationalities (Large mode), "
                            "tighter Ability / Potential"),
    # --- Joueur : fiche ---
    "style_mediatique": dict(cat="joueur_fiche",
                             fr="Style médiatique sous Personnalité, Réputation en bas, pieds écartés",
                             en="Media handling under Personality, Reputation last, feet spread out"),
    "temperament_infos": dict(cat="joueur_fiche",   # 2026-11-13, validé ; jamais en vue Guru (hors AVEC_GURU)
                              fr="Logo du tempérament à droite de la personnalité (fiche : nom au survol ; aussi "
                                 "dans l'infobulle du joueur)",
                              en="Mindset icon right of the personality (profile: name on hover; also in the "
                                 "player tooltip)"),
    "hors_defaut": dict(cat="joueur_fiche",
                        fr="Options d'entraînement sous les attributs (s'il y a la place)",
                        en="Training options under the attributes (when there is room)"),
    "fiche_joueur_plus": dict(cat="joueur_fiche", textes=True,   # textes : « Entraînement », « Projets »... (v1.56)
                              fr="Pour / Contre à la place du polygone (bouton pour revoir le polygone), bloc Entraînement (note, pouces, roue), logos Hiérarchie / Groupe ; "
                                 "Large : polygone à droite d'Infos, comme la vue Guru ; "
                                 "Small : Pour / Contre sous les attributs, polygone et Projets à droite, Suspensions / éligibilité / langues sous les postes, Rôles / Priorité / Intensité dans le bloc Entraînement",
                              en="Pros / Cons instead of the polygon (button to show the polygon back), Training block (rating, thumbs, cog), Hierarchy / Group icons; "
                                 "Large: polygon to the right of Info, like the Guru view; "
                                 "Small: Pros / Cons under the attributes, polygon and Plans on the right, Suspensions / eligibility / languages under the positions, Roles / Focus / Intensity in the Training block"),
    "listes_pour_contre": dict(cat="joueur_fiche",
                               fr="Listes Pour / Contre en pastilles colorées",
                               en="Pros / Cons lists as coloured badges"),
    "suspensions_noms_courts": dict(cat="joueur_fiche",   # 2026-11-12
                                    fr="Suspensions : nom court des compétitions (C/B, CSC...)",
                                    en="Bans: short competition names"),
    "tuile_forme": dict(cat="joueur_fiche", textes=True,   # 2026-11-12 (titre « État du joueur »)
                        fr="Tuile « État du joueur » : physique (condition, forme, fatigue) et mental (état "
                           "d'esprit, moral) ; logos Hiérarchie / Groupe à droite de Taille ; fiche : tuiles État "
                           "d'esprit (+ moral) et Condition (+ forme, fatigue) pareilles (essai)",
                        en="\"Player status\" tile: physical (condition, sharpness, fatigue) and mental "
                           "(happiness, morale); Hierarchy / Group icons next to Height; profile: Happiness (+ morale) "
                           "and Condition (+ sharpness, fatigue) tiles to match (test)",
                        aide=RESET_DISPOSITIONS),
    "fiche_ordre_tuiles": dict(cat="joueur_fiche",   # 2026-11-12, le joueur
                               fr="Vue d'ensemble : tuiles du bas dans l'ordre État d'esprit, Condition physique, "
                                  "Stats saison, Stats carrière, Forme, Blessures (Entraînement dans le menu de la "
                                  "tuile)",
                               en="Overview: bottom tiles in the order Happiness, Condition, Season stats, Career "
                                  "stats, Form, Injuries (Training in the tile's menu)",
                               aide=RESET_DISPOSITIONS),
    "tuile_carriere": dict(cat="joueur_fiche", textes=True,   # 2026-11-01, le joueur
                           fr="Tuile Stats carrière en tableau : une ligne par saison (club, matchs, buts, passes D ; "
                              "gardien : encaissés, clean sheets), total en bas, toutes les tailles",
                           en="Career stats tile as a table: one row per season (club, apps, goals, assists; "
                              "goalkeeper: conceded, clean sheets), total at the bottom, every size",
                           aide=RESET_DISPOSITIONS),
    "tuile_blessures": dict(cat="joueur_fiche",   # 2026-11-13, le joueur
                            fr="Tuile Historique des blessures : toutes les blessures du joueur en liste (date, "
                               "blessure, durée)",
                            en="Injury history tile: all the player's injuries as a list (date, injury, "
                               "duration)",
                            aide=RESET_DISPOSITIONS),
    "couleurs_polygone": dict(cat="joueur_fiche",   # 2026-11-12, le joueur
                              fr="Chiffres du polygone aux couleurs des attributs (réglées dans le jeu)",
                              en="Polygon numbers in the attribute colours (set in game)"),
    "fiche_contexte_equipe": dict(cat="joueur_fiche",   # 2026-11-12, le joueur
                                  fr="Fiche complète (État d'esprit, Entraînement, Pour / Contre) au clic sur un de "
                                     "tes joueurs, partout (Portail, stats, listes...)",
                                  en="Full profile (Happiness, Training, Pros / Cons) when clicking one of your "
                                     "players, everywhere (Portal, stats, lists...)"),
    # --- Joueur : infobulle ---
    "infobulle_pour_contre": dict(cat="joueur_infobulle",
                                  fr="Pour / Contre en pastilles à la place du rapport du préparateur",
                                  en="Pros / Cons badges instead of the coach report"),
    "infobulle_pieds": dict(cat="joueur_infobulle",
                            fr="Style médiatique, pieds sous Physique, gardiens sans caractéristiques, bouton du polygone",
                            en="Media handling, feet under Physical, keepers without traits, polygon button"),
    # --- Joueur : progression ---
    "attributs_tout_cocher": dict(cat="joueur_progression", textes=True,   # + ajout Kinito 26.12 (2026-11-12)
                                  fr="Attributs : interrupteurs pour cocher / décocher toute une colonne (avec Kinito)",
                                  en="Attributes: switches to tick / untick a whole column (with Kinito)"),
    "graphes_attributs": dict(cat="joueur_progression",
                              fr="Courbe des attributs : zone de survol plus grande",
                              en="Attribute chart: bigger hover area"),
    # --- Staff ---
    "notes_staff": dict(cat="staff",
                        # 2026-11-12 (le joueur) : « Modifier recherche » (Conditions / Attributs) en WIP : chiffres +
                        # / -, mais sur les 8 niveaux de FM (menu 1-20 : liste « au go » d'etat.md)
                        # 2026-11-12 (le joueur) : 1 par 1 impossible (code natif), WIP -> « partiellement fonctionnel »
                        # 2026-11-11 : lignes de Modifier recherche rendues à FM (Potentiel / Niveau actuel bloqués à 100)
                        fr="Notes 1-20 au lieu de Bon, Exceptionnel... (profil, liste et recherche de staff). "
                           "Choisir attributs : notes en chiffres, par paliers (1, 4, 7, 10, 12, 15, 18, 20), pas "
                           "1 par 1 (limite du jeu). Lignes de Modifier recherche : menu de FM (Bon, Très bon...) "
                           "ou, en option, notes 1-20 avec + / - (casse Potentiel / Niveau actuel au-dessus de 100 "
                           "dans la recherche de joueurs)",
                        en="Ratings 1-20 instead of Good, Outstanding... (profile, staff list and search). "
                           "Choose attributes: ratings as numbers, in steps (1, 4, 7, 10, 12, 15, 18, 20), not "
                           "1 by 1 (game limit). Edit search rows: FM's menu (Good, Very good...) or, as an "
                           "option, ratings 1-20 with + / - (breaks Potential / Current ability above 100 in the "
                           "player search)"),
    "staff_fm24": dict(cat="staff", textes=True,
                       fr="Écrans du staff comme FM24 (postes, comparaisons, tableau)",
                       en="Staff screens like FM24 (roles, comparisons, table)",
                       aide=RESET_DISPOSITIONS),
    "staff_fiche": dict(cat="staff",
                        fr="Fiche et infobulle staff : médias + réputation sous Personnalité",
                        en="Staff profile and tooltip: media + reputation under Personality"),
    "couleurs_staff_comme_joueurs": dict(cat="staff", marqueur="couleurs_staff",
                                         fr="Couleurs des notes du staff = celles des joueurs",
                                         en="Staff rating colours = player attribute colours"),
    # --- Club ---
    "club_bandeau_installations": dict(cat="club", textes=True,
                                       fr="Bandeau du haut : installations + étoiles, réputation, finances...",
                                       en="Top banner: facilities + stars, reputation, finances..."),
    # 2026-11-05, liste du 04/11 point 5 ; 2026-11-15 (le joueur) : WIP, facultative (plus activée de base)
    "club_histoire": dict(cat="club", textes=True, facultatif=True,
                          fr="WIP Histoire du club : tout sur un écran (trophées, infos, records, onze, repères, entraîneurs)",
                          en="WIP Club history: all on one screen (honours, info, records, XI, landmarks, managers)"),
    "club_page_bas": dict(cat="club", textes=True,
                          fr="Panneau du bas en 3 colonnes (photo du stade, maillots, budgets, légendes...)",
                          en="Bottom panel in 3 columns (stadium photo, kits, budgets, legends...)",
                          aide=("Photos des stades : tuto pas à pas et vérification sur la page « Photos des stades » "
                                "du menu (pack gratuit, ou une image <id du club>.jpg 1280 x 720 dans graphics\\FMVE "
                                "Stadium). Club sans photo : un stade générique, sièges aux couleurs du club.",
                                "Stadium photos: step-by-step guide and check on the « Stadium photos » page of the "
                                "menu (free pack, or a <club id>.jpg 1280 x 720 image in graphics\\FMVE Stadium). "
                                "Club without a photo: a generic stadium, seats in the club's colours.")),
    "salle_trophees": dict(cat="club", textes=True,   # 2026-11-09 (essai_salle_trophees v4 validé)
                           fr="Salle des trophées à la place des Actualités : les trophées gagnés par le club (image, "
                              "nombre de victoires, années au survol du nom), rangée qui défile ; plus petite en "
                              "affichage Large",
                           en="Trophy Room instead of the News: the trophies the club has won (image, number of wins, "
                              "years when hovering the name), scrolling row; smaller in Large display",
                           aide=("Images des trophées : pack à poser dans graphics\\FMVE Trophies (TROPHY<id de la "
                                 "compétition>.png, images d'origine : FM Scout). Sans le pack, les cartes n'ont pas "
                                 "d'image.",
                                 "Trophy images: a pack to put in graphics\\FMVE Trophies (TROPHY<competition id>.png, "
                                 "original images: FM Scout). Without the pack, the cards have no image.")),
    "palmares_images": dict(cat="club",   # 2026-11-09 (essai_trophees_image validé)
                            fr="Palmarès : l'image du trophée au-dessus de chaque compétition (pack FMVE Trophies, "
                               "comme la salle des trophées)",
                            en="Honours: the trophy image above each competition (FMVE Trophies pack, like the "
                               "Trophy Room)"),
    "club_vue_ensemble": dict(cat="club", textes=True,   # 2026-11-09 (essai_club_vue_ensemble v9 validé)
                              fr="Vue d'ensemble en une grande page : à gauche stade, infos, installations, onze de "
                                 "légende (noms cliquables) et maillots ; à droite vision, finances, staff et les "
                                 "tuiles du club rangées comme le menu",
                              en="Overview as one big page: on the left stadium, info, facilities, legends XI "
                                 "(clickable names) and kits; on the right vision, finances, staff and the club tiles "
                                 "in menu order"),
    "notes_installations": dict(cat="club",
                                fr="Installations : notes /20 au lieu de Bon, Correct... Centre d'entraînement : "
                                   "note exacte seulement avec l'éditeur en jeu (FM ne la donne pas ailleurs), "
                                   "sinon fourchette (ex. 12-13). Coupée : plus de notes ni d'étoiles d'installations "
                                   "nulle part (bandeau du club, bulle du club)",
                                en="Facilities: ratings /20 instead of Good, Adequate... Training facilities: exact "
                                   "rating only with the in-game editor (FM gives it nowhere else), otherwise a "
                                   "range (e.g. 12-13). Off: no facility ratings or stars anywhere (club banner, "
                                   "club tooltip)"),
    "club_infobulle_offres": dict(cat="club", textes=True,
                                  fr="Offres de transfert / prêt et colonne Club des tableaux : « i » à côté du club, "
                                     "bulle avec division, statut, installations...",
                                  en="Transfer / loan offers and tables' Club column: \"i\" next to the club, tooltip "
                                     "with division, status, facilities..."),
    "club_amical": dict(cat="club",   # 2026-11-12, demande du joueur ; validé le 2026-11-12 (v43) ; de base 2026-10-31
                        fr="Page Infos de tous les clubs : bouton « Organiser amical » qui ouvre la fenêtre d'amical "
                           "avec l'équipe affichée (équipe première, réserve, U19, U21…) déjà choisie comme "
                           "adversaire. FM ne choisit un adversaire que par son numéro dans la partie, différent "
                           "d'une partie à l'autre : le bouton le cherche, d'où des noms qui défilent (clubs : moins "
                           "d'1 s ; jeunes : 1 à 3 s). Pas sur ta propre équipe. Selon la base de données de la "
                           "partie (surtout les toutes petites), certains clubs peuvent arriver faux (vu sur des "
                           "clubs américains) ; en Europe, ça marche bien en général",
                        en="Every club's Info page: an « Arrange Friendly » button that opens the friendly window "
                           "with the team shown (first team, reserves, U19, U21…) already selected as the opponent. "
                           "FM only picks an opponent by its number in the save, which differs from one save to "
                           "another: the button searches for it, hence names scrolling by (clubs: under 1 s; youth: "
                           "1 to 3 s). Not on your own team. Depending on the save's database (especially very "
                           "small ones), some clubs may come out wrong (seen with American clubs); in Europe it "
                           "generally works fine"),
    # --- Finances ---
    "graphes_finances": dict(cat="finances",
                             fr="Graphiques : un point par mois + valeur au survol",
                             en="Charts: one point per month + value on hover"),
    "finances_tuile_unique": dict(cat="finances",   # 2026-11-12, maquette du joueur ; v16 validée en jeu, de base
                                  fr="Vue d'ensemble en une seule tuile : graphiques à gauche (dettes en haut à droite) ; "
                                     "à droite budgets modifiables (Transfert, Salaire, Recrutement), Solde, Chiffre "
                                     "d'affaires, boutons Clauses / Sponsors ; un clic sur un en-tête ouvre sa page",
                                  en="Overview as a single tile: charts on the left (debts at the top right); on the right "
                                     "editable budgets (Transfer, Wage, Scouting), Balance, Turnover, Clauses / Sponsors "
                                     "buttons; clicking a header opens its page",
                                  aide=RESET_DISPOSITIONS),
    # --- Effectif et dynamique ---
    "effectif_boutons_entrainement": dict(cat="effectif",
                                          fr="Onglet First Team : boutons Entraînement / Individuel / Programme",
                                          en="First Team tab: Training / Individual / Fixture Schedule buttons"),
    "effectif_equipes": dict(cat="effectif",   # + ajout Kinito 26.10 (fusion du 2026-11-12)
                             fr="Vue d'ensemble : boutons Entraînement / Individuel / Programme, liens et boutons des "
                                "équipes du club",
                             en="Overview: Training / Individual / Fixture Schedule buttons, club team links and "
                                "buttons",
                             aide=("Vue d'ensemble : les 3 boutons après le menu des vues, et des liens vers les autres "
                                   "équipes du club après « Équipe première ». Écran Effectif de chaque équipe : les "
                                   "boutons des équipes à droite de « Avec / Sans le ballon ». L'option des boutons "
                                   "(icônes ou écrits) vaut aussi pour l'écran Effectif et les Tactiques. Avec Kinito.",
                                   "Overview: the 3 buttons after the views menu, and links to the club's other teams "
                                   "after \"First Team\". Each team's Squad screen: the team buttons right of \"In / Out "
                                   "of possession\". The buttons option (icons or written) also applies to the Squad "
                                   "screen and Tactics. With Kinito.")),
    "effectif_repos_equipe": dict(cat="effectif", textes=True,   # 2026-10-30 (essai essai_repos_effectif)
                                  fr="Bouton repos après le calendrier (écran Effectif de chaque équipe, Vue "
                                     "d'ensemble) : un clic ouvre les jours de repos, posés à tout l'effectif",
                                  en="Rest button after the calendar (each team's Squad screen, Overview): one click "
                                     "opens the rest days, applied to the whole squad",
                                  aide=("Pas de bouton quand FM ne propose pas le repos : entraînement géré par le "
                                        "staff (Club > Responsabilités ; souvent les U19 / U23), joueurs en vacances, "
                                        "un joueur en déplacement vers sa sélection (« Trj » : FM bloque alors le "
                                        "repos de toute l'équipe jusqu'à son départ). Les blessés sont sautés.",
                                        "No button when FM does not offer rest: training handled by staff (Club > "
                                        "Responsibilities; often U19 / U23 teams), players on holiday, a player "
                                        "travelling to his national team (FM then blocks rest for the whole squad "
                                        "until he leaves). Injured players are skipped.")),
    "hierarchie_pyramide": dict(cat="effectif",
                                fr="Hiérarchie en pyramide : nom = fiche, clic sur une carte = qui t'aime / son groupe en couleur",
                                en="Hierarchy as a pyramid: name = profile, click a card = who likes you / their group in colour"),
    "cercles_amis_cartes": dict(cat="effectif",
                                fr="Cercles d'amis en cartes joueur, comme FM24",
                                en="Social groups as player cards, like FM24"),
    "dynamique_vue_ensemble": dict(cat="effectif",
                                   fr="Vue d'ensemble : blocs du haut moins hauts, Problèmes plus grand",
                                   en="Overview: shorter top blocks, bigger Issues panel",
                                   aide=RESET_DISPOSITIONS),
    "etat_esprit_fm24": dict(cat="effectif",
                             fr="État d'esprit : colonnes de satisfaction comme FM24",
                             en="Happiness: satisfaction columns like FM24"),
    "jeunes_candidats_fm24": dict(cat="effectif", textes=True,
                                  fr="Jeunes à l'essai (message et écran Jeunes candidats) comme FM24",
                                  en="Youth intake (inbox message and Youth Candidates screen) like FM24"),
    # --- Entraînement ---
    "entrainement_equipes": dict(cat="entrainement",
                                 fr="Calendrier (Entraînement, Rencontres) : un bouton par équipe du club",
                                 en="Calendar (Training, Fixtures): one button per club team"),
    "entrainement_individuel_equipes": dict(cat="entrainement", textes=True,   # + Kinito 26.14, 26.15 (2026-11-12)
                                            fr="Entraînement individuel : équipes du club (liens en Large, boutons en "
                                               "Medium / Small), onglet Rapport d'entraînement, pouces, liste plus "
                                               "large en Large (avec Kinito)",
                                            en="Individual training: club teams (links in Large, buttons in Medium / "
                                               "Small), Training report tab, thumbs, wider list in Large (with Kinito)"),
    "entrainement_individuel_boutons": dict(cat="entrainement",   # + Kinito 26.16 (2026-11-12)
                                            fr="Entraînement individuel : Féliciter / Critiquer / Rapport à côté des "
                                               "onglets, terrain des postes agrandi (avec Kinito)",
                                            en="Individual training: Praise / Criticise / Report next to the tabs, "
                                               "bigger positions pitch (with Kinito)"),
    "entrainement_pouces": dict(cat="entrainement", textes=True,   # textes : bouton « Féliciter les cochés »
                                fr="Entraînement individuel : pouces Féliciter / Critiquer dans la liste, "
                                   "la conversation se répond et se ferme seule (équipes de jeunes : la 2e "
                                   "conversation reste à la main), bouton « Féliciter les cochés »",
                                en="Individual training: Praise / Criticise thumbs in the list, the conversation "
                                   "replies and closes by itself (youth teams: the 2nd conversation stays manual), "
                                   "\"Praise selected\" button"),
    # --- Tactiques ---
    "photos_tactiques": dict(cat="tactiques",
                             fr="Photos des joueurs sur le terrain des tactiques",
                             en="Player photos on the tactics pitch"),
    "tactiques_forme_valeur": dict(cat="tactiques",
                                   fr="Colonne Forme avec valeur dans Insérer colonne",
                                   en="Form with Value column in Insert column"),
    "tactiques_boutons": dict(cat="tactiques", textes=True,   # v7 : (D) / (E) des prochains adversaires
                              fr="Boutons Effectif / Programme des rencontres à gauche de Conseil",
                              en="Squad / Fixture Schedule buttons left of Advice"),
    # --- Match ---
    "match_haut": dict(cat="match",
                       fr="Bandeau du haut : nouveau tableau de score à gauche (logos, couleurs des maillots), "
                          "barre et boutons alignés",
                       en="Top header: new scoreboard on the left (logos, kit colours), bar and buttons aligned"),
    "photos_match": dict(cat="match",
                         fr="Photos des joueurs : terrain du match et barre du bas",
                         en="Player photos: match pitch and bottom bar"),
    # 2026-11-13, le joueur : Hauteur / Zoom de la caméra -20..20 (FM 0-10), molette comprise, Caméras TV débloquée
    # facultative le 2026-11-14 (le joueur : tout ce qui touche au jeu, pas de base ; app : catégorie « affichage »)
    "match_camera_limites": dict(cat="match", facultatif=True,   # de base le 2026-11-14 (le joueur)
                                 fr="Caméra du match : Hauteur et Zoom de -60 à 60 (au lieu de 0 à 10, molette "
                                    "comprise), Hauteur aussi en Caméras TV",
                                 en="Match camera: Height and Zoom from -60 to 60 (instead of 0 to 10, mouse wheel "
                                    "included), Height in TV Cameras too"),
    # 2026-11-13, le joueur : x 1.4 entre 1.25 et 1.5 (liste dans les données de FM)
    "match_vitesses": dict(cat="match", facultatif=True,   # de base puis facultative le 2026-11-14 (le joueur)
                           fr="Vitesse du match pendant les temps forts : cran x 1.4 ajouté (entre x 1.25 et x 1.5)",
                           en="Match speed during highlights: x 1.4 step added (between x 1.25 and x 1.5)"),
    # 2026-11-09 (le joueur) : validé en jeu (v5), pour la release v1.71
    "match_cartons_buts": dict(cat="match",
                               fr="Terrain du match : pastille du poste en jaune après un carton, buts et passes D "
                                  "à côté du nom",
                               en="Match pitch: position badge turns yellow after a booking, goals and assists next "
                                  "to the name"),
    # 2026-11-14 (demande Discord) : PAS VU en jeu
    "buteurs_survol": dict(cat="match",
                           fr="WIP Buteurs : fiche du joueur au survol de son nom (autres matchs du jour, résultats, "
                              "calendrier, résumé du match)",
                           en="WIP Goalscorers: player tooltip when hovering their name (other matches of the day, "
                              "results, calendar, match summary)"),
    # 2026-11-18 (le joueur) : Banc de touche coincé à sa place -> tuile à choix ; VALIDÉ en jeu 2026-11-18
    "match_tuile_banc": dict(cat="match", aide=RESET_DISPOSITIONS,
                             fr="Match en direct : Banc de touche en tuile à choix (⌄ comme les autres tuiles), "
                                "Carte de passes domicile d'office à sa place",
                             en="Live match: Touchline as a selectable tile (⌄ like the other tiles), home team "
                                "Pass Map shown by default in its place"),
    # --- Calendrier ---
    "rencontres_stade_spectateurs": dict(cat="calendrier",
                                         # 2026-11-17 : colonnes du skin retirées (tableau de FM) ; boutons + tableau
                                         # Kinito (option)
                                         fr="Rencontres : boutons des équipes, vues et filtre (version Kinito ou du "
                                            "skin, dans Options)",
                                         en="Fixtures: team buttons, views and filter (Kinito or skin version, in "
                                            "Options)"),
    "rencontres_place_championnat": dict(cat="calendrier",   # 2026-11-05, le joueur
                                         fr="Rencontres : place en championnat sous le nom des équipes",
                                         en="Fixtures: league position under the team names"),
    # --- Tableaux ---
    "colonne_personnalite": dict(cat="tableaux",
                                 fr="Colonne Personnalité dans Insérer colonne > Infos générales",
                                 en="Personality column in Insert column > General info"),
    # 2026-11-19 (le joueur : « enlève-le du skin, pas actif à la base ») : facultatif ; déjà actif chez quelqu'un = reste
    "colonne_temperament": dict(cat="tableaux", textes=True, facultatif=True,   # 2026-11-13 ; textes : « Tempérament (logo) »
                                fr="Colonne Tempérament (Bosseur, Penseur...) dans Insérer colonne > Infos générales",
                                en="Mindset column (Hard Worker, Thinker...) in Insert column > General info"),
    "nation_drapeau_seul": dict(cat="tableaux",
                                fr="Colonnes Nationalité / 2e nationalité : logo seul plus grand (ou + 3 lettres, choix 500)",
                                en="Nationality / 2nd Nationality columns: bigger logo only (or + 3 letters, choice 500)"),
    "moral_icone_seule": dict(cat="tableaux", toujours=True,
                              fr="Moral et État d'esprit en logo seul, sans texte",
                              en="Morale and Happiness as icon only, without text"),
    # --- Séparateurs ---
    "colonnes_separateur": dict(cat="separateur", textes=True,
                                fr="Trait vertical à placer où tu veux dans les vues, jusqu'à 15 par vue "
                                   "(Insérer colonne > Séparateur)",
                                en="Vertical line to place anywhere in views, up to 15 per view "
                                   "(Insert column > Separator)"),
    # --- Haut de l'écran ---
    "prochain_match_domicile": dict(cat="haut_du_jeu", textes=True,
                                    fr="(D) / (E) (domicile / extérieur) après le prochain adversaire",
                                    en="(H) / (A) (home / away) after the next opponent"),
    # --- Fond des pages ---
    "theme_fond": dict(cat="theme", facultatif=True, toujours=True,
                       fr="Couleur du fond des pages (ex. 30 rouge, 30 #3C3F45)",
                       en="Page background colour (e.g. 30 red, 30 #3C3F45)"),
    "couleurs_interface": dict(cat="theme", facultatif=True, toujours=True,
                               fr="Couleurs de la barre du haut, de son texte, de la barre secondaire, de l'accent, "
                                  "des verts de l'écran Tactiques (bandeau, panneau, terrain), des tuiles et du "
                                  "match (tableau de score, boutons en haut à droite, bandeau de l'effectif, barre de "
                                  "commentaire)",
                               en="Colours of the top bar, its text, the secondary bar, the accent, the Tactics "
                                  "screen greens (header, panel, pitch), the tiles and the match (scoreboard, "
                                  "top-right buttons, squad strip, commentary bar)"),
    # (echelle_1080p, Affichages Moyen / Petit en 1080p : retirée le 2026-11-17, FM le fait lui-même depuis sa MAJ ;
    #  dans ABANDONNES pour enlever un patch resté)
    # --- Recrutement ---
    "rapport_recrutement_fm24": dict(cat="recrutement",   # 2026-11-12, idée du joueur (capture FM24)
                                     fr="Rapports du recruteur comme FM24 : attributs et Pour / Contre à gauche, "
                                        "infos du joueur (taille, réputation…) et du recruteur à droite ; pareil dans "
                                        "les messages",
                                     en="Scout reports like FM24: attributes and Pros / Cons on the left, player info "
                                        "(height, reputation…) and scout info on the right; same in messages"),
    "recherches_ciblees": dict(cat="recrutement",   # 2026-11-05, liste du 04/11 point 2
                               fr="Recherches ciblées : tête du joueur, vues personnalisables (Insérer colonne)",
                               en="Recruitment focuses: player face, custom views (Insert column)"),
    # 2026-11-10, le joueur (à la place d'une carte du monde) ; styles écrits par couleurs_interface (son marqueur)
    "connaissance_couleurs": dict(cat="recrutement",   # de base le 2026-11-14 (le joueur ; tuile encore WIP)
                                  fr="WIP Niveaux de connaissance en couleurs, du rouge (basique) au vert (inégalée) : "
                                     "pays et régions de « Connaissance du monde », recruteurs",
                                  en="WIP Knowledge levels in colour, from red (basic) to green (peerless): "
                                     "« World Knowledge » nations and regions, scouts"),
    # 2026-11-13, le joueur (né de essai_selection_top50) ; v2 2026-11-14 : un bouton par carte (WIP tant que pas vu)
    "selection_top50": dict(cat="recrutement",
                            fr="WIP Messages NXGN et 50 meilleurs joueurs du monde : bouton « Ajouter à la "
                               "sélection » sous chaque joueur, en un clic",
                            en="WIP NXGN and world's 50 best players messages: one-click « Add to shortlist » "
                               "button under each player"),
    # --- Vues d'AlexJeuVideal (hors_jeu : fichiers hors du jeu, retirés aussi par « Désinstaller tout ») ---
    "vues_alexjeuvideal": dict(cat="vues", hors_jeu=True,   # 2026-11-12, le joueur ; de base 2026-10-31
                               fr="Vues d'AlexJeuVideal, optimisées pour l'affichage Small : Effectif, Tactiques "
                                  "(Vue d'ensemble, Possession), Recrutement (base de données, rapports), Sélection. "
                                  "Elles s'ajoutent à tes vues dans le menu des vues de chaque tableau",
                               en="AlexJeuVideal's views, optimised for the Small display: Squad, Tactics (Overview, "
                                  "Possession), Scouting (database, reports), Shortlist. They are added to your own "
                                  "views in each table's views menu",
                               aide=("Une vue à toi du même nom n'est jamais écrasée. Retirer l'option n'efface que "
                                     "nos vues (pas celles que tu as modifiées).",
                                     "A view of yours with the same name is never overwritten. Turning the option off "
                                     "only deletes our views (not ones you edited).")),
    # --- Kinito (numéros 26.x de ses notes), rangés par catégorie (KINITO_GROUPES) ---
    # Joueur : fiche
    "kinito_entete_large": dict(cat="kinito", textes=True, facultatif=True,   # 26.20 (2026-11-08)
                                # v21 / bloc v33 (2026-11-19, Kinito) : Grand, Moyen et Petit, plus « 1080p » dans le nom
                                fr=("Fiche joueur (affichages Grand, Moyen et Petit) : en haut, des tuiles (contrat "
                                    "avec le temps de jeu en évidence, valeur, dispos, boutons d'action, polygones, "
                                    "entraînement) ; dessous, la carte du joueur (photo, nation avec drapeau, lieu de "
                                    "naissance, clubs), postes, notes, Infos, niveau et potentiel au-dessus de Pour / "
                                    "Contre avec leurs phrases et rapport ; remplace la fiche du skin"),
                                en=("Player profile (Large, Medium and Small displays): on top, tiles (contract with "
                                    "playing time highlighted, value, availability, action buttons, polygons, "
                                    "training); below, the player card (photo, nation with flag, place of birth, "
                                    "clubs), positions, attributes, Info, current and potential ability above Pros / "
                                    "Cons with their sentences and report; replaces the skin's profile"),
                                aide=(("Dans les trois affichages des informations (Grand, Moyen, Petit) et les "
                                       "quatre tailles du texte, partout où FM prend la grande mise en page de la "
                                       "fiche (1080p et plus grand). Une fenêtre plus petite garde la fiche du skin ; "
                                       "les tuiles du bas restent celles du skin."),
                                      ("In all three information displays (Large, Medium, Small) and the four text "
                                       "sizes, wherever FM uses the large profile layout (1080p and bigger). A "
                                       "smaller window keeps the skin's profile; the bottom tiles stay the skin's."))),
    # Effectif
    "kinito_capitaines_vues": dict(cat="kinito",   # 26.8
                                   fr="Capitaines : vues personnalisables dans « Tout l'effectif »",
                                   en="Captains: customisable views in the squad table"),
    "kinito_enregistrement": dict(cat="kinito",   # 26.17
                                  fr="Enregistrement de l'effectif : règles en entier (affichage Large), interrupteurs "
                                     "Enr. plus petits dans une colonne à leur taille, interrupteur d'en-tête pour les "
                                     "joueurs cochés (essai)",
                                  en="Squad registration: rules shown in full (Large display), smaller Reg. switches in "
                                     "a column sized to them, header switch for the ticked players (trial)"),
    "kinito_cartes_jeunes": dict(
        cat="kinito", textes=True, facultatif=True,   # 26.19 (2026-11-08) ; v31 + 26.22 v18 (2026-11-10) : révélation comprise, choix dans le message ;
        # v33 + 26.22 v20 (2026-11-13, Kinito) : « Réglages » sur la 1re rangée, textes dans la langue du jeu
        fr=("Message des jeunes : cartes à retourner et révélation d'un jeune (clic par carte, Tout retourner par "
            "groupe ; 1er clic sur le dos d'une carte : la carte en grand ; clic sur son nom : le dossier, puis sa "
            "fiche dévoilée). Style, Révélation (aucune, élite, élite et excellents, tous) et Dévoiler la fiche "
            "(fondu, rideau, portes ; tout seul ou à la main) se choisissent dans le message, par « Réglages » sur la "
            "1re rangée ; au départ : style J (dossier du recruteur), révélation des candidats d'élite, à la main. "
            "Les textes suivent la langue du jeu"),
        en=("Youth intake message: cards to flip and a youngster's reveal (click a card, Flip all per group; first "
            "click on a card's back: the card shown large; click their name: the file, then their profile revealed). "
            "Style, Reveal (none, elite, elite and top, all) and Reveal the profile (fade, curtain, doors; auto or by "
            "hand) are chosen in the message, with \"Settings\" on the first row; to start: style J (scout's file), "
            "reveal for elite prospects, by hand. Texts follow the game language"),
        aide=(("Faite par-dessus « Jeunes à l'essai (message et écran Jeunes candidats) comme FM24 » (Effectif) : les "
               "cartes prennent la couleur de ses groupes. Les choix faits dans le message sont gardés d'une partie à "
               "l'autre."),
              ("Built on top of \"Youth intake (inbox message and Youth Candidates screen) like FM24\" (Squad): the "
               "cards take its group colours. The choices made in the message are kept from one save to the next.")),
    ),
    # (26.10 kinito_effectif_vue et 26.12 kinito_attributs_interrupteurs : fusionnés le 2026-11-12 dans
    #  effectif_equipes (option « boutons_effectif ») et attributs_tout_cocher (interrupteurs toujours))
    # Entraînement
    "kinito_echange_seances": dict(cat="kinito",   # 26.6
                                   fr="Entraînement : échanger deux séances en deux clics",
                                   en="Training: swap two sessions in two clicks"),
    "kinito_vue_equipes": dict(cat="kinito",   # 26.7
                               fr="Entraînement, Vue d'ensemble : boutons des équipes à côté du mois",
                               en="Training, Overview: team buttons next to the month",
                               aide=("A besoin de « Calendrier (Entraînement, Rencontres) : un bouton par équipe du "
                                     "club » (Entraînement).",
                                     "Needs \"Calendar (Training, Fixtures): one button per club team\" (Training).")),
    # (26.14 à 26.16 : reçus de Kinito le 2026-11-12 ; 26.14 / 26.15 fusionnés dans entrainement_individuel_equipes,
    #  26.16 dans entrainement_individuel_boutons, le même jour, demande du joueur)
    # Tactiques
    "kinito_consignes_essai_b": dict(cat="kinito", textes=True, facultatif=True,   # 26.13 (pas de base, 2026-11-12)
                                     fr="Consignes : écran Terrain et vue FM24 des consignes d'équipe, écran FM24 des "
                                        "consignes individuelles (bouton FM 27 | FM24)",
                                     en="Instructions: Pitch screen and FM24 view for team instructions, FM24 screen "
                                        "for player instructions (FM 27 | FM24 button)"),
    "kinito_raccourcis_selections": dict(cat="kinito",   # 26.23 (2026-11-14) ; de base le 2026-11-14 (le joueur) ; seul à toucher
        # TacticalPlannerSpeakToActions (option « haut ») ou TacticalPlannerTeamShapeTableTemplate (« filtre ») ; v8 :
        # + TeamSquadBlock / SquadOverviewTableBlock (#QuickPick, après leurs propriétaires : SUIVANTS)
        fr=("Tactiques et Effectif : les 10 premières sélections d'équipe sauvegardées en boutons à droite de "
            "« Sélect. rapide » (leur nom dessus) ; un clic charge la sélection"),
        en=("Tactics and Squad: the first 10 saved team selections as buttons right of \"Quick Pick\" (their name on "
            "them); one click loads the selection")),
    # Match
    "kinito_fenetre_but": dict(cat="kinito",   # 26.18 (2026-11-08) ; de base depuis le 2026-11-09 (le joueur)
                               fr="Match : fenêtre de but avec la photo du buteur, ses buts dans le match et un "
                                  "bandeau « BUT ! 3e but en 12 matchs de Ligue 2 · Benson : 5e passe D » (dans la "
                                  "compétition)",
                               en="Match: goal pop-up with the scorer's photo, the scorer's goals in the match and a "
                                  "band « GOAL! 3rd goal in 12 Ligue 2 games · Benson: 5th assist » (in the "
                                  "competition)"),
    # Calendrier
    "kinito_calendrier_rencontres": dict(cat="kinito", facultatif=True,   # 26.1
                                         fr="Portail > Calendrier s'ouvre sur l'onglet Rencontres",
                                         en="Portal > Calendar opens on the Fixtures tab"),
    "kinito_vacances_jour": dict(cat="kinito", textes=True,   # 26.4
                                 fr="Calendrier, Général : icône vacances sur chaque jour à venir",
                                 en="Calendar, General: holiday icon on every upcoming day"),
    # Recrutement
    "kinito_rapports_vues": dict(cat="kinito",   # 26.5
                                 fr="Rapports des recruteurs : vues personnalisables",
                                 en="Scout reports: customisable views"),
    # Contrats et transferts
    "kinito_contrat_cadenas": dict(cat="kinito", facultatif=True,   # 26.3
                                   fr="Contrats et transferts : cadenas en icônes à droite de chaque ligne",
                                   en="Contracts and transfers: padlocks as icons on the right of each line"),
    # Pays et sélections
    "kinito_pays_formation": dict(
        cat="kinito",   # de base le 2026-11-14 (le joueur) ; 26.21 v8 (2026-11-10) : seul à toucher ses deux en-têtes (pays, sélection)
        fr=("Page d'un pays et d'une sélection : note de formation des jeunes sur 200 au départ et dates d'arrivée "
            "des jeunes, hommes et femmes (sur une sélection, son sexe ; pays sans championnat : la plage relevée en "
            "jeu), à côté de Population et du Classement mondial"),
        en=("Nation and national team pages: starting youth rating out of 200 and youth intake dates, men and women "
            "(on a national team, its own; nations with no league: the window recorded in game), next to Population "
            "and World Ranking"),
    ),
}

# où voir le changement en jeu (fr, en) : ligne « 📍 » sous le titre de la tuile dans l'app (2026-11-12, demande du
# joueur) ; fiche joueur = « Fiche joueur » seul, sans chemin
_FICHE = ("Fiche joueur", "Player profile")
_SURVOL = ("Survol d'un joueur (partout)", "Hovering a player (anywhere)")
_INDIV = ("Entraînement > Individuel", "Training > Individual")
_TACT = ("Tactiques", "Tactics")
_TABLEAUX = ("Tableaux de joueurs (Effectif, recherche...)", "Player tables (Squad, search...)")
OU = {
    "entete_fiche": _FICHE, "style_mediatique": _FICHE, "hors_defaut": _FICHE,
    "temperament_infos": ("Fiche joueur, survol d'un joueur", "Player profile, hovering a player"), "fiche_joueur_plus": _FICHE,
    "listes_pour_contre": _FICHE, "suspensions_noms_courts": _FICHE, "attributs_tout_cocher": _FICHE,
    "graphes_attributs": _FICHE, "fiche_ordre_tuiles": _FICHE, "tuile_carriere": _FICHE,
    "tuile_blessures": _FICHE,
    "couleurs_polygone": ("Fiche joueur, survol d'un joueur", "Player profile, hovering a player"),
    "fiche_contexte_equipe": ("Clic sur un de tes joueurs (partout)", "Clicking one of your players (anywhere)"),
    "tuile_forme": _SURVOL,
    "infobulle_pour_contre": _SURVOL, "infobulle_pieds": _SURVOL,
    "notes_staff": ("Fiche staff, Club > Staff, recherche de staff", "Staff profile, Club > Staff, staff search"),
    "staff_fm24": ("Club > Staff", "Club > Staff"),
    "staff_fiche": ("Fiche staff, survol d'un membre du staff", "Staff profile, hovering a staff member"),
    "couleurs_staff_comme_joueurs": ("Fiche staff, Club > Staff", "Staff profile, Club > Staff"),
    "club_bandeau_installations": ("Club > Vue d'ensemble", "Club > Overview"),
    "club_page_bas": ("Club > Vue d'ensemble", "Club > Overview"),
    "salle_trophees": ("Club > Vue d'ensemble", "Club > Overview"),
    "club_histoire": ("Club > Histoire du club", "Club > Club History"),
    "palmares_images": ("Club > Histoire du club, palmarès de la page club",
                        "Club > Club History, honours of the club page"),
    "club_vue_ensemble": ("Club > Vue d'ensemble", "Club > Overview"),
    "notes_installations": ("Club > Installations", "Club > Facilities"),
    "club_infobulle_offres": ("Offres de transfert / prêt reçues, colonne Club des tableaux",
                              "Transfer / loan offers received, tables' Club column"),
    "club_amical": ("Page d'un club > Infos (onglet de l'équipe)", "A club's page > Info (the team's tab)"),
    "graphes_finances": ("Finances", "Finances"),
    "finances_tuile_unique": ("Club > Finances > Vue d'ensemble", "Club > Finances > Overview"),
    "effectif_boutons_entrainement": ("Effectif > Équipe première", "Squad > First Team"),
    "effectif_equipes": ("Effectif > Vue d'ensemble", "Squad > Overview"),
    "effectif_repos_equipe": ("Effectif (chaque équipe), Effectif > Vue d'ensemble", "Squad (each team), Squad > Overview"),
    "hierarchie_pyramide": ("Effectif > Dynamique > Hiérarchie", "Squad > Dynamics > Hierarchy"),
    "cercles_amis_cartes": ("Effectif > Dynamique > Cercles d'amis", "Squad > Dynamics > Social Groups"),
    "dynamique_vue_ensemble": ("Effectif > Dynamique > Vue d'ensemble", "Squad > Dynamics > Overview"),
    "etat_esprit_fm24": ("Effectif > Dynamique > État d'esprit", "Squad > Dynamics > Happiness"),
    "jeunes_candidats_fm24": ("Boîte de réception (message des jeunes) > Jeunes candidats",
                              "Inbox (youth intake message) > Youth Candidates"),
    "entrainement_equipes": ("Calendrier > Entraînement / Rencontres", "Calendar > Training / Fixtures"),
    "entrainement_individuel_equipes": _INDIV, "entrainement_individuel_boutons": _INDIV, "entrainement_pouces": _INDIV,
    "photos_tactiques": _TACT, "tactiques_forme_valeur": _TACT, "tactiques_boutons": _TACT,    "match_haut": ("Match en direct", "Live match"), "photos_match": ("Match en direct", "Live match"),
    "match_cartons_buts": ("Match en direct (formations)", "Live match (formations)"),
    "match_camera_limites": ("Match en direct > Caméra", "Live match > Camera"),
    "match_vitesses": ("Match en direct > Temps forts", "Live match > Highlights"),
    "match_tuile_banc": ("Match en direct (tuiles)", "Live match (tiles)"),
    "buteurs_survol": ("Autres matchs du jour, résultats d'une compétition, calendrier, résumé du match",
                       "Other matches of the day, competition results, calendar, match summary"),
    "rencontres_stade_spectateurs": ("Calendrier > Rencontres", "Calendar > Fixtures"),
    "recherches_ciblees": ("Recrutement > Recherches ciblées", "Scouting > Recruitment Focuses"),
    "connaissance_couleurs": ("Recrutement > Recrutement > tuile Connaissance du monde",
                              "Scouting > Scouting > World Knowledge tile"),
    "selection_top50": ("Boîte de réception / Actualités (messages NXGN, top 50 mondial)",
                        "Inbox / News (NXGN, world top 50 messages)"),
    "rencontres_place_championnat": ("Portail > Calendrier > Rencontres", "Portal > Calendar > Fixtures"),
    "colonne_personnalite": _TABLEAUX, "colonne_temperament": _TABLEAUX, "nation_drapeau_seul": _TABLEAUX, "moral_icone_seule": _TABLEAUX,
    "colonnes_separateur": ("Tous les tableaux > clic droit > Insérer colonne > Séparateur",
                            "All tables > right click > Insert column > Separator"),
    "prochain_match_domicile": ("Barre du haut", "Top bar"),
    "rapport_recrutement_fm24": ("Recrutement > Joueurs recommandés > Rapports",
                                 "Scouting > Recommended players > Reports"),
    "theme_fond": ("Tout le jeu", "Whole game"), "couleurs_interface": ("Barre du haut, Tactiques, tuiles, match",
                                                                                "Top bar, Tactics, tiles, match"),
    "vues_alexjeuvideal": ("Menu des vues des tableaux", "Tables' views menu"),
    "kinito_entete_large": ("Fiche joueur", "Player profile"),
    "kinito_capitaines_vues": ("Effectif > Capitaines", "Squad > Captains"),
    "kinito_enregistrement": ("Effectif > Enregistrement", "Squad > Registration"),
    "kinito_cartes_jeunes": ("Boîte de réception (message des jeunes) > Arrivée des jeunes",
                             "Inbox (youth intake message) > Youth intake"),
    "kinito_echange_seances": ("Entraînement > Calendrier", "Training > Calendar"),
    "kinito_vue_equipes": ("Entraînement > Vue d'ensemble", "Training > Overview"),
    "kinito_consignes_essai_b": ("Tactiques > Consignes d'équipe et consignes individuelles",
                                 "Tactics > Team and Player Instructions"),
    "kinito_raccourcis_selections": ("Tactiques, Effectif (Joueurs, Vue d'ensemble), à droite de Sélect. rapide",
                                     "Tactics, Squad (Players, Overview), right of Quick Pick"),
    "kinito_fenetre_but": ("Match > Fenêtre de but", "Match > Goal pop-up"),
    "kinito_calendrier_rencontres": ("Portail > Calendrier", "Portal > Calendar"),
    "kinito_vacances_jour": ("Calendrier > Général", "Calendar > General"),
    "kinito_rapports_vues": ("Recrutement > Rapports", "Scouting > Reports"),
    "kinito_contrat_cadenas": ("Négociations de contrat / transfert", "Contract / transfer negotiations"),
    "kinito_pays_formation": ("Pays > Vue d'ensemble ; sélection > Vue d'ensemble",
                              "Nation > Overview; national team > Overview"),
}

# ordre du choix 1 (des fonctions lisent des modèles que d'autres modifient : ne pas changer sans raison)
#   infobulle_pieds avant style_mediatique : l'infobulle recopie le bloc des pieds du tableau d'attributs d'origine ;
#   entete_fiche / staff_fiche / entrainement_individuel_boutons avant fiche_joueur_plus : ils lisent le gros bloc
#   tel qu'avant ses ajouts (ancien fiches_plus, un seul passage).
#   notes_staff en premier : sa recette passait avant tout le reste (étape « notes au lieu des libellés »).
ORDRE_SKIN = [
    "notes_staff", "notes_installations", "club_bandeau_installations", "club_page_bas",
    "salle_trophees",   # après club_page_bas (même modèle ClubSiteBlock : repart de l'original + club_page_bas)
    "palmares_images",   # seul sur ClubHistoryHonourCardRow
    "club_histoire",   # après club_page_bas (son stade photo est recopié)
    "club_vue_ensemble",   # après club_page_bas (son stade photo est recopié)
    "couleurs_staff_comme_joueurs",
    "couleurs_polygone",
    "infobulle_pieds", "style_mediatique",
    "temperament_infos",   # après style_mediatique (sa ligne Média est recopiée de Personnalité, hors de notre ligne)
    "hors_defaut", "infobulle_pour_contre", "listes_pour_contre",
    "entete_fiche", "staff_fiche", "entrainement_individuel_boutons", "fiche_joueur_plus",
    "match_haut", "theme_fond", "colonne_personnalite",
    "recherches_ciblees",   # après colonne_personnalite (son menu recopie celui de la Base de données)
    "colonne_temperament",   # après colonne_personnalite (placée après Personnalité) et recherches_ciblees
    "finances_tuile_unique", "graphes_finances",
    "graphes_attributs",
    "hierarchie_pyramide", "photos_tactiques", "photos_match", "match_cartons_buts", "match_camera_limites", "match_vitesses",
    "match_tuile_banc",   # seul sur DugoutTileDescription + compositions MatchExperience* (ui-tileslayouts)
    "buteurs_survol",   # seul sur ses 5 modèles (repart de l'original)
    "attributs_tout_cocher", "nation_drapeau_seul", "suspensions_noms_courts",
    "tuile_forme", "fiche_ordre_tuiles", "tuile_carriere", "fiche_contexte_equipe",
    "moral_icone_seule",
    "rencontres_place_championnat",
    "cercles_amis_cartes", "dynamique_vue_ensemble", "etat_esprit_fm24",
    "entrainement_pouces", "staff_fm24", "entrainement_equipes", "effectif_boutons_entrainement",
    "entrainement_individuel_equipes", "prochain_match_domicile", "tactiques_forme_valeur",
    "tactiques_boutons", "effectif_equipes",
    "effectif_repos_equipe",   # après effectif_boutons_entrainement / effectif_equipes (repartent de l'original)
    "couleurs_interface",   # après tactiques_boutons : couleurs du bandeau des Tactiques (TacticalPlannerHeader)
    "connaissance_couleurs",   # passe par couleurs_interface.ecrire_styles (même bundles de styles)
    "club_infobulle_offres", "jeunes_candidats_fm24", "club_amical",
    "selection_top50",   # seul sur TopPlayersInTheWorldNewsStoryBlock : n'importe où
    # Kinito : après toutes les fonctions du skin (kinito_vue_equipes après entrainement_equipes)
    "kinito_calendrier_rencontres", "kinito_contrat_cadenas", "kinito_vacances_jour", "kinito_rapports_vues",
    "kinito_echange_seances", "kinito_vue_equipes", "kinito_capitaines_vues",
    "kinito_consignes_essai_b",
    "kinito_enregistrement",   # 26.17 après moral_icone_seule
    "rapport_recrutement_fm24",   # après kinito_rapports_vues (même modèle, qu'il réécrit depuis l'original)
    "vues_alexjeuvideal",   # fichiers hors du jeu : n'importe où
    "rencontres_stade_spectateurs",   # son option « rencontres » (version Kinito) suit entrainement_equipes
    # tout à la fin : après les scripts qui recopient / refont des menus Insérer colonne (colonne_personnalite,
    # recherches_ciblees, kinito_rapports_vues, kinito_capitaines_vues, kinito_rencontres_vues) et moral_icone_seule
    "colonnes_separateur",
    # Kinito 26.18 à 26.20 (2026-11-08), dans l'ordre vu en jeu chez lui :
    "kinito_fenetre_but",     # 26.18 : après match_haut (même bundle du match)
    "kinito_cartes_jeunes",   # 26.19 : après jeunes_candidats_fm24 (posée par-dessus son tableau)
    "kinito_entete_large",    # 26.20 : après tes fonctions de la fiche (entete_fiche, fiche_joueur_plus...)
    "kinito_pays_formation",  # 26.21 : seul à toucher ses deux en-têtes (pays, sélection) : n'importe où
    "kinito_raccourcis_selections",  # 26.23 : seul à toucher son modèle (Tactiques) : n'importe où
    # v6 : retouche PlayerReport (règle « pas en Large ») sur place : après kinito_cartes_jeunes (révélation des
    # jeunes), qui le refait depuis l'original
    "tuile_blessures",
]

# fonction activée ou retirée seule (app, menu) : ces fonctions sont relancées ensuite (« si-actif »), parce qu'elles
# retouchent un modèle que la première vient de réécrire (comme le choix 1, qui les passe après elle)
SUIVANTS = {
    # club_histoire recopie le stade (photo) de la page club faite par club_page_bas
    # + salle_trophees : son bandeau est dans ClubSiteBlock, que club_page_bas refait depuis l'original
    "club_page_bas": ["salle_trophees", "club_histoire", "club_vue_ensemble"],
    # bandeau du club, bulle du club : leurs notes + étoiles d'installations suivent l'interrupteur des notes /20
    "notes_installations": ["club_bandeau_installations", "club_infobulle_offres"],
    # leurs boutons réécrits (écrits) : effectif_equipes (ajout Kinito 26.10) les remet en icônes, selon son option ;
    # dans ORDRE_SKIN, effectif_equipes passe déjà après elles
    # + effectif_repos_equipe : bouton repos posé après leur calendrier (TeamSquadBlock / SquadOverviewTableBlock
    # repartent de l'original)
    # + kinito_raccourcis_selections (v8, 2026-11-14) : boutons de sélections à droite du Sélect. rapide de
    # TeamSquadBlock / SquadOverviewTableBlock (SUIVANTS pas en chaîne : listé partout où ces modèles sont refaits)
    "effectif_boutons_entrainement": ["effectif_equipes", "effectif_repos_equipe", "kinito_raccourcis_selections"],
    "effectif_equipes": ["effectif_repos_equipe", "kinito_raccourcis_selections"],
    # + couleurs_interface : tactiques_boutons repart de l'original de TacticalPlannerHeader (couleurs du bandeau)
    "tactiques_boutons": ["effectif_equipes", "effectif_repos_equipe", "couleurs_interface",
                          "kinito_raccourcis_selections"],
    # couleurs du tableau de score de base (Scoreboard, bundle du match) : match_haut remet tout le bundle d'origine
    # quand on le retire (ou pour défaire son alignement)
    # + Kinito 26.18 : sa fenêtre de but (GoalScoredPopup, même bundle) est refaite ensuite
    "match_haut": ["couleurs_interface", "kinito_fenetre_but"],
    # Kinito 26.19 : ses cartes sont posées dans YouthCandidatesCategoryTable, que jeunes_candidats_fm24 refait depuis
    # l'original
    "jeunes_candidats_fm24": ["kinito_cartes_jeunes", "tuile_blessures"],
    # tuile_blessures v6 : sa règle de visibilité est dans PlayerReport, que la révélation des jeunes (Kinito 26.22,
    # posée par kinito_cartes_jeunes) refait depuis l'original
    "kinito_cartes_jeunes": ["tuile_blessures"],
    # Kinito 26.20 : sa bande est dans PlayerReportHeader, que entete_fiche (entete_tuile) réécrit
    "entete_fiche": ["kinito_entete_large"],
    # Kinito 26.14 / 26.15 (lancés par entrainement_individuel_equipes) et 26.17 : leurs morceaux partent quand ces
    # fonctions repartent de l'original
    "entrainement_individuel_boutons": ["entrainement_individuel_equipes"],
    "entrainement_pouces": ["entrainement_individuel_equipes"],
    # + rencontres_stade_spectateurs : sa version Kinito (kinito_rencontres_vues) a sa colonne « kinito-selection »
    # dans ui-tablefactories (sans elle : plantage du tableau)
    "moral_icone_seule": ["entrainement_individuel_equipes", "kinito_enregistrement", "rencontres_stade_spectateurs"],
    # vue FM Guru (option fiche_fmguru) : refaite par-dessus ce que ces fonctions remettent dans la fiche joueur
    # (attributs_tout_cocher : le tableau d'attributs qu'elle recopie)
    # (fiche_joueur_plus : sa copie du tableau d'attributs pour le mode Large, refaite quand le modèle change)
    # + temperament_infos : posée seule après lui, la ligne Média tomberait dans notre ligne Personnalité (ressortie)
    "style_mediatique": ["temperament_infos", "fiche_joueur_plus", "fiche_fmguru"],
    "hors_defaut": ["fiche_fmguru"],
    "attributs_tout_cocher": ["fiche_fmguru"],
    # Kinito 26.5 réécrit PlayerRecommendationsMainBlock depuis l'original : le rapport façon FM24 est refait dessus
    "kinito_rapports_vues": ["rapport_recrutement_fm24", "colonnes_separateur"],
    # menus Insérer colonne recopiés de l'original (ou ui-tableviews remis d'origine au retrait de
    # colonne_personnalite) : la rubrique Séparateur est remise dessus
    # + colonne_temperament : placée après Personnalité ; remise si ui-tableviews / le menu repart de l'original
    "colonne_personnalite": ["colonne_temperament", "colonnes_separateur"],
    "recherches_ciblees": ["colonne_temperament", "colonnes_separateur"],
    "kinito_capitaines_vues": ["colonnes_separateur"],
    "rencontres_stade_spectateurs": ["colonnes_separateur"],
    # la tuile unique réécrit FinanceOverviewGraphsBlock depuis l'original : les points des courbes sont refaits dessus
    "finances_tuile_unique": ["graphes_finances"],
    # infobulle du joueur remise d'origine par infobulle_pieds : logos de Taille (tuile_forme) refaits dessus
    # + temperament_infos : sa ligne Média posée après tomberait dans notre rangée Personnalité de l'infobulle
    "infobulle_pieds": ["tuile_forme", "temperament_infos"],
    # cartes du terrain du match refaites depuis l'original par photos_match : jaune / buts / passes D remis dessus
    "photos_match": ["match_cartons_buts"],
}

# scripts lancés par le skin sans être une fonction à interrupteur : script -> dossier
AUTRES = {"fiche_fmguru": "joueur_fiche"}   # vue FM Guru : posée par son option, en fin de choix 1

# vue FM Guru choisie (option fiche_fmguru = guru) : elle prend le dessus, ces fonctions sont désactivées (raison
# affichée dans l'app, en rouge) ; elles reviennent quand l'option repasse sur le skin
BLOQUES_GURU = {
    "fiche_joueur_plus": ("Pas compatible avec l'affichage fiche joueur de FM Guru (choisi dans Features "
                          "additionnelles) : désactivée tant qu'il est choisi.",
                          "Not compatible with the FM Guru player profile display (chosen in Additional features): "
                          "disabled while it is chosen."),
    # Kinito 26.20 : sa fiche 1080p Large ne doit jamais se mêler à la vue Guru (fiche_fmguru refait le grand bloc
    # depuis l'original, après elle)
    "kinito_entete_large": ("Pas compatible avec l'affichage fiche joueur de FM Guru (choisi dans Features "
                            "additionnelles) : désactivée tant qu'il est choisi.",
                            "Not compatible with the FM Guru player profile display (chosen in Additional features): "
                            "disabled while it is chosen."),
}
# ... et ces fonctions vont avec elle : activées d'office en la choisissant (badge « Activée avec la vue FM Guru »)
# (+ infobulle du joueur au survol, 2026-11-12, le joueur : celle du skin de base)
# (+ tuiles du bas de la fiche, 2026-11-07, le joueur : ordre, État d'esprit / Condition, Stats carrière)
AVEC_GURU = ["entete_fiche", "style_mediatique", "hors_defaut", "listes_pour_contre", "infobulle_pieds",
             "infobulle_pour_contre", "fiche_ordre_tuiles", "tuile_forme", "tuile_carriere",
             "match_tuile_banc",   # 2026-11-18, demande du joueur : Banc de touche à choix aussi en vue Guru
             # 2026-11-19 (le joueur : « toutes les options de vues dans Guru », séparateurs, vues ; PAS le tempérament)
             "vues_alexjeuvideal", "colonnes_separateur", "colonne_personnalite", "nation_drapeau_seul",
             "moral_icone_seule", "tactiques_forme_valeur",   # colonne Forme avec valeur (5 matchs)
             "recherches_ciblees",   # (le joueur : « perso dans le recrutement ») vues personnalisables du recrutement
             # (le joueur : « toutes les vues modifiables qu'on a ajoutées ») : programme Rencontres (version Kinito,
             # vues), rapports des recruteurs, capitaines (Tout l'effectif)
             "rencontres_stade_spectateurs", "kinito_rapports_vues", "kinito_capitaines_vues"]
# (temperament_infos : jamais en vue Guru, ni fiche ni infobulle, le joueur 2026-11-13)

# zones d'essai : jamais dans le choix 1, retirées au début du choix 1
ESSAIS = ["essai_noms_installations", "essai_retour_entrainement", "essai_ids_attributs",
          "essai_raccourcis_selections",   # 2026-11-13 : sonde des sous-entrées de Sélect. rapide ; 2026-11-14 :
                                           # remplacé par kinito_raccourcis_selections, gardé pour retirer l'essai
          "essai_valeurs_criteres",   # 2026-11-12 : valeur cachée des conditions de recherche (notes du staff ?)
          "essai_fiche_bas_bloc",     # 2026-11-12 : rangée du bas de la fiche en un bloc, sélecteurs gardés
          "essai_repos_effectif",     # 2026-10-30 : devenu effectif_repos_equipe ; gardé pour retirer l'essai
          "essai_trophees_image",     # 2026-11-09 : devenu club\palmares_images.py ; gardé pour retirer l'essai
          "essai_salle_trophees",     # 2026-11-09 : bandeau des trophées à la place des Actualités de la page club
          "essai_carte_monde",        # 2026-11-10 : carte de la connaissance du monde, étape 1 (image par sélection féminine)
          "essai_continuer_club",     # 2026-11-11 : bouton Continuer à la couleur du club (comme FM24)
          "essai_competition_vue",    # 2026-11-12 : Compétition > Vue d'ensemble refaite (v7 : classement | stats en grille | 11 + transferts)
          "essai_selection_top50",    # 2026-11-13 : devenu recrutement\selection_top50 ; gardé pour retirer l'essai
          "essai_salle_honneurs"]     # 2026-11-15 : Honneurs du club = salle des trophées (fond IA + étagères)
# (essai_echelle_1080p : devenu affichage\echelle_1080p.py le 2026-11-12, script supprimé ; la fonction coupée
#  enlève au choix 1 un patch de GameAssembly.dll resté ; ses v1 / v2 (boutons, scène) déjà remises chez le joueur)
# (essai_club_vue_ensemble : devenu club\club_vue_ensemble.py le 2026-11-09, script supprimé ; même préfixe
#  UIPickerVueClub : la fonction refait les modèles posés par l'essai)
# (essai_repos_diag : devenu effectif\repos_diag.py, option « repos_bouton » du bouton repos, le 2026-11-01)
# (essai_image_stade : devenu club_page_bas v14 le 2026-11-12, script supprimé ; essai_stade_defaut : devenu
#  club_page_bas v15 + commun\fonds_jeu.py le 2026-11-12, script supprimé)

# fonctions abandonnées (refusées par le joueur) : script gardé dans son dossier, plus au menu, retirées au début du
# choix 1 (« rien à retirer » si jamais posées). nom : dossier
ABANDONNES = {"tactiques_stats_saison": "tactiques",   # 2026-11-12 : bloc Saison sous le terrain, « j'aime pas »
              # 2026-10-30 : bande note 5 matchs / condition / fatigue sous les cartes du terrain, mise de côté par le
              # joueur (« on verra un autre jour », pas livrée) ; pour la reprendre : FONCTIONS + ORDRE_SKIN après
              # photos_match + SUIVANTS photos_tactiques / photos_match (etat.md, liste « au go »)
              "infos_cartes_terrain": "tactiques",
              # 2026-11-05 (le joueur, avant release v1.62) : Présentation de saison (colonne Cotes jamais affichée,
              # bloc des équipes plus large), « pas prête, on oublie ». Pour la reprendre : FONCTIONS (cat calendrier)
              # + OU + ORDRE_SKIN après moral_icone_seule + SUIVANTS (mêmes que moral_icone_seule : sinon les colonnes
              # Kinito d'ui-tablefactories sautent = plantage). Son retrait ne touche que sa colonne / vue / grilles.
              "saison_presentation": "calendrier",
              # 2026-11-10 : carte du monde de la connaissance (images « continent » par pays), retirée par le
              # joueur : pays blancs (teinte pas prise) + trophée à la place d'un pays ; pas de carte dans FM27
              "carte_monde": "recrutement",
              # 2026-11-17 (le joueur) : MAJ de FM, Moyen / Petit en 1080p dans le jeu -> plus besoin ; retirer =
              # patch resté enlevé, discret si code pas reconnu (DLL neuve)
              "echelle_1080p": "affichage"}

# rangement du 2026-11-12 : ancien marqueur -> nouveaux (les scripts découpés), fait une fois (lancer.py migrer)
MIGRATION = {
    "fiches_plus": ["entete_fiche", "fiche_joueur_plus", "entrainement_individuel_boutons", "staff_fiche"],
    "style_mediatique": ["style_mediatique", "infobulle_pieds"],
    "infobulle_pour_contre": ["infobulle_pour_contre", "listes_pour_contre"],
    "photos_terrain": ["photos_tactiques", "photos_match"],
    "graphes_points": ["graphes_finances", "graphes_attributs"],
    "entrainement_equipes": ["entrainement_equipes", "effectif_boutons_entrainement", "kinito_raccourcis_selections"],
}

assert sorted(ORDRE_SKIN) == sorted(FONCTIONS), set(ORDRE_SKIN) ^ set(FONCTIONS)
assert sorted(OU) == sorted(FONCTIONS), set(OU) ^ set(FONCTIONS)
assert all(f["cat"] in {c for c, _, _ in CATEGORIES} for f in FONCTIONS.values())
assert all(n in FONCTIONS or n in AUTRES for k, v in SUIVANTS.items() for n in [k, *v])
assert all(n in FONCTIONS for n in [*BLOQUES_GURU, *AVEC_GURU])
