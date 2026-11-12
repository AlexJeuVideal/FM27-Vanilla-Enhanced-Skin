"""[AJOUT KINITO] 26.22 — RÉVÉLATION DES JEUNES : un clic sur le nom d'une carte retournée du message d'arrivée des
jeunes (cartes de 26.19) ouvre, par-dessus le message, une fenêtre « Dossier du recruteur » en deux phases (1 : la
personnalité, les rapports avec les médias et les projets, dévoilés un à un ; « Passer au rapport » ; 2 : le rapport de
l'adjoint, ses points forts et faibles), puis « Dévoiler la carte entière » ouvre la vraie fiche du joueur, découverte
par un cache. Une pastille « Révélation : oui / non » à côté de « Tout retourner » la coupe en jeu ; l'option de l'app
choisit les groupes (Élite / Élite et Excellents / tous). v9 : avec « oui », la barre du message porte aussi
« Fiche : Rideau ▾ » (un menu de FM : fondu, rideau, balayage, portes) et « Auto | Manuel » : la façon de découvrir
la fiche, choisie EN JEU (deux variables rangées que la fiche lit).
Demande de Kinito (09/11/2026) ; ses choix, mesures et plan : chantier-cartes-jeunes\\ETUDE, 8 duotricies et 8
tretricies. Ajout à part, facultatif ; il a besoin des cartes 26.19 v24 (kinito_cartes_jeunes), qu'il importe.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu.

Comment (mesuré le 09/11/2026, lecture seule) :
- LA FENÊTRE : le panneau de FM EndOfDemoDialog (couche ModalDialog : posé par-dessus l'écran, le message reste
  derrière ; ui-panelids cc7e1093…), ouvert par des modules du jeu, pour la démo ; son modèle (gameworld) n'est cité que
  par son panneau. Comme 26.4 (GoOnHolidayCard, vue en jeu) : nos paramètres ajoutés au panneau ET au BindingRoot du
  modèle ; notre fenêtre dans un SIVisible sur notre paramètre « kinitorevelation » (nul quand FM ouvre la fenêtre : rien
  de nous) ; la boîte de FM (#DialogFrame) cachée par une classe posée seulement quand notre paramètre est vrai (boîte de
  style de FM : une valeur nulle vaut faux, vu en jeu en 26.19 v3) ; le voile de FM (#Background) gardé.
- LES DONNÉES : texte de FM sur person.Personality et person.MediaHandling (PlayerAttributesTile). v2 (Kinito, v1 vue
  en jeu : « adapte la taille au contenu », « les projets comme la perso et les rapports médias », « le détail du
  rapport procons ») : plus de tuiles de FM. Les projets et les points Pour / Contre sont lus comme dans 26.20 (vu en
  jeu) : un BindingSetter de FM déclare une variable par élément, remplie par la fonction de FM « élément n d'une liste »
  (BindListItemUsingIndexToDestination), chaque ligne montrée par le NOMBRE d'éléments (jamais un SIVisible sur la
  variable : plantage de 26.20 v3) ; la 1re ligne de projet toujours (sans projet, la liste de FM a « Aucun projet ») ;
  les points Pour / Contre : la pastille d'Alex (ProConRow, une liste de FM) en face de chaque phrase
  (ProConsLongString), sur person.PlayerReportForContextTeam (team = human.Team, comme l'en-tête de FM). La fenêtre
  prend la hauteur de son contenu ; la phase cachée est à max-height 0 (pas display: none : les transitions de ses
  coups de tampon partent quand on y arrive). v4 (Kinito, v3 vue en jeu) : chaque phase en deux colonnes ; une phrase
  Pour / Contre coupée finit par « … » (classe de FM content-ellipsis) et FM montre la phrase entière au survol
  (DisplayTooltipWhenElided, comme 37 textes de FM) ; niveau et potentiel en étoiles dans l'en-tête, par les deux
  blocs de FM d'AbilityInfoHorizontal (report.ScoutedCurrentAbilityInfo / ScoutedPotentialAbilityInfo.StarRange,
  cellule data_display-cell-ability-regular, incluse par son GUID). v7 : à l'écran 1, niveau et potentiel dans les
  colonnes (sous les médias, sous le projet à long terme) ; l'en-tête ne les montre qu'à l'écran 2.
- LES CLICS : « Passer au rapport » copie vrai dans une variable de la fenêtre ; « Dévoiler la carte entière » envoie [vrai
  dans le signal du rideau, ouvrir la fiche (événement « ouvrir un écran » de 26.2 / 26.4, panneau PlayerReport, player
  et team, comme PlayerReportTile_2x1), fermer la fenêtre (événement de FM 146,27,56,49 + son panneau, comme
  GoOnHolidayFloatingBlock)].
- LE RIDEAU : dans PlayerReport (aucun script d'Alex ni d'autre ajout n'y touche), un ComponentElement à nous déclare le
  signal avec une clé « Persistent, Explicit » (la clé de rangement n'est faite que de ses deux noms : la fenêtre et la
  fiche partagent la valeur, PersistenceUtils.GetPersistenceKey) ; un SIVisible dessus montre le rideau, qui glisse
  (classe posée 0,05 s après, transition), puis un SIDelayEvent remet le signal à faux : ouverte d'ailleurs, la fiche
  n'a rien.
- v3, LE RIDEAU MANUEL (option de l'app « rideau_jeunes », Kinito 09/11 : « j'ouvre moi-même le rideau petit à petit,
  il reste au milieu si je l'arrête au milieu ») : un SISlider de FM (celui de ContractDetailsMLSWindow, même fichier
  que la fiche) sur toute la fiche, avec la barre de remplissage d'Unity (fill) et inverted. Code d'Unity 6000.3 lu
  (BaseSlider.UpdateFill) : inversé, la barre va de la poignée au bord droit (left = (1 - n) %), donc c'est le rideau,
  et la poignée (dorée) est son bord ; un clic sur le rideau y amène la poignée, puis on tire. v5 (v4 vue en jeu) :
  SISlider n'applique pas inverted (le rideau se retirait vers la gauche, poignée partie de droite) ; le curseur, non
  inversé, est retourné à l'horizontale (scale -1 1) : la poignée part de gauche, le rideau se retire vers la droite.
  Sa valeur va dans une
  variable Float à nous par son DataLink (comme les champs de FM : liste à recherche, sélecteur de couleur) ; ouvert en
  entier (valeur 0), un SIVisible BindIntToVisible (TryCastToInt, comme FM sur ses variables Float de la tactique)
  retire le curseur, qui sinon prendrait tous les clics de la fiche. Le signal est remis à faux après 0,4 s ; une
  variable locale (non rangée) garde le rideau tant que la fiche est ouverte.
- LE NOM DE LA CARTE (26.19, nos morceaux nommés) : pour les groupes de l'option, un SIButton par-dessus le lien de FM
  (SIVisible du repère du groupe > SIVisible de l'interrupteur), qui ouvre la fenêtre ; ailleurs, le lien de FM ouvre
  la fiche comme avant.
- L'INTERRUPTEUR : la zone de 26.19 v24 déclare kinitorevelationactive (clé « Persistent, Explicit », vrai au départ) ;
  deux SIButton dans des SIVisible (vrai / faux) y copient faux / vrai.
- v9, LE CHOIX EN JEU (Kinito, 09/11 : « dévoiler la fiche comporte un choix », chaque façon automatique OU manuelle,
  « dans un menu déroulant ») : notre pastille est un ComponentElement de FM qui déclare deux variables rangées
  (clés « Persistent, Explicit » : kinitodevoile, Float 1 à 4 ; kinitodevoilemanuel, Bool) ; la fiche déclare les
  mêmes (même clé : même valeur, comme le signal du rideau). Le menu (mesuré le 09/11, lecture seule) : le BindingSetter
  de LiveCupDrawButtons déclare option1…option4 = Float|1|…|4|, la fonction de FM BindCreateListSIDropdown (5b2e64da)
  en fait la liste, le modèle inclus « dropdown-secondary » (la flèche seule, de SetPieceInstructionRow) montre le
  choix fermé avec le modèle de ligne (UseRowTemplateToShowSelectedValue, 725 menus de FM) et l'écrit dans
  kinitodevoile (SelectionValueBinding) ; ses événements de FM retirés. La ligne : AnimTransitionSpeedDropdownRow
  (global, cité par rien) réécrit en la ligne du menu des tirages (SpeedMultiplierDropdownRow, paramètre « row »),
  un SIVisible de FM par choix (« row == k ») et son nom. La bascule Auto | Manuel : le mode choisi en plein (clair),
  l'autre à cliquer (il y copie vrai ou faux).
- v9, LA FICHE : les 4 façons x 2 modes posées, chacune sous « façon == k » (SIVisible de FM) et sous le mode.
  Automatique (3 s, classe posée 0,05 s après l'arrivée) : fondu (opacité), rideau (glisse, avec ses plis), balayage
  (le cache reste, sa largeur va à 0 : bord doré et trait de lumière), portes (deux battants qui s'écartent depuis le
  milieu). Manuel : le curseur de FM ; rideau et balayage = la barre du curseur est le cache (v5) ; fondu et portes =
  une barre dorée sous la fiche et 20 paliers (« valeur > (j - 1) x 50 » ; fondu : opacités choisies pour que le total
  fasse j / 20 ; portes : battants de plus en plus larges, posés du plus étroit au plus large) ; la fiche ne prend pas
  de clic tant qu'elle n'est pas découverte. L'option de l'app « rideau_jeunes » n'est plus que le mode de départ.

Retirer : la fenêtre, la fiche, la ligne du menu et le panneau remis d'origine ; nos morceaux, nos règles marquées
(REPERE_REGLE) et la déclaration du modèle inclus du menu enlevés de la carte et de la catégorie.

Usage : python kinito_revelation_jeunes.py appliquer|retirer|etat|si-actif [--dry-run]
"""
import copy
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from langue import texte as L  # noqa: E402
from notes_installations import first, _enc_varint  # noqa: E402
import notes_installations as ni  # noqa: E402
from arbre import Tree  # noqa: E402
import kinito_cartes_jeunes as cj  # noqa: E402  (les cartes 26.19 et leurs outils)

VERSION = 18  # v1 (09/11/2026) : fenêtre « Dossier du recruteur » (2 phases), rideau sur la fiche, interrupteur en jeu
#               v2 (09/11, v1 vue en jeu) : hauteur du contenu ; projets écrits comme la personnalité, court et long
#               terme toujours ; phase 2 = les points Pour / Contre (pastilles d'Alex et phrases)
#               v3 (09/11) : le rideau manuel, au choix dans l'app (option « rideau_jeunes », automatique par défaut)
#               v4 (09/11, v3 vue en jeu) : phase 1 en deux colonnes (personnalité et médias | projets), phase 2 en
#               deux colonnes (Pour | Contre), phrase coupée = « … » et infobulle de FM avec la phrase entière ; niveau
#               et potentiel en étoiles dans l'en-tête ; rideau automatique en 3 s ; fenêtre plus large
#               v5 (09/11, v4 vue en jeu) : rideau manuel de gauche à droite (curseur retourné : SISlider n'applique
#               pas inverted, vu en jeu) ; écran 1 à la largeur de son contenu (colonnes à leur taille), écran 2 à
#               880 px ; niveau et potentiel sur une ligne à l'écran 2
#               v6 (09/11, v5 vue en jeu) : niveau et potentiel au plus près du nom (le bloc du nom à la largeur exacte
#               du nom, plus de minimum de 110 px ; 14 px d'écart ; étiquettes de 70 px au lieu de 84)
#               v7 (09/11, v6 vue en jeu) : écran 1 : niveau sous les rapports avec les médias, potentiel sous le
#               projet à long terme, « Passer au rapport » sous le potentiel, le tampon du groupe juste après le nom
#               (dans l'en-tête, en flux : plus en absolu) ; écran 2 plus étroit : la largeur de son en-tête, 640 px
#               au moins (les phrases ne l'élargissent plus : flex-basis 0 ; coupées, entières au survol)
#               v8 (09/11, v7 vue en jeu) : écran 1 : niveau et potentiel EN HAUT des colonnes (au-dessus de la
#               personnalité et du projet à court terme), coups de tampon dans l'ordre de lecture ; le reste ne change pas
#               v9 (09/11, v8 construite ; Kinito : « dévoiler la fiche comporte un choix », chaque façon en auto OU
#               manuel) : quatre façons de dévoiler la fiche (fondu, rideau, balayage, portes), chacune automatique
#               ou manuelle, choisies EN JEU sur le message (un menu de FM « Fiche : Rideau », une bascule Auto /
#               Manuel), à côté de « Révélation : oui » ; l'option de l'app « rideau_jeunes » = le mode de départ
#               v10 (09/11, v9 vue en jeu : « Rideau » bien écrit, mais la rangée grandissait et les pastilles
#               débordaient de la barre ; Kinito veut aussi le style des cartes en jeu) : le menu (code dans 26.19
#               v25) a son CHAMP (créé par FM) ramené à la hauteur de la barre ; pastilles un peu plus étroites ; le
#               bouton du nom posé dans les 8 styles de la carte (26.19 v25)
#               v11 (09/11, v10 vue en jeu : « pour tous les styles, c'est le style recruteur ») : UN PACK PAR STYLE
#               DE CARTE (maquettes validées) : la fenêtre porte les 8, chacun sous « style == k » (le style passé
#               par la carte) ; même mise en page, matière, bande, photo, tampon, boutons et entrée du style ; J =
#               le dossier d'avant
#               v12 (10/11, v11 vue en jeu) : I : la barre de lecture aussi sur l'écran du rapport ; O : écran 1 en
#               2 s environ au lieu de 5 (l'écran 2 ne change pas)
#               v13 (10/11, maquette v2 validée : « Oui, construis ») : l'OUVERTURE au 1er clic sur le dos d'une
#               carte (la carte en grand au centre, une ouverture par style, puis « Ouvrir le dossier ») ; une
#               CROIX en haut à droite (ouverture et dossier : ferme la fenêtre ; fiche : enlève le cache)
#               v14 (10/11, v13 vue en jeu) : la croix du dossier dans le bandeau, centrée en hauteur, au dessin
#               du bouton du style ; celle de l'ouverture à côté d'« Ouvrir le dossier », au même dessin ; la
#               grande carte s'ouvre en même temps que la petite (minutage A3 de 26.19)
#               v15 (10/11, maquette v4 validée) : la fiche couverte par l'ÉCRAN DU STYLE (photo, poste, niveau,
#               potentiel, personnalité, médias, projets, Pour / Contre), qui part avec le cache : fondu en deux
#               temps, rideau, portes (balayage retiré) ; en manuel, notre cache suit la barre par crans de 2,5 % ;
#               le groupe passé de la fenêtre à la fiche
#               v16 (10/11, v15 vue en jeu : « sur l'holographique, faire apparaître les infos seulement au passage
#               du scan ») : I : un cache à la matière du dossier recule avec la barre de lecture, au pixel près (les
#               deux bougent en % de la même boîte, à la même vitesse) : écran 1, tout sous la bande ; écran 2, sous
#               l'en-tête ; la barre de la catégorie passe SOUS la barre de couleur d'Alex en taille de texte Normal
#               et plus, quand la révélation est sur oui (26.19 v29 : sa barre placée par une règle)
#               v17 (10/11, Kinito : « un seul bloc dans l'appli » ; « de base en jeu on met manuel, on enlève le
#               choix dans l'appli ») : posée par les cartes (26.19 v30 lance ce script, appliquer / retirer / etat) ;
#               le mode de départ est manuel, sans option de l'app (« rideau_jeunes » n'est plus lue ;
#               KINITO_OPTION_RIDEAU reste pour les bancs) ; les groupes restent une option de l'app (son choix)
#               v18 (10/11, Kinito : « les groupes en jeu, comme les autres ») : dans le message, un menu de FM
#               « Révélation : Non / Élite / Élite et excellents / Tous » à la place de « Révélation : oui / non »
#               (variable rangée de la zone, cj.V_REV, départ Élite) ; la carte porte la révélation pour les 5
#               groupes, chacun montré par une comparaison de FM sur ce menu (jamais un booléen lu comme un nombre) ;
#               plus d'option de l'app ; la barre passe sous celle d'Alex en texte Normal et plus, quel que soit le
#               menu ; la ligne du menu « Fiche » sert aussi à ce menu (valeurs 11 à 14)
PREFIXE ="UIPickerKinito-revelation-jeunes"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_revelation_jeunes.actif")
OPTION = "revelation_jeunes"   # l'option de l'app d'Alex : les groupes qui ont la révélation (1re valeur = défaut)
GROUPES_OPTION = {"elite": 1, "deux": 2, "tous": 5}
FENETRE = "EndOfDemoDialog"                         # modèle (gameworld) et panneau (ui-panelids) de la fenêtre
PANNEAU = "EndOfDemoDialog"
GUID_PANNEAU = "cc7e1093d501d67468041e3cc54289ba"
PANNEAUX = os.path.join(nb.AA, "ui-panelids_assets_all.bundle")
FICHE = "PlayerReport"                              # la vraie fiche du joueur (modèle et panneau)
GUID_FICHE = "77188c7bbd58fe54f9aa75e6d2c9a146"
# v2 : les morceaux de FM de 26.20 (vus en jeu), pris dans les modèles D'ORIGINE
SOURCE_ELEMENT = ("TransferBlockMainFrame", "firstItem")   # la fonction « élément n d'une liste » (21ee6b43)
SOURCE_SETTER = "report-player-banner-max"                 # un BindingSetter de FM (porteur des variables)
SOURCE_LISTE_PC = ("TeamMeetingBlock", "Players")          # la WrappedObjectList des pastilles d'Alex
SOURCE_PC = "ScoutedProsAndCons"                           # son paramètre « report » : le type du rapport
GUID_PASTILLE = "1d9ea6f83e853594c9a3339ba036281b"         # ProConRow, la pastille d'Alex (paramètre « procon »)
NOM_PASTILLE = "UIPickerPastilleBandeau-v"                 # son nom quand Alex l'a réécrite
RAPPORT = "person.PlayerReportForContextTeam"
EQUIPE_HUMAIN = "human.Team"
PROJETS_MAX = 5             # projets montés par liste (ses lectures FM 27 : 3 au plus)
PC_MAX = 10                 # points Pour / Contre montés par liste (une ligne fixe en face de chaque pastille)
PAS_PC = 30                 # px : la pastille d'Alex (28) et ses marges (1 + 1) : la hauteur d'une ligne de phrase
V_PROJET, V_PC = "kinitorevprojet", "kinitorevpc"
OP_EGAL, OP_SUP = 2, 4      # opérateurs des comparaisons de FM (BindIntToVisible)
OP_INF_EGAL, OP_SUP_EGAL = 1, 3   # v15 (relevés dans club_amical et hierarchie_pyramide, vus en jeu)
HAUT_LIBRE = 4000           # px : max-height de la phase montrée (la cachée est à 0)
ECHELLE_TAMPON = 1.3        # v2 : 1,6 en v1 ; les blocs sont maintenant larges (toute la fenêtre)
P_INTRO = "kinitorevintro"   # v13 : vrai quand la fenêtre est ouverte par le DOS de la carte (l'ouverture d'abord)
P_ON, P_GROUPE = "kinitorevelation", "kinitogroupe"   # paramètres de la fenêtre (vrai / le groupe i)
PARAMS = [(P_ON, 0), ("person", cj.TYPE_PERSONNE), ("player", cj.TYPE_PERSONNE), ("team", cj.TYPE_EQUIPE),
          ("human", cj.TYPE_PERSONNE)] + [(f"{P_GROUPE}{i}", 0) for i in range(5)] + [
          (cj.V_STYLE, 0), (P_INTRO, 0)]   # v11 : le style de la carte ; v13 : vrai = ouverte par le dos (ouverture)
V_OUVERT, V_PHASE2 = "kinitorevouvert", "kinitorevphase2"   # variables de la fenêtre
V_RIDEAU = "kinitorideau"                                    # signal fenêtre -> fiche (même clé des deux côtés)
CLE_RIDEAU = "(Persistent,Explicit,{kinito-revelation},{rideau})"
V_RIDEAU_GO = "kinitorideaugo"
DELAI_OUVERT = 0.05         # s : la classe d'ouverture posée après l'arrivée de la fenêtre (une transition demande un
#                             changement après l'affichage)
PAS_TAMPON = 0.30           # s : un coup de tampon par information
DEBUT_TAMPON = 0.55         # s : premier coup, après l'arrivée de la fenêtre (0,6 s)
DUREE_RIDEAU, DELAI_RIDEAU, FIN_RIDEAU = 3.0, 0.10, 3.6     # s : le rideau glisse (v4 : 3 s, Kinito ; 1,15 avant),
#                                                             puis le signal est remis à faux
FEN_MIN = 640               # v7 : px, largeur MINIMALE de la fenêtre à l'écran 2 (880 fixes en v4 à v6) : elle prend
#                             la largeur de son en-tête ; l'écran 1 prend celle de son contenu ; la hauteur suit le contenu
COL1_MAX, COL2_MAX, ECART_COL1 = 400, 380, 40   # v5 : px, écran 1 : colonnes à leur taille (plafonnées), écart fixe
#                                                 (v7 : 400 au lieu de 300 : des rapports avec les médias à trois
#                                                 libellés gardent leur taille au lieu de rapetisser)
ECART_TAMPON = 24           # v7 : px avant le tampon du groupe, dans l'en-tête (Kinito : « on rapproche Élite du nom »)
CL_ETOILES = "kinito-rev-etoiles"   # v7 : la ligne niveau / potentiel de l'en-tête, montrée à l'écran 2 seulement
CL_PIED = "kinito-rev-pied"         # v7 : le pied (« Dévoiler la carte entière »), montré à l'écran 2 seulement
ECART_NOM_ETOILES = 14      # v6 : px entre le nom et « NIVEAU » (v7 : à l'écran 2)
ECART_ETIQUETTE, ECART_LIGNE2 = 8, 24   # v7 : px, écran 2 : étiquette -> étoiles, niveau -> potentiel (sur une ligne,
#                                         les étiquettes n'ont plus à s'aligner : à leur taille)
# v4 : niveau et potentiel en étoiles (les deux blocs d'étoiles de FM d'AbilityInfoHorizontal : BindingRemapper
# starrating = report.Scouted…AbilityInfo.StarRange, et la cellule data_display-cell-ability-regular)
SOURCE_ETOILES = "AbilityInfoHorizontal"
CHEMINS_ETOILES = ("report.ScoutedCurrentAbilityInfo.StarRange", "report.ScoutedPotentialAbilityInfo.StarRange")
TEXTE_NIVEAU, TEXTE_POTENTIEL = L("NIVEAU", "ABILITY"), L("POTENTIEL", "POTENTIAL")
CLASSE_COUPE = "content-ellipsis"   # v4 : classe de FM (une ligne, overflow hidden, « … »), avec DisplayTooltipWhenElided
TAILLE_PHRASE = 14          # px : une phrase Pour / Contre (v4 : taille fixe, coupée par « … » ; 15 qui rétrécissait)
ENCRE, GRIS, PAPIER_POL = "#F3EEE2", "#D9D3C3", "#E9E5DB"
FOND_RIDEAU, BORD_RIDEAU = "#10131A", "#F2C14E"
TEXTE_ONGLET = L("JEUNES", "YOUTH")
TEXTE_FICHE = L("FICHE DU RECRUTEUR", "SCOUT REPORT")
TEXTE_PERSO = L("PERSONNALITÉ", "PERSONALITY")
TEXTE_MEDIAS = L("RAPPORTS AVEC LES MÉDIAS", "MEDIA HANDLING")
TEXTE_COURT = L("PROJET À COURT TERME", "SHORT-TERM PLAN")
TEXTE_LONG = L("PROJET À LONG TERME", "LONG-TERM PLAN")
TEXTE_POUR = L("POUR", "PROS")
TEXTE_CONTRE = L("CONTRE", "CONS")
TEXTE_RIEN = L("Rien de relevé", "Nothing noted")
LISTES_PROJETS = (("c", TEXTE_COURT, "person.ShortTermPlanList", "person.ShortTermPlanListCount"),
                  ("l", TEXTE_LONG, "person.LongTermPlanList", "person.LongTermPlanListCount"))
LISTES_PC = (("p", TEXTE_POUR, "report.ScoutedProConsList.ProsList", "report.ScoutedProConsList.ProsCount", "+"),
             ("c", TEXTE_CONTRE, "report.ScoutedProConsList.ConsList", "report.ScoutedProConsList.ConsCount", "–"))
TEXTE_PASSER = L("Passer au rapport", "Go to the report")
TEXTE_DEVOILER = L("Dévoiler la carte entière", "Reveal the full card")
TEXTE_OUI = L("Révélation : oui", "Reveal: on")     # (jusqu'à la v17)
TEXTE_NON = L("Révélation : non", "Reveal: off")
TEXTE_REV = L("Révélation :", "Reveal:")           # v18 : le menu des groupes
CL_MENU_REV = "kinito-rev-menu-groupes"
# v18 : (valeur, nom dans la liste, nom court dans le menu fermé), dans l'ordre de la liste
CHOIX_REV = ((cj.REV_NON, L("Non", "No"), L("Non", "No")),
             (cj.REV_ELITE, L("Élite", "Elite"), L("Élite", "Elite")),
             (cj.REV_DEUX, L("Élite et excellents", "Elite and top"), L("Élite + exc.", "Elite + top")),
             (cj.REV_TOUS, L("Tous les groupes", "All groups"), L("Tous", "All")))
SEUIL_GROUPE = (cj.REV_ELITE, cj.REV_DEUX, cj.REV_TOUS, cj.REV_TOUS, cj.REV_TOUS)   # groupe i : menu >= seuil
CL_ON, CL_OUVERT, CL_PHASE2 = "kinito-rev-on", "kinito-rev-ouvert", "kinito-rev-phase2"
CL_F1, CL_F2, CL_F3 = "kinito-rev-f1", "kinito-rev-f2", "kinito-rev-f3"   # opacité / glissé / rotation de la fenêtre
CL_P1, CL_P2 = "kinito-rev-p1", "kinito-rev-p2"
CL_BOUTON1, CL_BOUTON2 = "kinito-rev-bouton1", "kinito-rev-bouton2"
CL_RIDEAU, CL_RIDEAU_GO = "kinito-rideau", "kinito-rideau-go"
ID_ROTATE = 327680          # StylePropertyId « rotate » (cj : sm.PROPRIETES)
ID_MAX_HAUT = 131094        # StylePropertyId « max-height » (cj : sm.PROPRIETES)
# v3 : le rideau manuel
OPTION_RIDEAU = "rideau_jeunes"   # l'option de l'app : le rideau de la fiche (1re valeur = défaut)
MODES_RIDEAU = ("auto", "manuel")
SOURCE_CURSEUR = "ContractDetailsMLSWindow"   # son SISlider (bundle gameworld, comme PlayerReport : type déclaré)
CHAMPS_CURSEUR = ("valueOverride", "lowValue", "highValue", "fill", "inverted", "direction", "pageSize",
                  "showInputField", "DataLink", "UseIntegerValues", "InitialiseBindingFunc", "SliderSteps")
V_MANUEL, V_VAL = "kinitorideaumain", "kinitorideauval"   # variables locales de la fiche (non rangées)
VAL_MAX = 1000              # le curseur va de 0 (ouvert) à 1000 (fermé), en entiers (UseIntegerValues : 1,9 px par cran
#                             en 1920 de large ; un entier pour les comparaisons de FM)
FIN_SIGNAL = 0.40           # s : le signal remis à faux (le rideau reste par la variable locale, posée à 0,05 s)
POIGNEE = 18                # px : largeur de la poignée dorée (bord du rideau)
CL_MANUEL, CL_CURSEUR = "kinito-rideau-manuel", "kinito-rideau-curseur"
TEXTE_TIRE = L("Tire la barre dorée vers la droite pour dévoiler sa fiche",
               "Drag the gold bar to the right to reveal the profile")
MOT_AUTO = 2                # StyleValueKeyword.Auto (lu dans la feuille « default » de FM : flex: 1 0 auto)
# v9 (Kinito, 09/11 : « dévoiler la fiche comporte un choix », chaque façon en automatique OU manuel, choisi EN JEU sur
# le message) : la façon et le mode sont deux variables rangées (clé « Persistent, Explicit » : la barre du message les
# écrit, la fiche les lit, comme le signal du rideau) ; l'option de l'app « rideau_jeunes » n'est plus que le mode de
# départ (tant qu'on n'a rien choisi en jeu)
V_METHODE = "kinitodevoile"          # Float : 1 fondu, 2 rideau, 3 balayage, 4 portes (les choix du menu de FM)
CLE_METHODE = "(Persistent,Explicit,{kinito-revelation},{devoile})"
V_MODE = "kinitodevoilemanuel"       # Bool : vrai = manuel
CLE_MODE = "(Persistent,Explicit,{kinito-revelation},{manuel})"
METHODES = ((1, "fondu", L("Fondu", "Fade")), (2, "rideau", L("Rideau", "Curtain")),
            (3, "portes", L("Portes", "Doors")))   # v15 : balayage retiré (Kinito : « trop proche du rideau »)
METHODE_DEFAUT = 2                   # le rideau (celui de la v8)
PALIERS = 20                         # manuel, fondu et portes : la barre avance par 20 crans de 5 %
HAUT_BARRE = 46                      # px : la barre dorée sous la fiche (fondu et portes, manuel ; maquette du 09/11)
# le menu en jeu (mesuré le 09/11, vu en jeu en v9 : « Rideau » écrit dans le menu fermé) : depuis la v10, son code
# est dans 26.19 v25 (cj.sources_menu, cj.poser_menu, cj.construire_ligne_menu), qui s'en sert pour le style
MODELE_LIGNE = "AnimTransitionSpeedDropdownRow"   # global, cité par RIEN (modeles_libres.py, 09/11) : réécrit, seul
GUID_LIGNE = "a7b08a801b5b3b04d9c719a0788efb96"   #   propriétaire ; une ligne de menu de FM (paramètre « row »)
TEXTE_MENU = L("Fiche :", "Profile:")
TEXTE_AUTO, TEXTE_MANU = L("Auto", "Auto"), L("Manuel", "Manual")
CL_MENU = "kinito-rev-menu"
CL_GO = "kinito-devoile-go"                       # posée 0,05 s après l'arrivée : les caches automatiques partent
CL_FONDU, CL_BALAYAGE = "kinito-devoile-fondu", "kinito-devoile-balayage"
CL_PORTE_G, CL_PORTE_D = "kinito-devoile-porte-g", "kinito-devoile-porte-d"
CL_COUVRE = "kinito-devoile-couvre"               # manuel, rideau et balayage : la barre du curseur EST le cache
CL_BALAYE = "kinito-devoile-balaye"               # manuel, balayage : la poignée en trait de lumière
CL_BANDE = "kinito-devoile-bande"                 # manuel, fondu et portes : le curseur en barre sous la fiche
PLI = "#1B2130"                                   # les plis du rideau (un peu plus clairs que le cache)
V_VU, V_INTRO_GO = "kinitorevvu", "kinitorevintrogo"   # v13 : l'ouverture vue (« Ouvrir le dossier ») ; son départ
CL_INTRO_GO = "kinito-rev-intro-go"
ZOOM = 1.9                  # v13 : la carte en grand (132 x 220 -> 251 x 418 px en 1080p), depuis le centre de l'écran
# v14 (Kinito : « la carte en arrière-plan se dévoile plus vite que celle en zoom ») : l'ouverture suit l'animation A3
# de la petite carte (26.19, ANIM) : son dos se ferme à 0,25 s (en 0,12 s), sa face s'ouvre à 0,37 s (en 0,28 s),
# découverte à 0,65 s du clic ; la grande part 0,05 s après l'arrivée de la fenêtre (DELAI_OUVERT), d'où le décalage
DEBUT_OUV = cj.ANIM["fermer_a"] - 0.05                            # 0,20 s
FIN_OUV = cj.ANIM["ouvrir_a"] + cj.ANIM["ouvrir"] - 0.05           # 0,60 s
DUREE_ZOOM = 0.35
APPARITION_BOUTONS = FIN_OUV + 0.30   # « Ouvrir le dossier » et sa croix
# v14 : la place du bandeau de chaque dossier (haut en px depuis le haut du pack, retrait à droite), pour y poser la
# croix ; J : la bande de la feuille (posée à 12 px, comme la feuille), les autres : bande() de fond_pack
BANDE = {"j": (12, 20), "d": (8, 16), "a": (12, 22), "i": (8, 16), "l": (20, 18), "n": (14, 20), "o": (20, 24),
         "q": (8, 16)}
HAUT_BANDE, TAILLE_CROIX = 30, 24
# v15 : l'écran du style sur la fiche, et notre cache (maquette v4)
PAUSE_ECRAN = 2.0           # s : en automatique, l'écran reste avant de partir
DUREE_PART, DUREE_FONDU = 3.0, 1.5   # s : rideau et portes ; fondu : l'écran, puis le fond (chacun)
FIN_AUTO = PAUSE_ECRAN + DUREE_PART + 0.4   # s : le cache retiré (automatique)
CRANS, DUREE_CRAN, DELAI_CRAN = 40, 0.12, 0.03   # manuel : 40 crans de 2,5 %, adoucis ; le seuil passe à l'interrupteur
V_CRAN = "kinitocran"        # v15 : interrupteur du cran j (local), allumé par le seuil j de la barre
CL_CRAN, CL_MANU = "kinito-rev-cran", "kinito-rev-manu"
CL_EC_F, CL_EC_FC, CL_EC_R = "kinito-rev-ec-f", "kinito-rev-ec-fc", "kinito-rev-ec-r"   # fondu (cache, écran), rideau
CL_EC_PG, CL_EC_PD = "kinito-rev-ec-pg", "kinito-rev-ec-pd"   # les deux portes
BORD_LARGE = 18              # px : la bande dorée en tête du rideau (maquette)
MARGE_RIDEAU = 53            # px : du bord au début des textes, en rideau (Kinito : la marge de J, pour tous)
BAS_ECRAN = 120              # px : sous l'écran, la place de la consigne et de la barre dorée
V_GROUPE_FEN = "kinitorevg"  # v15 : le groupe, gardé par la fenêtre pour la fiche (variables gardées)


def cle_groupe(i):
    return f"(Persistent,Explicit,{{kinito-revelation}},{{groupe{i}}})"
TEXTE_OUVRIR = L("Ouvrir le dossier", "Open the file")
REPERE_REGLE = "--kinito-revelation-jeunes"       # propriété perso de nos règles à sélecteurs dans la catégorie


def nom(partie):
    return f"{PREFIXE}-v{VERSION}-{partie}"


NOM_FENETRE, NOM_LIGNE = nom("fenetre"), nom("ligne")


def nom_rideau(mode):
    """v9 : les quatre façons et les deux modes sont toujours posés ; <mode> (option de l'app) n'est que le mode de
    départ, écrit dans la déclaration de la variable : il est dans le nom pour qu'un autre choix refasse la fiche"""
    return nom(f"devoilement-{mode}")


def nom_inter(mode):
    return nom(f"interrupteur-{mode}")


def depart_mode(mode):
    return "Bool|1|" if mode == "manuel" else "Bool|0|"


def marques(t):
    return [r for r in t.walk() if (t.name(r) or "").startswith(PREFIXE)]


CODE_JEU = "jeu"   # v18 : les groupes se choisissent en jeu ; la carte porte les 5


def groupes_choisis():
    """(code, nombre de groupes) de l'option de l'app (KINITO_OPTION_REVELATION l'impose : bancs) ; défaut : Élite.
    v18 : PLUS UTILISÉ (les groupes se choisissent en jeu : CODE_JEU, 5 groupes)"""
    v = os.environ.get("KINITO_OPTION_REVELATION")
    if v not in GROUPES_OPTION:
        try:
            import options
            v = options.get(OPTION)
        except Exception:
            v = None
    v = v if v in GROUPES_OPTION else next(iter(GROUPES_OPTION))
    return v, GROUPES_OPTION[v]


MODE_DEPART = "manuel"   # v17 (Kinito : « de base en jeu on met manuel ») : plus d'option dans l'app


def mode_rideau():
    """le mode de départ du dévoilement (avant tout choix en jeu) : manuel ; KINITO_OPTION_RIDEAU l'impose (bancs).
    v17 : l'option de l'app (« rideau_jeunes ») n'est plus lue : « Auto | Manuel » se choisit dans le message"""
    v = os.environ.get("KINITO_OPTION_RIDEAU")
    return v if v in MODES_RIDEAU else MODE_DEPART


# ---------- événements (format de FM, refait à l'octet près) ----------
def _bloc(b):
    return struct.pack("<i", len(b)) + b


def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def ouvrir_panneau(guid, params):
    """« ouvrir le panneau <guid> avec ces paramètres » (format d'evenement_ecran / 26.4, vu en jeu)"""
    corps = bytes([211, 101, 102, 7, 2])
    corps += _bloc(bytes([1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0]))
    corps += _bloc(bytes([1, 0, 1, 1, 1, 32]) + guid.encode() + bytes([1, 0, 3, 0, 0, 0, 1, 1, 0]))
    corps += b"\x01\x01" + _enc_varint(len(params))
    for n, chemin in params:
        corps += _bloc(_texte(n) + _bloc(_texte(chemin)) + b"\x00")
    return corps + b"\x00\x00"


def fermer_panneau(guid):
    """« fermer le panneau <guid> » (relevé le 09/11 sur les deux boutons de GoOnHolidayFloatingBlock)"""
    return bytes([146, 27, 56, 49, 1, 1, 1, 1, 32]) + guid.encode() + bytes([1, 0])


def evenements_ok():
    """nos événements refaits = ceux de FM, octet par octet (relevés le 09/11)"""
    ferme = cj.liste([fermer_panneau("556e00163ab34794dbe1c6854b99f77f")])
    attendu_ferme = ([1, 1, 1, 1, 1, 43, 0, 0, 0, 146, 27, 56, 49, 1, 1, 1, 1, 32] + list(b"556e00163ab34794dbe1c6854b99f77f")
                     + [1, 0])
    fiche = cj.liste([ouvrir_panneau(GUID_FICHE, [("player", "Person"), ("team", "reportcontextteam")])])
    attendu_fiche = ([1, 1, 1, 1, 1, 139, 0, 0, 0, 211, 101, 102, 7, 2, 11, 0, 0, 0, 1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0, 47, 0,
                      0, 0, 1, 0, 1, 1, 1, 32] + list(GUID_FICHE.encode())
                     + [1, 0, 3, 0, 0, 0, 1, 1, 0, 1, 1, 2, 23, 0, 0, 0, 1, 1, 6] + list(b"player")
                     + [9, 0, 0, 0, 1, 1, 6] + list(b"Person") + [0, 32, 0, 0, 0, 1, 1, 4] + list(b"team")
                     + [20, 0, 0, 0, 1, 1, 17] + list(b"reportcontextteam") + [0, 0, 0])
    return ferme == attendu_ferme and fiche == attendu_fiche and cj.evenements_ok()


# ---------- outils ----------
def s_(v):
    return (3, {"unit": 3, "value": float(v)})


def px(v):
    return (3, {"unit": 1, "value": float(v)})


def pc(v):
    return (3, {"unit": 2, "value": float(v)})


def tr(prop, duree, delai, courbe):
    return [(cj.ID_T_PROP, "", [(7, prop)]), (cj.ID_T_DUREE, "", [s_(duree)]), (cj.ID_T_DELAI, "", [s_(delai)]),
            (cj.ID_T_COURBE, "", [(7, courbe)])]


def R(t, selecteurs, props):
    return cj.regle_selecteurs(t, selecteurs, props)


def delai(t, src, parent, duree, evenements, n=None):
    td, rd = src["delai"]
    d = cj.seul(t, td, rd, parent, n)
    cj.sans_clic(t, d)
    t.styles.style(t, d, {"position": "absolute", "width": 0, "height": 0})
    sd = t.sd(d)
    sd["m_duration"], sd["m_duration_UxmlAttributeFlags"] = float(duree), 1
    sd["TransitionEvents"], sd["TransitionEvents_UxmlAttributeFlags"] = {"m_bytes": cj.liste(evenements)}, 1
    return d


def bouton(t, src, parent, evenements, css, n=None, classes=()):
    """un SIButton de FM (celui de ContractNegotiationLink, comme le dos des cartes), sans contour : ses événements"""
    tb, rb = src["bouton"]
    b = cj.seul(t, tb, rb, parent, n, classes)
    sd = t.sd(b)
    sd["Events"], sd["Events_UxmlAttributeFlags"] = {"m_bytes": cj.liste(evenements)}, 1
    t.styles.style(t, b, {"border-top-width": 0, "border-bottom-width": 0, "border-left-width": 0,
                          "border-right-width": 0, "margin-top": 0, "margin-bottom": 0, "margin-left": 0,
                          "margin-right": 0, "padding-top": 0, "padding-bottom": 0, "padding-left": 0,
                          "padding-right": 0, "background-color": (0.0, 0.0, 0.0, 0.0), **css})
    return b


def texte_bouton(t, src, parent, s, couleur, taille):
    ttx, rtx = src["cat_texte"]
    r = cj.texte_fixe(t, ttx, rtx, parent, s, ["body-sm-strong"], {"color": cj.rgba(couleur), "font-size": taille,
                                                                    "white-space": "nowrap"})
    cj.sans_clic(t, r)
    return r


# ---------- v2 : les listes (projets, Pour / Contre), comme 26.20 ----------
def fonction_element():
    """la fonction de FM « élément n d'une liste » (BindListItemUsingIndexToDestination, 21ee6b43), celle de
    TransferBlockMainFrame qui met le 1er élément dans firstItem, recopiée avec ses arguments (26.13 v36, 26.20 : vue
    en jeu) ; None si introuvable"""
    o = ouvrir(SOURCE_ELEMENT[0], depart_original=True)
    if o is None:
        return None
    tm = o[3]
    for r in tm.walk():
        fs = tm.sd(r).get("BindFunction") if r in tm.refs else None
        for f in fs if isinstance(fs, list) else []:
            if (f.get("m_target") or {}).get("m_guid", "").startswith("21ee6b43"):
                args = ni.decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
                if len(chemins) == 2 and bytes(chemins[1][1]).endswith(SOURCE_ELEMENT[1].encode()) \
                        and sum(1 for a in args if bytes(a[0]).endswith(b"Int32VisualArg")) == 1:
                    return copy.deepcopy(f)
    return None


def _chemin_arg(c):
    b = c.encode()
    return bytes([1, len(b)]) + b   # (longueur < 128 : un octet)


def element_de_liste(fn, liste, index, destination):
    f = copy.deepcopy(fn)
    args = ni.decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
    chemins[0][1], chemins[1][1] = _chemin_arg(liste), _chemin_arg(destination)
    next(a for a in args if bytes(a[0]).endswith(b"Int32VisualArg"))[1] = struct.pack("<i", index)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = ni.encode_args(args)
    return f


def pastille_alex():
    """vrai si ProConRow, dans le jeu tel qu'il est, est la pastille d'Alex (26.20)"""
    try:
        _b, _o, tt = nb.find_vta("ProConRow")
    except Exception:
        return False
    if not tt:
        return False
    s = Tree(tt)
    return any((s.name(r) or "").startswith(NOM_PASTILLE) for r in s.walk())


def sources22():
    """les morceaux de FM de la v2 (modèles d'origine) ; une valeur None si introuvable"""
    out = {}
    o = ouvrir(SOURCE_SETTER, depart_original=True)
    ts = o[3] if o else None
    rs = ts and first(ts, lambda r: typ(ts, r).endswith("BindingSetter"))
    out["setter"] = (ts, rs) if rs is not None else None
    out["fn_element"] = fonction_element()
    sv, rv = ni.visible_model()
    out["comparer"] = (sv, rv) if rv is not None else None
    out["pastille"] = pastille_alex()
    o = ouvrir(SOURCE_LISTE_PC[0], depart_original=True)
    tl = o[3] if o else None
    rl = tl and first(tl, lambda r: tl.name(r) == SOURCE_LISTE_PC[1] and typ(tl, r).endswith("WrappedObjectList"))
    out["liste_pc"] = (tl, rl) if rl is not None else None
    o = ouvrir(SOURCE_PC, depart_original=True)
    tp = o[3] if o else None
    racine = tp.children(tp.tt["m_VisualTree"]["rid"]) if tp else []
    out["type_rapport"] = next((q["type"]["id"] for q in (tp.sd(racine[0]).get("Parameters") or [])
                                if q.get("name") == "report"), None) if racine else None
    # v4 : les deux blocs d'étoiles de FM (BindingRemapper starrating + la cellule incluse), niveau puis potentiel
    o = ouvrir(SOURCE_ETOILES, depart_original=True)
    te = o[3] if o else None
    blocs = []
    for c in CHEMINS_ETOILES:
        r = te and first(te, lambda r: typ(te, r).endswith("BindingRemapper") and [
            (m.get("from"), (m.get("to") or {}).get("m_path")) for m in te.sd(r).get("Mappings") or []] ==
            [("starrating", c)])
        if r is not None and len(te.children(r)) == 1 \
                and te.elem(te.children(r)[0]).get("m_TemplateAlias") == "data_display-cell-ability-regular":
            blocs.append(r)
    out["etoiles"] = (te, blocs) if len(blocs) == 2 else None
    return out


def curseur_fm():
    """v3 : le SISlider de FM de ContractDetailsMLSWindow (modèle d'origine), (arbre, élément) ; None si introuvable ou
    si sa forme a changé (un champ attendu manque)"""
    o = ouvrir(SOURCE_CURSEUR, depart_original=True)
    tc = o[3] if o else None
    r = tc and first(tc, lambda r: typ(tc, r).endswith("SISlider"))
    if r is None or not all(c in tc.sd(r) for c in CHAMPS_CURSEUR):
        return None
    return tc, r


def manque22(x):
    m = [n for n in ("setter", "fn_element", "comparer", "type_rapport", "etoiles") if x.get(n) is None]
    if x.get("pastille") and x.get("liste_pc") is None:
        m.append("liste_pc")
    return m


def lignes(t, x, parent, noms, liste, nombre, premier_toujours, faire_ligne):
    """un BindingSetter de FM qui déclare noms[i] = i-ème élément de <liste> (fonction de FM « élément n ») ; la ligne
    i montrée par le NOMBRE (« nombre > i » ; la 1re toujours si premier_toujours) ; faire_ligne(dans, i, variable)"""
    ts, rs = x["setter"]
    s = cj.seul(t, ts, rs, parent)
    sd = t.sd(s)
    sd["ValueVariables"], sd["ValueVariables_UxmlAttributeFlags"] = [], 1
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": n} for n in noms]
    sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    sd["BindFunction"] = [element_de_liste(x["fn_element"], liste, i, n) for i, n in enumerate(noms)]
    sd["BindFunction_UxmlAttributeFlags"] = 1
    t.styles.style(t, s, {"flex-direction": "column", "align-self": "stretch", "flex-grow": 1, "flex-shrink": 1,
                          "min-width": 0})
    sv, rv = x["comparer"]
    b = sv.sd(rv)["Binding"]
    for i, n in enumerate(noms):
        if i == 0 and premier_toujours:
            dans = s
        else:
            dans = ni.new_visible(t, sv, rv, s, None, "", ni.make_binding(b, OP_SUP, [nombre], i))
            t.styles.style(t, dans, {"flex-direction": "column", "align-self": "stretch", "flex-shrink": 0})
        faire_ligne(dans, i, n)
    return s


def si_vide(t, x, parent, nombre):
    """un SIVisible de FM « visible si nombre == 0 »"""
    sv, rv = x["comparer"]
    v = ni.new_visible(t, sv, rv, parent, None, "", ni.make_binding(sv.sd(rv)["Binding"], OP_EGAL, [nombre], 0))
    t.styles.style(t, v, {"flex-direction": "column", "align-self": "stretch", "flex-shrink": 0})
    return v


def pastilles(t, x, parent, chemin):
    """la liste de FM (WrappedObjectList de TeamMeetingBlock, comme 26.20) qui montre la pastille d'Alex pour chaque
    élément de chemin, l'une sous l'autre (chacune en face de sa phrase) ; PC_MAX au plus (les lignes de phrases)"""
    tl, rl = x["liste_pc"]
    w = cj.seul(t, tl, rl, parent)
    sd = t.sd(w)
    sd["ItemTemplate"] = {"m_AssetGUID": GUID_PASTILLE, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["VisualFuncBinding"] = hp.path_arg(sd["VisualFuncBinding"], chemin)
    sd["ItemParamName"] = "procon"
    sd["ItemUssClassName"] = "flex-no-shrink-class"   # (Alex : sinon les pastilles rétrécissent)
    t.styles.style(t, w, {"flex-direction": "column", "flex-shrink": 0, "width": PAS_PC, "min-width": PAS_PC,
                          "max-width": PAS_PC, "max-height": PC_MAX * PAS_PC, "overflow": "hidden",
                          "align-self": "flex-start", "margin-right": 8})
    return w


def tampon(t, src, parent, n, classe_a, classe_b, css=None, clic=False):
    """une information qui arrive « en coup de tampon » : opacité (a) puis échelle (b), deux boîtes (une propriété
    animée par boîte, comme A3 de 26.19)"""
    a = cj.boite(t, src, parent, {"flex-shrink": 0, **(css or {})}, [f"{classe_a}{n}"], clic=clic)
    return cj.boite(t, src, a, {"flex-grow": 1}, [f"{classe_b}{n}"], clic=clic)


def regles_tampons(t, declencheur, classe_a, classe_b, delais):
    for n, d in enumerate(delais):
        R(t, [[(".", f"{classe_a}{n}")]], [(cj.ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", 0.12, d, "linear"))
        R(t, [[(".", declencheur), (".", f"{classe_a}{n}")]], [(cj.ID_OPACITY, "", [(2, 1.0)])])
        R(t, [[(".", f"{classe_b}{n}")]], [(cj.ID_SCALE, "", [(2, ECHELLE_TAMPON), (2, ECHELLE_TAMPON)])]
          + tr("scale", 0.30, d, "ease-out-back"))
        R(t, [[(".", declencheur), (".", f"{classe_b}{n}")]], [(cj.ID_SCALE, "", [(2, 1.0), (2, 1.0)])])


# ---------- v11 : un pack de dossier par style de carte (maquettes validées par Kinito, 09/11 : « Oui, construis ») ----
# même mise en page pour tous (en-tête, deux colonnes, rapport en deux colonnes) ; chaque style a sa matière, sa bande,
# sa photo, son tampon de groupe, ses boutons et son entrée. J = le dossier d'avant, inchangé. Valeurs : maquette
# packs-revelation-v1.html (chantier-cartes-jeunes\maquettes-revelation)
PACKS = {
    "j": dict(bande=TEXTE_FICHE, encre=ENCRE, gris=GRIS, cote=12, haut=42, bas=14, debut=DEBUT_TAMPON,
              pas=PAS_TAMPON, anim="tampon", btn=dict(fond=ENCRE, texte="#2A1D04", rayon=6)),
    "d": dict(bande=L("RAPPORT DU RECRUTEUR", "SCOUT REPORT"), encre="#E6E9ED", gris="#9AA3AD", cote=12, haut=40,
              bas=14, debut=0.25, pas=0.12, anim="leve",
              btn=dict(fond=None, texte="#E6E9ED", bord=("#4A5166", 2), rayon=6)),
    "a": dict(bande=L("FICHE DU JOUEUR", "PLAYER FILE"), encre="#EEF0FF", gris="#B9BEE0", cote=16, haut=48, bas=18,
              debut=0.50, pas=0.18, anim="retourne",
              btn=dict(fond="#1A1C40", texte="#EEF0FF", bord=("#5A5FB0", 2), rayon=16)),
    "i": dict(bande=L("SCAN DU JOUEUR", "PLAYER SCAN"), encre="#EEF0FF", gris="#B9C2D6", cote=14, haut=42, bas=16,
              debut=0.35, pas=0.35, anim="fondu", btn=dict(fond="#7AE7FF", texte="#121622", rayon=6)),
    "l": dict(bande=L("NOUVEAU", "NEW"), encre="#FFFFFF", gris="#FFE9B8", cote=14, haut=56, bas=30, debut=0.75,
              pas=0.25, anim="jaillit", btn=dict(fond="#3A2A0F", texte="#FFE39A", rayon=6)),
    "n": dict(bande=L("LE RECRUTEUR", "THE SCOUT"), encre="#F2F2E8", gris="#B9C4BC", cote=22, haut=52, bas=22,
              debut=0.45, pas=0.40, anim="ecrit", cache="#212F29", duree=0.45,
              btn=dict(fond=None, texte="#F2F2E8", bord=("#C8CCC4", 2), rayon=4)),
    "o": dict(bande=L("DOSSIER", "FILE"), encre="#F1E6C8", gris="#9FB0C2", cote=24, haut=54, bas=24, debut=0.30,
              pas=0.20, anim="ecrit", cache="#0E1B2A", duree=0.60, duree1=0.35,   # v12 : écran 1 en 2 s (5 avant)
              btn=dict(fond="#D9B35B", texte="#0E1B2A", rayon=0)),
    "q": dict(bande=L("CASIER", "LOCKER"), encre="#E6E9ED", gris="#9AA3AD", cote=12, haut=40, bas=14, gauche=22,
              debut=1.15, pas=0.15, anim="tampon",
              btn=dict(fond="#2E3440", texte="#E6E9ED", bord=("#4A5166", 2), rayon=6)),
}
DELAIS_P2 = [0.30, 0.65, 1.10]       # écran 2 : Pour, Contre, « Dévoiler la carte entière »
SCAN = dict(debut=0.20, duree=1.40)  # I : la barre de lecture descend
SCAN2 = dict(debut=0.10, duree=1.00)  # v12 : I, la 2e barre, sur l'écran du rapport (Kinito : « pourquoi pas pour le rapport ? »)
SEUIL_DESSOUS = 100                   # v16 : taille du texte de FM (85 Petit, 100 Normal, 110 Grand, 120 Plus grand) à
#                                       partir de laquelle la barre de la catégorie passe sous celle d'Alex
CL_DESSOUS = "kinito-rev-barre-dessous"
HAUT_TETE, MARGE_ZONE = 86, 4         # px : l'en-tête du dossier et la marge au-dessus des écrans (v16 : le cache de
#                                       l'écran 2 de I commence sous l'en-tête, à haut + 86 + 4)
L_RAYONS = 12                        # L : rayons dorés derrière le sachet


def cl(s, x):
    """les classes d'un style : kinito-rev-<style>-<x>"""
    return f"kinito-rev-{s}-{x}"


def css_bouton(s):
    b = PACKS[s]["btn"]
    css = {"align-self": "stretch", "padding-left": 18, "padding-right": 18, "flex-direction": "row",
           "align-items": "center", "justify-content": "center", **cj.rayons(b["rayon"])}
    if b.get("fond"):
        css["background-color"] = cj.rgba(b["fond"])
    if b.get("bord"):
        css.update(cj.cadre(b["bord"][0], b["bord"][1], b["rayon"]))
    return css


def fond_holo(t, src, parent):
    """I : bleu nuit traversé de bandes de couleur (v16 : à part, le cache du scan la recopie à l'identique)"""
    cj.boite(t, src, parent, {**cj.PLEIN, "background-color": cj.rgba("#10122A"), **cj.rayons(16)})
    holo = cj.boite(t, src, parent, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(16), "opacity": 0.12})
    for i, c in enumerate(("#FF7AD9", "#7AE7FF", "#FFF27A", "#9B7AFF", "#7AFFB2")):
        cj.boite(t, src, holo, cj.ab(left=-200 + i * 220, top=-300, width=110, height=1200,
                                     **{"background-color": cj.rgba(c), "rotate": {"unit": 5, "value": 28.0}}))


def fond_pack(t, src, k, f3, s, pal, decale=0, partie="tout"):
    """la matière du pack, sous le contenu (en absolu, dans f3) ; un SIVisible par groupe quand la couleur du groupe
    entre en jeu (son paramètre n'est passé que par lui) ; v16, I seulement : partie « fond » (la matière) ou
    « dessus » (le cadre et la bande, posés après le cache du scan)"""
    tvi, rvi = src["cat_visible"]
    P_ = PACKS[s]
    bande_css = {"position": "absolute", "top": 0, "height": 30, "-unity-text-align": "middle-left",
                 "-unity-font-style": "bold"}

    def par_groupe():
        for i, g in enumerate(pal):
            gv = cj.visible(t, tvi, rvi, f3, f"{P_GROUPE}{i}")
            cj.sans_clic(t, gv)
            t.styles.style(t, gv, cj.PLEIN)
            yield gv, g

    def bande(parent, couleur, taille, centre=False, gauche=14, haut=0):
        r = cj.boite(t, src, parent, cj.ab(left=0, right=0, top=haut, height=30, **{
            "flex-direction": "row", "align-items": "center",
            "justify-content": "center" if centre else "flex-start", "padding-left": 0 if centre else gauche + decale}))
        cj.texte(k, r, P_["bande"], {"color": cj.rgba(couleur), "font-size": taille, "-unity-font-style": "bold"})
        # (pas d'espacement des lettres : « letter-spacing » n'est pas dans notre table de propriétés)
        return r

    if s == "j":   # le dossier d'avant (chemise, onglet, feuille, bande dorée), inchangé
        for gv, g in par_groupe():
            cj.boite(t, src, gv, {**cj.PLEIN, "background-color": cj.ton(g["sombre"]), **cj.rayons(6)})
            onglet = cj.boite(t, src, gv, cj.ab(left=22, top=-26, width=112, height=26,
                                                **{"background-color": cj.rgba(g["couleur"]), **cj.rayons(6, 6, 0, 0),
                                                   "align-items": "center", "justify-content": "center"}))
            cj.texte(k, onglet, TEXTE_ONGLET, {"color": cj.j_papier(g), "font-size": 13, "-unity-font-style": "bold"})
            papier = cj.boite(t, src, gv, cj.ab(left=12, top=BANDE["j"][0], right=12, bottom=12,
                                                **{"background-color": cj.j_papier(g), **cj.rayons(3)}))
            b = cj.boite(t, src, papier, cj.ab(left=0, right=0, top=0, height=30,
                                               **{"background-color": cj.rgba(g["couleur"]), **cj.rayons(3, 3, 0, 0)}))
            cj.texte(k, b, TEXTE_FICHE, {"position": "absolute", "left": 14 + decale, "top": 0, "height": 30,
                                         "-unity-text-align": "middle-left", "color": cj.j_papier(g), "font-size": 14,
                                         "-unity-font-style": "bold"})
    elif s == "d":   # ardoise, trait du groupe en haut
        cj.boite(t, src, f3, {**cj.PLEIN, "background-color": cj.rgba("#232838"), **cj.cadre("#343B50", 2, 14)})
        for gv, g in par_groupe():
            cj.boite(t, src, gv, cj.ab(left=0, right=0, top=0, height=6, **{"background-color": cj.rgba(g["couleur"]),
                                                                            **cj.rayons(14, 14, 0, 0)}))
        bande(f3, "#9AA3AD", 13, gauche=18, haut=BANDE["d"][0])
    elif s == "a":   # bleu nuit, lueur violette, double contour doré
        cj.boite(t, src, f3, {**cj.PLEIN, "background-color": cj.rgba("#0E1030"), **cj.rayons(18)})
        lueur = cj.boite(t, src, f3, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(18)})
        cj.degrade(t, src, lueur, 5, cj.ton("#9655FF", 0.5), cj.ton("#281E78", 0.0))
        cj.boite(t, src, f3, {**cj.PLEIN, **cj.cadre("#F2C14E", 3, 18)})
        cj.boite(t, src, f3, cj.ab(left=8, top=8, right=8, bottom=8, **cj.cadre("#FFE39A", 1, 12), opacity=0.5))
        bande(f3, "#F2C14E", 20, centre=True, haut=BANDE["a"][0])
    elif s == "i":   # bleu nuit traversé de bandes de couleur, contour argent
        if partie in ("tout", "fond"):
            fond_holo(t, src, f3)
        if partie in ("tout", "dessus"):
            cj.boite(t, src, f3, {**cj.PLEIN, **cj.cadre("#9AA6BA", 2, 16)})
            bande(f3, "#C9D3E6", 13, gauche=18, haut=BANDE["i"][0])
    elif s == "l":   # le sachet : dégradé du groupe, bords sombres en haut et en bas, reflet en biais
        for gv, g in par_groupe():
            fd = cj.boite(t, src, gv, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(8)})
            cj.degrade(t, src, fd, 0, cj.ton(g["couleur"]), cj.ton(g["sombre"]))
        reflet = cj.boite(t, src, f3, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(8)})
        cj.boite(t, src, reflet, cj.ab(left={"unit": 2, "value": 18.0}, top=-400, width=44, height=1400,
                                       **{"background-color": (1.0, 1.0, 1.0, 0.14),
                                          "rotate": {"unit": 5, "value": 26.0}}))
        for cote in ("top", "bottom"):
            cj.boite(t, src, f3, cj.ab(left=0, right=0, **{cote: 0}, height=16,
                                       **{"background-color": cj.rgba("#3A2A0F"),
                                          **(cj.rayons(8, 8, 0, 0) if cote == "top" else cj.rayons(0, 0, 8, 8))}))
        bande(f3, "#3A2A0F", 22, centre=True, haut=BANDE["l"][0])
    elif s == "n":   # ardoise verte dans son cadre en bois
        fd = cj.boite(t, src, f3, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(10)})
        cj.degrade(t, src, fd, 0, cj.ton("#24342D"), cj.ton("#1E2B26"))
        cj.boite(t, src, f3, {**cj.PLEIN, **cj.cadre("#6B4A2B", 10, 10)})
        bande(f3, "#F2F2E8", 20, gauche=22, haut=BANDE["n"][0])
    elif s == "o":   # bleu nuit et or, double cadre
        cj.boite(t, src, f3, {**cj.PLEIN, "background-color": cj.rgba("#0E1B2A"), **cj.rayons(4)})
        cj.boite(t, src, f3, cj.ab(left=10, top=10, right=10, bottom=10, **cj.cadre("#D9B35B", 2, 0)))
        cj.boite(t, src, f3, cj.ab(left=16, top=16, right=16, bottom=16, **cj.cadre("#D9B35B", 1, 0), opacity=0.6))
        bande(f3, "#D9B35B", 20, centre=True, haut=BANDE["o"][0])
    elif s == "q":   # le casier : intérieur sombre, montant de la couleur du groupe
        cj.boite(t, src, f3, {**cj.PLEIN, "background-color": cj.rgba("#1B1F27"), **cj.rayons(6)})
        for gv, g in par_groupe():
            cj.boite(t, src, gv, cj.ab(left=0, top=0, bottom=0, width=12, **{"background-color": cj.rgba(g["couleur"]),
                                                                             **cj.rayons(6, 0, 0, 6)}))
        bande(f3, "#D9DDE3", 20, gauche=26, haut=BANDE["q"][0])


def portes_casier(t, src, k, f3, pal):
    """Q : les deux portes du casier, par-dessus le contenu, peintes à la couleur du groupe (aérations, poignées) ; elles
    s'écartent à l'ouverture (règles plus bas)"""
    tvi, rvi = src["cat_visible"]
    portes = cj.boite(t, src, f3, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(6)})
    for i, g in enumerate(pal):
        gv = cj.visible(t, tvi, rvi, portes, f"{P_GROUPE}{i}")
        cj.sans_clic(t, gv)
        t.styles.style(t, gv, cj.PLEIN)
        for cote, classe in (("left", cl("q", "porte-g")), ("right", cl("q", "porte-d"))):
            p = cj.boite(t, src, gv, cj.ab(**{cote: 0}, top=0, bottom=0, width={"unit": 2, "value": 50.0},
                                           **{"overflow": "hidden", **cj.cadre("#000000", 3, 0)}), [classe])
            cj.degrade(t, src, p, 0, cj.ton(g["couleur"]), cj.ton(g["sombre"]))
            for y in (22, 34, 46):
                for haut in (True, False):
                    cj.boite(t, src, p, cj.ab(left={"unit": 2, "value": 22.0}, width={"unit": 2, "value": 56.0},
                                              **({"top": y} if haut else {"bottom": y}), height=5,
                                              **{"background-color": cj.ton("#000000", 0.35), **cj.rayons(3)}))
            cj.boite(t, src, p, cj.ab(**{("right" if cote == "left" else "left"): 10}, top={"unit": 2, "value": 44.0},
                                      width=10, height=50, **{"background-color": cj.ton("#000000", 0.4),
                                                              **cj.cadre("#FFFFFF", 2, 5)}))


def rayons_sachet(t, src, parent):
    """L : des rayons dorés derrière le sachet, qui tournent une fois (pas de boucle)"""
    tout = cj.boite(t, src, parent, cj.ab(left={"unit": 2, "value": 50.0}, top={"unit": 2, "value": 50.0}, width=0,
                                          height=0))
    o = cj.boite(t, src, tout, cj.ab(left=-700, top=-700, width=1400, height=1400), [cl("l", "rayons-o")])
    r = cj.boite(t, src, o, cj.PLEIN, [cl("l", "rayons")])   # (une propriété animée par couche)
    for i in range(L_RAYONS):
        cj.boite(t, src, r, cj.ab(left=685, top=0, width=30, height=1400,
                                  **{"background-color": cj.ton("#F2C14E", 0.18),
                                     "rotate": {"unit": 5, "value": float(i * 180 / L_RAYONS)}}))


def regles_items(t, s, declencheur, a_, b_, v_, delais, duree=None):
    """l'arrivée des informations, une règle par style (a_ = opacité, b_ = mouvement, v_ = cache qui recule)"""
    anim = PACKS[s]["anim"]
    for n, d in enumerate(delais):
        A, B, V = f"{a_}{n}", f"{b_}{n}", f"{v_}{n}"
        if anim == "ecrit":   # N, O : la ligne se découvre de gauche à droite (un cache à la couleur du fond recule)
            R(t, [[(".", A)]], [(cj.ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", 0.01, d, "linear"))
            R(t, [[(".", declencheur), (".", A)]], [(cj.ID_OPACITY, "", [(2, 1.0)])])
            idw = cj.sm.PROPRIETES["width"][0]
            R(t, [[(".", V)]], [(idw, "", [pc(100)])] + tr("width", duree or PACKS[s]["duree"], d, "linear"))
            R(t, [[(".", declencheur), (".", V)]], [(idw, "", [pc(0)])])
            continue
        duree_o = {"tampon": 0.12, "jaillit": 0.15, "leve": 0.20, "retourne": 0.01, "fondu": 0.15}[anim]
        R(t, [[(".", A)]], [(cj.ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", duree_o, d,
                                                                  "ease-out" if anim == "leve" else "linear"))
        R(t, [[(".", declencheur), (".", A)]], [(cj.ID_OPACITY, "", [(2, 1.0)])])
        if anim in ("tampon", "jaillit"):
            e = ECHELLE_TAMPON if anim == "tampon" else 1.6
            R(t, [[(".", B)]], [(cj.ID_SCALE, "", [(2, e), (2, e)])] + tr("scale", 0.30 if anim == "tampon" else 0.35,
                                                                          d, "ease-out-back"))
            R(t, [[(".", declencheur), (".", B)]], [(cj.ID_SCALE, "", [(2, 1.0), (2, 1.0)])])
        elif anim == "leve":
            R(t, [[(".", B)]], [(cj.ID_TRANSLATE, "", [px(0), px(6)])] + tr("translate", 0.20, d, "ease-out"))
            R(t, [[(".", declencheur), (".", B)]], [(cj.ID_TRANSLATE, "", [px(0), px(0)])])
        elif anim == "retourne":
            R(t, [[(".", B)]], [(cj.ID_SCALE, "", [(2, 0.0), (2, 1.0)])] + tr("scale", 0.35, d, "ease-out"))
            R(t, [[(".", declencheur), (".", B)]], [(cj.ID_SCALE, "", [(2, 1.0), (2, 1.0)])])


def delais_ecran1(s):
    """les 7 coups de l'écran 1, dans l'ordre de lecture (gauche : niveau, perso, médias ; droite : potentiel, court,
    long, bouton) ; I : v16, tout à 0 (le cache du scan découvre)"""
    P_ = PACKS[s]
    if P_["anim"] == "fondu":   # v16 : sous le cache du scan, tout est déjà là ; c'est le cache qui découvre
        return [0.0] * 7
    return [P_["debut"] + n * P_["pas"] for n in range(6)] + [P_["debut"] + 6 * P_["pas"] + 0.15]


def delais_ecran2(s):
    """v12 : écran 2 (Pour, Contre, « Dévoiler la carte entière ») ; I : quand la 2e barre de lecture passe (Pour et
    Contre côte à côte, à la même hauteur ; le bouton en bas) ; v16 : tout à 0 (le cache découvre)"""
    if PACKS[s]["anim"] == "fondu":   # v16 : le cache de l'écran 2 découvre
        return [0.0] * 3
    return DELAIS_P2


def regles_entree(t, s):
    """l'entrée du pack (classes e2 et e3 de f2 et f3 ; f1 : l'opacité, commune), au déclencheur CL_OUVERT"""
    o = CL_OUVERT
    e2, e3 = cl(s, "e2"), cl(s, "e3")
    if s == "j":   # le dossier d'avant : sort du bas en se redressant
        R(t, [[(".", e2)]], [(cj.ID_TRANSLATE, "", [px(0), px(150)])] + tr("translate", 0.60, 0, "ease-out"))
        R(t, [[(".", o), (".", e2)]], [(cj.ID_TRANSLATE, "", [px(0), px(0)])])
        R(t, [[(".", e3)]], [(ID_ROTATE, "", [(3, {"unit": 5, "value": -4.0})])] + tr("rotate", 0.60, 0,
                                                                                       "ease-out-back"))
        R(t, [[(".", o), (".", e3)]], [(ID_ROTATE, "", [(3, {"unit": 5, "value": 0.0})])])
    elif s == "a":   # se retourne comme une carte
        R(t, [[(".", e2)]], [(cj.ID_SCALE, "", [(2, 0.0), (2, 1.0)])] + tr("scale", 0.50, 0, "ease-out"))
        R(t, [[(".", o), (".", e2)]], [(cj.ID_SCALE, "", [(2, 1.0), (2, 1.0)])])
    elif s == "l":   # jaillit petit, grandit en tournant ; rayons derrière
        R(t, [[(".", e2)]], [(cj.ID_SCALE, "", [(2, 0.3), (2, 0.3)])] + tr("scale", 0.70, 0, "ease-out-back"))
        R(t, [[(".", o), (".", e2)]], [(cj.ID_SCALE, "", [(2, 1.0), (2, 1.0)])])
        R(t, [[(".", e3)]], [(ID_ROTATE, "", [(3, {"unit": 5, "value": -8.0})])] + tr("rotate", 0.70, 0,
                                                                                       "ease-out-back"))
        R(t, [[(".", o), (".", e3)]], [(ID_ROTATE, "", [(3, {"unit": 5, "value": 0.0})])])
        ro, ry = cl("l", "rayons-o"), cl("l", "rayons")
        R(t, [[(".", ro)]], [(cj.ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", 0.60, 0, "linear"))
        R(t, [[(".", o), (".", ro)]], [(cj.ID_OPACITY, "", [(2, 1.0)])])
        R(t, [[(".", ry)]], [(ID_ROTATE, "", [(3, {"unit": 5, "value": 0.0})])] + tr("rotate", 3.0, 0, "ease-out"))
        R(t, [[(".", o), (".", ry)]], [(ID_ROTATE, "", [(3, {"unit": 5, "value": 60.0})])])
    elif s == "n":   # l'ardoise se pose
        R(t, [[(".", e2)]], [(cj.ID_SCALE, "", [(2, 0.97), (2, 0.97)])] + tr("scale", 0.40, 0, "ease-out"))
        R(t, [[(".", o), (".", e2)]], [(cj.ID_SCALE, "", [(2, 1.0), (2, 1.0)])])
    elif s == "q":   # les portes du casier s'écartent
        for c, x in ((cl("q", "porte-g"), -102.0), (cl("q", "porte-d"), 102.0)):
            R(t, [[(".", c)]], [(cj.ID_TRANSLATE, "", [px(0), px(0)])] + tr("translate", 0.70, 0.35, "ease-in-out"))
            R(t, [[(".", o), (".", c)]], [(cj.ID_TRANSLATE, "", [pc(x), px(0)])])
    elif s == "i":   # la barre de lecture descend, puis s'efface
        so, sb = cl("i", "scan-o"), cl("i", "scan")
        idt = cj.sm.PROPRIETES["top"][0]
        R(t, [[(".", sb)]], [(idt, "", [pc(0)])] + tr("top", SCAN["duree"], SCAN["debut"], "linear"))
        R(t, [[(".", o), (".", sb)]], [(idt, "", [pc(100)])])
        R(t, [[(".", so)]], [(cj.ID_OPACITY, "", [(2, 1.0)])] + tr("opacity", 0.30, SCAN["debut"] + SCAN["duree"],
                                                                   "linear"))
        R(t, [[(".", o), (".", so)]], [(cj.ID_OPACITY, "", [(2, 0.0)])])
        # v16 : le cache de l'écran 1 recule avec la barre (même durée, même délai, même courbe)
        for c, y in ((cl("i", "voile"), 100.0), (cl("i", "voile-in"), -100.0)):
            R(t, [[(".", c)]], [(cj.ID_TRANSLATE, "", [px(0), pc(0)])] + tr("translate", SCAN["duree"], SCAN["debut"],
                                                                            "linear"))
            R(t, [[(".", o), (".", c)]], [(cj.ID_TRANSLATE, "", [px(0), pc(y)])])
        # v12 : la 2e barre, à l'écran du rapport (déclencheur CL_PHASE2) : apparaît, descend, s'efface
        p2 = CL_PHASE2
        sa, so2, sb2 = cl("i", "scan2-a"), cl("i", "scan2-o"), cl("i", "scan2")
        R(t, [[(".", sa)]], [(cj.ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", 0.01, SCAN2["debut"], "linear"))
        R(t, [[(".", p2), (".", sa)]], [(cj.ID_OPACITY, "", [(2, 1.0)])])
        R(t, [[(".", sb2)]], [(idt, "", [pc(0)])] + tr("top", SCAN2["duree"], SCAN2["debut"], "linear"))
        R(t, [[(".", p2), (".", sb2)]], [(idt, "", [pc(100)])])
        R(t, [[(".", so2)]], [(cj.ID_OPACITY, "", [(2, 1.0)])] + tr("opacity", 0.30, SCAN2["debut"] + SCAN2["duree"],
                                                                    "linear"))
        R(t, [[(".", p2), (".", so2)]], [(cj.ID_OPACITY, "", [(2, 0.0)])])
        # v16 : le cache de l'écran 2 (invisible à l'écran 1), qui recule avec la 2e barre
        a2 = cl("i", "voile2-a")
        R(t, [[(".", a2)]], [(cj.ID_OPACITY, "", [(2, 0.0)])])
        R(t, [[(".", p2), (".", a2)]], [(cj.ID_OPACITY, "", [(2, 1.0)])])
        for c, y in ((cl("i", "voile2"), 100.0), (cl("i", "voile2-in"), -100.0)):
            R(t, [[(".", c)]], [(cj.ID_TRANSLATE, "", [px(0), pc(0)])] + tr("translate", SCAN2["duree"],
                                                                            SCAN2["debut"], "linear"))
            R(t, [[(".", p2), (".", c)]], [(cj.ID_TRANSLATE, "", [px(0), pc(y)])])


def tampon_groupe(t, src, k, tete, s, pal):
    """le tampon du groupe dans l'en-tête, juste après le nom : un SIVisible par groupe ; sa forme suit le style"""
    tvi, rvi = src["cat_visible"]
    for i, g in enumerate(pal):
        gs = cj.visible(t, tvi, rvi, tete, f"{P_GROUPE}{i}")
        cj.sans_clic(t, gs)
        t.styles.style(t, gs, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})
        tourne = s in ("j", "a", "i", "l")
        tp = cj.boite(t, src, gs, {"height": 50, "align-items": "center", "flex-shrink": 0, "margin-left": ECART_TAMPON,
                                   **(cj.tourne(-6) if tourne else {})})
        c, teinte = g["couleur"], None
        if s in ("j", "a"):
            mot_css, coul_mot = {**cj.cadre(c, 2, 2)}, c
        elif s == "d":
            mot_css, coul_mot = {"background-color": cj.ton(c, 0.18), **cj.rayons(14)}, c
        elif s == "i":
            mot_css, coul_mot = {"background-color": cj.rgba("#121622"), **cj.rayons(5)}, c
        elif s == "l":
            mot_css, coul_mot, teinte = {"background-color": cj.rgba("#3A2A0F"), **cj.rayons(14)}, "#FFE39A", "#3A2A0F"
        elif s == "n":
            mot_css, coul_mot = {"border-bottom-width": 3, "border-bottom-color": cj.rgba(c)}, "#F2F2E8"
        elif s == "o":
            mot_css, coul_mot = {"border-top-width": 2, "border-bottom-width": 2, "border-top-color": cj.rgba(c),
                                 "border-bottom-color": cj.rgba(c)}, c
        else:   # q
            mot_css, coul_mot = {"background-color": cj.rgba("#E9ECEF"), **cj.cadre("#3A2A0F", 2, 4)}, "#1B1E26"
        mot = cj.boite(t, src, tp, {**mot_css, "padding-left": 8, "padding-right": 8, "flex-shrink": 0})
        cj.texte(k, mot, g["mot"], {"color": cj.rgba(coul_mot), "font-size": 20 if s != "d" else 18,
                                    "-unity-font-style": "bold"})
        cj.etoiles_dos(k, tp, g, 13, {"top": 36}, teinte)


def photo_pack(t, src, k, tete, s):
    """la photo de l'en-tête : polaroid (J, Q), rond cerclé (D, A, I, L, N), arche (O)"""
    if s in ("j", "q"):
        coul_, angle = (PAPIER_POL, -3) if s == "j" else ("#FFFFFF", 2)
        pol = cj.boite(t, src, tete, {"width": 64, "height": 74, "background-color": cj.rgba(coul_),
                                      "flex-shrink": 0, **cj.tourne(angle)})
        cj.photo(k, pol, 56, 0, {"position": "absolute", "left": 4, "top": 4})
    elif s == "o":
        cj.arche_photo(k, tete, 60, 78, "#D9B35B", "#0E1B2A", {})
    else:
        taille, coul_, ep = {"d": (66, "#9AA3AD", 2), "a": (70, "#8A8CFF", 3), "i": (70, "#FFFFFF", 3),
                             "l": (70, "#FFFFFF", 4), "n": (66, "#E6E8E0", 3)}[s]
        cj.anneau_photo(k, tete, taille, coul_, ep, {})


def caches_scan(t, src, f3, P_):
    """v16, I (Kinito : « faire apparaître les infos seulement au passage du scan ») : un cache à la matière du
    dossier (fond_holo, à l'identique) recule avec la barre de lecture. Deux couches : la boîte qui coupe (overflow
    hidden) descend de 0 à 100 % de sa hauteur, sa matière remonte d'autant : la matière reste en place, seul le bord
    haut du cache bouge. La barre (top de 0 à 100 % de la même boîte f3) et le cache (translate de 0 à 100 % de sa
    propre hauteur, celle de f3) vont donc au même endroit au même moment, à toutes les hauteurs de dossier.
    Écran 1 : tout le dossier (la bande et le cadre sont posés après) ; écran 2 : sous l'en-tête seulement (il reste
    affiché), dans une boîte qui commence à haut + HAUT_TETE + MARGE_ZONE et qui n'apparaît qu'à l'écran 2"""
    c1 = cj.boite(t, src, f3, {**cj.PLEIN, "overflow": "hidden"}, [cl("i", "voile")])
    fond_holo(t, src, cj.boite(t, src, c1, cj.PLEIN, [cl("i", "voile-in")]))
    y = P_["haut"] + HAUT_TETE + MARGE_ZONE
    a2 = cj.boite(t, src, f3, cj.ab(left=0, right=0, top=y, bottom=0, overflow="hidden"), [cl("i", "voile2-a")])
    c2 = cj.boite(t, src, a2, cj.ab(left=0, right=0, top=-y, bottom=0, overflow="hidden"), [cl("i", "voile2")])
    fond_holo(t, src, cj.boite(t, src, c2, cj.PLEIN, [cl("i", "voile2-in")]))


def dossier(t, src, k, x, parent, s):
    """le pack du style <s> : f1 (opacité) > f2, f3 (entrée du style) > matière, contenu, portes (Q), barre (I)"""
    P_ = PACKS[s]
    pal = cj.STYLES[s]["pal"]
    encre, gris = P_["encre"], P_["gris"]
    a1, b1, v1 = cl(s, "a"), cl(s, "b"), cl(s, "v")    # écran 1
    a2, b2, v2 = cl(s, "c"), cl(s, "d"), cl(s, "w")    # écran 2
    if s == "l":
        rayons_sachet(t, src, parent)
    f1 = cj.boite(t, src, parent, {"flex-shrink": 0}, [CL_F1], clic=True)
    f2 = cj.boite(t, src, f1, {"align-self": "stretch", "flex-shrink": 0}, [cl(s, "e2")], clic=True)
    f3 = cj.boite(t, src, f2, {"align-self": "stretch", "flex-shrink": 0}, [cl(s, "e3")], clic=True)
    fond_pack(t, src, k, f3, s, pal, partie="fond" if s == "i" else "tout")
    cont = cj.boite(t, src, f3, {"flex-direction": "column", "flex-shrink": 0, "margin-left": P_.get("gauche", P_["cote"]),
                                 "margin-top": P_["haut"], "margin-right": P_["cote"], "margin-bottom": P_["bas"]},
                    clic=True)
    tete = cj.boite(t, src, cont, {"flex-direction": "row", "align-items": "center", "height": HAUT_TETE, "padding-left": 16,
                                   "padding-right": 16, "flex-shrink": 0})
    photo_pack(t, src, k, tete, s)
    ident = cj.boite(t, src, tete, {"flex-direction": "column", "align-items": "flex-start", "margin-left": 16,
                                    "max-width": 240, "flex-shrink": 0})
    cj.noms(k, ident, encre, {"align-items": "flex-start", "align-self": "flex-start"})
    cj.poste(k, ident, gris, {"margin-top": 4}, taille=13)
    tr_, rr_ = src["remap"]

    def titre(parent_, s_txt, css=None):
        cj.texte(k, parent_, s_txt, {"color": cj.rgba(gris), "font-size": 11, "-unity-font-style": "bold",
                                     **(css or {})})

    te, blocs = x["etoiles"]

    def etoiles(parent_, bloc, css=None):
        zr = cj.remap(t, tr_, rr_, parent_, [("report", RAPPORT, x["type_rapport"])],
                      {"flex-direction": "row", "align-items": "center", "flex-shrink": 0, **(css or {})})
        e = cj.entier(t, te, bloc, zr)
        cj.sans_clic(t, e)
        t.styles.style(t, e, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})
        return zr

    zt = cj.remap(t, tr_, rr_, tete, [("team", EQUIPE_HUMAIN, cj.TYPE_EQUIPE)],
                  {"flex-direction": "row", "align-items": "center", "justify-content": "center", "flex-grow": 1,
                   "flex-shrink": 1, "min-width": 0, "margin-left": ECART_NOM_ETOILES, "align-self": "center"})
    t.elem(zt)["m_Classes"] = [CL_ETOILES]
    for n, (quoi, bloc) in enumerate(((TEXTE_NIVEAU, blocs[0]), (TEXTE_POTENTIEL, blocs[1]))):
        rangee = cj.boite(t, src, zt, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0,
                                       **({"margin-left": ECART_LIGNE2} if n else {})})
        titre(rangee, quoi, {"margin-right": ECART_ETIQUETTE, "flex-shrink": 0})
        etoiles(rangee, bloc)
    tampon_groupe(t, src, k, tete, s, pal)
    zone = cj.remap(t, tr_, rr_, cont, [("team", EQUIPE_HUMAIN, cj.TYPE_EQUIPE)],
                    {"flex-direction": "column", "align-self": "stretch", "flex-shrink": 0, "margin-top": MARGE_ZONE})

    def colonnes(parent_, egales=True):
        rang = cj.boite(t, src, parent_, {"flex-direction": "row", "align-items": "flex-start", "align-self": "stretch",
                                          "flex-shrink": 0})
        if egales:
            return [cj.boite(t, src, rang, {"flex-direction": "column", "flex-grow": 1, "flex-basis": 0,
                                            "min-width": 0, "flex-shrink": 1, "margin-left": 28 if n else 0})
                    for n in range(2)]
        return [cj.boite(t, src, rang, {"flex-direction": "column", "flex-grow": 0, "flex-shrink": 1, "min-width": 0,
                                        "max-width": COL2_MAX if n else COL1_MAX, "margin-left": ECART_COL1 if n else 0})
                for n in range(2)]

    def item(col, n, a_, b_, css, clic=False):
        return tampon(t, src, col, n, a_, b_, css, clic)

    def fin_item(b, n, v_):
        """N, O : le cache à la couleur du fond, par-dessus la ligne, qui recule de gauche à droite"""
        if P_["anim"] == "ecrit":
            cj.boite(t, src, b, cj.ab(right=0, top=0, bottom=0, **{"background-color": cj.rgba(P_["cache"])}),
                     [f"{v_}{n}"])

    # écran 1 : niveau, personnalité, médias | potentiel, court, long terme, « Passer au rapport »
    p1 = cj.boite(t, src, zone, {"flex-direction": "column", "align-self": "stretch", "flex-shrink": 0,
                                 "padding-left": 16, "padding-right": 16, "overflow": "hidden"}, [CL_P1])
    gauche, droite = colonnes(p1, egales=False)

    def ligne_etoiles(col, n, quoi, bloc):
        b = item(col, n, a1, b1, {"align-self": "stretch", "margin-top": 6})
        titre(b, quoi)
        etoiles(b, bloc, {"align-self": "flex-start", "margin-top": 2})
        fin_item(b, n, v1)

    ligne_etoiles(gauche, 0, TEXTE_NIVEAU, blocs[0])
    for n, (quoi, chemin) in enumerate(((TEXTE_PERSO, "person.Personality"), (TEXTE_MEDIAS, "person.MediaHandling"))):
        b = item(gauche, 1 + n, a1, b1, {"align-self": "stretch", "margin-top": 14})
        titre(b, quoi)
        cj.ligne_texte(k, b, chemin, encre, 18, {"-unity-text-align": "middle-left", "align-self": "stretch",
                                                 "margin-top": 2})
        fin_item(b, 1 + n, v1)
    ligne_etoiles(droite, 3, TEXTE_POTENTIEL, blocs[1])
    for j, (cle, quoi, liste, nombre) in enumerate(LISTES_PROJETS):
        b = item(droite, 4 + j, a1, b1, {"align-self": "stretch", "margin-top": 14})
        titre(b, quoi)

        def projet(dans, i, var):
            r = cj.texte_lie(t, k.s0, k.texte, dans, f"{var}.Name", ["body-sm-strong"],
                             {"color": cj.rgba(encre), "font-size": 16, "white-space": "normal",
                              "-unity-text-align": "upper-left", "align-self": "stretch", "flex-shrink": 0,
                              "margin-top": 2 if i == 0 else 5})
            cj.sans_clic(t, r)
        lignes(t, x, b, [f"{V_PROJET}{cle}{i}" for i in range(PROJETS_MAX)], liste, nombre, True, projet)
        fin_item(b, 4 + j, v1)
    css_b = css_bouton(s)
    texte_b = P_["btn"]["texte"]
    w1 = item(droite, 6, a1, b1, {"align-self": "flex-start", "margin-top": 16}, clic=True)
    t.elem(t.parent[w1])["m_Classes"].append(CL_BOUTON1)
    b1_ = bouton(t, src, w1, [cj.copier("const.True", V_PHASE2)], css_b, nom(f"{s}-passer"))
    texte_bouton(t, src, b1_, TEXTE_PASSER, texte_b, 15)
    fin_item(w1, 6, v1)
    # écran 2 : Pour | Contre (la pastille d'Alex en face de chaque phrase)
    p2 = cj.boite(t, src, zone, {"flex-direction": "column", "align-self": "stretch", "flex-shrink": 0,
                                 "padding-left": 16, "padding-right": 16, "overflow": "hidden"}, [CL_P2])
    rm = cj.remap(t, tr_, rr_, p2, [("report", RAPPORT, x["type_rapport"])],
                  {"flex-direction": "column", "align-self": "stretch", "flex-shrink": 0})
    cols = colonnes(rm)
    for j, (cle, quoi, liste, nombre, signe) in enumerate(LISTES_PC):
        b = item(cols[j], j, a2, b2, {"align-self": "stretch", "margin-top": 6})
        titre(b, quoi)
        corps = cj.boite(t, src, b, {"flex-direction": "row", "align-items": "flex-start", "align-self": "stretch",
                                     "flex-shrink": 0, "margin-top": 4})
        if x["pastille"]:
            pastilles(t, x, corps, liste)

        def point(dans, i, var, signe=signe):
            t.styles.style(t, dans, {"flex-direction": "row", "align-items": "center", "height": PAS_PC,
                                     "min-height": PAS_PC, "max-height": PAS_PC})
            if not x["pastille"]:   # sans la pastille d'Alex : un signe (jamais la couleur seule)
                cj.texte(k, dans, signe, {"color": cj.rgba(encre), "font-size": 18, "-unity-font-style": "bold",
                                          "width": 18, "flex-shrink": 0, "margin-right": 6})
            r = cj.texte_lie(t, k.s0, k.texte, dans, f"{var}.ProConsLongString", ["body-sm-strong", CLASSE_COUPE],
                             {"color": cj.rgba(encre), "font-size": TAILLE_PHRASE, "white-space": "nowrap",
                              "overflow": "hidden", "-unity-text-align": "middle-left", "flex-grow": 1,
                              "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "height": PAS_PC})
            sdr = t.sd(r)
            sdr["DisplayTooltipWhenElided"], sdr["DisplayTooltipWhenElided_UxmlAttributeFlags"] = 1, 1
            sdr["pickingMode"], sdr["pickingMode_UxmlAttributeFlags"] = 0, 1   # PickingMode.Position, écrit
        lignes(t, x, corps, [f"{V_PC}{cle}{i}" for i in range(PC_MAX)], liste, nombre, False, point)
        vide = si_vide(t, x, b, nombre)
        cj.texte(k, vide, TEXTE_RIEN, {"color": cj.rgba(encre), "font-size": 15, "margin-top": 2})
        fin_item(b, j, v2)
    pied = cj.boite(t, src, cont, {"flex-direction": "row", "justify-content": "flex-end", "height": 38,
                                   "flex-shrink": 0, "padding-right": 16, "margin-top": 14}, [CL_PIED], clic=True)
    w2 = item(pied, 2, a2, b2, {"align-self": "stretch"}, clic=True)
    t.elem(t.parent[w2])["m_Classes"].append(CL_BOUTON2)
    b2_ = bouton(t, src, w2, [cj.copier("const.True", V_RIDEAU),
                              ouvrir_panneau(GUID_FICHE, [("player", "person"), ("team", "team")]),
                              fermer_panneau(GUID_PANNEAU)], css_b, nom(f"{s}-devoiler"))
    texte_bouton(t, src, b2_, TEXTE_DEVOILER, texte_b, 15)
    fin_item(w2, 2, v2)
    # par-dessus le contenu : les portes du casier (Q), la barre de lecture (I)
    if s == "q":
        portes_casier(t, src, k, f3, pal)
    if s == "i":
        caches_scan(t, src, f3, P_)                      # v16 : les infos n'apparaissent qu'au passage de la barre
        fond_pack(t, src, k, f3, s, pal, partie="dessus")   # le cadre et la bande, par-dessus le cache
        so = cj.boite(t, src, f3, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(16)}, [cl("i", "scan-o")])
        barre = cj.boite(t, src, so, cj.ab(left=0, right=0, height=8), [cl("i", "scan")])
        cj.boite(t, src, barre, cj.ab(left=0, right=0, top=0, height=8, **{"background-color": cj.ton("#7AE7FF", 0.35)}))
        cj.boite(t, src, barre, cj.ab(left=0, right=0, top=2, height=3, **{"background-color": cj.rgba("#FFFFFF")}))
        # v12 : la 2e barre, pour l'écran du rapport : cachée à l'écran 1 (elle apparaît, descend, puis s'efface)
        sa = cj.boite(t, src, f3, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(16)}, [cl("i", "scan2-a")])
        so2 = cj.boite(t, src, sa, cj.PLEIN, [cl("i", "scan2-o")])
        barre2 = cj.boite(t, src, so2, cj.ab(left=0, right=0, height=8), [cl("i", "scan2")])
        cj.boite(t, src, barre2, cj.ab(left=0, right=0, top=0, height=8,
                                       **{"background-color": cj.ton("#7AE7FF", 0.35)}))
        cj.boite(t, src, barre2, cj.ab(left=0, right=0, top=2, height=3, **{"background-color": cj.rgba("#FFFFFF")}))
    # les règles du style
    regles_entree(t, s)
    regles_items(t, s, CL_OUVERT, a1, b1, v1, delais_ecran1(s), P_.get("duree1"))
    regles_items(t, s, CL_PHASE2, a2, b2, v2, delais_ecran2(s))
    croix_bandeau(t, src, f3, s, pal)   # v13 ; v14 : dans le bandeau



def croix(t, src, parent, evenements, css=None, taille=26, texte="#FFFFFF", dessin=None):
    """v13 (Kinito : « une petite croix en haut à droite pour sortir ») : un bouton « × » (le SIButton de nos
    pastilles), en absolu ; ses événements : fermer la fenêtre, ou enlever le cache de la fiche ; v14 : son dessin
    (défaut : le rond sombre de la fiche) et la couleur du « × » (#rrggbb ou (r, g, b, a))"""
    if dessin is None:
        dessin = {"background-color": cj.ton("#0A0C12", 0.65), **cj.cadre("#FFFFFF", 2, taille / 2)}
    b = bouton(t, src, parent, evenements, {"position": "absolute", "width": taille, "height": taille,
                                            "align-items": "center", "justify-content": "center",
                                            **dessin, **(css or {})})
    ttx, rtx = src["cat_texte"]
    r = cj.texte_fixe(t, ttx, rtx, b, "×", ["body-sm-strong"],
                      {"color": texte if isinstance(texte, tuple) else cj.rgba(texte),
                       "font-size": round(taille * 0.62), "white-space": "nowrap"})
    cj.sans_clic(t, r)
    return b


def dessin_croix(s):
    """v14 (Kinito : « une croix qui entre bien dans chaque design ») : le bouton du style en petit (fond, contour,
    coins, couleur du texte : ceux de « Passer au rapport » / « Ouvrir le dossier ») ; J : à part (croix_bandeau)"""
    b = PACKS[s]["btn"]
    rayon = min(b["rayon"], TAILLE_CROIX / 2)
    d = cj.rayons(rayon)
    if b.get("fond"):
        d["background-color"] = cj.rgba(b["fond"])
    if b.get("bord"):
        d.update(cj.cadre(b["bord"][0], min(b["bord"][1], 2), rayon))
    return d, b["texte"]


def croix_bandeau(t, src, f3, s, pal, ev=None):
    """v14 (Kinito : « la croix doit se trouver dans le bandeau et centrée ») : à droite du bandeau du dossier, centrée
    en hauteur sur lui ; posée en dernier dans le pack (par-dessus tout, portes de Q comprises) ; J : la bande est à
    la couleur du groupe et son texte à celle de la feuille : la croix aussi (contour et « × » couleur feuille), un
    SIVisible par groupe comme la bande"""
    haut, droite = BANDE[s]
    pos = {"top": haut + (HAUT_BANDE - TAILLE_CROIX) / 2, "right": droite}
    ev = ev or [fermer_panneau(GUID_PANNEAU)]   # v15 : sur la fiche, le cache s'en va
    if s != "j":
        d, coul = dessin_croix(s)
        return [croix(t, src, f3, ev, pos, TAILLE_CROIX, coul, d)]
    tvi, rvi = src["cat_visible"]
    out = []
    for i, g in enumerate(pal):
        gv = cj.visible(t, tvi, rvi, f3, f"{P_GROUPE}{i}")
        cj.sans_clic(t, gv)
        t.styles.style(t, gv, cj.PLEIN)
        p = cj.j_papier(g)
        out.append(croix(t, src, gv, ev, pos, TAILLE_CROIX, p, cj.cadre(p, 2, TAILLE_CROIX / 2)))
    return out


def ouverture_style(t, src, k, x, parent, s):
    """v13 : l'ouverture du style <s> : la carte (sa face et son dos, dessinés par 26.19) arrive en grand au centre,
    s'ouvre à la façon du style (maquette v2), puis « Ouvrir le dossier » ; la croix ferme la fenêtre"""
    W, H = cj.CARTE
    coin = cj.STYLES[s].get("rayon", 10)
    zr = cj.boite(t, src, parent, {"flex-direction": "column", "align-items": "center", "flex-shrink": 0})
    # les repères de groupe : la carte lit uipickercouleurcategorie<i> (par_groupe de 26.19, nom lu à l'appel), la
    # fenêtre a kinitogroupe<i> : on les lui fait lire directement, le temps de dessiner (comme le tampon du dossier,
    # vu en jeu ; plutôt qu'un BindingRemapper à type vide, jamais vu en jeu)
    ancien = cj.MARQUE_ALEX
    cj.MARQUE_ALEX = P_GROUPE
    try:
        return dessin_ouverture(t, src, k, zr, s, W, H, coin)
    finally:
        cj.MARQUE_ALEX = ancien


def dessin_ouverture(t, src, k, zr, s, W, H, coin):
    """v13 : le dessin de l'ouverture (voir ouverture_style)"""
    pal = cj.STYLES[s]["pal"]
    zo = cj.boite(t, src, zr, {"width": W, "height": H, "flex-shrink": 0}, [cl(s, "zo")], clic=True)   # opacité
    scene = cj.boite(t, src, zo, cj.PLEIN, [cl(s, "z")], clic=True)                                   # échelle
    corps = cj.boite(t, src, scene, {**cj.PLEIN, "overflow": "hidden", **cj.rayons(coin)})
    fond = {"background-color": cj.rgba(cj.FOND_DOS)}

    def dos_entier(parent_, css):
        d = cj.boite(t, src, parent_, {**cj.ab(width=W, height=H), **fond, **css})
        m = cj.STYLES[s]["dos"](k, d, pal)
        return d, m

    face = cj.boite(t, src, corps, {**cj.PLEIN, "flex-direction": "column", "align-items": "center"}, [cl(s, "if")])
    msgs = cj.STYLES[s]["face"](k, face, pal) or []
    if s in ("d", "a", "i", "l"):
        d, m = dos_entier(corps, {"left": 0, "top": 0})
        msgs += m or []
        t.elem(d)["m_Classes"] = [cl(s, "id")]
        if s == "i":
            cj.boite(t, src, d, cj.ab(left=0, right=0, top=-4, height=4, **{"background-color": cj.rgba("#FFFFFF")}))
        if s == "a":   # l'éclair : monte (dedans), puis s'efface (dehors)
            e1 = cj.boite(t, src, corps, cj.PLEIN, [cl(s, "ie-o")])
            cj.boite(t, src, e1, {**cj.PLEIN, "background-color": cj.rgba("#FFF6D6")}, [cl(s, "ie")])
        if s == "l":   # le haut du sachet, qui se déchire et s'envole
            so = cj.boite(t, src, corps, cj.ab(left=0, right=0, top=0, height=34), [cl(s, "is-o")])
            cj.boite(t, src, so, {**cj.PLEIN, "background-color": cj.rgba("#FFE39A"),
                                  "border-bottom-width": 3, "border-bottom-color": cj.rgba("#3A2A0F")}, [cl(s, "is")])
    elif s == "j":   # le rabat du dossier : la chemise se replie vers le haut (sa hauteur va à 0, coupée)
        w = cj.boite(t, src, corps, cj.ab(left=0, right=0, top=0, overflow="hidden"), [cl(s, "ir")])
        d, m = dos_entier(w, {"left": 0, "top": 0})
        msgs += m or []
    elif s == "n":   # l'ardoise : se découvre de gauche à droite (sa largeur va à 0, calée à droite), trait de craie
        w = cj.boite(t, src, corps, cj.ab(right=0, top=0, bottom=0, overflow="hidden"), [cl(s, "ir")])
        d, m = dos_entier(w, {"right": 0, "top": 0})
        msgs += m or []
        cj.boite(t, src, w, cj.ab(left=0, top=0, bottom=0, width=3, **{"background-color": cj.rgba("#F2F2E8")}))
    else:   # o, q : les deux moitiés du dos s'écartent
        for cote, cle in (("left", "ip-g"), ("right", "ip-d")):
            w = cj.boite(t, src, corps, cj.ab(**{cote: 0}, top=0, bottom=0, width=W / 2, overflow="hidden"),
                         [cl(s, cle)])
            d, m = dos_entier(w, {"left": 0 if cote == "left" else -W / 2, "top": 0})
            msgs += m or []
    cj.boite(t, src, scene, cj.PLEIN, clic=True)   # la grande carte ne prend aucun clic (son nom, son contrat)
    # v14 (Kinito : « la croix des cartes dévoilées, à côté d'« Ouvrir le dossier », dans le même design »)
    wb = cj.boite(t, src, zr, {"margin-top": round((H * ZOOM - H) / 2) + 26, "flex-shrink": 0, "flex-direction": "row",
                               "align-items": "center"}, [cl(s, "ib")], clic=True)
    b = bouton(t, src, wb, [cj.copier("const.True", V_VU), cj.copier("const.True", V_OUVERT)],
               {**css_bouton(s), "height": 34}, nom(f"{s}-ouvrir"))
    texte_bouton(t, src, b, TEXTE_OUVRIR, PACKS[s]["btn"]["texte"], 15)
    bx = bouton(t, src, wb, [fermer_panneau(GUID_PANNEAU)],
                {**css_bouton(s), "height": 34, "width": 34, "padding-left": 0, "padding-right": 0, "margin-left": 10},
                nom(f"{s}-fermer"))
    texte_bouton(t, src, bx, "×", PACKS[s]["btn"]["texte"], 21)
    return [m_ for m_ in msgs if m_]


def regles_ouverture(t, s):
    """v13 : l'ouverture du style <s>, déclenchée par CL_INTRO_GO (posée 0,05 s après l'arrivée) ; une propriété animée
    par couche"""
    g = CL_INTRO_GO

    def anim(classe, base, fin, prop, duree, delai_, courbe):
        R(t, [[(".", classe)]], [base] + tr(prop, duree, delai_, courbe))
        R(t, [[(".", g), (".", classe)]], [fin])

    op = lambda v: (cj.ID_OPACITY, "", [(2, float(v))])   # noqa: E731
    ech = lambda x_, y_: (cj.ID_SCALE, "", [(2, float(x_)), (2, float(y_))])   # noqa: E731
    gl = lambda x_, y_: (cj.ID_TRANSLATE, "", [x_, y_])   # noqa: E731
    D, F = DEBUT_OUV, FIN_OUV   # v14 : le dos de la grande se ferme quand celui de la petite, elle est découverte avec elle
    A = cj.ANIM
    anim(cl(s, "zo"), op(0), op(1), "opacity", 0.15, 0, "linear")
    anim(cl(s, "z"), ech(0.25, 0.25), ech(ZOOM, ZOOM), "scale", DUREE_ZOOM, 0, "ease-out")
    anim(cl(s, "ib"), op(0), op(1), "opacity", 0.30, APPARITION_BOUTONS, "linear")
    idw, idh = cj.sm.PROPRIETES["width"][0], cj.sm.PROPRIETES["height"][0]
    if s in ("d", "a"):   # se retourne comme la petite : le dos se ferme, la face s'ouvre (mêmes durées)
        anim(cl(s, "id"), ech(1, 1), ech(0, 1), "scale", A["fermer"], D, "ease-in")
        anim(cl(s, "if"), ech(0, 1), ech(1, 1), "scale", A["ouvrir"], A["ouvrir_a"] - 0.05, "ease-out")
        if s == "a":   # l'éclair de la petite (A3 : à 0,33 s)
            anim(cl(s, "ie"), op(0), op(0.9), "opacity", 0.08, A["eclair_a"] - 0.05, "linear")
            anim(cl(s, "ie-o"), op(1), op(0), "opacity", 0.40, A["eclair_a"] + 0.05, "linear")
    elif s == "j":
        R(t, [[(".", cl(s, "ir"))]], [(idh, "", [pc(100)])] + tr("height", F - D, D, "ease-in"))
        R(t, [[(".", g), (".", cl(s, "ir"))]], [(idh, "", [pc(0)])])
        anim(cl(s, "if"), ech(0.86, 0.86), ech(1, 1), "scale", 0.35, D + 0.15, "ease-out-back")
    elif s == "i":
        anim(cl(s, "id"), gl(px(0), px(0)), gl(px(0), pc(102)), "translate", F - D, D, "linear")
    elif s == "l":
        anim(cl(s, "is"), gl(px(0), px(0)), gl(px(40), px(-120)), "translate", 0.25, D, "ease-out")
        anim(cl(s, "is-o"), op(1), op(0), "opacity", 0.25, D, "linear")
        anim(cl(s, "id"), gl(px(0), px(0)), gl(px(0), pc(102)), "translate", F - D - 0.10, D + 0.10, "ease-in")
        anim(cl(s, "if"), ech(0.9, 0.9), ech(1, 1), "scale", 0.35, D + 0.15, "ease-out-back")
    elif s == "n":
        R(t, [[(".", cl(s, "ir"))]], [(idw, "", [pc(100)])] + tr("width", F - D, D, "linear"))
        R(t, [[(".", g), (".", cl(s, "ir"))]], [(idw, "", [pc(0)])])
    else:   # o, q
        anim(cl(s, "ip-g"), gl(px(0), px(0)), gl(pc(-102), px(0)), "translate", F - D, D, "ease-in-out")
        anim(cl(s, "ip-d"), gl(px(0), px(0)), gl(pc(102), px(0)), "translate", F - D, D, "ease-in-out")
        if s == "q":
            anim(cl(s, "if"), ech(0.9, 0.9), ech(1, 1), "scale", 0.35, D + 0.20, "ease-out-back")

def construire_fenetre(t, src, k, x):
    br = first(t, lambda r: typ(t, r) == "BindingRoot")
    fond = first(t, lambda r: t.name(r) == "Background")
    cadre_fm = first(t, lambda r: t.name(r) == "DialogFrame")
    if None in (br, fond, cadre_fm):
        return [f"{FENETRE} : BindingRoot, #Background ou #DialogFrame introuvable"]
    sd = t.sd(br)
    params = sd.setdefault("Parameters", [])
    for n, ty in PARAMS:
        if not any(p.get("name") == n for p in params):
            params.append({"m_serialisedType": 0, "name": n, "type": {"id": ty}, "isOptional": 1,
                           "defaultValue": {"m_kind": 0, "Path": {"m_path": ""}, "m_scopeValue": {"m_serializedData": ""}}})
    sd["Parameters_UxmlAttributeFlags"] = 1
    cj.attacher_feuille(t, fond)
    # la boîte de FM cachée quand c'est nous qui ouvrons (classe posée sur #Background si kinitorevelation est vrai)
    if cj.boite_style(t, src, fond, P_ON, CL_ON) is None:
        return [f"boîte de style de FM ({cj.SOURCE_STYLE}) : forme inattendue (introuvable)"]
    R(t, [[(".", CL_ON), ("#", "DialogFrame")]], [(cj.ID_DISPLAY, "", [(1, cj.MOT_AUCUN)])])
    tvi, rvi = src["cat_visible"]
    v = cj.visible(t, tvi, rvi, fond, P_ON, NOM_FENETRE)
    t.styles.style(t, v, cj.PLEIN)
    tc, rc = src["composant"]
    porteur = cj.seul(t, tc, rc, v, nom("porteur"))
    t.styles.style(t, porteur, cj.PLEIN)
    if not cj.variables(t, src, porteur, [(V_OUVERT, "Bool|0|"), (V_PHASE2, "Bool|0|"),
                                          (V_RIDEAU, f"Bool|0|{CLE_RIDEAU}"), (V_VU, "Bool|0|"),
                                          (V_INTRO_GO, "Bool|0|")]   # v13 : l'ouverture
                            + [(f"{V_GROUPE_FEN}{i}", f"Bool|0|{cle_groupe(i)}") for i in range(5)]):   # v15
        return [f"variable de FM ({cj.SOURCE_VARIABLES}) : forme inattendue (introuvable)"]
    # v15 : le groupe du jeune, gardé pour la fiche (elle ne le connaît pas) : seul le groupe passé à la fenêtre a son
    # SIVisible, et son délai écrit vrai pour lui, faux pour les autres
    for i in range(5):
        gv = cj.visible(t, tvi, rvi, porteur, f"{P_GROUPE}{i}")
        cj.sans_clic(t, gv)
        t.styles.style(t, gv, {"position": "absolute", "width": 0, "height": 0})
        delai(t, src, gv, DELAI_OUVERT, [cj.copier("const.True" if j == i else "const.False", f"{V_GROUPE_FEN}{j}")
                                         for j in range(5)])
    # v13 : ouverte par le nom (kinitorevintro faux, toujours passé : un SIVisible inversé sur une valeur nulle ne
    # montre rien), le dossier part tout de suite ; ouverte par le dos, c'est « Ouvrir le dossier » qui le fait partir
    sans_intro = cj.visible(t, tvi, rvi, porteur, P_INTRO, inverse=True)
    cj.sans_clic(t, sans_intro)
    t.styles.style(t, sans_intro, {"position": "absolute", "width": 0, "height": 0})
    delai(t, src, sans_intro, DELAI_OUVERT, [cj.copier("const.True", V_OUVERT)])
    for b, c in ((V_OUVERT, CL_OUVERT), (V_PHASE2, CL_PHASE2)):
        if cj.boite_style(t, src, porteur, b, c) is None:
            return [f"boîte de style de FM ({cj.SOURCE_STYLE}) : forme inattendue (introuvable)"]
    place = cj.boite(t, src, porteur, {**cj.PLEIN, "flex-direction": "column", "align-items": "center",
                                       "justify-content": "center"})
    # v11 : un pack par style de carte, chacun sous « style == k » (le style passé par la carte, choisi en jeu)
    sv, rvc = x["comparer"]
    bcmp = sv.sd(rvc)["Binding"]
    for n_style, s in enumerate(cj.ORDRE_STYLES, 1):
        vs = ni.new_visible(t, sv, rvc, place, None, nom(f"pack-{s}"),
                            ni.make_binding(bcmp, OP_EGAL, [cj.V_STYLE], n_style))
        cj.sans_clic(t, vs)
        t.styles.style(t, vs, {**cj.PLEIN, "flex-direction": "column", "align-items": "center",
                               "justify-content": "center"})
        dossier(t, src, k, x, vs, s)
    # v13 : l'ouverture (ouverte par le dos de la carte), par-dessus le dossier encore invisible, jusqu'à « Ouvrir le
    # dossier » ; un pack d'ouverture par style
    intro = cj.visible(t, tvi, rvi, porteur, P_INTRO, nom("ouverture"))
    cj.sans_clic(t, intro)
    t.styles.style(t, intro, cj.PLEIN)
    delai(t, src, intro, DELAI_OUVERT, [cj.copier("const.True", V_INTRO_GO)])
    pas_vu = cj.visible(t, tvi, rvi, intro, V_VU, inverse=True)
    cj.sans_clic(t, pas_vu)
    t.styles.style(t, pas_vu, cj.PLEIN)
    couche = cj.boite(t, src, pas_vu, {**cj.PLEIN, "flex-direction": "column", "align-items": "center",
                                       "justify-content": "center"}, clic=True)   # le dossier dessous ne prend rien
    if cj.boite_style(t, src, couche, V_INTRO_GO, CL_INTRO_GO) is None:
        return [f"boîte de style de FM ({cj.SOURCE_STYLE}) : forme inattendue (introuvable)"]
    for n_style, s in enumerate(cj.ORDRE_STYLES, 1):
        vo = ni.new_visible(t, sv, rvc, couche, None, nom(f"ouverture-{s}"),
                            ni.make_binding(bcmp, OP_EGAL, [cj.V_STYLE], n_style))
        cj.sans_clic(t, vo)
        t.styles.style(t, vo, {"flex-direction": "column", "align-items": "center", "flex-shrink": 0})
        m_ = ouverture_style(t, src, k, x, vo, s)
        if m_:
            return [f"ouverture {s} : {y_}" for y_ in m_]
        regles_ouverture(t, s)
    # l'animation commune : la fenêtre apparaît (f1)
    R(t, [[(".", CL_F1)]], [(cj.ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", 0.25, 0, "linear"))
    R(t, [[(".", CL_OUVERT), (".", CL_F1)]], [(cj.ID_OPACITY, "", [(2, 1.0)])])
    # les deux écrans (communs à tous les packs) : une seule phase prend de la place ; la cachée est à max-height 0 et
    # hors du flux ; écran 2 à la largeur de son en-tête (FEN_MIN au moins) ; étoiles de l'en-tête et pied à l'écran 2
    R(t, [[(".", CL_P2)]], [(ID_MAX_HAUT, "", [px(0)])])
    R(t, [[(".", CL_PHASE2), (".", CL_F1)]], [P("min-width", FEN_MIN)])
    R(t, [[(".", CL_P2)]], [P("position", "absolute")])
    R(t, [[(".", CL_PHASE2), (".", CL_P2)]], [P("position", "relative")])
    R(t, [[(".", CL_PHASE2), (".", CL_P1)]], [P("position", "absolute")])
    for c in (CL_ETOILES, CL_PIED):
        R(t, [[(".", c)]], [(cj.ID_DISPLAY, "", [(1, cj.MOT_AUCUN)])])
        R(t, [[(".", CL_PHASE2), (".", c)]], [(cj.ID_DISPLAY, "", [(7, "flex")])])
    R(t, [[(".", CL_PHASE2), (".", CL_P2)]], [(ID_MAX_HAUT, "", [px(HAUT_LIBRE)])])
    R(t, [[(".", CL_PHASE2), (".", CL_P1)]], [(ID_MAX_HAUT, "", [px(0)])])
    R(t, [[(".", CL_BOUTON2)]], [(cj.ID_DISPLAY, "", [(1, cj.MOT_AUCUN)])])
    R(t, [[(".", CL_PHASE2), (".", CL_BOUTON2)]], [(cj.ID_DISPLAY, "", [(7, "flex")])])
    R(t, [[(".", CL_PHASE2), (".", CL_BOUTON1)]], [(cj.ID_DISPLAY, "", [(1, cj.MOT_AUCUN)])])
    t.tt["m_Usings"].sort(key=lambda u: u.get("alias") or "")
    pc_ = "pastilles d'Alex" if x["pastille"] else "signes + / – (pastille d'Alex absente)"
    return [f"fenêtre : un pack par style de carte ({', '.join(x_.upper() for x_ in cj.ORDRE_STYLES)}), chacun sous "
            f"« style == k » : sa matière, sa bande, sa photo, son tampon, ses boutons et son entrée (J = le dossier "
            f"d'avant) ; écran 1 (niveau, personnalité, médias | potentiel, projets, « {TEXTE_PASSER} »), écran 2 "
            f"(Pour | Contre, {pc_}, « {TEXTE_DEVOILER} »)"]


# ---------- la vraie fiche (PlayerReport) : le rideau ----------
def P(prop, valeur):
    """v3 : une propriété de règle à sélecteur, par son nom CSS (sm.PROPRIETES de cj) ; ("mot", n) = mot-clé"""
    pid, ty = cj.sm.PROPRIETES[prop]
    if isinstance(valeur, tuple) and valeur and valeur[0] == "mot":
        return (pid, "", [(1, valeur[1])])
    if ty == 3:
        return (pid, "", [px(valeur)])
    return (pid, "", [(ty, valeur)])


def ecran_fiche(t, src, k, x, parent, s, gauche, croix_ev, classes_contenu=()):
    """v15 (maquette v4) : l'écran du style sur la fiche, avec ce qui est déjà dévoilé : la matière et le bandeau du
    dossier (sa croix enlève le cache), l'en-tête (photo, nom, poste, niveau, potentiel, tampon du groupe),
    personnalité, médias, les deux projets, Pour / Contre ; fixe (pas de classes d'animation du dossier) ; gauche : px du
    bord au début des textes (0 : comme le dossier) ; classes_contenu : sur le contenu (le fondu l'efface d'abord)"""
    P_ = PACKS[s]
    pal = cj.STYLES[s]["pal"]
    encre, gris = P_["encre"], P_["gris"]
    tr_, rr_ = src["remap"]
    f3 = cj.boite(t, src, parent, cj.ab(left=0, right=0, top=30 if s == "j" else 0, bottom=0,
                                        **{"flex-direction": "column"}))   # J : la place de l'onglet « JEUNES »
    marge = P_.get("gauche", P_["cote"])
    decale = max(0, gauche - marge - 16) if gauche else 0   # 16 : le retrait de l'en-tête et des colonnes
    fond_pack(t, src, k, f3, s, pal, decale)
    cont = cj.boite(t, src, f3, {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1,
                                 "margin-left": marge + decale, "margin-top": P_["haut"], "margin-right": P_["cote"],
                                 "margin-bottom": BAS_ECRAN}, list(classes_contenu))

    def titre(parent_, s_txt, css=None):
        cj.texte(k, parent_, s_txt, {"color": cj.rgba(gris), "font-size": 13, "-unity-font-style": "bold",
                                     **(css or {})})

    te, blocs = x["etoiles"]

    def etoiles(parent_, bloc, css=None):
        zr = cj.remap(t, tr_, rr_, parent_, [("report", RAPPORT, x["type_rapport"])],
                      {"flex-direction": "row", "align-items": "center", "flex-shrink": 0, **(css or {})})
        e = cj.entier(t, te, bloc, zr)
        cj.sans_clic(t, e)
        t.styles.style(t, e, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})
        return zr

    # l'équipe de la fiche (paramètre « team » de PlayerReport, celui que « Dévoiler la carte entière » lui passe)
    zone = cj.remap(t, tr_, rr_, cont, [("team", "team", cj.TYPE_EQUIPE)],
                    {"flex-direction": "column", "align-self": "stretch", "flex-grow": 1, "flex-shrink": 1})
    tete = cj.boite(t, src, zone, {"flex-direction": "row", "align-items": "center", "height": 100,
                                   "padding-left": 16, "padding-right": 16, "flex-shrink": 0})
    photo_pack(t, src, k, tete, s)
    ident = cj.boite(t, src, tete, {"flex-direction": "column", "align-items": "flex-start", "margin-left": 18,
                                    "max-width": 300, "flex-shrink": 0})
    cj.noms(k, ident, encre, {"align-items": "flex-start", "align-self": "flex-start"})
    cj.poste(k, ident, gris, {"margin-top": 4}, taille=14)
    zt = cj.boite(t, src, tete, {"flex-direction": "row", "align-items": "center", "justify-content": "center",
                                 "flex-grow": 1, "flex-shrink": 1, "min-width": 0,
                                 "margin-left": ECART_NOM_ETOILES, "align-self": "center"})
    for n, (quoi, bloc) in enumerate(((TEXTE_NIVEAU, blocs[0]), (TEXTE_POTENTIEL, blocs[1]))):
        rangee = cj.boite(t, src, zt, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0,
                                       **({"margin-left": ECART_LIGNE2 + 8} if n else {})})
        titre(rangee, quoi, {"margin-right": ECART_ETIQUETTE, "flex-shrink": 0})
        etoiles(rangee, bloc)
    tampon_groupe(t, src, k, tete, s, pal)

    def colonnes(parent_, n_, ecart):
        rang = cj.boite(t, src, parent_, {"flex-direction": "row", "align-items": "flex-start", "align-self": "stretch",
                                          "flex-shrink": 0, "padding-left": 16, "padding-right": 16})
        return [cj.boite(t, src, rang, {"flex-direction": "column", "flex-grow": 1, "flex-basis": 0, "min-width": 0,
                                        "flex-shrink": 1, "margin-left": ecart if n else 0}) for n in range(n_)]

    # personnalité, médias, projet à court terme, projet à long terme
    c4 = colonnes(zone, 4, 28)
    for col, (quoi, chemin) in zip(c4, ((TEXTE_PERSO, "person.Personality"), (TEXTE_MEDIAS, "person.MediaHandling"))):
        b = cj.boite(t, src, col, {"align-self": "stretch", "margin-top": 14, "flex-shrink": 0})
        titre(b, quoi)
        cj.ligne_texte(k, b, chemin, encre, 20, {"-unity-text-align": "middle-left", "align-self": "stretch",
                                                 "margin-top": 3})
    for col, (cle, quoi, liste, nombre) in zip(c4[2:], LISTES_PROJETS):
        b = cj.boite(t, src, col, {"align-self": "stretch", "margin-top": 14, "flex-shrink": 0})
        titre(b, quoi)

        def projet(dans, i, var):
            r = cj.texte_lie(t, k.s0, k.texte, dans, f"{var}.Name", ["body-sm-strong"],
                             {"color": cj.rgba(encre), "font-size": 17, "white-space": "normal",
                              "-unity-text-align": "upper-left", "align-self": "stretch", "flex-shrink": 0,
                              "margin-top": 3 if i == 0 else 5})
            cj.sans_clic(t, r)
        lignes(t, x, b, [f"{V_PROJET}{cle}{i}" for i in range(PROJETS_MAX)], liste, nombre, True, projet)
    # Pour | Contre (la pastille d'Alex en face de chaque phrase)
    rm = cj.remap(t, tr_, rr_, zone, [("report", RAPPORT, x["type_rapport"])],
                  {"flex-direction": "column", "align-self": "stretch", "flex-shrink": 0, "margin-top": 24})
    c2 = colonnes(rm, 2, 32)
    for j, (cle, quoi, liste, nombre, signe) in enumerate(LISTES_PC):
        b = cj.boite(t, src, c2[j], {"align-self": "stretch", "flex-shrink": 0})
        titre(b, quoi)
        corps = cj.boite(t, src, b, {"flex-direction": "row", "align-items": "flex-start", "align-self": "stretch",
                                     "flex-shrink": 0, "margin-top": 4})
        if x["pastille"]:
            pastilles(t, x, corps, liste)

        def point(dans, i, var, signe=signe):
            t.styles.style(t, dans, {"flex-direction": "row", "align-items": "center", "height": PAS_PC,
                                     "min-height": PAS_PC, "max-height": PAS_PC})
            if not x["pastille"]:
                cj.texte(k, dans, signe, {"color": cj.rgba(encre), "font-size": 18, "-unity-font-style": "bold",
                                          "width": 18, "flex-shrink": 0, "margin-right": 6})
            r = cj.texte_lie(t, k.s0, k.texte, dans, f"{var}.ProConsLongString", ["body-sm-strong", CLASSE_COUPE],
                             {"color": cj.rgba(encre), "font-size": TAILLE_PHRASE + 2, "white-space": "nowrap",
                              "overflow": "hidden", "-unity-text-align": "middle-left", "flex-grow": 1,
                              "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "height": PAS_PC})
            sdr = t.sd(r)
            sdr["DisplayTooltipWhenElided"], sdr["DisplayTooltipWhenElided_UxmlAttributeFlags"] = 1, 1
            sdr["pickingMode"], sdr["pickingMode_UxmlAttributeFlags"] = 0, 1
        lignes(t, x, corps, [f"{V_PC}{cle}{i}" for i in range(PC_MAX)], liste, nombre, False, point)
        vide = si_vide(t, x, b, nombre)
        cj.texte(k, vide, TEXTE_RIEN, {"color": cj.rgba(encre), "font-size": 16, "margin-top": 2})
    croix_bandeau(t, src, f3, s, pal, croix_ev)
    return f3


def regles_fiche(t):
    """v15 : les mouvements du cache (automatique : classe CL_GO, posée 0,05 s après l'arrivée ; manuel : CL_MANU et
    les classes des crans, une propriété animée par couche)"""
    op = lambda v: (cj.ID_OPACITY, "", [(2, float(v))])   # noqa: E731
    gl = lambda x_: (cj.ID_TRANSLATE, "", [pc(x_), px(0)])   # noqa: E731
    g, m = CL_GO, CL_MANU
    courbe = "ease-in-out"
    # automatique : l'écran reste PAUSE_ECRAN, puis part
    R(t, [[(".", CL_EC_R)]], [gl(0)] + tr("translate", DUREE_PART, PAUSE_ECRAN, courbe))
    R(t, [[(".", g), (".", CL_EC_R)]], [gl(101)])
    for c_, sens in ((CL_EC_PG, -101), (CL_EC_PD, 101)):
        R(t, [[(".", c_)]], [gl(0)] + tr("translate", DUREE_PART, PAUSE_ECRAN, courbe))
        R(t, [[(".", g), (".", c_)]], [gl(sens)])
    R(t, [[(".", CL_EC_FC)]], [op(1)] + tr("opacity", DUREE_FONDU, PAUSE_ECRAN, courbe))
    R(t, [[(".", g), (".", CL_EC_FC)]], [op(0)])
    R(t, [[(".", CL_EC_F)]], [op(1)] + tr("opacity", DUREE_FONDU, PAUSE_ECRAN + DUREE_FONDU, courbe))
    R(t, [[(".", g), (".", CL_EC_F)]], [op(0)])
    # manuel : des transitions courtes, sans attente (plus forte que la règle de base : deux classes)
    for c_, prop in ((CL_EC_R, "translate"), (CL_EC_PG, "translate"), (CL_EC_PD, "translate"),
                     (CL_EC_FC, "opacity"), (CL_EC_F, "opacity")):
        R(t, [[(".", m), (".", c_)]], tr(prop, DUREE_CRAN, 0, "linear"))
    # les crans (cumulés : le cran j allume aussi tous ceux d'avant ; le dernier écrit gagne)
    moitie = CRANS // 2
    for j in range(1, CRANS + 1):
        p = round(j * 100.0 / CRANS, 3)
        cran = (".", f"{CL_CRAN}{j}")
        R(t, [[cran, (".", CL_EC_R)]], [gl(p)])
        R(t, [[cran, (".", CL_EC_PG)]], [gl(-p)])
        R(t, [[cran, (".", CL_EC_PD)]], [gl(p)])
        if j <= moitie:   # fondu : l'écran s'efface sur la première moitié de la barre
            R(t, [[cran, (".", CL_EC_FC)]], [op(round(1 - j / moitie, 4))])
        else:             # puis le fond, sur la seconde
            R(t, [[cran, (".", CL_EC_F)]], [op(round(1 - (j - moitie) / moitie, 4))])


def construire_fiche(t, src, mode="auto", x=None, curseur=None, k=None):
    """v15 (maquette v4) : quand on arrive de la révélation, la fiche est couverte par l'écran du style (le style et le
    groupe lus dans les variables gardées), qui part avec le cache : fondu en deux temps, rideau, portes ; en
    automatique (PAUSE_ECRAN, puis le mouvement) comme en manuel (notre cache suit la barre dorée par crans) ; la façon
    (V_METHODE) et le mode (V_MODE) sont lus dans les variables gardées de la barre du message ; <mode> = le mode de
    départ (option de l'app)"""
    ce = first(t, lambda r: typ(t, r) == "ComponentElement")
    if ce is None:
        return [f"{FICHE} : ComponentElement introuvable"]
    tc, rc = src["composant"]
    porteur = cj.seul(t, tc, rc, ce, nom_rideau(mode))
    cj.sans_clic(t, porteur)
    t.styles.style(t, porteur, cj.PLEIN)
    variables = ([(V_RIDEAU, f"Bool|0|{CLE_RIDEAU}"), (V_RIDEAU_GO, "Bool|0|"), (V_MANUEL, "Bool|0|"),
                  (V_VAL, f"Float|{VAL_MAX}|"), (V_METHODE, f"Float|{METHODE_DEFAUT}|{CLE_METHODE}"),
                  (V_MODE, f"{depart_mode(mode)}{CLE_MODE}"),
                  (cj.V_STYLE, f"Float|{cj.numero_style(cj.style_choisi())}|{cj.CLE_STYLE}")]   # v15 : le style
                 + [(f"{P_GROUPE}{i}", f"Bool|{1 if i == 0 else 0}|{cle_groupe(i)}") for i in range(5)]   # le groupe
                 + [(f"{V_CRAN}{j}", "Bool|0|") for j in range(1, CRANS + 1)])   # les crans (manuel)
    if not cj.variables(t, src, porteur, variables):
        return [f"variable de FM ({cj.SOURCE_VARIABLES}) : forme inattendue (introuvable)"]
    cj.attacher_feuille(t, porteur)
    tvi, rvi = src["cat_visible"]
    sv, rv = x["comparer"]
    b = sv.sd(rv)["Binding"]
    zero = {"position": "absolute", "width": 0, "height": 0}

    def si(parent, chemin, op, valeur, classes=(), css=None):
        """un SIVisible de FM « chemin op valeur » (BindIntToVisible : il lit la valeur par TryCastToInt), sans clics"""
        r = ni.new_visible(t, sv, rv, parent, None, "", ni.make_binding(b, op, [chemin], valeur), list(classes))
        cj.sans_clic(t, r)
        t.styles.style(t, r, css or cj.PLEIN)
        return r

    def bloc(parent, css, classes=(), clic=False):
        return cj.boite(t, src, parent, css, classes, clic=clic)

    # ---- le signal (posé par « Dévoiler la carte entière ») : passe la main au cache local, retiré à 0,4 s ----
    v = cj.visible(t, tvi, rvi, porteur, V_RIDEAU)
    cj.sans_clic(t, v)
    t.styles.style(t, v, cj.PLEIN)
    bloc(v, {**cj.PLEIN, "background-color": cj.rgba(FOND_RIDEAU)}, clic=True)   # les 0,05 premières secondes
    delai(t, src, v, DELAI_OUVERT, [cj.copier("const.True", V_MANUEL)])
    va = cj.visible(t, tvi, rvi, v, V_MODE, inverse=True)   # automatique : le départ
    cj.sans_clic(t, va)
    t.styles.style(t, va, zero)
    delai(t, src, va, DELAI_OUVERT, [cj.copier("const.True", V_RIDEAU_GO)])
    delai(t, src, v, FIN_SIGNAL, [cj.copier("const.False", V_RIDEAU)])
    # ---- le cache (local) : automatique et manuel ----
    c = cj.visible(t, tvi, rvi, porteur, V_MANUEL)
    cj.sans_clic(t, c)
    t.styles.style(t, c, cj.PLEIN)
    cc = bloc(c, cj.PLEIN)
    for bb, cl_ in [(V_RIDEAU_GO, CL_GO), (V_MODE, CL_MANU)] + [(f"{V_CRAN}{j}", f"{CL_CRAN}{j}")
                                                              for j in range(1, CRANS + 1)]:
        if cj.boite_style(t, src, cc, bb, cl_) is None:
            return [f"boîte de style de FM ({cj.SOURCE_STYLE}) : forme inattendue (introuvable)"]
    # les crans : le seuil j de la barre (lu par un SIVisible, qui accepte la valeur en nombre à virgule) allume ou
    # éteint l'interrupteur j ; la boîte de style ci-dessus le lit en vrai / faux (jamais la barre elle-même : elle la
    # lirait par Get<int>)
    pas = VAL_MAX // CRANS
    for j in range(1, CRANS + 1):
        seuil = VAL_MAX - j * pas
        delai(t, src, si(cc, V_VAL, OP_INF_EGAL, seuil, css=zero), DELAI_CRAN,
              [cj.copier("const.True", f"{V_CRAN}{j}")])
        delai(t, src, si(cc, V_VAL, OP_SUP, seuil, css=zero), DELAI_CRAN, [cj.copier("const.False", f"{V_CRAN}{j}")])
    fa = cj.visible(t, tvi, rvi, cc, V_MODE, inverse=True)   # automatique : la fin
    cj.sans_clic(t, fa)
    t.styles.style(t, fa, zero)
    delai(t, src, fa, FIN_AUTO, [cj.copier("const.False", V_MANUEL), cj.copier("const.False", V_RIDEAU_GO)])
    vv = si(cc, V_VAL, OP_SUP, 0)   # tant que la fiche n'est pas découverte en entier (manuel)
    tr_, rr_ = src["remap"]
    rp = cj.remap(t, tr_, rr_, vv, [("person", "player", cj.TYPE_PERSONNE)], cj.PLEIN)   # le jeune de la fiche
    ev = [cj.copier("const.False", V_MANUEL), cj.copier("const.False", V_RIDEAU),
          cj.copier("const.False", V_RIDEAU_GO)]
    for n_style, s in enumerate(cj.ORDRE_STYLES, 1):
        vs = ni.new_visible(t, sv, rv, rp, None, nom(f"fiche-{s}"), ni.make_binding(b, OP_EGAL, [cj.V_STYLE], n_style))
        cj.sans_clic(t, vs)
        t.styles.style(t, vs, cj.PLEIN)
        # fondu : l'écran s'efface, puis le fond
        lf = bloc(si(vs, V_METHODE, OP_EGAL, 1), {**cj.PLEIN, "overflow": "hidden"}, [CL_EC_F], clic=True)
        ecran_fiche(t, src, k, x, lf, s, 0, ev, [CL_EC_FC])
        # rideau : l'écran part avec lui, la bande dorée en tête
        lr = bloc(si(vs, V_METHODE, OP_EGAL, 2), {**cj.PLEIN, "overflow": "hidden"}, [CL_EC_R], clic=True)
        ecran_fiche(t, src, k, x, lr, s, MARGE_RIDEAU, ev)
        bloc(lr, cj.ab(left=0, top=0, bottom=0, width=BORD_LARGE, **{"background-color": cj.rgba(BORD_RIDEAU)}))
        # portes : chacune sa moitié de l'écran, sans trait à la jointure (3, et 4 des versions d'avant)
        m3 = si(vs, V_METHODE, OP_SUP_EGAL, 3)
        for cote, cl_, decal in (("left", CL_EC_PG, 0.0), ("right", CL_EC_PD, -100.0)):
            porte = bloc(m3, cj.ab(**{cote: 0}, top=0, bottom=0, width={"unit": 2, "value": 50.0},
                                   **{"overflow": "hidden"}), [cl_], clic=True)
            dedans = bloc(porte, cj.ab(left={"unit": 2, "value": decal}, top=0, bottom=0,
                                       width={"unit": 2, "value": 200.0}))
            ecran_fiche(t, src, k, x, dedans, s, 0, ev)
    # ---- manuel : la barre dorée (le curseur de FM, une poignée) et la consigne ----
    vm = cj.visible(t, tvi, rvi, vv, V_MODE)
    cj.sans_clic(t, vm)
    t.styles.style(t, vm, cj.PLEIN)
    consigne = si(vm, V_VAL, OP_EGAL, VAL_MAX, (), cj.ab(left=0, right=0, bottom=HAUT_BARRE + 14, height=44, **{
        "flex-direction": "row", "justify-content": "center", "align-items": "center"}))
    pil = bloc(consigne, {"background-color": cj.ton("#000000", 0.6), **cj.rayons(8), "padding-left": 18,
                          "padding-right": 18, "height": 44, "justify-content": "center", "flex-shrink": 0})
    ttx, rtx = src["cat_texte"]
    s_ = cj.texte_fixe(t, ttx, rtx, pil, TEXTE_TIRE, ["body-sm-strong"],
                       {"color": cj.rgba(ENCRE), "font-size": 20, "white-space": "nowrap",
                        "-unity-text-align": "middle-center"})
    cj.sans_clic(t, s_)
    barre = bloc(vm, cj.ab(left=0, right=0, bottom=0, height=HAUT_BARRE), [CL_MANUEL, CL_BANDE])
    bloc(barre, {**cj.PLEIN, "background-color": cj.ton("#000000", 0.55)})
    bloc(barre, cj.ab(left=24, right=24, bottom=(HAUT_BARRE - 4) // 2, height=4,
                      **{"background-color": cj.ton(BORD_RIDEAU, 0.45), **cj.rayons(2)}))
    ts, rs = curseur
    cur = cj.seul(t, ts, rs, barre, nom("curseur"), [CL_CURSEUR])
    sd = t.sd(cur)
    for champ, val in (("valueOverride", float(VAL_MAX)), ("lowValue", 0.0), ("highValue", float(VAL_MAX)),
                       ("fill", 1), ("inverted", 0), ("direction", 0), ("pageSize", 0.0), ("showInputField", 0),
                       ("DataLink", {"m_path": V_VAL}), ("UseIntegerValues", 1), ("SliderSteps", 0)):
        sd[champ], sd[f"{champ}_UxmlAttributeFlags"] = val, 1
    f = sd["InitialiseBindingFunc"]   # pas de fonction de départ (bornes et valeur ci-dessus)
    f["m_target"]["m_guid"] = ""
    for kk in ("m_inputs", "m_outputs"):
        if isinstance(f.get(kk), dict):
            f[kk]["m_variable"]["m_argumentBytes"] = []
    sd["InitialiseBindingFunc_UxmlAttributeFlags"] = 0
    t.styles.style(t, cur, {**cj.PLEIN, "margin-top": 0, "margin-bottom": 0, "margin-left": 0, "margin-right": 0,
                            "padding-top": 0, "padding-bottom": 0, "padding-left": 0, "padding-right": 0,
                            "min-height": 0})
    regles_fiche(t)
    # les morceaux du curseur d'Unity (noms posés par BaseSlider, Unity 6000.3) : spécificité 111, au-dessus des
    # règles de FM (« .unity-base-slider__dragger.unity-base-slider--movable:hover:enabled » = 41)
    plein_r = [P("position", "absolute"), P("left", 0), P("top", 0), P("right", 0), P("bottom", 0),
               P("margin-top", 0), P("margin-bottom", 0), P("margin-left", 0), P("margin-right", 0)]
    R(t, [[(".", CL_MANUEL), (".", CL_CURSEUR), (".", "unity-base-slider__input")]], plein_r)
    R(t, [[(".", CL_MANUEL), ("#", "unity-drag-container")]], plein_r)
    R(t, [[(".", CL_MANUEL), ("#", "unity-tracker")]],
      plein_r + [P("height", ("mot", MOT_AUTO)), P("background-color", (0.0, 0.0, 0.0, 0.0)),
                 P("border-top-width", 0), P("border-bottom-width", 0), P("border-left-width", 0),
                 P("border-right-width", 0)] + [P(kk, 0) for kk in cj.rayons(0)])
    R(t, [[(".", CL_MANUEL), ("#", "unity-fill")]],
      [P("position", "absolute"), P("background-color", (0.0, 0.0, 0.0, 0.0))])
    R(t, [[(".", CL_MANUEL), ("#", "unity-dragger")]],
      [P("position", "absolute"), P("top", 0), P("bottom", 0), P("height", ("mot", MOT_AUTO)), P("margin-top", 0),
       P("margin-bottom", 0), P("margin-left", 0), P("margin-right", 0), P("width", POIGNEE),
       P("background-color", cj.rgba(BORD_RIDEAU)), P("border-top-width", 0), P("border-bottom-width", 0),
       P("border-left-width", 3), P("border-right-width", 3), P("border-left-color", cj.rgba(FOND_RIDEAU)),
       P("border-right-color", cj.rgba(FOND_RIDEAU))] + [P(kk, 0) for kk in cj.rayons(0)])
    R(t, [[(".", CL_BANDE), ("#", "unity-dragger")]],
      [P("top", 6), P("bottom", 6), P("width", 22), P("border-left-width", 0), P("border-right-width", 0)]
      + [P(kk, 6) for kk in cj.rayons(0)])
    R(t, [[(".", CL_MANUEL), ("#", "unity-dragger-border")]], [(cj.ID_DISPLAY, "", [(1, cj.MOT_AUCUN)])])
    # v5 : SISlider n'applique pas inverted (vu en jeu) : la barre est RETOURNÉE à l'horizontale (scale -1 1) : la
    # poignée part à gauche, la valeur descend de VAL_MAX à 0 quand on la tire vers la droite
    R(t, [[(".", CL_MANUEL)]], [(cj.ID_SCALE, "", [(2, -1.0), (2, 1.0)])])
    return [f"l'écran du style sur la fiche (photo, poste, niveau, potentiel, personnalité, médias, projets, Pour / "
            f"Contre ; style et groupe lus dans les variables gardées), qui part avec le cache : "
            f"{', '.join(n for _k, n, _x in METHODES)} ; automatique (l'écran {PAUSE_ECRAN} s, puis {DUREE_PART} s) "
            f"et manuel (barre dorée, notre cache par {CRANS} crans) ; façon et mode lus dans la barre du message "
            f"(départ : {mode})"]


# ---------- le panneau de la fenêtre (ui-panelids) ----------
def mono(env, n):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == n:
                return o
        except Exception:
            continue
    return None


def panneau_a_jour(tt):
    p = ((tt.get("m_panelDescription") or {}).get("parameters")) or []
    return all(n in p for n, _ in PARAMS)


def construire_panneau(tt):
    p = (tt.get("m_panelDescription") or {}).get("parameters")
    if p is None:
        return f"panneau {PANNEAU} : paramètres introuvables"
    for n, _ in PARAMS:
        if n not in p:
            p.append(n)
    return f"panneau {PANNEAU} : paramètres {', '.join(p)}"


# ---------- la carte (26.19) : le nom ouvre la fenêtre ----------
def blocs_nom(t):
    """v10 : les blocs du nom de la carte, un par style (26.19 v25 pose les 8 styles dans chaque carte)"""
    return [r for r in t.walk() if cj.CL_NOMS in (t.elem(r).get("m_Classes") or [])]


def carte_v24(t):
    """la carte de 26.19 redemande-t-elle notre variable ? (v31 : les groupes de la révélation)"""
    be = first(t, lambda r: typ(t, r) == "BindingExpect")
    return be is not None and any(p.get("name") == cj.V_REV for p in t.sd(be).get("Parameters") or [])


def carte_a_jour(t, code):
    """v10 : nos morceaux dans le bloc du nom de chaque style"""
    return any(t.name(r) == nom(f"{code}-s0-g0") for r in t.walk())


def poser_carte(t, src, code, nombre, x):
    blocs = blocs_nom(t)
    if not blocs:
        return ["carte de 26.19 : bloc du nom introuvable"]
    tvi, rvi = src["cat_visible"]
    sv, rvc = x["comparer"]
    bcmp = sv.sd(rvc)["Binding"]

    def selon_menu(parent, i):
        """v18 : le groupe i a la révélation si le menu du message est au moins à son seuil (comparaison de FM)"""
        a = ni.new_visible(t, sv, rvc, parent, None, "",
                           ni.make_binding(bcmp, OP_SUP_EGAL, [cj.V_REV], SEUIL_GROUPE[i]))
        cj.sans_clic(t, a)
        t.styles.style(t, a, cj.PLEIN)
        return a
    for j, bloc in enumerate(blocs):
        for i in range(nombre):
            g = cj.visible(t, tvi, rvi, bloc, f"{cj.MARQUE_ALEX}{i}", nom(f"{code}-s{j}-g{i}"))
            cj.sans_clic(t, g)
            t.styles.style(t, g, cj.PLEIN)
            a = selon_menu(g, i)
            bouton(t, src, a, [ouvrir_panneau(GUID_PANNEAU, [(P_ON, "const.True"), ("person", cj.PARAM),
                                                              ("player", cj.PARAM), ("team", "team"),
                                                              ("human", "human"), (f"{P_GROUPE}{i}", "const.True"),
                                                              (cj.V_STYLE, cj.V_STYLE),   # v11 : le style
                                                              (P_INTRO, "const.False")])],   # v13 : sans ouverture
                   cj.PLEIN)
    # v13 (Kinito) : le DOS (1er clic, carte cachée) : retourne la carte (comme son propre clic) et ouvre la fenêtre
    # par l'ouverture ; dans le dos de chaque style, par-dessus son dessin ; parti avec le dos une fois retournée
    doss = dos_carte(t)
    for j, dos in enumerate(doss):
        for i in range(nombre):
            g = cj.visible(t, tvi, rvi, dos, f"{cj.MARQUE_ALEX}{i}", nom(f"{code}-d{j}-g{i}"))
            cj.sans_clic(t, g)
            t.styles.style(t, g, cj.PLEIN)
            a = selon_menu(g, i)
            bouton(t, src, a, [cj.copier("const.True", cj.V_CARTE),
                               ouvrir_panneau(GUID_PANNEAU, [(P_ON, "const.True"), ("person", cj.PARAM),
                                                              ("player", cj.PARAM), ("team", "team"),
                                                              ("human", "human"), (f"{P_GROUPE}{i}", "const.True"),
                                                              (cj.V_STYLE, cj.V_STYLE), (P_INTRO, "const.True")])],
                   cj.PLEIN)
    return [f"carte : le nom ouvre la révélation pour les {nombre} groupes, chacun selon le menu « Révélation » du "
            f"message, dans les {len(blocs)} styles ; le dos (1er clic) l'ouvre par l'ouverture ({len(doss)} dos)"]


def dos_carte(t):
    """v13 : le dos de chaque style de la carte (le SIButton « …-<style>-dos » de 26.19 v25)"""
    return [r for r in t.walk() if (t.name(r) or "").startswith(cj.PREFIXE) and (t.name(r) or "").endswith("-dos")]


# ---------- la catégorie (zone de 26.19) : l'interrupteur ----------
def regle_marquee(t, selecteurs, props):
    """v9 : une règle à sélecteurs posée dans la feuille de la CATÉGORIE (partagée avec 26.19 et Alex), marquée à notre
    nom (REPERE_REGLE) : notre retrait la retrouve, celui de 26.19 ne la prend pas pour la sienne"""
    idx = t.styles.add_rule(list(props) + [(-1, REPERE_REGLE, [(2, float(VERSION))])])
    complexes = []
    for sel in selecteurs:
        parts, spec = [], 1
        for i, (k, v) in enumerate(sel):
            parts.append({"m_Parts": [{"m_Value": v, "m_Type": 3 if k == "." else 6}],
                          "m_PreviousRelationship": 0 if i == 0 else 2})
            spec += 10 if k == "." else 100
        complexes.append({"m_Specificity": spec, "m_Selectors": parts, "ruleIndex": idx})
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = complexes
    return idx


def poser_interrupteur(t, src, x, y, mode):
    barre = first(t, lambda r: t.name(r) == f"{cj.NOM_ZONE}-barre")
    tout = first(t, lambda r: t.name(r) == f"{cj.NOM_ZONE}-tout")
    if barre is None or tout is None:
        return ["zone de 26.19 : barre ou « Tout retourner » introuvable"]
    tc, rc = src["composant"]
    # v9 : un ComponentElement de FM (porteur de nos deux variables rangées, comme la zone de 26.19)
    pil = cj.seul(t, tc, rc, barre, nom_inter(mode), (), t.children(barre).index(tout))
    t.styles.style(t, pil, {"flex-direction": "row", "align-self": "stretch", "align-items": "stretch",
                            "margin-right": 6, "flex-shrink": 0})
    if not cj.variables(t, src, pil, [(V_METHODE, f"Float|{METHODE_DEFAUT}|{CLE_METHODE}"),
                                      (V_MODE, f"{depart_mode(mode)}{CLE_MODE}")]):
        return [f"variable de FM ({cj.SOURCE_VARIABLES}) : forme inattendue (introuvable)"]
    tvi, rvi = src["cat_visible"]
    sombre = (0.04, 0.06, 0.09, 0.32)
    css_pastille = {"align-self": "stretch", "min-height": 0, "padding-left": 10, "padding-right": 10,
                    "background-color": sombre, **cj.rayons(9), "flex-direction": "row", "align-items": "center",
                    "justify-content": "center"}
    # v18 : « Révélation : Élite ▾ », un menu de FM (comme « Style » et « Fiche ») qui écrit les groupes dans la
    # variable rangée de la zone (cj.V_REV) ; la liste : Non, Élite, Élite et excellents, Tous les groupes
    cj.poser_menu(t, src, y, pil, None, cj.V_REV, len(CHOIX_REV), CL_MENU_REV, TEXTE_REV, GUID_LIGNE, regle_marquee,
                  None, [v for v, _n, _c in CHOIX_REV])
    # sauf sur « Non » : « Fiche : <façon> ▾ » (le menu de FM de 26.19 v25, poser_menu ; v10 : son champ à la hauteur
    # de la barre, vu en jeu en v9) et la bascule Auto | Manuel (v18 : une comparaison de FM sur le menu)
    sv, rvc = x["comparer"]
    va = ni.new_visible(t, sv, rvc, pil, None, "",
                        ni.make_binding(sv.sd(rvc)["Binding"], OP_SUP_EGAL, [cj.V_REV], cj.REV_ELITE))
    cj.sans_clic(t, va)
    t.styles.style(t, va, {"flex-direction": "row", "align-self": "stretch"})
    cj.poser_menu(t, src, y, va, None, V_METHODE, len(METHODES), CL_MENU, TEXTE_MENU, GUID_LIGNE, regle_marquee,
                  {"margin-left": 6})
    # la bascule Auto | Manuel : le mode choisi en plein (clair, texte sombre, gras), l'autre à cliquer
    pmo = cj.boite(t, src, va, {"align-self": "stretch", "flex-direction": "row", "align-items": "stretch",
                                "margin-left": 6, "padding-left": 2, "padding-right": 2, "padding-top": 2,
                                "padding-bottom": 2, "background-color": sombre, **cj.rayons(9)}, clic=True)
    css_seg = {"align-self": "stretch", "min-height": 0, "padding-left": 8, "padding-right": 8, **cj.rayons(7),
               "flex-direction": "row", "align-items": "center", "justify-content": "center"}
    for manuel, s in ((False, TEXTE_AUTO), (True, TEXTE_MANU)):
        choisi = cj.visible(t, tvi, rvi, pmo, V_MODE, inverse=not manuel)
        t.styles.style(t, choisi, {"flex-direction": "row", "align-self": "stretch"})
        seg = cj.boite(t, src, choisi, {**css_seg, "background-color": cj.rgba("#F3EEE2")})
        texte_bouton(t, src, seg, s, "#10131A", 12)
        autre = cj.visible(t, tvi, rvi, pmo, V_MODE, inverse=manuel)
        t.styles.style(t, autre, {"flex-direction": "row", "align-self": "stretch"})
        b = bouton(t, src, autre, [cj.copier("const.True" if manuel else "const.False", V_MODE)], css_seg)
        texte_bouton(t, src, b, s, "#FFFFFF", 12)
    # v16 (Kinito : « en normal en taille d'écriture, ça passe pas, les boutons dans la barre ») : avec un texte Normal
    # ou plus grand, la barre quitte la barre d'Alex et se range en flux sous elle, à droite, sur un fond léger (la
    # classe posée sur la zone de 26.19 par une boîte de style de FM : taille du texte >= SEUIL_DESSOUS ; v18 : quel
    # que soit le menu, le booléen est le « vrai » de la zone, cj.V_VRAI ; en Petit, rien ne change)
    if cj.boite_style(t, src, t.parent[barre], cj.V_VRAI, CL_DESSOUS, valeur=SEUIL_DESSOUS,
                      nom=nom("barre-dessous")) is None:
        return [f"boîte de style de FM ({cj.SOURCE_STYLE}) : forme inattendue (introuvable)"]
    regle_marquee(t, [[(".", CL_DESSOUS), (".", cj.CL_BARRE)]],
                  [P("position", "relative"), P("right", 6), P("bottom", 0), P("align-self", "flex-end"),
                   P("margin-top", 2), P("margin-bottom", 8), P("padding-left", 4), P("padding-right", 4),
                   P("background-color", (1.0, 1.0, 1.0, 0.07)), P("border-top-left-radius", 12),
                   P("border-top-right-radius", 12), P("border-bottom-left-radius", 12),
                   P("border-bottom-right-radius", 12)])
    return [f"« {TEXTE_REV} {' / '.join(n for _v, n, _c in CHOIX_REV)} » (menu de FM) à côté de « Tout "
            f"retourner » ; sauf Non : menu de FM « {TEXTE_MENU} "
            f"{' / '.join(n for _k, _c, n in METHODES)} » (ligne = {MODELE_LIGNE}) et bascule « {TEXTE_AUTO} | "
            f"{TEXTE_MANU} » (départ : {mode}) ; en texte Normal et plus, avec oui : la barre sous celle d'Alex"]


# ---------- v9 : le modèle de ligne du menu (AnimTransitionSpeedDropdownRow, cité par rien) ----------
def ligne_a_jour(t):
    return any(t.name(r) == NOM_LIGNE for r in t.walk())


def retirer_morceaux(t):
    """nos morceaux (par leur nom) ET les règles de style intégrées qu'ils avaient (sinon elles restaient dans la
    feuille de 26.19 / d'Alex : vu au banc du 09/11) ; jamais une règle d'un autre"""
    ns = marques(t)
    enlever = set()
    for r in ns:
        if r in t.refs:
            enlever |= {t.elem(x).get("m_RuleIndex", -1) for x in t.walk(r)}
            t.remove(r)
    # v9 : nos règles à sélecteurs de la catégorie (le menu), marquées à notre nom (regle_marquee)
    marquees = {i for i, rg in enumerate(t.styles.sh["m_Rules"])
                if any(p.get("m_CustomName") == REPERE_REGLE for p in rg["m_Properties"])}
    if ns or marquees:
        retirer_regles(t, enlever | marquees)
    # v9 : la déclaration du modèle inclus de notre menu (« dropdown-secondary »), si plus rien ne s'en sert (vu au
    # banc du 09/11 : elle restait dans la catégorie après le retrait)
    # (v10 : 26.19 v25 s'en sert aussi, pour le menu des styles : retirée seulement si plus rien ne s'en sert)
    if ns:
        cj.retirer_alias_menu(t)
    return bool(ns or marquees)


def retirer_regles(t, enlever):
    """comme cj.retirer_regles, SANS les règles marquées de 26.19 (elles ne sont pas à nous) : les règles de <enlever>
    que plus rien n'utilise, renumérotées, et les valeurs qu'elles avaient ajoutées en fin de table"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = set(enlever) - utilisees - {-1}
    if not enlever:
        return
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for rg in t.styles.sh["m_Rules"]:
        for cs in rg.get("m_ComplexSelectors") or []:
            cs["ruleIndex"] = nouvel.get(cs.get("ruleIndex"), cs.get("ruleIndex"))
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
    servies = {}
    for rg in t.styles.sh["m_Rules"]:
        for p in rg["m_Properties"]:
            for v in p["m_Values"]:
                if v["m_ValueType"] in tables:
                    servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
    for n in set(tables.values()):
        vals = t.styles.sh.get(n) or []
        while vals and len(vals) - 1 not in servies.get(n, set()):
            vals.pop()
    t.styles.changed = True


def remettre_original(o, n):
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{n} : pas de sauvegarde d'origine, rien fait (vérification des fichiers Steam)")
        return False
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    print(f"{n} : remis d'origine")
    return True


# ---------- commandes ----------
def cmd_appliquer():
    if not evenements_ok():
        print("révélation des jeunes : format d'événement inattendu, rien n'est changé")
        return
    src = cj.sources()
    x22 = sources22()
    y9 = cj.sources_menu()   # v10 : le menu de FM, partagé avec 26.19 v25
    m = cj.manque(src) + manque22(x22) + cj.manque_menu(y9)
    if m:
        print(f"révélation des jeunes : morceaux de FM introuvables ({', '.join(m)}), rien n'est changé")
        return
    if not x22["pastille"]:
        print("révélation des jeunes : pastille d'Alex (ProConRow) pas dans le jeu : signes + / – à la place")
    code, nombre = CODE_JEU, len(SEUIL_GROUPE)   # v18 : les 5 groupes, chacun selon le menu du message
    mode = mode_rideau()
    curseur = curseur_fm()   # v9 : toujours (le mode se choisit en jeu)
    if curseur is None:
        print(f"révélation des jeunes : curseur de FM ({SOURCE_CURSEUR}) introuvable ou changé, rien n'est changé")
        return
    print(f"révélation des jeunes : groupes choisis en jeu (départ : Élite), dévoilement de départ « {mode} »")
    olig = ouvrir(MODELE_LIGNE)
    if olig is None:
        print(f"révélation des jeunes : {MODELE_LIGNE} introuvable, rien n'est changé")
        return
    oc, ocat = ouvrir(cj.MODELE_CARTE), ouvrir(cj.MODELE_CAT)
    if oc is None or ocat is None or not carte_v24(oc[3]) or not blocs_nom(oc[3]) or not cj.cat_a_jour(ocat[3]):
        print(f"révélation des jeunes : les cartes 26.19 v{cj.VERSION} ne sont pas posées (réinstaller d'abord « Message "
              f"des jeunes : cartes à retourner »), rien n'est changé")
        return
    ofen, ofi = ouvrir(FENETRE), ouvrir(FICHE)
    pan = mono(nb.env_of(PANNEAUX), PANNEAU)
    if ofen is None or ofi is None or pan is None:
        print(f"révélation des jeunes : {FENETRE}, {FICHE} ou le panneau {PANNEAU} introuvable, rien n'est changé")
        return
    travaux, msgs = [], []
    s0 = ouvrir(cj.MODELE_CARTE, depart_original=True)[3]   # v15 : aussi pour la fiche (l'écran du style)
    portrait = first(s0, lambda r: s0.elem(r).get("m_TemplateAlias") == "thumbnails-alt-person-picture")
    texte = first(s0, lambda r: typ(s0, r) == "SIText")
    if portrait is None or texte is None:
        print(f"{cj.MODELE_CARTE} : forme inattendue (introuvable), rien n'est changé")
        return
    if any(ofen[3].name(r) == NOM_FENETRE for r in marques(ofen[3])):
        print(f"{FENETRE} : déjà appliqué")
    else:
        w = ouvrir(FENETRE, depart_original=True)
        if marques(w[3]):
            print(f"{FENETRE} : pas de sauvegarde d'origine propre, rien n'est changé")
            return
        msgs += [f"{FENETRE} : {y}" for y in construire_fenetre(w[3], src, cj.K(w[3], src, s0, portrait, texte),
                                                                 x22)]
        travaux.append(w)
    if any(ofi[3].name(r) == nom_rideau(mode) for r in marques(ofi[3])):
        print(f"{FICHE} : déjà appliqué")
    else:
        f = ouvrir(FICHE, depart_original=True)
        if marques(f[3]):
            print(f"{FICHE} : pas de sauvegarde d'origine propre, rien n'est changé")
            return
        msgs += [f"{FICHE} : {x}" for x in construire_fiche(f[3], src, mode, x22, curseur,
                                                              cj.K(f[3], src, s0, portrait, texte))]
        travaux.append(f)
    if ligne_a_jour(olig[3]):
        print(f"{MODELE_LIGNE} : déjà appliqué")
    else:
        w = ouvrir(MODELE_LIGNE, depart_original=True)
        if marques(w[3]):
            print(f"{MODELE_LIGNE} : pas de sauvegarde d'origine propre, rien n'est changé")
            return
        # v18 : la même ligne pour les deux menus du message (« Fiche » : 1 à 3 ; « Révélation » : 11 à 14), noms
        # courts dans le menu fermé (ceux de « Fiche » : les mêmes)
        msgs += [f"{MODELE_LIGNE} : {x}" for x in cj.construire_ligne_menu(
            w[3], y9, [n for _k, _c, n in METHODES] + [n for _v, n, _c in CHOIX_REV], NOM_LIGNE,
            courts=[n for _k, _c, n in METHODES] + [c for _v, _n, c in CHOIX_REV],
            valeurs=[k for k, _c, _n in METHODES] + [v for v, _n, _c in CHOIX_REV])]
        travaux.append(w)
    tt_p = pan.read_typetree()
    pan_change = not panneau_a_jour(tt_p)
    if pan_change:
        tt_p = hp.original(PANNEAUX, pan) or tt_p
        msgs.append(construire_panneau(tt_p))
    else:
        print(f"panneau {PANNEAU} : déjà appliqué")
    if carte_a_jour(oc[3], code) and len(marques(oc[3])) == nombre * (len(blocs_nom(oc[3])) + len(dos_carte(oc[3]))):
        print(f"{cj.MODELE_CARTE} : déjà appliqué")
    else:
        retirer_morceaux(oc[3])
        msgs += [f"{cj.MODELE_CARTE} : {x}" for x in poser_carte(oc[3], src, code, nombre, x22)]
        travaux.append(oc)
    if any(ocat[3].name(r) == nom_inter(mode) for r in marques(ocat[3])):
        print(f"{cj.MODELE_CAT} : déjà appliqué")
    else:
        retirer_morceaux(ocat[3])
        msgs += [f"{cj.MODELE_CAT} : {x}" for x in poser_interrupteur(ocat[3], src, x22, y9, mode)]
        travaux.append(ocat)
    for x in msgs:
        print(x)
    if any("introuvable" in x for x in msgs):
        print("révélation des jeunes : rien n'est changé")
        return
    for o in travaux:
        cj.enregistrer(*o)
    if pan_change:
        pan.save_typetree(tt_p)
        nb._dirty.add(PANNEAUX)
    if travaux or pan_change:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as fm:
            json.dump({"actif": True, "version": VERSION, "groupes": code, "rideau_depart": mode}, fm)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for n in (FENETRE, FICHE, MODELE_LIGNE):   # v9 : la ligne du menu (modèle cité par rien) aussi
        o = ouvrir(n)
        if o is not None and marques(o[3]):
            fait = remettre_original(o, n) or fait
    pan = mono(nb.env_of(PANNEAUX), PANNEAU)
    if pan is not None and any(n in (((pan.read_typetree().get("m_panelDescription") or {}).get("parameters")) or [])
                               for n, _ in PARAMS):
        orig = hp.original(PANNEAUX, pan)
        if orig is None:
            print(f"panneau {PANNEAU} : pas de sauvegarde d'origine, rien fait")
        else:
            pan.save_typetree(orig)
            nb._dirty.add(PANNEAUX)
            fait = True
            print(f"panneau {PANNEAU} : remis d'origine")
    for n in (cj.MODELE_CARTE, cj.MODELE_CAT):
        o = ouvrir(n)
        if o is not None and retirer_morceaux(o[3]):
            cj.enregistrer(*o)
            fait = True
            print(f"{n} : nos morceaux retirés")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    code, nombre = CODE_JEU, len(SEUIL_GROUPE)
    mode = mode_rideau()
    for n, a_jour in ((FENETRE, lambda t: any(t.name(r) == NOM_FENETRE for r in marques(t))),
                      (FICHE, lambda t: any(t.name(r) == nom_rideau(mode) for r in marques(t))),
                      (MODELE_LIGNE, ligne_a_jour),
                      (cj.MODELE_CARTE, lambda t: carte_a_jour(t, code)),
                      (cj.MODELE_CAT, lambda t: any(t.name(r) == nom_inter(mode) for r in marques(t)))):
        o = ouvrir(n)
        if o is None:
            print(f"{n} : introuvable")
            continue
        t = o[3]
        print(f"{n} : " + (f"révélation posée (à jour, v{VERSION})" if a_jour(t) else
                           ("ANCIENNE version" if marques(t) else "rien de la révélation")))
    pan = mono(nb.env_of(PANNEAUX), PANNEAU)
    print(f"panneau {PANNEAU} : " + ("introuvable" if pan is None else
                                     "paramètres présents" if panneau_a_jour(pan.read_typetree()) else
                                     "ANCIENNE version (paramètres d'une version précédente)" if P_ON in (
                                         (pan.read_typetree().get("m_panelDescription") or {}).get("parameters") or [])
                                     else "d'origine"))
    print(f"groupes, façon et mode : choisis en jeu (départ : Élite, « {mode} »)")
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
            print("révélation des jeunes : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
