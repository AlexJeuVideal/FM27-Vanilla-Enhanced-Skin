"""Options du skin (page 500 de Outils FM.bat) : remplacer un morceau par un autre, ou l'enlever.

Chaque option a plusieurs valeurs (la 1re = celle du skin par défaut). Le choix est gardé dans backups\\options.json
(absent = tout par défaut) ; les scripts le lisent (get) : le choix 1 respecte donc les options. Changer une option
réapplique tout de suite le script concerné (FM fermé).

Ajouter une option : une entrée dans OPTIONS (titre, valeurs, script), puis lire options.get("<nom>") dans le script
et faire dépendre son VERSION de la valeur (sinon « déjà appliqué »).

Usage :
  .venv\\Scripts\\python.exe outils\\commun\\options.py liste
  .venv\\Scripts\\python.exe outils\\commun\\options.py changer <numéro>       (valeur suivante : menu 500)
  .venv\\Scripts\\python.exe outils\\commun\\options.py choisir <nom> <valeur>  (l'app)
"""
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
from langue import texte as L  # noqa: E402

FICHIER = os.path.join(backup.BACKUP_DIR, "options.json")

# nom : titre (fr, en), [(valeur, (libellé fr, en))], script à réappliquer (son choix « si-actif »), au besoin aide
# (fr, en) et kinito (True : ajout de Kinito, affiché dans la section Kinito de la page Options) ; les deux langues
# sont gardées (l'app les affiche selon sa langue) : titre() / libelle() donnent celle des textes du skin
OPTIONS = {
    # club_amical v42 (demande du joueur), validé le 2026-11-12 (v43)
    "amical_partie": {
        "titre": ("Organiser amical : taille de ta partie", "Arrange Friendly: size of your save"),
        "valeurs": [("grosse", ("grosse partie (plusieurs pays) : rapide", "big save (several countries): fast")),
                    ("petite", ("petite partie (un seul pays) : plus lent, plus sûr",
                                "small save (a single country): slower, safer"))],
        "script": "club_amical",
        "aide": ("Le bouton cherche le numéro de l'équipe dans ta partie (FM ne sait pas choisir un adversaire autrement). "
                 "« Grosse partie » va plus vite ; sur une partie avec un seul pays, si l'équipe trouvée n'est pas la "
                 "bonne (surtout U19 / U21), prends « petite partie ».",
                 "The button searches for the team's number in your save (FM can't pick an opponent any other way). "
                 "« Big save » is faster; on a save with a single country, if the team found is not the right one "
                 "(mostly U19 / U21), choose « small save »."),
    },
    "fond_pages": {
        "titre": ("Fond des pages (choix 30)", "Page background (choice 30)"),
        "valeurs": [("couleur", ("ta couleur partout", "your colour everywhere")),
                    ("competitions", ("ta couleur, mais les compétitions sous licence avec leur fond (LDC, PL…)",
                                      "your colour, but licensed competitions keep their background (UCL, PL…)")),
                    ("officiels", ("fonds de FM partout, comme le jeu de base",
                                   "FM's backgrounds everywhere, like the base game"))],
        "script": "theme_fond",
    },
    # 2026-11-05 (le joueur, v1.62) : « logo + 3 lettres » essayé en choix de base, vu en jeu : logo seul gardé
    # (« sans les initiales, c'est bien mieux »)
    "nationalite": {
        "titre": ("Tableaux, colonne Nationalité", "Tables, Nationality column"),
        "valeurs": [("logo", ("logo seul, plus grand", "logo only, bigger")),
                    ("3lettres", ("logo + 3 lettres", "logo + 3 letters"))],
        "script": "nation_drapeau_seul",
    },
    "nationalite_2": {
        "titre": ("Tableaux, colonne 2e nationalité", "Tables, 2nd Nationality column"),
        "valeurs": [("logo", ("logo seul, plus grand", "logo only, bigger")),
                    ("3lettres", ("logo + 3 lettres", "logo + 3 letters"))],
        "script": "nation_drapeau_seul",
    },
    # ajout Kinito 26.10 (outils\kinito\kinito_effectif_vue.py), porté par effectif_equipes : boutons d'Alex en icônes
    # (choix de base, 2026-11-12, demande du joueur) ou écrits ; liens / boutons des équipes dans les deux cas
    "boutons_effectif": {
        "titre": ("Boutons Entraînement / Individuel / Programme (Effectif, Tactiques)",
                  "Training / Individual / Fixture Schedule buttons (Squad, Tactics)"),
        "valeurs": [("icones", ("en icônes, nom au survol", "as icons, name on hover")),
                    ("texte", ("écrits", "written"))],
        "script": "effectif_equipes",
    },
    # Kinito 26.23 (kinito_raccourcis_selections v8, 2026-11-14, le joueur) : « haut » de base ; « filtre » = la place
    # de Kinito ; seulement l'écran Tactiques
    "selections_emplacement": {
        "titre": ("Tactiques : place des boutons de sélections", "Tactics: team selection buttons position"),
        "valeurs": [("haut", ("en haut, à droite de « Sélect. rapide »", "at the top, right of \"Quick Pick\"")),
                    ("filtre", ("au-dessus du tableau, à gauche de « Filtre » (place de Kinito)",
                                "above the table, left of \"Filter\" (Kinito's position)"))],
        "script": "kinito_raccourcis_selections",
        "kinito": True,
    },
    # version Kinito : ses scripts outils\kinito\kinito_rencontres_*.py, appliqués / retirés par rencontres_version.py
    "rencontres": {
        "titre": ("Calendrier, onglet Rencontres", "Calendar, Fixtures tab"),
        # 2026-11-12 : version Kinito = choix de base (demande du joueur)
        # 2026-11-17 : colonnes Stade / Spectateurs du skin retirées (tableau de FM maintenant) ; tableau Kinito gardé
        "valeurs": [("kinito", ("version Kinito (boutons dans le bandeau, programme en tableau avec vues et filtre)",
                                "Kinito version (buttons in the header, schedule as a table with views and filter)")),
                    ("skin", ("version du skin (boutons des équipes à droite)",
                              "skin version (team buttons on the right)"))],
        "script": "rencontres_stade_spectateurs",
        "kinito": True,   # app : dans la section Kinito de la page Options (pas sous sa fonction)
        "aide":("Version Kinito : boutons des équipes juste après « Programme des rencontres », et le programme a des "
                 "vues perso, des colonnes au choix et un filtre par compétition / domicile / extérieur. En petite "
                 "fenêtre, le tableau de FM reste.",
                 "Kinito version: team buttons right after \"Fixture Schedule\", and the schedule gets custom views, "
                 "columns of your choice and a filter by competition / home / away. In a small window, FM's table "
                 "stays."),
    },
    "fenetre_but": {   # 26.18 v3 : la fenêtre de but des compétitions sous licence aussi ; v10 (Kinito, 2026-11-10) : les 9
        "titre": ("Match : fenêtre de but", "Match: goal pop-up"),
        # « toutes » de base depuis le 2026-11-09 (le joueur)
        "valeurs": [("toutes", ("toutes les compétitions, sous licence comprises",
                                "all competitions, licensed ones included")),
                    ("ordinaire", ("compétitions sans licence seulement", "competitions without a licence only"))],
        "script": "kinito_fenetre_but",
        "kinito": True,
        "aide": ("Les compétitions sous licence ont leur propre fenêtre de but. « Toutes » y met la nôtre (photo, "
                 "bandeau), aux couleurs et dans la police de la compétition, avec le nombre de matchs du buteur.",
                 "Licensed competitions have their own goal pop-up. « All » puts ours there (photo, band), in the "
                 "competition's colours and font, with the scorer's number of matches."),
    },
    # (« cartes_jeunes » retirée le 2026-11-11, paquet de Kinito : 26.19 v31 + 26.22 v18, le style, la révélation et
    #  la façon se choisissent dans le message ; le script ne lit plus cette option)
    # 26.13 v48 (06/11, demandes de Kinito) : trois options ; la 1re valeur = celle de qui ne touche à rien
    # (v49, Kinito : « terrain à gauche » par défaut)
    "consignes_fm24_disposition": {
        "titre": ("Consignes d'équipe : disposition de la vue FM24", "Team instructions: FM24 view layout"),
        "valeurs": [("fm27", ("terrain à gauche, consignes, phases à droite (comme FM 27)",
                              "pitch on the left, instructions, phases on the right (as in FM 27)")),
                    ("miroir", ("phases à gauche, consignes, terrain à droite",
                                "phases on the left, instructions, pitch on the right"))],
        "script": "kinito_consignes_essai_b",
        "kinito": True,
        "aide": ("L'ordre des trois blocs de l'écran Consignes d'équipe, en vue FM24 seulement (Tuiles et Terrain ne "
                 "changent pas).",
                 "The order of the three blocks of the Team instructions screen, in the FM24 view only (Tiles and "
                 "Pitch do not change)."),
    },
    "consignes_arrivee": {
        "titre": ("Consignes d'équipe : vue à l'arrivée", "Team instructions: view on arrival"),
        "valeurs": [("tuiles", ("Tuiles (celles de FM 27)", "Tiles (FM 27's)")),
                    ("fm24", ("FM24", "FM24")),
                    ("terrain", ("Terrain", "Pitch"))],
        "script": "kinito_consignes_essai_b",
        "kinito": True,
        "aide": ("La vue de l'écran Consignes d'équipe à la première arrivée ; ensuite, le jeu garde la dernière que "
                 "tu as cliquée.",
                 "The view of the Team instructions screen on first arrival; after that, the game keeps the last one "
                 "you clicked."),
    },
    "consignes_indiv_arrivee": {
        "titre": ("Consignes individuelles : vue à l'ouverture", "Player instructions: view on opening"),
        "valeurs": [("fm27", ("FM 27", "FM 27")),
                    ("fm24", ("FM24", "FM24"))],
        "script": "kinito_consignes_essai_b",
        "kinito": True,
        "aide": ("La vue de la fenêtre des consignes individuelles à la première ouverture ; ensuite, le jeu garde la "
                 "dernière que tu as cliquée.",
                 "The view of the player instructions window on first opening; after that, the game keeps the last "
                 "one you clicked."),
    },
    # medias_entrainement (2026-11-12) RETIRÉE le 2026-11-26 (le joueur : « maintenant c'est full custom ») : la vue
    # Détails de l'entraînement individuel a des vues perso (Insérer colonne propose Rapports médias) ; vue de base =
    # l'ancien choix de base « sans » (Personnalité seule), voir kinito_largeur_liste.avec_medias
    # 2026-11-05 (le joueur) : lu par entete_fiche (entete_tuile) ; « tuile » = nouvel en-tête en grande tuile
    # (largeurs fixes, polygone, statut), choix de base depuis le 2026-11-05 (le joueur, + FORCES) ; « fm » = en-tête
    # de FM retouché comme avant. En premier (ordre de l'app, 2026-11-07) : il commande les options « sans_effet »
    "entete_vue": {
        "titre": ("En-tête de la fiche joueur", "Player profile header"),
        # 2026-11-07 (entete_tuile v30) : chaque info dans sa carte, polygone à droite (Progression en Small)
        "valeurs": [("tuile", ("en cartes : identité, âge, contrat, nation, valeur, club, dispos, niveau, polygone "
                               "(Progression en Small)",
                               "in cards: identity, age, contract, nation, value, club, availability, ability, "
                               "polygon (Progression in Small)")),
                    ("fm", ("en-tête de FM (retouché)", "FM header (tweaked)"))],
        "script": "entete_fiche",
        # taille cachée dans Infos avec la grande tuile (elle est dans l'en-tête) ; Kinito 26.20 refaite (si-actif)
        "aussi": ["fiche_joueur_plus", "kinito_entete_large"],
    },
    # 2026-11-19 (le joueur, maquette « A ») : lu par entete_fiche (entete_tuile) ; « numero » = grand numéro du maillot
    # derrière la photo, nom plus gros, trait doré à gauche, cartes sans fond ni bord (« que l'en-tête se fonde dans le
    # skin ») ; « gomez » validé en jeu 2026-11-19 (fiche du skin de base)
    "entete_style": {
        "titre": ("Style de l'en-tête en cartes", "Card header style"),
        "valeurs": [("cartes", ("cartes (fond et bord)", "cards (background and border)")),
                    ("numero", ("grand numéro, cases fondues aux couleurs du club",
                                "big number, boxes blended into the club colours")),
                    ("gomez", ("3 tuiles qui regroupent : identité, club, statut",
                               "3 grouped tiles: identity, club, status"))],
        "script": "entete_fiche",
        # fiche_joueur_plus : taille d'Infos remise avec « gomez » (l'en-tête ne la montre plus)
        "aussi": ["kinito_entete_large", "fiche_joueur_plus"],
        "sans_effet": ("entete_vue", "fm"),
    },
    # 2026-11-12 (le joueur) : lu par entete_fiche (bandeau Pour / Contre, mode Large) ; « 2 » de base
    "pour_contre_lignes": {
        "titre": ("Pastilles Pour / Contre de l'en-tête", "Pros / Cons dots in the header"),
        "valeurs": [("2", ("sur 2 lignes si elles sont nombreuses", "on 2 rows when there are many")),
                    ("1", ("sur 1 ligne (le surplus est caché)", "on 1 row (the extra ones are hidden)"))],
        "script": "entete_fiche",
        "aussi": ["kinito_entete_large"],   # Kinito 26.20 refaite (si-actif) quand entete_fiche est réappliquée
        # grande tuile : pas de pastilles dans l'en-tête (elle passe avant) ; l'app range ces options dans un groupe
        # « Seulement avec l'en-tête de FM », replié et grisé avec la grande tuile
        "sans_effet": ("entete_vue", "tuile"),
    },
    # 2026-10-30 (le joueur, v1.41) : lu par fiche_joueur_plus (colonne à droite d'Infos en Large) et entete_fiche
    # (« pour_contre » : plus de pastilles dans l'en-tête, elles sont dans la fiche)
    "fiche_large_colonne": {
        "titre": ("Fiche joueur (mode Large), à droite d'Infos", "Player profile (Large mode), right of Info"),
        "valeurs": [("polygone", ("polygone seul (Pour / Contre en pastilles dans l'en-tête)",
                                  "polygon alone (Pros / Cons as dots in the header)")),
                    ("pour_contre", ("Pour / Contre, bouton pour voir le polygone (plus de pastilles dans l'en-tête)",
                                     "Pros / Cons, button to see the polygon (no more dots in the header)"))],
        "script": "fiche_joueur_plus",
        # autres scripts qui lisent l'option (réappliqués aussi) ; Kinito 26.20 refaite (si-actif)
        "aussi": ["entete_fiche", "kinito_entete_large"],
        # grande tuile : Large = Pour / Contre seuls (fiche_joueur_plus LARGE_PC_SEULS), cette option ne compte plus
        "sans_effet": ("entete_vue", "tuile"),
        # app (2026-11-07) : affichée aussi sous la tuile de l'en-tête, à côté de l'option qui la commande
        "afficher_aussi": "entete_fiche",
        # 2026-11-07 (le joueur : « préviens sur l'app, sinon les gens peuvent être confus »)
        # (lignes : l'app garde les retours à la ligne des aides d'options)
        "aide": ("Ce qui s'affiche à droite d'Infos dépend de l'option « En-tête de la fiche joueur » :\n"
                 "• Grande tuile (choix de base) : le polygone est dans l'en-tête, donc ici Pour / Contre seuls. "
                 "Ce réglage ne sert à rien.\n"
                 "• En-tête de FM : ce réglage choisit. « Polygone seul » : le polygone ici, les Pour / Contre en "
                 "pastilles dans l'en-tête. « Pour / Contre » : les Pour / Contre ici, un bouton pour voir le polygone.",
                 "What shows right of Info depends on the \"Player profile header\" option:\n"
                 "• Big tile (default): the polygon is in the header, so Pros / Cons only here. This setting does "
                 "nothing.\n"
                 "• FM header: this setting decides. \"Polygon alone\": the polygon here, Pros / Cons as dots in the "
                 "header. \"Pros / Cons\": Pros / Cons here, a button to see the polygon."),
    },
    # 2026-11-14 (le joueur, demande de hunfair) : lu par entete_fiche (entete_tuile : carte de droite de l'en-tête en
    # Medium) et fiche_joueur_plus (colonne à droite d'Infos en Medium) ; les deux vont ensemble : polygone à droite
    # d'Infos = Pour / Contre en haut, forcément. En-tête en cartes seulement (vue de FM / FM Guru : sans effet)
    "fiche_medium_colonne": {
        "titre": ("Fiche joueur, affichage Moyen seulement : polygone ou Pour / Contre",
                  "Player profile, Medium display only: polygon or Pros / Cons"),
        "valeurs": [("pour_contre", ("polygone dans l'en-tête, Pour / Contre à droite d'Infos",
                                     "polygon in the header, Pros / Cons right of Info")),
                    ("polygone", ("Pour / Contre en pastilles dans l'en-tête, polygone à droite d'Infos",
                                  "Pros / Cons as dots in the header, polygon right of Info"))],
        "script": "entete_fiche",
        "aussi": ["fiche_joueur_plus", "kinito_entete_large"],
        "aide": ("Affichage Moyen (Medium) seulement : en Large et en Petit, rien ne change. Avec l'en-tête en cartes "
                 "(choix de base). Les deux s'échangent ensemble : "
                 "quand le polygone est à droite d'Infos, les Pour / Contre passent en pastilles dans la carte de "
                 "droite de l'en-tête (survol d'une pastille = son texte).",
                 "Medium display only: nothing changes in Large and Small. With the card header (default). Both swap "
                 "together: when the polygon is right of "
                 "Info, the Pros / Cons move as dots into the header's right card (hover a dot to read it)."),
    },
    # 2026-11-15 (le joueur : « on peut aussi le faire en large ? », puis « les gens pourront choisir ») : pareil en
    # Large, 3 choix ; lu par entete_fiche (entete_tuile : carte de droite de l'en-tête en Large) et fiche_joueur_plus
    # (colonne à droite d'Infos en Large). En-tête en cartes seulement
    "fiche_large_tuile": {
        "titre": ("Fiche joueur, affichage Large seulement : polygone et Pour / Contre",
                  "Player profile, Large display only: polygon and Pros / Cons"),
        "valeurs": [("entete", ("polygone dans l'en-tête, Pour / Contre à droite d'Infos",
                                "polygon in the header, Pros / Cons right of Info")),
                    ("pastilles", ("Pour / Contre en pastilles dans l'en-tête, polygone à droite d'Infos",
                                   "Pros / Cons as dots in the header, polygon right of Info")),
                    ("dessous", ("rien à droite de l'en-tête, polygone puis Pour / Contre dessous, à droite d'Infos",
                                 "nothing on the header's right, polygon then Pros / Cons below, right of Info"))],
        "script": "entete_fiche",
        "aussi": ["fiche_joueur_plus", "kinito_entete_large"],
        "aide": ("Affichage Large seulement : en Moyen et en Petit, rien ne change. Avec l'en-tête en cartes "
                 "(choix de base). Pastilles : survol d'une pastille = son texte. Sans rapport sur le joueur, "
                 "les Pour / Contre laissent la place à la phrase de FM et au bouton Observer joueur.",
                 "Large display only: nothing changes in Medium and Small. With the card header (default). Dots: "
                 "hover a dot to read it. With no report on the player, Pros / Cons give way to FM's sentence and "
                 "the Scout player button."),
    },
    # 2026-10-31 (le joueur) : lu par club_bandeau_installations (bandeau du club) et club_infobulle_offres (bulle
    # « i » du club) : « sans » = section Installations retirée des deux (ni notes ni étoiles) ; pages Installations
    # du club pas touchées (notes_installations)
    "etoiles_installations": {
        "titre": ("Installations dans le bandeau et la bulle du club (notes + étoiles)",
                  "Facilities in the club banner and club tooltip (ratings + stars)"),
        "valeurs": [("avec", ("affichées (notes + étoiles)", "shown (ratings + stars)")),
                    ("sans", ("retirées (ni notes ni étoiles)", "removed (no ratings, no stars)"))],
        "script": "club_bandeau_installations",
        "aussi": ["club_infobulle_offres"],
        "aide": ("« Retirées » enlève les notes et les étoiles des installations partout où le skin les ajoute : le "
                 "bandeau du haut de la page de chaque club, et toutes les bulles « i » des clubs (offres de transfert "
                 "/ prêt reçues, colonne Club de tous les tableaux : recrutement, recherche, base de données…). Le "
                 "reste du bandeau et des bulles reste, sans place vide. Les pages Club > Installations ne changent "
                 "pas (case « Installations : notes /20 »).",
                 "« Removed » takes the facility ratings and stars out of everywhere the skin adds them: the banner at "
                 "the top of every club page, and all the club « i » tooltips (transfer / loan offers received, Club "
                 "column of every table: recruitment, search, database…). The rest of the banner and tooltips stays, "
                 "no empty space. The Club > Facilities pages don't change (« Facilities: ratings /20 » box)."),
    },
    # (« repos_bouton » normal / diag retirée le 2026-11-07, v1.66 : le diag a fait son travail, bouton seul)
    # demande d'un ami du joueur (2026-11-12) ; 2026-11-12 : script à part fiche_fmguru.py, qui prend le dessus
    # (catalogue.BLOQUES_GURU désactivées) ; changer l'option refait tout le skin à partir des originaux
    "fiche_fmguru": {
        "titre": ("Fiche joueur (mode Large)", "Player profile (Large mode)"),
        "valeurs": [("skin", ("version du skin (Pour / Contre à la place du polygone)",
                              "skin version (Pros / Cons instead of the polygon)")),
                    ("guru", ("version FM Guru (Infos plus étroite, polygone à côté, sans Suspensions)",
                              "FM Guru version (narrower Info, polygon next to it, no Suspensions)"))],
        "script": "fiche_fmguru",
        "refaire_tout": True,
        "bloque": "guru",   # app : avec cette valeur, catalogue.BLOQUES_GURU sont désactivées (avertissement rouge)
        "fmguru": True,   # app : dans la section FM Guru de la page Features additionnelles
        "aide": ("Version FM Guru : seulement la fiche joueur (en-tête de FM avec Pour / Contre en pastilles, "
                 "polygone des attributs à côté des Infos, Efficacité tactique à la place d'Entraînement en bas) et "
                 "l'infobulle du joueur du skin, plus le Banc de touche en tuile à choix en match ; le reste du jeu "
                 "reste celui de FM.",
                 "FM Guru version: only the player profile (FM header with Pros / Cons dots, attribute polygon next "
                 "to Info, Tactical effectiveness instead of Training at the bottom) and the skin's player tooltip, "
                 "plus the Touchline as a selectable tile in matches; the rest of the game stays FM's."),
    },
    # 2026-11-10 (le joueur) : essai, pas validé en jeu (score_disposition.licence, lu par match_haut) ; en dernier
    # (menu 500 : les numéros des autres options ne bougent pas)
    "score_licence": {
        "titre": ("Match : tableau de score des compétitions sous licence",
                  "Match: scoreboard of licensed competitions"),
        "valeurs": [("licence", ("celui de la compétition (Ligue des champions, Bundesliga…)",
                                 "the competition's own (Champions League, Bundesliga…)")),
                    ("notre", ("notre tableau partout", "our scoreboard everywhere"))],
        "script": "match_haut",
        "aide": ("Les compétitions sous licence ont leur propre tableau de score en match. « Notre tableau partout » "
                 "y met le nôtre (logos, couleurs des maillots, temps dessous).",
                 "Licensed competitions have their own match scoreboard. « Our scoreboard everywhere » puts ours "
                 "there (logos, kit colours, time below)."),
    },
    # 2026-11-11 (retour Discord : Potentiel / Niveau actuel bloqués à 100) : la version chiffres des lignes de
    # Modifier recherche (notes_staff, boîtes v21) passe en option, pas de base
    "staff_recherche": {
        "titre": ("Recherche de staff, lignes de Modifier recherche", "Staff search, Edit search rows"),
        "valeurs": [("fm", ("menu de FM (Bon, Très bon...)", "FM's menu (Good, Very good...)")),
                    ("chiffres", ("notes 1-20 avec + / - (casse certaines choses)",
                                  "ratings 1-20 with + / - (breaks some things)"))],
        "script": "notes_staff",
        "aide": ("« Notes 1-20 » remplace le menu de FM par une zone à chiffres avec + / -, mais casse certaines "
                 "choses : dans la recherche de JOUEURS, Potentiel et Niveau actuel ne montent plus au-dessus de 100 "
                 "(un choix à 200 revient à 100) ; les + / - avancent de 5 en 5 et peuvent sortir de 1-20.",
                 "« Ratings 1-20 » replaces FM's menu with a number box with + / -, but breaks some things: in the "
                 "PLAYER search, Potential and Current ability can no longer go above 100 (picking 200 goes back to "
                 "100); the + / - move 5 at a time and can leave 1-20."),
    },
    # --- 2026-11-19 : à la fin (menu 500 : les numéros des autres options ne bougent pas) ---
    # (le joueur : « la couleur derrière les tuiles en haut, désactivable dans l'app ») : lu par entete_fiche
    # (entete_tuile : dégradé du club de l'en-tête de FM, caché si « non ») ; « oui » de base (comme avant) ; un thème
    # de l'app la met sur « non » (« FM d'origine » : « oui »)
    "entete_couleur_club": {
        "titre": ("Couleur du club derrière l'en-tête", "Club colour behind the header"),
        "valeurs": [("oui", ("oui (dégradé aux couleurs du club, comme FM)", "yes (club colour gradient, like FM)")),
                    ("non", ("non (fond du skin seul)", "no (skin background only)"))],
        "script": "entete_fiche",
        "aussi": ["kinito_entete_large"],
        "sans_effet": ("entete_vue", "fm"),
    },
    # (le joueur, v2.07) : la fiche du skin de base (FICHE_BASE : en-tête en 3 tuiles, Pour / Contre en haut en Moyen /
    # Large, polygone + Projets à droite d'Infos) ; « oui » de base et forcé une fois (FORCES) ; « non » = les réglages
    # du joueur (gardés, jamais écrasés) reprennent. Sans effet avec la vue FM Guru ou la fiche Kinito (26.20)
    "fiche_skin_base": {
        "titre": ("Fiche du skin de base", "Skin's default profile"),
        "valeurs": [("oui", ("oui (la fiche joueur du skin, réglages ci-dessous sans effet)",
                             "yes (the skin's player profile, settings below have no effect)")),
                    ("non", ("non (tes réglages ci-dessous)", "no (your settings below)"))],
        "script": "entete_fiche",
        "aussi": ["fiche_joueur_plus", "kinito_entete_large"],
        "aide": ("La fiche joueur du skin : en-tête en 3 tuiles (identité, club, Pour / Contre), polygone et Projets à "
                 "droite d'Infos. Tes réglages de la fiche restent gardés en dessous : mets « non » puis Appliquer "
                 "pour les retrouver. Sans effet avec la vue FM Guru ou la fiche de Kinito.",
                 "The skin's player profile: header in 3 tiles (identity, club, Pros / Cons), polygon and Plans right "
                 "of Info. Your profile settings stay kept below: pick « no » then Apply to get them back. No effect "
                 "with the FM Guru view or Kinito's profile."),
    },
}


def titre(nom):
    return L(*OPTIONS[nom]["titre"])


def libelle(nom, valeur):
    return L(*dict(OPTIONS[nom]["valeurs"])[valeur])


def defaut(nom):
    """valeur du skin de base (la 1re)"""
    return OPTIONS[nom]["valeurs"][0][0]


# options remises UNE FOIS sur une valeur pour tout le monde (v1.62, le joueur : grande tuile de l'en-tête pour tous à
# la réinstallation après la MAJ) : fait au début du choix 1, noté dans « _forces » d'options.json ; un choix fait
# ensuite (app, menu 500) est gardé, on ne repasse plus dessus
# staff_recherche (v1.78, le joueur) : menu de FM forcé une fois (Potentiel / Niveau actuel jusqu'à 200)
FORCES = {"entete_vue": "tuile", "staff_recherche": "fm",
          # 2026-11-19 (le joueur, v2.07) : fiche du skin de base une fois pour tous (réglages gardés, un bouton pour
          # revenir aux leurs)
          "fiche_skin_base": "oui"}
# 2026-11-19 (le joueur) : « Fiche du skin de base » = ces valeurs tant qu'elle est active (fiche_base_active)
FICHE_BASE = {"entete_vue": "tuile", "entete_style": "gomez", "fiche_medium_colonne": "polygone",
              "fiche_large_tuile": "pastilles"}
CLE_FORCES = "_forces"


def appliquer_forces():
    d = _lire()
    faits = [n for n in d.get(CLE_FORCES, []) if isinstance(n, str)]
    a_faire = [n for n in FORCES if n not in faits]
    if not a_faire:
        return
    for n in a_faire:
        d[n] = FORCES[n]
        print(L("Option remise sur le choix de base :", "Option set back to the default:")
              + f" {titre(n)} : {libelle(n, FORCES[n])}")
    d[CLE_FORCES] = faits + a_faire
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)


def _lire():
    try:
        with open(FICHIER, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _choisie(nom):
    """valeur enregistrée (ou forcée par le .bat) de l'option nom, sans la fiche du skin de base"""
    valeurs = [v for v, _ in OPTIONS[nom]["valeurs"]]
    # 2026-11-19 : tests du .bat (124) : UIPICKER_OPTION_<nom> force une valeur sans toucher aux réglages du joueur
    v = os.environ.get("UIPICKER_OPTION_" + nom)
    if v in valeurs:
        return v
    v = _lire().get(nom)
    return v if v in valeurs else valeurs[0]


def fiche_base_active():
    """« Fiche du skin de base » (option fiche_skin_base = oui) et ni vue FM Guru ni fiche Kinito (26.20, qui
    remplace la fiche du skin) : les options de FICHE_BASE prennent ses valeurs (réglages du joueur gardés)"""
    if _choisie("fiche_skin_base") != "oui" or _choisie("fiche_fmguru") == "guru":
        return False
    return not os.path.exists(os.path.join(backup.BACKUP_DIR, "kinito_entete_large.actif"))


def get(nom):
    """valeur de l'option nom (la 1re valeur si rien n'est choisi ou si la valeur n'existe plus) ; options de la fiche
    joueur : celles de FICHE_BASE tant que la fiche du skin de base est active (pas un choix forcé du .bat)"""
    if (nom in FICHE_BASE and not os.environ.get("UIPICKER_OPTION_" + nom)
            and fiche_base_active()):
        return FICHE_BASE[nom]
    return _choisie(nom)


def liste():
    for i, nom in enumerate(OPTIONS, 1):
        actuelle = get(nom)
        choix = " / ".join(f"[{libelle(nom, v)}]" if v == actuelle else libelle(nom, v)
                           for v, _ in OPTIONS[nom]["valeurs"])
        repere = "" if actuelle == defaut(nom) else L("   <== PAS le choix de base", "   <== NOT the default")
        print(f"  {i}. {titre(nom)} : {choix}{repere}")
    print()
    print(L("  [ ] = choix actuel ; le choix de base est toujours le 1er de la ligne.",
            "  [ ] = current choice; the default is always the first one on the line."))


def changer(numero):
    noms = list(OPTIONS)
    if not numero.isdigit() or not 1 <= int(numero) <= len(noms):
        print(L("numéro d'option inconnu", "unknown option number"))
        return
    nom = noms[int(numero) - 1]
    valeurs = [v for v, _ in OPTIONS[nom]["valeurs"]]
    choisir(nom, valeurs[(valeurs.index(get(nom)) + 1) % len(valeurs)])


def choisir(nom, nouvelle):
    """met l'option nom sur la valeur nouvelle et réapplique son script s'il est activé (FM fermé)"""
    o = OPTIONS.get(nom)
    if o is None or nouvelle not in dict(o["valeurs"]):
        sys.exit(L("option ou valeur inconnue", "unknown option or value"))
    # options supprimées (club_budgets, v14) : oubliées ; « _forces » gardé (sinon reforcé au choix 1 suivant)
    d = {k: v for k, v in _lire().items() if k in OPTIONS or k in (CLE_FORCES, CLE_ORDRE)}
    avant = get(nom)
    d[nom] = nouvelle
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    print(f"{titre(nom)} : {libelle(nom, nouvelle)}"
          + ("" if nouvelle == defaut(nom) else L("  (pas le choix de base)", "  (not the default)")))
    if o.get("refaire_tout"):   # tout réécrit à partir des originaux, dans les deux sens (fiche FM Guru)
        import notes_au_lieu_des_libelles as nb
        import sauvegarde_originaux as backup
        import subprocess
        if not any(os.path.exists(backup.backup_path(b)) for b in nb.BUNDLES):
            print(L("(skin pas encore installé : l'option servira à l'installation)",
                    "(skin not installed yet: the option will be used on install)"))
            return
        import catalogue
        import lancer

        def poser(n):
            with open(lancer.marqueur(n), "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)
        if nouvelle == o.get("bloque"):
            # mode FM Guru (2026-11-12, le joueur) : seulement la fiche joueur ; tout le reste du skin coupé, ce que la
            # vue garde (catalogue.AVEC_GURU) activé d'office
            for n in catalogue.FONCTIONS:
                if n in catalogue.AVEC_GURU:
                    if not lancer.actif(n):
                        poser(n)
                elif lancer.actif(n):
                    os.remove(lancer.marqueur(n))
            print(L("mode FM Guru : tout le skin coupé sauf la fiche joueur et l'infobulle du joueur (",
                    "FM Guru mode: the whole skin turned off except the player profile and the player tooltip (")
                  + ", ".join(L(catalogue.FONCTIONS[n]["fr"], catalogue.FONCTIONS[n]["en"]) for n in catalogue.AVEC_GURU)
                  + ")")
        elif avant == o.get("bloque"):   # sortie du mode Guru : le skin de base revient
            for n, f in catalogue.FONCTIONS.items():
                if not f.get("facultatif") and not lancer.actif(n):
                    poser(n)
            print(L("sortie du mode FM Guru : skin de base remis", "leaving FM Guru mode: default skin back"))
        print(L("fichiers d'origine du jeu remis, puis le skin refait avec ce choix\n",
                "game's original files put back, then the skin redone with this choice\n"))
        lancer.tout_d_origine()
        import langue
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lancer.py"),
                        "skin", langue.LANGUE], env=dict(os.environ, **{lancer.DEPART_ORIGINE: "1"}))
        return
    for i, script in enumerate([o["script"]] + o.get("aussi", [])):
        mod = importlib.import_module(script)
        if os.path.exists(mod.MARKER):
            mod.main(["si-actif"])
        elif i == 0:
            print(L("(fonction pas activée : l'option servira quand elle le sera)",
                    "(feature not enabled: the option will be used when it is)"))


# 2026-11-11 (le joueur) : ordre des tuiles du bas de la fiche choisi à la main (glisser-déposer dans l'app, section
# Fiche joueur) ; lu par fiche_ordre_tuiles (sa liste ORDRE de base sinon) ; gardé par choisir() comme « _forces »
CLE_ORDRE = "_ordre_tuiles"


def ordre_tuiles():
    """ordre perso des tuiles (liste de noms de FM), None = ordre du skin ; validé par fiche_ordre_tuiles"""
    v = _lire().get(CLE_ORDRE)
    return v if isinstance(v, list) and all(isinstance(x, str) for x in v) else None


def choisir_ordre(valeur):
    """« skin » = ordre du skin, sinon noms séparés par des virgules ; réapplique fiche_ordre_tuiles s'il est activé"""
    d = _lire()
    if valeur == "skin":
        d.pop(CLE_ORDRE, None)
    else:
        d[CLE_ORDRE] = [x for x in valeur.split(",") if x]
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    print(L("Ordre des tuiles de la fiche : ", "Profile tiles order: ") + (L("celui du skin", "the skin's") if valeur == "skin"
                                                                            else " | ".join(d[CLE_ORDRE])))
    mod = importlib.import_module("fiche_ordre_tuiles")
    if os.path.exists(mod.MARKER):
        mod.main(["si-actif"])
    else:
        print(L("(fonction pas activée : l'ordre servira quand elle le sera)",
                "(feature not enabled: the order will be used when it is)"))


def main(argv):
    if argv[:1] == ["liste"]:
        liste()
    elif argv[:1] == ["ordre_tuiles"] and len(argv) > 1:
        choisir_ordre(argv[1])
    elif argv[:1] == ["changer"] and len(argv) > 1:
        changer(argv[1])
    elif argv[:1] == ["choisir"] and len(argv) > 2:
        choisir(argv[1], argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
