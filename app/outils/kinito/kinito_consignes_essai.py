"""[AJOUT KINITO] Tactiques > Consignes d'équipe : ESSAI À UN BOUTON — la consigne « Rythme » en 5 boutons au-dessus
des cartes, réglable en un clic.

HORS DU MENU depuis le 12/11/2026 (choix de Kinito) : l'écran des consignes gardé est kinito_consignes_essai_b
(menu 26, fonction 13), qui IMPORTE ce script et n'en remplace que la disposition. Ce fichier reste donc : c'est la
base de kinito_consignes_essai_b (boutons de FM, cases, infobulles, langues, construction, retrait). Lancé seul, il
pose encore l'ancienne disposition (et retire l'autre) : ne plus le lancer.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : remplacer la grille de cartes des consignes d'équipe par des terrains façon FM24
(maquette « 3 terrains », chantier-consignes). Avant de construire l'écran entier, CET ESSAI prouve en jeu le seul
point non vu : qu'un bouton posé par le skin dans ce bloc change vraiment la consigne (avant-match ET en match).

Ce qui est recopié, sans rien inventer (mesuré, outils-analyse\\bouton_consigne.py, codes_options.py) :
- le bouton de consigne de FM (modèle inclus TacticTeamInstructionMultipleChoiceOptionButton) : au clic, l'événement
  EventFmxSetTacticTeamInstruction (« 6vvH ») avec la tactique et {n° de consigne, place de l'option} ; allumé quand
  tactic.SelectedTeamInstructionOption (de la consigne en cours) vaut le code de son option ; grisé si FM déclare
  l'option incompatible (tactic.SelectedTeamInstructionOptionConflicts) ;
- l'enveloppe qui dit « quelle consigne » : celle de la fenêtre Progression de FM (TacticProgressThroughOptionListBlock_4x7,
  5 boutons posés à la main, places const.zero à const.four) : ID = 21 (Rythme), TacticTeamInstruction =
  data.TacticTeamInstruction, teaminstructionid = TacticTeamInstruction.UniqueId ;
- les textes : ceux des cartes de FM (TeamInstructionTileTemplate_2x2) : le titre = TacticTeamInstruction.Name, le nom
  d'une option = data.TacticTeamInstructionOption.Name avec la variable id = code de l'option (posée par un
  BindingSetter, copié de TacticSupportingRunsOptionListBlock_4x7). Donc les noms du jeu, dans la langue du joueur.
Codes des 5 options de Rythme (ui-staticdataentries, m_optionID, dans l'ordre du jeu) : voir OPTIONS.

v4 (12/10, Kinito : on garde les cartes de FM à un clic ; « à l'ouverture de l'onglet j'aimerais arriver sur Terrain ») :
le bouton « Cartes / Terrain », en haut à droite du bloc. Recopié des cartes de chaleur du match (HeatMapsMatch_Block :
« Combiné / Avec le ballon / Sans le ballon ») :
- une variable entière, déclarée par un composant du bloc (BindingVariablesComponent, comme « possessionmode »),
  qui vaut VUE_DEPART à chaque ouverture de l'onglet ;
- deux boutons segmentés de FM (celui du début et celui de la fin : SIStyleSetter qui allume / éteint, SIButton qui
  copie une constante dans la variable, au format de FM à l'octet près) ;
- un interrupteur de FM (BindableSwitchElement, recopié de #possession-text-switch de ce bloc) autour de la zone des
  cartes : rang 0 = les cartes de FM (#Body, déplacé dedans, remis à sa place au retrait), rang 1 = notre terrain
  (pour l'instant : la rangée « Rythme ») ;
- textes : les mots de Kinito, « Cartes » et « Terrain », en texte fixe (langue du skin, choix 106). Essayé en jeu le
  12/10 avec des textes de FM : le n° 13422 (« Cards », bascule de la liste des recommandations de recrutement)
  s'affiche « Rapports » en français : faux ici. Le n° 8412 (« Pitch ») donnait bien « Terrain ».

Touché : TacticalPlannerTeamInstructionsBlock (bundle gameworldvisualtreeassetpreload), en tête de SIScrollView #Body,
avant la grille de cartes (#TeamInstructionTiles, pas touchée). Ce bloc n'est utilisé que par l'onglet Consignes
d'équipe (tactique, avant-match, match) ; aucun script d'Alex ni d'autre ajout Kinito ne le touche (vérifié le
12/10). Le bloc reçoit « Tactic » et les modèles de FM qu'il contient attendent « tactic » : la casse ne compte pas
(les cartes de FM, dans ce même bloc, le prouvent).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_consignes_essai.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_consignes_essai.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_consignes_essai.py etat
"""
import bisect
import copy
import json
import os
import struct
import sys

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
import langue  # noqa: E402  (textes fixes en français ou en anglais, choix 106)
import arbre as sm  # noqa: E402  (styles intégrés : numéros des propriétés)
import chemin_jeu  # noqa: E402  (dossier des bundles du jeu : données des consignes)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, decode_args, encode_args  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
CONSIGNE = 21   # Rythme (Tempo) : n° de la consigne (teaminstructionid)
OPTIONS = [     # (place envoyée au moteur, écrite comme FM ; code de l'option ; nom anglais, pour lire le script)
    ("const.zero", 1498756423, "Much Lower"),
    ("const.one", 1311996258, "Lower"),
    ("const.Two", 1496610426, "Standard"),
    ("const.three", 1345339954, "Higher"),
    ("const.four", 543778113, "Much Higher"),
]
VUE_DEPART = 1   # vue à l'ouverture de l'onglet : 0 = cartes de FM, 1 = terrain (Kinito : « arriver sur Terrain »)
TEXTES_VUES = [langue.texte("Cartes", "Cards"), langue.texte("Terrain", "Pitch")]   # les mots de Kinito
# v6 : terrain « Relance » de la maquette v23 (chantier-consignes\maquettes\maquette-3terrains-v23.html)
ZONES_GB = {   # Relances GB (16) : place de l'option -> zones [x, y, largeur, hauteur] en % du terrain (maquette v23)
    1: [(28, 58, 44, 27)], 2: [(2, 58, 22, 27), (76, 58, 22, 27)], 3: [(2, 28, 22, 27), (76, 28, 22, 27)],
    4: [(28, 28, 44, 27)], 5: [(2, 14, 96, 11)], 6: [(2, 1, 96, 11)],
    0: [(2, 87.5, 34, 10.5)]}   # v22 : « Équilibrées » (Kinito) : aligné à gauche sur les cases du dessus, jusqu'au but
#                                 (s'arrête avant la surface de but, 37 %), aussi haut que les rangées du haut (v6 à v21 :
#                                 petite pastille en bas à gauche)
BASCULES = {   # consigne : (places montrées dans l'ordre de la maquette, place par défaut) : cases à bascule
    20: ((0, 2), 1), 29: ((0, 2), 1), 17: ((0, 2), 1), 24: ((0, 2), 1), 18: ((0, 2), 1), 27: ((0, 2), 1), 19: ((0, 2), 1),
    3: ((0, 2), 1),   # Transition offensive : 0 Rester en place, 2 Contre-attaque (vu en jeu ; les noms des icônes
    #                   de FM, « press » pour la place 0, trompent : v8 les avait suivis et inversait les cases)
    5: ((0, 2), 1), 15: ((0, 2), 1),
    12: ((2, 0), 1),   # En taclant : « Engagez-vous plus » (2) avant « Ne vous jetez pas » (0), demandé par Kinito (v26)
    11: ((2, 0), 1)}   # Transition défensive : contre-pressing (2) au-dessus de regroupement (0), demandé par Kinito
COULOIRS = [(38, 62), (30, 70), (22, 78), (14, 86), (6, 94)]   # Largeur du jeu offensif : couloirs en % (maquette)
CRANS = {21, 1, 7}   # tuiles en crans : Rythme, Caract. direct des passes, Perdre du temps
TUILES = [(21, 3, 5), (1, 7, 6)]   # les deux rangées de tuiles du bas (maquette v23)
CONSIGNES_AVEC = {16, 17, 20, 29, 4, 24, 28, 30, 31, 18, 19, 26, 27, 1, 3, 5, 6, 7, 21}
CONSIGNES_SANS = {8, 9, 10, 11, 12, 15, 22, 23, 25}
TITRES_SANS = [langue.texte("Hauteur & bloc défensif", "Height & defensive block"),   # les mots de Kinito (maquette)
               langue.texte("Intensité & transitions", "Intensity & transitions"),
               langue.texte("Duels & zones d'intervention", "Duels & areas of engagement")]
Y_PRESSING = [42.5, 35.0, 28.0]   # Hauteur du pressing (bloc bas, bloc médian, pressing haut), % du terrain (maquette
#                                 v23 ramenée à un terrain de 400 px : repères = le rond central)
Y_LIGNE = [89.0, 81.0, 73.0, 65.0, 57.5]   # Ligne défensive (beaucoup plus basse … beaucoup plus haute)
BANDES_PRESSING = [(38.75, 50.0), (31.5, 38.75), (20.0, 31.5)]   # bandes de clic de chaque cran (maquette : de
BANDES_LIGNE = [(85.0, 97.5), (77.0, 85.0), (69.0, 77.0), (61.25, 69.0), (50.0, 61.25)]   # mi-chemin en mi-chemin)
DEFAUTS = {1: 2, 21: 2, 4: 2, 7: 1, 3: 1, 5: 1, 6: 0, 29: 1, 17: 1, 16: 0, 24: 1, 30: 0, 28: 0, 31: 0, 20: 1, 19: 1,
           18: 1, 26: 0, 27: 1, 8: 1, 9: 2, 15: 1, 10: 2, 11: 1, 12: 1, 25: 1, 23: 0, 22: 1}   # option par défaut
#           (maquette v23 : quand une autre est choisie, les autres cases de la consigne sont estompées)
TEXTES_COURSES = {"ext": langue.texte("Extérieur", "Outside"), "int": langue.texte("Intérieur", "Inside")}   # mots
#           de Kinito (12/10) au-dessus des cases des dédoublements ; v24 : ceux-là si la langue du jeu ne se lit pas
COURSES_LANGUES = [   # v24 (Kinito : « il faut que ça suive la langue du jeu ») : (langue du jeu, (extérieur, intérieur)).
    # Noms des langues = valeurs du réglage natif current_language, lus dans game_plugin.dll (la table que FM compare
    # à « english » dans son bandeau du dernier jour du mercato) ; FM n'a ces deux mots dans aucune langue : ce sont
    # NOS traductions (ses termes, « Overlap / Underlap », n'existent que dans des phrases « Overlap - [option] »)
    ("english", ("Outside", "Inside")), ("english (us)", ("Outside", "Inside")),
    ("french", ("Extérieur", "Intérieur")), ("german", ("Außen", "Innen")), ("italian", ("Esterno", "Interno")),
    ("spanish", ("Exterior", "Interior")), ("spanish (latam)", ("Exterior", "Interior")),
    ("portuguese", ("Exterior", "Interior")), ("portuguese (bra)", ("Exterior", "Interior")),
    ("dutch", ("Buiten", "Binnen")), ("danish", ("Udvendig", "Indvendig")), ("norwegian", ("Utvendig", "Innvendig")),
    ("swedish", ("Utsida", "Insida")), ("polish", ("Zewnątrz", "Wewnątrz")), ("czech", ("Vně", "Uvnitř")),
    ("russian", ("Снаружи", "Внутри")), ("turkish", ("Dış", "İç")), ("greek", ("Εξωτερικά", "Εσωτερικά")),
    ("indonesian", ("Luar", "Dalam")), ("japanese", ("外側", "内側")), ("korean", ("바깥쪽", "안쪽")),
    ("chinese", ("外侧", "内侧")), ("chinese (traditional)", ("外側", "內側")), ("thai", ("ด้านนอก", "ด้านใน")),
    ("arabic", ("خارجي", "داخلي"))]
VUES_LANGUES = [   # v25 : « Cartes / Terrain » dans la langue du jeu (Kinito, 12/10) ; NOS traductions (des mots de
    # Kinito : FM n'a pas ce bouton) ; langue illisible : TEXTES_VUES (langue du skin)
    ("english", ("Cards", "Pitch")), ("english (us)", ("Cards", "Pitch")), ("french", ("Cartes", "Terrain")),
    ("german", ("Karten", "Spielfeld")), ("italian", ("Schede", "Campo")), ("spanish", ("Fichas", "Campo")),
    ("spanish (latam)", ("Fichas", "Cancha")), ("portuguese", ("Cartas", "Campo")),
    ("portuguese (bra)", ("Cartas", "Campo")), ("dutch", ("Kaarten", "Veld")), ("danish", ("Kort", "Bane")),
    ("norwegian", ("Kort", "Bane")), ("swedish", ("Kort", "Plan")), ("polish", ("Karty", "Boisko")),
    ("czech", ("Karty", "Hřiště")), ("russian", ("Карточки", "Поле")), ("turkish", ("Kartlar", "Saha")),
    ("greek", ("Κάρτες", "Γήπεδο")), ("indonesian", ("Kartu", "Lapangan")), ("japanese", ("カード", "ピッチ")),
    ("korean", ("카드", "피치")), ("chinese", ("卡片", "球场")), ("chinese (traditional)", ("卡片", "球場")),
    ("thai", ("การ์ด", "สนาม")), ("arabic", ("بطاقات", "الملعب"))]
TITRES_SANS_LANGUES = [   # v25 : les trois titres « sans le ballon » (mots de Kinito) dans la langue du jeu ; NOS
    # traductions ; langue illisible : TITRES_SANS (langue du skin)
    ("english", ("Height & defensive block", "Intensity & transitions", "Duels & areas of engagement")),
    ("english (us)", ("Height & defensive block", "Intensity & transitions", "Duels & areas of engagement")),
    ("french", ("Hauteur & bloc défensif", "Intensité & transitions", "Duels & zones d'intervention")),
    ("german", ("Höhe & Abwehrblock", "Intensität & Umschaltspiel", "Zweikämpfe & Eingriffszonen")),
    ("italian", ("Altezza & blocco difensivo", "Intensità & transizioni", "Duelli & zone d'intervento")),
    ("spanish", ("Altura & bloque defensivo", "Intensidad & transiciones", "Duelos & zonas de intervención")),
    ("spanish (latam)", ("Altura & bloque defensivo", "Intensidad & transiciones", "Duelos & zonas de intervención")),
    ("portuguese", ("Altura & bloco defensivo", "Intensidade & transições", "Duelos & zonas de intervenção")),
    ("portuguese (bra)", ("Altura & bloco defensivo", "Intensidade & transições", "Duelos & zonas de intervenção")),
    ("dutch", ("Hoogte & verdedigingsblok", "Intensiteit & omschakeling", "Duels & interventiezones")),
    ("danish", ("Højde & forsvarsblok", "Intensitet & omstillinger", "Dueller & indgrebszoner")),
    ("norwegian", ("Høyde & forsvarsblokk", "Intensitet & overganger", "Dueller & inngrepssoner")),
    ("swedish", ("Höjd & försvarsblock", "Intensitet & omställningar", "Dueller & ingreppszoner")),
    ("polish", ("Wysokość & blok obronny", "Intensywność & przejścia", "Pojedynki & strefy interwencji")),
    ("czech", ("Výška & obranný blok", "Intenzita & přechody", "Souboje & zóny zákroků")),
    ("russian", ("Высота и оборонительный блок", "Интенсивность и переходы", "Единоборства и зоны отбора")),
    ("turkish", ("Yükseklik & savunma bloğu", "Yoğunluk & geçişler", "İkili mücadeleler & müdahale bölgeleri")),
    ("greek", ("Ύψος & αμυντικό μπλοκ", "Ένταση & μεταβάσεις", "Μονομαχίες & ζώνες επέμβασης")),
    ("indonesian", ("Ketinggian & blok bertahan", "Intensitas & transisi", "Duel & zona intervensi")),
    ("japanese", ("高さと守備ブロック", "強度とトランジション", "デュエルと介入ゾーン")),
    ("korean", ("높이와 수비 블록", "강도와 전환", "경합과 개입 지역")),
    ("chinese", ("高度与防守阵型", "强度与攻防转换", "对抗与干预区域")),
    ("chinese (traditional)", ("高度與防守陣型", "強度與攻防轉換", "對抗與干預區域")),
    ("thai", ("ความสูงและบล็อกรับ", "ความเข้มข้นและการเปลี่ยนจังหวะ", "การดวลและโซนเข้าปะทะ")),
    ("arabic", ("الارتفاع والكتلة الدفاعية", "الشدة والتحولات", "الالتحامات ومناطق التدخل"))]
SOURCE_LANGUE = "tdd-messages-banner"   # v24 : le bandeau du dernier jour du mercato : un ComponentElement déclare
#           name = current_language et relie languagesetting à app.NativeSettings ; un BindableSwitchElement compare
#           languagesetting.PropertyValue à « english » (fonction de FM 7980ef35)
HAUT_TUILE = 46   # hauteur des boutons des tuiles du bas (v15 : icônes seules, toutes de la même hauteur)
HAUT_BANDE = 34   # v19 : hauteur des boutons des bandes (réception des passes, gardien, largeur, style de centres)
REMPLI = 0.86     # v19 : part de sa case que prend le dessin d'une icône (en largeur ou en hauteur : la plus juste)
TEXTE_ZONES = 11  # v19 : taille du texte des zones des relances du gardien, en px (en « Plus grand », « latéraux »
#                   passait à la ligne)
TITRE_BANDE = 11  # v23 : titres des trois bandes du bas des terrains (gardien, largeur, style de centres), en px et
#                   sur une ligne, dans toutes les langues (Kinito : « Relances GB (vitesse) » sur une ligne ; en anglais,
#                   « GK DISTRIBUTION (SPEED) » passait à la ligne). Calculé avec la police du jeu (ABC Social Condensed) :
#                   la demi-bande fait ~118 px, « GK DISTRIBUTION (SPEED) » 10,1 em, « RELANCES GB (VITESSE) » 9,3 em
PLAFOND_ICONE = 1.5   # v23 : agrandissement maximal des icônes des tuiles du bas « sans le ballon » (au-delà, l'image de
#                   FM devient floue)
REMPLI_PROGRESSION = 0.95   # v23 : les schémas de la progression prennent plus de leur case (Kinito : moins de marge)
TEXTE_PROGRESSION = 0.30    # v23 : part du bas de ces cases pour le nom (Gauche / Axiale / Droite), centré dedans,
#                   juste sous le schéma
BADGE_LARGEURS = {120: 174, 85: 130, 100: 149, 110: 161}   # v23 : largeur des deux badges du terrain des lignes, en px,
#                   selon la taille du texte choisie dans FM (settings.TextScaling : 85 Petit, 100 Normal, 110 Grand,
#                   120 Plus grand ; la première est celle qui s'affiche si la valeur ne se lit pas). Celle du plus long
#                   texte (« HAUTEUR DU PRESSING ») : mesuré sur la capture de Kinito du 12/10 en texte PETIT (contrôlé
#                   avec la police du jeu : 107,6 px), × taille / 0,85, + 16 de marges + 2 de bord + 4 de jeu. Les textes
#                   anglais sont plus courts (police du jeu). v21 : une seule largeur en % (48), juste en Petit seulement
# =====================================================================================================

VERSION = f"26{langue.SUFFIXE}"   # v1, v2 : le jeu plantait à l'ouverture de l'onglet (règles de style non recopiées) ;
#               v3 : recopiées ; v4 : bouton « Cartes / Terrain » (textes de FM : « Rapports » au lieu de « Cartes ») ;
#               v5 : textes fixes ; v6 : terrain « Relance » (colonnes Avancée et 30 derniers mètres vides) ;
#               v7 : boutons de FM recopiés à plat (v6 : mots coupés dans les zones étroites), icônes plus grandes ;
#               v8 : terrains Avancée et 30 derniers mètres, tuiles du bas (Rythme devient une tuile) ;
#               v9 : « Centrer de loin » écrit à la verticale, bande du gardien en deux lignes, centres en 2 × 2,
#                    Transition offensive dans l'ordre de la maquette ; v10 : en texte « Plus grand », tout
#                    s'écrasait : la vue défile (copie de #Body), terrains de 400 px au moins, zones en label-sm ;
#               v11 : « Sans le ballon » (maquette v23) ; terrains « avec » de 455 px (texte Petit : page remplie) ;
#               v12 : liseré vert sur l'option choisie (sur l'herbe, l'allumage de FM se voyait mal), « Empêcher de
#                     centrer » à la verticale ; v13 : « sans » de 650 px (page remplie en texte Petit) ;
#               v14 : marges du bouton de FM annulées (~6,5 px de chaque côté, mesuré sur la capture de Kinito :
#                     c'est ce qui coupait les mots) ; bande du gardien et Style de centres sur une ligne (maquette) ;
#               v15 (demandes de Kinito, 12/10) : icônes seules + nom en infobulle (bandes du bas, tuiles), cases
#                     estompées (« contraire »), icônes de terrain en portrait, terrain des lignes comme la maquette ;
#               v16 : infobulle dans le bouton même (v15 : rien ne s'affichait) ; Réception des passes en icônes ;
#                     crans sans le nom dessous ; dédoublements : étiquettes, case contraire grisée, clic = échange ;
#               v17 : couleurs de la maquette (cases, tuiles ; mesurées sur ses captures), police étroite de FM
#                     (thematic) pour les titres, badges des lignes réparés, sans le ballon : icônes seules + infobulles,
#                     colonne du milieu 3/5 - 2/5 ; v18 : dédoublements : plus de n° de consigne écrit en dur (v16 /
#                     v17 : vu en jeu, plus aucun clic ne marchait) : la vraie valeur de FM, recopiée ;
#               v19 (demandes de Kinito, 12/10) : plus de défilement, tout tient dans le bloc ; icônes dessinées en %
#                     de leur case (elles suivent la taille du texte choisie dans FM), noms en infobulle (piège, centres,
#                     surface, tirs, dribbles, stratégie) ; badges des lignes de même taille ; flèches du piège ;
#                     un seul « Intérieur » ; fond des tuiles en dégradé (maquette) ;
#               v20 : badges des lignes : vus en jeu sur toute la largeur du terrain ; la rangée invisible qui les mesure
#                     n'a plus d'enveloppe de consigne ni de « nowrap » (voir ligne_consigne) ; v21 : toujours toute la
#                     largeur en jeu : plus de rangée invisible, une largeur minimale commune (BADGE_LARGEUR) ;
#               v22 (Kinito, 12/10) : dédoublements en miroir (FM dessine leur flanc gauche EN BAS de l'image, la
#                     progression EN HAUT) ; flèches du pressing sur centres ; tuiles du bas « sans le ballon » à la
#                     hauteur de « Regroupement » ; « Équilibrées » des relances du gardien en grande case ;
#               v23 (Kinito, 12/10) : badges des lignes à la taille du texte de FM (settings.TextScaling) ; « sans le
#                     ballon » en grille de 2 rangées ; titres des bandes du bas sur une ligne dans toutes les langues ;
#                     plus de « Gauche / Droite » sous les dédoublements ; progression : schémas plus grands, nom centré
#                     dessous ; v24 : « Extérieur / Intérieur » dans la langue du jeu (Kinito) ; v25 : « Cartes /
#                     Terrain » et les titres « sans le ballon » aussi ; v26 : « Engagez-vous plus » avant « Ne vous
#                     jetez pas » ; 26.14 (kinito_consignes_essai_b, autre disposition) l'exclut et réciproquement
PLACES = ["const.Zero", "const.One", "const.Two", "const.Three", "const.Four", "const.Five", "const.Six"]   # écrites
#               comme FM le fait le plus souvent (outils-analyse\consts.py : const.Five 32 fois, const.Six 28 fois)
RATIO_ICONE = 124 / 72   # toutes les icônes d'options de FM : 124 × 72 px (feuille FMImages_1x, mesuré le 12/10)
SOURCE_BULLE = "RoleLabelwIcon"   # v15 : infobulle de FM (celle de 26.4)
SOURCE_PHASES = "ProjectedPositionsTemplate"   # noms des phases de FM (« Relance »…) : SIText #GoalkeeperPhase…
PHASES = [("GoalkeeperPhase", "goalkeeperphase", 2), ("MidfieldPhase", "midfieldphase", 1),
          ("ForwardPhase", "forwardphase", 0)]   # SIText de FM, variable lue, valeur (comme dans ProjectedPositionsTemplate)
COUL = {"herbe1": (0x14 / 255, 0x53 / 255, 0x3f / 255, 1.0), "herbe2": (0x11 / 255, 0x4a / 255, 0x39 / 255, 1.0),
        "ligne": (1.0, 1.0, 1.0, 0.30), "cadre": (0x2f / 255, 0x6e / 255, 0x5d / 255, 1.0),
        "bandeau": (0x07 / 255, 0x1a / 255, 0x15 / 255, 0.80), "filet": (1.0, 1.0, 1.0, 0.18), "blanc": (1.0, 1.0, 1.0, 1.0),
        "gardien": (0x0b / 255, 0x2a / 255, 0x22 / 255, 1.0), "case": (0x19 / 255, 0x34 / 255, 0x2f / 255, 1.0),
        "pressing": (0x3d / 255, 0xdc / 255, 0x84 / 255, 1.0),
        "defense": (0x9f / 255, 0xe8 / 255, 1.0, 1.0), "choisi": (0x3f / 255, 0xe0 / 255, 0xb4 / 255, 1.0),
        "contraire": (0x1b / 255, 0x22 / 255, 0x30 / 255, 0.62), "contraire-bord": (0xb9 / 255, 0xc4 / 255, 0xd6 / 255, 0.26),
        "voile-pressing": (0x3d / 255, 0xdc / 255, 0x84 / 255, 0.16), "voile-defense": (0x02 / 255, 0x0a / 255, 0x08 / 255, 0.32),
        "badge": (0x0b / 255, 0x2a / 255, 0x22 / 255, 0.92),
        # v17 : cases comme la maquette (mesuré sur ses captures du 12/10 : non choisie (12,31,27) sur la tuile
        # (25,52,47), soit #04110d à 60 % ; estompée (25,39,47) ; choisie : liseré #3fe0b4 + halo vert à 30 %)
        "case-fond": (0x04 / 255, 0x11 / 255, 0x0d / 255, 0.60), "case-bord": (1.0, 1.0, 1.0, 0.16),
        "choisi-fond": (0x0b / 255, 0x3a / 255, 0x2c / 255, 0.45), "anneau": (0x3d / 255, 0xdc / 255, 0x84 / 255, 0.30),
        "tuile-bord": (0x2c / 255, 0x5b / 255, 0x52 / 255, 1.0)}   # maquette v23
for _k, _v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "right": (131103, 3),
               "bottom": (131080, 3), "width": (131105, 3), "height": (131087, 3), "flex-direction": (131083, 7),
               "justify-content": (131088, 7), "align-items": (131073, 7), "align-self": (131074, 7),
               "margin-top": (131093, 3), "margin-bottom": (131090, 3), "margin-left": (131091, 3),
               "margin-right": (131092, 3), "padding-top": (131101, 3), "padding-bottom": (131098, 3),
               "padding-left": (131099, 3), "padding-right": (131100, 3), "border-top-color": (458763, 4),
               "border-bottom-color": (458758, 4), "border-left-color": (458761, 4), "border-right-color": (458762, 4),
               "border-top-left-radius": (458764, 3), "border-top-right-radius": (458765, 3),
               "border-bottom-left-radius": (458759, 3), "border-bottom-right-radius": (458760, 3),
               "-unity-text-align": (65546, 7), "white-space": (65552, 7), "flex-wrap": (131086, 7),
               "rotate": (327680, 3), "color": (65536, 4),
               # v19 : taille du texte, opacité, background-size (mot-clé 8 = contain, comme FM 6 fois dans SIStyles)
               "font-size": (65537, 3), "opacity": (458767, 2), "background-size": (458757, 1),
               "max-height": (131094, 3)}.items():   # v23
    sm.PROPRIETES.setdefault(_k, _v)   # StylePropertyId d'Unity 6, lus dans UnityEngine.UIElementsModule (12/10)
SOURCE_BASCULE = "HeatMapsMatch_Block"   # variable, boutons segmentés (cartes de chaleur du match)
VARIABLE = "kinitovue"
BLOC = "TacticalPlannerTeamInstructionsBlock"
SOURCE = "TacticProgressThroughOptionListBlock_4x7"     # enveloppe + 5 boutons de consigne de FM
SOURCE_TEXTE = "TacticSupportingRunsOptionListBlock_4x7"   # un BindingSetter élément (variable id du texte)
MODELE_BOUTON = "TacticTeamInstructionMultipleChoiceOptionButton"
CHEMIN_TITRE = "TacticTeamInstruction.Name"
CHEMIN_OPTION = "data.TacticTeamInstructionOption.Name"
PREFIXE = "UIPickerKinito-consignes-essai"
NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_consignes_essai.actif")
RACINE = f"{PREFIXE}-v"   # v26 : début du nom de NOTRE racine, suivi du n° de version (26.14 : « -b-v ») ; retirer ne
#                   touche qu'à la sienne (« -vue », l'interrupteur, n'est pas une racine : un chiffre doit suivre)
AUTRE_MARQUEUR = "kinito_consignes_essai_b.actif"   # v26 : 26.13 et 26.14 s'excluent : appliquer l'une efface la
#                   marque de l'autre (dans le dossier de SA marque : celui des copies pendant un essai)


def est_racine(nom):
    """v26 : la racine de CETTE version de l'essai (nom = RACINE + n° de version)"""
    return nom.startswith(RACINE) and nom[len(RACINE):len(RACINE) + 1].isdigit()


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def surcharges(t, r):
    return [t.refs[ov["m_SerializedData"]["rid"]]["data"] for ov in t.elem(r).get("m_SerializedDataOverride") or []]


def recaler_parent(t, r):
    """clone() ne refait que m_Parent : l'identifiant du parent aussi, s'il existe"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def declarer_modele(t, s, alias):
    """déclare le modèle inclus <alias> (m_Usings de s), à sa place dans l'ordre des noms (comme FM)"""
    u = next((u for u in s.tt.get("m_Usings") or [] if u.get("alias") == alias), None)
    if u is None:
        return False
    usings = t.tt.setdefault("m_Usings", [])
    if not any(x.get("alias") == alias for x in usings):
        cles = [x.get("alias") or "" for x in usings]
        usings.insert(bisect.bisect_left(cles, alias) if cles == sorted(cles) else len(usings), copy.deepcopy(u))
    return True


def fonction_vide(f):
    f["m_target"] = {"m_guid": ""}
    f["m_inputs"] = {"m_variable": {"m_argumentBytes": []}}
    f["m_outputs"] = {"m_variable": {"m_argumentBytes": []}}


def texte_lie(t, r, chemin, repere):
    """le SIText r affiche la valeur du chemin <chemin> (liaison directe, comme les cartes de FM)"""
    sd = t.sd(r)
    tb = sd["TextBinding"]
    tb["m_kind"] = 1
    tb["m_direct"]["Path"]["m_path"] = chemin   # seulement la valeur : la structure de FM garde tous ses champs
    fonction_vide(tb["m_visualFunction"])
    sd["TextBinding_UxmlAttributeFlags"] = 1
    sd["DebugDisplay"] = repere


def est_bouton(t, r):
    return t.elem(r).get("m_TemplateAlias") == MODELE_BOUTON


def options_consignes(numeros):
    """{n° de consigne : [(code, classe d'icône)]} dans l'ordre du jeu (ui-staticdataentries, comme
    outils-analyse\\codes_options.py) : la place d'une option = son rang dans cette liste"""
    import UnityPy
    env = UnityPy.load(os.path.join(chemin_jeu.AA, "ui-staticdataentries_assets_all.bundle"))
    out = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            d = o.read_typetree()
        except Exception:
            continue
        if "m_instructionOptionEntries" in d and d.get("m_instructionID") in numeros:
            out[d["m_instructionID"]] = [(e["m_optionID"], e["m_imageUSS"]) for e in d["m_instructionOptionEntries"]]
    return out


def dessins_icones(classes):
    """v19 : {classe d'icône : (largeur, hauteur du dessin, décalage x, y de son centre, largeur, hauteur de la toile)}
    en px, lus dans le jeu : la règle de la classe (feuille FMImages_1x) pointe vers un sprite dont m_Rect est la toile
    (124 × 72 presque toujours) et m_RD.textureRect le dessin (souvent bien plus petit : 46 × 66 pour la transition
    défensive). Décalage : textureRectOffset (compté depuis le bas, comme Unity)"""
    import UnityPy
    styles = UnityPy.load(os.path.join(chemin_jeu.AA, "ui-styles_assets_1x.bundle"))
    refs = {}
    for o in styles.objects:
        if o.type.name != "MonoBehaviour" or b"tactic_icons" not in bytes(o.get_raw_data()):
            continue
        tt = o.read_typetree()
        for rule in tt.get("m_Rules") or []:
            for cs in rule.get("m_ComplexSelectors") or []:
                for sel in cs["m_Selectors"]:
                    nom = "".join(pt["m_Value"] for pt in sel["m_Parts"])
                    if nom in classes:
                        for pr in rule["m_Properties"]:
                            if pr["m_Id"] == 458753:
                                refs[nom] = tt["assets"][pr["m_Values"][0]["valueIndex"]]["m_PathID"]
    icones = UnityPy.load(os.path.join(chemin_jeu.AA, "ui-icons_assets_1x.bundle"),
                          os.path.join(chemin_jeu.AA, "ui-iconspriteatlases_assets_1x.bundle"))
    par_id = {o.path_id: o for o in icones.objects}
    out = {}
    for nom, pid in refs.items():
        if pid not in par_id:
            continue
        tt = par_id[pid].read_typetree()
        r, tr, off = tt["m_Rect"], tt["m_RD"]["textureRect"], tt["m_RD"]["textureRectOffset"]
        out[nom] = (tr["width"], tr["height"], off["x"] + tr["width"] / 2 - r["width"] / 2,
                    off["y"] + tr["height"] / 2 - r["height"] / 2, r["width"], r["height"])
    return out


def px(v):
    return {"unit": 1, "value": float(v)}


def pc(v):
    return {"unit": 2, "value": float(v)}


def cadre_css(largeur, couleur, rayon=None):
    css = {f"border-{c}-width": largeur for c in ("top", "bottom", "left", "right")}
    css.update({f"border-{c}-color": couleur for c in ("top", "bottom", "left", "right")})
    if rayon is not None:
        css.update({f"border-{c}-radius": rayon for c in ("top-left", "top-right", "bottom-left", "bottom-right")})
    return css


class Fab:
    """fabrique des éléments du terrain : boîtes (VisualElement), enveloppes de consigne, boutons de FM, cases à bascule"""

    def __init__(self, t, src):
        self.t, self.src = t, src
        self.proto = first(t, lambda r: t.name(r) == "team-instruction-header")   # VisualElement simple de FM
        self.inter = first(t, lambda r: typ(t, r) == "BindableSwitchElement" and t.name(r) == "possession-text-switch")
        self.defile = first(t, lambda r: typ(t, r) == "SIScrollView" and t.name(r) == "Body")   # zone des cartes
        self.n = 0

    def _nom(self, r, nom):
        sd = self.t.sd(r)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}-{nom}", 1

    def boite(self, parent, nom, css=None, classes=(), index=None):
        t = self.t
        r = t.clone_shallow(self.proto, parent, index)
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = list(classes), -1
        self._nom(r, nom)
        if css:
            t.styles.style(t, r, css)
        return r

    def interrupteur(self, parent, nom, chemin, css=None, index=None):
        """BindableSwitchElement de FM (recopié de #possession-text-switch) : montre l'enfant n° <valeur de chemin>"""
        t = self.t
        r = t.clone_shallow(self.inter, parent, index)
        self._nom(r, nom)
        t.sd(r)["Binding"]["m_direct"]["Path"]["m_path"] = chemin
        t.elem(r)["m_Classes"] = []
        if css:
            t.styles.style(t, r, css)
        return r

    def enveloppe(self, parent, n, nom, css=None, traverse=False):
        """le ComponentElement de la fenêtre Progression de FM, vidé de ses boutons : déclare la consigne n° n.
        traverse : calque posé sur tout un terrain, qui laisse passer les clics vers ce qui est dessous (pickingMode
        Ignore), sinon il couvrirait les cases des autres calques"""
        t, src = self.t, self.src
        env = t.clone(src.enveloppe, parent, src=src.tp)
        recaler_parent(t, env)
        t.styles.copy_from(src.tp.styles, t, env)
        ids = 0
        for k in list(t.children(env)):
            e = t.elem(k)
            if e.get("m_FullTypeName", "").endswith("Component"):
                if e.get("m_FullTypeName") == "SI.Bindable.BindingSetterComponent":
                    for p in e.get("m_Properties") or []:
                        if p.get("name") == "value-vars":
                            p["value"] = f"{{ID}}{{Int|{n}|}}"
                            ids += 1
            else:
                t.remove(k)
        for c in t.sd(env).get("m_components") or []:
            for v in ((t.refs.get(c["rid"]) or {}).get("data") or {}).get("ValueVariables") or []:
                if v.get("m_name") == "ID":
                    v["m_scopeValue"]["m_serializedData"] = f"Int|{n}|"
                    ids += 1
        if ids != 2:
            raise ValueError(f"enveloppe de la consigne {n} : n° écrit à {ids} endroit(s) sur 2")
        self._nom(env, nom)
        t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
        if traverse:
            self.traverse(env)
            css = {"position": "absolute", "left": 0, "top": 0, "width": pc(100), "height": pc(100), **(css or {})}
        if css:
            t.styles.style(t, env, css)
        return env

    def traverse(self, r):
        sd = self.t.sd(r)
        sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1   # PickingMode.Ignore

    def titre(self, env, nom, css=None, classe="thematic-xs"):
        """titre de la consigne de l'enveloppe (son nom dans les données du jeu), petit, centré, en capitales"""
        t, src = self.t, self.src
        r = t.clone(src.titre, env, src=src.tp)
        t.styles.copy_from(src.tp.styles, t, r)
        texte_lie(t, r, CHEMIN_TITRE, nom)
        self._nom(r, f"{nom}-titre")
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [classe, "global-text-secondary"], -1
        sd = t.sd(r)
        if "TextCase" in sd:
            sd["TextCase"] = 1
            sd["TextCase_UxmlAttributeFlags"] = 1
        t.styles.style(t, r, {"-unity-text-align": "middle-center", "margin-bottom": 4, "white-space": "normal",
                              **(css or {})})
        if css and css.get("position") == "absolute":
            self.traverse(r)
        return r

    def texte_fixe(self, parent, nom, texte, css=None, classe="label-md"):
        """un texte fixe (les mots de Kinito), même style que les titres de consignes"""
        t, src = self.t, self.src
        r = t.clone(src.titre, parent, src=src.tp)
        t.styles.copy_from(src.tp.styles, t, r)
        self._nom(r, nom)
        sd = t.sd(r)
        sd.update(text=texte, text_UxmlAttributeFlags=1, DebugDisplay=texte)   # texte fixe (recette de 26.4)
        sd["TextBinding"]["m_kind"] = 0
        sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        fonction_vide(sd["TextBinding"]["m_visualFunction"])
        if "TextCase" in sd:
            sd["TextCase"], sd["TextCase_UxmlAttributeFlags"] = 1, 1
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [classe, "global-text-primary"], -1
        if css:
            t.styles.style(t, r, css)
        return r

    def nom_option(self, parent, n, place, petit=True, css=None):
        """le nom d'une option (données du jeu : variable id = son code), dans un BindingSetter (un seul enfant posé)"""
        t, src = self.t, self.src
        code = src.options[n][place][0]
        self.n += 1
        var = t.clone(src.setter, parent, src=src.ts)
        recaler_parent(t, var)
        for k in list(t.children(var)):
            t.remove(k)
        t.styles.copy_from(src.ts.styles, t, var)
        vs = t.sd(var)
        vs["name"], vs["name_UxmlAttributeFlags"] = f"{PREFIXE}-o{self.n}-id", 1
        v0 = copy.deepcopy(vs["ValueVariables"][0])
        v0["m_name"], v0["m_scopeValue"]["m_serializedData"] = "id", f"Int|{code}|"
        vs["ValueVariables"], vs["ValueVariables_UxmlAttributeFlags"] = [v0], 1
        t.elem(var)["m_Classes"] = []
        if css:
            t.styles.style(t, var, css)
        texte = t.clone(src.texte_option, var, src=src.tp)
        t.styles.copy_from(src.tp.styles, t, texte)
        texte_lie(t, texte, CHEMIN_OPTION, f"option {place}")
        t.elem(texte)["m_Classes"] = ["body-sm" if petit else "label-md", "global-text-primary"]
        t.styles.style(t, texte, {"-unity-text-align": "middle-center", "white-space": "normal"})
        return var, texte

    def option(self, parent, n, place, affiche=None, allume=None, icone=False, haut=0, css=None, petit=False,
               texte=True, ligne=False, vertical=False, classe=None, bulle=False, assombrir=False, portrait=0, nu=False,
               n_vue=None, cible=None, extra=None, force=False, estompe=False, echelle=None, part=(1.0, 1.0),
               tourne=False, taille_texte=None, miroir=False, plafond=None, texte_bas=None, rempli=None):
        """un bouton de consigne de FM (recopié à plat) : envoie la place <place> de la consigne <n> ; montre l'option
        <affiche> (par défaut : la même) de la consigne <n_vue> (par défaut : n) ; s'allume quand l'option choisie (de
        la consigne de son enveloppe) a le code <allume> (par défaut : celui de l'option montrée).
        Contenu : icône de FM (hauteur <haut> ; portrait : largeur <portrait>, tournée d'un quart de tour) et / ou nom
        (ligne : icône à gauche ; vertical : écrit de bas en haut). bulle : le nom en infobulle. assombrir : estompé
        quand une AUTRE option que celle par défaut est choisie (maquette : « contraire ») ; estompe : toujours estompé.
        nu : invisible (bandes de clic du terrain des lignes). v16 : cible = n° de consigne écrit en dur (bouton posé
        dans l'enveloppe d'une autre consigne) ; extra = (consigne, place) : un 2e réglage envoyé APRÈS le premier ;
        force = sans le grisé de FM (options incompatibles), pour les cases qui échangent deux consignes.
        v19 : une icône sans hauteur donnée (ni haut ni portrait) prend sa CASE : dessinée en % de la case, elle suit sa
        taille (texte Petit ou Plus grand) ; echelle = dessin de référence de la rangée (Fab.echelle : même taille pour
        toutes), part = part de la case qui compte (cases plus larges que leurs voisines), tourne = quart de tour
        (portrait) ; le contenu ne pousse plus la case : c'est la case qui décide. taille_texte : en px"""
        t, src = self.t, self.src
        opts = src.options[n]
        opts_vue = src.options[n if n_vue is None else n_vue]
        vue = place if affiche is None else affiche
        code = opts_vue[vue][0] if allume is None else allume
        self.n += 1
        k = self.n
        # v16 : le BindingSetter « id » (code de l'option montrée) ENVELOPPE le bouton : l'infobulle, posée directement
        # dans le SIButton comme celle de 26.4 (v15 : posée plus bas, elle ne recevait pas le survol), y lit le nom
        var = t.clone(src.setter, parent, src=src.ts)
        recaler_parent(t, var)
        for c in list(t.children(var)):
            t.remove(c)
        t.styles.copy_from(src.ts.styles, t, var)
        self._nom(var, f"o{k}")
        vs = t.sd(var)
        v0 = copy.deepcopy(vs["ValueVariables"][0])
        v0["m_name"], v0["m_scopeValue"]["m_serializedData"] = "id", f"Int|{opts_vue[vue][0]}|"
        vs["ValueVariables"], vs["ValueVariables_UxmlAttributeFlags"] = [v0], 1
        t.elem(var)["m_Classes"], t.elem(var)["m_RuleIndex"] = [], -1
        # v7 : le bouton de FM recopié à plat (son contenu, pas le modèle inclus) : marges internes réglables
        b = t.clone(src.racine_bouton, var, src=src.tb)
        t.styles.copy_from(src.tb.styles, t, b)
        t.elem(b)["m_Classes"] = []
        self._nom(b, f"o{k}-bouton")
        t.styles.style(t, b, {"flex-grow": 1})
        if not regler_plat(t, b, PLACES[place], code, cible=cible, extra=extra and (extra[0], PLACES[extra[1]])):
            raise ValueError(f"consigne {n} : bouton de FM à plat inattendu")
        if force:
            for r in t.walk(b):
                if typ(t, r) == "SIEnabled":
                    t.sd(r)["Binding"]["m_direct"]["Path"]["m_path"] = "const.False"   # inversé : toujours actif
        bouton = first(t, lambda r: typ(t, r) == "SIButton", b)
        v, h = (2, 3) if petit else (5, 6)
        # v14 : le bouton de FM se donne ~6,5 px de marge de chaque côté (mesuré sur la capture de Kinito du 12/10 :
        # « Courtes » 74 px de large, 17 px d'écart avec « Longues » au lieu de 4) ; annulées ici
        t.styles.style(t, bouton, {"padding-top": v, "padding-bottom": v, "padding-left": h, "padding-right": h,
                                   "margin-bottom": 0, "margin-top": 0, "margin-left": 0, "margin-right": 0,
                                   **({"background-color": (0.0, 0.0, 0.0, 0.0), "border-top-width": 0,
                                       "border-bottom-width": 0, "border-left-width": 0, "border-right-width": 0}
                                      if nu else   # v17 : la case de la maquette (FM : presque transparente)
                                      {"background-color": COUL["case-fond"], **cadre_css(1, COUL["case-bord"], 8)})})
        remplit = icone and not (haut or portrait)
        contenu = self.boite(bouton, f"o{k}-contenu", css=(
            {"position": "absolute", "left": 0, "top": 0, "width": pc(100), "height": pc(100), "flex-direction": "column"}
            if remplit else
            {"flex-grow": 1, "flex-direction": "row" if ligne else "column", "align-items": "center",
             "justify-content": "flex-start" if ligne else "center"}))
        self.traverse(contenu)
        marge = {"margin-right": 4} if ligne else {"margin-bottom": 2} if texte else {}
        porte = contenu   # où va le nom
        if remplit:   # v19 : la zone de l'icône prend toute la case (moins le nom, s'il est écrit dessous)
            # v23 : texte_bas = part du bas de la case pour le nom, centré dedans (progression) ; plafond = agrandissement
            # maximal (l'icône, centrée par la zone, ne grandit plus au-delà)
            zone = self.boite(contenu, f"o{k}-zone", css={"flex-grow": 1 - (texte_bas or 0), "flex-basis": 0,
                                                         **({"justify-content": "center", "align-items": "center"}
                                                            if plafond else {})})
            self.traverse(zone)
            self.icone_case(zone, f"o{k}-icone", opts_vue[vue][1], echelle, part, tourne, miroir, plafond, rempli)
            if texte and texte_bas:
                porte = self.boite(contenu, f"o{k}-nom", css={"flex-grow": texte_bas, "flex-basis": 0,
                                                             "justify-content": "center", "align-items": "center"})
                self.traverse(porte)
        elif icone and portrait:   # v15 : icône de terrain en portrait (attaque vers le haut) : un quart de tour (−90°)
            hp_ = round(portrait * RATIO_ICONE, 1)
            cadre_ic = self.boite(contenu, f"o{k}-icone", css={"width": portrait, "height": hp_, "flex-shrink": 0, **marge})
            self.traverse(cadre_ic)
            self.traverse(self.boite(cadre_ic, f"o{k}-icone-tournee", classes=[opts_vue[vue][1]],
                                     css={"position": "absolute", "left": pc(50), "top": pc(50), "width": hp_,
                                          "height": portrait, "margin-left": -hp_ / 2, "margin-top": -portrait / 2,
                                          "rotate": {"unit": 5, "value": -90.0}}))
        elif icone:
            self.traverse(self.boite(contenu, f"o{k}-icone", classes=[opts_vue[vue][1]],
                                     css={"width": round(haut * RATIO_ICONE, 1), "height": haut, "flex-shrink": 0,
                                          **marge}))
        if texte:
            txt = t.clone(src.texte_option, porte, src=src.tp)
            t.styles.copy_from(src.tp.styles, t, txt)
            texte_lie(t, txt, CHEMIN_OPTION, f"option {vue}")
            t.elem(txt)["m_Classes"] = [classe or ("body-sm" if petit else "label-md"), "global-text-primary"]
            t.styles.style(t, txt, {"-unity-text-align": "middle-left" if ligne else "middle-center",
                                    "white-space": "normal", **({"flex-grow": 1, "flex-shrink": 1} if ligne else {}),
                                    **({"font-size": taille_texte} if taille_texte else {})})
            if vertical:   # écrit de bas en haut, centré (rotation de −90°, comme l'étiquette d'axe de FM
                #            « match-momentum-chart-y-axis-label ») ; la case garde sa largeur
                sd = t.sd(txt)
                if "TextCase" in sd:
                    sd["TextCase"], sd["TextCase_UxmlAttributeFlags"] = 1, 1
                t.styles.style(t, txt, {"position": "absolute", "left": pc(50), "top": pc(50), "width": 220, "height": 24,
                                        "margin-left": -110, "margin-top": -12, "white-space": "nowrap",
                                        "rotate": {"unit": 5, "value": -90.0}})
            self.traverse(txt)
        if bulle:   # le nom de l'option en infobulle (infobulle de FM, celle de RoleLabelwIcon), dans le bouton même
            bu = t.clone(src.bulle, bouton, src=src.tu)
            t.styles.copy_from(src.tu.styles, t, bu)
            recaler_parent(t, bu)
            self._nom(bu, f"o{k}-bulle")
            texte_lie(t, t.children(bu)[0], CHEMIN_OPTION, f"option {vue}")
        if not nu:
            self.lisere(bouton, n, k, assombrir, estompe)
        if css:
            t.styles.style(t, var, css)
        return var

    def dessin(self, classe):
        """v19 : (largeur, hauteur du dessin, décalage x, y, largeur, hauteur de la toile) ; sans mesure : la toile"""
        return self.src.dessins.get(classe) or (124.0, 72.0, 0.0, 0.0, 124.0, 72.0)

    def echelle(self, n, places, *autres):
        """v19 : le dessin de référence d'une rangée d'icônes (la plus grande largeur et la plus grande hauteur des
        dessins) : toutes les icônes de la rangée à la même échelle (Kinito : « harmonise la taille des icônes par
        ligne »). autres = (consigne, places) de plus dans la même rangée"""
        dims = [self.dessin(self.src.options[m][p][1]) for m, ps in ((n, places), *autres) for p in ps]
        return max(d[0] for d in dims), max(d[1] for d in dims)

    def style_brut(self, r, props):
        """propriétés à plusieurs valeurs (background-position : mot + décalage, comme FM) : [(m_Id, [(type, valeur)])]"""
        t = self.t
        e = t.elem(r)
        old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
        ids = {i for i, _ in props}
        e["m_RuleIndex"] = t.styles.add_rule([x for x in old if x[0] not in ids] + [(i, "", v) for i, v in props])

    def icone_case(self, zone, nom, classe, ref, part, tourne, miroir=False, plafond=None, rempli=None):
        """v19 : l'icône de FM (classe = sa toile, 124 × 72) dessinée en % de sa zone, en mode « contain » : le DESSIN
        de référence (ref) prend REMPLI de la zone dans le sens le plus juste, quelle que soit sa taille. La boîte est la
        toile agrandie d'autant (largeur en % de la largeur, hauteur en % de la hauteur), centrée ; le léger décalage
        du dessin dans sa toile est rattrapé. tourne : quart de tour (−90°, l'attaque vers le haut, v15)"""
        dw, dh, cx, cy, rw, rh = self.dessin(classe)
        rdw, rdh = ref or (dw, dh)
        fx, fy = part[0] * (rempli or REMPLI), part[1] * (rempli or REMPLI)
        if tourne:   # tourné, la largeur du dessin devient sa hauteur
            w, h = fx * rw / rdh * 100, fy * rh / rdw * 100
            dx = dy = 0.0
        else:
            w, h = fx * rw / rdw * 100, fy * rh / rdh * 100
            dx, dy = -cx * fx / rdw * 100, cy * fy / rdh * 100
        css = {"position": "absolute", "left": pc((100 - w) / 2 + dx), "top": pc((100 - h) / 2 + dy), "width": pc(w),
               "height": pc(h), "background-size": 8}
        if plafond:   # v23 : dans le flux, centrée par sa zone ; jamais plus de « plafond » fois sa taille d'origine
            css = {"width": pc(w), "height": pc(h), "flex-shrink": 0, "max-width": rw * plafond,
                   "max-height": rh * plafond, "background-size": 8}
        if tourne:
            css["rotate"] = {"unit": 5, "value": -90.0}
        ic = self.boite(zone, nom, classes=[classe], css=css)
        brut = [(458754, [(7, "center"), (2, 0.0)]), (458755, [(7, "center"), (2, 0.0)])]
        if miroir:   # v22 : retournée haut / bas AVANT le quart de tour (scale 1 −1, comme FM 7 fois dans ses modèles ;
            #          Unity applique l'échelle avant la rotation) : ce qui est dessiné en bas finit à gauche
            brut.append((327681, [(2, 1.0), (2, -1.0)]))
        self.style_brut(ic, brut)
        self.traverse(ic)
        return ic

    def lisere(self, bouton, n, k, assombrir, estompe=False):
        """v12 : quand l'option est choisie, un interrupteur sur la variable « is-selected » que le bouton de FM calcule
        lui-même (son data-to-send-setter) montre la case choisie de la maquette : v17 : fond vert sombre, liseré
        #3fe0b4 et halo, DERRIÈRE l'icône. v15 : éteinte, la case est estompée (maquette : « contraire ») si l'option
        choisie n'est pas celle par défaut (un calcul « option choisie ? » de plus, sur l'option par défaut) ; v16 :
        estompe = toujours estompée éteinte ; l'estompe est DEVANT l'icône (la maquette baissait l'icône à 32 %)"""
        plein = {"position": "absolute", "left": 0, "top": 0, "width": pc(100), "height": pc(100)}
        voile = {"flex-grow": 1, "background-color": COUL["contraire"], **cadre_css(1, COUL["contraire-bord"], 8)}
        sw = self.interrupteur(bouton, f"o{k}-choisie", "is-selected", css=plein, index=0)
        self.traverse(sw)
        self.traverse(self.boite(sw, f"o{k}-choisie-non", css={"flex-grow": 1}))
        oui = self.boite(sw, f"o{k}-choisie-oui", css={"flex-grow": 1, "background-color": COUL["choisi-fond"],
                                                       **cadre_css(2, COUL["choisi"], 8)})
        self.traverse(oui)
        self.traverse(self.boite(oui, f"o{k}-halo", css={"position": "absolute", "left": -5, "top": -5, "right": -5,
                                                         "bottom": -5, **cadre_css(3, COUL["anneau"], 11)}))
        if not (assombrir or estompe):
            return
        par = bouton
        if not estompe:
            d = DEFAUTS[n]
            par = self._choisi(bouton, n, f"o{k}-defaut", [d])
            self.t.styles.style(self.t, par, plein)
            self.traverse(par)
        sw = self.interrupteur(par, f"o{k}-lisere", "is-selected", css=plein)
        self.traverse(sw)
        if estompe:
            self.traverse(self.boite(sw, f"o{k}-estompe-oui", css=voile))
        else:
            sw2 = self.interrupteur(sw, f"o{k}-estompe", f"kinitoe{DEFAUTS[n]}", css={"flex-grow": 1})
            self.traverse(sw2)
            self.traverse(self.boite(sw2, f"o{k}-estompe-oui", css=voile))
            self.traverse(self.boite(sw2, f"o{k}-estompe-non", css={"flex-grow": 1}))
        self.traverse(self.boite(sw, f"o{k}-estompe-rien", css={"flex-grow": 1}))

    def retenir(self, parent, chemin, variable, nom):
        """v18 : un BindingSetter qui recopie la VALEUR de <chemin> (lue ici) dans la variable entière <variable>,
        visible de tout ce qu'il contient, même sous l'enveloppe d'une autre consigne. Fonction de FM 8ca91f1c
        (« copier une liaison dans une variable »), celle des cartes de chaleur du match (match -> fixture), recopiée
        avec ses arguments ; seuls les deux chemins changent"""
        t, src = self.t, self.src
        sel = t.clone(src.choix, parent, src=src.tb)
        for k in list(t.children(sel)):
            t.remove(k)
        t.styles.copy_from(src.tb.styles, t, sel)
        self._nom(sel, nom)
        t.elem(sel)["m_Classes"], t.elem(sel)["m_RuleIndex"] = [], -1
        sd = t.sd(sel)
        v = copy.deepcopy(next(x for x in sd["ValueVariables"] if x["m_name"] == "teaminstructionoptionid"))
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = variable, "Unset"   # sans type, comme playerList (cartes de chaleur)
        f = copy.deepcopy(src.copie)
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
        if len(chemins) != 2:
            raise ValueError("fonction de copie de FM (8ca91f1c) : arguments inattendus")
        chemins[0][1] = bytes([1, len(chemin)]) + chemin.encode()
        chemins[1][1] = bytes([1, len(variable)]) + variable.encode()
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        sd["ValueVariables"], sd["BindFunction"] = [v], [f]
        t.styles.style(t, sel, {"flex-grow": 1})
        return sel

    def _choisi(self, parent, n, nom, places):
        """le calcul « option choisie ? » du bouton de FM (data-to-send-setter : fonction
        BindAndSetToDestinationResultOfIntComparison sur tactic.SelectedTeamInstructionOption), recopié hors du bouton,
        une fois par place : variables kinitoe<place> (vrai si c'est l'option choisie)"""
        return self._comparer(parent, nom, [(f"kinitoe{p}", self.src.options[n][p][0]) for p in places])

    def _comparer(self, parent, nom, paires, source=None):
        """v23 : le même calcul de FM, une fois par paire (variable, entier) : variable = (source == entier) ; source =
        un autre chemin que tactic.SelectedTeamInstructionOption (ex. settings.TextScaling, lu par FM dans ses cellules
        de tableau sous la même racine « settings »)"""
        t, src = self.t, self.src
        sel = t.clone(src.choix, parent, src=src.tb)
        for k in list(t.children(sel)):
            t.remove(k)
        t.styles.copy_from(src.tb.styles, t, sel)
        self._nom(sel, nom)
        t.elem(sel)["m_Classes"], t.elem(sel)["m_RuleIndex"] = [], -1
        sd = t.sd(sel)
        pv = next(x for x in sd["ValueVariables"] if x["m_name"] == "is-selected")
        if len(sd.get("BindFunction") or []) != 1:
            raise ValueError("calcul « option choisie ? » du bouton de FM : forme inattendue")
        pf = sd["BindFunction"][0]
        variables, fonctions = [], []
        origine = b"tactic.SelectedTeamInstructionOption"
        for nom_var, entier in paires:
            v = copy.deepcopy(pv)
            v["m_name"] = nom_var
            variables.append(v)
            f = copy.deepcopy(pf)
            args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
            chemins = entiers = sources = 0
            for a in args:
                if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]") and bytes(a[1]) == bytes([1, 11]) + b"is-selected":
                    a[1] = bytes([1, len(v["m_name"])]) + v["m_name"].encode()
                    chemins += 1
                elif bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]") and bytes(a[1]) == bytes([1, len(origine)]) + origine:
                    if source:
                        a[1] = bytes([1, len(source)]) + source.encode()
                    sources += 1
                elif bytes(a[0]).endswith(b"Int32VisualArg"):
                    a[1] = struct.pack("<i", entier)
                    entiers += 1
            if (chemins, entiers, sources) != (1, 1, 1):
                raise ValueError("calcul « option choisie ? » du bouton de FM : arguments inattendus")
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
            fonctions.append(f)
        sd["ValueVariables"], sd["BindFunction"] = variables, fonctions
        return sel

    def selon(self, parent, n, faire, nom, css=None, places=None):
        """ce qui s'affiche dépend de l'option en cours de la consigne n : faire(parent, place) pose UN élément par
        place ; des interrupteurs de FM imbriqués (un par place, sur kinitoe<place>) choisissent le bon. L'option par
        défaut de FM (place 0 sauf mention) est la dernière : elle s'affiche tant que rien d'autre n'est vrai"""
        places = list(range(len(self.src.options[n]))) if places is None else places
        sel = self._choisi(parent, n, nom, places)
        if css:
            self.t.styles.style(self.t, sel, css)
        ordre = places[1:] + places[:1]

        def chaine(par, ks):
            if len(ks) == 1:
                faire(par, ks[0])
                return
            sw = self.interrupteur(par, f"{nom}-si-{ks[0]}", f"kinitoe{ks[0]}", css={"flex-grow": 1})
            chaine(sw, ks[1:])   # rang 0 : ce n'est pas l'option ks[0]
            faire(sw, ks[0])     # rang 1 : c'est elle
        chaine(sel, ordre)
        return sel

    def selon_valeur(self, parent, source, valeurs, faire, nom, css=None):
        """v23 : comme selon(), mais sur la valeur entière d'un chemin quelconque (variables kinitot<valeur>) ;
        valeurs[0] s'affiche si aucune autre n'est vraie (valeur absente ou illisible)"""
        sel = self._comparer(parent, nom, [(f"kinitot{v}", v) for v in valeurs], source)
        if css:
            self.t.styles.style(self.t, sel, css)

        def chaine(par, vs):
            if len(vs) == 1:
                faire(par, vs[0])
                return
            sw = self.interrupteur(par, f"{nom}-si-{vs[0]}", f"kinitot{vs[0]}")
            chaine(sw, vs[1:])
            faire(sw, vs[0])
        chaine(sel, list(valeurs[1:]) + [valeurs[0]])
        return sel

    def selon_langue(self, parent, nom, faire, langues, defaut, css=None):
        """v24 : ce qui s'affiche dépend de la langue du jeu : le conteneur de FM qui lit le réglage natif
        current_language (tdd-messages-banner), puis un interrupteur de FM par langue (languagesetting.PropertyValue
        == nom de la langue ; rang 1 = c'est elle) ; faire(parent, valeur) pose UN élément ; defaut si aucune ne
        correspond. Le tout laisse passer les clics"""
        t, src = self.t, self.src
        env = t.clone(src.langue_env, parent, src=src.tg)
        recaler_parent(t, env)
        for k in list(t.children(env)):
            if not t.elem(k).get("m_FullTypeName", "").endswith("Component"):
                t.remove(k)
        t.styles.copy_from(src.tg.styles, t, env)
        self._nom(env, nom)
        t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
        donnees = json.dumps([(t.refs.get(c["rid"]) or {}).get("data") for c in t.sd(env).get("m_components") or []])
        if "current_language" not in donnees or "app.NativeSettings" not in donnees:
            raise ValueError("conteneur de langue de FM (tdd-messages-banner) : forme inattendue")
        self.traverse(env)
        t.styles.style(t, env, {"flex-grow": 1} if css is None else css)

        def chaine(par, i):
            if i == len(langues):
                faire(par, defaut)
                return
            sw = t.clone(src.langue_sw, par, src=src.tg)
            recaler_parent(t, sw)
            for k in list(t.children(sw)):
                t.remove(k)
            t.styles.copy_from(src.tg.styles, t, sw)
            self._nom(sw, f"{nom}-{i}")
            t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
            f = t.sd(sw)["Binding"]["m_visualFunction"]
            args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
            mots = [a for a in args if bytes(a[0]).endswith(b"StringVisualArg")]
            if len(mots) != 1 or bytes(mots[0][1]) != bytes([1, 7]) + b"english":
                raise ValueError("interrupteur de langue de FM : arguments inattendus")
            mot = langues[i][0].encode("utf-8")
            mots[0][1] = bytes([1, len(mot)]) + mot
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
            self.traverse(sw)
            t.styles.style(t, sw, {"flex-grow": 1})
            chaine(sw, i + 1)          # rang 0 : ce n'est pas cette langue
            faire(sw, langues[i][1])   # rang 1 : c'est elle
        chaine(env, 0)
        return env

    def bascule(self, parent, n, place, defaut, css=None, **kw):
        """case à bascule (maquette v23) : éteinte, elle choisit son option ; allumée, un clic remet l'option par
        défaut (selon l'option en cours : deux boutons de FM, un seul affiché)"""
        code = self.src.options[n][place][0]
        self.n += 1
        return self.selon(parent, n, lambda par, k: self.option(par, n, defaut if k == place else place, affiche=place,
                                                                 allume=code, css={"flex-grow": 1}, **kw),
                          f"b{self.n}", css=css, places=[defaut, place])

    def etats(self, parent, n, regle, affiche, css=None, **kw):
        """case qui combine des côtés (courses de soutien, progression) : regle(place en cours) -> (place envoyée,
        allumée ?) ; une variante de bouton par option en cours"""
        opts = self.src.options[n]
        self.n += 1

        def faire(par, k):
            cible, allumee = regle(k)
            self.option(par, n, cible, affiche=affiche, allume=opts[k][0] if allumee else opts[cible][0],
                        css={"flex-grow": 1}, **kw)
        return self.selon(parent, n, faire, f"e{self.n}", css=css)


def champ_terrain(fab, cadre, nom, traits):
    """l'herbe (bandes) et les lignes du terrain (traits : [(nom, css)] en position absolue)"""
    c = fab.boite(cadre, f"{nom}-champ", css={"flex-grow": 1, "min-height": 160, "background-color": COUL["herbe2"],
                                              "overflow": "hidden"})
    for i in range(5):
        fab.boite(c, f"{nom}-herbe-{i}", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(20 * i),
                                              "height": pc(10), "background-color": COUL["herbe1"]})
    for n, css in traits:
        fab.traverse(fab.boite(c, f"{nom}-{n}", css={"position": "absolute", **css}))
    return c


def milieu(y, rond):
    return [("milieu", {"left": 0, "width": pc(100), "top": pc(y), "height": 0, "border-top-width": 1,
                        "border-top-color": COUL["ligne"]}),
            ("rond", {"left": pc(50), "top": pc(y), "width": rond, "height": rond, "margin-left": -rond / 2,
                      "margin-top": -rond / 2, **cadre_css(1, COUL["ligne"], pc(50))})]


TRAITS_RELANCE = milieu(50, 52) + [
    ("surface", {"left": pc(18), "width": pc(64), "bottom": -1, "height": pc(15), **cadre_css(1, COUL["ligne"])}),
    ("six-metres", {"left": pc(37), "width": pc(26), "bottom": -1, "height": pc(5), **cadre_css(1, COUL["ligne"])}),
    ("but", {"left": pc(43), "width": pc(14), "bottom": 0, "height": 3, "background-color": COUL["blanc"]})]
TRAITS_AVANCEE = milieu(58, 70)
TRAITS_FINITION = [
    ("six-metres", {"left": pc(36), "width": pc(28), "top": -1, "height": pc(9), **cadre_css(1, COUL["ligne"])}),
    ("but", {"left": pc(43), "width": pc(14), "top": 0, "height": 3, "background-color": COUL["blanc"]}),
    ("arc", {"left": pc(50), "top": pc(30), "width": 70, "height": 22, "margin-left": -35,
             **cadre_css(1, COUL["ligne"]), "border-top-width": 0, "border-bottom-left-radius": 70,
             "border-bottom-right-radius": 70})]
BANDE = {"flex-direction": "column", "padding-top": 6, "padding-bottom": 6, "padding-left": 8, "padding-right": 8,
         "background-color": COUL["bandeau"]}
BANDE_BAS = {**BANDE, "border-top-width": 1, "border-top-color": COUL["filet"]}
TITRE_BAS = {"font-size": TITRE_BANDE, "white-space": "nowrap", "flex-grow": 1, "-unity-text-align": "lower-center"}


def case_abs(fab, parent, nom, x, y, w, h):
    """emplacement d'une case sur un terrain, en % (3 px de marge, comme la maquette)"""
    return fab.boite(parent, nom, css={"position": "absolute", "left": pc(x), "top": pc(y), "width": pc(w),
                                       "height": pc(h), "padding-top": 3, "padding-bottom": 3, "padding-left": 3,
                                       "padding-right": 3})


def relance(fab, cadre):
    """terrain « Relance » de la maquette v23 : Réception des passes en haut, cibles du gardien sur le terrain,
    Sorties de but et Relances GB (vitesse) en bas"""
    haut = fab.boite(cadre, "reception", css={**BANDE, "border-bottom-width": 1, "border-bottom-color": COUL["filet"]})
    e = fab.enveloppe(haut, 20, "reception-env", css={"flex-direction": "column"})
    fab.titre(e, "reception")
    duo = fab.boite(e, "reception-duo", css={"flex-direction": "row"})
    places, defaut = BASCULES[20]
    ech = fab.echelle(20, places)
    for i, p in enumerate(places):   # v16 : nom en infobulle ; v19 : icônes à la taille de leur case
        fab.bascule(duo, 20, p, defaut, css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                                             "margin-left": 6 if i else 0},
                    icone=True, echelle=ech, petit=True, texte=False, bulle=True, assombrir=True)
    champ = champ_terrain(fab, cadre, "relance", TRAITS_RELANCE)
    e = fab.enveloppe(champ, 16, "gb-env", traverse=True)
    for p, zones in ZONES_GB.items():   # v19 : police fixe (en « Plus grand », « latéraux » se coupait)
        for x, y, w, h in zones:
            fab.option(e, 16, p, petit=True, classe="label-sm", assombrir=True, taille_texte=TEXTE_ZONES,
                       css={"position": "absolute", "left": pc(x), "top": pc(y), "width": pc(w), "height": pc(h)})
    fab.traverse(fab.boite(champ, "gardien-point", css={"position": "absolute", "left": pc(50), "top": pc(95), "width": 13,
                                                        "height": 13, "margin-left": -6.5, "margin-top": -6.5,
                                                        "background-color": COUL["blanc"],
                                                        **cadre_css(2, COUL["gardien"], pc(50))}))
    bas = fab.boite(cadre, "gardien", css={**BANDE_BAS, "flex-direction": "row"})
    for j, n in enumerate((29, 17)):   # v14 : comme la maquette, les 4 boutons sur une ligne, chaque titre au-dessus
        #                                des deux siens (v9 à v13 : une ligne par consigne, à cause des marges de FM)
        e = fab.enveloppe(bas, n, f"gardien-env-{n}", css={"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1,
                                                           "flex-basis": 0, "margin-left": 5 if j else 0})
        # v15 : titres plus petits ; v23 : TITRE_BANDE px sur une ligne, en bas de leur place (boutons alignés)
        fab.titre(e, f"gardien-{n}", css=TITRE_BAS)
        rang = fab.boite(e, f"gardien-{n}-boutons", css={"flex-direction": "row"})
        places, defaut = BASCULES[n]
        ech = fab.echelle(29, BASCULES[29][0], (17, BASCULES[17][0]))   # v19 : les 4 icônes de la bande à la même échelle
        for i, p in enumerate(places):   # v15 : icônes seules, nom en infobulle
            fab.bascule(rang, n, p, defaut, css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                                                 "margin-left": 4 if i else 0}, icone=True, echelle=ech, petit=True,
                        texte=False, bulle=True, assombrir=True)


def cote(gauche):
    """courses de soutien (4 options : équilibré, flanc gauche, flanc droit, les deux) : le côté s'allume ou s'éteint"""
    if gauche:   # allumé si flanc gauche (1) ou les deux (3)
        return lambda s: {0: (1, False), 1: (0, True), 2: (3, False), 3: (2, True)}[s]
    return lambda s: {0: (2, False), 1: (3, False), 2: (0, True), 3: (1, True)}[s]


REGLES_PROGRESSION = {   # progression (0 équilibrée, 1 axe, 2 flanc gauche, 3 flanc droit, 4 les deux flancs)
    "G": lambda s: {0: (2, False), 1: (2, False), 2: (0, True), 3: (4, False), 4: (3, True)}[s],
    "A": lambda s: (0, True) if s == 1 else (1, False),
    "D": lambda s: {0: (3, False), 1: (3, False), 2: (4, False), 3: (0, True), 4: (2, True)}[s]}


def course(fab, place, n, autre, gauche, ech, part):
    """une case des dédoublements (Kinito, 12/10) : intérieur (28) et extérieur (31) du même côté s'excluent (FM refuse
    les deux). La case dépend de l'option en cours de SA consigne et de l'autre :
    - son côté est pris par sa consigne : allumée ; un clic le retire ;
    - son côté est pris par l'autre consigne : grisée (« impossible ») ; un clic ÉCHANGE : l'autre consigne perd ce
      côté, puis celle-ci le prend (deux réglages d'un clic, dans cet ordre ; le grisé de FM levé sur ce bouton) ;
    - sinon : un clic prend le côté.
    Pour connaître l'option de l'autre consigne, la case pose son enveloppe à elle (n° = autre). v18 : avant, la
    vraie valeur que FM envoie pour CETTE consigne (teaminstructionid) est recopiée dans la variable kinitoida (Fab.
    retenir) : les boutons posés dans l'enveloppe de l'autre l'envoient (v16 / v17 : n° écrit en dur, ne marchait pas)."""
    opts = fab.src.options[n]
    cote_pris = (1, 3) if gauche else (2, 3)
    ajoute = {0: 1, 2: 3} if gauche else {0: 2, 1: 3}
    retire = {1: 0, 3: 2} if gauche else {2: 0, 3: 1}
    montre = 1 if gauche else 2
    # v22 : miroir : FM dessine le flanc gauche des dédoublements EN BAS de son image (celui de la progression EN HAUT,
    # extrait des images du jeu le 12/10) ; tournées sans miroir, les quatre icônes montraient le mauvais flanc (Kinito)
    kw = dict(icone=True, echelle=ech, part=part, tourne=True, miroir=True, texte=False, bulle=True,
              css={"flex-grow": 1})
    fab.n += 1
    nom = f"course-{fab.n}"

    def selon_soi(par, s_soi):
        if s_soi in cote_pris:
            fab.option(par, n, retire[s_soi], affiche=montre, allume=opts[s_soi][0], **kw)
            return
        garde = fab.retenir(par, "teaminstructionid", "kinitoida", f"{nom}-id-{s_soi}")
        env = fab.enveloppe(garde, autre, f"{nom}-autre-{s_soi}", css={"flex-grow": 1})

        def selon_autre(par2, s_autre):
            cible = ajoute[s_soi]
            if s_autre in cote_pris:   # impossible : grisée ; un clic échange
                fab.option(par2, autre, retire[s_autre], n_vue=n, affiche=montre, allume=opts[cible][0],
                           extra=("kinitoida", cible), force=True, estompe=True, **kw)
            else:
                fab.option(par2, n, cible, n_vue=n, affiche=montre, allume=opts[cible][0], cible="kinitoida", force=True,
                           **kw)
        fab.selon(env, autre, selon_autre, f"{nom}-selon-autre-{s_soi}", css={"flex-grow": 1})
    fab.selon(place, n, selon_soi, f"{nom}-selon", css={"flex-grow": 1})


def etiquettes(fab, parent, nom, y, items, classe="label-sm"):
    """v19 : une rangée de textes alignés à la même hauteur (y en % du terrain) : items = [(x, largeur, texte)] en % ;
    texte = mot fixe de Kinito, ou (consigne, place) pour le nom d'une option de FM"""
    rang = fab.boite(parent, nom, css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y), "height": 18})
    fab.traverse(rang)
    for i, (x, w, texte) in enumerate(items):
        case = fab.boite(rang, f"{nom}-{i}", css={"position": "absolute", "left": pc(x), "width": pc(w), "top": 0,
                                                  "height": pc(100), "justify-content": "center", "align-items": "center"})
        fab.traverse(case)
        if isinstance(texte, str):
            r = fab.texte_fixe(case, f"{nom}-{i}-texte", texte, classe=classe, css={"white-space": "nowrap"})
        else:
            var, r = fab.nom_option(case, texte[0], texte[1])
            fab.traverse(var)
            fab.t.elem(r)["m_Classes"] = [classe, "global-text-primary"]
            fab.t.styles.style(fab.t, r, {"white-space": "nowrap"})
            sd = fab.t.sd(r)
            if "TextCase" in sd:
                sd["TextCase"], sd["TextCase_UxmlAttributeFlags"] = 1, 1
        fab.traverse(r)


def avancee(fab, cadre):
    """terrain « Avancée » de la maquette v23 : couloirs de la largeur, courses de soutien, progression, stratégie
    d'attaques placées ; en bas, la largeur du jeu offensif"""
    t = fab.t
    champ = champ_terrain(fab, cadre, "avancee", TRAITS_AVANCEE)
    # les deux couloirs suivent la largeur du jeu offensif (traits pleins : l'interface n'a pas de pointillés)
    e = fab.enveloppe(champ, 4, "couloirs-env", traverse=True)

    def couloirs(par, k):
        b = fab.boite(par, f"couloirs-{k}", css={"flex-grow": 1})
        fab.traverse(b)
        for x in COULOIRS[k]:
            fab.traverse(fab.boite(b, f"couloir-{k}-{x}", css={"position": "absolute", "left": pc(x), "top": 0,
                                                               "height": pc(100), "width": 0, "border-left-width": 2,
                                                               "border-left-color": (1.0, 1.0, 1.0, 0.45)}))
    sel = fab.selon(e, 4, couloirs, "couloirs", css={"flex-grow": 1})
    fab.traverse(sel)
    for r in t.walk(sel):
        if typ(t, r) == "BindableSwitchElement":
            fab.traverse(r)
    # courses de soutien : extérieures (31) sur les bords, intérieures (28) au milieu ; icônes de FM en portrait
    e28 = fab.enveloppe(champ, 28, "courses-env-28", traverse=True)
    fab.titre(e28, "courses", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(0.6)})
    e31 = fab.enveloppe(champ, 31, "courses-env-31", traverse=True)
    ech = fab.echelle(28, (1, 2), (31, (1, 2)))
    for n, autre, env, gauche, x, w in ((31, 28, e31, True, 0, 22), (28, 31, e28, True, 22, 28),
                                        (28, 31, e28, False, 50, 28), (31, 28, e31, False, 78, 22)):
        place = case_abs(fab, env, f"course-{n}-{'g' if gauche else 'd'}", x, 9, w, 22)
        # v19 : les quatre icônes à la même taille (la case la plus étroite, 22 %, commande)
        course(fab, place, n, autre, gauche, ech, (22 / w, 1.0))
    # v19 : « Extérieur » au-dessus de chaque flanc, un seul « Intérieur » sur les deux cases du milieu, même hauteur
    # v24 : dans la langue du jeu (Kinito) ; ceux du skin si elle ne se lit pas

    def mots(par, ext_int):
        b = fab.boite(par, f"courses-noms-{fab.n}", css={"flex-grow": 1})
        fab.n += 1
        fab.traverse(b)
        etiquettes(fab, b, f"courses-noms-{fab.n}", 4.6, [(0, 22, ext_int[0]), (22, 56, ext_int[1]),
                                                          (78, 22, ext_int[0])])
    fab.selon_langue(e31, "courses-langue", mots, COURSES_LANGUES, (TEXTES_COURSES["ext"], TEXTES_COURSES["int"]),
                     css={"position": "absolute", "left": 0, "top": 0, "width": pc(100), "height": pc(100)})
    # progression : flanc gauche, axe, flanc droit (v23 : plus de « Gauche » / « Droite » sous les dédoublements, Kinito)
    e30 = fab.enveloppe(champ, 30, "progression-env", traverse=True)
    fab.titre(e30, "progression", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(36)})
    ech = fab.echelle(30, (2, 1, 3))
    for cle, montre, x, w in (("G", 2, 0, 30), ("A", 1, 30, 40), ("D", 3, 70, 30)):
        place = case_abs(fab, e30, f"progression-{cle}", x, 40.5, w, 36)
        # v19 : les trois icônes à la même taille ; v23 : schéma plus grand, nom centré dans le bas de la case
        fab.etats(place, 30, REGLES_PROGRESSION[cle], montre, css={"flex-grow": 1}, icone=True, echelle=ech,
                  part=(30 / w, 1.0), tourne=True, petit=True, rempli=REMPLI_PROGRESSION, texte_bas=TEXTE_PROGRESSION)
    # stratégie d'attaques placées (24) : Gérer le pressing / Contourner le pressing ; v19 : icônes seules + infobulle
    e24 = fab.enveloppe(champ, 24, "strategie-env", traverse=True)
    places, defaut = BASCULES[24]
    ech = fab.echelle(24, places)
    for i, p in enumerate(places):
        place = case_abs(fab, e24, f"strategie-{p}", 50 * i, 80, 50, 20)
        fab.bascule(place, 24, p, defaut, css={"flex-grow": 1}, icone=True, echelle=ech, petit=True, texte=False,
                    bulle=True, assombrir=True)
    # en bas : largeur du jeu offensif, les 5 options en icônes
    bas = fab.boite(cadre, "largeur", css=BANDE_BAS)
    e = fab.enveloppe(bas, 4, "largeur-env", css={"flex-direction": "column"})
    fab.titre(e, "largeur", css=TITRE_BAS)   # v23 : comme les titres de la bande du gardien
    rang = fab.boite(e, "largeur-boutons", css={"flex-direction": "row"})
    ech = fab.echelle(4, range(5))
    for p in range(len(fab.src.options[4])):
        fab.option(rang, 4, p, icone=True, echelle=ech, texte=False, petit=True, bulle=True,
                   css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                        "margin-left": 4 if p else 0})


def finition(fab, cadre):
    """terrain « 30 derniers mètres » de la maquette v23 : Patience (jouer dans la surface, centrer de loin), Tirs de
    loin, Dribbles ; en bas, Style de centres. v19 : icônes seules à la taille de leur case, noms en infobulle"""
    champ = champ_terrain(fab, cadre, "finition", TRAITS_FINITION)
    e18 = fab.enveloppe(champ, 18, "patience-env", traverse=True)
    places, defaut = BASCULES[18]   # (0 centrer de loin, 2 jouer le ballon dans la surface), défaut 1
    surface = case_abs(fab, e18, "surface", 20, 0, 60, 30)
    fab.bascule(surface, 18, 2, defaut, css={"flex-grow": 1}, icone=True, petit=True, texte=False, bulle=True,
                assombrir=True)
    for cle, x in (("g", 2), ("d", 82)):   # v15 : texte plus gros, en gras et en capitales, case plus courte et centrée
        loin = case_abs(fab, e18, f"loin-{cle}", x, 6, 16, 50)
        fab.bascule(loin, 18, 0, defaut, css={"flex-grow": 1}, petit=True, vertical=True, classe="heading-xsmall-14px",
                    assombrir=True)
    for n, y, cases in ((27, 30.6, ((0, 20, 29.5), (2, 50.5, 29.5))), (19, 62.8, ((0, 2, 47), (2, 51, 47)))):
        e = fab.enveloppe(champ, n, f"actions-env-{n}", traverse=True)
        fab.titre(e, f"actions-{n}", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y)})
        places, defaut = BASCULES[n]
        ech = fab.echelle(n, places)
        for p, x, w in cases:
            place = case_abs(fab, e, f"actions-{n}-{p}", x, y + 6.5, w, 26 if n == 27 else 30)
            fab.bascule(place, n, p, defaut, css={"flex-grow": 1}, icone=True, echelle=ech, petit=True, texte=False,
                        bulle=True, assombrir=True)
    bas = fab.boite(cadre, "centres", css=BANDE_BAS)
    e = fab.enveloppe(bas, 26, "centres-env", css={"flex-direction": "column"})
    fab.titre(e, "centres", css=TITRE_BAS)   # v23 : comme les titres de la bande du gardien
    rang = fab.boite(e, "centres-boutons", css={"flex-direction": "row"})
    ech = fab.echelle(26, range(4))
    for p in range(len(fab.src.options[26])):   # v15 : 4 de front, icônes seules, nom en infobulle
        fab.option(rang, 26, p, icone=True, echelle=ech, petit=True, texte=False, bulle=True, assombrir=True,
                   css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                        "margin-left": 4 if p else 0})


CASE = {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
        "justify-content": "center", "padding-top": 6, "padding-bottom": 6, "padding-left": 8, "padding-right": 8,
        "background-color": COUL["case"], "overflow": "hidden", **cadre_css(1, COUL["tuile-bord"], 9)}


def degrade(fab, e, nom):
    """v19 : le fond des tuiles de la maquette, un dégradé (#1a3631 en haut -> #142b27 en bas), en 8 bandes posées
    sous tout le reste (les styles de l'interface ne font pas de dégradé ; SIGradient prend ses couleurs dans les
    feuilles de FM). À poser juste après l'enveloppe, avant son contenu"""
    haut, bas = (0x1a, 0x36, 0x31), (0x14, 0x2b, 0x27)
    for i in range(8):
        c = tuple((haut[j] + (bas[j] - haut[j]) * i / 7) / 255 for j in range(3)) + (1.0,)
        fab.traverse(fab.boite(e, f"{nom}-degrade-{i}", css={"position": "absolute", "left": 0, "width": pc(100),
                                                              "top": pc(12.5 * i), "height": pc(13),
                                                              "background-color": c}))


def tuile(fab, rangee, n, i, colonne=False, icones=False, plafond=None, remplir=False, marge=None, css=None):
    """une tuile du bas (maquette v23) : 5 ou 3 crans en icônes, ou des cartes. v15 / v16 (icones) : titres alignés en
    haut des tuiles, boutons de même hauteur, icônes seules, nom de l'option en infobulle ; cartes estompées quand une
    autre option que celle par défaut est choisie ; v19 : icônes à la taille de leur case, fond en dégradé ; v23 :
    titre en bas de sa place (s'il passe à la ligne dans une langue, les boutons restent alignés d'une tuile à
    l'autre) ; colonne = options l'une sous l'autre (« sans le ballon ») ; plafond : voir PLAFOND_ICONE ; v26 (26.14) :
    remplir = boutons à la hauteur de la tuile, marge = écart à gauche (sinon 10 px), css = style de plus"""
    e = fab.enveloppe(rangee, n, f"tuile-{n}", css={**CASE, "margin-left": marge if marge is not None else (10 if i else 0),
                                                    "justify-content": "flex-start" if icones else "center",
                                                    **(css or {})})
    degrade(fab, e, f"tuile-{n}")
    fab.titre(e, f"tuile-{n}", css=None if colonne else {"flex-grow": 1, "-unity-text-align": "lower-center"})
    rang = fab.boite(e, f"tuile-{n}-boutons", css={"flex-direction": "column" if colonne else "row",
                                                   "justify-content": "center",
                                                   **({"flex-grow": 1} if colonne or remplir else {})})
    hauteur = {"height": HAUT_TUILE} if icones and not (colonne or remplir) else {}
    if n in CRANS:
        nb_crans = len(fab.src.options[n])
        ech = fab.echelle(n, range(nb_crans))
        for p in range(nb_crans):
            fab.option(rang, n, p, icone=True, echelle=ech, texte=False, petit=True, bulle=True,
                       css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "margin-left": 4 if p else 0, **hauteur})
        if not icones:   # v16 : avec le ballon, le nom de l'option en cours n'est plus écrit dessous (infobulles)
            fab.selon(e, n, lambda par, k: fab.nom_option(par, n, k, css={"margin-top": 3}), f"tuile-{n}-valeur")
        return
    places, defaut = BASCULES.get(n, (tuple(range(len(fab.src.options[n]))), None))
    ech = fab.echelle(n, places)
    for j, p in enumerate(places):
        css = ({"margin-top": 6 if j else 0, "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0} if colonne else
               {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "margin-left": 6 if j else 0, **hauteur})
        kw = (dict(icone=True, echelle=ech, petit=True, texte=False, bulle=True, assombrir=True, plafond=plafond)
              if icones else
              dict(icone=True, haut=22, petit=True, ligne=True, assombrir=True))
        if defaut is None:
            fab.option(rang, n, p, css=css, **kw)
        else:
            fab.bascule(rang, n, p, defaut, css=css, **kw)


TRAITS_LIGNES = milieu(50, 60) + [
    ("surface-haut", {"left": pc(18), "width": pc(64), "top": -1, "height": pc(13), **cadre_css(1, COUL["ligne"])}),
    ("six-metres-haut", {"left": pc(37), "width": pc(26), "top": -1, "height": pc(4.5), **cadre_css(1, COUL["ligne"])}),
    ("surface", {"left": pc(18), "width": pc(64), "bottom": -1, "height": pc(13), **cadre_css(1, COUL["ligne"])}),
    ("six-metres", {"left": pc(37), "width": pc(26), "bottom": -1, "height": pc(4.5), **cadre_css(1, COUL["ligne"])}),
    ("but", {"left": pc(43), "width": pc(14), "bottom": 0, "height": 3, "background-color": COUL["blanc"]})]
TRAITS_PIEGE = milieu(50, 60) + [
    ("surface", {"left": pc(18), "width": pc(64), "bottom": -1, "height": pc(21), **cadre_css(1, COUL["ligne"])}),
    ("six-metres", {"left": pc(37), "width": pc(26), "bottom": -1, "height": pc(7), **cadre_css(1, COUL["ligne"])}),
    ("but", {"left": pc(43), "width": pc(14), "bottom": 0, "height": 3, "background-color": COUL["blanc"]})] + [
    (f"couloir-{x}-{y}", {"left": pc(x), "top": pc(y), "height": pc(h), "width": 0, "border-left-width": 2,
                          "border-left-color": (1.0, 1.0, 1.0, 0.40)})
    for x in (27, 73) for y, h in ((6, 46), (56.5, 43.5))]


def calque_selon(fab, env, n, faire, nom):
    """ce qui dépend de l'option en cours, posé en calque sur tout le terrain, sans prendre les clics"""
    sel = fab.selon(env, n, faire, nom, css={"position": "absolute", "left": 0, "top": 0, "width": pc(100),
                                             "height": pc(100)})
    for r in fab.t.walk(sel):
        if typ(fab.t, r) in ("BindableSwitchElement", "BindingSetter"):
            fab.traverse(r)
    return sel


def fleche(fab, par, nom, x1, x2, y, couleur):
    """v19 : une flèche peinte sur l'herbe (maquette : flecheHerbe) de x1 % à x2 %, à y % : halo, trait plein (pas de
    pointillés dans l'interface de FM) et pointe (un coin à deux bords, tourné de 45°)"""
    r, g, b, _ = couleur
    g0, d0 = min(x1, x2), max(x1, x2)
    fab.traverse(fab.boite(par, f"{nom}-halo", css={"position": "absolute", "left": pc(g0), "width": pc(d0 - g0),
                                                     "top": pc(y), "height": 10, "margin-top": -5,
                                                     "background-color": (r, g, b, 0.22), **cadre_css(0, couleur, 5)}))
    fab.traverse(fab.boite(par, f"{nom}-trait", css={"position": "absolute", "left": pc(g0), "width": pc(d0 - g0),
                                                      "top": pc(y), "height": 3, "margin-top": -1.5,
                                                      "background-color": couleur}))
    droite = x2 > x1
    fab.traverse(fab.boite(par, f"{nom}-pointe", css={"position": "absolute", "left": pc(x2), "top": pc(y), "width": 11,
                                                       "height": 11, "margin-left": -10 if droite else -1,
                                                       "margin-top": -5.5, "border-top-width": 3,
                                                       "border-right-width": 3, "border-top-color": couleur,
                                                       "border-right-color": couleur,
                                                       "rotate": {"unit": 5, "value": 45.0 if droite else -135.0}}))


FLECHES_PIEGE = {0: [(5.8, 36.7), (94.2, 63.3)],    # piège dans l'axe : des deux touches vers le milieu (maquette v23)
                 2: [(41.7, 7.5), (58.3, 92.5)]}    # piège sur les côtés : du milieu vers les touches


FLECHES_CENTRES = {2: FLECHES_PIEGE[0],   # v22 : Laisser centrer (la case du milieu) : vers l'axe (maquette v23)
                   0: FLECHES_PIEGE[2]}   # Empêcher de centrer (les cases des côtés) : vers les côtés


def fleches(fab, par, k, nom, table, ys):
    """les flèches de l'option k (table : option -> [(x1, x2)] en %), une rangée à chaque hauteur de ys (en %)"""
    b = fab.boite(par, f"{nom}-fleches-{k}", css={"flex-grow": 1})
    fab.traverse(b)
    for y in ys:   # piège : au-dessus et au-dessous des cases, comme la maquette
        for j, (x1, x2) in enumerate(table.get(k, [])):
            fleche(fab, b, f"{nom}-fleche-{k}-{y}-{j}", x1, x2, y, COUL["pressing"])


def trait_horizontal(fab, par, nom, y, couleur):
    b = fab.boite(par, nom, css={"flex-grow": 1})
    fab.traverse(b)
    fab.traverse(fab.boite(b, f"{nom}-trait", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y),
                                                   "height": 0, "border-top-width": 3, "border-top-color": couleur}))


def ligne_consigne(fab, par, n, k, y, couleur, voile, nom):
    """une variante du terrain des lignes (maquette v23) : voile, halo + trait de la ligne, points des crans, badge
    « nom de la consigne / option » posé sur la ligne"""
    t = fab.t
    b = fab.boite(par, f"{nom}-{k}", css={"flex-grow": 1})
    fab.traverse(b)
    haut, bas, coul_voile = voile
    fab.traverse(fab.boite(b, f"{nom}-{k}-voile", css={"position": "absolute", "left": 0, "width": pc(100),
                                                        "top": pc(y if bas else 0), "height": pc((100 - y) if bas else y),
                                                        "background-color": coul_voile}))
    r, g, bl, _ = couleur
    fab.traverse(fab.boite(b, f"{nom}-{k}-halo", css={"position": "absolute", "left": pc(8), "width": pc(89), "top": pc(y),
                                                       "height": 12, "margin-top": -6, "background-color": (r, g, bl, 0.2),
                                                       **{f"border-{c}-radius": 6 for c in ("top-left", "top-right",
                                                                                            "bottom-left", "bottom-right")}}))
    fab.traverse(fab.boite(b, f"{nom}-{k}-trait", css={"position": "absolute", "left": pc(8), "width": pc(89), "top": pc(y),
                                                        "height": 3, "margin-top": -1.5, "background-color": couleur}))
    crans = Y_PRESSING if n == 8 else Y_LIGNE
    for j, yj in enumerate(crans):   # les points des crans, à gauche ; celui de l'option en cours plus gros
        d = 12 if j == k else 6
        fab.traverse(fab.boite(b, f"{nom}-{k}-cran-{j}", css={"position": "absolute", "left": pc(4), "top": pc(yj),
                                                               "width": d, "height": d, "margin-left": -d / 2,
                                                               "margin-top": -d / 2,
                                                               "background-color": couleur if j == k else (r, g, bl, 0.4),
                                                               **cadre_css(0, couleur, d / 2)}))
    if n == 9:   # repères de la ligne défensive (maquette : petits ronds blancs cerclés)
        for x in (5, 17, 83, 95):
            fab.traverse(fab.boite(b, f"{nom}-{k}-repere-{x}", css={"position": "absolute", "left": pc(x), "top": pc(y),
                                                                     "width": 10, "height": 10, "margin-left": -5,
                                                                     "margin-top": -5,
                                                                     "background-color": (0xf2 / 255, 0xfd / 255, 1.0, 1.0),
                                                                     **cadre_css(2, couleur, 5)}))
    # le badge, centré sur la ligne (v17 : rangée de 44 px ; v15 / v16 : hauteur nulle, le badge était écrasé)
    rang = fab.boite(b, f"{nom}-{k}-badge-rang", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y),
                                                       "height": 44, "margin-top": -22, "flex-direction": "row",
                                                       "justify-content": "center", "align-items": "center"})
    fab.traverse(rang)
    # v21 : les deux badges ont la MÊME taille, fixe, celle du plus long texte ; s'il le faut, le badge s'élargit à son
    # texte (comme en v18), il ne le coupe jamais. v19 / v20 : une rangée invisible de hauteur nulle portait les textes
    # les plus longs ; vu deux fois en jeu, le badge prenait alors TOUTE la largeur du terrain : abandonné. v23 : la
    # largeur suit la taille du texte choisie dans FM (Kinito : « en Petit c'est bon, en Grand la taille change ») :
    # un badge par taille (BADGE_LARGEURS, px), FM montre celui de la taille en cours (settings.TextScaling)

    def badge_(par, taille):
        badge = fab.boite(par, f"{nom}-{k}-badge-{taille}", css={"flex-direction": "column", "align-items": "center",
                                                                 "min-width": BADGE_LARGEURS[taille],
                                                                 "padding-top": 2, "padding-bottom": 3,
                                                                 "padding-left": 8, "padding-right": 8,
                                                                 "background-color": COUL["badge"],
                                                                 **cadre_css(1, couleur, 6)})
        fab.traverse(badge)
        tit = fab.titre(badge, f"{nom}-{k}-badge-{taille}-nom", css={"margin-bottom": 0, "color": couleur})
        fab.traverse(tit)
        var, txt = fab.nom_option(badge, n, k, petit=False)
        fab.traverse(var)
        fab.traverse(txt)
        t.styles.style(t, txt, {"color": COUL["blanc"]})
    sel = fab.selon_valeur(rang, "settings.TextScaling", list(BADGE_LARGEURS), badge_, f"{nom}-{k}-taille")
    for r in t.walk(sel):
        if typ(t, r) in ("BindableSwitchElement", "BindingSetter"):
            fab.traverse(r)


def lignes(fab, cadre, traits=None):
    """v15 : terrain des lignes comme la maquette v23 : relance courte du gardien en haut ; la hauteur du pressing et la
    ligne défensive en lignes qui changent de place (voile vert au-dessus du pressing, voile sombre sous la ligne
    défensive, badge sur chaque ligne) ; on clique n'importe où dans la bande d'un cran (bandes invisibles, nom de
    l'option en infobulle). Pas de pointillés ni de glissement : l'interface de FM ne sait pas les faire."""
    champ = champ_terrain(fab, cadre, "lignes", TRAITS_LIGNES if traits is None else traits)   # v26 : 26.14 a les siens
    e = fab.enveloppe(champ, 8, "pressing-env", traverse=True)
    calque_selon(fab, e, 8, lambda par, k: ligne_consigne(fab, par, 8, k, Y_PRESSING[k], COUL["pressing"],
                                                          (True, False, COUL["voile-pressing"]), "pressing"),
                 "pressing-ligne")
    e = fab.enveloppe(champ, 9, "defense-env", traverse=True)
    calque_selon(fab, e, 9, lambda par, k: ligne_consigne(fab, par, 9, k, Y_LIGNE[k], COUL["defense"],
                                                          (False, True, COUL["voile-defense"]), "defense"),
                 "defense-ligne")
    for n, bandes in ((8, BANDES_PRESSING), (9, BANDES_LIGNE)):   # les bandes de clic, par-dessus les lignes
        e = fab.enveloppe(champ, n, f"bandes-env-{n}", traverse=True)
        for k, (y0, y1) in enumerate(bandes):
            fab.option(e, n, k, nu=True, texte=False, bulle=True,
                       css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y0), "height": pc(y1 - y0)})
    e = fab.enveloppe(champ, 23, "relance-courte-env", traverse=True)
    fab.titre(e, "relance-courte", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(0.6)})
    ech = fab.echelle(23, (0, 1))
    for k, x in ((0, 3), (1, 51.5)):
        fab.option(case_abs(fab, e, f"relance-courte-{k}", x, 5.5, 45.5, 13), 23, k, icone=True, echelle=ech, petit=True,
                   texte=False, bulle=True, assombrir=True, css={"flex-grow": 1})   # v17 : nom en infobulle


def sans(fab, conteneur):
    """la vue « Terrain », sans le ballon (maquette v23), titres de Kinito. v23 : grille de 2 rangées (choix de Kinito,
    12/10) : en haut le terrain des lignes, le déclenchement du pressing et le terrain du piège (3/5 de la hauteur),
    en bas trois tuiles de même forme (titre + 2 cases l'une sous l'autre) : Comportement de la ligne, Transition
    défensive, En taclant (2/5) ; tout s'aligne d'une colonne à l'autre, à toutes les tailles de texte"""
    titres = fab.boite(conteneur, "sans-titres", css={"flex-direction": "row", "margin-bottom": 4})
    for i in range(len(TITRES_SANS)):   # v25 : dans la langue du jeu (Kinito) ; ceux du skin si elle ne se lit pas
        def titre_(par, mots, i=i):
            fab.n += 1
            fab.texte_fixe(par, f"sans-titre-{i}-{fab.n}", mots[i], classe="thematic-sm",
                           css={"flex-grow": 1, "-unity-text-align": "lower-center"})
        fab.selon_langue(titres, f"sans-titre-{i}", titre_, TITRES_SANS_LANGUES, TITRES_SANS,
                         css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                              "margin-left": 10 if i else 0})
    haut = fab.boite(conteneur, "sans-haut", css={"flex-direction": "row", "flex-grow": 3, "flex-shrink": 1,
                                                  "flex-basis": 0, "min-height": 180})
    bas = fab.boite(conteneur, "sans-bas", css={"flex-direction": "row", "flex-grow": 2, "flex-shrink": 1,
                                                "flex-basis": 0, "min-height": 120, "margin-top": 8})

    def cadre_(i):
        return {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "margin-left": 10 if i else 0,
                "flex-direction": "column", "overflow": "hidden", "background-color": COUL["herbe2"],
                **cadre_css(1, COUL["cadre"], 10)}
    # en haut à gauche : le terrain des lignes (v15 : comme la maquette)
    lignes(fab, fab.boite(haut, "sans-cadre-0", css=cadre_(0)))
    # en haut au milieu : Déclench. pressing en échelle (beaucoup plus souvent en haut)
    e = fab.enveloppe(haut, 10, "declench-env", css={**CASE, "margin-left": 10, "justify-content": "flex-start"})
    degrade(fab, e, "declench")
    fab.titre(e, "declench")
    ech = fab.echelle(10, range(5))
    for i, p in enumerate((4, 3, 2, 1, 0)):   # v17 : icônes seules, nom en infobulle ; v19 : à la taille de leur case
        fab.option(e, 10, p, icone=True, echelle=ech, petit=True, texte=False, bulle=True,
                   css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "margin-top": 4 if i else 0})
    # en haut à droite : piège du pressing (côtés / axe) et pressing sur centres
    piege(fab, fab.boite(haut, "sans-cadre-2", css=cadre_(2)))
    # en bas : trois tuiles de même forme ; v17 : contre-pressing au-dessus de regroupement (Kinito)
    for i, n in enumerate((15, 11, 12)):
        tuile(fab, bas, n, i, colonne=True, icones=True, plafond=PLAFOND_ICONE)


def piege(fab, cadre, traits=None):
    """le terrain du piège du pressing (côtés / axe) et du pressing sur centres (v26 : fonction à part, 26.14 la
    réutilise avec des traits aux vraies proportions)"""
    champ = champ_terrain(fab, cadre, "piege", TRAITS_PIEGE if traits is None else traits)
    e = fab.enveloppe(champ, 25, "piege-env", traverse=True)
    # v19 : les flèches de la maquette (au-dessus et au-dessous des cases) selon le piège choisi, sous les cases
    calque_selon(fab, e, 25, lambda par, k: fleches(fab, par, k, "piege", FLECHES_PIEGE, (9, 39)), "piege-fleches")
    fab.titre(e, "piege", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(0.6)})
    ech = fab.echelle(25, (0, 2))
    for p, x, w in ((2, 2, 23), (0, 30, 40), (2, 75, 23)):   # côtés sur les flancs, axe au milieu (places de la maquette)
        # v19 : icônes seules (nom en infobulle), les trois à la même taille (la case la plus étroite commande)
        fab.bascule(case_abs(fab, e, f"piege-{p}-{x}", x, 13, w, 22), 25, p, 1, css={"flex-grow": 1}, icone=True,
                    echelle=ech, part=(23 / w, 1.0), petit=True, texte=False, bulle=True, assombrir=True)
    e = fab.enveloppe(champ, 22, "centres-env", traverse=True)
    # v22 : les mêmes flèches que le piège (Kinito) : vers l'axe si « Laisser centrer » (la case du milieu), vers les
    # côtés si « Empêcher de centrer » (les cases des côtés) ; une rangée au-dessus des cases
    calque_selon(fab, e, 22, lambda par, k: fleches(fab, par, k, "centres", FLECHES_CENTRES, (57.5,)), "centres-fleches")
    fab.titre(e, "centres-sans", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(51)})
    ech = fab.echelle(22, (1, 2))
    for p, x, y, w, h in ((1, 29, 61, 42, 11), (0, 2, 61, 23, 37), (2, 29, 74, 42, 24), (0, 75, 61, 23, 37)):
        cote_ = p == 0   # « Empêcher de centrer » sur les côtés : écrit à la verticale (v12 ; le mot se coupait)
        # v19 : Équilibré et Laisser centrer : icônes seules, nom en infobulle ; v23 : « Empêcher de centrer » en
        # TEXTE_ZONES px (terrain plus court : en « Plus grand », le texte du jeu dépassait de sa case)
        fab.option(case_abs(fab, e, f"centres-{p}-{x}", x, y, w, h), 22, p, icone=not cote_, echelle=ech, petit=True,
                   vertical=cote_, texte=cote_, bulle=not cote_, assombrir=True, css={"flex-grow": 1},
                   taille_texte=TEXTE_ZONES if cote_ else None)


def terrain(fab, racine):
    """la vue « Terrain » : avec le ballon, trois colonnes (Relance, Avancée, 30 derniers mètres : titres = noms des
    phases de FM) puis deux rangées de tuiles ; sans le ballon : trois colonnes (titres de Kinito), voir sans().
    v19 : plus de défilement (v10 à v18 : copie de #Body) : tout prend la place du bloc, quelle que soit la taille du
    texte choisie dans FM (demande de Kinito) ; les terrains prennent ce que laissent les tuiles"""
    t, src = fab.t, fab.src
    t.styles.style(t, racine, {"flex-grow": 1, "flex-direction": "column"})
    pos = fab.interrupteur(racine, "possession", "inpossession", css={"flex-grow": 1})
    sans(fab, fab.boite(pos, "sans", css={"flex-grow": 1, "flex-direction": "column"}))   # rang 0 : sans le ballon
    avec = fab.boite(pos, "avec", css={"flex-grow": 1, "flex-direction": "column"})        # rang 1 : avec
    rangee = fab.boite(avec, "terrains", css={"flex-direction": "row", "flex-grow": 1, "min-height": 280})
    cadres = []
    for i, (texte, _, _) in enumerate(PHASES):
        col = fab.boite(rangee, f"colonne-{i}", css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                                    "flex-direction": "column", "margin-left": 10 if i else 0})
        tete = t.clone(src.phases[texte], col, src=src.tq)
        t.styles.copy_from(src.tq.styles, t, tete)
        fab._nom(tete, f"phase-{i}")
        t.elem(tete)["m_Classes"], t.elem(tete)["m_RuleIndex"] = ["thematic-sm", "global-text-primary"], -1
        t.styles.style(t, tete, {"-unity-text-align": "middle-center", "margin-bottom": 4})
        cadres.append(fab.boite(col, f"cadre-{i}", css={"flex-grow": 1, "flex-direction": "column", "overflow": "hidden",
                                                       "background-color": COUL["herbe2"],
                                                       **cadre_css(1, COUL["cadre"], 10)}))
    relance(fab, cadres[0])
    avancee(fab, cadres[1])
    finition(fab, cadres[2])
    for j, ligne in enumerate(TUILES):
        r = fab.boite(avec, f"tuiles-{j}", css={"flex-direction": "row", "margin-top": 8})
        for i, n in enumerate(ligne):
            tuile(fab, r, n, i, icones=True)


# ---------- morceaux de FM recopiés ----------
def forme_copie(f):
    """28/10 : une fonction 8ca91f1c de FM a la forme que retenir() attend : deux chemins puis un booléen faux, aucune
    sortie"""
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    return (len(args) == 3 and all(bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]") for a in args[:2])
            and bytes(args[2][0]).endswith(b"BooleanVisualArg") and bytes(args[2][1]) == b"\x00"
            and not (f.get("m_outputs") or {}).get("m_variable", {}).get("m_argumentBytes"))


class Sources:
    def __init__(self):
        p = ouvrir(SOURCE, depart_original=True)
        self.tp = p[3] if p else None
        s = ouvrir(SOURCE_TEXTE, depart_original=True)
        self.ts = s[3] if s else None
        self.enveloppe = self.titre = self.setter = None
        if self.tp is not None:
            # l'enveloppe : le ComponentElement qui porte « ID » et les correspondances, avec ses boutons
            self.enveloppe = first(self.tp, lambda r: typ(self.tp, r) == "ComponentElement"
                                   and any(est_bouton(self.tp, x) for x in self.tp.walk(r)))
            self.titre = first(self.tp, lambda r: typ(self.tp, r) == "SIText"
                               and "body-md-strong" in (self.tp.elem(r).get("m_Classes") or []))
        if self.ts is not None:
            self.setter = first(self.ts, lambda r: typ(self.ts, r) == "BindingSetter"
                                and any(v.get("m_name") == "ID" for v in self.ts.sd(r).get("ValueVariables") or []))
        # v4 : la variable et les boutons segmentés des cartes de chaleur
        h = ouvrir(SOURCE_BASCULE, depart_original=True)
        self.th = h[3] if h else None
        self.variable = self.variable_sd = self.segments = self.copie = None
        if self.th is not None:
            th = self.th
            self.variable = first(th, lambda r: th.elem(r).get("m_FullTypeName") == "SI.Bindable.BindingVariablesComponent")
            if self.variable is not None:
                ident = th.elem(self.variable)["m_Id"]
                proprio = th.sd(th.parent[self.variable])
                self.variable_sd = next((c["rid"] for c in proprio.get("m_components") or []
                                         if ((th.refs.get(c["rid"]) or {}).get("data") or {}).get("uxmlAssetId") == ident), None)
            self.segments = first(th, lambda r: th.name(r) == "buttons-segmented-button-row-regular-default")
            # v18 : la fonction de FM qui copie une liaison dans une variable (8ca91f1c : match -> fixture). 28/10 :
            # FM 27 (jeu du 27/10, déjà au 22/10 ?) n'a plus « match -> fixture » dans ce bloc, il garde ses deux autres
            # 8ca91f1c (selectedperson -> tableselection, tableselection -> person) : MÊME forme, à l'octet près (deux
            # chemins, puis un booléen faux ; sorties vides : relevé dans l'ancien original et dans celui du jour), et
            # retenir() réécrit les deux chemins : la fonction écrite est la même. Sans ce repli, Sources().ok() échouait
            # et 26.13 ne se posait plus du tout (« morceaux de FM introuvables »)
            copies = [copy.deepcopy(f) for r in th.refs.values() for f in (((r or {}).get("data") or {})
                      .get("BindFunction") or []) if isinstance(f, dict)
                      and f.get("m_target", {}).get("m_guid") == "8ca91f1cfa07a3447ad7c8381cadfef5"
                      and forme_copie(f)]
            self.copie = next((f for f in copies if b"fixture" in bytes(f["m_inputs"]["m_variable"]["m_argumentBytes"])),
                              copies[0] if copies else None)
        # v6 : le bouton de FM à texte seul (prototype), le calcul « option choisie ? » du bouton de FM (pour les cases à
        # bascule), les noms des phases, les codes et icônes des options (données du jeu)
        self.bouton_texte = None
        if self.tp is not None:
            self.bouton_texte = first(self.tp, lambda r: est_bouton(self.tp, r) and len(self.tp.children(r)) == 1
                                      and typ(self.tp, self.tp.children(r)[0]) == "SIText")
        b = ouvrir(MODELE_BOUTON, depart_original=True)
        self.tb = b[3] if b else None
        self.choix = first(self.tb, lambda r: self.tb.name(r) == "data-to-send-setter") if self.tb else None
        # v7 : le contenu du bouton de FM (BindingExpect > BindingSetter > SIEnabled > SIStyleSetter > SIButton), recopié
        # « à plat » dans le bloc : ses marges internes se règlent alors (dans un modèle inclus, non)
        self.racine_bouton = self.tb.parent.get(self.choix) if self.choix is not None else None
        self.texte_option = self.tp.children(self.bouton_texte)[0] if self.bouton_texte is not None else None
        u = ouvrir(SOURCE_BULLE, depart_original=True)   # v15 : infobulle (Tooltip > SIText), comme 26.4
        self.tu = u[3] if u else None
        self.bulle = first(self.tu, lambda r: typ(self.tu, r) == "Tooltip" and len(self.tu.children(r)) == 1
                           and typ(self.tu, self.tu.children(r)[0]) == "SIText") if self.tu else None
        q = ouvrir(SOURCE_PHASES, depart_original=True)
        self.tq = q[3] if q else None
        self.phases = {n: first(self.tq, lambda r, n=n: self.tq.name(r) == n and typ(self.tq, r) == "SIText")
                       for n, _, _ in PHASES} if self.tq else {}
        self.options = options_consignes(CONSIGNES_AVEC | CONSIGNES_SANS)
        self.dessins = dessins_icones({c for v in self.options.values() for _, c in v if c})   # v19
        g = ouvrir(SOURCE_LANGUE, depart_original=True)   # v24 : la langue du jeu
        self.tg = g[3] if g else None
        self.langue_env = self.langue_sw = None
        if self.tg is not None:
            tg = self.tg
            self.langue_env = first(tg, lambda r: typ(tg, r) == "ComponentElement" and any(
                "languagesetting" in json.dumps((tg.refs.get(c["rid"]) or {}).get("data") or {})
                for c in tg.sd(r).get("m_components") or []))
            self.langue_sw = first(tg, lambda r: typ(tg, r) == "BindableSwitchElement"
                                   and (((tg.sd(r).get("Binding") or {}).get("m_visualFunction") or {})
                                        .get("m_target") or {}).get("m_guid") == "7980ef35a33c35e43940a2b7add470dd")

    def ok(self):
        return None not in (self.enveloppe, self.titre, self.setter, self.variable, self.variable_sd, self.segments,
                            self.bouton_texte, self.choix, self.racine_bouton, self.texte_option, self.bulle, self.copie,
                            self.langue_env, self.langue_sw, *self.phases.values()) \
            and typ(self.tb, self.racine_bouton) == "BindingExpect" \
            and len(self.phases) == len(PHASES) and self.formats_ok() and self.donnees_ok()

    def donnees_ok(self):
        """les codes de Rythme écrits dans OPTIONS sont ceux du jeu ; chaque consigne a ses options"""
        attendu = {16: 7, 4: 5, 28: 4, 31: 4, 30: 5, 26: 4, 21: 5, 1: 5, 7: 3, 6: 2, **{n: 3 for n in BASCULES},
                   8: 3, 9: 5, 10: 5, 22: 3, 23: 2, 25: 3}
        return ([c for _, c, _ in OPTIONS] == [c for c, _ in self.options.get(CONSIGNE, [])]
                and all(len(self.options.get(n, [])) == m for n, m in attendu.items()))

    def formats_ok(self):
        """nos événements « copier » refont à l'octet près ceux des boutons de FM (const.Zero / const.One)"""
        boutons = {self.th.name(r): bytes(self.th.sd(r)["Events"]["m_bytes"]) for r in self.th.walk(self.segments)
                   if typ(self.th, r) == "SIButton"}
        return (boutons.get("combinedButton") == bytes(liste([copier("const.Zero", "possessionmode", 0)]))
                and boutons.get("inPossessionButton") == bytes(liste([copier("const.One", "possessionmode", 1)])))


# ---------- événements (format de FM, refait à l'octet près ; vérifié par Sources.formats_ok) ----------
def _bloc(b):
    return struct.pack("<i", len(b)) + b


def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def copier(source, destination, drapeau):
    """« copier la valeur de <source> dans <destination> » ; dernier octet utile : 0 pour const.Zero, 1 pour const.One
    (comme FM dans les cartes de chaleur)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([drapeau, 0])


def liste(contenus):
    """liste d'événements : [1,1,1,N] puis [1] + longueur + contenu pour chacun"""
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def deplacer(t, r, parent, index):
    """déplace l'élément r (un élément de FM) sous parent, au rang index"""
    ancien = t.parent[r]
    t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != r]
    t.elem(parent)["m_Children"].insert(index, {"rid": r})
    t.elem(r)["m_Parent"] = {"rid": parent}
    t.parent[r] = parent
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(parent)["m_Id"]


def regler_bouton(t, b, place, code):
    """la surcharge du bouton de FM : place envoyée, code de l'option, code comparé pour l'allumer"""
    ov = next((d for d in surcharges(t, b) if any(v.get("m_name") == "datatosend" for v in d.get("ValueVariables") or [])), None)
    if ov is None:
        return False
    for v in ov["ValueVariables"]:
        if v["m_name"] == "datatosend":
            dr = json.loads(v["m_scopeValue"]["m_serializedData"])
            dr["m_data"][1]["BindingPath"] = place
            v["m_scopeValue"]["m_serializedData"] = json.dumps(dr, separators=(",", ":"), ensure_ascii=False)
        elif v["m_name"] == "teaminstructionoptionid":
            v["m_scopeValue"]["m_serializedData"] = f"Int|{code}|"
    n = 0
    for f in ov.get("BindFunction") or []:
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if bytes(a[0]).endswith(b"Int32VisualArg"):
                a[1] = struct.pack("<i", code)
                n += 1
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return n == 1


def envoyer(cible, donnees, evenement):
    """contenu d'un événement « envoyer au moteur l'événement <n°> à <cible> avec <données> » (27,222,7,0), format de
    26.6 ; vérifié contre le bouton de FM dans regler_plat"""
    return bytes([27, 222, 7, 0, 1]) + _bloc(_texte(cible)) + _bloc(_texte(donnees)) + struct.pack("<I", evenement)


def regler_plat(t, b, place, code, cible=None, extra=None):
    """bouton de FM recopié à plat : place envoyée et code de l'option écrits dans SON data-to-send-setter (les mêmes
    trois valeurs que la surcharge du modèle inclus, voir regler_bouton). v16 : cible = n° de consigne écrit en dur
    (variable kinitoid) au lieu de teaminstructionid ; extra = (n° de consigne, place) : un 2e réglage (variables
    kinitoenvoi2 / kinitoid2), envoyé par le bouton APRÈS le premier (deux événements « 6vvH »).
    v18 : cible / extra[0] peuvent être un CHEMIN (texte) : la variable qui porte la vraie valeur de FM (voir
    Fab.retenir) ; un nombre écrit en dur ne marche pas (vu en jeu le 12/10 : plus aucun clic des dédoublements)"""
    s = first(t, lambda r: t.name(r) == "data-to-send-setter", b)
    if s is None:
        return False
    sd = t.sd(s)
    n = 0
    modele_dts = modele_int = None
    for v in sd.get("ValueVariables") or []:
        if v["m_name"] == "datatosend":
            dr = json.loads(v["m_scopeValue"]["m_serializedData"])
            dr["m_data"][1]["BindingPath"] = place
            if cible is not None:
                dr["m_data"][0]["BindingPath"] = cible if isinstance(cible, str) else "kinitoid"
            v["m_scopeValue"]["m_serializedData"] = json.dumps(dr, separators=(",", ":"), ensure_ascii=False)
            modele_dts = v
            n += 1
        elif v["m_name"] == "teaminstructionoptionid":
            v["m_scopeValue"]["m_serializedData"] = f"Int|{code}|"
            modele_int = v
            n += 1
    for f in sd.get("BindFunction") or []:
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if bytes(a[0]).endswith(b"Int32VisualArg"):
                a[1] = struct.pack("<i", code)
                n += 1
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    if n != 3:
        return False
    ajouts = []
    if cible is not None and not isinstance(cible, str):
        w = copy.deepcopy(modele_int)
        w["m_name"], w["m_scopeValue"]["m_serializedData"] = "kinitoid", f"Int|{cible}|"
        ajouts.append(w)
    if extra:
        n2, place2 = extra
        d2 = copy.deepcopy(modele_dts)
        dr = json.loads(d2["m_scopeValue"]["m_serializedData"])
        dr["m_data"][0]["BindingPath"] = n2 if isinstance(n2, str) else "kinitoid2"
        dr["m_data"][1]["BindingPath"] = place2
        d2["m_name"], d2["m_scopeValue"]["m_serializedData"] = "kinitoenvoi2", json.dumps(dr, separators=(",", ":"),
                                                                                          ensure_ascii=False)
        ajouts.append(d2)
        if not isinstance(n2, str):
            w = copy.deepcopy(modele_int)
            w["m_name"], w["m_scopeValue"]["m_serializedData"] = "kinitoid2", f"Int|{n2}|"
            ajouts.append(w)
        bouton = first(t, lambda r: typ(t, r) == "SIButton", b)
        ev = bytes(t.sd(bouton)["Events"]["m_bytes"])
        numero = struct.unpack("<I", ev[-4:])[0]
        if ev != bytes(liste([envoyer("tactic", "datatosend", numero)])):
            return False   # format du bouton de FM inattendu : rien d'écrit à moitié (l'appelant s'arrête)
        t.sd(bouton)["Events"]["m_bytes"] = liste([envoyer("tactic", "datatosend", numero),
                                                   envoyer("tactic", "kinitoenvoi2", numero)])
    sd["ValueVariables"] = (sd.get("ValueVariables") or []) + ajouts
    return True


def tasser_regles(t, n0):
    """garde les n0 premières règles de la feuille (celles du bloc) et, parmi les nôtres, seulement celles qu'un élément
    utilise encore ; renumérote les éléments"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    regles = t.styles.sh["m_Rules"]
    nouvelles, nouvel, vues = list(regles[:n0]), {i: i for i in range(n0)}, {}
    for i in range(n0, len(regles)):   # v6 : une règle identique à une autre des nôtres est partagée
        if i in utilisees:
            cle = json.dumps(regles[i], sort_keys=True)
            if cle not in vues:
                vues[cle] = len(nouvelles)
                nouvelles.append(regles[i])
            nouvel[i] = vues[cle]
    if len(nouvelles) == len(regles):
        return
    t.styles.sh["m_Rules"] = nouvelles
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    t.styles.changed = True


def construire(t, src):
    corps = first(t, lambda r: typ(t, r) == "SIScrollView" and t.name(r) == "Body")
    if corps is None or corps not in t.parent:
        return ["SIScrollView #Body (la zone des cartes) introuvable"]
    # v2 : rien n'est posé DANS #Body (v1 y plantait, cause réelle : les règles de style, voir v3) ; v4 : #Body va dans
    # l'interrupteur « Cartes / Terrain ». v3 : chaque élément copié d'un autre modèle a ses règles de style recopiées
    # (copy_from) : oubliées, le jeu plantait en recopiant l'arbre (InlineStyleAccess.SetInlineRule).
    # v8 : la rangée « Rythme » de l'essai (boutons de FM en modèle inclus) est remplacée par la tuile Rythme.
    zone = t.parent[corps]
    n0 = len(t.styles.sh["m_Rules"])   # règles du bloc avant nous (après retrait d'une ancienne version)
    fab = Fab(t, src)
    racine = fab.boite(zone, "terrain", index=t.children(zone).index(corps))
    t.sd(racine)["name"] = NOM   # repère de la version (« déjà appliqué »)
    erreur = bascule(t, src, zone, corps, racine, fab)
    if erreur:
        return [erreur]
    try:
        terrain(fab, racine)
    except (ValueError, KeyError, IndexError, StopIteration) as e:
        return [f"terrain : {e} (introuvable)"]
    tasser_regles(t, n0)
    return [f"bouton « {TEXTES_VUES[0]} / {TEXTES_VUES[1]} » en haut à droite ; "
            f"à l'ouverture : {'terrain' if VUE_DEPART else 'cartes de FM'}",
            f"terrain, avec le ballon : Relance, Avancée, 30 derniers mètres, puis {sum(map(len, TUILES))} tuiles ; "
            f"{fab.n} boutons ou cases ; codes et noms lus dans les données du jeu ; sans le ballon : les lignes, "
            f"le déclenchement du pressing, le piège et les centres, 3 tuiles",
            f"icônes à la taille de leur case : {len(fab.src.dessins)} dessins mesurés dans le jeu"]


def bascule(t, src, zone, corps, racine, fab):
    """v4 : variable VARIABLE, interrupteur [cartes de FM, terrain] et deux boutons segmentés dans l'en-tête ;
    v6 : le même composant déclare aussi les variables des noms de phases (PHASES)"""
    th = src.th
    # 1. la variable, déclarée par un composant du bloc (FM : « possessionmode » des cartes de chaleur)
    rang = sum(1 for k in t.children(zone) if t.elem(k).get("m_FullTypeName", "").endswith("Component"))
    var = t.clone(src.variable, zone, rang, src=th)
    recaler_parent(t, var)
    n = 0
    for p in t.elem(var).get("m_Properties") or []:
        if p.get("name") == "value-vars":
            p["value"] = ",".join([f"{{{VARIABLE}}}{{Int|{VUE_DEPART}|}}"] +
                                  [f"{{{nom}}}{{Int|{val}|}}" for _, nom, val in PHASES])   # virgules : comme FM
            n += 1
    d = copy.deepcopy(th.refs[src.variable_sd])
    d["rid"] = t.new_rid()
    dd = d["data"]
    dd["uxmlAssetId"] = t.elem(var)["m_Id"]
    if n != 1 or len(dd.get("ValueVariables") or []) != 1:
        return "variable des cartes de chaleur : forme inattendue (introuvable)"
    v0 = dd["ValueVariables"][0]
    for _, nom, val in PHASES:
        v = copy.deepcopy(v0)
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = nom, f"Int|{val}|"
        dd["ValueVariables"].append(v)
    v0["m_name"], v0["m_scopeValue"]["m_serializedData"] = VARIABLE, f"Int|{VUE_DEPART}|"
    t.refs[d["rid"]] = d
    t.tt["references"]["RefIds"].append(d)
    zs = t.sd(zone)
    zs.setdefault("m_components", []).append({"rid": d["rid"]})
    zs["m_components_UxmlAttributeFlags"] = 1
    # 2. l'interrupteur (celui de FM qui, dans ce bloc, choisit le texte « avec / sans le ballon »), sans ses textes
    modele = first(t, lambda r: typ(t, r) == "BindableSwitchElement" and t.name(r) == "possession-text-switch")
    if modele is None:
        return "interrupteur #possession-text-switch du bloc introuvable"
    sw = t.clone_shallow(modele, zone, t.children(zone).index(corps))
    s = t.sd(sw)
    s["name"], s["name_UxmlAttributeFlags"] = f"{PREFIXE}-vue", 1
    s["Binding"]["m_direct"]["Path"]["m_path"] = VARIABLE
    t.elem(sw)["m_Classes"] = ["flex-grow-class"]
    deplacer(t, corps, sw, 0)    # rang 0 : les cartes de FM
    deplacer(t, racine, sw, 1)   # rang 1 : notre terrain
    # 3. les deux boutons, à droite de l'en-tête (après un espace qui pousse)
    tete = first(t, lambda r: t.name(r) == "team-instruction-header")
    rangee = t.children(tete)[0] if tete is not None and t.children(tete) else None
    if rangee is None or "row-direction-normal" not in (t.elem(rangee).get("m_Classes") or []):
        return "rangée de l'en-tête #team-instruction-header introuvable"
    vide = t.clone_shallow(rangee, rangee)
    t.elem(vide)["m_Classes"], t.elem(vide)["m_RuleIndex"] = ["flex-grow-class"], -1
    t.sd(vide)["name"], t.sd(vide)["name_UxmlAttributeFlags"] = f"{PREFIXE}-espace", 1
    seg = t.clone(src.segments, rangee, src=th)
    t.styles.copy_from(th.styles, t, seg)
    t.sd(seg)["name"] = f"{PREFIXE}-boutons-vue"
    reglages = t.children(seg)
    if len(reglages) != 3 or any(typ(t, r) != "SIStyleSetter" for r in reglages):
        return "boutons segmentés des cartes de chaleur : forme inattendue (introuvable)"
    t.remove(reglages[1])   # le bouton du milieu
    for reglage, valeur, const, drapeau, mot, nom in (
            (reglages[0], 0, "const.Zero", 0, TEXTES_VUES[0], "cartes"),
            (reglages[2], 1, "const.One", 1, TEXTES_VUES[1], "terrain")):
        rs = t.sd(reglage)
        rs["name"] = f"{PREFIXE}-allume-{nom}"
        args = decode_args(rs["BindFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
        chemins = entiers = 0
        for a in args:
            if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]"):
                if bytes(a[1]) != bytes([1, 14]) + b"possessionmode":
                    return "réglage d'un bouton segmenté : chemin inattendu (introuvable)"
                a[1] = bytes([1, len(VARIABLE)]) + VARIABLE.encode()
                chemins += 1
            elif bytes(a[0]).endswith(b"Int32VisualArg"):
                a[1] = struct.pack("<i", valeur)
                entiers += 1
        if (chemins, entiers) != (1, 1):
            return "réglage d'un bouton segmenté : arguments inattendus (introuvable)"
        rs["BindFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        bouton = t.children(reglage)[0]
        bs = t.sd(bouton)
        bs["name"] = f"{PREFIXE}-bouton-{nom}"
        bs["Events"] = {"m_bytes": liste([copier(const, VARIABLE, drapeau)])}
        for k in list(t.children(bouton)):
            if t.name(k) == "controllers-keyboard-container":   # raccourci clavier de FM : pas le nôtre
                t.remove(k)
        texte = next((k for k in t.children(bouton) if typ(t, k) == "SIText"), None)
        if texte is None:
            return "texte d'un bouton segmenté introuvable"
        t.elem(texte)["m_Classes"] = [c for c in t.elem(texte)["m_Classes"] if c != "margin-right-global-gap-regular"]
        ts = t.sd(texte)
        ts["name"], ts["name_UxmlAttributeFlags"] = f"{PREFIXE}-texte-{nom}", 1
        ts.update(text=mot, text_UxmlAttributeFlags=1, DebugDisplay=mot)   # texte fixe (recette de 26.4)
        ts["TextBinding"]["m_kind"] = 0
        ts["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        fonction_vide(ts["TextBinding"]["m_visualFunction"])
        # v25 : le mot dans la langue du jeu (Kinito) : ce texte, recopié dans une variante par langue, à sa place
        rang_texte = t.children(bouton).index(texte)
        j = 0 if nom == "cartes" else 1

        def mot_(par, mots, texte=texte, nom=nom, j=j):
            c = t.clone_shallow(texte, par)
            fab.n += 1
            cs = t.sd(c)
            cs["name"] = f"{PREFIXE}-texte-{nom}-{fab.n}"
            cs.update(text=mots[j], DebugDisplay=mots[j])
        try:
            env = fab.selon_langue(bouton, f"vue-{nom}-langue", mot_, VUES_LANGUES, TEXTES_VUES, css={})
        except ValueError as e:
            return f"bouton « {mot} » : {e} (introuvable)"
        deplacer(t, env, bouton, rang_texte)
        t.remove(texte)
    return None


def retirer_essai(o):
    """retire notre enveloppe ; et la déclaration du modèle inclus si plus rien ne s'en sert"""
    bundle, obj, tt, t = o

    def ancetre_marque(r):
        p = t.parent.get(r)
        while p is not None:
            if t.name(p).startswith(PREFIXE):
                return True
            p = t.parent.get(p)
        return False
    # v4 : les cartes de FM (#Body) ressortent de notre interrupteur, à sa place ; puis la variable (composant sans
    # nom, reconnu à sa déclaration) et sa donnée dans la liste des composants du bloc
    for sw in [r for r in t.walk() if t.name(r) == f"{PREFIXE}-vue"]:
        for k in [k for k in t.children(sw) if typ(t, k) == "SIScrollView" and t.name(k) == "Body"]:
            deplacer(t, k, t.parent[sw], t.children(t.parent[sw]).index(sw))
    for r in list(t.walk()):
        e = t.elem(r)
        if e.get("m_FullTypeName") == "SI.Bindable.BindingVariablesComponent" and any(
                f"{{{VARIABLE}}}" in (p.get("value") or "") for p in e.get("m_Properties") or []):
            ps = t.sd(t.parent[r])
            partis = {c["rid"] for c in ps.get("m_components") or []
                      if ((t.refs.get(c["rid"]) or {}).get("data") or {}).get("uxmlAssetId") == e["m_Id"]}
            ps["m_components"] = [c for c in ps["m_components"] if c["rid"] not in partis]
            tt["references"]["RefIds"] = [x for x in tt["references"]["RefIds"] if x["rid"] not in partis]
            for p in partis:
                t.refs.pop(p, None)
            t.remove(r)
    racines = [r for r in marques(t) if r in t.parent and not ancetre_marque(r)]   # nos racines seulement
    for r in racines:
        t.remove(r)
    if not any(est_bouton(t, r) for r in t.walk()):
        tt["m_Usings"] = [u for u in tt.get("m_Usings") or [] if u.get("alias") != MODELE_BOUTON]
    # les règles de style ajoutées (v3) : feuille d'origine remise si plus aucune n'est utilisée, sinon retirées une à une
    orig = hp.original(bundle, obj)
    feuille = orig and hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if feuille is None:
        return
    n0 = len(feuille["m_Rules"])
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in tt["references"]["RefIds"] if r}
    if not any(i >= n0 for i in utilisees):
        t.styles.sh, t.styles.changed = feuille, True
        return
    regles = t.styles.sh["m_Rules"]
    garder = list(range(n0)) + [i for i in range(n0, len(regles)) if i in utilisees]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    t.styles.changed = True


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


# ---------- commandes ----------
def cmd_appliquer():
    o = ouvrir(BLOC)
    if o is None:
        print(f"[Kinito] Consignes (essai) : {BLOC} introuvable (renommé par une mise à jour ?), ignoré")
        return
    if any(o[3].name(r) == NOM for r in marques(o[3])):
        print("[Kinito] Consignes (essai) : déjà appliqué")
    else:
        src = Sources()
        if not src.ok():
            print("[Kinito] Consignes (essai) : morceaux de FM introuvables (fenêtres Progression / Courses de soutien), "
                  "rien enregistré")
            return
        retirer_essai(o)   # une ancienne version, s'il y en a une
        msgs = construire(o[3], src)
        for m in msgs:
            print(f"[Kinito] Consignes (essai) : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Consignes (essai) : rien enregistré")
            return
        enregistrer(*o)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
        autre = os.path.join(os.path.dirname(MARKER), AUTRE_MARQUEUR)   # v26 : l'autre version n'est plus active
        if os.path.exists(autre):
            os.remove(autre)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    o = ouvrir(BLOC)
    if o is None or not any(est_racine(o[3].name(r)) for r in marques(o[3])):   # v26 : seulement la nôtre
        print("rien à retirer")
        return
    retirer_essai(o)
    enregistrer(*o)
    nb.save_all()
    print(f"{BLOC} : essai « Rythme » retiré (le reste du bloc n'est pas touché)")


def cmd_etat():
    o = ouvrir(BLOC)
    if o is None:
        print(f"{BLOC} : introuvable")
    else:
        t = o[3]
        print(f"{BLOC} : " + (f"essai « Rythme » présent (à jour, v{VERSION})" if any(t.name(r) == NOM for r in marques(t))
                              else ("ANCIENNE version" if any(est_racine(t.name(r)) for r in marques(t))
                                    else "pas d'essai")))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("[Kinito] Consignes (essai) : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
