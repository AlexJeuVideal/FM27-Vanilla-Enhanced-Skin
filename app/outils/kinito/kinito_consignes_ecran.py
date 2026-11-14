"""[AJOUT KINITO] 26.13 v54 — la vue « Terrain » sur TOUT l'écran des consignes d'équipe (maquette 37, ESSAI).

Demande de Kinito (09/11/2026) : construire « EXACTEMENT comme la maquette » la maquette 37 (la 30 rangée par lui :
trois terrains en perspective dans leur stade, « Avec le ballon » à gauche, « Sans le ballon » à droite, une rangée
de cartes sous les terrains). Choix de Kinito : un ESSAI d'abord — l'écran entier dessiné, UNE consigne branchée
(En taclant, son logo qui suit l'option), pour voir en jeu ce qui n'est pas prouvé : un bouton de consigne posé dans
l'onglet (hors des blocs de FM), le dessin en perspective, ce que coûtent ~3 200 éléments.

Comment :
- le dessin vient de la maquette elle-même : `exporter-37.mjs` (dossier du chantier) l'ouvre dans Chrome, coupe les
  transformations, relève chaque boîte (place dans son parent, en unités de FM : l'écran 1080p est dessiné sur
  1680 unités), puis ses transformations (rotation, échelle, translation), son fond, son dégradé, ses bords et coins,
  son opacité, son débordement, ses textes (boîte du texte mesurée) et ses icônes (consigne, option). Le résultat est
  rangé, compressé, dans kinito_consignes_ecran_37.py (DONNEES) : rien n'est recopié à la main ;
- ici, chaque boîte devient un élément de FM placé en absolu (une boîte simple de notre bloc, un dégradé de FM
  SIGradient, un texte de FM SIText, une icône de FM par sa classe) ; les rotations et échelles sont celles d'Unity
  (prouvées en jeu par 26.22) ;
- l'écran se pose dans l'onglet (TacticalPlannerTeamInstructions), dans #Body, après la grille de FM, dans un
  interrupteur de FM sur la vue (kinitovue, déclarée par l'onglet depuis la v20) : rien en Tuiles (0) ni en FM24 (2),
  l'écran en Terrain (1). Il couvre tout l'onglet et prend les clics (les blocs de FM, dessous, ne les reçoivent pas) ;
- en-tête : « FM24 », « Tuiles », « Terrain » ont chacun un bouton de FM invisible par-dessus qui écrit la vue
  (comme les boutons de la v12) ; « Partir de zéro » n'est que dessiné dans l'essai ;
- En taclant (consigne 12) : l'enveloppe de consigne de FM (Fab.enveloppe), la carte dessinée UNE FOIS PAR OPTION
  (exportée ainsi par la maquette) et montrée selon l'option choisie (Fab.selon), trois boutons de consigne de FM
  invisibles sur les crans (Fab.option, nu) ;
- tailles du texte : l'essai est exporté en texte Petit (celui de Kinito) ; ABC Social grossit avec le réglage de FM
  (FontManager : TextScaling / 100), sa taille est donc écrite pour 100 ; ABC Social Condensed (police des titres
  thematic, mesurés fixes) est écrite telle quelle. À vérifier en jeu.

v56 (Kinito, 09/11, v55 vue en jeu : « tu as branché qu'une seule consigne ? », puis « ensuite tu branches ») : les
28 consignes branchées, et la colonne de droite rangée de bas en haut (maquette).
- les 21 cartes : comme En taclant, la carte dessinée une fois par option (exportée ainsi), des boutons de FM
  invisibles sur les crans ; un 2e clic sur l'option choisie remet l'option neutre (Fab.bascule, comme bouton_b de
  26.13 ; DEFAUTS, sauf la hauteur du pressing qui n'en a pas) ;
- les terrains : ce qui change avec une consigne est enveloppé dans la maquette (balise « dep », display: contents) ;
  l'export donne le contenu de chaque enveloppe pour chaque option (ou chaque paire d'options) ; ici, une enveloppe de
  consigne de FM et Fab.selon (imbriqués pour une paire), un groupe par niveau de peinture (z-index) de ses éléments ;
  ce qui ne change pas (zones et flèches éteintes, milieu du bloc) est dessiné une fois, l'allumé par-dessus ;
- les clics des terrains : un bouton de FM invisible sur chaque zone, pastille et bande de la maquette (data-i /
  data-o : bascule comme les cartes), la progression par Fab.etats (REGLES_PROGRESSION de 26.13), les courses de soutien
  par course_nu (base.course sans dessin : intérieur et extérieur du même côté s'échangent) ;
- l'accroche d'un texte est MESURÉE dans la maquette (exporter-37 : le texte élargi, la boîte de son parent figée :
  gauche, centre, droite) ; un texte qui remplit une boîte dessinée (bouton, pastille) y est centré. La v55 devinait le
  centre : « Avec le ballon » (aligné à gauche, mais par hasard au milieu de sa rangée) était centré, et plus large en
  jeu (gras réel de FM), il partait vers l'icône ;
- tout l'écran 8 unités plus bas (DECALAGE_HAUT : 9 px mesurés sur sa capture de la v55, en haut comme en bas).

v57 (Kinito, 10/11 : il choisit la maquette 53) : les données sont celles de la 53 (kinito_consignes_ecran_37.py garde
son nom) ; rien ne change ici. Nouveau dans le dessin, NON PROUVÉ en jeu : la pointe pleine des flèches, un cadre qui
coupe (overflow hidden), tourné ET écrasé (scale), autour d'un carré tourné de 45° ; le halo d'une pastille choisie
(un ::before de la maquette, devenu une boîte par l'export).

v58 (Kinito, 10/11, v57 vue en jeu : pointes, halos et icônes s'affichent ; mais les icônes mordaient sur le texte des
pastilles) : le GRAS de la police étroite est, dans FM, 15 à 20 % plus large que dans la maquette (8 textes mesurés sur
sa capture ; même hauteur ; la police normale, elle, a la même largeur). La maquette réserve maintenant cette largeur
(espacement de 0,064 em sur ses textes gras étroits, grasFM) ; ici rien ne change : l'espacement n'est pas écrit, le
jeu élargit lui-même.
"""
import base64
import bisect
import copy
import json
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kinito_consignes_essai as base  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, decode_args, encode_args  # noqa: E402

base.sm.PROPRIETES.setdefault("-unity-font-style", (65543, 7))   # StylePropertyId d'Unity 6 (comme 26.22)
base.sm.PROPRIETES.setdefault("align-content", (131072, 7))   # v67 : StylePropertyId.AlignContent (FM l'écrit ainsi)
SOURCE_DEGRADE = ("tile-figma-fixture-background-template", "background-gradient")   # comme 26.22
FONCTION_DEGRADE = "47578265f34902049a44904bda1f1db1"   # StaticSIGradientColours : [couleur début, couleur fin]
VUE_TUILES, VUE_TERRAIN, VUE_FM24 = 0, 1, 2   # valeurs de base.VARIABLE (kinitovue)
# ---------- v95 : la vue Terrain dans la LANGUE DU JEU (Kinito, 13/11 : « traduire dans les langues du jeu ») ----------
# Ses choix : la langue réglée dans FM, en direct ; un texte plus long que le français coupé avec « … » ; nos mots
# traduits par nous. Comment (voir chantier-consignes\TRADUCTION - consignes dans les langues du jeu.md) :
# - les noms de consigne et d'option (360 textes sur 418) : par leur N° DE TRADUCTION (m_nameTranslationID des données
#   ui-staticdataentries, lu à la pose) ; le jeu les écrit lui-même dans sa langue (liaison de traduction de FM, comme
#   la case « Ne plus afficher ce message » de la fenêtre de confirmation) : un seul élément par texte. L'export de la
#   maquette dit lequel est lequel (fm : ["n", consigne] / ["o", consigne, option]) ;
# - les autres (58) : une copie par langue, montrée par une classe de langue posée sur le conteneur de l'écran (un
#   réglage de FM par langue compare languagesetting.PropertyValue, comme v87) et nos règles CLASSE_MOT ;
# - chaque texte s'étend sur sa PLACE LIBRE mesurée dans la maquette (place), puis « … »
base.sm.PROPRIETES.setdefault("text-overflow", (196609, 7))   # StylePropertyId.TextOverflow (Unity 6 : Clip, Ellipsis)
SOURCE_TRADUIT = "GenericModalDialog"   # la case « Do not show this message again. » : un texte traduit par le jeu
FONCTION_TRADUIT = "eae2be944eee9e2449baef416111a087"   # le texte n° TranslationID, dans la langue du jeu
CHEMIN_LANGUE = "languagesetting.PropertyValue"   # la langue du jeu, sous le conteneur de tdd-messages-banner (v24)
CLASSE_LANGUE = "kinito-lg-"       # sur le conteneur de langue de l'écran, une par langue : kinito-lg-german…
CLASSE_MOT = "kinito-lt"           # un mot écrit dans une langue : caché, sauf sous sa classe de langue
CLASSE_MOT_DEFAUT = "kinito-ltd"   # le mot de secours (anglais) : montré seulement si la langue n'est pas connue
REPERE_LANGUE = 95.0               # nos règles de langue (REPERE_REGLE_ECRAN)
MARGE_ELLIPSE = 6    # un texte traduit : sa boîte = sa place libre, au moins sa largeur française + cette marge
LANGUES_JEU = [code for code, _ in base.COURSES_LANGUES]   # les valeurs de current_language (game_plugin.dll)
DEUX_LIGNES = {("Centrer de", "loin"): ("o", 18, 0), ("Jouer le ballon", "dans la surface"): ("o", 18, 2)}   # v58 :
#               deux lignes de la maquette ; traduit, le nom entier de l'option dans la boîte des deux lignes
MOTS_KINITO = {}   # nos mots par langue posés par kinito_consignes_essai_b (« Partir de zéro », « Tuiles »)
LIBRES_FM = {"Gauche": ("o", 30, 2), "Axiale": ("o", 30, 1), "Droite": ("o", 30, 3)}   # v59 : les noms sous les flèches
#               de la Progression, écrits en toutes lettres par la maquette : les options 2, 1 et 3 de la consigne 30
# v95 (traduction, Kinito 13/11 : « dans les langues du jeu ») : les MOTS DE FM de l'écran qui ne sont ni un nom de
# consigne ni un nom d'option, dans chaque langue du jeu (valeurs du réglage natif current_language, comme
# base.COURSES_LANGUES) : recopiés du fichier des langues de FM 27 (data\game_simulation\languages.fmf) PAR LEUR
# CLÉ, jamais retapés (Consignes 0x7da4d, Avec / Sans le ballon 0x9b81f / 0x9b81e, 30 derniers mètres 0x9b822,
# Relance 0x9b824 + Progression 0xa6aa9, Courses de soutien 0xa6a9d) ; czech et thai, absentes du fichier : l'anglais ;
# chinese (traditional) : le chinois simplifié (seule table chinoise du fichier)
MOTS_FM = {
    'Consignes': {
        'english': 'Instructions', 'english (us)': 'Instructions',
        'french': 'Consignes', 'german': 'Anweisungen',
        'italian': 'Istruzioni', 'spanish': 'Instrucciones',
        'spanish (latam)': 'Instrucciones', 'portuguese': 'Instruções',
        'portuguese (bra)': 'Instruções', 'dutch': 'Instructies',
        'danish': 'Instruktioner', 'norwegian': 'Instruksjoner',
        'swedish': 'Instruktioner', 'polish': 'Polecenia',
        'czech': 'Instructions', 'russian': 'Инструкции',
        'turkish': 'Talimatlar', 'greek': 'Οδηγίες',
        'indonesian': 'Instruksi', 'japanese': '指示',
        'korean': '지시 사항', 'chinese': '指\u200b令',
        'chinese (traditional)': '指\u200b令', 'thai': 'Instructions',
        'arabic': 'التعليمات',
    },
    'Avec le ballon': {
        'english': 'In Possession', 'english (us)': 'In Possession',
        'french': 'Avec le ballon', 'german': 'Mit Ball',
        'italian': 'In possesso', 'spanish': 'Con posesión',
        'spanish (latam)': 'Con posesión', 'portuguese': 'Com posse de bola',
        'portuguese (bra)': 'Com posse de bola', 'dutch': 'In balbezit',
        'danish': 'I boldbesiddelse', 'norwegian': 'Med ball',
        'swedish': 'Med boll', 'polish': 'Przy piłce',
        'czech': 'In Possession', 'russian': 'С мячом',
        'turkish': 'Topa Sahipken', 'greek': 'Κατοχή',
        'indonesian': 'Saat Menguasai Bola', 'japanese': 'ポゼッション時',
        'korean': '공 소유 시', 'chinese': '持球',
        'chinese (traditional)': '持球', 'thai': 'In Possession',
        'arabic': 'الاستحواذ',
    },
    'Sans le ballon': {
        'english': 'Out of Possession', 'english (us)': 'Out of Possession',
        'french': 'Sans le ballon', 'german': 'Ohne Ball',
        'italian': 'Non in possesso', 'spanish': 'Sin posesión',
        'spanish (latam)': 'Sin posesión', 'portuguese': 'Sem Posse de Bola',
        'portuguese (bra)': 'Sem Posse de Bola', 'dutch': 'Zonder balbezit',
        'danish': 'Uden boldbesiddelse', 'norwegian': 'Uten ball',
        'swedish': 'Utan boll', 'polish': 'Bez piłki',
        'czech': 'Out of Possession', 'russian': 'Без мяча',
        'turkish': 'Top Rakipteyken', 'greek': 'Χωρίς Κατοχή',
        'indonesian': 'Saat Tidak Menguasai Bola', 'japanese': '非ポゼッション時',
        'korean': '공 미소유 시', 'chinese': '无球阶段',
        'chinese (traditional)': '无球阶段', 'thai': 'Out of Possession',
        'arabic': 'عدم الاستحواذ',
    },
    '30 derniers mètres': {
        'english': 'Final Third', 'english (us)': 'Final Third',
        'french': '30 derniers mètres', 'german': 'Angriffsdrittel',
        'italian': 'Trequarti', 'spanish': 'Último tercio',
        'spanish (latam)': 'Último tercio', 'portuguese': 'Último terço',
        'portuguese (bra)': 'Último terço', 'dutch': 'Helft van de tegenstander',
        'danish': 'Sidste tredjedel', 'norwegian': 'Siste tredjedel',
        'swedish': 'Sista tredjedelen', 'polish': 'Na przedpolu bramki rywala',
        'czech': 'Final Third', 'russian': 'Последняя треть',
        'turkish': 'Üçüncü Bölge', 'greek': 'Επιθετικό Τρίτο',
        'indonesian': 'Sepertiga Akhir', 'japanese': 'アタッキングサード',
        'korean': '상대팀 진영', 'chinese': '前场进攻',
        'chinese (traditional)': '前场进攻', 'thai': 'Final Third',
        'arabic': 'الثلث الأخير',
    },
    'Relance · Progression': {
        'english': 'Buildup · Progress Through', 'english (us)': 'Buildup · Progress Through',
        'french': 'Relance · Progression', 'german': 'Aufbaudrittel · Aufbauspiel',
        'italian': 'Costruzione del gioco · Sviluppa gioco', 'spanish': 'Área de creación de oportunidades · Progresar por',
        'spanish (latam)': 'Área de creación de oportunidades · Avance', 'portuguese': 'Primeiro terço · Avançar por',
        'portuguese (bra)': 'Primeiro terço · Avançar por', 'dutch': 'Opbouw · Aanvallen',
        'danish': 'Opbygning · Løb gennem', 'norwegian': 'Oppbygning · Gå gjennom',
        'swedish': 'Uppbyggnad · Avancera genom', 'polish': 'Na przedpolu swojej bramki · Wejścia',
        'czech': 'Buildup · Progress Through', 'russian': 'Схема · Продвижение',
        'turkish': 'Oyun Kurma · Oynanacak Bölge', 'greek': 'Ανάπτυξη Από Τα Μετόπισθεν · Προώθηση',
        'indonesian': 'Build-Up · Progres Melalui', 'japanese': 'ディフェンシブサード · 攻撃',
        'korean': '빌드업 · 전진', 'chinese': '组织进攻 · 向前推进',
        'chinese (traditional)': '组织进攻 · 向前推进', 'thai': 'Buildup · Progress Through',
        'arabic': 'بناء الهجمات · الانطلاقات التقدمية من',
    },
    'Courses de soutien': {
        'english': 'Supporting Runs', 'english (us)': 'Supporting Runs',
        'french': 'Courses de soutien', 'german': 'Unterstützende Läufe',
        'italian': 'Movimenti a supporto', 'spanish': 'Carreras de apoyo',
        'spanish (latam)': 'Carreras de apoyo', 'portuguese': 'Apoiar Corridas com Bola',
        'portuguese (bra)': 'Apoiar Corridas com Bola', 'dutch': 'Overlappende runs',
        'danish': 'Støttende løb', 'norwegian': 'Støtteløp',
        'swedish': 'Understödjande löpningar', 'polish': 'Wejścia za piłką',
        'czech': 'Supporting Runs', 'russian': 'Поддержка в атаке',
        'turkish': 'Destek Koşuları', 'greek': 'Υποστηρικτικές Κινήσεις',
        'indonesian': 'Pergerakan Mendukung', 'japanese': 'サポートラン',
        'korean': '공격 가담', 'chinese': '支援跑动',
        'chinese (traditional)': '支援跑动', 'thai': 'Supporting Runs',
        'arabic': 'انطلاقات المساندة',
    },
}
# v95 : le texte anglais de secours de chaque nom de FM (consigne n, option n.k), écrit avec son n° de traduction :
# le jeu l'affiche si le n° ne se lisait pas (alors visible tout de suite dans une partie en français). Relevé par
# le texte français de la maquette dans le fichier des langues (1re clé) ; écarts de la maquette : à la main
ANGLAIS_FM = {
    'n1': 'Passing Directness', 'o1.0': 'Much Shorter', 'o1.1': 'Shorter',
    'o1.2': 'Standard', 'o1.3': 'More Direct', 'o1.4': 'Much More Direct',
    'n3': 'Attacking Transition', 'o3.0': 'Hold Shape', 'o3.1': 'Standard',
    'o3.2': 'Counter Attack', 'n4': 'Attacking Width', 'o4.0': 'Much Narrower',
    'o4.1': 'Narrower', 'o4.2': 'Standard', 'o4.3': 'Wider',
    'o4.4': 'Much Wider', 'n5': 'Creative Freedom', 'o5.0': 'More Disciplined',
    'o5.1': 'Balanced', 'o5.2': 'More Expressive', 'n6': 'Play For Set Pieces',
    'o6.0': 'Keep Ball in Play', 'o6.1': 'Play For Set Pieces', 'n7': 'Time Wasting',
    'o7.0': 'Less Often', 'o7.1': 'Standard', 'o7.2': 'More Often',
    'n8': 'Line Of Engagement', 'o8.0': 'Low Block', 'o8.1': 'Mid Block',
    'o8.2': 'High Press', 'n9': 'Defensive Line', 'o9.0': 'Much Lower',
    'o9.1': 'Lower', 'o9.2': 'Standard', 'o9.3': 'Higher',
    'o9.4': 'Much Higher', 'n10': 'Trigger Press', 'o10.0': 'Much Less Often',
    'o10.1': 'Less Often', 'o10.2': 'Standard', 'o10.3': 'More Often',
    'o10.4': 'Much More Often', 'n11': 'Defensive Transition', 'o11.0': 'Regroup',
    'o11.1': 'Standard', 'o11.2': 'Counter-Press', 'n12': 'Tackling',
    'o12.0': 'Stay On Feet', 'o12.1': 'Standard', 'o12.2': 'Get Stuck In',
    'n15': 'Defensive Line Behaviour', 'o15.0': 'Hold the Line', 'o15.1': 'Balanced',
    'o15.2': 'Drop Off', 'n16': 'GK Distribution', 'o16.0': 'Balanced',
    'o16.1': 'Centre-Backs', 'o16.2': 'Full-Backs', 'o16.3': 'Flanks',
    'o16.4': 'midfield playmaker', 'o16.5': 'Target Forward', 'o16.6': 'Over Opposition Defence',
    'n17': 'GK Distribution (Speed)', 'o17.0': 'Slow Pace Down', 'o17.1': 'Balanced',
    'o17.2': 'Distribute Quickly', 'n18': 'Patience', 'o18.0': 'Hit Early Crosses',
    'o18.1': 'Standard', 'o18.2': 'Work Ball Into Box', 'n19': 'Dribbles',
    'o19.0': 'Discourage', 'o19.1': 'Standard', 'o19.2': 'Encourage',
    'n20': 'Pass Reception', 'o20.0': 'Pass to Feet', 'o20.1': 'Standard',
    'o20.2': 'Pass Into Space', 'n21': 'Tempo', 'o21.0': 'Much Lower',
    'o21.1': 'Lower', 'o21.2': 'Standard', 'o21.3': 'Higher',
    'o21.4': 'Much Higher', 'n22': 'CROSS ENGAGEMENT', 'o22.0': 'Stop Crosses',
    'o22.1': 'Standard', 'o22.2': 'Invite Crosses', 'n23': 'Short Goalkeeper Distribution',
    'o23.0': 'No', 'o23.1': 'Yes', 'n24': 'Build-Up Strategy',
    'o24.0': 'Play Through Press', 'o24.1': 'Balanced', 'o24.2': 'Bypass Press',
    'n25': 'Pressing Trap', 'o25.0': 'Trap Inside', 'o25.1': 'Balanced',
    'o25.2': 'Trap Outside', 'n26': 'Crossing Style', 'o26.0': 'Balanced',
    'o26.1': 'Floated Crosses', 'o26.2': 'Whipped Crosses', 'o26.3': 'Low Crosses',
    'n27': 'long shots', 'o27.0': 'Discourage', 'o27.1': 'Standard',
    'o27.2': 'Encourage', 'n28': 'Supporting Runs', 'o28.0': 'Balanced',
    'o28.1': 'Left', 'o28.2': 'Right', 'o28.3': 'Both Flanks',
    'n29': 'Goal Kicks', 'o29.0': 'Short', 'o29.1': 'Mixed',
    'o29.2': 'Long', 'n30': 'Progress', 'o30.0': 'Balanced',
    'o30.1': 'Middle', 'o30.2': 'Left', 'o30.3': 'Right',
    'o30.4': 'Both Flanks', 'n31': 'Supporting Runs', 'o31.0': 'Balanced',
    'o31.1': 'Left', 'o31.2': 'Right', 'o31.3': 'Both Flanks',
}
BRANCHEES = None    # v56 : toutes les cartes qui ont leurs variantes (v54, v55 : (12,), En taclant seule)
SANS_RETOUR = {8}   # comme 26.13 : la hauteur du pressing n'a pas d'option neutre (pas de 2e clic qui y ramène)
DECALAGE_HAUT = 8   # v56 à v59 : l'écran posé 8 unités plus bas que le centre de #Body (sa capture de la v55 : tout 9 px
#                    trop haut ; 9 / 1,143 = 7,9 unités). v60 : PLUS LU (l'écran est calé en haut d'un défilement, voir poser)
PROGRESSION_MONTRE = {"G": 2, "A": 1, "D": 3}   # option montrée par chaque flèche (comme avancee_b de 26.13)
DEPASSE_BAS = 17    # v62 : la grille de tuiles de FM descend ~15 unités sous #Body (mesuré sur sa capture v61 hors match :
#                    bas de #Body à 1048 px, bas des tuiles à 1064 px, soit 707 et 721 unités) ; la vue Terrain descend
#                    d'autant (2 de plus, pour ne pas laisser voir un bout de tuile), hors match comme en match (en match
#                    le bas des tuiles touche la barre du match)
# v63 (Kinito, 10/11, grand écran : 2560 x 1440 en « Information Display » Small, ~2 470 x 1 220 unités pour la vue,
# l'écran de 1 624 x 722 laissait un grand vide ; il choisit la maquette A : le visualiseur de FM à gauche, notre écran
# agrandi à côté, des tuiles en bas — les tuiles viendront ensuite). En 1080p (hors match) : exactement la v62.
# v70 (Kinito, 10/11, v69 vue en 2560 x 1440 Moyen : « on peut pas juste agrandir en moyen, pour remplir un peu
# l'espace libre des côtés ? on laisse l'espace libre en bas si on ne peut pas remplir ») : 1,2 était un plafond choisi
# par nous ; l'écran grandit maintenant jusqu'à 1,3 (2 560 Moyen : ~1,24, la largeur pleine ; 3 440 Petit avec les tuiles
# à droite : ~1,28) et se cale EN HAUT de sa place (la place à ses pieds reste vide) : l'élément de FM ne règle que
# l'échelle (SIAspectRatioFitterCore::ScaleToParent n'écrit que style.scale, lu le 10/11), le point fixe de l'échelle
# est le nôtre (transform-origin : top). Là où l'écran était déjà plus petit que 1,2 (1080p, en match, 3 440 Grand),
# rien ne change
# v72 (Kinito, 11/11, v71 vue en 3440 Petit, vue large : « augmenter encore un poil la taille des consignes, pour ne
# pas avoir de marge aussi grande à côté de sans ballon / avec ballon, ni entre les tuiles et les consignes ») : 1,34
# (mesuré sur sa capture : ~40 libres sous l'écran, ~17 sous les tuiles ; la rangée de tuiles du dessous passe à 166 :
# 8 au-dessus, 10 au-dessous). Seule la vue large l'atteint (ailleurs l'écran est limité avant : 1080p, en match,
# 2 560 et 3 440 Moyen, 2 560 Petit)
AGRANDI = 1.34       # v63 à v69 : 1,2 ; v70, v71 : 1,3. L'écran est DESSINÉ AGRANDI fois plus grand ; l'élément de FM qui l'ajuste
#                    (SIAspectRatioFitter, mode 3 ScaleToFit) le RÉDUIT pour qu'il tienne et ne l'agrandit jamais
#                    (SIAspectRatioFitterCore::ScaleInside : min(largeur dispo / largeur, hauteur dispo / hauteur),
#                    plafonné à 1,0, lu dans GameAssembly.dll). En 1080p la place fait 720 de haut : 720 / 864 = 1 / 1,2,
#                    l'écran retombe pile à sa taille de la v62 ; en match (moins de hauteur) il rétrécit pour tenir en
#                    entier au lieu de défiler (choix de Kinito, 10/11)
MODELE_AJUSTE = ("RecruitmentAddTransferTargetCard", "CloseButtonAspectRatioFitter")   # comme cadre_proportions (v52)
MODE_SCALE_TO_FIT = 3   # SIAspectRatioFitterCore+Mode : 0 WidthControlsHeight, 1 HeightControlsWidth, 2 FitInParent
ID_ORIGINE = 327682     # v70 : StylePropertyId.TransformOrigin (FM l'écrit d'un mot : center, left, bottom ; lu le 10/11)
CELLULE, ECART = 66, 16   # la grille de FM (GridLayoutSettings, globalobjects : m_cellSize 66, m_spacing 16, en unités)
TROU = 6 * CELLULE + 6 * ECART   # 492 : le visualiseur de FM (6 colonnes de la grille, à gauche) et l'écart qui le suit.
#                    La rangée passe à la ligne : quand écran (1 624) + trou ne tiennent pas (1080p), le trou part à la
#                    ligne suivante, coupée : l'écran prend toute la largeur, comme en v62
# v64 (Kinito, 10/11, v63 vue en 2560 x 1440 Small : « il manque les tuiles, le reste c'est ok » ; l'entraînement
# individuel en bas à droite) : sous l'écran, une BANDE de tuiles de FM, COPIES de ses modèles de tuiles (incluses par
# leur GUID, comme les blocs de la page du club, club_page_bas), chacune sous un remappeur qui lui passe ce que la
# grille de l'onglet passe aux siennes (m_nameBindings de #TeamInstructionsTabGrid : team = Team, isonmainscreen =
# const.False ; « human » pour l'entraînement, comme la tuile des capitaines). Six colonnes de 4 cases (66 + 16), sur
# 4 rangées : la bande ne paraît que si elle tient sous l'écran (la vue passe à la ligne en colonne, coupée : en 1080p
# et en match en 1080p, rien) ; trop étroite, ses dernières colonnes passent à la ligne, coupées. L'entraînement
# individuel n'existe qu'en 2 x 4, 4 x 4 et 8 x 4 : il prend la 6e colonne entière (en bas à droite), les consignes
# adverses et l'entraînement partagent la 5e
TUILES = [   # colonnes ; (modèle de FM, GUID, rangées)
    [("DataHubTile_4x4", "3fa039d6dfb726040a44efaf073fe66c", 4)],                     # centre des données
    [("TeamOrOppositionReportTile_4x2", "d177033bd2926a440972ad50eefca137", 2,        # rapport prochain adversaire
      {"team": "Team.NextMatchOpponent"}),   # v65 : comme la grille (m_gridElementBindingData : team.NextMatchOpponent)
     ("SquadCaptainsTile_4x2", "598328d85a6bc42df85022db2db77954", 2)],               # capitaines
    [("SetPiecesTile_4x2", "9b8b51cdd59a440059d9690a102debe9", 2),                    # coups de pied arrêtés
     ("PenaltiesTile_4x2", "cb28efcb0992197428f2dcb657c18b61", 2)],                   # penalties
    [("TacticalEffectivenessTile_4x4", "a058093a5fd01644e932b96a21b1857b", 4)],       # efficacité tactique
    [("OppositionInstructionsTile_4x2", "6dfc1c4c3d48848189d4eee3a907cbf1", 2),       # consignes adverses
     ("TrainingTile_4x2", "0ac43ed68f31a8743afc71b6e5cf84d9", 2)],                    # entraînement
    [("IndividualTrainingTile_4x4", "01203d84ffbd8b1428230b7967874e45", 4)],          # entraînement individuel
]
# v66 : en vue FM24 (disposition miroir), les tuiles à droite de la grille plafonnée, une par une, dans l'ordre de la
# colonne de FM (rapport, centre des données, capitaines, CPA, penalties, consignes adverses), puis les nôtres
# v67 (Kinito, 10/11, v66 vue en 2560 Small : « problème de taille sur les tuiles de droite, mais dans le bon sens ») : la
# 2e colonne passait coupée au bord de l'écran (~566 de place, deux colonnes en demandent 648). Les colonnes sont
# maintenant FIXÉES (celle de FM, puis la nôtre) et ne paraissent qu'ENTIÈRES ; dans chacune, une tuile qui ne tient
# pas en hauteur part dans une colonne cachée au lieu d'être coupée en bas
# v70 (Kinito, 10/11, v69 vue en 3440 Petit : « on ne peut pas avoir plus de tuiles à droite ? ») : la 2e colonne ne
# paraissait pas (l'intérieur plafonné pile à deux colonnes : un arrondi la faisait passer à la ligne) et la 1re (6
# tuiles, 1 124 de haut avec leurs écarts) perdait sa dernière en 3 440 (moins haut qu'en 2 560 : ~1 133 pour la vue
# contre ~1 219, mesuré sur ses captures). Les neuf tuiles en deux colonnes égales (964 et 968 avec leurs écarts)
# tiennent en 2 560 comme en 3 440 Petit. Les mêmes, dans le même ordre, à droite de la vue Terrain quand elle a la place
# (TUILES_DROITE)
# v71 (Kinito, 10/11, v70 vue en jeu, 3 440 Petit : « une seule colonne ; consignes particulières tout en haut, on
# descend les autres d'un cran » ; efficacité, entraînement et entraînement individuel ne sont plus en vue FM24) : une
# colonne de six (1 124 de haut avec leurs écarts : elle tient en 3 440 Petit, ~1 133 ; plus bas, les dernières se
# cachent)
TUILES24 = [[TUILES[4][0], TUILES[1][0], TUILES[0][0], TUILES[1][1], TUILES[2][0], TUILES[2][1]]]
# ce que la grille passe à ses tuiles (TacticalPlannerTeamInstructions : m_nameBindings) ; les types sont ceux que les
# tuiles attendent (BindingExpect) ; « human » comme la tuile des capitaines (game.GameCurrentManager)
PASSAGES_TUILES = [("team", "Team", 1145176088), ("isonmainscreen", "const.False", 0),
                   ("human", "game.GameCurrentManager", 1145176065)]
MODELE_REMAPPEUR = "DataHubTile_4x4"   # un BindingRemapper de FM (sa liste de correspondances est remplacée)
INSTANCE_ONGLET = "TacticalPlannerTeamInstructionsHeaderSimplified"   # un modèle inclus de l'onglet (recopié vide)
RANGEE = lambda n: n * CELLULE + (n - 1) * ECART   # noqa: E731  (2 : 148 ; 4 : 312)
BANDE = ECART + RANGEE(4)                   # 328 : l'écart sous l'écran et les 4 rangées
# v65 (sa capture de la v64 en 2560 Small : la 6e colonne passait à la ligne) : le cadre n'y fait que ~1 944 dedans
# (mesuré sur le bloc du terrain de FM, 476 unités = 283 px de capture), pas 1 960 : 6 x 312 + 5 x 16 = 1 952 ne
# tenait pas. Colonnes de 304, écart de 12 : 1 884
COLONNE, ECART_TUILES = 304, 12
# v70 : la bande du bas ne paraît que si la vue est assez haute pour la zone de l'écran (BASE_ZONE) ET elle : 2 560
# Petit (~1 219) oui, 3 440 Petit (~1 133) non — l'écran y prend toute la hauteur. (v70 : et deux colonnes de tuiles à
# droite du cadre en 3 440 Petit ; vues en jeu : les tuiles de FM, sous la vue, se voyaient entre les nôtres — « en
# double » — et la 2e colonne manquait (pile la place, un arrondi). Remplacées en v71, voir LARGE_ECRAN)
# v71 (Kinito, 10/11, v70 vue en 3440 Petit : « dispositif — consignes + 4 tuiles sous les consignes — visualiseur
# terrain », « et la tuile data hub sous le dispositif ») : quand la vue est LARGE (au moins LARGE_ECRAN pour le cadre,
# plus le visualiseur à gauche et un autre à droite : ~2 931 ; 3 440 Petit ~3 199 oui, 3 440 Moyen ~2 613 et moins non),
# de gauche à droite : le terrain de Positionnement (Avec / Sans) et le centre des données dessous, par-dessus la place
# du visualiseur de FM | l'écran et, dessous, rapport, capitaines, CPA, penalties | une COPIE du bloc visualiseur de FM
# (son modèle inclus par son GUID : FM pose toujours le sien à gauche). Comment la vue « sait » qu'elle est large :
# - à droite du cadre, la copie du visualiseur est dans une rangée qui passe à la ligne avec lui (dessous, coupée,
#   quand le cadre n'a pas LARGE_ECRAN à côté) ;
# - à gauche, un FILET (1 unité) passe à la ligne au même moment (même largeur demandée) ; le terrain de Positionnement
#   et le centre des données sont posés à partir de lui, en absolu, sur la place du visualiseur de FM (qu'ils couvrent) ;
# - dessous, une rangée de toute la largeur du cadre garde les quatre tuiles derrière un repère vide : elles passent à la
#   ligne (coupées) sous la même largeur.
# Sur un écran à la fois très large et très haut (4K en Petit), la bande du bas resterait aussi (non vu)
LARGE_ECRAN = 1946   # le cadre de la vue large : l'écran à 1,2 (1 622 x 1,2)
BASE_LARGE = LARGE_ECRAN + TROU   # 2 438 : le cadre et la copie du visualiseur
FILET = 1
# v72 (Kinito, 11/11 : « ajouter les consignes particulières en bas, à gauche de rapport prochain adversaire »)
BANDE4 = [TUILES[4][0], TUILES[1][0], TUILES[1][1], TUILES[2][0], TUILES[2][1],   # + consignes adverses en tête
          TUILES[4][1]]   # v76 (Kinito, 3 440 Petit : « une tuile de plus, entraînement ») : six (1 884 sur 1 946)
VISUALISEUR = ("TacticalPlannerTeamInstructionsPitchBlock", "40ee2527178f425d956e5d2e8f8f89cb")
BASE_ZONE = 830      # v63 à v69 : 722 ; la bande (347) reste dessous si la vue fait au moins 1 177 (milieu entre 1 133
#                      et 1 219, les deux mesurés) ; plus courte que la zone (1080p, en match), la zone prend tout
TAILLE_TEXTE = 0.85  # la taille du texte de l'export (Petit)
POLICE_FIXE = "ABC Social Condensed"   # écrite à sa taille exacte (voir CLASSES_POLICE)
# v55 (mesuré sur la capture de Kinito de la v54 contre la maquette, mêmes textes de FM au pixel près) : « thematic »
# n'est PAS la police étroite de la maquette mais la police d'affichage de FM (titres, menus) : 9 à 20 % plus large et
# plus haute, d'où les textes coupés. FM a la vraie : la famille « condensed » (--typography-family-condensed), classes
# condensed-sm-regular / -strong. ABC Social (body-sm) : même hauteur que la maquette, 2 à 9 % plus étroite (le moteur
# de texte d'Unity), rien de coupé. Que FM réduise ou non la police « condensed » avec la taille du texte n'est pas
# mesuré : écrite à sa taille exacte, au pire plus petite, jamais coupée (à mesurer sur la prochaine capture)
CLASSES_POLICE = {"ABC Social Condensed": "condensed-sm-regular", "ABC Social": "body-sm"}
HAUT_CLIC = 18       # hauteur de la zone de clic d'un cran (la piste de la maquette fait 7 unités)
MARGE_TEXTE = 40     # un texte sur une ligne : sa boîte est élargie d'autant (les mesures d'Unity ≠ celles de Chrome)


def nom_racine(version):
    return f"{base.PREFIXE}-ecran-v{version}"


def est_racine(nom):
    return nom.startswith(f"{base.PREFIXE}-ecran-v")


def donnees():
    """le dessin, lu dans kinito_consignes_ecran_37.py À CÔTÉ DE CE FICHIER (v55 : un « import » le prenait au premier
    dossier du chemin de Python, au banc celui de l'app d'Alex, qui avait encore les données de la v54)"""
    import importlib.util
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kinito_consignes_ecran_37.py")
    spec = importlib.util.spec_from_file_location("kinito_consignes_ecran_37_donnees", chemin)
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    return json.loads(zlib.decompress(base64.b64decode(d.DONNEES)).decode("utf-8"))


# ---------- v95 : la langue du jeu ----------
def slug(code):
    """« english (us) » -> « english-us » (un nom de classe)"""
    return code.replace(" (", "-").replace(")", "").replace(" ", "-")


def majuscules(s, code):
    """les capitales d'un mot dans sa langue (la maquette écrit certains titres en capitales) : le i pointé du turc,
    les capitales grecques sans accent"""
    if code == "turkish":
        return s.replace("i", "İ").replace("ı", "I").upper()
    if code == "greek":
        import unicodedata
        return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", s.upper())
                                                    if c not in "́͂"))
    return s.upper()


def mots_langues():
    """{texte français de la maquette : {langue du jeu : texte}} : les mots de FM (MOTS_FM), les nôtres (base), et ceux
    que pose kinito_consignes_essai_b (MOTS_KINITO). Les courses de soutien intérieures / extérieures (noms de Kinito,
    la maquette) : ailleurs qu'en français, le nom de FM et notre mot entre parenthèses"""
    d = {k: dict(v) for k, v in MOTS_FM.items()}
    d["Extérieur"] = {lg: m[0] for lg, m in base.COURSES_LANGUES}
    d["Intérieur"] = {lg: m[1] for lg, m in base.COURSES_LANGUES}
    d["Terrain"] = {lg: m[1] for lg, m in base.VUES_LANGUES}
    soutien = MOTS_FM["Courses de soutien"]
    for fr, rang in (("Courses de soutien intérieures", 1), ("Courses de soutien extérieures", 0)):
        d[fr] = {lg: fr if lg == "french" else f"{soutien[lg]} ({m[rang]})" for lg, m in base.COURSES_LANGUES}
    d.update({k: dict(v) for k, v in MOTS_KINITO.items()})
    return d


def ids_traduction():
    """{n° de consigne : (n° de traduction de son nom, [n° de traduction de chaque option, dans l'ordre du jeu])},
    lus dans les données du jeu (ui-staticdataentries, comme base.options_consignes)"""
    import UnityPy
    env = UnityPy.load(os.path.join(base.chemin_jeu.AA, "ui-staticdataentries_assets_all.bundle"))
    out = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            d = o.read_typetree()
        except Exception:
            continue
        if "m_instructionOptionEntries" in d and "m_instructionID" in d:
            out[d["m_instructionID"]] = (d["m_nameTranslationID"]["GameID"],
                                         [e["m_nameTranslationID"]["GameID"] for e in d["m_instructionOptionEntries"]])
    return out


def texte_arg(s):
    b = s.encode("utf-8")
    if len(b) > 127:
        raise ValueError(f"texte trop long : {s}")
    return bytes([1, len(b)]) + b


# ---------- accélérer l'arbre (3 200 éléments : la recherche linéaire d'Unity Tree prenait des minutes) ----------
def accelerer(t):
    """new_rid : un compteur au lieu de max() à chaque appel ; Styles._index : un dictionnaire des valeurs déjà
    rangées au lieu de « in » + index() sur des listes de milliers de dimensions. Mêmes résultats"""
    prochain = [max(t.refs) + 1]

    def new_rid():
        r = prochain[0]
        while r in t.refs:
            r += 1
        prochain[0] = r + 1
        t.refs[r] = None
        return r
    t.new_rid = new_rid
    st = t.styles
    if getattr(st, "_kinito_cache", None) is None:
        tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
        cache = {}   # nom de table -> {valeur (texte JSON) : rang}, lu une fois ; seule cette fonction y ajoute ensuite

        def index(typ_, value):
            if typ_ == 1:
                return int(value)
            nom = tables[typ_]
            table = st.sh.setdefault(nom, [])
            if typ_ == 3 and not isinstance(value, dict):
                value = {"unit": 1, "value": float(value)}
            elif typ_ == 4 and not isinstance(value, dict):
                value = dict(zip("rgba", (float(v) for v in value)))
            elif typ_ == 2:
                value = float(value)
            c = cache.get(nom)
            if c is None or c.get("__taille") != len(table):   # lue (ou relue si quelqu'un l'a changée sans nous)
                c = {}
                for i, v in enumerate(table):
                    c.setdefault(json.dumps(v, sort_keys=True), i)
                cache[nom] = c
            k = json.dumps(value, sort_keys=True)
            if k not in c:
                table.append(value)
                c[k] = len(table) - 1
            c["__taille"] = len(table)
            return c[k]
        st._index = index
        st._kinito_cache = cache


# ---------- les sources de FM ----------
class SourcesEcran:
    def __init__(self, src, tb):
        self.src, self.tb = src, tb
        self.proto = first(tb, lambda r: tb.name(r) == "team-instruction-header")   # boîte simple de notre bloc
        self.inter = first(tb, lambda r: typ(tb, r) == "BindableSwitchElement" and tb.name(r) == "possession-text-switch")
        d = ouvrir(SOURCE_DEGRADE[0], depart_original=True)
        self.td = d[3] if d else None
        self.degrade = self.td and first(self.td, lambda r: self.td.name(r) == SOURCE_DEGRADE[1]
                                         and typ(self.td, r).endswith("SIGradient"))
        th = src.th
        self.bouton = th and src.segments is not None and first(th, lambda r: typ(th, r) == "SIButton", src.segments)
        # v63 : l'élément de FM qui ajuste l'écran à la place (v60 à v62 : le défilement SIScrollView #Body du bloc)
        o = ouvrir(MODELE_AJUSTE[0], depart_original=True)
        self.ta = o[3] if o else None
        self.ajuste = self.ta and first(self.ta, lambda r: self.ta.name(r) == MODELE_AJUSTE[1]
                                        and typ(self.ta, r) == "SIAspectRatioFitter")
        # v64 : le remappeur de FM qu'on recopie au-dessus de chaque tuile
        o = ouvrir(MODELE_REMAPPEUR, depart_original=True)
        self.tr = o[3] if o else None
        self.remap = self.tr and first(self.tr, lambda r: typ(self.tr, r) == "BindingRemapper"
                                       and (self.tr.sd(r).get("Mappings") or []))
        # v95 : la liaison de traduction de FM (un texte n° TranslationID dans la langue du jeu) et les n° des noms
        o = ouvrir(SOURCE_TRADUIT, depart_original=True)
        tf = o[3] if o else None
        traduit = tf and first(tf, lambda r: typ(tf, r) == "SIText" and (
            ((tf.sd(r).get("TextBinding") or {}).get("m_visualFunction") or {}).get("m_target") or {}).get(
            "m_guid") == FONCTION_TRADUIT)
        self.liaison_traduite = copy.deepcopy(tf.sd(traduit)["TextBinding"]) if traduit else None
        self.ids = ids_traduction()

    def manque(self):
        out = []
        lt = self.liaison_traduite
        args = decode_args(lt["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]) if lt else []
        if lt is None or lt.get("m_kind") != 2 or len(args) != 1 or not bytes(args[0][0]).endswith(
                b"[SI.Translation.TranslationID]"):
            out.append(f"texte traduit par le jeu ({SOURCE_TRADUIT}) : forme inattendue")
        if any(n not in self.ids for n in base.DEFAUTS):
            out.append("n° de traduction des consignes (ui-staticdataentries)")
        s = self.src
        if None in (getattr(s, "langue_env", None), getattr(s, "tg", None)) or REGLAGE_TEXTE is None:
            out.append("conteneur de la langue du jeu (tdd-messages-banner) ou réglage de classe")
        if self.proto is None or self.inter is None:
            out.append("boîte ou interrupteur de notre bloc")
        if self.degrade is None:
            out.append(f"dégradé de FM ({SOURCE_DEGRADE[0]})")
        else:
            f = self.td.sd(self.degrade).get("BindGradientFunc") or {}
            args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"]) if f else []
            if (f.get("m_target") or {}).get("m_guid") != FONCTION_DEGRADE or len(args) != 2 or any(
                    not bytes(a[0]).endswith(b"ColorVisualArg") or len(bytes(a[1])) != 16 for a in args):
                out.append("dégradé de FM : forme inattendue")
        if not self.bouton:
            out.append("bouton de FM (boutons segmentés des cartes de chaleur)")
        if self.ajuste is None:
            out.append(f"ajustement de FM ({MODELE_AJUSTE[0]} : {MODELE_AJUSTE[1]})")
        elif not self.ta.sd(self.ajuste).get("AspectMode_UxmlAttributeFlags"):
            out.append(f"ajustement de FM ({MODELE_AJUSTE[1]}) : réglages inattendus")
        if self.remap is None:
            out.append(f"remappeur de FM ({MODELE_REMAPPEUR})")
        else:
            m = (self.tr.sd(self.remap).get("Mappings") or [{}])[0]
            if set(m) != {"m_serialisedType", "from", "to", "type"}:
                out.append(f"remappeur de FM ({MODELE_REMAPPEUR}) : forme inattendue")
        if self.src.titre is None:
            out.append("texte de FM (fenêtre Progression)")
        return out


# ---------- l'écran ----------
class Ecran:
    def __init__(self, t, src, se, data):
        self.t, self.src, self.se, self.d = t, src, se, data
        self.n = 0
        self.boutons_vue = []   # (x, y, w, h, valeur) des boutons de l'en-tête, en unités de l'écran
        self.alertes = []
        self.n_deps = 0         # v56 : groupes d'enveloppes posés
        self.clics = []         # v56 : (x, y, w, h, données) des éléments cliquables des terrains
        self.n_clics = 0
        self.n_cartes = 0
        self.mots = mots_langues()   # v95
        self.n_traduits = self.n_mots = self.n_fixes = self.n_vues_dans = self.n_survols = 0
        fab = base.Fab.__new__(base.Fab)
        fab.t, fab.src, fab.n, fab.defile = t, src, 0, None
        self.fab = fab

    # -- éléments simples --
    def seul(self, ts, rid, parent, nom=None, index=None):
        """un élément de FM recopié SEUL (sans enfants, composants, surcharges, classes ni règle), sans clics"""
        t = self.t
        r = t.clone(rid, parent, index, src=ts)
        base.recaler_parent(t, r)
        for k in list(t.children(r)):
            t.remove(k)
        sd = t.sd(r)
        if sd.get("m_components"):
            partis = {c["rid"] for c in sd["m_components"]}
            t.tt["references"]["RefIds"] = [x for x in t.tt["references"]["RefIds"] if x["rid"] not in partis]
            for p in partis:
                t.refs.pop(p, None)
            sd["m_components"] = []
        e = t.elem(r)
        if e.get("m_SerializedDataOverride"):
            e["m_SerializedDataOverride"] = []
        e["m_Classes"], e["m_RuleIndex"] = [], -1
        if nom:
            sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1
        else:
            sd["name"], sd["name_UxmlAttributeFlags"] = "", 0
        self.sans_clic(r)
        self.n += 1
        return r

    def sans_clic(self, r):
        sd = self.t.sd(r)
        sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1   # PickingMode.Ignore

    def avec_clic(self, r):
        sd = self.t.sd(r)
        sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 0, 1   # PickingMode.Position

    def boite(self, parent, css, nom=None, index=None):
        t = self.t
        r = t.clone_shallow(self.fab.proto, parent, index)
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
        sd = t.sd(r)
        sd["name"], sd["name_UxmlAttributeFlags"] = (nom, 1) if nom else ("", 0)
        self.sans_clic(r)
        if css:
            t.styles.style(t, r, css)
        self.n += 1
        return r

    # -- traductions maquette -> style d'Unity --
    @staticmethod
    def couleur(c):
        return (c[0] / 255, c[1] / 255, c[2] / 255, float(c[3]))

    def place(self, n, dx=0.0, dy=0.0):
        tr = n.get("tr") or {}
        css = {"position": "absolute", "left": round(n["x"] + tr.get("tx", 0.0) + dx, 2),
               "top": round(n["y"] + tr.get("ty", 0.0) + dy, 2), "width": n["w"], "height": n["h"]}
        return css

    def css_boite(self, n):
        css = self.place(n)
        if n.get("bg"):
            css["background-color"] = self.couleur(n["bg"])
        if n.get("bw"):
            for cote, w, c in zip(("top", "right", "bottom", "left"), n["bw"], n["bc"]):
                if w > 0 and c:
                    css[f"border-{cote}-width"] = w
                    css[f"border-{cote}-color"] = self.couleur(c)
        if n.get("rad"):
            for coin, v in zip(("top-left", "top-right", "bottom-right", "bottom-left"), n["rad"]):
                if v > 0:
                    css[f"border-{coin}-radius"] = v
        if n.get("op") is not None:
            css["opacity"] = n["op"]
        # v55 : une boîte qui ne contient que du texte ne le coupe plus (un texte un peu plus large dans le jeu que dans
        # Chrome dépasse de quelques points au lieu d'être rogné)
        if n.get("ovf") and not all(k["t"] == "#text" for k in n.get("k") or []):
            css["overflow"] = "hidden"
        tr = n.get("tr") or {}
        if abs(tr.get("rot", 0.0)) > 0.01:
            css["rotate"] = {"unit": 5, "value": round(tr["rot"], 3)}
        return css

    def transformer(self, r, n):
        """l'échelle (deux nombres, comme FM) ; l'origine des transformations doit être le centre (celle d'Unity)"""
        tr = n.get("tr") or {}
        if not tr:
            return
        o = tr.get("origine", "")
        try:
            ox, oy = (float(v.replace("px", "")) for v in o.split()[:2])
            if abs(ox - n["w"] / 2) > 0.6 or abs(oy - n["h"] / 2) > 0.6:
                self.alertes.append(f"origine de transformation hors du centre ({o}, {n['w']} x {n['h']})")
        except ValueError:
            pass
        if abs(tr.get("sx", 1) - 1) > 1e-3 or abs(tr.get("sy", 1) - 1) > 1e-3:
            self.fab.style_brut(r, [(327681, [(2, round(tr["sx"], 4)), (2, round(tr["sy"], 4))])])

    def degrade(self, parent, n):
        g = n["deg"]
        if len(g.get("c") or []) != 2:
            self.alertes.append(f"dégradé à {len(g.get('c') or [])} couleurs ignoré")
            return
        se, t = self.se, self.t
        r = self.seul(se.td, se.degrade, parent)
        sd = t.sd(r)
        f = sd.get("BindGradientFunc") or {}
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        args[0][1], args[1][1] = (struct.pack("<4f", *self.couleur(c)) for c in g["c"])
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        sd["GradientDirection"], sd["GradientDirection_UxmlAttributeFlags"] = 0, 1   # TopToBottom
        w, h = n["w"], n["h"]
        bl = (n.get("bw") or [0, 0, 0, 0])
        iw, ih = w - bl[1] - bl[3], h - bl[0] - bl[2]   # dans les bords (une boîte en absolu se pose dans les bords)
        rad = n.get("rad")
        if g["ang"] in (180, 0):
            css = {"position": "absolute", "left": 0, "top": 0, "width": iw, "height": ih}
            if g["ang"] == 0:
                css["rotate"] = {"unit": 5, "value": 180.0}
        elif g["ang"] in (90, 270):   # un dégradé de haut en bas tourné d'un quart de tour
            css = {"position": "absolute", "left": (iw - ih) / 2, "top": (ih - iw) / 2, "width": ih, "height": iw,
                   "rotate": {"unit": 5, "value": -90.0 if g["ang"] == 90 else 90.0}}
        else:
            self.alertes.append(f"dégradé à {g['ang']}° ignoré")
            t.remove(r)
            return
        if rad and max(rad) > 0:
            v = min(max(rad), iw / 2, ih / 2)
            for coin in ("top-left", "top-right", "bottom-right", "bottom-left"):
                css[f"border-{coin}-radius"] = v
        t.styles.style(t, r, css)

    @staticmethod
    def ancrage(n, pn, gpn):
        """où le texte s'accroche (gauche, centre, droite) : l'alignement de la maquette (text-align) ; un texte aligné
        au début dans une boîte à sa largeur, elle-même CENTRÉE dans son parent (pastilles, badges), est centré.
        v55 (Kinito, vu en jeu : textes coupés à gauche, nom et choix d'une carte pas alignés) : la v54 devinait le
        centre d'après la place du texte, et prenait pour centrés tous les textes aussi larges que leur boîte (noms et
        choix des cartes) : un texte plus large dans le jeu débordait des deux côtés, et la boîte (overflow hidden)
        coupait sa gauche"""
        f = n["f"]
        al = f.get("al") or "start"
        if al in ("center", "-webkit-center"):
            return "centre"
        if al in ("right", "end", "-webkit-right"):
            return "droite"
        bw, _ = f["boite"]
        remplit = abs(n["w"] - (bw - f["pad"][0] - f["pad"][1])) < 1.0
        # v56 : un texte qui remplit une boîte DESSINÉE (bouton, pastille : fond, bord ou dégradé) y est centré : la
        # boîte garde sa taille dans le jeu, ses marges restent égales
        if remplit and pn is not None and (pn.get("bg") or pn.get("bw") or pn.get("deg")):
            return "centre"
        # v56 : sinon, l'accroche mesurée dans la maquette (le texte élargi, la boîte de son parent figée)
        anc = n.get("anc")
        if anc in ("g", "c", "d"):
            return {"g": "gauche", "c": "centre", "d": "droite"}[anc]
        if anc == "?":
            return "gauche"
        if pn is not None and gpn is not None:   # (export d'avant la v56 : sans mesure, la règle de la v55)
            bw, _ = f["boite"]
            if abs(n["w"] - (bw - f["pad"][0] - f["pad"][1])) < 1.0:   # le texte remplit sa boîte
                gbl = gpn.get("bw") or [0, 0, 0, 0]
                gw = gpn["w"] - gbl[1] - gbl[3]
                if pn["x"] > 1.5 and abs(pn["x"] + pn["w"] / 2 - gw / 2) < 1.5:
                    return "centre"
        return "gauche"

    def texte(self, parent, n, pn=None, gpn=None):
        """v95 : un texte de la maquette, dans la langue du jeu : un mot de MOTS (une copie par langue), un nom de FM
        (fm : par son n° de traduction, le jeu l'écrit), sinon tel quel (FM24)"""
        mots = self.mots.get(n["txt"])
        if mots:
            return self.texte_langues(parent, n, pn, gpn, mots)
        fm = n.get("fm") or LIBRES_FM.get(n["txt"])
        if fm:
            return self.texte_un(parent, n, pn, gpn, fm=list(fm))
        self.n_fixes += 1
        return self.texte_un(parent, n, pn, gpn)

    def texte_langues(self, parent, n, pn, gpn, mots):
        """v95 : une copie du texte par mot différent ; chacune porte la classe des langues qui l'écrivent ainsi
        (montrée sous la classe de langue du conteneur, voir regles_langues), plus le mot de secours (anglais)"""
        maj = n["f"].get("maj") == "uppercase"
        groupes = {}
        for code in LANGUES_JEU:
            mot = mots.get(code) or mots.get("english") or n["txt"]
            groupes.setdefault(majuscules(mot, code) if maj else mot, []).append(code)
        r = None
        for mot, codes in groupes.items():
            r = self.texte_un(parent, n, pn, gpn, mot=mot, classes=[CLASSE_MOT] + [f"{CLASSE_MOT}-{slug(c)}" for c in codes])
        defaut = mots.get("english") or n["txt"]
        self.texte_un(parent, n, pn, gpn, mot=majuscules(defaut, "english") if maj else defaut,
                      classes=[CLASSE_MOT_DEFAUT])
        self.n_mots += 1
        return r

    def texte_un(self, parent, n, pn=None, gpn=None, fm=None, mot=None, classes=(), flux=False):
        """un SIText de FM en absolu à la place du texte n de la maquette. fm : le nom de FM par son n° de traduction ;
        mot : ce texte-là (une langue). v95 : traduit (fm ou mot), la boîte prend la place libre du texte (place, relevée
        dans la maquette) et le texte trop long finit par « … » ; flux : dans le flux de son parent (en-tête), à la
        largeur de son mot"""
        t, src = self.t, self.src
        f = n["f"]
        r = t.clone(src.titre, parent, src=src.tp)
        t.styles.copy_from(src.tp.styles, t, r)
        base.recaler_parent(t, r)
        for k in list(t.children(r)):
            t.remove(k)
        sd = t.sd(r)
        sd["name"], sd["name_UxmlAttributeFlags"] = "", 0
        traduit = fm is not None or mot is not None
        if mot is None:
            # v55 : les capitales écrites dans le texte (en jeu, la v54 montrait « Relance » au lieu de « RELANCE »)
            mot = n["txt"].upper() if f.get("maj") == "uppercase" else n["txt"]
        sd.update(text=mot, text_UxmlAttributeFlags=1, DebugDisplay=mot)
        sd["TextBinding"]["m_kind"] = 0
        sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        base.fonction_vide(sd["TextBinding"]["m_visualFunction"])
        if fm is not None:
            self.lier_traduction(r, fm)
        if "TextCase" in sd:
            sd["TextCase"], sd["TextCase_UxmlAttributeFlags"] = 0, 1
        fam = f["fam"]
        if fam not in CLASSES_POLICE:
            self.alertes.append(f"police inconnue : {fam}")
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [CLASSES_POLICE.get(fam, "body-sm"), *classes], -1
        taille = f["taille"] if fam == POLICE_FIXE else f["taille"] / TAILLE_TEXTE
        bw, _bh = f["boite"]
        p0, p1 = f["pad"]
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        css = {"position": "absolute", "top": y, "height": h, "margin-top": 0, "margin-bottom": 0, "margin-left": 0,
               "margin-right": 0, "padding-top": 0, "padding-bottom": 0, "padding-left": 0, "padding-right": 0,
               "font-size": round(taille, 3), "-unity-font-style": "bold" if f["poids"] >= 600 else "normal",
               "color": self.couleur(f["coul"])}
        ou = self.ancrage(n, pn, gpn)
        al = {"centre": "middle-center", "droite": "middle-right", "gauche": "middle-left"}[ou]
        if n.get("lignes", 1) <= 1:
            larg = w + MARGE_TEXTE
            gauche = x + w / 2 - larg / 2 if ou == "centre" else (x + w - larg if ou == "droite" else x)
            if traduit:   # v95 : la place libre, au moins la largeur française et MARGE_ELLIPSE
                pg, pd = n.get("place") or (x, x + w)
                if ou == "centre":
                    cx = x + w / 2
                    demi = max(min(cx - pg, pd - cx), (w + MARGE_ELLIPSE) / 2)
                    gauche, larg = cx - demi, 2 * demi
                elif ou == "droite":
                    gauche = min(pg, x - MARGE_ELLIPSE)
                    larg = x + w - gauche
                else:
                    gauche, larg = x, max(pd - x, w + MARGE_ELLIPSE)
            css.update({"left": round(gauche, 2), "width": round(larg, 2), "white-space": "nowrap",
                        "-unity-text-align": al})
        else:
            css.update({"left": p0, "width": round(bw - p0 - p1, 2), "white-space": "normal", "-unity-text-align": al})
        if traduit:
            css.update({"overflow": "hidden", "text-overflow": "ellipsis"})
            if n.get("lignes", 1) > 1:   # deux lignes : la boîte un peu plus large, même centre (police du jeu)
                css.update({"left": round(p0 - MARGE_ELLIPSE / 2, 2), "width": round(bw - p0 - p1 + MARGE_ELLIPSE, 2)})
        if flux:   # v95 : l'en-tête, dans le flux du bouton
            for k in ("left", "top", "width", "overflow", "text-overflow"):
                css.pop(k, None)
            css.update({"position": "relative", "flex-shrink": 0, "white-space": "nowrap",
                        "-unity-text-align": "middle-center"})
        elif traduit:   # v96 : coupé par « … », le survol montre la phrase entière (comme les en-têtes de FM)
            sd["DisplayTooltipWhenElided"], sd["DisplayTooltipWhenElided_UxmlAttributeFlags"] = 1, 1
        t.styles.style(t, r, css)
        if traduit and not flux:   # v96 : il reçoit le survol (dessous des boutons de clic : il ne leur prend rien)
            self.avec_clic(r)
            self.n_survols += 1
        else:
            self.sans_clic(r)
        self.n += 1
        return r

    def lier_traduction(self, r, fm):
        """v95 : le SIText r affiche le nom de FM fm (["n", consigne] ou ["o", consigne, option]) dans la langue du jeu :
        la liaison de traduction de FM recopiée (SourcesEcran.liaison_traduite), avec le n° de traduction du nom (lu
        dans les données du jeu) et son texte anglais de secours"""
        t, se = self.t, self.se
        if fm[0] == "n":
            ident, cle = se.ids[fm[1]][0], f"n{fm[1]}"
        else:
            ident, cle = se.ids[fm[1]][1][fm[2]], f"o{fm[1]}.{fm[2]}"
        anglais = ANGLAIS_FM.get(cle, "")
        if cle not in ANGLAIS_FM:
            self.alertes.append(f"texte anglais de secours : {cle} (introuvable)")
        tb = copy.deepcopy(se.liaison_traduite)
        fn = tb["m_visualFunction"]
        args = decode_args(fn["m_inputs"]["m_variable"]["m_argumentBytes"])
        args[0][1] = struct.pack("<i", ident) + texte_arg(anglais)
        fn["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        sd = t.sd(r)
        sd["TextBinding"], sd["TextBinding_UxmlAttributeFlags"] = tb, 1
        sd.update(text=anglais, DebugDisplay=anglais)
        self.n_traduits += 1

    @staticmethod
    def paire_deux_lignes(enfants):
        """v95 : (1re ligne, 2e ligne, nom de FM) d'un texte écrit sur deux lignes par la maquette (DEUX_LIGNES), ou None"""
        textes = [k for k in enfants if k["t"] == "#text"]
        for a, b in zip(textes, textes[1:]):
            fm = DEUX_LIGNES.get((a["txt"], b["txt"]))
            if fm:
                return a, b, list(fm)
        return None

    def texte_deux_lignes(self, parent, a, b, fm, pn, gpn):
        """v95 : les deux lignes de la maquette remplacées par le nom entier de l'option (le jeu l'écrit dans sa langue),
        sur deux lignes au plus dans la boîte des deux, centré"""
        x0, x1 = min(a["x"], b["x"]), max(a["x"] + a["w"], b["x"] + b["w"])
        n = dict(a, x=x0, w=x1 - x0, h=b["y"] + b["h"] - a["y"], lignes=2, anc="c", fm=fm,
                 txt=f"{a['txt']} {b['txt']}", f=dict(a["f"], al="center"))
        return self.texte_un(parent, n, pn, gpn, fm=fm)

    def icone(self, parent, n):
        """une icône de FM (classe de l'option), la boîte agrandie de la toile pour que le DESSIN tombe sur l'image de
        la maquette (comme Fab.icone_case)"""
        ic = n.get("ic")
        if not isinstance(ic, list):
            self.alertes.append(f"image sans consigne : {ic}")
            return
        cid, k = ic
        opts = self.src.options.get(cid) or []
        classe = opts[k][1] if k < len(opts) else None
        if not classe:
            self.alertes.append(f"consigne {cid}, option {k} : pas d'icône de FM")
            return
        dw, dh, cx, cy, rw, rh = self.fab.dessin(classe)
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        if w <= 0 or h <= 0:   # une image pas encore chargée au moment de l'export
            self.alertes.append(f"consigne {cid}, option {k} : image de taille nulle dans l'export")
            return
        s = min(w / dw, h / dh)
        W, H = rw * s, rh * s
        gx, gy = x + w / 2 - cx * s - W / 2, y + h / 2 + cy * s - H / 2
        css = {"position": "absolute", "left": round(gx, 2), "top": round(gy, 2), "width": round(W, 2),
               "height": round(H, 2), "background-size": 8}
        if n.get("op") is not None:
            css["opacity"] = n["op"]
        r = self.boite(parent, css)
        self.t.elem(r)["m_Classes"] = [classe]
        self.fab.style_brut(r, [(458754, [(7, "center"), (2, 0.0)]), (458755, [(7, "center"), (2, 0.0)])])

    def ballon(self, parent, n):
        """le ballon de la piste (un rond blanc cerclé, un point sombre) : le dessin SVG de la maquette ne se fait pas"""
        x, y, w = n["x"], n["y"], n["w"]
        d = 0.9 * w
        self.boite(parent, {"position": "absolute", "left": x + (w - d) / 2, "top": y + (w - d) / 2, "width": d,
                            "height": d, "background-color": (1.0, 1.0, 1.0, 1.0),
                            **{f"border-{c}-width": max(1.0, 0.06 * w) for c in ("top", "right", "bottom", "left")},
                            **{f"border-{c}-color": (0x0b / 255, 0x11 / 255, 0x20 / 255, 1.0)
                               for c in ("top", "right", "bottom", "left")},
                            **{f"border-{c}-radius": d / 2 for c in ("top-left", "top-right", "bottom-right",
                                                                     "bottom-left")}})
        p = 0.44 * w
        self.boite(parent, {"position": "absolute", "left": x + (w - p) / 2, "top": y + 0.48 * w - p / 2, "width": p,
                            "height": p, "background-color": (0x0b / 255, 0x11 / 255, 0x20 / 255, 1.0),
                            **{f"border-{c}-radius": p / 2 for c in ("top-left", "top-right", "bottom-right",
                                                                     "bottom-left")}})

    # -- l'arbre --
    @staticmethod
    def _niveau(k):
        """(positionné ?, z-index) d'un élément de la maquette : son niveau de peinture"""
        return (0, 0) if k["t"] == "#text" else (1 if k.get("pos") else 0, k.get("z", 0))

    def ordre(self, enfants):
        """l'ordre de peinture de Chrome : ce qui n'est pas positionné (et les textes), puis le positionné par z-index.
        v56 : une enveloppe dep (display: contents) n'a pas de boîte, ses éléments se peignent chacun à leur niveau :
        elle devient un groupe par niveau (« depg »), chacun à sa place ; ses variantes vides sont sautées"""
        items = []
        for k in enfants:
            if k["t"] != "dep":
                items.append(k)
                continue
            v = self.d["deps"][k["cle"]]["v"]
            niveaux = []
            for ks in [k.get("k") or []] + list(v.values()):
                for c in ks:
                    if self._niveau(c) not in niveaux:
                        niveaux.append(self._niveau(c))
            if k.get("texte"):
                self.alertes.append(f"enveloppe {k['cle']} : texte nu ignoré")
            for pos, z in niveaux:
                items.append({"t": "depg", "dep": k, "pos": pos, "z": z})
        flux = [k for k in items if k["t"] == "#text" or not k.get("pos")]
        pos = sorted((k for k in items if k["t"] != "#text" and k.get("pos")), key=lambda k: k.get("z", 0))
        return flux + pos

    @staticmethod
    def vide(n):
        return not (n.get("bg") or n.get("deg") or n.get("bw") or n.get("k") or n["t"] in ("img", "svg"))

    def est_carte(self, n):
        if "lc" not in n.get("cl", "").split():
            return None

        def crans(x):
            if x.get("data", {}).get("i") and "cran" in x.get("cl", "").split():
                yield int(x["data"]["i"])
            for k in x.get("k") or []:
                yield from crans(k)
        ids = set(crans(n))
        ids &= {int(i) for i in self.d.get("variantes", {})}
        return next(iter(ids), None) if len(ids) == 1 else None

    def construire(self, parent, n, ox, oy, brancher=True, pn=None, gpn=None):
        """pose la boîte n (et ses enfants) sous parent ; ox, oy : coin de parent dans l'écran (en-tête) ; brancher :
        faux pour les variantes d'une carte branchée (elles se dessinent telles quelles) ; pn, gpn : les boîtes de la
        maquette parent et grand-parent de n (l'accroche d'un texte)"""
        if n["t"] == "#text":
            self.texte(parent, n, pn, gpn)
            return
        if n["t"] == "img":
            self.icone(parent, n)
            return
        if n["t"] == "svg":
            self.ballon(parent, n)
            return
        if n["t"] == "depg":   # v56 : un groupe d'une enveloppe des terrains
            self.dependance(parent, n["dep"], (n["pos"], n["z"]), ox, oy, pn, gpn)
            return
        cid = self.est_carte(n) if brancher else None
        if cid is not None and (BRANCHEES is None or cid in BRANCHEES):
            self.carte_branchee(parent, n, cid)
            return
        if self.vide(n):
            return
        if any("btn-e" in (k.get("cl") or "").split() for k in n.get("k") or []):   # v95 : l'en-tête
            self.entete(parent, n, ox, oy, pn)
            return
        if "btn-e" in n.get("cl", "").split():
            mot = " ".join(k["txt"] for k in n.get("k") or [] if k["t"] == "#text")
            valeur = {"FM24": VUE_FM24, "Tuiles": VUE_TUILES, "Terrain": VUE_TERRAIN}.get(mot)
            if valeur is not None:
                self.boutons_vue.append((ox + n["x"], oy + n["y"], n["w"], n["h"], valeur))
        r = self.boite(parent, self.css_boite(n))
        self.transformer(r, n)
        if n.get("deg"):
            self.degrade(r, n)
        bl = n.get("bw") or [0, 0, 0, 0]
        enfants = self.ordre(n.get("k") or [])
        paire = self.paire_deux_lignes(enfants)   # v95
        for k in enfants:
            if paire and k is paire[1]:
                continue
            if paire and k is paire[0]:
                self.texte_deux_lignes(r, paire[0], paire[1], paire[2], n, pn)
                continue
            self.construire(r, k, ox + n["x"] + bl[3], oy + n["y"] + bl[0], brancher, n, pn)

    # -- la carte branchée --
    def crans(self, n, x0=0.0, y0=0.0):
        """(option, x, y, w, h) de chaque cran de la carte n, dans le repère de son parent"""
        bl = n.get("bw") or [0, 0, 0, 0]
        if "cran" in n.get("cl", "").split() and n.get("data", {}).get("o") is not None:
            yield int(n["data"]["o"]), x0 + n["x"], y0 + n["y"], n["w"], n["h"]
            return
        for k in n.get("k") or []:
            if k["t"] != "#text":
                yield from self.crans(k, x0 + n["x"] + bl[3], y0 + n["y"] + bl[0])

    def carte_branchee(self, parent, n, cid):
        """la carte de la consigne cid : son dessin selon l'option choisie (une variante exportée par option), et un
        bouton de consigne de FM invisible sur chaque cran (zone de clic de HAUT_CLIC de haut, dans la carte)"""
        fab, t = self.fab, self.t
        variantes = self.d["variantes"][str(cid)]
        self.n_cartes += 1
        plein = {"position": "absolute", "left": 0, "top": 0, "width": base.pc(100), "height": base.pc(100)}
        env = fab.enveloppe(parent, cid, f"ecran-consigne-{cid}", traverse=True)

        def faire(par, k):
            self.construire(par, variantes[k], 0.0, 0.0, brancher=False)
        sel = fab.selon(env, cid, faire, f"ecran-c{cid}", css=plein)
        fab.traverse(sel)
        for r in t.walk(sel):   # les interrupteurs de selon : sur toute la place (les cartes y sont en absolu)
            if typ(t, r) == "BindableSwitchElement":
                t.styles.style(t, r, plein)
                fab.traverse(r)
        haut_carte = n["y"] + n["h"]
        for o, x, y, w, h in self.crans(n):
            hh = max(h, HAUT_CLIC)
            yy = min(max(y + h / 2 - hh / 2, n["y"]), haut_carte - hh)
            self.cliquer(env, cid, o, {"position": "absolute", "left": round(x, 2), "top": round(yy, 2),
                                       "width": round(w, 2), "height": hh})

    def cliquer(self, env, cid, o, css):
        """v56 : le bouton de FM invisible de l'option o de la consigne cid (dans son enveloppe), comme bouton_b de
        26.13 : l'option neutre (DEFAUTS) et la hauteur du pressing (SANS_RETOUR) en bouton simple ; les autres en case
        à bascule (un 2e clic sur l'option choisie remet l'option neutre, comme les clics de la maquette)"""
        d = base.DEFAUTS.get(cid)
        if d is None or o == d or cid in SANS_RETOUR:
            return self.fab.option(env, cid, o, nu=True, texte=False, css=css)
        return self.fab.bascule(env, cid, o, d, nu=True, texte=False, css=css)

    # -- v56 : les enveloppes des terrains --
    def dependance(self, parent, dep, niveau, ox, oy, pn, gpn):
        """le groupe <niveau> de l'enveloppe dep : ses éléments de ce niveau, dessinés selon l'option de sa consigne
        (une enveloppe de FM et Fab.selon), de ses DEUX consignes pour le bloc (8 et 9 : imbriqués). Les éléments gardent
        leur place : l'enveloppe, le choix et chaque variante couvrent tout le parent, comme la balise dep de la maquette
        (sans boîte à elle)"""
        fab, t = self.fab, self.t
        ids, v = dep["ids"], self.d["deps"][dep["cle"]]["v"]
        plein = {"position": "absolute", "left": 0, "top": 0, "width": base.pc(100), "height": base.pc(100)}

        def garder(ks):
            return [c for c in ks if self._niveau(c) == niveau]
        if not any(garder(ks) for ks in v.values()):
            return
        self.n_deps += 1
        nom = f"ecran-dep{self.n_deps}"

        def niveau_(par, i, choix):
            env = fab.enveloppe(par, ids[i], f"{nom}-c{ids[i]}", traverse=True)

            def faire(p2, k):
                b = self.boite(p2, plein)
                if i + 1 < len(ids):
                    niveau_(b, i + 1, choix + [k])
                    return
                cle = ",".join(str(x) for x in choix + [k])
                if cle not in v:
                    self.alertes.append(f"enveloppe {dep['cle']} : pas de variante {cle}")
                    return
                for c in self.ordre(garder(v[cle])):
                    self.construire(b, c, ox, oy, False, pn, gpn)
            sel = fab.selon(env, ids[i], faire, f"{nom}-s{ids[i]}", css=plein)
            fab.traverse(sel)
            for r in t.walk(sel):
                if typ(t, r) == "BindableSwitchElement":
                    t.styles.style(t, r, plein)
                    fab.traverse(r)
        niveau_(parent, 0, [])

    # -- v56 : les clics des terrains --
    def collecter(self, n, ox, oy, dans_carte=False):
        """les éléments cliquables de la maquette hors des cartes (zones, pastilles, flèches, bandes), dans l'ordre de
        peinture, avec leur place dans l'écran : (x, y, w, h, données)"""
        if n["t"] in ("#text", "img", "svg"):
            return
        if n["t"] == "dep":
            for k in n.get("k") or []:
                self.collecter(k, ox, oy, dans_carte)
            return
        carte = dans_carte or "lc" in n.get("cl", "").split()
        tr = n.get("tr") or {}
        x, y = ox + n["x"] + tr.get("tx", 0.0), oy + n["y"] + tr.get("ty", 0.0)
        dd = n.get("data") or {}
        if not carte and ("prog" in dd or "course" in dd or ("i" in dd and "o" in dd)):
            if abs(tr.get("rot", 0.0)) > 0.01 or abs(tr.get("sx", 1) - 1) > 1e-3 or abs(tr.get("sy", 1) - 1) > 1e-3:
                self.alertes.append(f"zone de clic tournée ou agrandie ignorée : {dd}")
            else:
                self.clics.append((x, y, n["w"], n["h"], dd))
        bl = n.get("bw") or [0, 0, 0, 0]
        for k in self.ordre_simple(n.get("k") or []):
            self.collecter(k, x + bl[3], y + bl[0], carte)

    @staticmethod
    def ordre_simple(enfants):
        flux = [k for k in enfants if k["t"] in ("#text", "dep") or not k.get("pos")]
        pos = sorted((k for k in enfants if k["t"] not in ("#text", "dep") and k.get("pos")), key=lambda k: k.get("z", 0))
        return flux + pos

    def poser_clics(self, ecran):
        """un bouton de FM invisible sur chaque élément cliquable des terrains, dans l'enveloppe de sa consigne (une par
        consigne, sur tout l'écran, qui laisse passer les clics), dans l'ordre de peinture (le dernier dessus)"""
        fab = self.fab
        envs = {}

        def env_de(cid):
            if cid not in envs:
                envs[cid] = fab.enveloppe(ecran, cid, f"ecran-clics-{cid}", traverse=True)
            return envs[cid]
        for x, y, w, h, dd in self.clics:
            css = {"position": "absolute", "left": round(x, 2), "top": round(y, 2), "width": round(w, 2),
                   "height": round(h, 2)}
            if "prog" in dd:
                k = dd["prog"]
                if k == "E":   # « Progression : Équilibrée » : toujours l'option 0 (maquette : cliquerProg)
                    fab.option(env_de(30), 30, 0, nu=True, texte=False, css=css)
                else:
                    fab.etats(env_de(30), 30, base.REGLES_PROGRESSION[k], PROGRESSION_MONTRE[k], css=css, nu=True,
                              texte=False)
            elif "course" in dd:
                cid, bit = (int(v) for v in dd["course"].split(":"))
                place = self.boite(env_de(cid), css)
                course_nu(fab, place, cid, 31 if cid == 28 else 28, bit == 1)
            else:
                self.cliquer(env_de(int(dd["i"])), int(dd["i"]), int(dd["o"]), css)
            self.n_clics += 1

    # -- l'en-tête : les boutons de vue --
    def entete(self, parent, n, ox, oy, pn):
        """v95 : l'en-tête de la maquette (titre, « Partir de zéro », FM24 / Tuiles / Terrain). Ses boutons avaient la
        largeur de leur mot français : traduits (« Kacheln », « Spielfeld »), ils étaient coupés. Chaque groupe de
        boutons voisins est une RANGÉE accrochée du côté où il est (le dernier groupe à droite), chaque bouton prend la
        largeur de son mot dans la langue du jeu (copies par langue dans le flux : les cachées ne prennent pas de
        place) et porte son bouton de FM invisible qui écrit la vue (les 3 boutons de vue)"""
        r = self.boite(parent, self.css_boite(n))
        self.transformer(r, n)
        bl = n.get("bw") or [0, 0, 0, 0]
        largeur = n["w"] - bl[1] - bl[3]
        groupes, courant = [], []
        for k in n.get("k") or []:
            if "btn-e" in (k.get("cl") or "").split():
                if courant and k["x"] - (courant[-1]["x"] + courant[-1]["w"]) > 12:
                    groupes.append(courant)
                    courant = []
                courant.append(k)
                continue
            if courant:
                groupes.append(courant)
                courant = []
            self.construire(r, k, ox + n["x"] + bl[3], oy + n["y"] + bl[0], True, n, pn)
        if courant:
            groupes.append(courant)
        for g in groupes:
            a_droite = largeur - (g[-1]["x"] + g[-1]["w"]) < g[0]["x"]
            css = {"position": "absolute", "top": g[0]["y"], "height": g[0]["h"], "flex-direction": "row",
                   "align-items": "center"}
            css.update({"right": round(largeur - (g[-1]["x"] + g[-1]["w"]), 2)} if a_droite else {"left": g[0]["x"]})
            rangee = self.boite(r, css)
            ecart = g[1]["x"] - (g[0]["x"] + g[0]["w"]) if len(g) > 1 else 0
            for i, b in enumerate(g):
                css_b = {k: v for k, v in self.css_boite(b).items() if k not in ("position", "left", "top", "width")}
                tx = next((k for k in b.get("k") or [] if k["t"] == "#text"), None)
                pad = tx["f"]["pad"] if tx else [8, 8]
                css_b.update({"position": "relative", "flex-shrink": 0, "flex-direction": "row", "align-items": "center",
                              "justify-content": "center", "padding-left": pad[0], "padding-right": pad[1],
                              "margin-left": round(ecart, 2) if i else 0})
                bouton = self.boite(rangee, css_b)
                if tx is None:
                    continue
                self.texte_flux(bouton, tx)
                valeur = {"FM24": VUE_FM24, "Tuiles": VUE_TUILES, "Terrain": VUE_TERRAIN}.get(tx["txt"])
                if valeur is not None:
                    self.bouton_vue(bouton, 0, 0, base.pc(100), base.pc(100), valeur)
                    self.n_vues_dans += 1

    def texte_flux(self, parent, n):
        """v95 : un texte de l'en-tête DANS LE FLUX de son bouton (sa largeur fait celle du bouton) : une copie par
        langue si c'est un de nos mots, sinon tel quel"""
        mots = self.mots.get(n["txt"])
        if mots:
            maj = n["f"].get("maj") == "uppercase"
            groupes = {}
            for code in LANGUES_JEU:
                mot = mots.get(code) or mots.get("english") or n["txt"]
                groupes.setdefault(majuscules(mot, code) if maj else mot, []).append(code)
            for mot, codes in groupes.items():
                self.texte_un(parent, n, mot=mot, classes=[CLASSE_MOT] + [f"{CLASSE_MOT}-{slug(c)}" for c in codes],
                              flux=True)
            self.texte_un(parent, n, mot=mots.get("english") or n["txt"], classes=[CLASSE_MOT_DEFAUT], flux=True)
            self.n_mots += 1
        else:
            self.n_fixes += 1
            self.texte_un(parent, n, flux=True)

    def bouton_vue(self, cadre, x, y, w, h, valeur):
        t, se = self.t, self.se
        r = self.seul(self.src.th, se.bouton, cadre)
        sd = t.sd(r)
        sd["Events"] = {"m_bytes": base.liste([base.copier(base.PLACES[valeur], base.VARIABLE, 1)])}
        t.styles.style(t, r, {"position": "absolute", "left": x if isinstance(x, dict) else round(x, 2),
                              "top": y if isinstance(y, dict) else round(y, 2), "width": w,
                              "height": h, "background-color": (0.0, 0.0, 0.0, 0.0), "border-top-width": 0,
                              "border-bottom-width": 0, "border-left-width": 0, "border-right-width": 0,
                              "margin-top": 0, "margin-bottom": 0, "margin-left": 0, "margin-right": 0})
        self.avec_clic(r)


def conteneur_langue(e, parent, largeur, hauteur, version):
    """v95 : le conteneur de FM qui lit la langue du jeu (celui de tdd-messages-banner : current_language, et
    languagesetting -> app.NativeSettings ; comme Fab.selon_langue de 26.13 v24), sur toute la boîte de l'écran, sans
    clic ; dedans, un réglage de FM par langue (comparaison de texte, REGLAGE_TEXTE comme la v87) qui pose sur lui la
    classe CLASSE_LANGUE + la langue ; nos règles (regles_langues) montrent sous elle les mots de cette langue"""
    t, src = e.t, e.src
    env = t.clone(src.langue_env, parent, src=src.tg)
    base.recaler_parent(t, env)
    for k in list(t.children(env)):
        if not t.elem(k).get("m_FullTypeName", "").endswith("Component"):
            t.remove(k)
    t.styles.copy_from(src.tg.styles, t, env)
    sd = t.sd(env)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{nom_racine(version)}-langue", 1
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    donnees_ = json.dumps([(t.refs.get(c["rid"]) or {}).get("data") for c in sd.get("m_components") or []])
    if "current_language" not in donnees_ or "app.NativeSettings" not in donnees_:
        raise ValueError("conteneur de langue de FM (tdd-messages-banner) : forme inattendue")
    t.styles.style(t, env, {"position": "absolute", "left": 0, "top": 0, "width": largeur, "height": hauteur})
    e.fab.traverse(env)
    for code in LANGUES_JEU:
        REGLAGE_TEXTE(t, env, f"{nom_racine(version)}-langue-{slug(code)}", CHEMIN_LANGUE, code,
                      CLASSE_LANGUE + slug(code), {"position": "absolute", "width": 0, "height": 0})
    attacher_feuille(t, env)
    regles_langues(t)
    return env


CHEMIN_EXPLICATION = "data.TacticTeamInstructionOption.DescriptionLong"   # v96 : comme la vue FM24 (v38)


def bulles_options(e, racine):
    """v96 (Kinito, 13/11 : « l'infobulle correspondant au choix de la consigne, comme sur la vue FM24 ») : dans
    chaque bouton d'option de l'écran (crans des cartes, zones et pastilles des terrains : ceux qu'enveloppe le
    BindingSetter « id » de Fab.option), l'infobulle de FM (celle de RoleLabelwIcon, dans le bouton même : v16)
    liée à l'explication de l'option dans la langue du jeu — comme kinito_consignes_essai_b.bulles_equipe24"""
    t, src, fab = e.t, e.src, e.fab
    n = 0
    for r in list(t.walk(racine)):
        if typ(t, r) != "SIButton" or any(typ(t, k) == "Tooltip" for k in t.children(r)):
            continue
        p, option = r, False
        while p in t.parent:
            p = t.parent[p]
            if any(v.get("m_name") == "id" for v in t.sd(p).get("ValueVariables") or []):
                option = True
                break
            if p == racine:
                break
        if not option:
            continue
        bu = t.clone(src.bulle, r, src=src.tu)
        t.styles.copy_from(src.tu.styles, t, bu)
        base.recaler_parent(t, bu)
        fab._nom(bu, f"ecran-bulle-{n}")
        base.texte_lie(t, t.children(bu)[0], CHEMIN_EXPLICATION, "explication")
        n += 1
    return n


def regles_langues(t):
    """v95 : un mot écrit dans une langue est caché (CLASSE_MOT), sauf sous la classe de sa langue ; le mot de secours
    (CLASSE_MOT_DEFAUT, anglais) est caché sous toute classe de langue connue"""
    affichage = base.sm.PROPRIETES["display"][0]
    regle_selecteurs(t, [(affichage, "", [(7, "none")])], REPERE_LANGUE, [[(TYPE_CLASSE, CLASSE_MOT, 0)]])
    regle_selecteurs(t, [(affichage, "", [(7, "flex")])], REPERE_LANGUE + 0.01,
                     [[(TYPE_CLASSE, CLASSE_LANGUE + slug(c), 0), (TYPE_CLASSE, f"{CLASSE_MOT}-{slug(c)}", DESCENDANT)]
                      for c in LANGUES_JEU])
    regle_selecteurs(t, [(affichage, "", [(7, "none")])], REPERE_LANGUE + 0.02,
                     [[(TYPE_CLASSE, CLASSE_LANGUE + slug(c), 0), (TYPE_CLASSE, CLASSE_MOT_DEFAUT, DESCENDANT)]
                      for c in LANGUES_JEU])


def course_nu(fab, place, n, autre, gauche):
    """v56 : une case des courses de soutien SANS dessin (le dessin vient de la maquette) : base.course de 26.13, les
    mêmes boutons de FM, invisibles. Intérieur (28) et extérieur (31) du même côté s'excluent : son côté pris par sa
    consigne, un clic le retire ; pris par l'autre, un clic ÉCHANGE (l'autre le perd, celle-ci le prend) ; sinon, un
    clic le prend (comme cliquerCourse de la maquette)"""
    opts = fab.src.options[n]
    cote_pris = (1, 3) if gauche else (2, 3)
    ajoute = {0: 1, 2: 3} if gauche else {0: 2, 1: 3}
    retire = {1: 0, 3: 2} if gauche else {2: 0, 3: 1}
    montre = 1 if gauche else 2
    kw = dict(nu=True, texte=False, css={"flex-grow": 1})
    fab.n += 1
    nom = f"ecran-course-{fab.n}"

    def selon_soi(par, s_soi):
        if s_soi in cote_pris:
            fab.option(par, n, retire[s_soi], affiche=montre, allume=opts[s_soi][0], **kw)
            return
        garde = fab.retenir(par, "teaminstructionid", "kinitoida", f"{nom}-id-{s_soi}")
        env = fab.enveloppe(garde, autre, f"{nom}-autre-{s_soi}", css={"flex-grow": 1})

        def selon_autre(par2, s_autre):
            cible = ajoute[s_soi]
            if s_autre in cote_pris:   # le côté est à l'autre : un clic échange
                fab.option(par2, autre, retire[s_autre], n_vue=n, affiche=montre, allume=opts[cible][0],
                           extra=("kinitoida", cible), force=True, **kw)
            else:
                fab.option(par2, n, cible, n_vue=n, affiche=montre, allume=opts[cible][0], cible="kinitoida",
                           force=True, **kw)
        fab.selon(env, autre, selon_autre, f"{nom}-selon-autre-{s_soi}", css={"flex-grow": 1})
    fab.selon(place, n, selon_soi, f"{nom}-selon", css={"flex-grow": 1})


def body_de(t):
    return first(t, lambda r: t.name(r) == "Body" and typ(t, r) == "VisualElement")


def bande_tuiles(e, se, cadre, version):
    """v64 : sous la zone de l'écran, la bande des tuiles de FM (TUILES) ; rend le nombre de tuiles posées"""
    t = e.t
    inst = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == INSTANCE_ONGLET)
    if inst is None:
        return 0
    bande = e.boite(cadre, {"width": base.pc(100), "height": BANDE + DEPASSE_BAS + 2, "flex-shrink": 0,
                            "padding-top": ECART, "padding-bottom": DEPASSE_BAS + 2},
                    nom=f"{nom_racine(version)}-tuiles")
    # v65 : les colonnes dans une rangée à leur hauteur exacte, coupée : une colonne passée à la ligne n'apparaît plus
    # dans la marge du bas de la bande (v64 : le haut de l'entraînement individuel s'y voyait)
    rang = e.boite(bande, {"width": base.pc(100), "height": RANGEE(4), "flex-shrink": 0, "flex-direction": "row",
                           "flex-wrap": "wrap", "justify-content": "center", "align-items": "flex-start",
                           "overflow": "hidden"})
    usings = t.tt.setdefault("m_Usings", [])
    n = 0
    for i, colonne in enumerate(TUILES):   # 6 x 304 + 5 x 12 = 1 884
        col = e.boite(rang, {"width": COLONNE, "height": RANGEE(4), "flex-shrink": 0,
                             "margin-left": ECART_TUILES if i else 0, "flex-direction": "column",
                             "justify-content": "space-between"})
        for tuile in colonne:
            tuile_fm(e, se, inst, col, tuile)
            n += 1
    return n


def poser_seul24(t, src, tb, z, nom, x=None):
    """v76 : en vue FM24, quand le terrain de Positionnement ne paraît pas, notre dispositif par-dessus le visualiseur
    de FM, et le choix « Dispositif | Visualiseur » (voir X_VISU24) ; posé depuis la boîte z ; rend le nom du dispositif"""
    x = X_VISU24 if x is None else x   # v79 (X_VISU24 est défini plus bas)
    e = _ecran_boites(t, src, tb)
    boite, _ = boite_variables(t, z, f"{nom}-choix-vars", {VAR_GAUCHE: 0},
                               {"position": "absolute", "left": x - PLACE_DEUX24, "top": base.pc(-100),
                                "width": LARGEUR_TERRAIN24, "height": base.pc(100)})
    e.sans_clic(boite)
    choix = interrupteur(e, tb, boite, f"{nom}-choix", VAR_GAUCHE)
    cas_d = e.boite(choix, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0},
                    nom=f"{nom}-cas-dispositif")
    nom_d = f"{nom}-dispositif"
    poser_terrain24(t, src, tb, cas_d, nom_d, css={"width": LARGEUR_TERRAIN24, "height": base.pc(100),
                                                   "flex-direction": "column"}, hauteur=HAUT_TERRAIN_COUPE)
    e.boite(choix, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}, nom=f"{nom}-cas-visualiseur")
    bascule(e, tb, boite, f"{nom}-bascule", VAR_GAUCHE)   # v81 (v76 à v80 : SEGMENTS)
    return nom_d


def bascule(e, tb, parent, nom, variable):
    """v81 (voir ICONE_VERS_VISUALISEUR) : le bouton unique à icône, en absolu sur toute la place du panneau (parent) ;
    un interrupteur de FM sur variable : 0 (le dispositif est montré) -> le bouton du petit terrain, qui met 1 ; 1 -> le
    bouton des joueurs, qui met 0"""
    t, src = e.t, e.src
    cas = interrupteur(e, tb, parent, f"{nom}-cas", variable)
    for valeur, icone, place in ((1, ICONE_VERS_VISUALISEUR, BASCULE_SUR_DISPOSITIF),
                                 (0, ICONE_VERS_DISPOSITIF, BASCULE_SUR_VISUALISEUR)):
        z = e.boite(cas, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0},
                    nom=f"{nom}-cas-{valeur}")
        BOUTON(t, src, z, f"{nom}-vers-{valeur}", variable, valeur, place, icone=icone, taille_icone=BASCULE_ICONE)
    return cas


def ligne_tuiles(e, se, cadre, version, rapport):
    """v75 : sous la zone de l'écran, en Moyen, UNE rangée de tuiles 4 x 2 (LIGNE_TERRAIN), derrière un repère vide (une
    tuile qui ne tient pas en largeur passe à la ligne, cachée) ; elle ne reste dans le cadre (qui passe à la ligne en
    colonne) que s'il a sa hauteur sous la zone ; rend le nombre de tuiles"""
    t = e.t
    inst = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == INSTANCE_ONGLET)
    if inst is None:
        return 0
    # v77 : en absolu dans le cadre, à la hauteur de l'écran (rapport : sa hauteur / sa largeur) + 16 (voir CLASSE_PETIT)
    ligne = e.boite(cadre, {"position": "absolute", "left": 0, "right": 0, "top": 0, "bottom": DEPASSE_BAS + 2,
                            "margin-top": base.pc(round(100 * rapport, 3)), "padding-top": ECART,
                            "flex-direction": "column", "flex-wrap": "wrap", "align-content": "flex-start",
                            "overflow": "hidden"}, nom=f"{nom_racine(version)}-ligne")
    e.boite(ligne, {"width": base.pc(100), "height": 0, "flex-shrink": 0})
    # v76 : les tuiles dans une rangée de leur hauteur exacte, coupée (v75 : la 5e, passée à la ligne, dépassait dessous)
    # v78 : des tuiles 4 x 4 réduites (ECHELLE_LIGNE) : chacune dans une boîte de sa taille réduite, la tuile (à sa vraie
    # taille, 304 x 312) centrée dessus et réduite autour de son centre (l'échelle ne change pas la mise en page)
    k = ECHELLE_LIGNE
    lw, lh = round(COLONNE * k), round(RANGEE(4) * k)   # 231 x 237
    rang = e.boite(ligne, {"width": base.pc(100), "height": lh, "flex-shrink": 0, "flex-direction": "row",
                           "flex-wrap": "wrap", "justify-content": "center", "align-content": "flex-start",
                           "overflow": "hidden"})
    e.boite(rang, {"width": 0, "height": base.pc(100), "flex-shrink": 0})
    for tuile in LIGNE_TERRAIN:
        place = e.boite(rang, {"width": lw, "height": lh, "flex-shrink": 0, "margin-left": round(ECART_TUILES * k)})
        remap = tuile_fm(e, se, inst, place, tuile, {"position": "absolute", "left": (lw - COLONNE) / 2,
                                                       "top": (lh - RANGEE(4)) / 2})
        e.fab.style_brut(remap, [(327681, [(2, k), (2, k)])])   # scale (comme l'écran), autour du centre
    return len(LIGNE_TERRAIN)


def interrupteur(e, tb, parent, nom, variable):
    """v75 : l'interrupteur de FM (celui de notre bloc, comme celui de la vue) qui montre l'enfant n° <variable>, en
    absolu sur toute la place de son parent, sans clic"""
    t, se = e.t, e.se
    sw = t.clone(se.inter, parent, src=tb)
    for k in list(t.children(sw)):
        t.remove(k)
    t.styles.copy_from(tb.styles, t, sw)
    base.recaler_parent(t, sw)
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
    ss = t.sd(sw)
    ss["name"], ss["name_UxmlAttributeFlags"] = nom, 1
    ss["Binding"]["m_direct"]["Path"]["m_path"] = variable
    t.styles.style(t, sw, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0})
    e.sans_clic(sw)
    return sw


def tuile_fm(e, se, inst, parent, tuile, css=None):
    """une tuile de FM recopiée (v64) : un remappeur (ce que la grille passe à ses tuiles, PASSAGES_TUILES, sauf ce que la
    tuile change) et dedans le modèle de la tuile inclus par son GUID ; tuile = (modèle, GUID, rangées[, changements])"""
    t = e.t
    alias, guid, rangees, *propres = tuile
    propres = propres[0] if propres else {}
    remap = e.seul(se.tr, se.remap, parent)
    sd = t.sd(remap)
    modele = sd["Mappings"][0]
    sd["Mappings"] = [{**json.loads(json.dumps(modele)), "from": de,
                       "to": {**modele["to"], "m_path": propres.get(de, vers)},
                       "type": {**modele["type"], "id": ty}} for de, vers, ty in PASSAGES_TUILES]
    if "Mappings_UxmlAttributeFlags" in sd:
        sd["Mappings_UxmlAttributeFlags"] = 1
    t.styles.style(t, remap, {"width": COLONNE, "height": RANGEE(rangees), "flex-shrink": 0, **(css or {})})
    r = t.clone_shallow(inst, remap)
    base.recaler_parent(t, r)
    el = t.elem(r)
    el["m_TemplateAlias"], el["m_Classes"], el["m_RuleIndex"] = alias, [], -1
    si = t.sd(r)
    if "templateId" in si:
        si["templateId"] = alias
    si["name"], si["name_UxmlAttributeFlags"] = "", 0
    t.styles.style(t, r, {"flex-grow": 1, "flex-shrink": 1})
    usings = t.tt.setdefault("m_Usings", [])
    if not any(u.get("alias") == alias for u in usings):   # à sa place dans l'ordre des noms, comme FM
        cles = [u.get("alias") or "" for u in usings]
        usings.insert(bisect.bisect_left(cles, alias) if cles == sorted(cles) else len(usings),
                      {"alias": alias, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
    e.n += 2
    return remap


# v69 (Kinito, 10/11, v68 vue en 3440 Small : « possible d'ajouter un truc à droite ? », puis « le terrain de gauche de
# Positionnement de l'équipe, qui n'aurait pour choix QUE avec ballon, sans ballon et combiné », puis « le mettre à
# gauche de l'écran et décaler le reste, sans que ça impacte les autres résolutions ») : en vue FM24, une COPIE du
# terrain de l'onglet Positionnement (TacticalPlannerCollapsablePitchesDouble, avec son en-tête : Vue combinée / Avec
# le ballon / Sans le ballon / Les deux) dans une boîte à nous qui déclare ce que l'onglet Positionnement déclare
# (TacticalPlannerTeamShape : son composant de variables — inpossession, tableshowshirts, collapsed,
# selectedpositionmask, dragdropkey — et son composant qui en déduit « avec le ballon » du mode), plus NOTRE « mode »
# (0 : vue combinée), pour ne pas toucher à l'onglet Positionnement, et un repli jamais retenu. « Les deux » et le
# côté droit de l'en-tête (repli, options) sont cachés par nos règles, dans notre copie seulement
# Lu le 10/11 (lecture seule) : le modèle attend team, tactic, dragdropkey, mode, inpossession, selected-tab,
# teaminstructionstab, collapsed, selectedpositionmask ; selected-tab, teaminstructionstab, team et tactic viennent de
# TacticalPlannerBody (au-dessus des deux onglets : vus d'ici aussi) ; mode aussi, MAIS c'est celui que l'en-tête du
# terrain écrit (ButtonGroup : #overview 0, #IP 1, #OOP 2, #both 3), d'où le nôtre. Sous le terrain, à l'échelle Large,
# FM montre ses remplaçants (TacticalPlannerSubsBlock, classe tactics-subs-block, quand le terrain n'est pas replié) :
# cachés aussi dans notre copie (le terrain seul, demandé)
POSITIONNEMENT = "TacticalPlannerTeamShape"
DOUBLE24 = ("TacticalPlannerCollapsablePitchesDouble", "d9631ff4e1974814295dc6478ebaf6b2")
LARGEUR_TERRAIN24 = 6 * CELLULE + 5 * ECART   # 476 : six cases de la grille
# v70 (Kinito, 10/11, v69 vue en 3440 Petit : « notre écran FM24 déborde à gauche sur le terrain et n'est pas aligné
# avec lui ») : mesuré sur sa capture, les blocs de FM commencent ~2 unités APRÈS le bord de la grille (pas 12), en haut
# ~1 avant celui de l'enveloppe, et finissent ~2 au-dessus de son bas. La v69 posait le terrain avec un bord de 12 en haut
# et à gauche, et le panneau du terrain finit 16 au-dessus du bas de son modèle (margin-bottom-16 de FM) : 14 trop bas
# en haut, 14 trop haut en bas, et 6 seulement jusqu'au premier bloc. Maintenant : rien en haut ni à gauche, le modèle
# descend de 14 sous la boîte (coupé par l'enveloppe, c'est le vide de sa marge), et 14 à droite (16 avec les 2 de FM)
DECALE_FM24 = 2                               # où les blocs de FM commencent dans la grille (mesuré)
MARGE_TERRAIN24 = 20   # v70, v71 : 14 ; sur ses captures de la v71, ~10 vus en 3440 Petit, ~8 en 3440 Moyen : la grille de
#                        FM (20 colonnes) ne commence pas au même endroit selon la taille ; 20 : ~16 en 3440 Petit
DESCEND_TERRAIN24 = ECART - DECALE_FM24       # 14 : le panneau finit alors 2 au-dessus du bas, comme les blocs
PLACE_TERRAIN24 = LARGEUR_TERRAIN24 + MARGE_TERRAIN24   # 496 (v70, v71 : 490)
CACHES_TERRAIN24 = (("#", "both"), ("#", "RHS"), (".", "tactics-subs-block"))   # « Les deux », repli et options, remplaçants
# v71 (Kinito, 10/11 : en 3 440 Petit, vue FM24, « à la place du terrain avec un seul dispositif, on met les deux
# terrains, avec et sans ballon » ; « sans boutons ») : le mode « Les deux » de FM (son 2e terrain, dans le modèle, a la
# classe margin-left-8), sans le groupe de boutons de l'en-tête
MODE_LES_DEUX = 3
# v72 (Kinito, 11/11, v71 vue en 3440 Petit : « la même marge entre chaque bloc ») : mesuré sur sa capture, ~3 unités
# entre les deux terrains (margin-left-8 de FM, les panneaux débordent un peu de leur boîte) : 21 à la place, ~16 vus ;
# et la v71 laissait voir les boutons du 1er terrain (la classe de leur groupe, que FM remplace : on cache les boutons
# par leur nom). Les deux terrains prennent toute la place de la 2e boîte (PLACE_DEUX24) et du terrain simple
ECART_DEUX = 21
PLACE_DEUX24 = 600    # v71 : 484 ; voir FIN_DEUX24 (kinito_consignes_essai_b)
# v74 (Kinito, 11/11, v73 vue en jeu, 3 440 Petit : « le avec ballon et sans ballon sont dégueux ») : sur sa capture, les
# deux terrains de FM (mode « Les deux ») ne dépassent pas ~478 de large chacun et se calent à gauche de leur moitié :
# sur 1 076, le 2e s'arrêtait ~50 avant le bord et laissait voir le terrain simple, dessous. Ils font maintenant 476
# chacun (deux moitiés de 476 et l'écart), et partent de la 2e boîte à GAUCHE_DEUX24 : le 2e couvre exactement le
# terrain simple. La 2e boîte garde sa largeur (elle ne paraît toujours qu'en 3 440 Petit)
LARGEUR_DEUX24 = 2 * LARGEUR_TERRAIN24 + ECART_DEUX   # 973 (v71 à v73 : 1 076)
GAUCHE_DEUX24 = PLACE_DEUX24 - LARGEUR_TERRAIN24 - ECART_DEUX   # 103
CACHES_DEUX24 = (("#", "overview"), ("#", "IP"), ("#", "OOP"))
# v73 (Kinito, 11/11 : en vue FM24, « la colonne visualiseur écrit » — la Vue d'ensemble de FM, la colonne de droite de
# la vue Tuiles — « à la place des tuiles », et les tuiles « dans l'espace libre laissé par le cut » : les panneaux
# coupés sous les terrains, même marge que sur les côtés) :
# - la Vue d'ensemble : une COPIE du bloc de FM (PhasesTeamInstructionsBlock, inclus par son GUID) dans une boîte qui
#   déclare sa vue à 0 : nos cartes FM24, posées dans ce bloc, ne s'y montrent qu'en vue 2 (et son miroir aussi) ;
#   coupée sous son contenu (HAUT_VDE, mesuré sur ses captures : ~620), une tuile dessous ;
# - les terrains : le panneau de FM (classe tactics-collapsable-pitch-container) coupé à HAUT_PANNEAU (le terrain y est
#   plafonné à 720 par FM : phases-pitch-max-height ; mesuré sur sa capture 2 560 Petit : ~720 du haut du panneau au bas
#   du terrain) ; dessous, des tuiles, dans une colonne qui cache celles qui ne tiennent pas
VUE_ENSEMBLE = ("PhasesTeamInstructionsBlock", "e2965bf4b1e80064d81c7d5d4ba2c4fe")
LARGEUR_VDE = 4 * CELLULE + 3 * ECART   # 312 : la colonne de FM en vue Tuiles (4 cases)
# v74 (Kinito, 11/11, v73 vue en jeu : « même marge à gauche, à droite et en bas » sur les terrains ; nos blocs FM24
# coupés « pour aligner sur le bas des terrains », les tuiles dans la place libérée, « a minima ensemble ») : mesuré sur
# ses six captures (2 560 et 3 440, Petit et Moyen), la ligne du bas du terrain tombe à ~711 du haut du panneau,
# dispositif comme visualiseur, avec ~10 à 15 de marge sur les côtés : la coupe à 736 en laissait ~25 en bas. Tout est
# coupé à HAUT_PANNEAU (les terrains, nos deux blocs FM24, la copie de la Vue d'ensemble) ; dessous, 16 plus bas
# (HAUT_TERRAIN_COUPE), les tuiles et les remplaçants
HAUT_PANNEAU = 724   # v73 : 736
HAUT_TERRAIN_COUPE = HAUT_PANNEAU + ECART   # 740 : le modèle de Positionnement (sa rangée garde 16 sous le panneau)
HAUT_VDE = HAUT_PANNEAU   # v73 : 650 ; la tuile du centre des données descend dans la ligne des autres
TUILES_SOUS_VDE = [[TUILES[0][0]]]   # centre des données
# v74 : la bande de tuiles de la vue FM24, sous nos blocs coupés : cinq colonnes réparties sur la largeur de la grille,
# au niveau du centre des données (sous la Vue d'ensemble) ; deux rangées en Petit, une en Moyen (une tuile qui ne
# tient pas se cache), les 4 x 4 au bout
BANDE24 = [[TUILES[1][0], TUILES[4][0]],    # rapport prochain adversaire, consignes adverses
           [TUILES[1][1], TUILES[4][1]],    # capitaines, entraînement
           [TUILES[2][0], TUILES[2][1]],    # coups de pied arrêtés, penalties
           [TUILES[3][0]],                  # efficacité tactique
           [TUILES[5][0]]]                  # entraînement individuel
BAS_FM24 = 3   # les blocs de FM finissent ~3 au-dessus du bas de l'intérieur (voir poser_tuiles24 : 20 - 17)
# v74 (Kinito : « la liste des remplaçants sous le dispositif ») : le bloc des remplaçants de FM (celui que l'onglet
# Positionnement montre sous son terrain, R1 à R9), recopié par son GUID ; il attend Tactic et team (l'onglet les a) et
# mode (le terrain de Positionnement le déclare ; ailleurs, une boîte à nous). Moins haut que MIN_REMPLACANTS (son titre
# et une rangée), il se cache
REMPLACANTS = ("TacticalPlannerSubsBlock", "78037b43a1f746740a7dbac11358e5e3")
MIN_REMPLACANTS = 100   # v74 : 140 (en 3 440 Moyen, vue Terrain, il y a ~120 sous le visualiseur : rien ne paraissait)
# v75 (Kinito, 11/11, v74 vue en jeu) — « Information Display » de FM (settings.AdaptiveScalingLevelIndex : Large 0,
# Moyen 1, Petit 2, lu aussi par 26.20) : en Moyen, une seule rangée de tuiles tient sous les blocs coupés (mesuré en
# 3 440 Moyen : ~159 sous les panneaux, une tuile 4 x 2 en fait 148). Notre classe CLASSE_MOYEN, posée par un réglage de
# FM (REGLAGE : reglage_miroir de kinito_consignes_essai_b, qui a les morceaux de FM, posé ici à son chargement),
# choisit les arrangements du Moyen par nos règles :
# - vue FM24 : la rangée à 8 sous les panneaux (au lieu de 16 : seul moyen d'y loger une tuile), six tuiles 4 x 2 (les
#   seules : les 4 x 4 n'y tiennent pas), cinq sous la grille et une sous la Vue d'ensemble ; les remplaçants au même
#   niveau ;
# - vue Terrain : sous l'écran, une rangée de tuiles (LIGNE_TERRAIN), qui ne paraît que s'il reste sa place sous une zone
#   de ZONE_MOYEN (2 560 Moyen, où l'écran rétrécit pour laisser la colonne de gauche ; pas 3 440 Moyen)
CHEMIN_AFFICHAGE, AFFICHAGE_MOYEN = "settings.AdaptiveScalingLevelIndex", 1
CLASSE_MOYEN = "kinito-consignes-affichage-moyen"
REGLAGE = None   # reglage_miroir(t, src, parent, nom, css, index=None, classe=None, vue=..., chemin=None)
BOUTON = None    # bouton_choix (v75, plus utilisé)
SEGMENTS = None  # v76 : segments_choix(t, src, parent, nom, variable, css) : « Dispositif | Visualiseur », boutons
#                  segmentés de FM (comme « Tuiles | Terrain »), le choisi allumé
# v80 (Kinito, 11/11, ses captures EN MATCH à toutes les tailles, « sans impacter la vue hors du match ») : en match,
# la vue Terrain finit sur la ligne de FM (le bas de nos remplaçants, 2 au-dessus du bas de #Body) au lieu de descendre
# encore de DEPASSE_BAS + 2 (« notre écran passe sous le bandeau un peu ; même laisser une petite marge ») ; les blocs de
# FM que la vue couvre, qui descendent jusqu'à la barre du match, sont masqués (leur bas se verrait sous la vue), le
# visualiseur de FM du trou remplacé par notre copie (VISUALISEUR) ; en 3 440 Petit (vue large), ni tuiles sous l'écran
# ni visualiseur à droite, l'écran agrandi (AGRANDI_MATCH). Tout passe par deux classes que deux réglages de FM, vides,
# posent sur leur PARENT (#Body de l'onglet) : CLASSE_MATCH (game.IsDuringMatch, comme ses propres tuiles retirées en
# match) et CLASSE_ONGLET_TERRAIN (kinitovue vaut VUE_TERRAIN). Hors match, aucune règle du match ne s'applique
CLASSE_MATCH = "kinito-consignes-en-match"
CLASSE_ONGLET_TERRAIN = "kinito-consignes-onglet-terrain"
# v87 (Kinito, 11/11 : en 3 440 Petit, hors match, vue FM24, « virer la colonne de droite et agrandir tout le reste »,
# une seule rangée de tuiles) : hors match, rien ne distingue 3 440 Petit de 2 560 Petit par la mise en page (même
# affichage, même hauteur). FMSonde 0.28.1 (ses lectures du 11/11) : FM donne la résolution au skin, en TEXTE
# seulement (settings.selectedresolution.DisplayValue : « 3440 x 1440 », « 2560 x 1440 ») ; l'affichage
# (settings.AdaptiveScalingLevelIndex) vaut 1 en Moyen, 2 en Petit. Trois classes de plus sur #Body, posées par des
# réglages de FM vides : CLASSE_HORS_MATCH et CLASSE_3440 par la fonction de FM qui compare un texte
# (BindStringToAorBUssClass, voir kinito_consignes_essai_b.reglage_texte), CLASSE_PETIT par celle des entiers. Hors
# match : « False » attendu ; s'il s'écrivait autrement, la classe ne serait jamais posée (rien ne change, sans danger)
CLASSE_HORS_MATCH = "kinito-consignes-hors-match"
CLASSE_3440 = "kinito-consignes-ecran-3440"
CLASSE_PETIT = "kinito-consignes-affichage-petit"
CHEMIN_RESOLUTION, TEXTE_3440 = "settings.selectedresolution.DisplayValue", "3440 x 1440"
AFFICHAGE_PETIT = 2
# v88 (Kinito, 11/11, 2 560 Moyen hors match, vue FM24 : « agrandir tout » ; son choix : retirer la colonne de droite et
# la rangée du bas) : l'écran 2 560 x 1440 et l'affichage Moyen sur #Body aussi (CLASSE_MOYEN, elle, est posée par
# chaque réglage Moyen sur lui-même : un autre nom pour #Body)
CLASSE_2560, TEXTE_2560 = "kinito-consignes-ecran-2560", "2560 x 1440"
CLASSE_ONGLET_MOYEN = "kinito-consignes-onglet-moyen"
# v89 (Kinito, 11/11, 3 440 Grand hors match : « fusionner visualiseur et dispo, une colonne de tuiles à droite ») :
# l'affichage Grand (0) sur #Body aussi
CLASSE_ONGLET_GRAND, AFFICHAGE_GRAND = "kinito-consignes-onglet-grand", 0
REGLAGE_TEXTE = None   # reglage_texte(t, parent, nom, chemin, texte, classe, css) : classe sur le parent si le texte
#                        lu sous chemin vaut texte (kinito_consignes_essai_b)
# v82 : la vue FM24 aussi sur #Body (kinitovue vaut VUE_FM24), pour l'ajusteur de la vue FM24 en match
# (kinito_consignes_essai_b.poser_fm24_match). v81 : l'affichage Petit / Moyen sur #Body, RETIRÉ : la classe posée
# d'après settings.AdaptiveScalingLevelIndex ne suivait pas un changement d'affichage pendant le match
CLASSE_ONGLET_FM24 = "kinito-consignes-onglet-fm24"
REGLAGE_MATCH = None    # reglage_match(t, parent, nom, classe, css) : la classe sur le parent en match
#                         (kinito_consignes_essai_b)
REGLAGE_PARENT = None   # reglage_parent(t, src, parent, nom, chemin, valeur, classe, css) : la classe sur le parent si
#                         chemin vaut valeur
AGRANDI_MATCH = 2.0     # en match, l'écran DESSINÉ à 2 au lieu d'AGRANDI : l'ajusteur de FM le réduit pour qu'il tienne.
#                         Seule la vue large (3 440 Petit) était plafonnée par AGRANDI (son cadre, en match, ~1 113 de haut
#                         pour un écran de 967) : partout ailleurs, l'écran est déjà plus petit qu'AGRANDI, rien ne change
VISIBILITE = 65551      # StylePropertyId.Visibility (lu dans les feuilles de FM, SIStyles : « visible » / « hidden »)
ID_ECHELLE = 327681     # StylePropertyId.Scale
CASES_ONGLET = ("TeamInstructionsPitch", "TeamInstructionsBlock", "PhasesAndTeamInstructions")   # les trois blocs de FM
HAUT_RANGEE_MOYEN = HAUT_PANNEAU + 8   # 732
# v87 (Kinito, 11/11, 3 440 Petit hors match : une seule rangée ; son choix : rapport, capitaines, CPA, consignes
# particulières à la place de l'efficacité) : la bande a cinq places sous la grille (pas quatre, comme je le lui avais
# dit) : penalties à la 5e
BANDE24_3440 = [[TUILES[1][0]], [TUILES[1][1]], [TUILES[2][0]], [TUILES[4][0]], [TUILES[2][1]]]
# v88 (Kinito, 11/11, 2 560 Petit hors match : « le visualiseur en choix sur le dispo, tout décaler, enlever la colonne
# Vue d'ensemble, une seule ligne de tuiles, remplaçants coupés au bas de la ligne de tuiles » ; ses choix : trois tuiles
# réparties, « prochain adversaire, CPA et capitaines »)
BANDE24_2560 = [[TUILES[1][0]], [TUILES[2][0]], [TUILES[1][1]]]
BANDE24_MOYEN = [[TUILES[1][0]], [TUILES[4][0]], [TUILES[1][1]], [TUILES[2][0]], [TUILES[2][1]]]   # rapport,
#                                                    consignes particulières, capitaines, CPA, penalties
TUILES_SOUS_VDE_MOYEN = [[TUILES[4][1]]]   # entraînement
# v85 (Kinito, 11/11 : « en Moyen, virer la colonne Vue d'ensemble et ajouter 3 tuiles, 2 hautes et une comme celle du
# bas » ; ses choix : Efficacité tactique et Centre des données, Entraînement gardé en bas) : en Moyen, vue FM24, la
# copie de la Vue d'ensemble cachée et, à sa place (HAUT_VDE, 724), ces deux tuiles 4 x 4 l'une sous l'autre (312 + 12 +
# 312) ; la tuile de la rangée (TUILES_SOUS_VDE_MOYEN) ne change pas. Les règles ne lisent pas la largeur : 3 440 et
# 2 560 Moyen ensemble. En Petit, rien ne change
TUILES_HAUTES_MOYEN = [[TUILES[3][0], TUILES[0][0]]]   # efficacité tactique, centre des données
# v75 (Kinito : « couper la tuile des remplaçants au niveau du bas des tuiles de droite ») : en Petit, les remplaçants
# s'arrêtent au bas de la 2e rangée de la bande (deux rangées : 308)
HAUT_REMPLACANTS = 2 * RANGEE(2) + ECART_TUILES   # 308. v75 : RANGEE(2), une seule rangée (Kinito, v75 vue en
#                                                   2 560 Petit : « au bas de la 2e rangée, pas de la 1re »)
# v76 (Kinito, 3 440 Petit, vue FM24 : « 2 ou 3 tuiles pertinentes sous les remplaçants » ; son choix : dynamique,
# blessés, retours tactique) : sous les deux terrains, les remplaçants sur une rangée (148), ces trois tuiles dessous.
# Ni dans la grille de l'onglet ni dans nos tuiles : GUID lus dans les descriptions de tuiles de FM (ui-tileslayouts :
# SquadDynamicsTileDescription, SquadCurrentInjuriesTileDescription, OnThePitchTacticsFeedbackTileDescription) ; elles
# n'attendent que team (et isonmainscreen, facultatif) : nos remappeurs les passent
FOND_PAGE24 = (14 / 255, 16 / 255, 32 / 255, 1.0)   # v77 : la page de FM sous la bande (sa capture 3 440 Petit)
TUILES_SOUS_DEUX24 = [("SquadDynamicsTile_4x2", "d8dd200c9b102754ca4dfd0974b8f900", 2),
                      ("SquadCurrentInjuriesTile_4x2", "76c1231ee9eceed468d4e8a11c69e0ec", 2),
                      ("TacticsFeedbackTile_4x2", "d0f28a30066cc2f4593dd72fd9806160", 2)]
# v89 (Kinito, 11/11, 3 440 Moyen hors match : « on fusionne le visualiseur et le dispo, on décale tout à gauche et on
# ajoute des tuiles à droite » ; ma proposition, acceptée) : deux colonnes de plus après celle de la Vue d'ensemble
# (Efficacité, Centre des données, Entraînement à la rangée), cachées sauf en 3 440 Moyen (kinito_consignes_essai_b) :
# (tuiles du haut, tuiles de la rangée du Moyen)
COLS_3440_MOYEN = [([TUILES[5][0], TUILES_SOUS_DEUX24[0]], [TUILES[2][1]]),   # entr. individuel, dynamique ; penalties
                   ([TUILES[4][0], TUILES_SOUS_DEUX24[1], TUILES_SOUS_DEUX24[2]], [])]   # consignes part., blessés,
#                                                                                         retours tactique
# v90 (Kinito, 11/11, 3 440 Petit fusionné ; ma proposition, acceptée) : la 2e colonne de droite, cinq petites tuiles
COL_3440_PETIT = [TUILES[1][0], TUILES[1][1], TUILES[2][0], TUILES[2][1], TUILES[4][0]]   # rapport, capitaines, CPA,
#                                                                                           penalties, consignes part.
# v92 (Kinito, 11/11, v90 vue en 2 560 Petit : « une 3e grande tuile ne passe pas ? ») : je lui avais dit non (960 de
# haut pour ~905 : hauteur estimée). Sa mesure FMSonde (2 560 Petit hors match : #Body 2 443 x 1 199) : à x1,24, la
# colonne a ~967 : trois grandes tuiles passent. Son vœu d'origine : Data hub, Efficacité, Entraînement individuel
COL_2560_PETIT = [TUILES[3][0], TUILES[0][0], TUILES[5][0]]   # efficacité, centre des données, entr. individuel
# v75 (Kinito, vue Terrain : « mettre le dispositif à la place du visualiseur, avec un bouton pour passer au
# visualiseur ») : la colonne de gauche (le trou) montre notre dispositif, un bouton « Visualiseur » laisse voir celui
# de FM (dessous), un bouton « Dispositif » ramène ; VAR_GAUCHE (0 dispositif, 1 visualiseur), déclarée par notre boîte
# (pas retenue : le dispositif revient à chaque ouverture). Boutons posés à côté des boutons de FM, mesurés sur ses
# captures (3 440 Moyen) : « Vue combinée / Avec / Sans » du dispositif de x 15 à 256, y 16 à 48 ; « Avec / Sans » du
# visualiseur de x 8 à 168, y 11 à 44
VAR_GAUCHE = "kinitogauche"
# v76 (Kinito, v75 vue en 2 560 Petit : « le texte n'est pas centré ; mets-le en switch comme vue combinée / avec / sans,
# à droite ») : un seul choix « Dispositif | Visualiseur », boutons segmentés de FM, à droite de l'en-tête, aux deux états
POS_CHOIX = {"right": 14, "top": 13}   # v76 à v80 (plus lu depuis la v81)
# v81 (Kinito, 11/11 : « le bouton Dispositif / Visualiseur n'est pas aligné et pas de la bonne couleur quand il est
# allumé par rapport aux boutons Vue combinée » ; « possible de mettre un seul bouton ? en plus grande taille de police
# les boutons se chevauchent ; une icône visualiseur pour aller sur visualiseur et une icône dispo pour switch sur
# dispo ») : UN bouton, une icône de FM et pas de texte, qui mène à l'autre panneau. Sur le dispositif, il montre le
# petit terrain (le visualiseur) ; sur le visualiseur, les joueurs en place (le dispositif). Calé sur les boutons de
# l'en-tête de chaque panneau, mesurés par FMSonde 0.28.0 (3 440 Petit, en match) : dispositif, « Vue combinée » à 16
# du haut, 32 de haut ; visualiseur, « Avec / Sans » de 11 à 44 (ses captures). À 14 du bord droit, comme ceux de FM
# à 14 du bord gauche
ICONE_VERS_VISUALISEUR = "game-concepts-position-visualiser-midfield"   # le petit terrain de FM
ICONE_VERS_DISPOSITIF = "game-concepts-shape-ip"                        # les joueurs en place, de FM
BASCULE_L, BASCULE_ICONE = 40, 20
BASCULE_SUR_DISPOSITIF = {"right": 14, "top": 16, "width": BASCULE_L, "height": 32}
BASCULE_SUR_VISUALISEUR = {"right": 14, "top": 11, "width": BASCULE_L, "height": 33}
# v76 (Kinito : en vue FM24, quand le terrain est seul — 1080p, 2 560 Moyen et Grand —, le dispositif par défaut et le
# choix du visualiseur ; son choix : le miroir gardé, ce terrain reste donc à droite) : notre dispositif par-dessus le
# visualiseur de FM, avec le même choix. Il ne doit paraître que si le terrain de Positionnement (à gauche) ne paraît
# pas : une boîte de largeur 0 juste APRÈS lui dans l'enveloppe passe à la ligne avec lui ; posé depuis elle à -100 % de
# sa hauteur (en haut de l'enveloppe), le dispositif n'est dans l'enveloppe que quand cette boîte est sur la 2e ligne
# (à PLACE_DEUX24 du bord : la 2e boîte des deux terrains passe à la ligne avec elle) ; sur la 1re ligne, il est
# au-dessus, coupé. X_VISU24 : le bord gauche du visualiseur de FM dans l'intérieur (grille retournée), mesuré sur ses
# captures (2 560 Petit et Moyen, 3 440 Moyen : 1 146 à 1 150)
X_VISU24 = 1147
X_VISU24_FM27 = 1   # v79 : dans l'ordre FM 27 (grille non retournée), le visualiseur commence au bord : 1 624 - 1 147 - 476
# v75 (Kinito, 2 560 Moyen, vue Terrain : « réduire la taille du terrain pour avoir dispositif + visualiseur sur la
# colonne de gauche, remplaçants en dessous, et une ligne de tuiles sous les consignes ») : la colonne de gauche paraît
# dès que l'écran a LARGE_MIN à côté d'elle (v63 à v74 : sa largeur, 1 624) : 2 560 Moyen (~2 017 de large) l'a
# maintenant, l'écran y rétrécit (~1 525 de large, ~677 de haut) ; 1080p (Petit ~1 847, Large ~1 624) ne l'a pas
# v77 (Kinito, v76 vue en jeu : en 2 560 Grand et en 1080p, vue Terrain, « réduire les consignes pour y faire entrer le
# dispo / visualiseur à gauche, et des tuiles en bas ») : dès 1 100 à côté d'elle (v75, v76 : 1 480) : 1080p Large
# (~1 624 de large : l'écran y passe à ~1 132, ~70 % de sa taille d'avant) et Petit (~1 847), 2 560 Grand (~1 700) l'ont ;
# 1080p Moyen (~1 513) non
LARGE_MIN = 1480   # v78 (Kinito, v77 vue en jeu : « en 1080p et en 2 560 Grand, vue Terrain, on remet la version où
#                    c'était que les consignes, c'est mieux ») : de nouveau 1 480 (v77 : 1 100)
# v76 (Kinito, v75 vue en 2 560 Moyen : « les tuiles ne vont pas du tout là », la 5e dépassait sous les quatre) : quatre
# (cinq demandent 1 568, l'écran n'y a que ~1 525 ; le centre des données, 312 de haut, n'a pas sa place), dans une
# rangée de leur hauteur exacte (une tuile passée à la ligne ne dépasse plus), juste sous l'écran : la zone part de
# ZONE_MOYEN, la rangée de LIGNE_MOYEN (leur somme, 940, tient en 2 560 Moyen ~966 et pas en 3 440 Moyen ~883)
# v78 (Kinito, 2 560 Moyen : « remplir le bandeau du bas » ; son choix parmi quatre : « 6 grandes tuiles réduites »,
# le centre des données tout à droite) : les versions 4 x 4 des tuiles, dessinées à ECHELLE_LIGNE (~254 de haut sous
# l'écran : 312 x 0,76 = 237) ; six sur la largeur (6 x 231 + 5 x 9 = 1 431 pour ~1 525). GUID lus dans les descriptions
# de tuiles de FM (ui-tileslayouts) ; elles n'attendent que team (le rapport : l'adversaire, comme en 4 x 2)
LIGNE_TERRAIN = [("TeamOrOppositionReportTile_4x4", "cabd8a5f7c66332428bf9b52c843ef2a", 4,
                  {"team": "Team.NextMatchOpponent"}),                                     # rapport prochain adversaire
                 ("OppositionInstructionsTile_4x4", "88833199a2a38d94e845cc48dd43f204", 4),   # consignes particulières
                 ("SquadCaptainsTile_4x4", "00a434379c30251468f1b96ab1e7ccd7", 4),             # capitaines
                 ("SetPiecesTile_4x4", "480cb417c12b8554cbf05cb2ac019bf2", 4),                 # coups de pied arrêtés
                 TUILES[3][0],                                                                 # efficacité tactique
                 TUILES[0][0]]                                                                 # centre des données
ECHELLE_LIGNE = 0.76
# v77 : la rangée n'est plus dans le cadre (v75, v76 : une zone réduite en Moyen) mais posée par-dessus, à 16 sous
# l'écran : quand l'écran est limité par sa largeur (1080p, 2 560 Grand et Moyen, à côté de la colonne de gauche), sa
# hauteur vaut 720 / 1 622 de la largeur du cadre ; une marge du haut en % se compte sur la LARGEUR du parent : la
# rangée tombe juste dessous, sans rien changer à l'écran. Limité par sa hauteur (3 440 Moyen et Grand), l'écran est
# moins haut que cette marge : la rangée part sous le bas du cadre, cachée (un repère vide la cache aussi si elle ne
# tient pas entière). En Petit, rien (la bande de quatre rangées, ou la vue large) : notre classe CLASSE_PETIT
CLASSE_PETIT, AFFICHAGE_PETIT = "kinito-consignes-affichage-petit", 2


def _composant(t, ts, ce_src, comp, ce):
    """recopie le composant comp (son élément et ses données, comme poser_ecran de 26.13) du ComponentElement ce_src
    (modèle ts) dans le ComponentElement ce ; rend (élément, données)"""
    rang = sum(1 for k in t.children(ce) if (t.elem(k).get("m_FullTypeName") or "").endswith("Component"))
    r = t.clone(comp, ce, rang, src=ts)
    base.recaler_parent(t, r)
    ident = ts.elem(comp)["m_Id"]
    src_d = next((ts.refs[c["rid"]] for c in ts.sd(ce_src).get("m_components") or []
                  if (ts.refs[c["rid"]].get("data") or {}).get("uxmlAssetId") == ident), None)
    if src_d is None:
        raise ValueError(f"{POSITIONNEMENT} : données d'un composant (introuvables)")
    d = copy.deepcopy(src_d)
    d["rid"] = t.new_rid()
    d["data"]["uxmlAssetId"] = t.elem(r)["m_Id"]
    t.refs[d["rid"]] = d
    t.tt["references"]["RefIds"].append(d)
    s = t.sd(ce)
    s.setdefault("m_components", []).append({"rid": d["rid"]})
    s["m_components_UxmlAttributeFlags"] = 1
    return r, d["data"]


def _sources_positionnement():
    """v73 (sorti de poser_terrain24) : l'onglet Positionnement de FM, son ComponentElement racine et ses deux composants
    (variables, et celui qui en déduit « avec le ballon ») : (modèle, racine, variables, déduction)"""
    o = ouvrir(POSITIONNEMENT, depart_original=True)
    if not o:
        raise ValueError(f"{POSITIONNEMENT} (introuvable)")
    ts = o[3]

    def prop(tr, r, nom_p):
        return next((p.get("value") or "" for p in tr.elem(r).get("m_Properties") or [] if p.get("name") == nom_p), "")
    var = first(ts, lambda r: ts.elem(r).get("m_FullTypeName") == "SI.Bindable.BindingVariablesComponent"
                and "{inpossession}" in prop(ts, r, "value-vars") and "{collapsed}" in prop(ts, r, "value-vars"))
    fixe = first(ts, lambda r: ts.elem(r).get("m_FullTypeName") == "SI.Bindable.BindingSetterComponent"
                 and "ffe24c8d" in prop(ts, r, "bind-funcs"))
    if var is None or fixe is None or ts.parent[var] != ts.parent[fixe]:
        raise ValueError(f"{POSITIONNEMENT} : composants de variables (introuvables)")
    return ts, ts.parent[var], var, fixe


def _boite_ce(t, parent, nom, css):
    """v73 (sorti de poser_terrain24) : un ComponentElement à nous (la racine de l'onglet recopiée vide), qui peut porter
    des composants ; rend (élément, modèle inclus de l'onglet)"""
    racine_onglet = first(t, lambda r: typ(t, r) == "ComponentElement")
    inst = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == INSTANCE_ONGLET)
    if racine_onglet is None or inst is None:
        raise ValueError("élément racine ou modèle inclus de l'onglet (introuvable)")
    boite = t.clone_shallow(racine_onglet, parent)
    base.recaler_parent(t, boite)
    el = t.elem(boite)
    el["m_Classes"], el["m_RuleIndex"] = [], -1
    for k in ("m_Stylesheets", "m_StylesheetPaths"):
        if el.get(k):
            el[k] = []
    sb = t.sd(boite)
    sb["m_components"] = []
    sb["name"], sb["name_UxmlAttributeFlags"] = nom, 1
    t.styles.style(t, boite, css)
    return boite, inst


def boite_variables(t, parent, nom, variables, css):
    """v74 (v73 : boite_vue) : une boîte qui déclare ses propres variables entières (variables = {nom: valeur}) : ce qui
    est dessous les lit là (le composant de variables de l'onglet Positionnement recopié, sa déclaration remplacée) ;
    rend (élément, modèle inclus)"""
    ts, ce_src, var, _ = _sources_positionnement()
    boite, inst = _boite_ce(t, parent, nom, css)
    rv, dv = _composant(t, ts, ce_src, var, boite)
    pv = next((p for p in t.elem(rv).get("m_Properties") or [] if p.get("name") == "value-vars"), None)
    vals = dv.get("ValueVariables") or []
    entier = next((v for v in vals if (v.get("m_scopeValue") or {}).get("m_serializedData", "").startswith("Int|")), None)
    if pv is None or entier is None:
        raise ValueError(f"{POSITIONNEMENT} : variables : forme inattendue (introuvables)")
    pv["value"] = ",".join(f"{{{n}}}{{Int|{v}|}}" for n, v in variables.items())
    nouvelles = []
    for n, v in variables.items():
        vv = copy.deepcopy(entier)
        vv["m_name"], vv["m_scopeValue"]["m_serializedData"] = n, f"Int|{v}|"
        nouvelles.append(vv)
    dv["ValueVariables"] = nouvelles
    return boite, inst


def boite_vue(t, parent, nom, vue, css):
    """v73 : une boîte qui déclare sa propre vue (base.VARIABLE = vue)"""
    return boite_variables(t, parent, nom, {base.VARIABLE: vue}, css)


def _ecran_boites(t, src, tb):
    """v74 : de quoi poser nos boîtes simples et des tuiles dans l'onglet (comme boite24) ; rend l'Ecran"""
    se = SourcesEcran(src, tb)
    racine = first(t, lambda r: est_racine(t.name(r)))
    if se.remap is None or racine is None:
        raise ValueError("remappeur de FM ou écran plein (introuvables)")
    e = Ecran(t, src, se, None)
    e.fab.proto = racine
    return e


def poser_remplacants(t, src, tb, inst, parent, nom, css):
    """v74 : le bloc des remplaçants de FM (REMPLACANTS) dans une zone qui le cache s'il n'a pas MIN_REMPLACANTS (une
    colonne qui passe à la ligne, derrière un repère vide : le bloc part à droite, caché) ; sinon il prend toute la
    zone (il défile lui-même). Rend la zone"""
    e = _ecran_boites(t, src, tb)
    zone = e.boite(parent, {"flex-direction": "column", "flex-wrap": "wrap", "align-content": "flex-start",
                            "overflow": "hidden", **css}, nom=nom)
    e.boite(zone, {"width": base.pc(100), "height": 0, "flex-shrink": 0})
    inclure_modele(t, inst, zone, REMPLACANTS, {"width": base.pc(100), "flex-basis": MIN_REMPLACANTS,
                                                "flex-grow": 1, "flex-shrink": 0})
    return zone


def poser_terrain24(t, src, tb, parent, nom, mode=0, css=None, descend=DESCEND_TERRAIN24, hauteur=None,
                    remplacants=False, bas=BAS_FM24, tuiles_dessous=None):
    """v69 : la boîte du terrain de Positionnement (voir POSITIONNEMENT) ; rend son élément. v71 : mode de départ (0 vue
    combinée, 3 les deux terrains : MODE_LES_DEUX), style de la boîte (css, sinon celui de la vue FM24), et de combien
    le modèle descend sous elle (descend). v73 : hauteur, le modèle à cette hauteur (coupé sous son terrain). v74 :
    remplacants, le bloc des remplaçants dessous (à HAUT_TERRAIN_COUPE, jusqu'à « bas » du bas de la boîte)"""
    ts, ce_src, var, fixe = _sources_positionnement()
    boite, inst = _boite_ce(t, parent, nom, css or {"width": LARGEUR_TERRAIN24, "height": base.pc(100),
                                                   "flex-shrink": 0, "flex-grow": 0, "margin-right": MARGE_TERRAIN24,
                                                   "flex-direction": "column"})
    rv, dv = _composant(t, ts, ce_src, var, boite)
    _composant(t, ts, ce_src, fixe, boite)
    # le repli : jamais retenu (celui de FM l'est, « tactics-collapsed-pitches ») ; notre « mode » : vue combinée
    pv = next((p for p in t.elem(rv).get("m_Properties") or [] if p.get("name") == "value-vars"), None)
    morceaux = [("{collapsed}{Bool|0|}" if m.startswith("{collapsed}") else m) for m in pv["value"].split(",")]
    if not any(m.startswith("{collapsed}") for m in morceaux) or any(m.startswith("{mode}") for m in morceaux):
        raise ValueError(f"{POSITIONNEMENT} : variables : forme inattendue (introuvables)")
    pv["value"] = ",".join(morceaux + [f"{{mode}}{{Int|{mode}|}}"])
    vals = dv.get("ValueVariables") or []
    rep = next((v for v in vals if v.get("m_name") == "collapsed"), None)
    entier = next((v for v in vals if (v.get("m_scopeValue") or {}).get("m_serializedData", "").startswith("Int|")), None)
    if rep is None or entier is None:
        raise ValueError(f"{POSITIONNEMENT} : variables : forme inattendue (introuvables)")
    rep["m_scopeValue"]["m_serializedData"] = "Bool|0|"
    vm = copy.deepcopy(entier)
    vm["m_name"], vm["m_scopeValue"]["m_serializedData"] = "mode", f"Int|{mode}|"
    vals.append(vm)
    # le terrain de Positionnement, inclus par son GUID
    # v73 : coupé, il descend toujours de « descend » sous sa place (rétréci sur un écran bas, son panneau finit au
    # même endroit qu'avant) ; ce qui le suit commence donc à hauteur - descend (les remplaçants)
    inclure_modele(t, inst, boite, DOUBLE24, {"height": hauteur, "flex-grow": 0, "flex-shrink": 1,
                                              "margin-bottom": -descend} if hauteur else
                   {"flex-grow": 1, "flex-shrink": 1, "margin-bottom": -descend})
    if remplacants and hauteur:   # v74
        # v75 : dans un réglage Moyen ; leur marge du haut (au niveau de la bande) et leur hauteur (en Petit, jusqu'au
        # bas de sa 2e rangée) viennent de nos règles : un style intégré passerait devant
        dessus = HAUT_TERRAIN_COUPE - (hauteur - descend)   # 14
        # v76 : avec des tuiles dessous (tuiles_dessous), les remplaçants sur une rangée de tuile (148), à leur hauteur
        # v77 : min / max (le réglage de FM remplace hauteur et largeur par « auto » : v76, la hauteur perdue, les
        # remplaçants n'avaient plus de place)
        h_reg = dessus + RANGEE(2) + bas
        css_reg = ({"min-height": h_reg, "max-height": h_reg, "flex-grow": 0, "flex-shrink": 0,
                    "flex-direction": "column"}
                   if tuiles_dessous else
                   {"flex-grow": 1, "flex-basis": 0, "min-height": 0, "flex-direction": "column"})
        reg = REGLAGE(t, src, boite, f"{nom}-remplacants-reglage", css_reg,
                      classe=CLASSE_MOYEN, vue=AFFICHAGE_MOYEN, chemin=CHEMIN_AFFICHAGE)
        zone_r = f"{nom}-remplacants"
        poser_remplacants(t, src, tb, inst, reg, zone_r, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                                                           "min-height": 0, "padding-bottom": bas})
        haut = base.sm.PROPRIETES["padding-top"][0]
        plafond = base.sm.PROPRIETES["max-height"][0]
        regle_selecteurs(t, [(haut, "", [(3, {"unit": 1, "value": float(dessus)})]),
                             (plafond, "", [(3, {"unit": 1, "value": float(dessus + HAUT_REMPLACANTS + bas)})])],
                         75.0, [[(TYPE_NOM, zone_r, 0)]])
        regle_selecteurs(t, [(haut, "", [(3, {"unit": 1, "value": float(dessus - (HAUT_TERRAIN_COUPE
                                                                                     - HAUT_RANGEE_MOYEN))})])],
                         75.1, [[(TYPE_CLASSE, CLASSE_MOYEN, 0), (TYPE_NOM, zone_r, DESCENDANT)]])
        attacher_feuille(t, reg)
        if tuiles_dessous:   # v76 : une rangée centrée, à 12 sous la rangée des remplaçants
            e = _ecran_boites(t, src, tb)
            # v77 : dessous, les remplaçants du terrain simple (deux rangées, sous le 2e terrain) se voyaient entre les
            # tuiles : un fond de la couleur de la page les couvre (mesurée sur sa capture : ~14, 16, 32)
            e.boite(boite, {"position": "absolute", "left": LARGEUR_TERRAIN24 + ECART_DEUX - 2,
                            "top": HAUT_TERRAIN_COUPE + RANGEE(2), "width": LARGEUR_TERRAIN24 + 4,
                            "height": ECART_TUILES + RANGEE(2) + bas + 4, "background-color": FOND_PAGE24},
                    nom=f"{nom}-fond")
            rang = e.boite(boite, {"height": RANGEE(2), "flex-shrink": 0, "flex-direction": "row",
                                   "justify-content": "center", "margin-top": ECART_TUILES - bas},
                           nom=f"{nom}-tuiles")
            for i, tuile in enumerate(tuiles_dessous):
                tuile_fm(e, e.se, inst, rang, tuile, {"margin-left": ECART_TUILES if i else 0})
    return boite


def poser_bande24(t, src, tb, parent, nom, largeur, visu_droite=False):
    """v74 : la bande de tuiles de la vue FM24 (BANDE24), sous nos blocs coupés (en absolu dans l'intérieur, sur la
    largeur de la grille) : cinq colonnes réparties, chacune derrière un repère vide (une tuile qui ne tient pas en
    hauteur se cache). v75 : dans un réglage Moyen (qui porte nom, couvre l'intérieur et ne prend pas les clics) :
    BANDE24 en Petit, BANDE24_MOYEN (une rangée à HAUT_RANGEE_MOYEN) en Moyen. Rend le nombre de tuiles"""
    e = _ecran_boites(t, src, tb)
    inst = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == INSTANCE_ONGLET)
    if inst is None:
        raise ValueError("modèle inclus de l'onglet (introuvable)")
    reg = REGLAGE(t, src, parent, nom, {"position": "absolute", "left": 0, "top": 0, "width": largeur, "bottom": 0},
                  classe=CLASSE_MOYEN, vue=AFFICHAGE_MOYEN, chemin=CHEMIN_AFFICHAGE)
    e.sans_clic(reg)
    n = 0
    for fin, colonnes, haut, bas in (("-petit", BANDE24, HAUT_TERRAIN_COUPE, BAS_FM24),
                                     ("-moyen", BANDE24_MOYEN, HAUT_RANGEE_MOYEN, 0),
                                     ("-grand", BANDE24_3440, HAUT_TERRAIN_COUPE, BAS_FM24)):   # v87
        bande = e.boite(reg, {"position": "absolute", "left": DECALE_FM24, "top": haut,
                              "width": largeur - 2 * DECALE_FM24, "bottom": bas, "flex-direction": "row",
                              "justify-content": "space-between", "overflow": "hidden"}, nom=f"{nom}{fin}")
        for colonne in colonnes:
            col = e.boite(bande, {"width": COLONNE, "height": base.pc(100), "flex-shrink": 0,
                                  "flex-direction": "column", "flex-wrap": "wrap", "align-content": "flex-start",
                                  "overflow": "hidden"})
            e.boite(col, {"width": base.pc(100), "height": 0, "flex-shrink": 0})
            for tuile in colonne:   # v76 : en Moyen, une rangée sans écart dessous (v75 : 12 ; en 3 440 Moyen la
                #                      tuile demandait alors 160 pour ~151 : elle ne paraissait pas)
                tuile_fm(e, e.se, inst, col, tuile, {"margin-bottom": ECART_TUILES if fin == "-petit" else 0})
                n += 1
    # v88 (voir BANDE24_2560) : sous le panneau unique, les remplaçants (une rangée, dans une boîte qui déclare mode,
    # comme ceux de la vue Terrain), puis les tuiles réparties sous les consignes et les phases ; le panneau est à droite
    # de la grille dans la disposition miroir (visu_droite), à gauche dans l'ordre FM 27
    # v89 : la même au niveau de la rangée du Moyen (« -seul-moyen », 3 440 Moyen fusionné)
    for fin, haut, bas in (("-seul", HAUT_TERRAIN_COUPE, BAS_FM24), ("-seul-moyen", HAUT_RANGEE_MOYEN, 0)):
        seul = e.boite(reg, {"position": "absolute", "left": DECALE_FM24, "top": haut,
                             "width": largeur - 2 * DECALE_FM24, "bottom": bas,
                             "flex-direction": "row-reverse" if visu_droite else "row", "overflow": "hidden"},
                       nom=f"{nom}{fin}")
        boite_r, _ = boite_variables(t, seul, f"{nom}{fin}-remplacants", {"mode": 0},
                                     {"width": LARGEUR_TERRAIN24, "height": RANGEE(2), "flex-shrink": 0,
                                      "flex-direction": "column"})
        poser_remplacants(t, src, tb, inst, boite_r, f"{nom}{fin}-remplacants-zone",
                          {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
        # v93 (Kinito, v92 vue en 2 560 Petit : les trois petites toujours écartées) : « justify-content » n'est plus
        # dans le style intégré (il passait devant la règle qui centre) : règle 93.0 (réparties) ou celle du 2 560 Petit
        # (centrées) ; chaque colonne nommée (« -1 » à « -3 ») pour leur écart
        tuiles = e.boite(seul, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "flex-direction": "row",
                                "margin-right" if visu_droite else "margin-left": ECART_TUILES},
                         nom=f"{nom}{fin}-tuiles")   # v90 : nommée (le 3 440 Petit fusionné la cache)
        regle_selecteurs(t, [(base.sm.PROPRIETES["justify-content"][0], "", [(7, "space-between")])], 93.0,
                         [[(TYPE_NOM, f"{nom}{fin}-tuiles", 0)]])
        for i, colonne in enumerate(BANDE24_2560, start=1):
            col = e.boite(tuiles, {"width": COLONNE, "height": base.pc(100), "flex-shrink": 0,
                                   "flex-direction": "column", "flex-wrap": "wrap", "align-content": "flex-start",
                                   "overflow": "hidden"}, nom=f"{nom}{fin}-tuiles-{i}")
            e.boite(col, {"width": base.pc(100), "height": 0, "flex-shrink": 0})
            for tuile in colonne:
                tuile_fm(e, e.se, inst, col, tuile, {"margin-bottom": 0})
                n += 1
    selon_moyen(t, f"{nom}-petit", f"{nom}-moyen", 75.3)
    # v87 : la rangée du 3 440 Petit cachée ; kinito_consignes_essai_b.poser_3440 la montre (et cache « -petit »).
    # v88 : la rangée du 2 560 Petit aussi. v89 : celle du 3 440 Moyen
    regle_selecteurs(t, [(base.sm.PROPRIETES["display"][0], "", [(7, "none")])], 87.0,
                     [[(TYPE_NOM, f"{nom}{x}", 0)] for x in ("-grand", "-seul", "-seul-moyen")])
    attacher_feuille(t, reg)
    return n


def poser_vde24(e, se, inst, src, tb, parent, nom):
    """v73 : la Vue d'ensemble de FM (voir VUE_ENSEMBLE) dans sa boîte de vue 0, coupée à HAUT_VDE, et la tuile dessous ;
    rend le nombre de tuiles"""
    t = e.t
    boite, _ = boite_vue(t, parent, nom, VUE_TUILES, {"width": LARGEUR_VDE, "height": base.pc(100), "flex-shrink": 0,
                                                     "flex-grow": 0, "margin-left": ECART_TUILES,
                                                     "flex-direction": "column"})
    # v85 (voir TUILES_HAUTES_MOYEN) : la Vue d'ensemble dans un réglage Moyen, à côté des deux tuiles hautes du Moyen ;
    # l'une ou l'autre selon l'affichage (selon_moyen). v73 à v84 : la Vue d'ensemble seule, à HAUT_VDE
    # v86 (Kinito, v85 vue en 3 440 Moyen : ni Efficacité ni Centre des données, Entraînement en haut de la colonne) :
    # le réglage de FM remet hauteur et largeur à « auto » (reglage_miroir) : la zone tombait à 0. Sa hauteur par
    # flex-basis, qu'il ne touche pas (v85 : height)
    haut = REGLAGE(t, src, boite, f"{nom}-haut", {"flex-basis": HAUT_VDE, "flex-grow": 0, "flex-shrink": 1,
                                                  "min-height": 0, "flex-direction": "column"},
                   classe=CLASSE_MOYEN, vue=AFFICHAGE_MOYEN, chemin=CHEMIN_AFFICHAGE)
    vde = e.boite(haut, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "flex-direction": "column"},
                  nom=f"{nom}-fm")
    inclure_modele(t, inst, vde, VUE_ENSEMBLE, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
    n_hautes = colonnes_tuiles(e, se, inst, haut, TUILES_HAUTES_MOYEN,
                               {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                                "margin-left": -8, "margin-right": -8}, f"{nom}-hautes", tete=True)
    selon_moyen(t, f"{nom}-fm", f"{nom}-hautes", 85.0)
    attacher_feuille(t, haut)
    # la colonne (304, et son écart de 12 devant) dans la boîte de 312 : la zone déborde de 8 de chaque côté, la tuile
    # tombe à 4 du bord, centrée
    # v75 : dans un réglage Moyen : le centre des données (Petit), ou une tuile 4 x 2 au niveau de la rangée (Moyen ; sa
    # zone descend de 3 jusqu'au bas de l'intérieur, sinon la tuile y tiendrait pile)
    reg = REGLAGE(t, src, boite, f"{nom}-reglage", {"flex-grow": 1, "flex-basis": 0, "min-height": 0,
                                                     "flex-direction": "column"},
                  classe=CLASSE_MOYEN, vue=AFFICHAGE_MOYEN, chemin=CHEMIN_AFFICHAGE)
    n = colonnes_tuiles(e, se, inst, reg, TUILES_SOUS_VDE,
                        {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                         "margin-left": -8, "margin-right": -8, "padding-top": ECART}, f"{nom}-tuiles", tete=True)
    n += colonnes_tuiles(e, se, inst, reg, TUILES_SOUS_VDE_MOYEN,
                         {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                          "margin-left": -8, "margin-right": -8, "margin-bottom": -BAS_FM24,
                          "padding-top": HAUT_RANGEE_MOYEN - HAUT_VDE}, f"{nom}-tuiles-moyen", tete=True,
                         ecart_bas=0)   # v76 : une seule rangée, sans écart dessous (v75 : 12, la tuile ne tenait pas)
    selon_moyen(t, f"{nom}-tuiles", f"{nom}-tuiles-moyen", 75.2)
    attacher_feuille(t, reg)
    return n + n_hautes


def selon_moyen(t, petit, moyen, repere):
    """v75 : nos règles « l'un ou l'autre » de l'affichage Moyen : l'élément moyen caché, sauf sous CLASSE_MOYEN ; sous
    CLASSE_MOYEN, l'élément petit caché"""
    affichage = base.sm.PROPRIETES["display"][0]
    regle_selecteurs(t, [(affichage, "", [(7, "none")])], repere, [[(TYPE_NOM, moyen, 0)],
                                                                   [(TYPE_CLASSE, CLASSE_MOYEN, 0),
                                                                    (TYPE_NOM, petit, DESCENDANT)]])
    regle_selecteurs(t, [(affichage, "", [(7, "flex")])], repere + 0.01,
                     [[(TYPE_CLASSE, CLASSE_MOYEN, 0), (TYPE_NOM, moyen, DESCENDANT)]])


def inclure_modele(t, inst, parent, modele, css, index=None):
    """v71 (sorti de poser_terrain24) : un modèle de FM inclus par son GUID (modele = (alias, GUID)), comme les tuiles :
    le modèle inclus de l'onglet recopié vide, son alias changé, l'alias ajouté aux modèles inclus de l'onglet (à sa
    place dans l'ordre des noms, comme FM) ; rend l'élément"""
    r = t.clone_shallow(inst, parent, index)
    base.recaler_parent(t, r)
    er = t.elem(r)
    er["m_TemplateAlias"], er["m_Classes"], er["m_RuleIndex"] = modele[0], [], -1
    sr = t.sd(r)
    if "templateId" in sr:
        sr["templateId"] = modele[0]
    sr["name"], sr["name_UxmlAttributeFlags"] = "", 0
    t.styles.style(t, r, css)
    usings = t.tt.setdefault("m_Usings", [])
    if not any(u.get("alias") == modele[0] for u in usings):
        cles = [u.get("alias") or "" for u in usings]
        usings.insert(bisect.bisect_left(cles, modele[0]) if cles == sorted(cles) else len(usings),
                      {"alias": modele[0], "path": modele[1], "asset": {"m_FileID": 0, "m_PathID": 0}})
    return r


def boite24(t, src, tb, parent, nom, css, index=None):
    """v69 : une boîte simple (comme celles de l'écran plein) dans l'onglet"""
    se = SourcesEcran(src, tb)
    e = Ecran(t, src, se, None)
    e.fab.proto = first(t, lambda r: est_racine(t.name(r)))
    if e.fab.proto is None:
        raise ValueError("écran plein (introuvable)")
    return e.boite(parent, css, nom=nom, index=index)


def poser_tuiles24(t, src, tb, parent, nom):
    """v66 (kinito_consignes_essai_b, poser_tuiles24) : en vue FM24, à droite de la grille plafonnée, nos copies des
    tuiles de FM (TUILES24), les unes sous les autres puis en colonnes suivantes s'il y a la place (coupées sinon) ;
    rend le nombre de tuiles posées"""
    se = SourcesEcran(src, tb)
    if se.remap is None:
        raise ValueError(f"remappeur de FM ({MODELE_REMAPPEUR}) (introuvable)")
    inst = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == INSTANCE_ONGLET)
    racine = first(t, lambda r: est_racine(t.name(r)))
    if inst is None or racine is None:
        raise ValueError("modèle inclus de l'onglet ou écran plein (introuvable)")
    e = Ecran(t, src, se, None)
    e.fab.proto = racine
    # v70 : la zone va jusqu'en bas des blocs de FM (la grille descend de DEPASSE_BAS sous l'intérieur : sa capture de la
    # v69 en 3440 Petit, bas des blocs ~14 unités sous celui du terrain de Positionnement, qui finissait 16 au-dessus du
    # bas de l'enveloppe) : étirée par l'intérieur (pas de hauteur), sa marge du bas négative
    # v73 : la Vue d'ensemble à la place de la colonne de tuiles (poser_vde24), derrière un repère vide (elle ne paraît
    # qu'entière, comme les colonnes de tuiles)
    zone = e.boite(parent, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                            "margin-bottom": -DEPASSE_BAS, "overflow": "hidden", "flex-direction": "row",
                            "flex-wrap": "wrap", "align-content": "flex-start"}, nom=nom)
    e.boite(zone, {"width": 0, "height": base.pc(100), "flex-shrink": 0})
    n = poser_vde24(e, se, inst, src, tb, zone, f"{nom}-vde")
    # v89 (voir COLS_3440_MOYEN) : deux colonnes de plus, de la taille de celle de la Vue d'ensemble, cachées par défaut
    # (kinito_consignes_essai_b.poser_3440 les montre en 3 440 Moyen) ; même découpe : le haut à HAUT_VDE, la rangée du
    # Moyen dessous
    for i, (hautes, rangee) in enumerate(COLS_3440_MOYEN, start=2):
        col = e.boite(zone, {"width": LARGEUR_VDE, "height": base.pc(100), "flex-shrink": 0, "flex-grow": 0,
                             "margin-left": ECART_TUILES, "flex-direction": "column"}, nom=f"{nom}-col{i}")
        haut = e.boite(col, {"height": HAUT_VDE, "flex-grow": 0, "flex-shrink": 1, "min-height": 0,
                             "flex-direction": "column"})
        n += colonnes_tuiles(e, se, inst, haut, [hautes],
                             {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                              "margin-left": -8, "margin-right": -8}, f"{nom}-col{i}-hautes", tete=True)
        if rangee:
            n += colonnes_tuiles(e, se, inst, col, [rangee],
                                 {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                                  "margin-left": -8, "margin-right": -8, "margin-bottom": -BAS_FM24,
                                  "padding-top": HAUT_RANGEE_MOYEN - HAUT_VDE}, f"{nom}-col{i}-rangee", tete=True,
                                 ecart_bas=0)
    # v90 (voir COL_3440_PETIT) : une 4e colonne, cinq petites tuiles l'une sous l'autre, cachée par défaut
    col4 = e.boite(zone, {"width": LARGEUR_VDE, "height": base.pc(100), "flex-shrink": 0, "flex-grow": 0,
                          "margin-left": ECART_TUILES, "flex-direction": "column"}, nom=f"{nom}-col4")
    n += colonnes_tuiles(e, se, inst, col4, [COL_3440_PETIT],
                         {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                          "margin-left": -8, "margin-right": -8}, f"{nom}-col4-tuiles", tete=True)
    # v92 (voir COL_2560_PETIT) : une 5e colonne, trois grandes tuiles, un écart de 12 entre elles et aucun sous la
    # dernière (960 pile : la colonne en a ~967)
    col5 = e.boite(zone, {"width": LARGEUR_VDE, "height": base.pc(100), "flex-shrink": 0, "flex-grow": 0,
                          "margin-left": ECART_TUILES, "flex-direction": "column"}, nom=f"{nom}-col5")
    z5 = e.boite(col5, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "margin-left": -8,
                        "margin-right": -8, "overflow": "hidden", "flex-direction": "row", "flex-wrap": "wrap",
                        "align-content": "flex-start"}, nom=f"{nom}-col5-tuiles")
    e.boite(z5, {"width": 0, "height": base.pc(100), "flex-shrink": 0})
    c5 = e.boite(z5, {"width": COLONNE, "height": base.pc(100), "flex-shrink": 0, "margin-left": ECART_TUILES,
                      "flex-direction": "column", "flex-wrap": "wrap", "align-content": "flex-start",
                      "overflow": "hidden"})
    e.boite(c5, {"width": base.pc(100), "height": 0, "flex-shrink": 0})
    for i, tuile in enumerate(COL_2560_PETIT):
        tuile_fm(e, se, inst, c5, tuile, {"margin-top": ECART_TUILES if i else 0, "margin-bottom": 0})
        n += 1
    regle_selecteurs(t, [(base.sm.PROPRIETES["display"][0], "", [(7, "none")])], 89.0,
                     [[(TYPE_NOM, f"{nom}-col{i}", 0)] for i in range(2, 4 + len(COLS_3440_MOYEN))])
    attacher_feuille(t, zone)
    return n


def colonnes_tuiles(e, se, inst, parent, colonnes, css, nom, tete=False, ecart_bas=ECART_TUILES):
    """v67 (v70 : commun à la vue FM24 et aux tuiles de droite de la vue Terrain) : une rangée de colonnes qui passe à la
    ligne (une colonne qui ne tient pas en largeur part sous la rangée, coupée) ; chaque colonne, à sa largeur, passe
    elle-même à la ligne (une tuile qui ne tient pas en hauteur part à droite de la colonne, coupée). Tailles fixées,
    sans rétrécir : c'est ce qui fait passer à la ligne (v65). v68 : écart de 12 avant chaque colonne. v70 (Kinito, 10/11,
    v69 vue en 2560 Moyen : « la colonne de droite est coupée ») : la PREMIÈRE colonne restait sur la rangée même sans la
    place (une ligne prend toujours son premier élément) : un repère vide, de toute la hauteur, ouvre maintenant la
    rangée — une colonne qui ne tient pas, la première comprise, passe dessous. Rend le nombre de tuiles posées.
    v73 : tete, un repère vide en tête de chaque colonne aussi (sous un terrain coupé, la place peut manquer même pour la
    première tuile : elle passe alors à droite, cachée, au lieu de paraître coupée)"""
    zone = e.boite(parent, {"overflow": "hidden", "flex-direction": "row", "flex-wrap": "wrap",
                            "align-content": "flex-start", **css}, nom=nom)
    e.boite(zone, {"width": 0, "height": base.pc(100), "flex-shrink": 0})
    n = 0
    for colonne in colonnes:
        col = e.boite(zone, {"width": COLONNE, "height": base.pc(100), "flex-shrink": 0, "margin-left": ECART_TUILES,
                             "flex-direction": "column", "flex-wrap": "wrap", "align-content": "flex-start",
                             "overflow": "hidden"})
        if tete:
            e.boite(col, {"width": base.pc(100), "height": 0, "flex-shrink": 0})
        for tuile in colonne:
            tuile_fm(e, se, inst, col, tuile, {"margin-bottom": ecart_bas})
            n += 1
    return n


HAUT_BANDE4, BAS_BANDE4 = 8, 10   # v72 (v71 : 16 et 19) : la place rendue à l'écran (AGRANDI)
BANDE4_HAUT = HAUT_BANDE4 + RANGEE(2) + BAS_BANDE4   # 166 : une rangée de 4 x 2
TYPE_CLASSE, TYPE_NOM, ENFANT, DESCENDANT = 3, 6, 1, 2   # comme kinito_consignes_essai_b (sélecteurs d'Unity 6)
REPERE_REGLE_ECRAN = "--kinito-consignes-ecran"         # v71 : propriété perso de nos règles à sélecteurs de l'écran


def regle_selecteurs(t, valeurs, repere, selecteurs):
    """v71 : une règle à sélecteurs dans la feuille intégrée (comme kinito_consignes_essai_b._selecteur) :
    selecteurs = [[(type, valeur, relation au précédent)]]"""
    idx = t.styles.add_rule(valeurs + [(-1, REPERE_REGLE_ECRAN, [(2, repere)])])
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [
        {"m_Specificity": 1 + sum(10 if ty == TYPE_CLASSE else 100 for ty, _, _ in parties),
         "m_Selectors": [{"m_Parts": [{"m_Value": v, "m_Type": ty}], "m_PreviousRelationship": rel}
                         for ty, v, rel in parties],
         "ruleIndex": idx} for parties in selecteurs]
    return idx


def attacher_feuille(t, r):
    """la feuille intégrée du modèle rattachée à r : ses règles à sélecteurs valent pour r et tout ce qui est dessous"""
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(r).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)


def vue_large(e, se, inst, src, tb, large, milieu, filet, rangee, fond, version):
    """v71 : la vue large (voir LARGE_ECRAN) : la copie du visualiseur à droite du cadre, le terrain de Positionnement et
    le centre des données à partir du filet (sur la place du visualiseur de FM), les quatre tuiles sous l'écran ; rend
    le nombre d'éléments de FM recopiés (modèles inclus)"""
    t = e.t
    n = 0
    racine = nom_racine(version)
    # à droite : la copie du bloc visualiseur de FM (16 après le cadre, comme entre deux blocs de la grille)
    visu = e.boite(milieu, {"width": TROU, "height": base.pc(100), "flex-shrink": 0, "flex-grow": 0,
                            "padding-left": ECART, "padding-bottom": DEPASSE_BAS - DECALE_FM24,
                            "flex-direction": "column", "background-color": fond}, nom=f"{racine}-visu")
    inclure_modele(t, inst, visu, VISUALISEUR, {"flex-grow": 1, "flex-shrink": 1})
    n += 1
    # v74 (Kinito : « passer la tuile data hub à droite ») : le centre des données sous la copie du visualiseur (coupée
    # à HAUT_PANNEAU en vue Terrain, comme le visualiseur de FM)
    tuile_fm(e, se, inst, visu, TUILES[0][0], {"position": "absolute", "top": HAUT_TERRAIN_COUPE,
                                                 "left": ECART + (LARGEUR_TERRAIN24 - COLONNE) / 2})
    n += 1
    # v75 : à gauche, plus rien de posé à partir du filet (v71 à v74 : le dispositif, sur le visualiseur de FM) : le trou
    # le porte maintenant, avec son bouton « Visualiseur », à toutes les tailles (voir poser)
    # dessous : rapport, capitaines, CPA, penalties, sur toute la largeur du cadre, derrière un repère vide (ils passent
    # à la ligne, coupés, si le cadre n'a pas LARGE_ECRAN)
    dessous = e.boite(large, {"position": "absolute", "left": FILET, "right": TROU, "bottom": 0, "height": BANDE4_HAUT,
                              "flex-direction": "row", "flex-wrap": "wrap", "justify-content": "center",
                              "align-content": "flex-start", "overflow": "hidden"}, nom=f"{racine}-dessous")
    e.boite(dessous, {"width": 0, "height": base.pc(100), "flex-shrink": 0})
    rang = e.boite(dessous, {"width": LARGE_ECRAN, "height": base.pc(100), "flex-shrink": 0, "flex-direction": "row",
                             "justify-content": "center", "padding-top": HAUT_BANDE4})
    for i, tuile in enumerate(BANDE4):
        tuile_fm(e, se, inst, rang, tuile, {"margin-left": ECART_TUILES if i else 0})
        n += 1
    return n


def poser(o, src, tb, version):
    """pose l'écran dans l'onglet o (TacticalPlannerTeamInstructions) ; rend les messages"""
    t = o[3]
    corps = body_de(t)
    if corps is None:
        return ["onglet : #Body (introuvable)"]
    se = SourcesEcran(src, tb)
    manque = se.manque()
    if manque:
        return [f"écran plein : {m} (introuvable)" for m in manque]
    data = donnees()
    accelerer(t)
    e = Ecran(t, src, se, data)
    fab = e.fab
    # la racine : une boîte simple de notre bloc, sur tout #Body, après la grille de FM (dessus)
    racine = t.clone(se.proto, corps, 1, src=tb)
    for k in list(t.children(racine)):
        t.remove(k)
    t.styles.copy_from(tb.styles, t, racine)
    base.recaler_parent(t, racine)
    t.elem(racine)["m_Classes"], t.elem(racine)["m_RuleIndex"] = [], -1
    sd = t.sd(racine)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom_racine(version), 1
    # v62 : jusqu'au bas de la grille de tuiles de FM, qui dépasse de #Body (DEPASSE_BAS)
    t.styles.style(t, racine, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": -DEPASSE_BAS})
    e.sans_clic(racine)
    fab.proto = racine
    sw = t.clone(se.inter, racine, src=tb)
    for k in list(t.children(sw)):
        t.remove(k)
    t.styles.copy_from(tb.styles, t, sw)
    base.recaler_parent(t, sw)
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
    ss = t.sd(sw)
    ss["name"], ss["name_UxmlAttributeFlags"] = f"{nom_racine(version)}-vue", 1
    ss["Binding"]["m_direct"]["Path"]["m_path"] = base.VARIABLE
    t.styles.style(t, sw, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0})
    e.sans_clic(sw)
    fab.inter = sw
    e.boite(sw, {"width": 0, "height": 0})   # 0 : tuiles de FM, rien par-dessus
    # 1 : l'écran ; il prend les clics. v60 (Kinito, 10/11, vu en match : l'écran passait sous la barre des onglets en
    # haut et sous la barre du match en bas, on ne pouvait ni cliquer en bas ni faire défiler) : #Body fait ~722 unités
    # hors match (l'écran, 720, y tient tout juste) mais ~657 en match ; centré, l'écran débordait des deux côtés.
    # Il est maintenant dans un DÉFILEMENT de FM (le SIScrollView #Body de notre bloc, recopié vide), calé en haut :
    # hors match il tient sans défiler (9 unités plus haut qu'en v56-v59, où il était centré puis descendu de
    # DECALAGE_HAUT), en match il ne passe plus sous les onglets et la molette amène le bas au-dessus de la barre du match.
    # Centré en largeur par une rangée (grands écrans larges)
    # v62 (Kinito, 10/11, v61 vue hors match : « toujours pas bon » — les tuiles de FM dépassaient sous l'écran — puis
    # « dans les coins, arrondir plutôt qu'angle droit, comme les tuiles derrière, aux 4 coins ») : la grille de tuiles
    # de FM descend ~15 unités sous #Body ; jusqu'en v59, l'écran (centré, plus long) la couvrait par hasard. La racine
    # descend maintenant jusqu'en bas de la grille (DEPASSE_BAS) et le CADRE porte la bordure et les coins arrondis de
    # l'écran de la maquette sur toute cette zone : sous ses coins on voit le fond de l'onglet, comme sous ceux des tuiles,
    # et il coupe son contenu en arrondi. L'écran, dedans, perd sa bordure (le cadre la dessine) et revient à 722 (v59)
    # v63 (Kinito, 10/11, maquette A du grand écran) : plus de défilement (en match, l'écran rétrécit pour tenir, son
    # choix). La vue est une RANGÉE qui passe à la ligne, de droite à gauche : le cadre (l'écran), puis le TROU du
    # visualiseur de FM (transparent, sans clic : on voit et on touche le bloc du terrain de FM, posé là par sa grille).
    # Quand cadre (au moins la largeur de l'écran de la v62) + trou ne tiennent pas, le trou passe à la ligne suivante,
    # sous la rangée, coupée : en 1080p, le cadre couvre tout, comme en v62. Dans le cadre, la ZONE de l'écran (sa
    # hauteur, 720 en 1080p hors match) et dedans l'élément de FM qui l'ajuste (AGRANDI) ; l'écran, dessiné à sa taille
    # de la v62, y est agrandi de 1,2 autour de son centre
    rd = data["racine"]
    fond = e.couleur(rd["bg"]) if rd.get("bg") else (0.04, 0.07, 0.13, 1.0)
    bords = {k: v for k, v in e.css_boite(rd).items() if k.startswith("border-")}
    bl = rd.get("bw") or [0, 0, 0, 0]
    iw, ih = rd["w"] - bl[1] - bl[3], rd["h"] - bl[0] - bl[2]   # la boîte intérieure de l'écran (1 622 x 720)
    marge_bas = 2   # v62 : l'intérieur du cadre fait 722 en 1080p hors match, l'écran 720 posé en haut
    # v75 : la vue Terrain dans un réglage Moyen (voir CLASSE_MOYEN), sans clic
    # v77 : sur l'affichage Petit (CLASSE_PETIT : la rangée sous l'écran cachée) ; v75, v76 : Moyen
    moyen = REGLAGE(t, src, sw, f"{nom_racine(version)}-affichage",
                    {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0},
                    classe=CLASSE_PETIT, vue=AFFICHAGE_PETIT, chemin=CHEMIN_AFFICHAGE)
    e.sans_clic(moyen)
    rangee = e.boite(moyen, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0,
                             "flex-direction": "row-reverse", "flex-wrap": "wrap", "overflow": "hidden"},
                     nom=f"{nom_racine(version)}-rangee")
    # v64 : le cadre passe aussi à la ligne (en colonne) : la bande de tuiles ne tient pas sous l'écran -> elle part dans
    # une 2e colonne, à droite de la zone (qui prend toute la largeur), coupée
    # v65 (Kinito, 10/11, v64 vue en 1080p : « tu as tout cassé, il ne devrait y avoir ni les tuiles ni le visualiseur ») :
    # rien n'est passé à la ligne, le jeu a RÉTRÉCI le cadre et la zone (flex-shrink 1, taille donnée par flex-basis)
    # pour tout faire tenir : visualiser à gauche, écran minuscule, tuiles dessous. Les colonnes de tuiles, elles (largeur
    # fixée, flex-shrink 0), passaient bien à la ligne. Le cadre et la zone sont donc faits pareil : une LARGEUR / HAUTEUR
    # (plus de flex-basis), flex-shrink 0, et un plafond à 100 % de la place (max-width / max-height) au lieu du
    # rétrécissement : plus étroit que l'écran de la v62, le cadre prend toute la rangée, le trou passe à la ligne
    # v71 (voir LARGE_ECRAN) : à la place du cadre d'avant, une rangée À L'ENVERS qui passe à la ligne : [milieu (le
    # cadre, puis la copie du visualiseur, dans une rangée qui passe à la ligne) | filet] ; elle ne coupe rien (le
    # terrain de Positionnement part du filet vers la gauche) : la ligne cachée l'est par la vue (coupée en bas)
    large = e.boite(rangee, {"flex-grow": 1, "flex-shrink": 0, "width": LARGE_MIN, "max-width": base.pc(100),
                             "height": base.pc(100), "flex-direction": "row-reverse", "flex-wrap": "wrap",
                             "align-content": "flex-start"},
                    nom=f"{nom_racine(version)}-large")
    milieu = e.boite(large, {"flex-grow": 1, "flex-shrink": 0, "width": BASE_LARGE, "max-width": base.pc(100),
                             "height": base.pc(100), "flex-direction": "row", "flex-wrap": "wrap",
                             "align-content": "flex-start", "overflow": "hidden"},
                     nom=f"{nom_racine(version)}-milieu")
    cadre = e.boite(milieu, {"flex-grow": 1, "flex-shrink": 0, "width": LARGE_ECRAN, "max-width": base.pc(100),
                             "height": base.pc(100), "flex-direction": "column", "flex-wrap": "wrap",
                             "background-color": fond, "overflow": "hidden", **bords},
                    nom=f"{nom_racine(version)}-cadre")
    e.avec_clic(cadre)
    filet = e.boite(large, {"width": FILET, "height": base.pc(100), "flex-shrink": 0},
                    nom=f"{nom_racine(version)}-filet")
    trou = e.boite(rangee, {"width": TROU, "height": base.pc(100), "flex-shrink": 0},
                   nom=f"{nom_racine(version)}-trou")
    # v65 : la zone (hauteur 722, jamais plus que le cadre : en match elle tient dedans) et dedans la PLACE de l'écran
    # (au plus 866, l'écran à 1,2) : la zone prend la hauteur que la bande laisse, l'écran reste en haut
    # v70 : zone de BASE_ZONE (la bande du bas ne reste que dans une vue assez haute), place au plus l'écran à AGRANDI,
    # l'écran calé en haut de sa place
    zone = e.boite(cadre, {"flex-grow": 1, "flex-shrink": 0, "height": BASE_ZONE, "max-height": base.pc(100),
                           "width": base.pc(100), "flex-direction": "column"},
                   nom=f"{nom_racine(version)}-zone")
    # v80 : son plafond (max-height) par règle, voir la fin
    place = e.boite(zone, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0,
                           "padding-bottom": marge_bas, "flex-direction": "row", "justify-content": "center",
                           "align-items": "flex-start"},
                    nom=f"{nom_racine(version)}-place")
    n_tuiles = bande_tuiles(e, se, cadre, version)
    n_ligne = ligne_tuiles(e, se, cadre, version, ih / iw)   # v75 ; v77 : sous l'écran
    inst = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == INSTANCE_ONGLET)
    n_large = vue_large(e, se, inst, src, tb, large, milieu, filet, rangee, fond, version) if inst is not None else 0
    # v74 (Kinito, 11/11, v73 vue en 2 560 Petit, vue Terrain : « tu proposes quoi sous le visualiseur ? ») : les
    # remplaçants, dans le trou (sur le visualiseur de FM, coupé à HAUT_PANNEAU). v75 : le trou porte aussi notre
    # dispositif, par-dessus le visualiseur de FM, et le bouton qui passe de l'un à l'autre (voir VAR_GAUCHE). Une boîte
    # à nous déclare VAR_GAUCHE et « mode » (attendu par les remplaçants) ; elle ne prend pas les clics
    n_remplacants = n_gauche = 0
    if inst is not None:
        racine_n = nom_racine(version)
        boite_g, _ = boite_variables(t, trou, f"{racine_n}-gauche", {VAR_GAUCHE: 0, "mode": 0},
                                     {"position": "absolute", "left": 0, "top": 0, "width": LARGEUR_TERRAIN24,
                                      "bottom": 0})
        e.sans_clic(boite_g)
        choix = interrupteur(e, tb, boite_g, f"{racine_n}-gauche-choix", VAR_GAUCHE)
        cas_d = e.boite(choix, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0},
                        nom=f"{racine_n}-gauche-dispositif")
        nom_d = f"{racine_n}-dispositif"
        poser_terrain24(t, src, tb, cas_d, nom_d, css={"width": LARGEUR_TERRAIN24, "height": base.pc(100),
                                                       "flex-direction": "column"}, hauteur=HAUT_TERRAIN_COUPE)
        cas_v = e.boite(choix, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0},
                        nom=f"{racine_n}-gauche-visualiseur")
        # v80 : en match, le visualiseur de FM (dessous) est masqué : notre copie à sa place (cachée hors match)
        visu_m = e.boite(cas_v, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0,
                                 "flex-direction": "column"}, nom=f"{racine_n}-gauche-visu-match")
        inclure_modele(t, inst, visu_m, VISUALISEUR, {"flex-grow": 1, "flex-shrink": 1})
        bascule(e, tb, boite_g, f"{racine_n}-gauche-bascule", VAR_GAUCHE)   # v81 (v76 à v80 : SEGMENTS)
        n_gauche = 1
        # dans le dispositif : ni « Les deux », ni le côté droit de l'en-tête, ni les remplaçants du modèle
        affichage = base.sm.PROPRIETES["display"][0]
        regle_selecteurs(t, [(affichage, "", [(7, "none")])], 71.0,
                         [[(TYPE_NOM, nom_d, 0), (TYPE_NOM if k == "#" else TYPE_CLASSE, v, DESCENDANT)]
                          for k, v in CACHES_TERRAIN24])
        boite_r = e.boite(boite_g, {"position": "absolute", "left": 0, "top": HAUT_TERRAIN_COUPE,
                                    "width": LARGEUR_TERRAIN24, "bottom": DEPASSE_BAS + 2, "flex-direction": "column"},
                          nom=f"{racine_n}-remplacants")
        poser_remplacants(t, src, tb, inst, boite_r, f"{racine_n}-remplacants-zone",
                          {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
        n_remplacants = 1
    # v77 : la rangée sous l'écran, cachée en Petit (v75, v76 : la zone réduite en Moyen, ZONE_MOYEN)
    racine_n = nom_racine(version)
    regle_selecteurs(t, [(base.sm.PROPRIETES["display"][0], "", [(7, "none")])], 77.0,
                     [[(TYPE_CLASSE, CLASSE_PETIT, 0), (TYPE_NOM, f"{racine_n}-ligne", DESCENDANT)]])
    attacher_feuille(t, moyen)
    ajuste = e.seul(se.ta, se.ajuste, place, nom=f"{nom_racine(version)}-ajuste")
    sa = t.sd(ajuste)
    sa["AspectMode"], sa["AspectRatio"] = MODE_SCALE_TO_FIT, 1.0
    sa["AspectMode_UxmlAttributeFlags"] = sa["AspectRatio_UxmlAttributeFlags"] = 1
    # v80 : sa taille (AGRANDI, ou AGRANDI_MATCH en match) par règle, voir la fin
    t.styles.style(t, ajuste, {"flex-grow": 0, "flex-shrink": 0})
    fab.style_brut(ajuste, [(ID_ORIGINE, [(7, "top")])])   # v70 : l'échelle de FM part du haut (comme FM : un mot)
    # v62 : sans sa bordure (le cadre la dessine), coins et coupe gardés ; même boîte intérieure (son contenu ne bouge
    # pas : les enfants en absolu se placent dans la boîte intérieure, dans FM comme dans la maquette)
    css_ecran = {k: v for k, v in e.css_boite(rd).items()
                 if k not in ("position", "left", "top") and not (k.startswith("border-") and not k.endswith("-radius"))}
    css_ecran["width"], css_ecran["height"] = iw, ih
    # v80 : sa place (left, top) et son échelle par règle, voir la fin (v63 à v79 : style intégré, qui passerait devant
    # la règle du match)
    css_ecran.update({"position": "absolute", "flex-shrink": 0})
    ecran = e.boite(ajuste, css_ecran, nom=f"{nom_racine(version)}-ecran")
    e.avec_clic(ecran)
    dessin = conteneur_langue(e, ecran, iw, ih, version)   # v95 : tout le dessin sous la langue du jeu
    for k in e.ordre(rd.get("k") or []):
        e.construire(dessin, k, bl[3], bl[0], True, rd, None)
    for k in rd.get("k") or []:   # v56 : les clics des terrains, au-dessus de tout le dessin (dans les bords de l'écran,
        e.collecter(k, 0.0, 0.0)  #       comme ses enfants en absolu)
    e.poser_clics(ecran)
    for x, y, w, h, valeur in e.boutons_vue:
        e.bouton_vue(ecran, x - bl[3], y - bl[0], w, h, valeur)
    n_bulles = bulles_options(e, ecran)   # v96 : l'explication de chaque option au survol
    e.boite(sw, {"width": 0, "height": 0})   # 2 : FM24, rien par-dessus
    n_match = poser_match(t, src, corps, racine, version, iw, ih, marge_bas)   # v80
    msgs = [f"écran plein (maquette {data['maquette']}) : {e.n} éléments, {len(e.boutons_vue) + e.n_vues_dans} boutons de vue, "
            f"{e.n_cartes} cartes branchées, {e.n_deps} groupes de terrain, {e.n_clics} zones de clic des terrains, "
            f"{n_tuiles} tuiles de FM en bande ({n_ligne} en rangée, Moyen) ; vue large : {n_large} éléments de FM "
            f"recopiés ; remplaçants : {n_remplacants} ; dispositif ou visualiseur à gauche : {n_gauche}"]
    if n_tuiles != sum(len(c) for c in TUILES):
        msgs.append(f"écran plein : {n_tuiles} tuiles sur {sum(len(c) for c in TUILES)} (introuvables)")
    if n_large != len(BANDE4) + 2:   # v75 : + 2 (v71 à v74 : + 3, le dispositif de gauche)
        msgs.append(f"écran plein : vue large, {n_large} éléments de FM sur {len(BANDE4) + 2} (introuvables)")
    if n_remplacants != 1 or n_gauche != 1:
        msgs.append("écran plein : remplaçants ou dispositif de gauche (introuvables)")
    msgs.append(f"langue du jeu (v95) : {e.n_traduits} noms de FM par leur n° de traduction, {e.n_mots} mots écrits "
                f"dans {len(LANGUES_JEU)} langues, {e.n_fixes} textes fixes")
    msgs.append(f"infobulles (v96) : {n_bulles} boutons d'option avec l'explication de FM, {e.n_survols} textes qui "
                f"montrent leur phrase entière quand elle est coupée")
    msgs += [f"écran plein : {a}" for a in sorted(set(e.alertes)) if "texte" in a or "langue" in a]
    msgs.append(f"en match : {n_match} règles (vue Terrain sur la ligne de FM, blocs de FM masqués dessous, 3 440 Petit "
                f"sans tuiles ni visualiseur à droite, écran jusqu'à {AGRANDI_MATCH})")
    if n_ligne != len(LIGNE_TERRAIN):
        msgs.append(f"écran plein : rangée du Moyen, {n_ligne} tuiles sur {len(LIGNE_TERRAIN)} (introuvables)")
    if len(e.boutons_vue) + e.n_vues_dans != 3:   # v95 : dans les boutons de l'en-tête
        msgs.append(f"écran plein : boutons de vue {len(e.boutons_vue) + e.n_vues_dans} sur 3 (introuvables)")
    # v56 : l'option neutre de la maquette = celle de 26.13 (DEFAUTS), sinon un 2e clic ne ferait pas la même chose
    ecarts = [c for c, d in (data.get("defauts") or {}).items() if base.DEFAUTS.get(int(c)) != d]
    if ecarts or set(data.get("sansRetour") or [8]) != SANS_RETOUR:
        msgs.append(f"écran plein : options neutres différentes de 26.13 pour {', '.join(ecarts) or 'SANS_RETOUR'} "
                    f"(introuvables)")
    branchees = {int(c) for c in data.get("variantes") or {}}
    if e.n_cartes != len(branchees):
        msgs.append(f"écran plein : {e.n_cartes} cartes branchées sur {len(branchees)} (introuvables)")
    alertes = sorted(set(e.alertes))
    msgs += [f"écran plein : {a}" for a in alertes[:12]]
    return msgs


def poser_match(t, src, corps, racine, version, iw, ih, marge_bas):
    """v80 (voir CLASSE_MATCH) : les deux réglages de FM sur #Body (vides, en absolu, sans taille, nommés comme la racine :
    retirer les emporte), la taille dessinée de l'écran par règles (AGRANDI hors match, AGRANDI_MATCH en match) et les
    règles du match ; rend le nombre de règles posées"""
    nv = nom_racine(version)
    vide = {"position": "absolute", "left": 0, "top": 0, "width": 0, "height": 0}
    REGLAGE_MATCH(t, corps, f"{nv}-match", CLASSE_MATCH, vide)
    REGLAGE_PARENT(t, src, corps, f"{nv}-onglet-terrain", base.VARIABLE, VUE_TERRAIN, CLASSE_ONGLET_TERRAIN, vide)
    REGLAGE_PARENT(t, src, corps, f"{nv}-onglet-fm24", base.VARIABLE, VUE_FM24, CLASSE_ONGLET_FM24, vide)   # v82
    # v87 (voir CLASSE_3440) : hors match, l'écran 3 440 x 1440, l'affichage Petit
    REGLAGE_TEXTE(t, corps, f"{nv}-hors-match", "game.IsDuringMatch", "False", CLASSE_HORS_MATCH, vide)
    REGLAGE_TEXTE(t, corps, f"{nv}-ecran-3440", CHEMIN_RESOLUTION, TEXTE_3440, CLASSE_3440, vide)
    REGLAGE_PARENT(t, src, corps, f"{nv}-petit", CHEMIN_AFFICHAGE, AFFICHAGE_PETIT, CLASSE_PETIT, vide)
    # v88 : l'écran 2 560 x 1440, l'affichage Moyen
    REGLAGE_TEXTE(t, corps, f"{nv}-ecran-2560", CHEMIN_RESOLUTION, TEXTE_2560, CLASSE_2560, vide)
    REGLAGE_PARENT(t, src, corps, f"{nv}-moyen", CHEMIN_AFFICHAGE, AFFICHAGE_MOYEN, CLASSE_ONGLET_MOYEN, vide)
    REGLAGE_PARENT(t, src, corps, f"{nv}-grand", CHEMIN_AFFICHAGE, AFFICHAGE_GRAND, CLASSE_ONGLET_GRAND, vide)   # v89
    P = base.sm.PROPRIETES

    def px(v):
        return (3, {"unit": 1, "value": float(v)})

    def nm(n, rel=0):
        return (TYPE_NOM, f"{nv}-{n}", rel)
    M = (TYPE_CLASSE, CLASSE_MATCH, 0)
    n = 0
    # la taille dessinée de l'écran (v63 à v79 : style intégré, qui passerait devant toute règle du match)
    for a, rep, sel in ((AGRANDI, 80.0, lambda x: [[nm(x)]]), (AGRANDI_MATCH, 80.1, lambda x: [[M, nm(x, DESCENDANT)]])):
        regle_selecteurs(t, [(P["width"][0], "", [px(iw * a)]), (P["height"][0], "", [px(ih * a)])], rep,
                         sel("ajuste"))
        regle_selecteurs(t, [(P["left"][0], "", [px(iw * (a - 1) / 2)]), (P["top"][0], "", [px(ih * (a - 1) / 2)]),
                             (ID_ECHELLE, "", [(2, a), (2, a)])], rep, sel("ecran"))   # autour de son centre
        regle_selecteurs(t, [(P["max-height"][0], "", [px(ih * a + marge_bas)])], rep, sel("place"))
        n += 3
    # la vue finit sur la ligne de FM (DEPASSE_BAS + 2 plus haut), les remplaçants restent au bas de la vue
    regle_selecteurs(t, [(P["margin-bottom"][0], "", [px(DEPASSE_BAS + 2)])], 80.2, [[M, nm("vue", DESCENDANT)]])
    regle_selecteurs(t, [(P["margin-bottom"][0], "", [px(-(DEPASSE_BAS + 2))])], 80.3,
                     [[M, nm("remplacants", DESCENDANT)]])
    # 3 440 Petit (vue large) : ni le visualiseur ni le centre des données à droite, ni les tuiles sous l'écran ; la
    # bande et la rangée du Moyen, déjà coupées en match, cachées aussi
    affichage = P["display"][0]
    regle_selecteurs(t, [(affichage, "", [(7, "none")])], 80.4,
                     [[M, nm(x, DESCENDANT)] for x in ("visu", "dessous", "ligne", "tuiles")])
    # notre copie du visualiseur dans le trou : en match seulement (hors match, celui de FM se voit dessous)
    regle_selecteurs(t, [(affichage, "", [(7, "none")])], 80.5, [[nm("gauche-visu-match")]])
    regle_selecteurs(t, [(affichage, "", [(7, "flex")])], 80.6, [[M, nm("gauche-visu-match", DESCENDANT)]])
    n += 5
    # en match et en vue Terrain : les trois blocs de FM masqués (visibility : la grille de FM écrit elle-même leur
    # display) ; la règle vit dans la feuille de l'onglet, rattachée à l'enveloppe de la vue FM24, au-dessus de la grille
    idx = t.styles.add_rule([(VISIBILITE, "", [(7, "hidden")]), (-1, REPERE_REGLE_ECRAN, [(2, 80.7)])])
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [
        {"m_Specificity": 1 + 10 + 10 + 100 + 100,
         "m_Selectors": [{"m_Parts": [{"m_Value": CLASSE_MATCH, "m_Type": TYPE_CLASSE},
                                      {"m_Value": CLASSE_ONGLET_TERRAIN, "m_Type": TYPE_CLASSE}],
                          "m_PreviousRelationship": 0},
                         {"m_Parts": [{"m_Value": "GridLayoutElementContent", "m_Type": TYPE_NOM}],
                          "m_PreviousRelationship": DESCENDANT},
                         {"m_Parts": [{"m_Value": case, "m_Type": TYPE_NOM}], "m_PreviousRelationship": ENFANT}],
         "ruleIndex": idx} for case in CASES_ONGLET]
    n += 1
    attacher_feuille(t, racine)
    return n


def retirer(o):
    """retire notre écran (toutes versions) de l'onglet ; rend True s'il y en avait un"""
    t = o[3]
    rs = [r for r in t.walk() if est_racine(t.name(r))
          and not any(est_racine(t.name(p)) for p in _ancetres(t, r))]
    for r in rs:
        t.remove(r)
    nettoyer_modeles(t)
    return bool(rs)


def nettoyer_modeles(t):
    """v64 : les modèles inclus de nos tuiles, si plus rien ne les cite (v66 : appelé aussi par le retrait du miroir,
    qui retire les tuiles de la vue FM24 après l'écran plein ; v69 : et le terrain de Positionnement)"""
    nos = {tuile[0] for colonne in TUILES for tuile in colonne} | {DOUBLE24[0], VISUALISEUR[0], VUE_ENSEMBLE[0],
                                                                    REMPLACANTS[0]} \
        | {tuile[0] for tuile in TUILES_SOUS_DEUX24} | {tuile[0] for tuile in LIGNE_TERRAIN}   # v76, v78
    cites = {t.elem(r).get("m_TemplateAlias") for r in t.walk()}
    if t.tt.get("m_Usings"):
        t.tt["m_Usings"] = [u for u in t.tt["m_Usings"] if u.get("alias") not in nos or u.get("alias") in cites]


def _ancetres(t, r):
    p = t.parent.get(r)
    while p is not None:
        yield p
        p = t.parent.get(p)


def pose(o, version):
    return o is not None and any(o[3].name(r) == nom_racine(version) for r in o[3].walk())
