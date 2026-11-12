"""ESSAI : Compétition > Vue d'ensemble refaite (maquette validée par le joueur le 2026-11-12).

Championnat (CompetitionSiteBlock, #ActiveNoParent) — v3 (maquette du joueur, 2026-11-12) :
  [classement FM, plus étroit] | [NOTRE tuile stats joueurs 3x2 : 6 stats, top 3 de chacune] |
  [équipe type des médias SANS la liste des joueurs clés, puis anciens vainqueurs (tuile FM)]
  Transferts et articles cachés (boîte absolue 0 px, éléments FM gardés). Réputation retirée (championnat).
  Tuile stats : cadre de la tuile FM (tile-wide-8x4 de CompetitionSitePlayerStatsTile_8x4 : titre, clic vers les
  stats ; sa bascule « pas de données » retirée en v5) ; chaque case = variables comme le bloc stats téléphone de FM (type, catégorie et
  phase nulles) + `comp.PlayerStats` → liste `playerstatslist.Players` (3 lignes visibles), titre
  `comp.PlayerTopStats.LongString`. Ligne = MODELE_LIGNE (modèle de FM cité par RIEN, réécrit : nom + photo de
  RecordLinePerson, `item.statvalue`).
Coupe (CompetitionSiteBlock_Cup) :
  - avant le début : anciens vainqueurs | clubs (FM) + colonne réputation ;
  - commencée : stats joueurs | stats équipes (FM) + colonne réputation / anciens vainqueurs à la place des articles.
Le bandeau des matchs (en haut de la page) n'est pas dans ces modèles : intouché.

- Tuiles FM incluses telles quelles (elles attendent `comp`, déjà là) ; 11 des médias : CompLeagueStatsBlock dans un
  BindingRemapper showDetails = const.False (paramètre FM qui cache la liste). Le terrain de FM n'existe qu'en grande
  fenêtre (app.GridBreakpointIsLarge) : en fenêtre plus petite, la colonne de droite = anciens vainqueurs seuls.
- Seul écrivain de ces deux modèles ; appliquer repart de l'original, retirer le remet.
v1 (2026-11-12) : premier essai. Vu en jeu : tout s'arrêtait à mi-hauteur (réputation tassée, gardien coupé).
v2 : rangée étirée sur toute la hauteur (parents jusqu'à #Container) ; réputation 2 / stats 3.
v3 : classement | notre tuile stats 3x2 (top 3) | 11 + anciens vainqueurs. Numéros des stats (TYPES) : 27 = note
  moyenne (sûr, CompetitionHighestAverageRatingLine) ; les autres pris dans la tuile FM, À VÉRIFIER en jeu (titres).
v4 : v3 vue en jeu = tuile vide (titre seul) : bascule HasStartedSwitch étirée + hauteur mini des rangées.
v5 : v4 vue = toujours vide, rien dans Player.log : bascule HasStartedSwitch retirée (#Frame dans la tuile), rangées
  align-self stretch (plus de « pas de données » avant le début : listes vides).
v6 : v5 vue = toujours vide -> tuile 3x2 MISE DE CÔTÉ (joueur, 2026-11-12) : TUILE_MAISON = False, tuile stats de FM
  au milieu ; MatchScorelineKickoffCell remis d'origine (retiré au passage).

Menu Outils FM.bat (jeu fermé) : 124 (125 à blanc). Retiré au début du choix 1 (catalogue.ESSAIS).
Usage : essai_competition_vue.py appliquer [--dry-run] | retirer [--dry-run] | etat
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first  # noqa: E402
import club_page_bas as cpb  # noqa: E402  (move)
from elements import copy_usings  # noqa: E402
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
PART_TABLE = 23         # parts de largeur : classement | stats | droite (v3 : classement plus étroit)
PART_CENTRE = 50
PART_DROITE = 27
TYPES = ((2, 27, 5),    # stats de la tuile 3x2, ligne du haut puis du bas (souhait : buts, note moy., passes D /
         (20, 46, 23))  # homme du match, clean sheets, cartons J) ; 27 sûr, les autres À VÉRIFIER (titre = FM)
LIGNES = 3              # joueurs visibles par case
HAUT_LIGNE = 30         # px d'une ligne de joueur
ECART_CASE = 10         # px entre deux cases
HAUT_TITRE = 30         # px réservés au titre d'une case (hauteur mini d'une rangée = titre + LIGNES lignes)
PART_REPUTATION = 2     # coupe : hauteur de la réputation pour PART_VAINQUEURS d'anciens vainqueurs
PART_ONZE = 3           # hauteur du 11 des médias pour PART_VAINQUEURS d'anciens vainqueurs
PART_VAINQUEURS = 2
ECART = 12              # px entre deux tuiles d'une colonne
TUILE_REPUTATION = ("CompetitionAboutRankingsTile_8x4", "dcc31486fdbf1fb44bc0fdf0cbf19788")
TUILE_STATS = ("CompetitionSitePlayerStatsTile_8x4", "629d577a761094044815cf34473fd224")
TUILE_MAISON = False    # v6 : notre tuile 3x2 MISE DE CÔTÉ (v3-v5 vides en jeu, sans erreur) -> tuile stats de FM
TUILE_VAINQUEURS =("CompetitionsAboutPastWinnersTile_4x2", "ae066b69ad9885b42b722bfcfbd44cbd")
# =====================================================================================================

VERSION = "6"
PREFIXE = "UIPickerEssaiComp"
NOM = f"{PREFIXE}-v{VERSION}"
LIGUE, COUPE = "CompetitionSiteBlock", "CompetitionSiteBlock_Cup"
MODELE_ONZE = "CompLeagueStatsBlock"
MODELE_LIGNE = "MatchScorelineKickoffCell"            # gameworld, cité par RIEN (modeles_libres_2026-11-05) : réécrit
GUID_LIGNE = "b46efa76ec582df418fb7c39bb1226d2"
SRC_TUILE = "CompetitionSitePlayerStatsTile_8x4"      # cadre de tuile, BindingVariables, StreamedObjectList
SRC_LIGNE = "RecordLinePerson"                        # nom + photo du joueur, valeur, titre
TYPE_LISTE_STATS = 1668313964                         # CompetitionStatsPlayerStatsList (bloc stats téléphone de FM)
TYPE_JOUEUR = 1145176065
for _k, _v in {"display": (131081, 1), "min-width": (131097, 3), "max-width": (131095, 3),
               "flex-basis": (131082, 3), "position": (131102, 7), "left": (131089, 3), "top": (131104, 3),
               "margin-top": (131093, 3), "height": (131087, 3), "width": (131105, 3),
               "min-height": (131096, 3), "flex-direction": (131083, 7), "align-items": (131073, 7),
               "margin-left": (131091, 3), "max-height": (131094, 3), "align-self": (131074, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
CENT = {"unit": 2, "value": 100.0}


class Outils:
    def __init__(self, t):
        self.t, self.st = t, t.styles
        self.trait = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical")
        self.vide = first(t, lambda r: typ(t, r) == "VisualElement" and not t.elem(r).get("m_TemplateAlias"))
        self.remap = first(t, lambda r: typ(t, r) == "BindingRemapper")

    def boite(self, parent, css, index=None, nom=""):
        t = self.t
        r = t.clone_shallow(self.vide, parent, index)
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1 if nom else 0
        self.st.style(t, r, css)
        return r

    def tuile(self, parent, modele, guid):
        """tuile FM incluse telle quelle (copie d'une instance de modèle, autre alias + using)"""
        t = self.t
        inst = t.clone_shallow(self.trait, parent)
        t.elem(inst)["m_TemplateAlias"] = modele
        t.elem(inst)["m_Classes"], t.elem(inst)["m_RuleIndex"] = ["height-100-percent"], -1
        t.sd(inst)["templateId"] = modele
        t.sd(inst)["name"], t.sd(inst)["name_UxmlAttributeFlags"] = "", 0
        self.st.style(t, inst, {"flex-grow": 1})
        us = t.tt.setdefault("m_Usings", [])
        if not any(u.get("alias") == modele for u in us):
            us.append({"alias": modele, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return inst

    def colonne(self, parent, part, index=None, nom=""):
        return self.boite(parent, {"flex-direction": "column", "flex-grow": part, "flex-shrink": 1,
                                   "flex-basis": 0, "min-width": 0}, index, nom)

    def case(self, col, part, haut=False):
        css = {"flex-grow": part, "flex-shrink": 1, "flex-basis": 0, "min-height": 0}
        if haut:
            css["margin-top"] = ECART
        return self.boite(col, css)

    def trait_vertical(self, parent, index=None):
        t = self.t
        r = t.clone(self.trait, parent, index)
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        return r

    def cache(self, parent):
        """boîte absolue 0 px sans débordement : éléments FM gardés (pas retirés) mais invisibles"""
        return self.boite(parent, {"position": "absolute", "left": 0, "top": 0, "width": 0, "height": 0,
                                   "overflow": "hidden"}, nom=f"{PREFIXE}Cache")


def ligue(t):
    o = Outils(t)
    nom = lambda n: first(t, lambda r: t.name(r) == n)  # noqa: E731
    rang, table, div1, onze = nom("ActiveNoParent"), nom("LeagueTable"), nom("Divider1"), nom("TeamOfTheWeek")
    a_cacher = [nom(n) for n in ("Divider2", "TransferNewsVisible", "CompNews")]
    inst_onze = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == MODELE_ONZE)
    if None in (rang, table, div1, onze, inst_onze, o.trait, o.vide, o.remap, *a_cacher):
        return None, "éléments FM introuvables (classement, 11 des médias, transferts, articles)"
    # transferts / articles : déplacés dans une boîte cachée
    cache = o.cache(rang)
    for x in a_cacher:
        cpb.move(t, x, cache)
    o.st.style(t, table, {"flex-grow": PART_TABLE, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    # v2 : la rangée et ses parents prennent toute la hauteur de la tuile (v1 : #ParentLeagueSwitch sans flex-grow,
    # tout s'arrêtait à la hauteur du classement ; chez FM, c'est le tableau des transferts qui l'étirait)
    x = rang
    while x is not None and t.name(x) != "Container":
        o.st.style(t, x, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        x = t.parent.get(x)
    # centre : tuile stats joueurs de FM (v6) ou notre tuile 3x2 (TUILE_MAISON, mise de côté)
    i = t.children(rang).index(div1) + 1
    centre = o.colonne(rang, PART_CENTRE, i, NOM)
    if TUILE_MAISON:
        src = sources()
        if src is None:
            return None, f"modèles sources introuvables ({SRC_TUILE}, {SRC_LIGNE})"
        err = tuile_stats(o, centre, src)
        if err:
            return None, err
    else:
        o.tuile(o.case(centre, 1), *TUILE_STATS)
    o.trait_vertical(rang, i + 1)
    # droite : 11 des médias (sans la liste) puis anciens vainqueurs
    droite = o.colonne(rang, PART_DROITE, i + 2)
    cpb.move(t, onze, droite)
    for x in (onze, *[r for r in t.walk(onze) if "comp-site-totw-block" in (t.elem(r).get("m_Classes") or [])]):
        o.st.style(t, x, {"width": CENT, "min-width": 0, "max-width": CENT})
    o.st.style(t, onze, {"flex-grow": PART_ONZE, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
    parent = t.parent[inst_onze]
    rm = t.clone_shallow(o.remap, parent, t.children(parent).index(inst_onze))
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = ["flex-grow-class"], -1
    t.sd(rm)["name"], t.sd(rm)["name_UxmlAttributeFlags"] = f"{PREFIXE}SansListe", 1
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": "showDetails", "to": {"m_path": "const.False"},
                             "type": {"id": 0}}]
    cpb.move(t, inst_onze, rm)
    o.tuile(o.case(droite, PART_VAINQUEURS, haut=True), *TUILE_VAINQUEURS)
    return "championnat : classement | stats joueurs 3x2 (top 3) | 11 des médias (sans liste) + anciens vainqueurs", None


# ---------- v3 : tuile stats joueurs 3x2 ----------
_SOURCES = []


def sources():
    """arbres d'origine de FM (lecture seule) : tuile stats et ligne de record"""
    if not _SOURCES:
        tu, li = ouvrir(SRC_TUILE, depart_original=True), ouvrir(SRC_LIGNE, depart_original=True)
        if tu is None or li is None:
            return None
        _SOURCES.append((tu[3], li[3]))
    return _SOURCES[0]


def tuile_stats(o, centre, src):
    t, st = o.t, o.st
    tu, li = src
    cadre = first(tu, lambda r: t_alias(tu, r) == "tile-wide-8x4")
    switch = cadre is not None and first(tu, lambda r: tu.name(r) == "HasStartedSwitch")
    frame = cadre is not None and first(tu, lambda r: tu.name(r) == "Frame")
    varsrc = first(tu, lambda r: tu.name(r) == "BindingTypesLeft")
    liste = varsrc is not None and next((k for k in tu.children(varsrc) if "StreamedObjectList" in typ(tu, k)), None)
    titre = first(li, lambda r: li.name(r) == "Subtitle")
    if not all((cadre, switch, frame, varsrc, liste, titre)):
        return f"{SRC_TUILE} / {SRC_LIGNE} : éléments introuvables (cadre, liste, titre)"
    # cadre de tuile FM (titre, clic vers les stats, « pas de données » avant le début) ; #Frame vidé
    tuile = t.clone(cadre, centre, src=tu)
    st.copy_from(tu.styles, t, tuile)
    copy_usings(t, tu, cadre)
    st.style(t, tuile, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
    mon_frame = first_in(t, tuile, lambda r: t.name(r) == "Frame")
    for k in list(t.children(mon_frame)):
        t.remove(k)
    # v3 / v4 vues : tuile vide sans erreur. La bascule « commencé » de FM enveloppe la branche choisie (taille du
    # contenu = 0, nos cases partent de flex-basis 0) -> v5 : bascule retirée, #Frame directement dans la tuile
    bascule = first_in(t, tuile, lambda r: t.name(r) == "HasStartedSwitch")
    cpb.move(t, mon_frame, tuile)
    t.remove(bascule)
    plein = {"align-self": "stretch", "min-width": 0}
    st.style(t, mon_frame, {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "min-height": 0, **plein})
    for n, rangee in enumerate(TYPES):
        css = {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 0, "flex-basis": 0,
               "min-height": HAUT_LIGNE * LIGNES + HAUT_TITRE, **plein}
        if n:
            css["margin-top"] = ECART_CASE
        r = o.boite(mon_frame, css)
        for m, ty in enumerate(rangee):
            case(o, r, ty, m > 0, varsrc, liste, titre, tu, li)
    return None


def case(o, rangee, ty, gauche, varsrc, liste, titre, tu, li):
    """une stat : variables (comme le bloc stats téléphone de FM) > remappeur > titre + liste des joueurs"""
    t, st = o.t, o.st
    css = {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
           "overflow": "hidden"}
    if gauche:
        css["margin-left"] = ECART_CASE
    boite = o.boite(rangee, css)
    v = t.clone(varsrc, boite, src=tu)
    for k in list(t.children(v)):
        t.remove(k)
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    sd = t.sd(v)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}Stat{ty}", 1
    sd["ValueVariables"] = [{"m_name": "type", "m_scopeValue": {"m_serializedData": f"Int|{ty}|"}},
                            {"m_name": "nextseason", "m_scopeValue": {"m_serializedData": "Bool|0|"}}]
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 0, "m_name": "selectedcategory"},
                                {"m_type": {"id": 0}, "m_initToNull": 0, "m_name": "selectedstage"}]
    sd["ValueVariables_UxmlAttributeFlags"], sd["ReferenceVariables_UxmlAttributeFlags"] = 1, 1
    st.style(t, v, {"flex-grow": 1, "min-height": 0, "min-width": 0})
    rm = t.clone_shallow(o.remap, v)
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = [], -1
    t.sd(rm)["name"], t.sd(rm)["name_UxmlAttributeFlags"] = "", 0
    t.sd(rm)["Mappings"] = [
        {"m_serialisedType": 0, "from": "statcategory", "to": {"m_path": "selectedcategory.PropertyValue"},
         "type": {"id": 0}},
        {"m_serialisedType": 0, "from": "stage", "to": {"m_path": "selectedstage.StageIndex"}, "type": {"id": 0}},
        {"m_serialisedType": 0, "from": "playerstatslist", "to": {"m_path": "comp.PlayerStats"},
         "type": {"id": TYPE_LISTE_STATS}},
        {"m_serialisedType": 0, "from": "gender", "to": {"m_path": "comp.Gender"}, "type": {"id": 0}}]
    t.sd(rm)["Mappings_UxmlAttributeFlags"] = 1
    st.style(t, rm, {"flex-direction": "column", "flex-grow": 1, "min-height": 0, "min-width": 0})
    # titre : nom de la stat donné par FM
    ti = t.clone(titre, rm, src=li)
    st.copy_from(li.styles, t, ti)
    t.sd(ti)["name"], t.sd(ti)["name_UxmlAttributeFlags"] = "", 0
    t.sd(ti)["TextBinding"]["m_direct"]["Path"]["m_path"] = "comp.PlayerTopStats.LongString"
    # liste : LIGNES joueurs visibles
    zone = o.boite(rm, {"height": HAUT_LIGNE * LIGNES, "min-height": HAUT_LIGNE * LIGNES,
                        "max-height": HAUT_LIGNE * LIGNES, "overflow": "hidden", "flex-shrink": 0,
                        "margin-top": 4})
    ls = t.clone(liste, zone, src=tu)
    t.elem(ls)["m_RuleIndex"] = -1
    sl = t.sd(ls)
    sl["name"], sl["name_UxmlAttributeFlags"] = "", 0
    sl["Binding"]["m_direct"]["Path"]["m_path"] = "playerstatslist.Players"
    sl["RowTemplate"]["m_AssetGUID"] = GUID_LIGNE
    sl["RowParamName"] = "item"
    sl["FixedElementSize"], sl["FixedElementSize_UxmlAttributeFlags"] = float(HAUT_LIGNE), 1
    sl["NumPreviewElements"] = LIGNES
    sl["SetIgnorePickingMode"] = 0
    st.style(t, ls, {"flex-grow": 1, "min-height": 0, "min-width": 0})


def ligne(t):
    """MODELE_LIGNE réécrit : une ligne de joueur (paramètre item = élément de playerstatslist.Players)"""
    src = sources()
    if src is None:
        return None, f"{SRC_LIGNE} introuvable"
    _, li = src
    racine = first(t, lambda r: typ(t, r).endswith("BindingExpect"))
    remap = first(li, lambda r: li.name(r) == "HasPlayerRemapper")
    valeur = first(li, lambda r: li.name(r) == "StatValue")
    if None in (racine, remap, valeur):
        return None, "éléments introuvables (racine de la ligne, nom / valeur de RecordLinePerson)"
    fond = next(iter(t.children(racine)), None)
    if fond is None:
        return None, "racine de la ligne vide"
    for k in list(t.children(racine))[1:]:
        t.remove(k)
    for k in list(t.children(fond)):
        t.remove(k)
    sd = t.sd(racine)
    p = sd["Parameters"][0]
    p["name"], p["type"], p["isOptional"] = "item", {"id": 0}, 0
    sd["Parameters"], sd["Parameters_UxmlAttributeFlags"] = [p], 1
    sd["name"], sd["name_UxmlAttributeFlags"] = NOM, 1
    t.elem(racine)["m_Classes"], t.elem(racine)["m_RuleIndex"] = [], -1
    t.elem(fond)["m_Classes"], t.elem(fond)["m_RuleIndex"] = [], -1
    t.sd(fond)["name"], t.sd(fond)["name_UxmlAttributeFlags"] = "", 0
    t.styles.style(t, racine, {"height": HAUT_LIGNE, "flex-shrink": 0})
    t.styles.style(t, fond, {"flex-direction": "row", "align-items": "center", "flex-grow": 1, "min-width": 0})
    rm = t.clone(remap, fond, src=li)
    t.styles.copy_from(li.styles, t, rm)
    copy_usings(t, li, remap)
    t.sd(rm)["Mappings"][0]["to"]["m_path"] = "item.player"
    t.sd(rm)["Mappings"][0]["type"]["id"] = TYPE_JOUEUR
    t.styles.style(t, rm, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "overflow": "hidden"})
    va = t.clone(valeur, fond, src=li)
    t.styles.copy_from(li.styles, t, va)
    t.sd(va)["TextBinding"]["m_direct"]["Path"]["m_path"] = "item.statvalue"
    t.styles.style(t, va, {"flex-shrink": 0, "margin-left": 6})
    return "ligne de joueur (nom + photo, valeur) pour la tuile stats", None


def t_alias(t, r):
    return t.elem(r).get("m_TemplateAlias") or ""


def first_in(t, root, pred):
    return next((r for r in t.walk(root) if pred(r)), None)


def coupe(t):
    o = Outils(t)
    nom = lambda n: first(t, lambda r: t.name(r) == n)  # noqa: E731
    avant, pendant, news = nom("Preseason"), nom("CompHasStarted"), nom("CompNews")
    if None in (avant, pendant, news, o.trait, o.vide, o.remap):
        return None, "éléments FM introuvables (avant / pendant la coupe, articles)"
    # avant le début : + réputation à droite
    o.trait_vertical(avant)
    col = o.colonne(avant, PART_DROITE, nom=NOM)
    o.tuile(o.case(col, 1), *TUILE_REPUTATION)
    # commencée : articles cachés, à leur place réputation puis anciens vainqueurs
    i = t.children(pendant).index(news)
    cpb.move(t, news, o.cache(pendant))
    col = o.colonne(pendant, PART_DROITE, i)
    o.tuile(o.case(col, PART_REPUTATION), *TUILE_REPUTATION)
    o.tuile(o.case(col, PART_VAINQUEURS, haut=True), *TUILE_VAINQUEURS)
    return "coupe : + réputation (avant le début) ; réputation + anciens vainqueurs à la place des articles", None


MODELES = ((LIGUE, ligue), (COUPE, coupe)) + (((MODELE_LIGNE, ligne),) if TUILE_MAISON else ())
# retirer remet aussi la ligne (posée par v3-v5) même quand TUILE_MAISON est coupé
A_RETIRER = ((LIGUE, ligue), (COUPE, coupe), (MODELE_LIGNE, ligne))


def marque(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def cmd_appliquer():
    for modele, faire in MODELES:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} introuvable (renommé par une mise à jour ?), rien fait")
            continue
        if any(o[3].name(r) == NOM for r in marque(o[3])):
            print(f"{modele} : déjà appliqué")
            continue
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marque(t):
            print(f"{modele} : pas de sauvegarde d'origine propre, rien fait")
            continue
        msg, err = faire(t)
        if err:
            print(f"{modele} : {err}, rien enregistré")
            continue
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        print(msg)
    nb.save_all()


def cmd_retirer():
    rien = True
    for modele, _ in A_RETIRER:
        o = ouvrir(modele)
        if o is None or not marque(o[3]):
            continue
        rien = False
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{modele} : pas de sauvegarde d'origine")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        print(f"{modele} : remis d'origine")
    nb.save_all()
    if rien:
        print("essai vue d'ensemble compétition : rien à retirer")


def cmd_etat():
    for modele, _ in MODELES:
        o = ouvrir(modele)
        m = o and marque(o[3])
        print(f"{modele} :", ("à jour" if any(o[3].name(r) == NOM for r in m) else "ANCIENNE version") if m
              else "d'origine")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": cmd_appliquer, "retirer": cmd_retirer, "etat": cmd_etat}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    fn()


if __name__ == "__main__":
    sys.modules.setdefault("essai_competition_vue", sys.modules[__name__])
    main(sys.argv[1:])
