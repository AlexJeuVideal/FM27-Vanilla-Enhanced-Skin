"""Bouton « Organiser amical » sur la page Infos de tous les clubs, adversaire déjà choisi (ESSAI).

v5 (2026-11-12) : retour du bouton des v1 / v2, cette fois avec une vraie ligne du menu de FM.
Ce qu'on a lu dans le moteur (game_plugin.dll, réaction à l'action 0x79307538 « adversaire choisi ») : FM prend la
ligne envoyée (DisplayValuePair, comme les lignes du menu « Choisir adversaire »), lit son champ PropertyValue (code
0x7074766c), le prend comme numéro d'équipe et va chercher l'équipe à ce numéro. v1 envoyait l'équipe, v2 son numéro
seul : pas de PropertyValue -> 0 -> l'équipe n° 0 = Algérie.
Donc ici : une variable locale DisplayValuePair (créée par FM, comme selectedNationDvp de ClubSectionLHS), remplie par
une copie (217,15,225,87 vers <variable>.PropertyValue, comme IGEKitEditorChangeKitStyleDialog), puis envoyée.
Deux boutons côte à côte, un par valeur essayée (VARIANTES) : le numéro de l'équipe (team.UniqueId), l'équipe elle-même.
v3 / v4 (retirées, rien d'affiché en jeu) : entrées d'action du jeu dans les menus d'équipe (ClubEntitySubtabs) ->
appliquer remet ClubEntitySubtabs d'origine s'il porte encore nos entrées.

Page club > Infos : au-dessus de l'équipe affichée par les onglets d'équipes de FM (Équipe première, Réserve, U19…).
Clic : 1. ouvrir la fenêtre d'amical de FM (ArrangeFriendlyCard 78a354d5, comme le calendrier) pour human.team ;
2. copier la valeur dans la ligne ; 3. l'envoyer à human.team.ArrangeFriendly comme le menu « Choisir adversaire ».
Caché sur ta propre équipe (team.UniqueId ≠ human.team.UniqueId).

Modèles / données touchés (ce script est leur seul propriétaire, appliquer repart toujours de l'original sauvegardé) :
- ClubInfoReportBlock : page Infos du club (bouton dans les 2 versions : onglets d'équipes et menu déroulant) ;
- ClubEntitySubtabs (gamemodules_assets_gameworld.bundle) : remis d'origine (v3 / v4) ;
- BindAndSetValueToDestination (ui-visualfunctions_assets_all.bundle, fonction FM inutilisée) : réécrite en « a − b »
  (v26, correction du numéro ; v14-v18 : soustraction d'une constante) ;
- NegativeColourDataCollection (ui-datacollections_assets_all.bundle, table FM inutilisée) : réécrite en table
  UniqueId -> numéro du moteur des équipes de la base (club_amical_equipes.txt, v19).

Usage (jeu fermé) : club_amical.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import struct
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, make_binding, new_visible, visible_model, decode_args, encode_args, \
    _enc_varint  # noqa: E402
import entrainement_equipes as ee  # noqa: E402  (événement « ouvrir un écran », morceaux de FM)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
EQUIPE_JOUEUR = "human.team"     # équipe du joueur qui joue l'amical (celle de la fenêtre)
LISTE = f"{EQUIPE_JOUEUR}.ArrangeFriendly.TeamOpponent"   # lignes du menu « Choisir adversaire » de la fenêtre
# le menu de la fenêtre (lu au mod, sonde « amical ») : 11 catégories {RowData : {DisplayValue, PropertyValue vide},
# ChildList : les équipes} ; une équipe choisie = {DisplayValue « Alessandria (9,66K €) », PropertyValue 910 (numéro
# du moteur)}. On envoie l'équipe n° EQUIPE de la catégorie n° CATEGORIE (sa RowData), PropertyValue remplacé ou non.
CATEGORIE, EQUIPE = 0, 0
SOURCE_NUMERO = "team.UniqueId"      # seule donnée « numéro » lisible sur la page (v17 : Alessandria 1102, moteur 910)
VAR_NUMERO = "uipickernumero"        # numéro du moteur trouvé dans la table (variable du bouton), copié dans PropertyValue
HORS_TABLE = -1                      # numéro des équipes hors table (jeunes / réserves créés par la partie : numéros
                                     # propres à chaque partie) : v25 : bouton caché pour elles (OP_DIFFERENT)
DELAI = 0.4                      # s après le clic (v28 ; 0,5 avant) : la fenêtre (ouverte en 0,33 s) repart de ses réglages à l'ouverture
ECART_BAS = 8                    # px sous les boutons
ECART_BOUTONS = 8                # px entre les boutons
OP_DIFFERENT = 5                 # opérateur FM « ≠ » (ComparisonOperator)
# =====================================================================================================

VERSION = 43  # v42 vue : marche (grosse partie), « paraît plus lent » -> v43 : grosse partie = bas de la dichotomie
              # 39 000 (v36) ; le reste = v36 (1 attente de 0,08 s par essai) ;
              # v42 (demande du joueur) : option de l'app « grosse partie » (rapide : une attente par essai) /
              # « petite partie » (2 attentes, comme v41) ;
              # v40 vue : remarche partout, petite partie comprise, mais « beaucoup plus lent » -> v41 : relecture
              # 0,03 s, bas de la dichotomie 20 000 ;
              # v39 vue : fenêtre ouverte, reste « Choisir adversaire » -> cause : le « déjà la bonne équipe ? » de
              # la v36 compare l'adversaire de la fenêtre, VIDE quand aucun n'est choisi -> comparaison fausse, rien
              # envoyé (v36 vue seulement avec un adversaire déjà là) -> v40 : étape 0 sans ce test ;
              # v38 vue : toujours rien -> v39 = réglages de la v36 exactement (pour retrouver ce qui marchait, puis
              # changer un réglage à la fois) ;
              # v37 vue : plus rien ne part (même les clubs) -> v38 : moins d'étapes jeunes (variables du bouton
              # 102 -> 86) ;
              # v36 vue : niquel, sauf partie PL seule (Chelsea U21 / U19 -> Monmouth U19) : relu trop tôt (sonde :
              # Monmouth = n° 39 001) -> v37 : plus de fusion, relecture 0,06 s ; clubs : 6 envois au plus ;
              # v36 (demande du joueur) : rien d'envoyé si la fenêtre a déjà la bonne équipe (clubs : arrêt dès
              # qu'elle est juste, plus de corrections inutiles) ;
              # v34 vue : au 2e clic, mauvais adversaire (Dinar Tatarlı Spor) ; le joueur : « ça repart de mon choix »
              # -> vrai : l'étape où la recherche avait trouvé restait allumée et repartait avec la nouvelle -> v35 :
              # le clic éteint toutes les étapes ; fusion des attentes remise (v33 : « une fois sur 2 » = même cause) ;
              # v33 vue : Wolfsburg U19 OK partout ; Liverpool U21 (partie Wolfsburg) -> Marlow U18 une fois sur 2
              # -> v34 : plus de fusion des attentes (v30) ;
              # v32 vue : Vallauris U19 aussi (autre partie : Rés. Chaumont FC) ; D1 / D2 anglaises, France OK -> v33 :
              # dichotomie pour les équipes créées par la partie (voir J_BAS), fusion des attentes remise ;
              # v31 vue : partie Wolfsburg, Wolfsburg U19 -> Arsenal (Sarandí) U20 ou Vallauris U19 (change d'un clic à
              # l'autre) -> v32 = v30 (2 attentes par essai) ;
              # v30 vue : encore plus rapide, juste -> v31 (essai) : jeunes, une seule attente par essai (J_FUSION ;
              # si ça rate : J_FUSION = False = v30) ;
              # v29 vue : 2-3 s, « beaucoup plus rapide », juste -> v30 : attentes encore réduites (jeunes 0,03 / 0,05,
              # clubs 0,06 / 0,06) ;
              # v28 vue : marche, « pas vraiment plus rapide » -> v29 : attentes encore réduites (jeunes 0,06 / 0,08,
              # clubs 0,1 / 0,1) ;
              # v27 vue : MARCHE (jeunes), mais lent -> v28 : départ plus haut, pas plus grand, attentes plus courtes
              # (clubs aussi : DELAI 0,4 s, relecture 0,2 s, envoi 0,15 s) ;
              # v26 vue : correction MARCHE partout (Wolfsburg, Arsenal, D4 espagnole) -> v27 : + bouton des équipes
              # jeunes / réserves (recherche du bloc des jeunes, voir J_DEPART) ;
              # v25 vue : sur la partie Wolfsburg, Wolfsburg -> VfB Leipzig (base de la partie ≠ table) -> v26 (go du
              # joueur) : correction automatique, 2 envois de plus d'après l'adversaire réel relu (voir ETAPES) ;
              # v24 vue : les C ne font rien ; le moteur (fenêtre d'amical, lu en entier) ne prend l'adversaire que par
              # son numéro -> v25 (demande du joueur) : bouton A seul (table = équipes de la base), caché hors table,
              # plus de B / C ni de textes de contrôle ;
              # v23 vue : B remarche, MAIS seulement l'affichage (indemnité / commentaires = l'adversaire réel du moteur,
              # celui de A ou Algérie) -> v24 : + 3 boutons C (EventFmxDoAction 44 + ActionID « choisir pour un amical »
              # sur team / team.TeamContainer) ;
              # v21 / v22 vues : B seul (sans A ni textes) -> plus rien, même sur la partie Wolfsburg -> v23 : la v20
              # remise à l'identique (A + B + textes), pour retrouver ce qui fait marcher B ;
              # v19 vue : MARCHE (clubs de la base, Paris SG 2…), U19 -> Algérie ; mais la base change d'une partie à
              # l'autre (autre partie : 68 clubs en moins, 91 en plus -> numéros décalés dès le n° 594) -> v20 : 2e bouton
              # B sans numéro : team copié dans human.team.ArrangeFriendly.Team (l'adversaire affiché par la fenêtre) ;
              # v18 vue : l'envoi MARCHE, mais écart pas constant (Reggiana 1164 -> 965) ; sonde « amical table » : numéros
              # de la base (0-39900) identiques sur 2 parties -> v19 : table UniqueId -> numéro (DataCollection de FM
              # inutilisée réécrite, lue par la fonction FM BindMapAndSetToDestination), plus de soustraction ;
              # v17 vue : seul team.UniqueId répond (Alessandria 1102 ; moteur 910) -> v18 : envoi de UniqueId − 192
              # (écart constant ?) ;
              # v16 vue : texte du haut vide (DatabaseReferenceField pas lisible), uipickernumero = 0 -> v17 : 13 données
              # candidates affichées avec leur nom (Index, ID, DatabaseRecord…) : laquelle = 910 sur Alessandria ? ;
              # v15 vue : plus de crash, mais Algérie (numéro 0) -> v16 : sous le bouton, 2 textes de contrôle
              # (team.DatabaseReferenceField lu / uipickernumero calculé) ;
              # v14 vue : crash en ouvrant Infos club (NullReference dans BindNode : entrées de la fonction réécrite
              # rattachées à l'ancien m_id) -> v15 : tout rattaché au m_id de la cible ;
              # v13 vue : Tynset ; sonde : la fenêtre veut le numéro du moteur (Alessandria 910 marqué à la main -> OK),
              # FM l'a dans team.DatabaseReferenceField + 0x18000000 -> v14 : soustraction par une fonction FM réécrite ;
              # v12 vue : team -> Algérie -> v13 : team.Club.UniqueId (idée du joueur : « l'id du club ») ;
              # v11 vue : l'envoi d'une vraie équipe MARCHE (Alessandria) ; PropertyValue = team.UniqueId -> Tynset
              # (UniqueId ≠ numéro du moteur) -> v12 : PropertyValue = team (l'équipe elle-même) ;
              # v10 vue : tout Algérie. Sonde du mod : les lignes du haut sont des CATÉGORIES (PropertyValue vide -> 0
              # -> Algérie), les équipes sont dans leur ChildList -> v11 : une vraie équipe (RowData d'une sous-ligne) ;
              # v9 vue : tout Algérie (même des lignes du menu intactes) ; la fenêtre range le choix dans une variable
              # de VALEUR (selectedteam, Null), pas de référence DisplayValuePair -> v10 : variable de valeur ;
              # v8 vue : encore Algérie -> v9 : lignes n° 0 et 3 du menu, telles quelles (l'envoi d'une ligne
              # marche-t-il ?) et n° 3 + numéro (la copie dans PropertyValue marche-t-elle ?) ;
              # v7 vue : encore Algérie, même la ligne non touchée -> ligne vide (LISTE vide tant que la fenêtre n'est
              # pas ouverte ?) -> v8 : la ligne est prise DELAI s après le clic (BindingSetter relié à ce moment) ;
              # v1 : équipe envoyée -> Algérie ; v2 : numéro envoyé -> Algérie ; v3 / v4 : menus d'équipe (cachés) ;
              # v5 : ligne DisplayValuePair déclarée + PropertyValue copié -> 2 boutons gris en jeu ;
              # v6 : 4 boutons : ligne vide = gris ; dernière ligne du menu = cliquable mais Algérie + date 1/1/1900
              # (la fenêtre repart de ses réglages APRÈS notre envoi) -> v7 : envoi DELAI s après le clic
MODELE = "ClubInfoReportBlock"
SOURCE_BOUTON = "CalendarHeaderSeasonBlock"          # son #ArrangeFriendly (texte FM traduit « Organiser amical ») et
                                                     # son BindingSetter à variables DisplayValuePair (firstItem)
SOURCE_VISIBLE = ("CalendarDay_block", "GradientHeaderVisible")   # SIVisible direct de FM (comme kinito_vacances_jour)
SOURCE_DELAI = "GameCreationGameSummaryScreen"       # son SIDelayEvent sans enfant (comme kinito_vacances_jour)
FENETRE = "78a354d56ca929843bf55c2bdb4ec63e"         # ArrangeFriendlyCard (ouverte par le calendrier avec team)
ID_ADVERSAIRE = 0x79307538                           # action FM « adversaire choisi » (SelectedTeam du menu)
TYPE_LIGNE = 1513318467                              # DisplayValuePair (type des lignes du menu de la fenêtre)
VARIABLE = "uipickeradversaire"                      # la sous-ligne d'équipe (sa RowData est envoyée)
VAR_CATEGORIE = "uipickercategorie"                  # la catégorie du menu qui la contient
DRAPEAU = "uipickerenvoi"                            # vrai entre le clic et l'envoi (variable locale de chaque bouton)
DELAI_ENVOI = 0.06                                   # s entre la prise de la ligne (et les calculs) et son envoi
# v26 : correction automatique (la base de la partie peut différer de la table : numéros décalés). Après chaque envoi,
# l'adversaire réel du moteur (OPP_UID) est relu, son rang dans la table (VAR_RANG) comparé à celui de l'équipe voulue
# (VAR_NUMERO) : numéro suivant = numéro envoyé − (VAR_RANG − VAR_NUMERO) (les numéros suivent l'ordre des UniqueId,
# le décalage change rarement). ETAPES envois en tout (1er = la table). Calculs : fonction FM inutilisée réécrite en
# « a − b » (FN_CIBLE). Envoi seulement si 0 ≤ numéro ≤ BORNE (hors limites = crash du moteur).
DELAI_DEJA_LA = 0.01             # v40 : arrêt « déjà la bonne équipe » de l'étape 0, avant son envoi
ETAPES = 6                       # v40 : 6 (v37 ; v39 : 3) ; « plus rien ne partait » venait du test « déjà là » ; partie PL seule : base bien plus petite (jeunes dès le n° 33 000)
                                 # -> décalage qui change, plus de corrections ; arrêt dès que c'est juste (v36)
DELAI_RELIRE = 0.06                                  # s entre un envoi et la relecture de l'adversaire (v30)
BORNE = 40500                                        # base = 0-39 900 dans toutes les parties vues (≥ 44 000 équipes)
OPP_UID = f"{EQUIPE_JOUEUR}.ArrangeFriendly.Team.UniqueId"
VAR_COURANT = "uipickercourant"                      # dernier numéro envoyé
VAR_RANG = "uipickerrang"                            # rang dans la table de l'adversaire réel
VAR_ECART = "uipickerecart"                          # VAR_RANG − VAR_NUMERO
VAR_SUIVANT = "uipickersuivant"                      # VAR_COURANT − VAR_ECART
ETAPE = "uipickeretape{}"                            # vrai : étape n (prise de la ligne, calcul, envoi)
RELIRE = "uipickerrelire{}"                          # vrai : attente avant l'étape n
OP_SUP_EGAL, OP_INF_EGAL, OP_EGAL = 3, 1, 2          # ComparisonOperator de FM (≥, ≤, =)
# v27 : équipes jeunes / réserves (hors table, UID ≥ UID_JEUNES). Elles sont tout au bout de la liste des équipes, en
# un bloc où UID = n° + K (K propre à la partie), après les équipes créées par la partie (UID croissants, avec des trous).
# La fin de la liste n'est pas lisible (n° au-delà = crash) : on part de J_DEPART (valide partout), on monte de J_PAS
# tant que l'écart UID − n° change d'un relevé à l'autre (équipes créées) ; 2 relevés de même écart = dans le bloc des
# jeunes -> saut exact n° + (UID voulu − UID relu). Arrêt dès que l'adversaire relu est l'équipe voulue.
# Sûr si le bloc des jeunes compte ≥ 2 × J_PAS équipes (vu : 2 500 à 64 000).
UID_JEUNES = 2000000000
# v28 (« plus vite ») : départ 42 000 (toutes les listes vues ≥ 44 000), pas de 1 200 (bloc des jeunes ≥ 2 400 ;
# vu : 2 500 au moins), relecture 0,15 s (v27 : 40 500, 1 000, 0,2 s)
J_DEPART, J_PAS, J_ETAPES = 42000, 1200, 26          # jusqu'au n° 72 000 (début des jeunes vu : 42 000 à 60 000)
J_DELAI_RELIRE, J_DELAI_ENVOI = 0.03, 0.05           # v41 : 0,03 (v40 : 0,06, « beaucoup plus lent » ; v30 : 0,03
                                                     # sans fusion = juste partout) ; v30 (v29 : 0,06 / 0,08 = 2-3 s ; v28 : 0,15 / 0,1)
# v31 (essai) : une seule attente par essai : l'envoi allume directement l'étape suivante (plus d'étape « relire ») ;
# ses calculs se relient tout de suite et doivent suivre l'adversaire relu quand il change. Retour v30 : J_FUSION = False
import options  # noqa: E402
OPTION_PARTIE = "amical_partie"                      # v42 : « grosse » (rapide, fusion) / « petite » (2 attentes)
PETITE_PARTIE = options.get(OPTION_PARTIE) == "petite"
J_FUSION = not PETITE_PARTIE                         # v42 : fusion pour les grosses parties (v35 / v36 : juste) ;
                                                     # v40 : False (comme v37) ; v37 / v38 False : partie PL seule, Chelsea U21 -> Monmouth U19 (n° 39 001,
                                                     # juste au-dessus du bas) : chaque relevé lu AVANT la mise à jour
                                                     # (les calculs ne se refont pas quand l'adversaire change) -> tous
                                                     # « trop loin » -> 2 attentes par essai, relecture 0,06 s
J_ETAPES = 32                                        # v40 : 32 (v39 : 40) ; v38 : 40 -> 32 (simulé : 26 au plus). v37 = plus rien ne
                                                     # partait (clubs compris) : 102 variables dans le BindingSetter du
                                                     # bouton (v36 : 96) -> limite de FM (100 ?) supposée
J_DELAI_FUSION = 0.08                                # attente unique (= 0,03 + 0,05 de la v30)
VAR_DEPART, VAR_MOINS_PAS = "uipickerdepart", "uipickermoinspas"
VAR_ECART_UID = "uipickerecartuid"                   # UID relu − n° envoyé (= K dans le bloc des jeunes)
VAR_ECART_PREC = "uipickerecartprec"                 # le même au relevé précédent
VAR_RESTE = "uipickerreste"                          # UID relu − UID voulu
J_ETAPE, J_RELIRE = "uipickerjetape{}", "uipickerjrelire{}"
# v33 : équipes créées par la partie (ex. Wolfsburg U19 de la vraie Ligue U19 : UID dans la zone à trous, avant le bloc
# des jeunes) -> le saut retombait à côté (Vallauris U19, Rés. Chaumont). Maintenant : dès qu'un relevé dépasse l'équipe
# voulue, dichotomie entre le dernier n° en dessous (VAR_BAS, au départ J_BAS : base, UID < 2e9 < voulu) et le dernier
# au-dessus (VAR_HAUT) : jamais hors de n° déjà vus. Moitié d'un écart = table (clé J_DECALAGE_MOITIE + écart -> écart / 2,
# ajoutée à la table des UniqueId, après eux).
J_BAS = 20000 if PETITE_PARTIE else 39000   # v43 : grosse partie = 39 000 comme v36 (1 envoi de moins) ; v41 : 20 000 (v40 : 0 ; v36 : 39 000) ; partie PL seule : base ≈ 33 000 -> 20 000
                                 # reste dans la base partout (UID < 2e9), 1 à 2 envois de moins ; partie PL seule : jeunes dès le n° 33 000 (n° 0 = Algérie,
                                 # UID 5 : toujours sous l'équipe voulue)
J_DECALAGE_MOITIE, J_MOITIE_MAX = 2100000000, 65535
VAR_BAS, VAR_HAUT, VAR_BAS0 = "uipickerbas", "uipickerhaut", "uipickerbas0"
VAR_MOINS_UN, VAR_ZERO, VAR_MOINS_DECALAGE = "uipickermoinsun", "uipickerzero", "uipickermoinsdecalage"
VAR_LARGEUR, VAR_CLE, VAR_MOITIE = "uipickerlargeur", "uipickercle", "uipickermoitie"
OP_INF, OP_SUP = 0, 4
PREFIXE = "UIPickerAmical"
NOM_RACINE = f"{PREFIXE}-v{VERSION}{'p' if PETITE_PARTIE else 'g'}"   # l'option change le repère (réapplication)
MENU = os.path.join(nb.AA, "gamemodules_assets_gameworld.bundle")
DONNEES_MENU = "ClubEntitySubtabs"
MARKER = os.path.join(backup.BACKUP_DIR, "club_amical.actif")
# v14-v18 : fonction FM inutilisée réécrite en soustraction (UIPickerSoustraction) : remise d'origine à l'application
FONCTIONS = os.path.join(nb.AA, "ui-visualfunctions_assets_all.bundle")
FN_CIBLE = "1cbe40249ce6ba14cbe944da282e7479"        # BindAndSetValueToDestination (inutilisée)
NOM_CIBLE = "BindAndSetValueToDestination"
MODELE_FN = "BindListItemsCountWithOffsetToDestination"   # son graphe recopié (v26 : « a − b »)
NOM_FN = f"UIPickerDifference-v{VERSION}"
# v19 : la table UniqueId -> numéro du moteur. Une DataCollection de FM que le jeu n'utilise nulle part (guid cité dans
# aucun objet de aa\, 2026-11-12) réécrite : clé = UniqueId (croissants), colonne COLONNE = numéro ; FM y prend la 1re
# ligne de clé ≥ la valeur, dernière clé 2147483647 -> HORS_TABLE. Lue par la fonction FM FN_TABLE (valeur -> table ->
# colonne -> destination), appel recopié de SOURCE_FN_TABLE. Ce script est le seul écrivain de ce bundle.
TABLE = os.path.join(nb.AA, "ui-datacollections_assets_all.bundle")
DC_CIBLE = "1d4964367643c22439133c09766afd63"        # NegativeColourDataCollection (inutilisée)
NOM_DC_CIBLE = "NegativeColourDataCollection"
NOM_DC = f"UIPickerEquipes-v{VERSION}"
COLONNE = "Numero"
DONNEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "club_amical_equipes.txt")
FN_TABLE = "88249b42c2ed8084db2a4f2a79a92903"        # BindMapAndSetToDestination
SOURCE_FN_TABLE = "FMMenuDropdownRow"                # un modèle de FM qui l'appelle (args : table, colonne, valeur,
                                                     # destination, forcer)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


# ---------- l'événement : ouvrir la fenêtre, remplir la ligne, l'envoyer ----------
def _corps(ev):
    """corps d'une action seule (événement [1,1,1,1, 1, longueur, corps])"""
    n = struct.unpack_from("<i", bytes(ev), 5)[0]
    return bytes(ev[9:9 + n])


def _appel(objet, argument):
    return bytes([27, 222, 7, 0, 1]) + ee._bloc(ee._texte(objet)) + ee._bloc(ee._texte(argument)) \
        + struct.pack("<I", ID_ADVERSAIRE)


def _copie(source, destination):
    return bytes([217, 15, 225, 87, 1]) + ee._bloc(ee._texte(source)) + ee._bloc(ee._texte(destination)) \
        + bytes([1, 0])


def _liste(actions):
    out = bytes([1, 1, 1, len(actions)])
    for c in actions:
        out += b"\x01" + struct.pack("<i", len(c)) + c
    return list(out)


def evenement_clic(eteindre=()):
    """ouvrir la fenêtre d'amical, éteindre les étapes restées allumées (v35 : une recherche finie avant sa dernière
    étape laissait la sienne allumée -> au clic suivant, elle repartait en même temps que la nouvelle), allumer DRAPEAU
    (le SIDelayEvent part)"""
    return _liste([_corps(ee.evenement_ecran(FENETRE, [("team", EQUIPE_JOUEUR)]))]
                  + [_copie("const.False", d) for d in eteindre] + [_copie("const.True", DRAPEAU)])


def evenement_bascule(allumer, eteindre):
    """fin d'une attente : allumer (l'étape suivante se relie), eteindre"""
    return _liste([_copie("const.True", allumer), _copie("const.False", eteindre)])


def evenement_envoi(valeur, etape, suivant, apres=(), avant=()):
    """équipe prise : son PropertyValue remplacé par valeur, sa RowData envoyée comme le menu de la fenêtre, (copies
    avant,) valeur gardée dans VAR_COURANT (+ copies apres) ; etape éteinte, suivant (attente de la relecture) allumé"""
    return _liste([_copie(valeur, f"{VARIABLE}.RowData.PropertyValue"),
                   _appel(f"{EQUIPE_JOUEUR}.ArrangeFriendly", f"{VARIABLE}.RowData")]
                  + [_copie(s, d) for s, d in avant] + [_copie(valeur, VAR_COURANT)]
                  + [_copie(s, d) for s, d in apres] + [_copie("const.False", etape)]
                  + ([_copie("const.True", suivant)] if suivant else []))


def _verifier_evenement():
    """le bouton du calendrier refait à l'identique (ouvrir la fenêtre avec team) ; le choix de l'adversaire refait
    comme le menu de la fenêtre (friendly | SelectedTeam)"""
    calendrier = [1, 1, 1, 1, 1, 99, 0, 0, 0] + list(_corps(ee.evenement_ecran(FENETRE, [("team", "team")])))
    attendu_cal = [1, 1, 1, 1, 1, 99, 0, 0, 0, 211, 101, 102, 7, 2, 11, 0, 0, 0, 1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0, 47, 0,
                   0, 0, 1, 0, 1, 1, 1, 32] + list(FENETRE.encode()) + [1, 0, 3, 0, 0, 0, 1, 1, 0, 1, 1, 1, 19, 0, 0,
                   0, 1, 1, 4] + list(b"team") + [7, 0, 0, 0, 1, 1, 4] + list(b"team") + [0, 0, 0]
    attendu_menu = bytes([27, 222, 7, 0, 1, 11, 0, 0, 0, 1, 1, 8]) + b"friendly" + bytes([15, 0, 0, 0, 1, 1, 12]) \
        + b"SelectedTeam" + bytes([56, 117, 48, 121])
    return calendrier == attendu_cal and _appel("friendly", "SelectedTeam") == attendu_menu


# ---------- le bouton ----------
def _parent_id(t, rid):
    """clone ne refait que m_Parent : l'identifiant du parent aussi (composants seulement)"""
    p = t.parent[rid]
    if "m_ParentId" in t.elem(rid):
        t.elem(rid)["m_ParentId"] = t.elem(p).get("m_Id", t.elem(rid)["m_ParentId"])


def construire(t, src, mx, pieces, fn_table, fn_rang, fn_moitie):
    bouton = first(src, lambda r: typ(src, r) == "SIButton" and src.name(r) == "ArrangeFriendly")
    if bouton is None:
        return ["bouton « Organiser amical » du calendrier introuvable"]
    reglage = first(src, lambda r: typ(src, r) == "BindingSetter" and any(
        v.get("m_name") == "firstItem" and (v.get("m_type") or {}).get("id") == TYPE_LIGNE
        for v in src.sd(r).get("ReferenceVariables") or []))
    if reglage is None:
        return ["variables DisplayValuePair du calendrier introuvables"]
    # sa fonction « élément d'une liste » (21ee6b43 : liste, destination, n°, depuis la fin, ?), celle de firstItem
    modele_fn = None
    for f in src.sd(reglage).get("BindFunction") or []:
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        chem = [a for a in args if a[0].endswith(b"BindingPath]")]
        if len(chem) == 2 and chem[1][1].endswith(b"firstItem") and len(args) == 5 \
                and args[2][0].endswith(b"Int32VisualArg") and args[3][0].endswith(b"BooleanVisualArg"):
            modele_fn = f
    if modele_fn is None:
        return ["fonction « élément d'une liste » du calendrier introuvable"]

    def ligne_n(liste, destination, n):
        f = copy.deepcopy(modele_fn)
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a, c in zip([a for a in args if a[0].endswith(b"BindingPath]")], (liste, destination)):
            a[1] = b"\x01" + _enc_varint(len(c)) + c.encode()
        args[2][1], args[3][1] = struct.pack("<i", n), b"\x00"
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        return f

    def difference(a, b, destination):
        """appel de la fonction réécrite FN_CIBLE (entrées : a, b, destination, forcer) : a − b -> destination"""
        f = copy.deepcopy(modele_fn)
        f["m_target"]["m_guid"] = FN_CIBLE
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        chemin, booleen = args[0][0], args[3][0]
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(
            [[chemin, b"\x01" + _enc_varint(len(c)) + c.encode()] for c in (a, b, destination)] + [[booleen, b"\x00"]])
        return f
    s_cmp, cmp = visible_model()   # SIVisible de FM « chemin <op> entier » (bouton caché hors table)
    if cmp is None:
        return ["modèle de comparaison FM introuvable"]
    # les 2 endroits où FM affiche l'équipe choisie (team) : onglets (BindingSetter) et menu déroulant (BindingRemapper)
    zones = [t.parent[r] for r in t.walk() if t.elem(r).get("m_TemplateAlias") == "NationAndClubInfoTeamsBlock"]
    if len(zones) != 2:
        return [f"équipe affichée de la page Infos du club introuvable ({len(zones)} endroit(s) au lieu de 2)"]
    for i, z in enumerate(zones):
        b = make_binding(mx.s_vis.sd(mx.vis)["Binding"], OP_DIFFERENT, ["team.UniqueId", f"{EQUIPE_JOUEUR}.UniqueId"])
        vis = new_visible(t, mx.s_vis, mx.vis, z, 0, f"{NOM_RACINE}-{i}", b, ["row-direction-normal"])
        t.sd(vis)["name_UxmlAttributeFlags"] = 1
        t.styles.style(t, vis, {"flex-shrink": 0, "margin-bottom": ECART_BAS})
        def vis_cmp(parent, nom, op, chemin, valeur):
            v = new_visible(t, s_cmp, cmp, parent, None, nom, make_binding(s_cmp.sd(cmp)["Binding"], op, [chemin], valeur))
            t.sd(v)["name_UxmlAttributeFlags"] = 1
            return v

        def vis_2(parent, nom, op, a, b):
            v = new_visible(t, mx.s_vis, mx.vis, parent, None, nom, make_binding(mx.s_vis.sd(mx.vis)["Binding"], op, [a, b]))
            t.sd(v)["name_UxmlAttributeFlags"] = 1
            t.styles.style(t, v, {"position": "absolute", "width": 0, "height": 0})
            return v

        def calcul(parent, nom, fonction, variable, defaut):
            s = _reglage(t, reglage, src, parent, nom, [fonction], [], [], [])
            _entier(t, s, variable, defaut)
            return s

        def lignes(parent, nom):
            gc = _reglage(t, reglage, src, parent, f"{PREFIXE}-categorie-{nom}",
                          [ligne_n(LISTE, VAR_CATEGORIE, CATEGORIE)], [], [], [], [VAR_CATEGORIE])
            return _reglage(t, reglage, src, gc, f"{PREFIXE}-ligne-{nom}",
                            [ligne_n(f"{VAR_CATEGORIE}.ChildList", VARIABLE, EQUIPE)], [], [], [], [VARIABLE])

        def bouton_dans(parent, nom, eteindre):
            x = t.clone(bouton, parent, src=src)
            t.styles.copy_from(src.styles, t, x)
            sd = t.sd(x)
            sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1
            sd["Events"]["m_bytes"] = evenement_clic(eteindre)

        for k in range(1):
            # BindingSetter de FM (enfants retirés) : drapeaux des étapes, VAR_NUMERO (table), VAR_COURANT…
            etapes, relire = [ETAPE.format(e) for e in range(ETAPES)], [RELIRE.format(e) for e in range(1, ETAPES)]
            jetapes = [J_ETAPE.format(e) for e in range(J_ETAPES)]
            jrelire = [J_RELIRE.format(e) for e in range(1, J_ETAPES)]
            g = _reglage(t, reglage, src, vis, f"{PREFIXE}-bouton-zone-{i}-{k}", [copy.deepcopy(fn_table)],
                         [DRAPEAU] + etapes + relire + jetapes + jrelire, [], [])
            for n, v in ((VAR_NUMERO, HORS_TABLE), (VAR_COURANT, -1), (VAR_DEPART, J_DEPART), (VAR_MOINS_PAS, -J_PAS),
                         (VAR_ECART_PREC, 0), (VAR_BAS, J_BAS), (VAR_BAS0, J_BAS), (VAR_HAUT, -1), (VAR_MOINS_UN, -1),
                         (VAR_ZERO, 0), (VAR_MOINS_DECALAGE, -J_DECALAGE_MOITIE)):
                _entier(t, g, n, v)
            t.styles.style(t, g, {"flex-shrink": 0})
            # ----- équipes de la table (VAR_NUMERO ≠ HORS_TABLE) -----
            connu = vis_cmp(g, f"{PREFIXE}-connu-{i}", OP_DIFFERENT, VAR_NUMERO, HORS_TABLE)
            t.styles.style(t, connu, {"flex-shrink": 0})
            bouton_dans(connu, f"{PREFIXE}-bouton-{i}-{k}", etapes + relire)
            # DRAPEAU > DELAI s : étape 0 (fenêtre ouverte, LISTE remplie)
            _attente(t, pieces, connu, DRAPEAU, f"{PREFIXE}-attente-{i}-{k}", DELAI,
                     evenement_bascule(etapes[0], DRAPEAU))
            # ----- équipes jeunes / réserves (hors table, UID ≥ UID_JEUNES) : recherche du bloc des jeunes -----
            jeune = vis_cmp(vis_cmp(g, f"{PREFIXE}-horstable-{i}", OP_EGAL, VAR_NUMERO, HORS_TABLE),
                            f"{PREFIXE}-jeune-{i}", OP_SUP_EGAL, "team.UniqueId", UID_JEUNES)
            t.styles.style(t, jeune, {"flex-shrink": 0})
            bouton_dans(jeune, f"{PREFIXE}-bouton-jeune-{i}-{k}", jetapes + jrelire)
            _attente(t, pieces, jeune, DRAPEAU, f"{PREFIXE}-jattente-{i}-{k}", DELAI,
                     evenement_bascule(jetapes[0], DRAPEAU))
            for e in range(J_ETAPES):
                nom = f"j{i}-{k}-{e}"
                suivant = (jetapes[e + 1] if J_FUSION else jrelire[e]) if e < J_ETAPES - 1 else None
                attente = J_DELAI_FUSION if J_FUSION else J_DELAI_ENVOI
                if e and not J_FUSION:
                    _attente(t, pieces, jeune, jrelire[e - 1], f"{PREFIXE}-relire-{nom}", J_DELAI_RELIRE,
                             evenement_bascule(jetapes[e], jrelire[e - 1]))
                p = _visible(t, pieces, jeune, jetapes[e], f"{PREFIXE}-etape-{nom}")
                if not e:   # 1er envoi : J_DEPART ; bornes de la dichotomie remises à zéro (v36 : rien si la fenêtre
                    # a déjà la bonne équipe, gardée du clic précédent)
                    # v40 : pas de « ≠ » ici : fenêtre sans adversaire = UID vide, toute comparaison fausse -> rien
                    # ne partait (v36-v39) ; l'arrêt « déjà là » éteint l'étape avant l'envoi (attente plus courte)
                    _delai(t, pieces, vis_2(p, f"{PREFIXE}-dejala-{nom}", OP_EGAL, OPP_UID, "team.UniqueId"),
                           f"{PREFIXE}-fin-{nom}", DELAI_DEJA_LA, _liste([_copie("const.False", jetapes[e])]))
                    _delai(t, pieces, lignes(p, nom), f"{PREFIXE}-envoi-{nom}", J_DELAI_ENVOI,
                           evenement_envoi(VAR_DEPART, jetapes[e], suivant,
                                           apres=[(VAR_BAS0, VAR_BAS), (VAR_MOINS_UN, VAR_HAUT), (VAR_ZERO, VAR_ECART_PREC)]))
                    continue
                p = calcul(p, f"{PREFIXE}-ecartuid-{nom}", difference(OPP_UID, VAR_COURANT, VAR_ECART_UID),
                           VAR_ECART_UID, -1)
                p = calcul(p, f"{PREFIXE}-reste-{nom}", difference(OPP_UID, "team.UniqueId", VAR_RESTE), VAR_RESTE, 0)
                # trouvé : l'étape s'éteint (sinon un choix fait ensuite à la main dans la fenêtre la relancerait)
                fini = vis_2(p, f"{PREFIXE}-trouve-{nom}", OP_EGAL, OPP_UID, "team.UniqueId")
                _delai(t, pieces, fini, f"{PREFIXE}-fin-{nom}", J_DELAI_ENVOI, _liste([_copie("const.False", jetapes[e])]))
                p = vis_2(p, f"{PREFIXE}-pastrouve-{nom}", OP_DIFFERENT, OPP_UID, "team.UniqueId")   # sinon : fini
                gl = lignes(p, nom)

                def cas(parent, suffixe, calculs, garder):
                    """calculs : [(a, b, variable)] enchaînés (le dernier = n° suivant) ; garder : copie de VAR_COURANT
                    dans VAR_BAS / VAR_HAUT avant l'envoi"""
                    q = parent
                    for n_c, (a, b, var) in enumerate(calculs):
                        if var == VAR_MOITIE:   # moitié : table (clé = écart + J_DECALAGE_MOITIE)
                            q = _reglage(t, reglage, src, q, f"{PREFIXE}-moitie-{nom}-{suffixe}", [copy.deepcopy(fn_moitie)],
                                         [], [], [])
                            _entier(t, q, VAR_MOITIE, 0)
                        else:
                            q = calcul(q, f"{PREFIXE}-calc-{nom}-{suffixe}-{n_c}", difference(a, b, var), var, -1)
                    q = vis_cmp(q, f"{PREFIXE}-borne-{nom}-{suffixe}", OP_SUP_EGAL, VAR_SUIVANT, 0)
                    t.styles.style(t, q, {"position": "absolute", "width": 0, "height": 0})
                    _delai(t, pieces, q, f"{PREFIXE}-envoi-{nom}-{suffixe}", attente,
                           evenement_envoi(VAR_SUIVANT, jetapes[e], suivant, apres=[(VAR_ECART_UID, VAR_ECART_PREC)],
                                           avant=[(VAR_COURANT, garder)]))

                def milieu(bas, haut):
                    """n° suivant = haut − (haut − bas) / 2 (moitié lue dans la table)"""
                    return [(haut, bas, VAR_LARGEUR), (VAR_LARGEUR, VAR_MOINS_DECALAGE, VAR_CLE), (None, None, VAR_MOITIE),
                            (haut, VAR_MOITIE, VAR_SUIVANT)]
                # trop loin (UID relu > voulu) : ce n° devient le haut ; milieu entre le bas et lui
                trop = vis_cmp(gl, f"{PREFIXE}-trop-{nom}", OP_SUP, VAR_RESTE, 0)
                t.styles.style(t, trop, {"position": "absolute", "width": 0, "height": 0})
                cas(trop, "trop", milieu(VAR_BAS, VAR_COURANT), VAR_HAUT)
                # pas assez loin : ce n° devient le bas ; haut connu -> milieu ; sinon saut / pas
                court = vis_cmp(gl, f"{PREFIXE}-court-{nom}", OP_INF, VAR_RESTE, 0)
                t.styles.style(t, court, {"position": "absolute", "width": 0, "height": 0})
                connu_h = vis_cmp(court, f"{PREFIXE}-hautconnu-{nom}", OP_SUP_EGAL, VAR_HAUT, 0)
                t.styles.style(t, connu_h, {"position": "absolute", "width": 0, "height": 0})
                cas(connu_h, "milieu", milieu(VAR_COURANT, VAR_HAUT), VAR_BAS)
                sans_h = vis_cmp(court, f"{PREFIXE}-sanshaut-{nom}", OP_EGAL, VAR_HAUT, -1)
                t.styles.style(t, sans_h, {"position": "absolute", "width": 0, "height": 0})
                # même écart qu'au relevé précédent = bloc des jeunes : saut exact ; sinon : J_PAS plus loin
                for op, retrait in ((OP_EGAL, VAR_RESTE), (OP_DIFFERENT, VAR_MOINS_PAS)):
                    q = vis_2(sans_h, f"{PREFIXE}-cas-{nom}-{op}", op, VAR_ECART_UID, VAR_ECART_PREC)
                    cas(q, f"pas{op}", [(VAR_COURANT, retrait, VAR_SUIVANT)], VAR_BAS)
            # ----- étapes des équipes de la table -----
            for e in range(ETAPES):
                nom = f"{i}-{k}-{e}"
                if e:   # attente de la relecture (le moteur a pris l'envoi précédent)
                    _attente(t, pieces, connu, relire[e - 1], f"{PREFIXE}-relire-{nom}", DELAI_RELIRE,
                             evenement_bascule(etapes[e], relire[e - 1]))
                # étape e > BindingSetters reliés seulement maintenant : (calcul du numéro corrigé,) la catégorie de
                # LISTE > son équipe > envoi
                p = _visible(t, pieces, connu, etapes[e], f"{PREFIXE}-etape-{nom}")
                # v36 : la fenêtre a déjà la bonne équipe (clic précédent, ou corrigée) : on arrête là ; v40 : à
                # l'étape 0, pas de « ≠ » (fenêtre sans adversaire : comparaison fausse, rien ne partait), l'arrêt
                # éteint l'étape avant l'envoi (attente plus courte)
                _delai(t, pieces, vis_2(p, f"{PREFIXE}-dejala-{nom}", OP_EGAL, OPP_UID, "team.UniqueId"),
                       f"{PREFIXE}-fin-{nom}", DELAI_DEJA_LA if not e else DELAI_ENVOI,
                       _liste([_copie("const.False", etapes[e])]))
                if e:
                    p = vis_2(p, f"{PREFIXE}-pastrouve-{nom}", OP_DIFFERENT, OPP_UID, "team.UniqueId")
                valeur = VAR_NUMERO
                if e:
                    p = _reglage(t, reglage, src, p, f"{PREFIXE}-rang-{nom}", [copy.deepcopy(fn_rang)], [], [], [])
                    _entier(t, p, VAR_RANG, HORS_TABLE)
                    p = _reglage(t, reglage, src, p, f"{PREFIXE}-ecart-{nom}",
                                 [difference(VAR_RANG, VAR_NUMERO, VAR_ECART)], [], [], [])
                    _entier(t, p, VAR_ECART, 0)
                    p = _reglage(t, reglage, src, p, f"{PREFIXE}-suivant-{nom}",
                                 [difference(VAR_COURANT, VAR_ECART, VAR_SUIVANT)], [], [], [])
                    _entier(t, p, VAR_SUIVANT, -1)
                    valeur = VAR_SUIVANT
                for op, borne in ((OP_SUP_EGAL, 0), (OP_INF_EGAL, BORNE)):   # jamais hors limites
                    p = vis_cmp(p, f"{PREFIXE}-borne-{nom}-{op}", op, valeur, borne)
                    t.styles.style(t, p, {"position": "absolute", "width": 0, "height": 0})
                _delai(t, pieces, lignes(p, nom), f"{PREFIXE}-envoi-{nom}", DELAI_ENVOI,
                       evenement_envoi(valeur, etapes[e], relire[e] if e < ETAPES - 1 else None))
    return [f"bouton « Organiser amical » de FM au-dessus de l'équipe affichée (onglets et menu déroulant) : clic = "
            f"fenêtre d'amical, {DELAI} s plus tard l'équipe envoyée par son numéro (table), puis {ETAPES - 1} "
            f"corrections d'après l'adversaire réel relu ; équipes jeunes / réserves : recherche de leur bloc (départ "
            f"n° {J_DEPART}, pas de {J_PAS}, {J_ETAPES} envois au plus) ; caché sur ta propre équipe"]


def _entier(t, g, nom, valeur):
    t.sd(g)["ValueVariables"].append({"m_name": nom, "m_scopeValue": {"m_serializedData": f"Int|{valeur}|"}})


def _reglage(t, reglage, src, parent, nom, fonctions, booleens, lignes, valeurs, libres=()):
    """BindingSetter de FM (enfants retirés) : ses fonctions, variables booléennes (faux), DisplayValuePair, de
    valeur vides (Null, comme selectedteam de la fenêtre) et de référence sans type (comme 417 variables du jeu)"""
    g = t.clone(reglage, parent, src=src)
    for e in list(t.children(g)):
        t.remove(e)
    _parent_id(t, g)
    t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = [], -1
    sg = t.sd(g)
    sg["name"], sg["name_UxmlAttributeFlags"] = nom, 1
    sg["BindFunction"], sg["BindFunction_UxmlAttributeFlags"] = fonctions, 1
    sg["ValueVariables"] = [{"m_name": n, "m_scopeValue": {"m_serializedData": "Bool|0|"}} for n in booleens] \
        + [{"m_name": n, "m_scopeValue": {"m_serializedData": "Null"}} for n in valeurs]
    sg["ReferenceVariables"] = [{"m_type": {"id": TYPE_LIGNE}, "m_initToNull": 0, "m_name": n} for n in lignes] \
        + [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": n} for n in libres]
    sg["ValueVariables_UxmlAttributeFlags"] = sg["ReferenceVariables_UxmlAttributeFlags"] = 1
    return g


def _visible(t, pieces, parent, chemin, nom):
    """SIVisible direct de FM sur chemin (ne relie ses enfants aux données que visible), sans place"""
    v = t.clone(pieces.visible, parent, src=pieces.tv)
    for e in list(t.children(v)):
        t.remove(e)
    _parent_id(t, v)
    sv = t.sd(v)
    sv["name"], sv["name_UxmlAttributeFlags"] = nom, 1
    sv["Binding"]["m_kind"] = 1
    sv["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    sv["InvertDirectBinding"], sv["InvertDirectBinding_UxmlAttributeFlags"] = 0, 1
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    t.styles.style(t, v, {"position": "absolute", "width": 0, "height": 0})
    return v


def _delai(t, pieces, parent, nom, duree, evenement):
    """SIDelayEvent de FM : evenement duree s après sa liaison aux données"""
    dl = t.clone(pieces.delai, parent, src=pieces.td)
    t.styles.copy_from(pieces.td.styles, t, dl)
    _parent_id(t, dl)
    sl = t.sd(dl)
    sl["name"], sl["name_UxmlAttributeFlags"] = nom, 1
    sl["m_duration"], sl["m_duration_UxmlAttributeFlags"] = float(duree), 1
    sl["TransitionEvents"], sl["TransitionEvents_UxmlAttributeFlags"] = {"m_bytes": evenement}, 1
    return dl


def _attente(t, pieces, parent, chemin, nom, duree, evenement):
    return _delai(t, pieces, _visible(t, pieces, parent, chemin, nom), nom + "-delai", duree, evenement)


class Pieces:
    """SIVisible direct et SIDelayEvent de FM (les mêmes que kinito_vacances_jour, relus dans leurs modèles d'origine)"""
    def __init__(self):
        v = ouvrir(SOURCE_VISIBLE[0], depart_original=True)
        self.tv = v and v[3]
        self.visible = self.tv and first(self.tv, lambda r: self.tv.name(r) == SOURCE_VISIBLE[1]
                                         and typ(self.tv, r) == "SIVisible")
        d = ouvrir(SOURCE_DELAI, depart_original=True)
        self.td = d and d[3]
        self.delai = self.td and first(self.td, lambda r: self.td.elem(r).get("m_FullTypeName") == "FM.UI.SIDelayEvent"
                                       and not self.td.children(r))

    def ok(self):
        return None not in (self.visible, self.delai)


# ---------- la table UniqueId -> numéro du moteur (bundle des DataCollection de FM) ----------
def _objets(bundle):
    """{guid: objet} des assets du bundle (sa table m_Container), ou None"""
    if not os.path.exists(bundle):
        return None
    env = nb.env_of(bundle)
    par_pid = {o.path_id: o for o in env.objects}
    for o in env.objects:
        if o.type.name == "AssetBundle":
            return {k.lower(): par_pid.get(v["asset"]["m_PathID"]) for k, v in o.read_typetree()["m_Container"]}
    return None


def lire_donnees():
    """UniqueId des équipes de la base, rangés par numéro du moteur ([] si fichier absent ou pas croissant)"""
    if not os.path.exists(DONNEES):
        return []
    with open(DONNEES, encoding="utf-8") as f:
        uids = [int(x) for x in f if x.strip() and not x.startswith("#")]
    return uids if all(a < b for a, b in zip(uids, uids[1:])) else []


def poser_table():
    """réécrit la DataCollection DC_CIBLE (messages ; « introuvable » = rien fait)"""
    objs = _objets(TABLE)
    obj = objs and objs.get(DC_CIBLE)
    if obj is None:
        return ["table de FM à réécrire introuvable (bundle des tables changé par une mise à jour ?)"]
    actuel = obj.read_typetree()
    if actuel.get("m_Name") == NOM_DC:
        return []
    cible = hp.original(TABLE, obj) or actuel
    refs = (cible.get("references") or {}).get("RefIds") or []
    cle = next((r for r in refs if r["rid"] == (cible.get("m_keyColumn") or {}).get("rid")), None)
    if cible.get("m_Name") != NOM_DC_CIBLE or cle is None or cle["type"]["class"] != "IntDataSet":
        return [f"table FM {NOM_DC_CIBLE} introuvable (mise à jour de FM ?)"]
    uids = lire_donnees()
    if not uids:
        return ["liste des équipes (club_amical_equipes.txt) introuvable"]
    g = copy.deepcopy(cible)
    k, n = copy.deepcopy(cle), copy.deepcopy(cle)   # 2 colonnes d'entiers (même classe que la clé de FM)
    # v33 : après les UID, la table des moitiés (clé J_DECALAGE_MOITIE + x -> x // 2), précédée d'une clé « hors table »
    # (UID des jeunes / créées < J_DECALAGE_MOITIE − 1 -> HORS_TABLE)
    moities = list(range(J_MOITIE_MAX + 1))
    k["data"]["m_rows"] = uids + [J_DECALAGE_MOITIE - 1] + [J_DECALAGE_MOITIE + x for x in moities] + [2147483647]
    n["rid"] = max(r["rid"] for r in refs) + 1
    n["data"]["m_name"] = COLONNE
    n["data"]["m_rows"] = list(range(len(uids))) + [HORS_TABLE] + [x // 2 for x in moities] + [HORS_TABLE]
    g["m_columns"] = [{"rid": k["rid"]}, {"rid": n["rid"]}]
    g["references"]["RefIds"] = [k, n]
    g["m_Name"] = NOM_DC
    obj.save_typetree(g)
    nb._dirty.add(TABLE)
    return [f"table FM inutilisée {NOM_DC_CIBLE} réécrite : {len(uids)} équipes de la base (UniqueId -> numéro du "
            f"moteur), les autres -> {HORS_TABLE}"]


def retirer_table():
    objs = _objets(TABLE)
    obj = objs and objs.get(DC_CIBLE)
    if obj is None or not str(obj.read_typetree().get("m_Name", "")).startswith("UIPickerEquipes"):
        return []
    orig = hp.original(TABLE, obj)
    if orig is None:
        return [f"{NOM_DC_CIBLE} : pas de sauvegarde d'origine, laissée (utiliser la vérification des fichiers Steam)"]
    obj.save_typetree(orig)
    nb._dirty.add(TABLE)
    return [f"{NOM_DC_CIBLE} : remise d'origine"]


def fonction_table(src, source=SOURCE_NUMERO, destination=VAR_NUMERO):
    """appel de FN_TABLE recopié du modèle src : source -> table -> COLONNE -> destination (None si pas trouvé)"""
    for r in src.walk():
        if typ(src, r) != "BindingSetter":
            continue
        for f in src.sd(r).get("BindFunction") or []:
            if f["m_target"]["m_guid"] != FN_TABLE:
                continue
            args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
            if len(args) != 5 or not args[0][0].endswith(b"AssetReferenceVisualArg") \
                    or not args[1][0].endswith(b"StringVisualArg") or args[0][1][:1] != b"\x20" \
                    or not all(a[0].endswith(b"BindingPath]") for a in args[2:4]):
                continue
            f = copy.deepcopy(f)
            args[0][1] = args[0][1][:1] + DC_CIBLE.encode() + args[0][1][33:]
            args[1][1] = b"\x01" + _enc_varint(len(COLONNE)) + COLONNE.encode()
            for a, c in zip(args[2:4], (source, destination)):
                a[1] = b"\x01" + _enc_varint(len(c)) + c.encode()
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
            return f
    return None


def _noeud(tt, classe):
    return next((r for r in tt["references"]["RefIds"] if r["type"]["class"] == classe), None)


def _id_neuf():
    return {"m_idBytes": list(os.urandom(16))}


def graphe_difference(modele, cible):
    """typetree de cible (fonction inutilisée d'origine) refait avec le graphe de modele (Count(liste) − b, mis à 0
    si ≤ 0) : Get<int>(source) − Get<int>(b), mis tel quel dans les 2 cas"""
    g = copy.deepcopy(modele)
    sub = _noeud(g, "GeneralVisualFunction_Subtract_int_int_int")
    lire = _noeud(g, "TypedValueVisualFunctionLibrary_GetInt")
    compte = _noeud(g, "GeneralVisualFunction_Count")
    liste = _noeud(g, "TypedValueVisualFunctionLibrary_GetTypedList")
    creer = [r for r in g["references"]["RefIds"] if r["type"]["class"] == "TypedValueVisualFunctionLibrary_IntToTypedValue"]
    if None in (sub, lire, compte, liste) or len(creer) != 2:
        return None
    s, lr, c, ls = sub["data"], lire["data"], compte["data"], liste["data"]
    # le modèle attendu : a <- Count(GetTypedList(source)), b <- Get<int>(décalage), un Create<int> <- a − b, l'autre 0
    vide = [r for r in creer if not any(r["data"]["m_dataInValue"]["m_sourceID"]["m_idBytes"])]
    if s["m_dataInA"]["m_sourceID"] != c["m_dataOutInt32"]["m_id"] \
            or c["m_dataInList"]["m_sourceID"] != ls["m_dataOutList"]["m_id"] \
            or s["m_dataInB"]["m_sourceID"] != lr["m_dataOutInt32"]["m_id"] or len(vide) != 1:
        return None
    a = copy.deepcopy(lire)   # 2e Get<int>, sur la source
    a["rid"] = max(r["rid"] for r in g["references"]["RefIds"]) + 1
    a["data"]["m_id"] = _id_neuf()
    a["data"]["m_dataInValue"]["m_id"], a["data"]["m_dataOutInt32"]["m_id"] = _id_neuf(), _id_neuf()
    a["data"]["m_dataInValue"]["m_sourceID"] = copy.deepcopy(ls["m_dataInValue"]["m_sourceID"])
    s["m_dataInA"]["m_sourceID"] = copy.deepcopy(a["data"]["m_dataOutInt32"]["m_id"])
    vide[0]["data"]["m_dataInValue"]["m_sourceID"] = copy.deepcopy(s["m_dataOutInt32"]["m_id"])
    retires = {compte["rid"], liste["rid"]}
    g["m_nodes"] = [n for n in g["m_nodes"] if n["rid"] not in retires] + [{"rid": a["rid"]}]
    g["references"]["RefIds"] = [r for r in g["references"]["RefIds"] if r["rid"] not in retires] + [a]
    # identité de la cible gardée (son m_id), nom = notre repère ; tout ce qui est rattaché au m_id du modèle (nœuds ET
    # entrées / sorties / variables) l'est à celui de la cible (v14 : entrées oubliées -> crash)
    ancien, nouveau = modele["m_id"]["m_idBytes"], cible["m_id"]["m_idBytes"]

    def rattacher(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "m_parentID" and isinstance(v, dict) and v.get("m_idBytes") == ancien:
                    x[k] = {"m_idBytes": list(nouveau)}
                else:
                    rattacher(v)
        elif isinstance(x, list):
            for v in x:
                rattacher(v)
    rattacher(g)
    for k in ("m_GameObject", "m_Enabled", "m_Script", "m_id"):
        g[k] = copy.deepcopy(cible[k])
    g["m_Name"] = g["m_name"] = NOM_FN
    return g


def poser_difference():
    """réécrit la fonction FN_CIBLE en « a − b » (messages ; « introuvable » = rien fait)"""
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    if obj is None:
        return ["fonction FM à réécrire introuvable (bundle des fonctions changé par une mise à jour ?)"]
    actuel = obj.read_typetree()
    if actuel.get("m_Name") == NOM_FN:
        return []
    cible = hp.original(FONCTIONS, obj) or actuel
    modele = next((o.read_typetree() for o in fns.values() if o is not None and o.peek_name() == MODELE_FN), None)
    if cible.get("m_Name") != NOM_CIBLE or modele is None or cible["m_Script"] != modele["m_Script"]:
        return [f"fonction FM {NOM_CIBLE} / {MODELE_FN} introuvable (mise à jour de FM ?)"]
    g = graphe_difference(modele, cible)
    if g is None:
        return [f"graphe de {MODELE_FN} inattendu (introuvable)"]
    obj.save_typetree(g)
    nb._dirty.add(FONCTIONS)
    return [f"fonction FM inutilisée {NOM_CIBLE} réécrite en « a − b » (correction du numéro)"]


def retirer_soustraction():
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    if obj is None or not str(obj.read_typetree().get("m_Name", "")).startswith("UIPicker"):
        return []
    orig = hp.original(FONCTIONS, obj)
    if orig is None:
        return [f"{NOM_CIBLE} : pas de sauvegarde d'origine, laissée (utiliser la vérification des fichiers Steam)"]
    obj.save_typetree(orig)
    nb._dirty.add(FONCTIONS)
    return [f"{NOM_CIBLE} : remise d'origine"]


# ---------- v3 / v4 : remettre les menus d'équipe d'origine ----------
def nettoyer_menus():
    if not os.path.exists(MENU) or not os.path.exists(backup.backup_path(MENU)):
        return []
    obj = next((o for o in nb.env_of(MENU).objects
                if o.type.name == "MonoBehaviour" and o.peek_name() == DONNEES_MENU), None)
    if obj is None:
        return []
    tt = obj.read_typetree()
    if not any(str((r.get("data") or {}).get("debug_name", "")).startswith("UIPicker")
               for r in (tt.get("references") or {}).get("RefIds") or []):
        return []
    o = next((x for x in UnityPy.load(backup.backup_path(MENU)).objects if x.path_id == obj.path_id), None)
    if o is None:
        return [f"{DONNEES_MENU} : pas de sauvegarde d'origine, entrées des essais v3 / v4 laissées"]
    obj.save_typetree(o.read_typetree())
    nb._dirty.add(MENU)
    return [f"{DONNEES_MENU} remis d'origine (entrées des essais v3 / v4)"]


# ---------- commandes ----------
def cmd_appliquer():
    if not _verifier_evenement():
        print("amical depuis la page club : format d'événement inattendu, rien enregistré")
        return
    msgs = nettoyer_menus()
    fn = poser_table() + poser_difference()
    if any("introuvable" in x for x in fn):
        for x in fn:
            print(f"amical depuis la page club : {x}")
        print("amical depuis la page club : rien enregistré")
        return
    msgs += fn
    actuel = ouvrir(MODELE)
    if actuel is None:
        print("page Infos du club introuvable (renommée par une mise à jour ?), ignoré")
        return
    if any(actuel[3].name(r).startswith(NOM_RACINE) for r in marques(actuel[3])):
        if not msgs:
            print("amical depuis la page club : déjà appliqué")
    else:
        ancien = bool(marques(actuel[3]))
        travail = ouvrir(MODELE, depart_original=True)
        if marques(travail[3]):
            print("amical depuis la page club : pas de sauvegarde d'origine propre, ignoré")
            return
        src, mx, pieces = ouvrir(SOURCE_BOUTON, depart_original=True), ee.Morceaux(), Pieces()   # calendrier d'origine
        st = ouvrir(SOURCE_FN_TABLE, depart_original=True)
        fn_table = st and fonction_table(st[3])
        fn_rang = st and fonction_table(st[3], OPP_UID, VAR_RANG)
        fn_moitie = st and fonction_table(st[3], VAR_CLE, VAR_MOITIE)
        if src is None or not mx.ok() or not pieces.ok() or None in (fn_table, fn_rang, fn_moitie):
            print("amical depuis la page club : morceaux de FM introuvables, rien enregistré")
            return
        m = construire(travail[3], src[3], mx, pieces, fn_table, fn_rang, fn_moitie)
        if any("introuvable" in x for x in m):
            for x in m:
                print(f"amical depuis la page club : {x}")
            print("amical depuis la page club : rien enregistré")
            return
        msgs += m + (["ancienne version remplacée"] if ancien else [])
        bundle, obj, tt, t = travail
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    for m in msgs:
        print(f"amical depuis la page club : {m}")
    if msgs:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    msgs = nettoyer_menus() + retirer_soustraction() + retirer_table()
    o = ouvrir(MODELE)
    if o is not None and marques(o[3]):
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            msgs.append(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        else:
            obj.save_typetree(orig)
            sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
            if sheet is not None:
                t.styles.sh, t.styles.changed = sheet, True
                t.styles.save()
            nb._dirty.add(bundle)
            msgs.append(f"{MODELE} : remis d'origine")
    if msgs:
        for m in msgs:
            print(m)
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        t = o[3]
        etat = "à jour" if any(t.name(r).startswith(NOM_RACINE) for r in marques(t)) else "ANCIENNE version"
        print(f"{MODELE} : " + (f"appliqué ({etat}, v{VERSION})" if marques(t) else "d'origine"))
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
            print("amical depuis la page club : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
