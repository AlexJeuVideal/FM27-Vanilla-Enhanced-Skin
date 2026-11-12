"""[AJOUT KINITO] Entraînement : échanger deux séances en deux clics (à la place du glisser-déposer de FM24).

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : dans FM24, on attrapait une séance du calendrier d'entraînement et on la lâchait sur
une autre pour les intervertir. Un vrai glisser-déposer est impossible en skin (mesuré : FMDropTarget n'envoie au moteur
que l'événement prévu par FM, et aucun n'existe pour l'entraînement ; pendant un glisser, la souris est capturée). Forme
choisie avec lui : l'échange en deux clics.

Sur chaque séance modifiable, une petite icône (game-concepts-transfer_small, dans le bouton « contrôle » de FM, celui
de la poubelle des contrats), À LA PLACE de l'icône de catégorie de la séance (v2, demandé par Kinito : la couleur de la
case dit déjà la catégorie ; la v1 la posait à droite, par-dessus la fin du nom) ; une séance non modifiable (jour passé)
garde son icône de FM :
  1er clic : la séance est retenue (sa date, son numéro dans la journée, son type, l'équipe affichée) ; elle s'entoure de
             l'anneau blanc que FM met sur la séance choisie dans la mini-semaine de sa fenêtre (v2 : plus de cadre sur
             toutes les icônes, jugé chargé par Kinito) ;
  2e clic sur une autre séance : les deux séances échangent leur type ; tout redevient normal. Un 2e clic sur la séance
             retenue elle-même ne change rien (annuler). Sur une autre équipe que celle de la séance retenue, l'icône est
             grisée (FM : BindMultipleBindingsAreEqualToEnabled sur team / l'équipe retenue).
Partout : Portail > Calendrier > Entraînement (cases MaxRes, StandardRes, MinRes) et Entraînement > Programme (cases
Flex). D'une semaine à l'autre, et d'un mois à l'autre.

Relevé dans le jeu (2026-11-12), rien de deviné :
- sonde FMSonde 0.15 (GamePlugin.SendEvent, l'entonnoir de tous les événements de l'interface vers le moteur), séances
  changées par Kinito : la fenêtre de FM envoie à human.TrainingCalendar (la cible « trainingselector » de
  TrainingScheduleEditor quand IsCustomSchedule est faux) BeginTrainingWeekEditFromCard {date, n°, type} ->
  SelectTrainingSession {date, n°, type} -> ConfirmTrainingSessionFromCard {type : la nouvelle} ->
  CommitTrainingWeekFromCard (null) ; la cible porte l'équipe affichée (clé « Team ») ; sans Begin le changement tient
  aussi (vu en jeu sur Équipe 2) ;
- {date, n°, type} = la variable selectData de Training_TrainingSession_Any_Flex (DynamicReferenceScopeValue
  1131498817 day.Date, 1382758229 Event.SessionIndex, 1330735726 Event.SessionType), que cette case FM envoie elle-même
  avec Begin et Select ; « confirmer » = customConfirmData de TrainingScheduleEditor ({1330735726 : la séance cochée}) ;
- format d'un envoi : 27,222,7,0,1 + cible + données + numéro de l'événement (4 octets) : refait à l'octet près ici et
  comparé aux boutons de FM (_verifier) ;
- la case de séance est choisie par Training_TrainingSession_Any_ItemFactory selon « resolution » : 0 MaxRes, 1 MinRes,
  4 StandardRes (CalendarTrainingView_MaxRes / _MinRes / _StandardRes), 7 Flex (TrainingOverviewCalendarBlock) ;
- l'anneau : #SelectionRing (classe calendar-training-session-selection-ring, affiché seulement sous
  .calendar-training-session-selected) de Training_TrainingSession_Any_Flex_Edit_Session ; FM l'allume par un
  SIStyleSetter (BindDimmedTrainingSessionUSSClass, deux paires d'ENTIERS) sur Event.DayIndex, propre à sa fenêtre.
  Dans le calendrier, le jour n'a que day.DayOfTheMonth, un TEXTE (« 17 », « 1 nov » : relevé F7 du 10/10) et day.Date :
  depuis la v7, la séance retenue est reconnue à ce texte et à son numéro (Event.SessionIndex, un entier), par deux
  switch de FM (voir v7 plus bas).
- une variable « Null » (comme add-data de TacticsPicker) reçoit n'importe quelle valeur ; une copie depuis une case
  écrit dans la variable déclarée plus haut (comme « selected-tab » des onglets de FM).

Limite connue, laissée telle quelle par Kinito (12/11, « attendre les mises à jour du jeu ») : le jeu
transforme en Repos une séance de Préparation de match posée un lendemain de match (vu en jeu avec sa PROPRE fenêtre :
Placement défensif sur le sam. 22/08 après le match du 21) ; un échange qui y envoie une telle séance la perd.

v8 (12/11/2026, Kinito : « construis la v8 ») — l'échange envoyé étape par étape. Relevé à la sonde (FMSonde 0.15,
journal du 27-28/10) après la mise à jour de FM du 27/10 : nos événements sont ceux de la fenêtre de FM, à l'octet
près (cible, données, ordre) ; seul le temps diffère. Depuis le jeu du ~20/10, une liste d'événements part dans la
même milliseconde (avant : une image entre chaque, ~16 ms) ; la fenêtre de FM, elle, les espace de secondes (le temps
des clics). Sur un calendrier pas encore modifié depuis le chargement de la partie, FM perd un changement envoyé d'un
bloc ; une fois un changement passé (sa fenêtre, ou un programme appliqué à une semaine), tout tient, partout. Le
2e clic garde donc la 2e séance dans la mémoire du calendrier et ouvre une zone d'écriture (un SIVisible sur
« kinitoechecrit », dans chaque calendrier) dont les SIDelayEvent de FM envoient les étapes l'une après l'autre
(ETAPE_1, puis ECART entre deux), dans l'ordre de la fenêtre de FM ; la dernière referme la zone. FM fait de même :
un SIDelayEvent de StateSetPieceWizardCreation envoie un événement au moteur. Pendant l'écriture, les icônes sont
désactivées (SIEnabled de FM sur « kinitoechecrit » inversé, comme l'interrupteur d'en-tête de 26.17 v5) : un clic
de plus ne peut pas changer la séance retenue pendant qu'on l'écrit.
v8 VUE EN JEU le 28/10 (01:26) : les étapes partaient exactement à 0,2 s d'écart, l'échange était quand même perdu :
le temps n'était pas la cause. Kinito : « enlève ce machin qui fait ralentir le switch ».

v9 (12/11/2026, choix de Kinito : « instantané + essai ») — l'échange redevient instantané (le 2e clic envoie tout d'un
bloc, comme la v7), plus un ESSAI : chaque calendrier lit en permanence, en cachette, ce que lit la fenêtre de séance de
FM en s'ouvrant. Mesuré en jeu par Kinito (essais A et C du 12/11, journaux evenements_20261112_020001.txt et
clics_20261112_020001.log) : ouvrir la fenêtre de FM sur une séance (sa case envoie Begin + Select, les mêmes que les
nôtres) puis la fermer SANS rien envoyer (ni Annuler, ni Confirmer) suffit à débloquer le calendrier : les ⇄ suivants
tiennent. Seule différence avec nos envois : la fenêtre ouverte (TrainingScheduleEditor) et ce qu'elle lit, avec
trainingselector = Human.TrainingCalendar hors programme personnalisé : CalendarWeekAsList (la mini-semaine, DateGrid),
TrainingSessionCategoryOnlyDropdown et TrainingSessionsForCategoryDropdown (les deux SIRadioGroup), TrainingScheduleName
(SIText), et ses BindAndSetToDestination de ...SessionsForCategoryDropdownSelectedValue.PropertyValue -> selectedSession
et de ...SessionCategoryOnlyDropdownSelectedValue -> trainingcategory. La zone de lecture (dernier enfant du porteur de
« resolution », sans place, contenu rogné) fait les mêmes lectures avec des morceaux de FM : trois SIVisible
BindListHasItemsToVisible (la fonction du #HasData de TrainingOverviewCalendarBlock) sur les trois listes, le SIText
#SessionTemplateName de l'éditeur sur TrainingScheduleName, et un BindingSetter avec les deux BindAndSetToDestination de
l'éditeur (recopiés, la source sur human.TrainingCalendar, la destination dans nos variables). Rien n'est envoyé au
moteur. PAS PROUVÉ que ces lectures suffisent (la fenêtre peut faire autre chose en s'ouvrant) : c'est l'essai.

Touchés :
- CalendarTrainingView_MaxRes / _StandardRes / _MinRes (bundle global) : la mémoire de l'échange, ajoutée au composant
  qui déclare « resolution », et (v9) la zone de lecture, dernier enfant de l'élément qui porte ce composant ; seul
  propriétaire : appliquer repart de l'original, retirer le remet ;
- Training_TrainingSession_Any_MaxRes / _StandardRes / _MinRes / _Flex (bundle global) : l'anneau (dans l'élément qui
  contient la case, le parent de son SIGradient) et l'icône (dans le bouton de la case, à la place de #Icon) ; seul
  propriétaire : appliquer repart de l'original, retirer le remet ;
- TrainingOverviewCalendarBlock (gameworld) : la mémoire de l'échange et la zone de lecture, comme les calendriers.
  PARTAGÉ avec l'ajout 26.7 (boutons des équipes, choix de Kinito du 10/10) : ici on part du modèle ACTUEL et on
  n'ajoute / retire que nos variables (noms kinitoech*) et nos éléments (noms UIPickerKinito-echange…, avec leurs
  règles de style), sans jamais remettre le bloc d'origine.
La case du jour (CalendarDay_block, ajout 26.4) n'est PAS touchée : on n'y lit que l'original, pour recopier son SIVisible.
Morceaux de FM recopiés, sans les modifier : le bouton de la poubelle de ContractNegotiationAddOnItem (sans infobulle
depuis la v4), le SIVisible #GradientHeaderVisible de CalendarDay_block, le BindingSetter de GoOnHolidayWidget,
#SelectionRing de Training_TrainingSession_Any_Flex_Edit_Session, le SIEnabled (BindMultipleBindingsAreEqualToEnabled)
de TransferBlockMainFrame, depuis la v7 les BindableSwitchElement de KeyboardShortcutEditCell et de
MentalityDropdownRow (vidés de leurs enfants), et depuis la v9 le SIVisible #HasData de TrainingOverviewCalendarBlock
(vidé de son enfant), le SIText #SessionTemplateName et deux BindFunction (BindAndSetToDestination) de
TrainingScheduleEditor (la v8 recopiait un SIDelayEvent et un SIEnabled, retirés en v9).

Historique des versions (demandes, relevés en jeu, essais) : résumé dans « AJOUTS KINITO - DETAILS.md »,
§ 7 ; texte complet gardé par Kinito.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_echange_seances.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_echange_seances.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_echange_seances.py etat
"""
import json
import os
import struct
import sys

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, _enc_varint, decode_args, encode_args  # noqa: E402
import arbre  # noqa: E402  (v7 : propriétés de style des couches posées sur la case ; numéros de moteur_graphes et
arbre.PROPRIETES.setdefault("left", (131089, 3))     # d'elements, StylePropertyId Left et Bottom)
arbre.PROPRIETES.setdefault("bottom", (131080, 3))

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
ICONE_CLASSE = "game-concepts-transfer_small"   # deux flèches en cercle de FM (16 x 16, FMImages_1x)
BOUTON = 16          # px, place occupée : celle de l'icône de séance de FM (16 x 16, + 4 px à droite)
ICONE = 16           # px
ZONE_CLIC = (22, 24)                 # px, largeur x hauteur de la zone cliquable autour de l'icône (v3, Kinito : « augmenter
DEBORD = {"margin-left": -4, "margin-right": -2, "margin-top": -4, "margin-bottom": -4}   # la hitbox ») ; ces marges
                                     # négatives gardent la place occupée à 16 x 16 : le nom ne bouge pas
# v5 (Kinito, 10/10 : « quand je sélectionne une séance pour la switch, le bouton switch s'allume en jaune ») : la classe
# de FM qui teinte l'icône de la séance retenue. Classes de FM qui ne règlent QUE la teinte d'une image (relevé dans
# AlwaysAppliedStyleSheet) : « injury-severity-image-colour-minor » = --colours-base-yellow-strong #f7ff12 (jaune vif) ;
# « bib-colour-yellow » = --colours-base-yellow-soft #edea97 (jaune pâle) ; « team-reputation-star » =
# --colours-data-ratings-star-ability-orange #ffb82a (l'orangé des étoiles). L'icône de FM (game-concepts-transfer_small)
# n'a pas de teinte à elle, et les styles du bouton contrôle n'en donnent pas à ses enfants.
CLASSE_JAUNE = "injury-severity-image-colour-minor"
# v9 (voir la docstring) : ce que la fenêtre de séance de FM lit en s'ouvrant, lu en cachette par chaque calendrier
LISTES_LUES = ["CalendarWeekAsList", "TrainingSessionCategoryOnlyDropdown", "TrainingSessionsForCategoryDropdown"]
TEXTE_LU = "TrainingScheduleName"
# =====================================================================================================

VERSION = 9   # v1 : icône à droite de la case, cadre sur toutes les icônes une fois une séance retenue ; v2 : à la place
              # de l'icône de séance, anneau seul ; bloc de la vue d'ensemble partagé avec 26.7 ; v3 : zone de clic
              # 22 x 24 px autour de l'icône (place occupée inchangée) ; v4 : sans infobulle (plus aucun texte fixe :
              # plus de dépendance à la langue) ; v5 : l'icône de la séance retenue s'allume en jaune (CLASSE_JAUNE),
              # restée blanche en jeu ; v6 : l'icône est elle-même le SIStyleSetter qui pose le jaune (blanche aussi) ;
              # v7 : anneau et jaune par deux switch de FM (texte du jour, n° de séance), classes posées en dur ;
              # v8 : l'échange envoyé étape par étape par une zone d'écriture du calendrier (SIDelayEvent de FM),
              # icônes désactivées pendant l'écriture (vue en jeu : n'y change rien) ; v9 : l'échange de nouveau
              # instantané, et chaque calendrier lit en cachette ce que lit la fenêtre de séance de FM (essai)
CALENDRIERS = ["CalendarTrainingView_MaxRes", "CalendarTrainingView_StandardRes", "CalendarTrainingView_MinRes",
               "TrainingOverviewCalendarBlock"]   # ceux qui déclarent « resolution » : 0, 4, 1 et 7
PARTAGE = "TrainingOverviewCalendarBlock"         # partagé avec 26.7 : nos morceaux seulement, sur le modèle actuel
CASES = ["Training_TrainingSession_Any_MaxRes", "Training_TrainingSession_Any_StandardRes",
         "Training_TrainingSession_Any_MinRes", "Training_TrainingSession_Any_Flex"]
# événements du moteur (FM.GamePlugin.InteropEventIDs), relevés par la sonde et vérifiés sur les boutons de FM
BEGIN = 1222759635       # EventFmxBeginTrainingWeekEditFromCard
SELECT = 1483633258      # EventFmxSelectTrainingSession
CONFIRMER = 3824478846   # EventFmxConfirmTrainingSessionFromCard
VALIDER = 4108082463     # EventFmxCommitTrainingWeekFromCard
CALENDRIER = "human.TrainingCalendar"   # la cible (celle de selectData dans Training_TrainingSession_Any_Flex)
CLE_DATE, CLE_NUMERO, CLE_TYPE = 1131498817, 1382758229, 1330735726   # clés de selectData
# la mémoire de l'échange, déclarée dans chaque calendrier (au-dessus de toutes ses cases)
V_ICI = "kinitoechange"        # vrai : on est dans un calendrier qui a l'échange (ailleurs : pas d'icône)
V_ARME = "kinitoecharme"       # vrai : une séance est retenue
V_DATE, V_NUMERO, V_TYPE, V_JOUR, V_EQUIPE = ("kinitoechdate", "kinitoechindex", "kinitoechtype", "kinitoechjour",
                                              "kinitoechteam")
VARIABLES_CALENDRIER = [(V_ICI, "Bool|1|"), (V_ARME, "Bool|0|"), (V_DATE, "Null"), (V_NUMERO, "Null"),
                        (V_TYPE, "Null"), (V_JOUR, "Null"), (V_EQUIPE, "Null")]
SELECTDATA_FM = [(CLE_DATE, "day.Date"), (CLE_NUMERO, "Event.SessionIndex"), (CLE_TYPE, "Event.SessionType")]
# dans chaque case : les données des événements (DynamicReferenceScopeValue, comme selectData de FM)
SEL_RETENUE, SEL_ICI = "kinitoechsela", "kinitoechselb"
VERS_RETENUE, VERS_ICI = "kinitoechversa", "kinitoechversb"
VARIABLES_CASE = [
    (SEL_RETENUE, [(CLE_DATE, V_DATE), (CLE_NUMERO, V_NUMERO), (CLE_TYPE, V_TYPE)]),
    (SEL_ICI, SELECTDATA_FM),
    (VERS_RETENUE, [(CLE_TYPE, "Event.SessionType")]),   # la séance retenue prend le type de celle-ci
    (VERS_ICI, [(CLE_TYPE, V_TYPE)]),                    # celle-ci prend le type de la séance retenue
]
# v9 : les variables où la zone de lecture recopie ce que la fenêtre de FM recopie dans les siennes (selectedSession :
# valeur « Unset » ; trainingcategory : référence, type relevé dans TrainingScheduleEditor)
V_LU_SEANCE, V_LU_CATEGORIE = "kinitoechluseance", "kinitoechlucategorie"
DESTINATIONS_EDITEUR = {"selectedSession": V_LU_SEANCE, "trainingcategory": V_LU_CATEGORIE}
CLASSE_CHOISIE = "calendar-training-session-selected"   # celle de FM : affiche l'anneau
BOUTON_INACTIF = "buttons-controls-pc-default--active-false"  # contrôle FM nu : celui de la poubelle
SOURCE_BOUTON = ("ContractNegotiationAddOnItem", "buttons-controls-pc-default")   # bouton-icône FM (poubelle)
SOURCE_VISIBLE = ("CalendarDay_block", "GradientHeaderVisible")        # SIVisible direct (original, lu seulement)
SOURCE_REGLAGE = ("GoOnHolidayWidget", "BindingSetter")                # élément BindingSetter de FM (enfant retiré)
SOURCE_ANNEAU = ("Training_TrainingSession_Any_Flex_Edit_Session", "SelectionRing")
# v7 : les deux switch de FM qui disent « cette séance est la séance retenue » (enfant 1 si égal, 0 sinon)
SOURCE_SWITCH_TEXTE = "KeyboardShortcutEditCell"                       # son BindableSwitchElement sur ...
GUID_SWITCH_TEXTE = "45ff404d74e03fa42b6a86df09674c74"                 # BindStringComparisonToSwitch (2 chemins)
SOURCE_SWITCH_NOMBRE = "MentalityDropdownRow"                          # son BindableSwitchElement sur ...
GUID_SWITCH_NOMBRE = "0ab972d3f1b7a954295e2ae05b133c98"                # BindTwoIntPropertyComparisonToSwitch
OPERATEUR_EGAL = bytes([2, 0, 0, 0])   # GeneralVisualFunction.ComparisonOperator.Equal (celui de MentalityDropdownRow)
CHEMIN_ARG = b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"
OPERATEUR_ARG = b"SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]"
SOURCE_EGAL = "TransferBlockMainFrame"                                 # son SIEnabled sur ...
GUID_EGAL = "1e7f6df75fe06da4c93e981c9c438543"                         # BindMultipleBindingsAreEqualToEnabled
SOURCE_FLEX = "Training_TrainingSession_Any_Flex"                      # pour vérifier selectData, Begin et Select
SOURCE_EDITEUR = "TrainingScheduleEditor"                              # pour vérifier Confirmer et Valider
SOURCE_LISTE = ("TrainingOverviewCalendarBlock", "HasData")   # v9 : SIVisible de FM sur BindListHasItemsToVisible
GUID_LISTE = "fb85a893388896b458c4be0009043d13"                # BindListHasItemsToVisible
SOURCE_TEXTE = (SOURCE_EDITEUR, "SessionTemplateName")         # v9 : SIText de la fenêtre de FM (TrainingScheduleName)
GUID_COPIE = "8ca91f1cfa07a3447ad7c8381cadfef5"                # v9 : BindAndSetToDestination (BindFunction de l'éditeur)
SELECTEUR = "trainingselector."                                # v9 : dans l'éditeur ; Human.TrainingCalendar ici
PREFIXE = "UIPickerKinito"
NOM = f"{PREFIXE}-echange-seances-v{VERSION}"
NOM_LECTURE = f"{PREFIXE}-echange-lecture-v{VERSION}"   # v9 : la zone de lecture de chaque calendrier
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_echange_seances.actif")


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(f"{PREFIXE}-echange")]


# ---------- événements et variables (formats de FM) ----------
def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def _bloc(b):
    return struct.pack("<i", len(b)) + b


def copier(source, destination):
    """contenu d'un événement « copier la valeur de <source> dans <destination> » (217,15,225,87)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([1, 0])


def envoyer(cible, donnees, evenement):
    """contenu d'un événement « envoyer au moteur l'événement <n°> à <cible> avec <données> » (27,222,7,0)"""
    return bytes([27, 222, 7, 0, 1]) + _bloc(_texte(cible)) + _bloc(_texte(donnees)) + struct.pack("<I", evenement)


def liste(contenus):
    """liste d'événements : [1,1,1,N] puis [1] + longueur + contenu pour chacun"""
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def decouper(octets):
    """contenus des événements d'une liste ; None si le format n'est pas celui attendu"""
    b = bytes(octets)
    if len(b) < 4 or b[:3] != b"\x01\x01\x01":
        return None
    i, out = 4, []
    for _ in range(b[3]):
        if i + 5 > len(b) or b[i] != 1:
            return None
        n = struct.unpack_from("<i", b, i + 1)[0]
        out.append(b[i + 5:i + 5 + n])
        i += 5 + n
    return out if i == len(b) else None


def portee(paires):
    """une DynamicReferenceScopeValue : {clé : chemin}, écrite comme selectData de FM"""
    return json.dumps({"$type": "SI.Bindable.DynamicReferenceScopeValue, SI.Bindable",
                       "m_data": [{"PropertyID": {"id": c, "ID": c}, "BindingPath": p} for c, p in paires]},
                      separators=(",", ":"), ensure_ascii=False)


def _verifier():
    """les formats écrits ici = ceux de FM, refaits à l'octet près : la copie de ClubNationInfoTabButton ; Begin et
    Select de la case Flex et sa variable selectData ; Confirmer et Valider de la fenêtre (TrainingScheduleEditor)"""
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    if liste([copier("rowindex", "selected-tab")]) != attendu:
        return "copie"
    o = ouvrir(SOURCE_FLEX, depart_original=True)
    if o is None:
        return SOURCE_FLEX
    t = o[3]
    b = first(t, lambda r: typ(t, r) == "SIButton")
    ev = b is not None and decouper(t.sd(b).get("Events", {}).get("m_bytes") or [])
    if not ev or len(ev) != 3 or ev[0] != envoyer(CALENDRIER, "selectData", BEGIN) \
            or ev[1] != envoyer(CALENDRIER, "selectData", SELECT):
        return "Begin / Select de la case Flex"
    vars_ = [v for r in t.refs.values() if r for v in ((r.get("data") or {}).get("ValueVariables") or [])
             if isinstance(v, dict) and v.get("m_name") == "selectData"]
    if len(vars_) != 1 or vars_[0]["m_scopeValue"]["m_serializedData"] != portee(SELECTDATA_FM):
        return "selectData de la case Flex"
    e = ouvrir(SOURCE_EDITEUR, depart_original=True)
    if e is None:
        return SOURCE_EDITEUR
    te = e[3]
    confirmer = valider = False
    for r in te.walk():
        for cle in ("SelectionEvents", "Events"):
            c = decouper(((te.sd(r).get(cle) or {}).get("m_bytes")) or []) or []
            if c and c[0] == envoyer("trainingselector", "customConfirmData", CONFIRMER):
                confirmer = True
            if te.name(r) == "confirm" and c and c[0] == envoyer("trainingselector", "null", VALIDER):
                valider = True
    if not (confirmer and valider):
        return "Confirmer / Valider de la fenêtre"
    return None


# ---------- les calendriers : la mémoire de l'échange ----------
def composant_resolution(t):
    """données du composant qui déclare « resolution » (celui que lisent les cases), ou None"""
    for r in t.refs.values():
        if not r or not str((r.get("type") or {}).get("class", "")).startswith("BindingVariablesComponent"):
            continue
        vv = (r.get("data") or {}).get("ValueVariables") or []
        if any(isinstance(v, dict) and v.get("m_name") == "resolution" for v in vv):
            return r["data"]
    return None


def porteur_resolution(t):
    """l'élément dont un composant déclare « resolution » (ses descendants lisent la mémoire de l'échange), ou None"""
    d = composant_resolution(t)
    for r in t.walk():
        for c in (t.sd(r) or {}).get("m_components") or []:
            if d is not None and (t.refs.get(c.get("rid")) or {}).get("data") is d:
                return r
    return None


def calendrier_a_jour(t):
    d = composant_resolution(t)
    noms = {v.get("m_name") for v in (d or {}).get("ValueVariables") or [] if isinstance(v, dict)}
    return (d is not None and all(n in noms for n, _ in VARIABLES_CALENDRIER)
            and any(t.name(r) == NOM_LECTURE for r in t.walk()))


def calendrier_marque(t):
    d = composant_resolution(t)
    return d is not None and (bool(marques(t)) or any(
        isinstance(v, dict) and str(v.get("m_name", "")).startswith("kinitoech") for v in d.get("ValueVariables") or []))


def retirer_regles(t, enlever):
    """les règles de la feuille intégrée (numéros dans enlever) que plus rien n'utilise, et les valeurs qu'elles avaient
    ajoutées en fin de table (comme 26.14 / 26.15 / 26.16 / 26.17)"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = set(enlever) - utilisees - {-1}
    if not enlever:
        return
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
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
    for nom in set(tables.values()):
        vals = t.styles.sh.get(nom) or []
        while vals and len(vals) - 1 not in servies.get(nom, set()):
            vals.pop()
    t.styles.changed = True


def retirer_morceaux(t):
    """retire nos variables (noms kinitoech*) du composant « resolution » et nos éléments (noms UIPickerKinito-echange…,
    la zone d'écriture de la v8, la zone de lecture de la v9) avec leurs règles de style, et rien d'autre (bloc partagé
    avec 26.7)"""
    d = composant_resolution(t)
    if d is not None:
        d["ValueVariables"] = [v for v in d.get("ValueVariables") or []
                               if not (isinstance(v, dict) and str(v.get("m_name", "")).startswith("kinitoech"))]
    m = set(marques(t))
    hauts = [r for r in m if t.parent.get(r) not in m]
    regles = {t.elem(x).get("m_RuleIndex", -1) for r in hauts for x in t.walk(r)}
    for r in hauts:
        t.remove(r)
    retirer_regles(t, regles)


def construire_calendrier(t, src):
    d = composant_resolution(t)
    porteur = porteur_resolution(t)
    if d is None or porteur is None:
        return ["composant « resolution » introuvable"]
    vv = d.setdefault("ValueVariables", [])
    for nom, valeur in VARIABLES_CALENDRIER:
        if not any(isinstance(v, dict) and v.get("m_name") == nom for v in vv):
            vv.append({"m_name": nom, "m_scopeValue": {"m_serializedData": valeur}})
    d["ValueVariables_UxmlAttributeFlags"] = 1
    # v9 : la zone de lecture, dernier enfant du porteur (sans place, contenu rogné, sans clics) : un BindingSetter
    # (les deux BindAndSetToDestination de la fenêtre de FM, vers nos variables) > trois SIVisible
    # BindListHasItemsToVisible sur les listes de la fenêtre, le SIText de son nom de programme ; rien n'est envoyé
    z = _vide(t, src, porteur, NOM_LECTURE)
    t.styles.style(t, z, {"position": "absolute", "width": 0, "height": 0, "overflow": "hidden"})
    g = _reglage(t, src, z, f"{PREFIXE}-echange-lecture-donnees", [])
    _a_zero(t, g)
    sg = t.sd(g)
    sg["BindFunction"] = [_copie_editeur(f) for f in src.copies]
    sg["ValueVariables"] = [{"m_name": V_LU_SEANCE, "m_scopeValue": {"m_serializedData": src.valeur_seance}}]
    sg["ReferenceVariables"] = [dict(src.reference_categorie, m_name=V_LU_CATEGORIE)]
    for nom in LISTES_LUES:
        v = t.clone(src.liste, g, src=src.tl)
        _vider(t, v)
        _parent_id(t, v)
        _nommer(t, v, f"{PREFIXE}-echange-lecture-{nom}")
        t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
        _a_zero(t, v)
        vf = t.sd(v)["Binding"]["m_visualFunction"]
        args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
        chem = [a for a in args if bytes(a[0]) == CHEMIN_ARG]
        if len(chem) != 1:
            return [f"SIVisible de FM ({SOURCE_LISTE[1]}) : arguments inattendus"]
        chem[0][1] = _chemin(f"{CALENDRIER}.{nom}")
        vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    x = t.clone(src.texte, g, src=src.tx)
    _vider(t, x)
    _parent_id(t, x)
    _nommer(t, x, f"{PREFIXE}-echange-lecture-{TEXTE_LU}")
    t.elem(x)["m_Classes"], t.elem(x)["m_RuleIndex"] = [], -1
    _a_zero(t, x)
    t.sd(x)["TextBinding"]["m_direct"]["Path"]["m_path"] = f"{CALENDRIER}.{TEXTE_LU}"
    return [f"mémoire de l'échange : {', '.join(n for n, _ in VARIABLES_CALENDRIER)}",
            f"zone de lecture : {', '.join(LISTES_LUES)} (listes), {TEXTE_LU} (texte), "
            f"{len(src.copies)} copies de la fenêtre de FM ({', '.join(DESTINATIONS_EDITEUR)})"]


def _copie_editeur(f):
    """une BindFunction BindAndSetToDestination de la fenêtre de FM, recopiée : la source sur Human.TrainingCalendar au
    lieu de trainingselector, la destination dans notre variable"""
    f = json.loads(json.dumps(f))
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        chemin = _lire_chemin(a[1]) if bytes(a[0]) == CHEMIN_ARG else None
        if chemin is None:
            continue
        if chemin.startswith(SELECTEUR):
            a[1] = _chemin(CALENDRIER + "." + chemin[len(SELECTEUR):])
        elif chemin in DESTINATIONS_EDITEUR:
            a[1] = _chemin(DESTINATIONS_EDITEUR[chemin])
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return f


def _lire_chemin(b):
    """le chemin d'un argument BindingPath (1, longueur en varint, texte), ou None"""
    b = bytes(b)
    if not b or b[0] != 1:
        return None
    n, k, i = 0, 0, 1
    while i < len(b):
        c = b[i]
        n |= (c & 0x7F) << k
        i += 1
        if c < 0x80:
            break
        k += 7
    return b[i:i + n].decode("utf-8", errors="replace")


# ---------- les cases : l'anneau et l'icône ----------
class Sources:
    def __init__(self):
        def ouvre(m):
            o = ouvrir(m, depart_original=True)
            return o and o[3]
        self.tb = ouvre(SOURCE_BOUTON[0])
        self.bouton = self.tb and first(self.tb, lambda r: self.tb.name(r) == SOURCE_BOUTON[1]
                                        and typ(self.tb, r) == "SIButton")
        self.tv = ouvre(SOURCE_VISIBLE[0])
        self.visible = self.tv and first(self.tv, lambda r: self.tv.name(r) == SOURCE_VISIBLE[1]
                                         and typ(self.tv, r) == "SIVisible")
        self.tg = ouvre(SOURCE_REGLAGE[0])
        self.reglage = self.tg and first(self.tg, lambda r: typ(self.tg, r) == SOURCE_REGLAGE[1])
        self.ta = ouvre(SOURCE_ANNEAU[0])
        self.anneau = self.ta and first(self.ta, lambda r: self.ta.name(r) == SOURCE_ANNEAU[1])
        self.te = ouvre(SOURCE_EGAL)
        self.egal = self.te and first(self.te, lambda r: typ(self.te, r) == "SIEnabled" and (
            (self.te.sd(r).get("Binding") or {}).get("m_visualFunction") or {}).get("m_target", {}).get(
            "m_guid") == GUID_EGAL)
        self.tk = ouvre(SOURCE_SWITCH_TEXTE)
        self.sw_texte = self.tk and _switch_source(self.tk, GUID_SWITCH_TEXTE)
        self.tm = ouvre(SOURCE_SWITCH_NOMBRE)
        self.sw_nombre = self.tm and _switch_source(self.tm, GUID_SWITCH_NOMBRE)
        # v9 : les lectures de la fenêtre de séance de FM (lues seulement, dans les originaux)
        self.tl = ouvre(SOURCE_LISTE[0])
        self.liste = self.tl and first(self.tl, lambda r: self.tl.name(r) == SOURCE_LISTE[1]
                                       and typ(self.tl, r) == "SIVisible" and (
            ((self.tl.sd(r).get("Binding") or {}).get("m_visualFunction") or {}).get("m_target") or {}).get(
            "m_guid") == GUID_LISTE)
        self.tx = ouvre(SOURCE_TEXTE[0])
        self.texte = self.tx and first(self.tx, lambda r: self.tx.name(r) == SOURCE_TEXTE[1] and typ(self.tx, r) == "SIText")
        self.copies, self.valeur_seance, self.reference_categorie = [], None, None
        racine = self.tx and self.tx.children(self.tx.tt["m_VisualTree"]["rid"])
        for c in (self.tx.sd(racine[0]).get("m_components") or []) if racine else []:
            d = (self.tx.refs.get(c.get("rid")) or {}).get("data") or {}
            if "BindFunction" not in d:
                continue
            self.copies = [f for f in d["BindFunction"] if (f.get("m_target") or {}).get("m_guid") == GUID_COPIE]
            self.valeur_seance = next((v["m_scopeValue"]["m_serializedData"] for v in d.get("ValueVariables") or []
                                       if v.get("m_name") == "selectedSession"), None)
            self.reference_categorie = next((v for v in d.get("ReferenceVariables") or []
                                             if v.get("m_name") == "trainingcategory"), None)

    def copies_ok(self):
        """les deux BindAndSetToDestination de l'éditeur : chacune une source trainingselector.… et une destination
        connue (selectedSession, trainingcategory)"""
        vus = set()
        for f in self.copies:
            chemins = [_lire_chemin(a[1]) for a in decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                       if bytes(a[0]) == CHEMIN_ARG]
            if len(chemins) != 2 or not (chemins[0] or "").startswith(SELECTEUR) or chemins[1] not in DESTINATIONS_EDITEUR:
                return False
            vus.add(chemins[1])
        return vus == set(DESTINATIONS_EDITEUR)

    def ok(self):
        icones = self.bouton is not None and [k for k in self.tb.children(self.bouton) if typ(self.tb, k) == "VisualElement"]
        anneau_seul = self.anneau is not None and not self.ta.children(self.anneau)
        texte_direct = self.texte is not None and ((self.tx.sd(self.texte).get("TextBinding") or {}).get(
            "m_kind") == 1)
        return (None not in (self.bouton, self.visible, self.reglage, self.anneau, self.egal, self.sw_texte,
                             self.sw_nombre, self.liste, self.texte, self.valeur_seance, self.reference_categorie)
                and len(icones or []) == 1 and anneau_seul and texte_direct and self.copies_ok())


def _switch_source(t, guid):
    """le BindableSwitchElement d'un modèle de FM qui utilise cette fonction, ou None"""
    return first(t, lambda r: typ(t, r) == "BindableSwitchElement" and (
        ((t.sd(r).get("Binding") or {}).get("m_visualFunction") or {}).get("m_target") or {}).get("m_guid") == guid)


def _parent_id(t, rid):
    """clone / clone_shallow ne refont que m_Parent : l'identifiant du parent aussi (composants seulement)"""
    p = t.parent[rid]
    if "m_ParentId" in t.elem(rid):
        t.elem(rid)["m_ParentId"] = t.elem(p).get("m_Id", t.elem(rid)["m_ParentId"])


def _nommer(t, rid, nom):
    t.sd(rid)["name"], t.sd(rid)["name_UxmlAttributeFlags"] = nom, 1


def _vider(t, rid):
    for k in list(t.children(rid)):
        t.remove(k)


def _chemin(chemin):
    return b"\x01" + _enc_varint(len(chemin)) + chemin.encode()


def _deplacer(t, rid, parent, index=None):
    """déplace un élément (et son sous-arbre) sous un autre parent du même modèle"""
    ancien = t.parent[rid]
    t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != rid]
    enfants = t.elem(parent)["m_Children"]
    enfants.insert(len(enfants) if index is None else index, {"rid": rid})
    t.elem(rid)["m_Parent"] = {"rid": parent}
    t.parent[rid] = parent


def _visible(t, src, parent, chemin, inverse, nom, index=None):
    """SIVisible direct de FM (copie de #GradientHeaderVisible, sans son enfant) sur <chemin>"""
    v = t.clone(src.visible, parent, index, src=src.tv)
    _vider(t, v)
    _parent_id(t, v)
    sd = t.sd(v)
    _nommer(t, v, nom)
    sd["Binding"]["m_kind"] = 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = (1 if inverse else 0), 1
    t.elem(v)["m_Classes"] = []
    t.elem(v)["m_RuleIndex"] = -1
    return v


def _a_zero(t, rid):
    """sans place ni clics (comme la zone cachée de 26.17)"""
    t.styles.style(t, rid, {"position": "absolute", "width": 0, "height": 0})
    _ignorer_souris(t, rid)


def _reglage(t, src, parent, nom, variables):
    """BindingSetter de FM (celui de GoOnHolidayWidget, vidé) qui déclare des DynamicReferenceScopeValue {clé : chemin},
    comme selectData de FM"""
    g = t.clone(src.reglage, parent, src=src.tg)
    _vider(t, g)
    _parent_id(t, g)
    t.elem(g)["m_Classes"] = []
    t.elem(g)["m_RuleIndex"] = -1
    _nommer(t, g, nom)
    sg = t.sd(g)
    sg["BindFunction"] = []
    sg["ValueVariables"] = [{"m_name": n, "m_scopeValue": {"m_serializedData": portee(p)}} for n, p in variables]
    sg["ReferenceVariables"] = []
    sg["ValueVariables_UxmlAttributeFlags"] = sg["BindFunction_UxmlAttributeFlags"] = 1
    sg["ReferenceVariables_UxmlAttributeFlags"] = 1
    return g


# v7 : la séance retenue est reconnue par deux switch de FM (voir la docstring) ; enfant 1 = « c'est elle »
def _ignorer_souris(t, rid):
    t.sd(rid)["pickingMode"], t.sd(rid)["pickingMode_UxmlAttributeFlags"] = 1, 1


def _couche(t, rid):
    """élément posé par-dessus la case, à sa taille exacte, transparent pour la souris"""
    t.styles.style(t, rid, {"position": "absolute", "top": 0, "left": 0, "right": 0, "bottom": 0})
    _ignorer_souris(t, rid)


def _vide(t, src, parent, nom, index=None):
    """un VisualElement nu (copie de #SelectionRing de FM, sans sa classe ni son style), transparent pour la souris"""
    e = t.clone(src.anneau, parent, index, src=src.ta)
    _parent_id(t, e)
    _nommer(t, e, nom)
    t.elem(e)["m_Classes"], t.elem(e)["m_RuleIndex"] = [], -1
    _ignorer_souris(t, e)
    return e


def _switch(t, src, parent, sorte, chemins, nom, index=None):
    """BindableSwitchElement de FM, vidé, qui compare chemins[0] et chemins[1] et montre son enfant 1 si c'est égal,
    0 sinon : sorte « texte » (BindStringComparisonToSwitch, comme KeyboardShortcutEditCell) ou « nombre »
    (BindTwoIntPropertyComparisonToSwitch, opérateur Égal, comme MentalityDropdownRow). None si les arguments de FM ne
    sont pas ceux attendus."""
    s_src, t_src = (src.sw_texte, src.tk) if sorte == "texte" else (src.sw_nombre, src.tm)
    s = t.clone(s_src, parent, index, src=t_src)
    _vider(t, s)
    _parent_id(t, s)
    _nommer(t, s, nom)
    t.elem(s)["m_Classes"], t.elem(s)["m_RuleIndex"] = [], -1
    _ignorer_souris(t, s)
    f = t.sd(s)["Binding"]["m_visualFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chem = [a for a in args if bytes(a[0]) == CHEMIN_ARG]
    ops = [a for a in args if bytes(a[0]) == OPERATEUR_ARG]
    attendus = 0 if sorte == "texte" else 1
    if len(chem) != 2 or len(ops) != attendus or len(args) != 2 + attendus \
            or any(bytes(o[1]) != OPERATEUR_EGAL for o in ops):
        return None
    chem[0][1], chem[1][1] = _chemin(chemins[0]), _chemin(chemins[1])
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return s


def _anneau(t, src, case):
    """l'anneau blanc de FM sur la séance retenue : SIVisible (séance modifiable) > switch du jour > switch du n° >
    élément à la classe calendar-training-session-selected > #SelectionRing ; tout à la taille de la case"""
    va = _visible(t, src, case, "Event.CanEdit", False, f"{PREFIXE}-echange-anneau-modifiable")
    _couche(t, va)
    sj = _switch(t, src, va, "texte", ("day.DayOfTheMonth", V_JOUR), f"{PREFIXE}-echange-anneau-jour")
    if sj is None:
        return None
    _couche(t, sj)
    _vide(t, src, sj, f"{PREFIXE}-echange-anneau-autre-jour")                 # enfant 0 : un autre jour
    ss = _switch(t, src, sj, "nombre", ("Event.SessionIndex", V_NUMERO), f"{PREFIXE}-echange-anneau-seance")
    if ss is None:
        return None
    _couche(t, ss)
    _vide(t, src, ss, f"{PREFIXE}-echange-anneau-autre-seance")               # enfant 0 : une autre séance
    retenue = _vide(t, src, ss, f"{PREFIXE}-echange-anneau-retenue")          # enfant 1 : la séance retenue
    t.elem(retenue)["m_Classes"] = [CLASSE_CHOISIE]
    _couche(t, retenue)
    a = t.clone(src.anneau, retenue, src=src.ta)
    t.styles.copy_from(src.ta.styles, t, a)
    _parent_id(t, a)
    _nommer(t, a, f"{PREFIXE}-echange-anneau")
    return a


def _icone_jaune(t, src, bouton, icone):
    """l'icône du bouton « échanger » : blanche (enfant 0 des switch), jaune sur la séance retenue (enfant 1 du second :
    une copie de l'icône avec CLASSE_JAUNE posée en dur)"""
    i = t.children(bouton).index(icone)
    sj = _switch(t, src, bouton, "texte", ("day.DayOfTheMonth", V_JOUR), f"{PREFIXE}-echange-jaune-jour", i)
    if sj is None:
        return None
    _deplacer(t, icone, sj)                                                   # enfant 0 : un autre jour
    ss = _switch(t, src, sj, "nombre", ("Event.SessionIndex", V_NUMERO), f"{PREFIXE}-echange-jaune-seance")
    if ss is None:
        return None
    blanche = t.clone(icone, ss)                                              # enfant 0 : une autre séance
    _nommer(t, blanche, f"{PREFIXE}-echange-echanger-icone-blanche")
    jaune = t.clone(icone, ss)                                                # enfant 1 : la séance retenue
    _nommer(t, jaune, f"{PREFIXE}-echange-echanger-icone-jaune")
    t.elem(jaune)["m_Classes"] = [ICONE_CLASSE, CLASSE_JAUNE]
    for s in (sj, ss):
        t.styles.style(t, s, {"width": ICONE, "height": ICONE, "flex-shrink": 0})
    return jaune


def _meme_equipe(t, src, parent):
    """SIEnabled de FM (BindMultipleBindingsAreEqualToEnabled) : actif seulement si team = l'équipe retenue"""
    e = t.clone(src.egal, parent, src=src.te)
    _vider(t, e)
    _parent_id(t, e)
    _nommer(t, e, f"{PREFIXE}-echange-meme-equipe")
    t.elem(e)["m_Classes"] = []
    t.elem(e)["m_RuleIndex"] = -1
    vf = t.sd(e)["Binding"]["m_visualFunction"]
    args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    if [a[0] for a in args] != [b"SI.VisualScripting.BooleanVisualArg",
                                b"SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BindingPath]"]:
        return None
    args[0][1] = b"\x00"   # pas inversé : actif quand tout est égal
    args[1][1] = bytes([2]) + _chemin("team") + _chemin(V_EQUIPE)
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return e


def _bouton(t, src, parent, classe, evenements, nom):
    """le bouton-icône de FM (poubelle des contrats) : icône d'échange, événements"""
    b = t.clone(src.bouton, parent, src=src.tb)
    t.styles.copy_from(src.tb.styles, t, b)
    _parent_id(t, b)
    _nommer(t, b, nom)
    t.elem(b)["m_Classes"] = [classe]
    t.sd(b)["Events"] = {"m_bytes": liste(evenements)}
    t.sd(b)["Events_UxmlAttributeFlags"] = 1
    largeur, hauteur = ZONE_CLIC
    assert largeur + DEBORD["margin-left"] + DEBORD["margin-right"] == BOUTON
    assert hauteur + DEBORD["margin-top"] + DEBORD["margin-bottom"] == BOUTON
    t.styles.style(t, b, dict({"width": largeur, "min-width": largeur, "height": hauteur, "min-height": hauteur,
                               "padding": 0, "flex-shrink": 0, "justify-content": "center", "align-items": "center"},
                              **DEBORD))
    icone = next(k for k in t.children(b) if typ(t, k) == "VisualElement")
    _nommer(t, icone, f"{nom}-icone")
    t.elem(icone)["m_Classes"] = [ICONE_CLASSE]
    t.styles.style(t, icone, {"width": ICONE, "height": ICONE})
    return b   # v4 : sans infobulle (Kinito : « elle encombre l'écran pour rien dès qu'on passe sur l'icône »)


def construire_case(t, src):
    grad = first(t, lambda r: typ(t, r) == "SIGradient")
    if grad is None or grad not in t.parent:
        return ["case de séance (SIGradient) introuvable"]
    case = t.parent[grad]   # l'élément qui a la taille de la case (ses marges sont dehors)
    icone = first(t, lambda r: t.name(r) == "Icon" and typ(t, r) == "SIImage", grad)
    if icone is None or icone not in t.parent or typ(t, t.parent[icone]) != "SIButton":
        return ["icône de la séance (#Icon dans le bouton de la case) introuvable"]
    bouton_fm = t.parent[icone]   # le bouton de FM de la case (ouvre la fenêtre) : icône, puis nom, en ligne
    i = t.children(bouton_fm).index(icone)
    # 1. l'anneau blanc de FM sur la séance retenue (v7 : montré par deux switch de FM, classe posée en dur)
    if _anneau(t, src, case) is None:
        return ["switch de FM (texte ou nombre) : arguments inattendus"]
    # 2. à la place de l'icône de séance, dans les calendriers qui ont la mémoire de l'échange : notre icône si la
    # séance est modifiable, sinon l'icône de FM (copie) ; ailleurs, l'icône de FM telle quelle. Un bouton dans le
    # bouton de la case : FM le fait dans 19 de ses modèles (rangées de messages, actions rapides…)
    v = _visible(t, src, bouton_fm, V_ICI, False, NOM, index=i)
    t.elem(v)["m_Classes"] = ["margin-right-global-gap-small"]   # l'écart de l'icône de FM (4 px)
    t.styles.style(t, v, {"flex-shrink": 0, "flex-direction": "column", "justify-content": "center",
                          "align-items": "center"})
    fige = _visible(t, src, v, "Event.CanEdit", True, f"{PREFIXE}-echange-non-modifiable")
    copie = t.clone(icone, fige)
    _nommer(t, copie, f"{PREFIXE}-echange-icone-seance")
    t.elem(copie)["m_Classes"] = [c for c in t.elem(icone).get("m_Classes") or [] if c != "margin-right-global-gap-small"]
    ailleurs = _visible(t, src, bouton_fm, V_ICI, True, f"{PREFIXE}-echange-icone-fm", index=i + 1)
    t.styles.style(t, ailleurs, {"flex-shrink": 0})
    _deplacer(t, icone, ailleurs)
    v2 = _visible(t, src, v, "Event.CanEdit", False, f"{PREFIXE}-echange-modifiable", index=0)
    g = _reglage(t, src, v2, f"{PREFIXE}-echange-donnees", VARIABLES_CASE)   # v9 : comme la v7
    # 2a. rien de retenu : le clic retient cette séance
    va = _visible(t, src, g, V_ARME, True, f"{PREFIXE}-echange-libre")
    _bouton(t, src, va, BOUTON_INACTIF, [
        copier("day.Date", V_DATE),
        copier("Event.SessionIndex", V_NUMERO),
        copier("Event.SessionType", V_TYPE),
        copier("day.DayOfTheMonth", V_JOUR),
        copier("team", V_EQUIPE),
        copier("const.True", V_ARME),
    ], f"{PREFIXE}-echange-choisir")
    # 2b. une séance retenue (même équipe) : le clic échange les deux types, puis tout redevient libre (v9 : d'un bloc,
    # comme la v7 ; la v8 envoyait les étapes l'une après l'autre, sans rien y changer en jeu)
    vb = _visible(t, src, g, V_ARME, False, f"{PREFIXE}-echange-arme")
    e = _meme_equipe(t, src, vb)
    if e is None:
        return ["fonction « valeurs égales » de FM : arguments inattendus"]
    be = _bouton(t, src, e, BOUTON_INACTIF, [   # v2 : sans cadre (l'anneau, et depuis la v5 l'icône jaune, disent laquelle)
        envoyer(CALENDRIER, SEL_RETENUE, BEGIN),        # la séance retenue prend le type de celle-ci
        envoyer(CALENDRIER, SEL_RETENUE, SELECT),
        envoyer(CALENDRIER, VERS_RETENUE, CONFIRMER),
        envoyer(CALENDRIER, "null", VALIDER),
        envoyer(CALENDRIER, SEL_ICI, BEGIN),            # celle-ci prend le type de la séance retenue
        envoyer(CALENDRIER, SEL_ICI, SELECT),
        envoyer(CALENDRIER, VERS_ICI, CONFIRMER),
        envoyer(CALENDRIER, "null", VALIDER),
        copier("const.False", V_ARME),
        copier("const.EmptyString", V_JOUR),            # v7 : un texte vide, jamais égal à un jour : l'anneau et le
    ], f"{PREFIXE}-echange-echanger")                  # jaune s'éteignent (v1–v6 : const.Zero)
    # 2c. sur la séance retenue, l'icône de ce bouton passe en jaune (v7 : les deux switch, copie jaune posée en dur)
    icone_e = next((k for k in t.children(be) if t.name(k) == f"{PREFIXE}-echange-echanger-icone"), None)
    if icone_e is None or _icone_jaune(t, src, be, icone_e) is None:
        return ["icône jaune de la séance retenue : bouton ou switch de FM inattendus"]
    return [f"anneau dans {t.name(case) or typ(t, case)}, icône d'échange ({ICONE_CLASSE}) à la place de l'icône de "
            f"séance (séance non modifiable : icône de FM), jaune sur la séance retenue ({CLASSE_JAUNE})"]


# ---------- écriture ----------
def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre_original(o, nom):
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{nom} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return False
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    print(f"{nom} : remis d'origine")
    return True


def a_jour():
    for m in CALENDRIERS:
        o = ouvrir(m)
        if o is None or not calendrier_a_jour(o[3]):
            return False
    for m in CASES:
        o = ouvrir(m)
        if o is None or not any(o[3].name(r) == NOM for r in marques(o[3])):
            return False
    return True


# ---------- commandes ----------
def cmd_appliquer():
    pb = _verifier()
    if pb:
        print(f"[Kinito] Échange de séances : format de FM inattendu ({pb}), rien enregistré")
        return
    if any(ouvrir(m) is None for m in CALENDRIERS + CASES):
        print("[Kinito] Échange de séances : un modèle du calendrier d'entraînement est introuvable "
              "(renommé par une mise à jour ?), ignoré")
        return
    if a_jour():
        print("[Kinito] Échange de séances : déjà appliqué")
    else:
        src = Sources()
        if not src.ok():
            print("[Kinito] Échange de séances : morceaux de FM introuvables (bouton, SIVisible, "
                  "BindingSetter, anneau, SIEnabled, ou les lectures de la fenêtre de séance), rien enregistré")
            return
        travaux, msgs = [], []
        for m in CALENDRIERS + CASES:
            if m == PARTAGE:   # bloc partagé avec 26.7 : le modèle actuel, sans nos anciens morceaux
                o = ouvrir(m)
                retirer_morceaux(o[3])
            else:              # seul propriétaire : depuis l'original
                o = ouvrir(m, depart_original=True)
                if marques(o[3]) or calendrier_marque(o[3]):
                    print(f"[Kinito] Échange de séances : pas de sauvegarde d'origine propre de {m}, ignoré")
                    return
            r = construire_calendrier(o[3], src) if m in CALENDRIERS else construire_case(o[3], src)
            msgs += [f"{m} : {x}" for x in r]
            travaux.append(o)
        for x in msgs:
            print(f"[Kinito] Échange de séances : {x}")
        if any("introuvable" in x or "inattendus" in x for x in msgs):
            print("[Kinito] Échange de séances : rien enregistré")
            return
        for o in travaux:
            enregistrer(*o)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for m in CALENDRIERS + CASES:
        o = ouvrir(m)
        if o is None or not (marques(o[3]) or calendrier_marque(o[3])):
            continue
        if m == PARTAGE:   # bloc partagé avec 26.7 : on ne retire que nos morceaux
            retirer_morceaux(o[3])
            enregistrer(*o)
            print(f"{m} : variables et zone de lecture de l'échange retirées (le reste du bloc n'est pas touché)")
            fait = True
        else:
            fait = remettre_original(o, m) or fait
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for m in CALENDRIERS:
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        print(f"{m} : " + (f"mémoire et zone de lecture de l'échange présentes (à jour, v{VERSION})"
                           if calendrier_a_jour(t) else ("ANCIENNE version" if calendrier_marque(t) else "d'origine")))
    for m in CASES:
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        print(f"{m} : " + (f"icône d'échange présente (à jour, v{VERSION})" if any(t.name(r) == NOM for r in marques(t))
                           else ("ANCIENNE version" if marques(t) else "d'origine")))
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
            print("[Kinito] Échange de séances : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
