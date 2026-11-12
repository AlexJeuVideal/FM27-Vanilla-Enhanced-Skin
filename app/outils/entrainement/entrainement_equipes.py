"""Boutons des équipes du club (Équipe première, Réserve, U23, U21, U19…) qui ouvrent leur calendrier d'entraînement.

Une rangée de boutons FM (ceux des onglets d'équipes de Infos du club), un par équipe du club (`club.Teams`, liste FM :
seulement les équipes qui existent). Clic = calendrier d'entraînement de cette équipe (comme le lien de la vue
d'ensemble de l'entraînement de FM). Le bouton de l'équipe affichée est surligné (UniqueId de l'équipe = celui du
paramètre `team` de la page). Portail > Calendrier > Entraînement : à droite de « mois < > Aujourd'hui ».
(Boutons de l'écran Effectif : effectif\\effectif_boutons_entrainement.py, qui réutilise ce code avec MODELES_SCRIPT
= [TeamSquadBlock] et ses propres réglages ; entrainement_individuel_equipes.py et staff_fm24.py aussi.)

v8 (2026-11-12) : même rangée dans l'onglet Rencontres (Organiser amical | copie de « Partir en vacances » | équipes) ;
le clic garde l'onglet affiché (calendartab -> uipickeronglet). Onglet Général : possible (EMPLACEMENTS["general"]),
désactivé (le calendrier général ne change pas avec l'équipe).

Modèles touchés (ce script est leur seul propriétaire, appliquer repart toujours des originaux sauvegardés) :
- CalendarHeaderSeasonBlock : contrôles du haut du calendrier (mois, < >, Aujourd'hui) ; rangées ajoutées dans
  #TrainingViewControls, #GeneralViewControls et #FixturesViewControls (un par onglet).
- TeamIconAndNameCell : cellule FM inutilisée (citée par aucun bundle), réécrite en bouton d'équipe
  (copie de ClubNationInfoTabButton : clic = ouvrir l'entraînement de l'équipe, au lieu de changer d'onglet).

Usage (jeu fermé) : entrainement_equipes.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir, path_arg  # noqa: E402
from notes_installations import (first, decode_args, encode_args, _enc_varint, visible_model, make_binding,  # noqa: E402
                                 new_visible, SOURCE_COMPARE, FN_COMPARE)
from arbre import no_styles  # noqa: E402
import arbre as sm  # noqa: E402
import rencontres_version  # noqa: E402  (option « rencontres » : rangée de l'onglet Rencontres ou version Kinito)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
#  largeur : px réservés à la rangée (la liste FM défile si elle ne suffit pas, rétrécit si la place manque)
#  hauteur : px (= hauteur des boutons FM : rangée centrée comme les boutons voisins)
#  descendre : px, décalage vers le bas (+) ou le haut (-) pour s'aligner sur les boutons voisins
#  marge : px, écart à gauche
#  largeur None : la rangée prend la largeur de ses boutons (liste FM non virtualisée) -> « Partir en vacances » collé
#  vacances : « Partir en vacances » (recopié de l'onglet Général) AVANT la rangée (juste après les boutons FM)
#  écarts : 8 px = écart FM entre les flèches < > / « Aujourd'hui » / « Organiser amical » (global-gap-regular)
EMPLACEMENTS = {
    "calendrier": {"actif": True, "liste": "human.Club.Teams", "largeur": 520, "hauteur": 32, "descendre": -0.5,
                   "marge": 0},   # #DropdownButtons a déjà 8 px à droite (même écart qu'Aujourd'hui | vacances)
    # Général : retiré (2026-11-12, vu en jeu : le calendrier général est le même pour toutes les équipes)
    "general": {"actif": False, "liste": "human.Club.Teams", "largeur": None, "hauteur": 32, "descendre": -0.5,
                "marge": 8},
    # Rencontres : Organiser amical | Partir en vacances | équipes
    "rencontres": {"actif": True, "liste": "human.Club.Teams", "largeur": None, "hauteur": 32, "descendre": -0.5,
                   "marge": 8, "vacances": True},
    "effectif": {"actif": True, "texte": 1378, "descendre": 0, "marge": 0},   # réglé par effectif_boutons_entrainement.py
}
EFFECTIF_INDIVIDUEL = {"actif": True, "texte": 8962, "ecart": 8}           # idem
EFFECTIF_PROGRAMME = {"actif": True, "texte": 8487, "ecart": 8}            # idem
ECART_VACANCES = 8      # px entre « Organiser amical » et « Partir en vacances » (Rencontres)
SURLIGNER = True        # bouton de l'équipe affichée surligné
# =====================================================================================================

VERSION = 12  # v2 : alignement (hauteur 32 + décalage), rangée aussi sur l'écran Effectif ;
              # v3 : calendrier descendre 2 -> 0.5 (v1 : 3 px trop haut à l'écran, v2 : 2 px trop bas) ;
              # v4 : calendrier -0.5 (1 px plus haut) ; Effectif : un seul bouton « Entraînement » de l'équipe affichée
              # v5 : Effectif : 2e bouton « Entraînement individuel » à droite
              # v6 : rangée aussi dans Général et Rencontres (+ « Partir en vacances » dans Rencontres), clic = même
              #      onglet pour l'équipe choisie ; bouton seul (club à une équipe) arrondi des deux côtés
              # v7 : Général / Rencontres : rangée vide en jeu (liste virtualisée sans largeur) -> WrappedObjectList,
              #      boutons séparés arrondis
              # v8 : Général retiré ; Rencontres : Organiser amical | Partir en vacances | équipes ; écarts 8 px
              #      (comme entre les flèches) au lieu de 32
              # v9 : Effectif : 3e bouton « Programme des rencontres » (calendrier, onglet Rencontres de l'équipe)
              # v10 : calendrier : rangée + « Partir en vacances » seulement pour les équipes du club du joueur
              # v11 : condition team.IsHuman (au lieu de « même club » : la U23 allemande est un club à part, rangée
              #       cachée sur son calendrier, vu en jeu 2026-10-30) ; calendrier + effectif
              # v12 : v11 cachait aussi U19 / U23 (IsHuman = équipe entraînée par le joueur, vu en jeu) -> BindingSetter
              #       « human.Club.Teams contient team » (la liste même des boutons) > SIVisible
ENTETE = "CalendarHeaderSeasonBlock"
EFFECTIF = "TeamSquadBlock"
BOUTON = "TeamIconAndNameCell"
GUID_BOUTON = "a275ff26e28e2ad4481ce05aa8d1564e"   # TeamIconAndNameCell (catalogue Addressables)
BOUTON_SOURCE = "ClubNationInfoTabButton"           # bouton FM des onglets d'équipes (Infos du club)
LISTE_SOURCE = "ClubInfoReportBlock"                # sa liste horizontale sur club.Teams
GUID_LISTE_FM = "49e2bf75b4088f84fbb4a5044f74f9c1"  # ClubNationInfoTabButton (RowTemplate de cette liste)
ECRAN = "9925aa51dd9e78f438d92dc65b26d9cc"          # CalendarToolTrainingTab (calendrier, onglet Entraînement)
ECRAN_CALENDRIER = "373351a1f7249424eb22205fc799d1b9"   # CalendarTool (onglet donné par calendartab, comme FM)
PARAM_ONGLET = "uipickeronglet"                     # onglet affiché (calendartab), vu depuis le bouton
PARAM_SEPARER = "uipickerseparer"                   # vrai : boutons séparés arrondis (liste sans rowindex)
ECART_BOUTONS = 8                                   # px entre deux boutons séparés
RAYON = 4                                           # px, arrondi FM des boutons (--numbers-border-radius-small)
ECRAN_INDIVIDUEL = "41012275212b88b46957d71fc17c5876"   # TeamIndividualTrainingTool (entraînement individuel)
# CalendarToolFixturesTab, ouvert avec calendartab = 2 + team par la tuile FM SquadFixtureScheduleTile_*
ECRAN_RENCONTRES = "cc93f9746a2f0204d8d5a7bcb3fb316f"
TYPE_EQUIPE = 1145176088
PARAM_EQUIPE = "uipickerequipe"                     # équipe affichée, vue depuis le bouton
PREFIXE = "UIPickerEquipesEntrainement"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
NOM_BOUTON = f"UIPickerBoutonEquipe-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "entrainement_equipes.actif")

sm.PROPRIETES.setdefault("width", (131105, 3))
sm.PROPRIETES.setdefault("height", (131087, 3))
sm.PROPRIETES.setdefault("margin-left", (131091, 3))
sm.PROPRIETES.setdefault("margin-right", (131092, 3))
sm.PROPRIETES.setdefault("flex-direction", (131083, 7))
sm.PROPRIETES.setdefault("flex-wrap", (131086, 7))
sm.PROPRIETES.setdefault("top", (131104, 3))
sm.PROPRIETES.setdefault("position", (131102, 7))


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE) or t.name(r).startswith("UIPickerBoutonEquipe")]


# ---------- événement « ouvrir un écran » de FM (action 211,101,102,7) ----------
def _texte(s):
    s = s.encode()
    return b"\x01\x01" + _enc_varint(len(s)) + s


def _bloc(b):
    return struct.pack("<i", len(b)) + b


def evenement_ecran(guid, params):
    """événement de bouton qui ouvre l'écran <guid> avec les paramètres [(nom, chemin)] (format de FM, vérifié en
    refaisant à l'identique l'événement de TrainingOverviewCalendarBlock)"""
    corps = bytes([211, 101, 102, 7, 2])
    corps += _bloc(bytes([1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0]))
    corps += _bloc(bytes([1, 0, 1, 1, 1, 32]) + guid.encode() + bytes([1, 0, 3, 0, 0, 0, 1, 1, 0]))
    corps += b"\x01\x01" + _enc_varint(len(params))
    for nom, chemin in params:
        corps += _bloc(_texte(nom) + _bloc(_texte(chemin)) + b"\x00")
    corps += b"\x00\x00"
    return list(bytes([1, 1, 1, 1, 1]) + _bloc(corps) + b"\x00")


def _verifier_evenement():
    attendu = [1, 1, 1, 1, 1, 134, 0, 0, 0, 211, 101, 102, 7, 2, 11, 0, 0, 0, 1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0, 47, 0,
               0, 0, 1, 0, 1, 1, 1, 32] + list(ECRAN.encode()) + [1, 0, 3, 0, 0, 0, 1, 1, 0, 1, 1, 2, 31, 0, 0, 0, 1,
               1, 11] + list(b"calendartab") + [12, 0, 0, 0, 1, 1, 9] + list(b"const.one") + [0, 19, 0, 0, 0, 1, 1,
               4] + list(b"team") + [7, 0, 0, 0, 1, 1, 4] + list(b"team") + [0, 0, 0, 0]
    return evenement_ecran(ECRAN, [("calendartab", "const.one"), ("team", "team")]) == attendu


# ---------- le bouton (TeamIconAndNameCell réécrit) ----------
def _chemins(args, remplacer):
    for a in args:
        if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            p = a[1][1:]
            n = p[0]  # longueur (< 128 ici)
            ancien = p[1:1 + n].decode()
            if ancien in remplacer:
                nouveau = remplacer[ancien].encode()
                a[1] = b"\x01" + _enc_varint(len(nouveau)) + nouveau
    return args


def construire_bouton(t, src):
    racine = t.tt["m_VisualTree"]["rid"]
    s_racine = src.tt["m_VisualTree"]["rid"]
    comp = next((r for r in src.children(s_racine) if typ(src, r) == "ComponentElement"), None)
    if comp is None:
        return ["bouton d'équipe FM introuvable"]
    for k in list(t.children(racine)):
        t.remove(k)
    b = t.clone(comp, racine, src=src)
    t.styles.copy_from(src.styles, t, b)
    t.sd(b)["name"] = NOM_BOUTON
    t.sd(b)["name_UxmlAttributeFlags"] = 1

    # version téléphone retirée (onglet iOS, modèle inclus)
    for r in list(t.walk(b)):
        if r in t.refs and t.name(r) == "PhoneLandscapeStyleSetter":
            t.remove(r)

    composants = [c["rid"] for c in t.sd(b).get("m_components") or []]
    attente = next((c for c in composants if "BindingExpect" in t.refs[c]["type"]["class"]), None)
    reglage = next((c for c in composants if "BindingSetter" in t.refs[c]["type"]["class"]), None)
    if attente is None or reglage is None:
        return ["composants du bouton FM introuvables"]

    # paramètres : row (équipe), rowindex (début / milieu / fin de la rangée), équipe affichée et onglet du
    # calendrier affiché (facultatifs)
    params = t.refs[attente]["data"]["Parameters"]
    p = copy.deepcopy(params[0])
    p["name"], p["type"]["id"], p["isOptional"] = PARAM_EQUIPE, TYPE_EQUIPE, 1
    o = copy.deepcopy(params[0])
    o["name"], o["type"]["id"], o["isOptional"] = PARAM_ONGLET, 0, 1
    # boutons séparés (liste à largeur du contenu, Général / Rencontres) : pas de rowindex fourni -> -1 (ni début ni
    # fin), uipickerseparer vrai -> 4e cas (bouton arrondi des deux côtés)
    s = copy.deepcopy(params[0])
    s["name"], s["type"]["id"], s["isOptional"] = PARAM_SEPARER, 0, 1
    s["defaultValue"]["m_scopeValue"] = {"m_serializedData": "Bool|0|"}
    for x in params:
        if x["name"] == "rowindex":
            x["isOptional"] = 1
            x["defaultValue"]["m_kind"] = 0
            x["defaultValue"]["m_scopeValue"] = {"m_serializedData": "Int|-1|"}
    params[:] = [x for x in params if x["name"] != "selected-tab"] + [p, o, s]
    for e in (t.elem(r) for r in t.walk(b)):
        for prop in e.get("m_Properties") or []:
            if prop["name"] == "params":
                prop["value"] = prop["value"].replace("selected-tab:invalid:False",
                                                      f"{PARAM_EQUIPE}:team:True,{PARAM_ONGLET}:invalid:True,"
                                                      f"{PARAM_SEPARER}:invalid:True").replace(
                    "rowindex:invalid:False", "rowindex:invalid:True")

    # surbrillance : même équipe que celle affichée (UniqueId), au lieu de « même numéro d'onglet »
    remplacer = {"rowindex": "row.UniqueId", "selected-tab": f"{PARAM_EQUIPE}.UniqueId"}
    for f in t.refs[reglage]["data"]["BindFunction"]:
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        if not any(b"isSelected" in a[1] for a in args):
            continue
        if SURLIGNER:
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(_chemins(args, remplacer))
        else:   # jamais surligné
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(
                _chemins(args, {"rowindex": "const.zero", "selected-tab": "const.One"}))

    # bouton seul (club à une équipe) : FM le dessine en « fin de rangée » (arrondi à droite seulement) ->
    # 4e cas du switch (buttontype 3 = début ET fin) = copie du « début de rangée », arrondi des 4 coins
    msg_seul = bouton_seul(t, b, reglage)
    if msg_seul is None:
        return ["switch début / milieu / fin du bouton FM introuvable"]

    # clic = même onglet du calendrier (paramètre de la rangée : Général, Entraînement, Rencontres), cette équipe
    ev = evenement_ecran(ECRAN_CALENDRIER, [("calendartab", PARAM_ONGLET), ("team", "row")])
    boutons = [r for r in t.walk(b) if typ(t, r) == "SIButton"]
    for r in boutons:
        t.sd(r)["Events"]["m_bytes"] = list(ev)
    if not boutons:
        return ["boutons du modèle FM introuvables"]
    return [f"bouton d'équipe : copie de {BOUTON_SOURCE}, clic = même onglet du calendrier pour l'équipe"
            + (", équipe affichée surlignée" if SURLIGNER else ""), msg_seul]


COINS = {"border-top-left-radius": (458764, 3), "border-top-right-radius": (458765, 3),
         "border-bottom-left-radius": (458759, 3), "border-bottom-right-radius": (458760, 3)}
for _k, _v in COINS.items():
    sm.PROPRIETES.setdefault(_k, _v)


def bouton_seul(t, b, reglage):
    switch = next((r for r in t.walk(b) if t.name(r) == "FMTabs"), None)
    if switch is None or len(t.children(switch)) != 3:
        return None
    debut = t.children(switch)[0]
    seul = t.clone(debut, switch, None)
    for r in t.walk(seul):
        if typ(t, r) == "SIButton":   # + écart à droite (boutons séparés ; sans effet sur un bouton seul en fin)
            t.styles.style(t, r, dict({k: RAYON for k in COINS}, **{"margin-right": ECART_BOUTONS}))
    fonctions = t.refs[reglage]["data"]["BindFunction"]
    i, deux = next(((i, f) for i, f in enumerate(fonctions) if any(
        a[1] == b"\x01\tconst.Two" for a in decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"]))), (None, None))
    if deux is None:
        return None
    trois = copy.deepcopy(deux)
    args = decode_args(trois["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[1] == b"\x01\tconst.Two":
            a[1] = b"\x01\x0bconst.Three"
        elif a[0].startswith(b"SI.VisualScripting.StructListVisualArg"):
            a[1] = b"\x02\x01\x08is-start\x00\x01\x06is-end\x00"   # is-start ET is-end (sans inversion)
    trois["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    separe = copy.deepcopy(trois)   # même 4e cas si la rangée demande des boutons séparés
    args = decode_args(separe["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0].startswith(b"SI.VisualScripting.StructListVisualArg"):
            a[1] = b"\x01\x01" + _enc_varint(len(PARAM_SEPARER)) + PARAM_SEPARER.encode() + b"\x00"
    separe["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    fonctions[i + 1:i + 1] = [trois, separe]
    return f"bouton seul (club à une équipe) / boutons séparés : arrondis des deux côtés ({RAYON} px)"


# ---------- la rangée ----------
class Morceaux:
    """morceaux de FM recopiés dans les rangées"""

    def __init__(self):
        self.lst = hp.src_tree(LISTE_SOURCE)
        self.liste = self.lst and first(self.lst, lambda r: typ(self.lst, r) == "StreamedObjectList" and (
            self.lst.sd(r).get("RowTemplate") or {}).get("m_AssetGUID") == GUID_LISTE_FM)
        # liste à la largeur de son contenu (non virtualisée, comme les pastilles Pour / Contre de l'en-tête)
        self.wlst = hp.src_tree("TeamMeetingBlock")
        self.wliste = self.wlst and first(self.wlst, lambda r: self.wlst.name(r) == "Players"
                                          and typ(self.wlst, r).endswith("WrappedObjectList"))
        self.ent = hp.src_tree(ENTETE)
        self.remap = self.ent and first(self.ent, lambda r: typ(self.ent, r) == "BindingRemapper")
        self.s_vis, self.vis = visible_model(SOURCE_COMPARE, FN_COMPARE)
        e = self.ent
        self.aujourdhui = e and first(e, lambda r: typ(e, r) == "SIButton" and r in e.parent
                                      and e.name(e.parent[r]) == "Today")   # bouton « Aujourd'hui » de FM

    def ok(self):
        return None not in (self.liste, self.wliste, self.remap, self.vis)


# v12 : condition « l'équipe affichée est une des équipes du club du joueur » (human.Club.Teams contient team : la
# liste même des boutons). v10 « même club » (team.Club == human.Club) : cachée sur la U23 allemande (club à part pour
# FM) ; v11 team.IsHuman : vrai seulement pour l'équipe que le joueur entraîne (cachée sur U19 / U23, vu en jeu)
VAR_CLUB = "uipickerequipeduclub"                 # variable Bool posée par le BindingSetter, lue par le SIVisible
SOURCE_CALCUL = ("GoOnHolidayWidget", "BindingSetter")   # BindingSetter de FM (variables + fonctions)
FN_CONTIENT = ("ControllerRemapSettingsRow", "53435a45561e1754cba90ac41c45e5a7")   # BindListContainsValueToDestination
_SOURCES = {}


def _chemin_arg(chemin):
    chemin = chemin.encode()
    return b"\x01" + _enc_varint(len(chemin)) + chemin


def _sources_club():
    """(arbre, BindingSetter de FM, fonction « contient » de FM, arbre et SIVisible modèle) ; None si introuvable"""
    if "ok" not in _SOURCES:
        o = ouvrir(SOURCE_CALCUL[0], depart_original=True)
        calc = o and first(o[3], lambda r: typ(o[3], r) == SOURCE_CALCUL[1])
        fn = None
        f = ouvrir(FN_CONTIENT[0], depart_original=True)
        for r in (f[3].walk() if f else []):
            fs = f[3].sd(r).get("BindFunction")
            fn = next((copy.deepcopy(x) for x in (fs if isinstance(fs, list) else [fs])
                       if isinstance(x, dict) and (x.get("m_target") or {}).get("m_guid") == FN_CONTIENT[1]), None)
            if fn is not None:
                break
        s_vis, vis = visible_model(SOURCE_COMPARE, FN_COMPARE)
        _SOURCES["ok"] = None if None in (calc, fn, vis) else (o[3], calc, fn, s_vis, vis)
    return _SOURCES["ok"]


def visible_equipe_geree(t, parent, index, nom, classes=(), liste="human.Club.Teams", equipe="team"):
    """BindingSetter de FM (variable VAR_CLUB = <liste> contient <equipe>, nommé nom) > SIVisible sur VAR_CLUB (classes
    données) ; (haut, SIVisible) — les enfants vont dans le SIVisible, sa place (largeur, marges) aussi : caché, rien ne
    reste à l'écran. None si les morceaux de FM sont introuvables"""
    s = _sources_club()
    if s is None:
        return None
    sc, calc, fn, s_vis, vis = s
    haut = t.clone(calc, parent, index, src=sc)
    _vide(t, haut)
    sd = t.sd(haut)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1
    sd["ValueVariables"] = [{"m_name": VAR_CLUB, "m_scopeValue": {"m_serializedData": "Bool|0|"}}]
    sd["ReferenceVariables"] = []
    sd["ValueVariables_UxmlAttributeFlags"] = sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    f = copy.deepcopy(fn)
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    attendu = ["BooleanVisualArg", "BindingPath]", "BindingPath]", "BooleanVisualArg", "BindingPath]"]
    if len(args) != len(attendu) or any(not bytes(a[0]).endswith(x.encode()) for a, x in zip(args, attendu)):
        return None
    for a, v in zip(args, [b"\x00", _chemin_arg(liste), _chemin_arg(equipe), None, _chemin_arg(VAR_CLUB)]):
        if v is not None:
            a[1] = v
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["BindFunction"], sd["BindFunction_UxmlAttributeFlags"] = [f], 1
    t.elem(haut)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.styles.style(t, haut, {"flex-shrink": 1, "min-width": 0})

    b = copy.deepcopy(s_vis.sd(vis)["Binding"])
    b["m_kind"] = 1
    b["m_direct"] = {"Path": {"m_path": VAR_CLUB}, "Nullable": 0}
    b["m_visualFunction"]["m_target"]["m_guid"] = ""
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    b["m_visualFunction"]["m_outputs"]["m_variable"]["m_argumentBytes"] = []
    # nom hors de PREFIXE : Kinito 26.10 renomme le haut et refuse tout PREFIXE restant dedans
    v = new_visible(t, s_vis, vis, haut, None, "UIPickerEquipeDuClub", b, classes)
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.sd(v)["InvertDirectBinding"] = 0
    return haut, v


def ancienne_condition(t):
    """vrai si un de nos SIVisible (UIPicker…) a encore une ancienne condition (v10 « même club », v11 team.IsHuman) :
    à refaire (sert aux scripts qui posent rangee(meme_club=True) pour se savoir pas à jour)"""
    for r in t.walk():
        if typ(t, r) != "SIVisible" or not t.name(r).startswith("UIPicker"):
            continue
        b = t.sd(r).get("Binding") or {}
        if b.get("m_kind") == 2 and b"Club.UniqueId" in bytes(
                b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]):
            return True
        if b.get("m_kind") == 1 and b["m_direct"]["Path"]["m_path"] in ("team.IsHuman", "Team.IsHuman"):
            return True
    return False


def _vide(t, r):
    no_styles(t, r)
    for k in list(t.children(r)):
        t.remove(k)
    t.elem(r)["m_Classes"] = []


def rangee(t, mx, parent, index, reglage, meme_club=False, nom=None, guid=None):
    """rangée des équipes sous parent (à la position index) : [SIVisible même club] > BindingRemapper (équipe affichée
    -> uipickerequipe, onglet du calendrier -> uipickeronglet) > liste FM horizontale de boutons d'équipe
    (guid = autre cellule bouton que celle du calendrier, ex. effectif_equipes)"""
    guid = guid or GUID_BOUTON
    auto = reglage.get("largeur") is None
    place = {"height": reglage["hauteur"], "margin-left": reglage["marge"], "top": reglage["descendre"]}
    place.update({"flex-shrink": 0} if auto else {"width": reglage["largeur"], "flex-shrink": 1, "min-width": 0})
    if meme_club:   # v12 : équipe du club du joueur (human.Club.Teams contient team), U23 / équipe B comprises
        x = visible_equipe_geree(t, parent, index, NOM_RACINE)
        if x is None:   # morceaux de FM introuvables : rien posé (les appelants le voient : « introuvable »)
            return None
        haut, dehors = x
        # la place sur le haut (les appelants qui réécrivent sa règle : Kinito 26.10 / 26.15), le SIVisible le remplit ;
        # vraie largeur fixe (> 1 px, ex. 26.2 : 520) : largeur et marge sur le SIVisible, caché il ne reste pas de vide
        dedans = ("width", "margin-left") if (reglage.get("largeur") or 0) > 1 else ()
        t.styles.style(t, haut, {k: v for k, v in place.items() if k not in dedans})
        t.styles.style(t, dehors, dict({"flex-grow": 1, "flex-shrink": 1, "min-width": 0},
                                       **{k: place[k] for k in dedans}))
        parent, index = dehors, None

    c = t.clone(mx.remap, parent, index, src=mx.ent)
    _vide(t, c)
    sd = t.sd(c)
    sd["name"], sd["name_UxmlAttributeFlags"] = (f"{PREFIXE}-equipe" if meme_club else nom or NOM_RACINE), 1
    m = copy.deepcopy(sd["Mappings"][0])
    m["from"], m["to"]["m_path"], m["type"]["id"] = PARAM_EQUIPE, "team", TYPE_EQUIPE
    o = copy.deepcopy(sd["Mappings"][0])
    o["from"], o["to"]["m_path"], o["type"]["id"] = PARAM_ONGLET, "calendartab", 0
    sd["Mappings"] = [m] if meme_club else [m, o]
    t.styles.style(t, c, {"flex-grow": 1} if meme_club else place)

    if auto:
        # liste FM non virtualisée (WrappedObjectList : largeur de son contenu ; v6 essayée en StreamedObjectList sans
        # largeur : vide en jeu). Elle ne donne pas de rowindex -> boutons séparés, arrondis (uipickerseparer)
        s = copy.deepcopy(m)
        s["from"], s["to"]["m_path"], s["type"]["id"] = PARAM_SEPARER, "const.True", 0
        sd["Mappings"].append(s)
        w = t.clone(mx.wliste, c, src=mx.wlst)
        _vide(t, w)
        wd = t.sd(w)
        wd["name"] = ""
        wd["ItemTemplate"] = {"m_AssetGUID": guid,"m_SubObjectName": "", "m_SubObjectType": ""}
        wd["VisualFuncBinding"] = path_arg(wd["VisualFuncBinding"], reglage["liste"])
        wd["ItemParamName"] = "row"
        wd["ItemUssClassName"] = "flex-no-shrink-class"
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "nowrap", "flex-shrink": 0})
        return c
    w = t.clone(mx.liste, c, src=mx.lst)
    _vide(t, w)
    wd = t.sd(w)
    wd["RowTemplate"] = {"m_AssetGUID": guid,"m_SubObjectName": "", "m_SubObjectType": ""}
    wd["Binding"]["m_visualFunction"] = path_arg(wd["Binding"]["m_visualFunction"], reglage["liste"])
    t.styles.style(t, w, {"flex-grow": 1})
    return c


ZONES_CALENDRIER = [   # (emplacement, contrôles FM de l'onglet, rangée insérée avant cet enfant (None = à la fin))
    ("calendrier", "TrainingViewControls", None),
    ("general", "GeneralViewControls", "ActionButtons"),      # Aujourd'hui | équipes | Partir en vacances
    ("rencontres", "FixturesViewControls", None),             # Organiser amical | Partir en vacances | équipes
]


def construire_calendrier(t, mx):
    msgs = []
    vacances = first(t, lambda r: t.name(r) == "ActionButtons" and t.name(t.parent.get(r)) == "GeneralViewControls")
    for cle, nom_zone, avant in ZONES_CALENDRIER:
        reglage = EMPLACEMENTS[cle]
        if not reglage["actif"]:
            continue
        zone = first(t, lambda r: t.name(r) == nom_zone)
        if zone is None:
            return [f"contrôles du calendrier ({nom_zone}) introuvables"]
        index = None
        if avant:
            k = next((k for k in t.children(zone) if t.name(k) == avant), None)
            index = t.children(zone).index(k) if k is not None else None
        # v10 : tout dans un SIVisible « équipe du club du joueur » (vu en jeu : rangée + vacances sur le calendrier
        # de Newcastle en jouant Liverpool)
        x = visible_equipe_geree(t, zone, index, NOM_RACINE if cle == "calendrier" else f"{PREFIXE}-{cle}",
                                 ["row-direction-normal", "align-items-center"])
        if x is None:
            return ["morceaux de FM de la condition « équipe du club » (BindingSetter, fonction contient) introuvables"]
        haut, club = x
        t.styles.style(t, haut, {"flex-shrink": 0} if reglage.get("largeur") is None
                       else {"flex-shrink": 1, "min-width": 0})
        t.styles.style(t, club, {"flex-shrink": 0} if reglage.get("largeur") is None
                       else {"flex-shrink": 1, "min-width": 0})
        if reglage.get("vacances"):   # avant les équipes, juste après les boutons FM
            if vacances is None:
                return ["bouton « Partir en vacances » de FM introuvable"]
            v = t.clone(vacances, club)
            t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = f"{PREFIXE}-vacances-{cle}", 1
            t.styles.style(t, v, {"margin-left": ECART_VACANCES})
            msgs.append(f"calendrier ({cle}) : « Partir en vacances » à côté des boutons FM")
        if cle == "rencontres" and rencontres_version.kinito():
            msgs.append("calendrier (rencontres) : pas de rangée des équipes (version Kinito : boutons dans le bandeau)")
            continue
        rangee(t, mx, club, None, reglage, nom=f"{PREFIXE}-equipes-{cle}")
        msgs.append(f"calendrier ({cle}) : rangée des équipes ({reglage['liste']}), équipes du club du joueur seulement")
    return msgs


def construire_effectif(t, mx):
    """un bouton FM normal « Entraînement » (copie du bouton « Aujourd'hui » du calendrier) : calendrier
    d'entraînement de l'équipe affichée ; seulement pour les équipes du club du joueur"""
    reglage = EMPLACEMENTS["effectif"]
    vues = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "TableViewDropdown")
    switch = vues and t.parent.get(vues)
    if switch is None or typ(t, switch) != "BindableSwitchElement" or mx.aujourdhui is None:
        return ["menu des vues de l'écran Effectif / bouton « Aujourd'hui » de FM introuvable"]
    p = t.parent[switch]
    x = visible_equipe_geree(t, p, t.children(p).index(switch) + 1, NOM_RACINE,
                             ["row-direction-normal", "align-items-center"])
    if x is None:
        return ["morceaux de FM de la condition « équipe du club » (BindingSetter, fonction contient) introuvables"]
    haut, vis = x
    t.styles.style(t, haut, {"flex-shrink": 0})
    t.styles.style(t, vis, {"margin-left": reglage["marge"], "top": reglage["descendre"], "flex-shrink": 0})

    def bouton(nom, texte, dbg, evenement):
        x = t.clone(mx.aujourdhui, vis, src=mx.ent)
        _vide(t, x)
        t.elem(x)["m_Classes"] = ["buttons-button-base-default", "button-size-medium"]
        sd = t.sd(x)
        sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1
        sd["InputActionRef"]["m_inputActionAsset"]["m_AssetGUID"] = ""   # pas de raccourci clavier (celui d'Aujourd'hui)
        sd["InputActionRef"]["m_actionID"] = ""
        f = sd["BindTextFunction"]
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"TranslationID]"):
                a[1] = struct.pack("<i", texte) + b"\x01" + _enc_varint(len(dbg)) + dbg
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        sd["Events"]["m_bytes"] = evenement
        return x

    bouton(f"{PREFIXE}-bouton", reglage["texte"], b"UIPicker Training",
           evenement_ecran(ECRAN, [("calendartab", "const.one"), ("team", "team")]))
    msgs = ["effectif : bouton « Entraînement » de l'équipe affichée après le menu des vues "
            "(équipes du club du joueur seulement)"]
    if EFFECTIF_INDIVIDUEL["actif"]:
        x = bouton(f"{PREFIXE}-individuel", EFFECTIF_INDIVIDUEL["texte"], b"UIPicker Individual Training",
                   evenement_ecran(ECRAN_INDIVIDUEL, [("team", "team"), ("selectedplayer", "null")]))
        t.styles.style(t, x, {"margin-left": EFFECTIF_INDIVIDUEL["ecart"]})
        msgs.append("effectif : bouton « Entraînement individuel » à droite (entraînement individuel de l'équipe)")
    if EFFECTIF_PROGRAMME["actif"]:
        x = bouton(f"{PREFIXE}-programme", EFFECTIF_PROGRAMME["texte"], b"UIPicker Fixture Schedule",
                   evenement_ecran(ECRAN_RENCONTRES, [("calendartab", "const.two"), ("team", "team")]))
        t.styles.style(t, x, {"margin-left": EFFECTIF_PROGRAMME["ecart"]})
        msgs.append("effectif : bouton « Programme des rencontres » à droite (rencontres de l'équipe)")
    return msgs


CONSTRUIRE = {ENTETE: construire_calendrier, EFFECTIF: construire_effectif}
MODELES_RANGEE = {ENTETE: "calendrier", EFFECTIF: "effectif"}
# modèles de CE script (calendrier) ; effectif\effectif_boutons_entrainement.py réutilise ce code avec [EFFECTIF]
MODELES_SCRIPT = [ENTETE, BOUTON]


def modeles():
    return [m for m in MODELES_SCRIPT if m != BOUTON and EMPLACEMENTS[MODELES_RANGEE[m]]["actif"]] \
        + [m for m in MODELES_SCRIPT if m == BOUTON]


def rangee_rencontres_ok(t):
    """rangée de l'onglet Rencontres présente si et seulement si voulue (option « rencontres » : version Kinito sans)"""
    voulue = EMPLACEMENTS["rencontres"]["actif"] and not rencontres_version.kinito()
    return (first(t, lambda r: t.name(r) == f"{PREFIXE}-equipes-rencontres") is not None) == voulue


# ---------- commandes ----------
def cmd_appliquer():
    if not _verifier_evenement():
        print("équipes à l'entraînement : format d'événement inattendu, rien enregistré")
        return
    tous = list(MODELES_SCRIPT)
    actuels = {m: ouvrir(m) for m in tous}
    if None in actuels.values():
        print("modèles du calendrier / de l'effectif introuvables (renommés par une mise à jour ?), ignoré")
        return
    a_jour = all(any(actuels[m][3].name(r) == (NOM_BOUTON if m == BOUTON else NOM_RACINE)
                     for r in marques(actuels[m][3])) for m in modeles()) and \
        not any(marques(actuels[m][3]) for m in tous if m not in modeles()) and \
        (ENTETE not in actuels or rangee_rencontres_ok(actuels[ENTETE][3]))
    if a_jour:
        print("équipes à l'entraînement : déjà appliqué")
    else:
        ancien = any(marques(v[3]) for v in actuels.values())
        travail = {m: ouvrir(m, depart_original=True) for m in tous}
        if any(marques(v[3]) for v in travail.values()):
            print("équipes à l'entraînement : pas de sauvegarde d'origine propre, ignoré")
            return
        src_b, mx = ouvrir(BOUTON_SOURCE), Morceaux()
        if src_b is None or not mx.ok():
            print("équipes à l'entraînement : morceaux de FM (bouton, liste d'équipes) introuvables, rien enregistré")
            return
        msgs = construire_bouton(travail[BOUTON][3], src_b[3]) if BOUTON in travail else []
        for m in modeles():
            if m != BOUTON:
                msgs += CONSTRUIRE[m](travail[m][3], mx)
        msgs += ["ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"équipes à l'entraînement : {m}")
        if any("introuvable" in m for m in msgs):
            print("équipes à l'entraînement : rien enregistré")
            return
        for bundle, obj, tt, t in travail.values():
            t.finish()
            t.styles.save()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for m in MODELES_SCRIPT:
        o = ouvrir(m)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{m} : remis d'origine")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for m in MODELES_SCRIPT:
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        cible = NOM_BOUTON if m == BOUTON else NOM_RACINE
        etat = "à jour" if any(t.name(r) == cible for r in marques(t)) else "ANCIENNE version"
        print(f"{m} : " + (f"appliqué ({etat}, v{VERSION})" if marques(t) else "d'origine"))
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
            print("équipes à l'entraînement : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
