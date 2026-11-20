"""ESSAI : Compétition > Vue d'ensemble refaite.

v7 (2026-11-19, capture de référence du joueur) — championnat (CompetitionSiteBlock, #ActiveNoParent) :
  [classement FM] | [bloc stats de FM (CompLeagueStatsDetailBlock recopié : onglets Stats joueurs / Stats équipes /
  Récompenses) avec les stats en grille, de gauche à droite (COLONNES par rangée)] |
  [11 de la semaine (terrain de FM, sans la liste) au-dessus des transferts de FM]
  Articles cachés (boîte absolue 0 px, éléments FM gardés). Bandeau des anciens vainqueurs (haut de page) intouché.
  - Grille : chaque case = recopie de #PlayerStatsContent / #TeamStatsContent de FM (sa variable playerStatTypes /
    teamStatTypes réduite à UN numéro, liste de FM 1 ligne de 120 px). Titres et top 3 donnés par FM.
  - Colonne de droite dans une recopie de #TransferNewsVisible (visible seulement en Large, comme le terrain et les
    transferts de FM) : hors Large, classement | stats seuls.
  - Les modèles partagés (CompLeagueStatsBlock, CompLeagueStatsDetailBlock : aussi dans un article) : intouchés.
v8 : v7 vue (stats OK ; nombres à 2-3 chiffres passés à la ligne, 11 absent en fin de saison = place vide) :
  stats 60 % (classement 22, droite 18) ; 11 dans une recopie de #TeamOfTheWeekTitleVisible (sans 11 : transferts
  sur toute la hauteur).
v9 : v8 vue OK ; le joueur veut du riche sous les stats (réf.) : rangée 11 de la semaine (Large, s'il existe) |
  tuile Matchs de FM (CompetitionSiteFixturesTile_8x4 : résultats / à venir de la journée) ; droite = transferts seuls.
v10 : v9 vue (Rencontres trop grosse, nombres encore à la ligne, transferts tronqués) : Rencontres 300 px maxi ;
  CompPlayerStatRow / CompTeamStatRow : bloc du nombre sans rétrécir ; largeurs 21 / 56 / 23.
v11 : v10 vue (nombres OK ; Rencontres toujours la moitié de l'écran, « rajoute des infos », réputation comme v6) :
  rangée du bas = 11 (s'il existe) | tuiles FM 4x4 Rencontres | Réputation | Records.
v12 : demande du joueur : centre = en haut classement | 11 | Records | Rencontres ; dessous les stats seules (onglet
  Récompenses masqué) ; Réputation retirée ; droite = transferts.
v13 : v12 vue (tuiles étirées jusqu'aux stats = vide, Classements manquant, stats en bas) : rangée du haut à la
  hauteur du classement (classement | 11 | Records | Rencontres | Classements), stats centrées en hauteur dessous.
v14 : on repart de zéro (capture vanilla du joueur, peu de place) : classement | stats en grille au milieu, 11 de
  la semaine dessous | transferts de FM à droite ; articles (Infos) cachés ; tuiles retirées. On ajoutera ensuite.
v15 : v14 VUE (marche, noms coupés) : stats sur 3 étages (joueurs 4 par rangée, équipes 3) ; coupe (Champions
  League...) même affichage : classement | stats | articles (pas de transferts en coupe), avant le début = FM.
v16 : v15 VUE OK (championnat) ; sous les stats, rangée [11 s'il existe] | tuile Rencontres (matchs à venir) |
  tuile Réputation (CompetitionAboutRankingsTile), aussi en coupe.
v17 : v16 VUE OK ; stats dans un défilement de FM haut de 2 rangées (3e en faisant défiler) : Rencontres /
  Réputation plus hautes.
v18 : v17 VUE OK (PL fin de saison) ; en cours de saison (Ligue 1) le 11 de la semaine apparaissait et débordait
  sur Rencontres : 11 retiré (le joueur), sa colonne cachée.
v19 : coupe VUE OK ; Rencontres remplacée par la tuile Anciens vainqueurs de FM (championnat et coupe).
v20 : Large + Medium VALIDÉS ; championnat en Small seulement : à gauche Classements (réputation) puis Anciens
  vainqueurs empilés | à droite 11 de la semaine (s'il existe). Coupe : inchangée.
v21 : v20 VUE (11 petit en haut à gauche : FM ne l'étire qu'en Large) : bloc du 11 recopié, étiré sur toute la place.
v22 : coupe en Small pareil (Classements / Vainqueurs empilés | 11, colonne du 11 recopiée de la page championnat).
v23 : Small VALIDÉ ; « i » de FM (PlayerReportPreviewTooltip) à gauche du nom dans les lignes de stats joueurs.
v24 : v23 vue (le « i » des stats existait déjà = la silhouette : doublon retiré ; le joueur le voulait sur le 11) :
  « i » à gauche du nom des joueurs du 11 (modèle de position du terrain, seul écrivain).
v25 : v24 VUE OK ; coupe internationale (comp.IsInternational : continentales, sélections) : Anciens vainqueurs |
  Records dans tous les modes (le classement de FM n'y listait que les coupes nationales).
v26 : v25 vue (Europa League inchangée : IsInternational = sélections) -> condition comp.Nation (sans pays).
v27 : v26 VUE OK (« plus de records ») : continentale = tuiles 8x4 de FM (Anciens vainqueurs, Records : 10 records).
v28 : v27 vue (vainqueurs 8x4 OK ; records 8x4 = 2 colonnes qui se chevauchent) : Records 8x4 recopiée, colonnes
  empilées en une seule (trait retiré), dans un défilement de FM.
v29 : anciens vainqueurs de haut en bas (le joueur) : tuile 4x8 de FM (tenant + 10 vainqueurs, une colonne).
v30 : v29 VALIDÉE ; coupe nationale tous modes = vainqueurs 4x8 | Classements (plus de 11 ni d'empilement en
  Small) ; championnat inchangé.
v31 : v30 VUE OK (vainqueurs) ; coupe nationale : à droite Classements puis Records (tuile maison) empilés.
Coupe : pas touchée de v7 à v14.
Historique : v1-v2 rangée étirée ; v3-v5 tuile stats 3x2 maison restée vide en jeu ; v6 tuile stats de FM au milieu
  (mis de côté le 2026-11-12).

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
import notes_installations as ni  # noqa: E402  (bascule Small : SIVisible de comparaison d'entier)

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
PART_TABLE = 26         # parts de largeur : classement | centre (stats + 11) | transferts
PART_CENTRE = 50
PART_DROITE = 24
ETAGES_VISIBLES = 2    # v17 : rangées visibles, les autres en faisant défiler
DEFILEMENT_SOURCE = "PlayerRecommendationsMainBlock"   # un SIScrollView vertical de FM à recopier
ETAGES = 3             # rangées de stats (v15) : par rangée = arrondi au-dessus (10 joueurs : 4 ; 9 équipes : 3)          # stats par rangée (de gauche à droite)
# numéros des stats (titres donnés par FM), lus en jeu (v7) : 2 buts, 5 passes D, 46 tirs, 23 passes clés,
# 63 tacles remportés, 27 note moy., 12 homme du match, 13 passes réussies (%), 62 dribbles, 20 clean sheets.
# Ordre (le joueur, 2026-11-20) :
# buts | passes D | note | HdM / tirs | passes clés | passes réussies | dribbles / tacles | clean sheets
STATS_JOUEURS = (2, 5, 27, 12, 46, 23, 13, 62, 63, 20)
STATS_EQUIPES = (5, 15, 28, 54, 55, 24, 25, 41, 16)    # celles de FM (onglet Stats équipes)
HAUT_CASE = 120         # px d'une stat (celle de FM)
ECART_CASE = 12         # px entre deux cases
ECART = 12              # px entre les stats et la rangée du bas, entre deux tuiles
# v16 : rangée sous les stats = [11 de la semaine s'il existe] | Rencontres (matchs à venir) | Réputation
TUILES_BAS = (("CompetitionsAboutPastWinnersTile_4x4", "76f93fa2d80f2224bb34cff5d10a115a"),  # derniers vainqueurs (v19)
              ("CompetitionAboutRankingsTile_4x4", "a94aad0e16a943e44a736f9ad138d1c4"))      # Réputation
# v20 : championnat en Small : Réputation au-dessus, vainqueurs en dessous (à gauche) | 11 de la semaine (à droite)
TUILES_BAS_SMALL = (TUILES_BAS[1], TUILES_BAS[0])
# v25 : coupe internationale (continentale), tous les modes : vainqueurs | records
# v27 : versions 8x4 (records : 10 en coupe au lieu de 5)
# v30-v31 : coupe nationale, tous modes : vainqueurs 4x8 | classements (réputation) puis records empilés
TUILES_NAT = (("CompetitionsAboutPastWinnersTile_4x8", "9acc80489b400c7448581e1e5af2a8f2"), TUILES_BAS[1],
              ("CompetitionSiteAboutRecordsTile_8x4", "1739b6074e3972744b90dd54e4f68120"))
# v29 : vainqueurs = 4x8 (une colonne, tenant + 10 vainqueurs, comme la 4x4 mais plus remplie)
TUILES_INTER = (("CompetitionsAboutPastWinnersTile_4x8", "9acc80489b400c7448581e1e5af2a8f2"),
                ("CompetitionSiteAboutRecordsTile_8x4", "1739b6074e3972744b90dd54e4f68120"))
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Large, 1 Medium, 2 Small
# =====================================================================================================

VERSION = "31"
PREFIXE = "UIPickerEssaiComp"
NOM = f"{PREFIXE}-v{VERSION}"
LIGUE, COUPE = "CompetitionSiteBlock", "CompetitionSiteBlock_Cup"
MODELE_ONZE = "CompLeagueStatsBlock"
MODELE_DETAIL = "CompLeagueStatsDetailBlock"
MODELE_LIGNE = "MatchScorelineKickoffCell"            # réécrit par v3-v5 : retirer le remet
for _k, _v in {"display": (131081, 1), "min-width": (131097, 3), "max-width": (131095, 3),
               "flex-basis": (131082, 3), "position": (131102, 7), "left": (131089, 3), "top": (131104, 3),
               "margin-top": (131093, 3), "height": (131087, 3), "width": (131105, 3),
               "min-height": (131096, 3), "flex-direction": (131083, 7), "align-items": (131073, 7),
               "margin-left": (131091, 3), "margin-right": (131092, 3), "max-height": (131094, 3), "align-self": (131074, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
CENT = {"unit": 2, "value": 100.0}
ENUM = '{"$type":"SI.Bindable.EnumListScopeValue, SI.Bindable","m_value":[%s]}'


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
        us = t.tt.setdefault("m_Usings", [])
        if not any(u.get("alias") == modele for u in us):
            us.append({"alias": modele, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return inst

    def colonne(self, parent, part, index=None, nom=""):
        return self.boite(parent, {"flex-direction": "column", "flex-grow": part, "flex-shrink": 1,
                                   "flex-basis": 0, "min-width": 0}, index, nom)

    def trait_vertical(self, parent, index=None):
        t = self.t
        r = t.clone(self.trait, parent, index)
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        return r

    def cache(self, parent):
        """boîte absolue 0 px sans débordement : éléments FM gardés (pas retirés) mais invisibles"""
        return self.boite(parent, {"position": "absolute", "left": 0, "top": 0, "width": 0, "height": 0,
                                   "overflow": "hidden"}, nom=f"{PREFIXE}Cache")


def first_in(t, root, pred):
    return next((r for r in t.walk(root) if pred(r)), None)


_SOURCE = []
_DEFILE = []
_ONZE = []


def source_onze():
    """arbre d'origine de CompLeagueStatsBlock, le 11 de la semaine (lecture seule)"""
    if not _ONZE:
        o = ouvrir(MODELE_ONZE, depart_original=True)
        if o is None:
            return None
        _ONZE.append(o[3])
    return _ONZE[0]


def source_defilement():
    """arbre d'origine d'un modèle de FM qui a un SIScrollView vertical (lecture seule)"""
    if not _DEFILE:
        o = ouvrir(DEFILEMENT_SOURCE, depart_original=True)
        if o is None:
            return None
        _DEFILE.append(o[3])
    return _DEFILE[0]


def source_detail():
    """arbre d'origine de CompLeagueStatsDetailBlock (lecture seule)"""
    if not _SOURCE:
        o = ouvrir(MODELE_DETAIL, depart_original=True)
        if o is None:
            return None
        _SOURCE.append(o[3])
    return _SOURCE[0]


def fixer_variable(t, cellule, nom_var, ids):
    """la variable (composant de la case, déclaré 2 fois : données m_components + propriété value-vars) = ids"""
    valeur = ENUM % ",".join(str(i) for i in ids)
    n = 0
    for c in t.sd(cellule).get("m_components") or []:
        for v in ((t.refs.get(c["rid"]) or {}).get("data") or {}).get("ValueVariables") or []:
            if v.get("m_name") == nom_var:
                v["m_scopeValue"]["m_serializedData"] = valeur
                n += 1
    for k in t.children(cellule):
        if typ(t, k) == "BindingVariablesComponent":
            for p in t.elem(k).get("m_Properties") or []:
                if p.get("name") == "value-vars" and f"{{{nom_var}}}" in (p.get("value") or ""):
                    p["value"] = "{%s}{%s}" % (nom_var, valeur.replace(",", "&#44;"))
                    n += 1
    return n == 2


def grille(o, contenu, src, src_cellule, nom_var, ids):
    """#PlayerStatsContent / #TeamStatsContent recopié : sa liste retirée, à la place des rangées de COLONNES cases"""
    t, st = o.t, o.st
    for k in list(t.children(contenu)):
        if "StreamedObjectList" in typ(t, k):
            t.remove(k)
    st.style(t, contenu, {"flex-direction": "column", "flex-grow": 1, "min-width": 0})
    COLONNES = -(-len(ids) // ETAGES)   # noqa: N806
    # v17 : rangées dans un défilement de FM, hauteur = ETAGES_VISIBLES rangées (le reste en faisant défiler)
    ds = source_defilement()
    sv = ds and first(ds, lambda r: typ(ds, r).endswith("SIScrollView"))
    if sv is None:
        return f"défilement de FM ({DEFILEMENT_SOURCE}) introuvable"
    v = t.clone(sv, contenu, src=ds)
    for k in list(t.children(v)):
        t.remove(k)
    t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = f"{PREFIXE}Defile", 1
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    if "VerticalScrollerVisibility" in t.sd(v):
        t.sd(v)["VerticalScrollerVisibility"] = 0   # barre seulement s'il y a plus que la place
    haut = ETAGES_VISIBLES * HAUT_CASE + (ETAGES_VISIBLES - 1) * ECART_CASE
    st.style(t, v, {"height": haut, "min-height": haut, "max-height": haut, "flex-grow": 0, "flex-shrink": 0,
                    "align-self": "stretch", "min-width": 0})
    contenu = v
    for n in range(0, len(ids), COLONNES):
        css = {"flex-direction": "row", "flex-shrink": 0, "height": HAUT_CASE, "min-height": HAUT_CASE,
               "align-self": "stretch", "min-width": 0}
        if n:
            css["margin-top"] = ECART_CASE
        rangee = o.boite(contenu, css)
        for m in range(COLONNES):
            if n + m >= len(ids):   # rangée incomplète : cases vides pour garder la même largeur
                o.boite(rangee, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                 "margin-left": ECART_CASE})
                continue
            c = t.clone(src_cellule, rangee, src=src)
            st.copy_from(src.styles, t, c)
            t.elem(c)["m_Classes"], t.elem(c)["m_RuleIndex"] = [], -1
            t.sd(c)["name"], t.sd(c)["name_UxmlAttributeFlags"] = f"{PREFIXE}Stat{ids[n + m]}", 1
            if not fixer_variable(t, c, nom_var, [ids[n + m]]):
                return f"variable {nom_var} de FM : forme inattendue"
            css = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden"}
            if m:
                css["margin-left"] = ECART_CASE
            st.style(t, c, css)
            ls = next((k for k in t.children(c) if "StreamedObjectList" in typ(t, k)), None)
            if ls is None:
                return "liste des stats de FM introuvable"
            t.sd(ls)["NumPreviewElements"] = 1
            st.style(t, ls, {"flex-grow": 1, "min-height": 0, "min-width": 0})
    return None


def bloc_stats(o, parent):
    """bloc stats de FM recopié (onglets Stats joueurs / Stats équipes, Récompenses masqué), stats en grille ;
    attend « comp » (donné en championnat ET en coupe)"""
    t = o.t
    src = source_detail()
    racine = src and first(src, lambda r: typ(src, r) == "ComponentElement" and src.parent.get(r) is not None
                           and typ(src, src.parent[r]) == "BindingExpect")
    racine = racine or (src and first(src, lambda r: typ(src, r) == "ComponentElement"))
    cell_j = src and first(src, lambda r: src.name(r) == "PlayerStatsContent")
    cell_e = src and first(src, lambda r: src.name(r) == "TeamStatsContent")
    if None in (src, racine, cell_j, cell_e):
        return f"{MODELE_DETAIL} : éléments introuvables (bloc, stats joueurs / équipes)"
    bloc = t.clone(racine, parent, src=src)
    t.styles.copy_from(src.styles, t, bloc)
    copy_usings(t, src, racine)
    o.st.style(t, bloc, {"flex-grow": 0, "flex-shrink": 0, "min-width": 0})
    recomp = first_in(t, bloc, lambda r: t.name(r) == "Awards")
    if recomp is None:
        return "onglet Récompenses (#Awards) introuvable"
    o.st.style(t, recomp, {"display": 6})   # mot-clé None (display: none)
    mon_j = first_in(t, bloc, lambda r: t.name(r) == "PlayerStatsContent")
    mon_e = first_in(t, bloc, lambda r: t.name(r) == "TeamStatsContent")
    for contenu, cel, var, ids in ((mon_j, cell_j, "playerStatTypes", STATS_JOUEURS),
                                   (mon_e, cell_e, "teamStatTypes", STATS_EQUIPES)):
        err = grille(o, contenu, src, cel, var, ids)
        if err:
            return err
    return None


def tuiles(o, parent, direction, liste):
    """tuiles FM de liste côte à côte (row) ou empilées (column), parts égales"""
    t = o.t
    for i, (modele, guid) in enumerate(liste):
        css = {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
               "min-height": 0}
        if i:
            css["margin-left" if direction == "row" else "margin-top"] = ECART
        col = o.boite(parent, css)
        if modele == RECORDS_8X4:   # v28 : tuile maison (recopie refaite)
            err = tuile_records(o, col)
            if err:
                return err
            continue
        tu = o.tuile(col, modele, guid)
        o.st.style(t, tu, {"flex-grow": 1, "min-height": 0, "min-width": 0})
    return None


RECORDS_8X4 = "CompetitionSiteAboutRecordsTile_8x4"


def tuile_records(o, parent):
    """v28 : tuile Records 8x4 de FM RECOPIÉE (cadre, titre, données) et refaite pour une place étroite et haute :
    ses 2 colonnes de 5 records (séparées par un trait vertical) empilées en une seule, dans un défilement de FM"""
    t = o.t
    o_src = ouvrir(RECORDS_8X4, depart_original=True)
    s = o_src and o_src[3]
    racine = s and first(s, lambda r: s.name(r) == "TileBindingExpect")
    if racine is None:
        return f"{RECORDS_8X4} introuvable"
    tu = t.clone(racine, parent, src=s)
    t.styles.copy_from(s.styles, t, tu)
    copy_usings(t, s, racine)
    t.sd(tu)["name"], t.sd(tu)["name_UxmlAttributeFlags"] = f"{PREFIXE}Records", 1
    o.st.style(t, tu, {"flex-grow": 1, "min-height": 0, "min-width": 0})
    trait = first_in(t, tu, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical")
    racine_vis = first_in(t, tu, lambda r: t.name(r) == "RootVisible")
    if None in (trait, racine_vis):
        return f"{RECORDS_8X4} : trait / RootVisible introuvables"
    rangee = t.parent[trait]
    t.remove(trait)
    o.st.style(t, rangee, {"flex-direction": "column", "align-items": "stretch", "min-width": 0})
    for k in t.children(rangee):
        o.st.style(t, k, {"width": CENT, "max-width": CENT, "min-width": 0, "flex-shrink": 0})
    # défilement : tout le contenu de RootVisible dedans
    ds = source_defilement()
    sv = ds and first(ds, lambda r: typ(ds, r).endswith("SIScrollView"))
    if sv is None:
        return f"défilement de FM ({DEFILEMENT_SOURCE}) introuvable"
    contenu = list(t.children(racine_vis))
    v = t.clone(sv, racine_vis, 0, src=ds)
    for k in list(t.children(v)):
        t.remove(k)
    t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = f"{PREFIXE}RecordsDefile", 1
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    o.st.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "min-width": 0})
    for k in contenu:
        cpb.move(t, k, v)
    o.st.style(t, racine_vis, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0})
    return None


def si_mode(o, parent, small):
    """SIVisible vide : affiché seulement en Small (small) ou seulement hors Small (copie de la bascule du skin :
    settings.AdaptiveScalingLevelIndex, 0 Large / 1 Medium / 2 Small)"""
    t = o.t
    s, vis = ni.visible_model()
    if vis is None:
        return None
    b = ni.make_binding(s.sd(vis)["Binding"], 4 if small else 0, [MODE_AFFICHAGE], 1 if small else 2)
    v = ni.new_visible(t, s, vis, parent, None, f"{PREFIXE}{'Small' if small else 'HorsSmall'}", b)
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.elem(v)["m_RuleIndex"] = -1
    o.st.style(t, v, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                      "min-height": 0, "min-width": 0})
    return v


def rangee_bas(o, centre, petit=False):
    """rangée sous les stats, le reste de la hauteur : tuiles FM de TUILES_BAS côte à côte. petit (v20, championnat) :
    en Small seulement, TUILES_BAS_SMALL empilées à gauche (la colonne de droite est renvoyée, pour le 11)"""
    t = o.t
    bas = o.boite(centre, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                           "min-height": 0, "min-width": 0, "margin-top": ECART}, nom=f"{PREFIXE}Bas")
    if not petit:
        tuiles(o, bas, "row", TUILES_BAS)
        return bas, None
    hors, small = si_mode(o, bas, False), si_mode(o, bas, True)
    if None in (hors, small):
        return bas, None
    tuiles(o, hors, "row", TUILES_BAS)
    gauche = o.boite(small, {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                             "min-height": 0, "min-width": 0})
    tuiles(o, gauche, "column", TUILES_BAS_SMALL)
    return bas, small


def onze_small(o, small, src, onze):
    """v20-v22 : dans small (Small seulement), à droite, le 11 de la semaine : recopie de la colonne #TeamOfTheWeek
    (onze, de l'arbre src : la page championnat elle-même, ou son original pour la coupe) dans une recopie de
    #TeamOfTheWeekTitleVisible (masqué sans 11 : la colonne de gauche prend alors toute la largeur).
    v21 : le terrain de FM ne s'étire qu'en Large (#IsLarge : classe flex-grow seulement si app.GridBreakpointIsLarge)
    -> CompLeagueStatsBlock (partagé avec un article : intouché) RECOPIÉ à la place de son instance, sans la partie
    détails (showDetails), et tout étiré jusqu'au terrain (FillAllAvailableSpace de FM)"""
    t = o.t
    autre = None if src is t else src
    titre = first_in(src, onze, lambda r: src.name(r) == "TeamOfTheWeekTitleVisible")
    if titre is None:
        return "#TeamOfTheWeekTitleVisible de FM introuvable"
    env = t.clone(titre, small, src=autre)
    if autre is not None:
        t.styles.copy_from(src.styles, t, env)
    for k in list(t.children(env)):
        t.remove(k)
    t.sd(env)["name"], t.sd(env)["name_UxmlAttributeFlags"] = f"{PREFIXE}Onze", 1
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    for cle in ("StyleClassToApplyOnVisible", "StyleClassBindingToApplyOnVisible"):
        if isinstance(t.sd(env).get(cle), str):
            t.sd(env)[cle] = ""
    o.st.style(t, env, {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                        "min-height": 0, "min-width": 0, "margin-left": ECART, "overflow": "hidden"})
    col = t.clone(onze, env, src=autre)
    if autre is not None:
        t.styles.copy_from(src.styles, t, col)
        copy_usings(t, src, onze)
    t.sd(col)["name"], t.sd(col)["name_UxmlAttributeFlags"] = f"{PREFIXE}OnzeColonne", 1
    o.st.style(t, col, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
    for y in (col, *[r for r in t.walk(col) if "comp-site-totw-block" in (t.elem(r).get("m_Classes") or [])]):
        o.st.style(t, y, {"width": CENT, "min-width": 0, "max-width": CENT})
    inst = first_in(t, col, lambda r: t.elem(r).get("m_TemplateAlias") == MODELE_ONZE)
    s = source_onze()
    racine = s and first(s, lambda r: typ(s, r) == "ComponentElement")
    if None in (inst, racine):
        return f"{MODELE_ONZE} : bloc introuvable"
    parent = t.parent[inst]
    i = t.children(parent).index(inst)
    t.remove(inst)
    bloc = t.clone(racine, parent, i, src=s)
    t.styles.copy_from(s.styles, t, bloc)
    copy_usings(t, s, racine)
    t.sd(bloc)["name"], t.sd(bloc)["name_UxmlAttributeFlags"] = f"{PREFIXE}Terrain", 1
    details = first_in(t, bloc, lambda r: typ(t, r) == "SIVisible"
                       and (t.sd(r).get("Binding") or {}).get("m_direct", {}).get("Path", {}).get("m_path")
                       == "showDetails")
    if details is not None:
        t.remove(details)
    etire = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "min-width": 0}
    o.st.style(t, bloc, etire)
    for r in list(t.walk(bloc)):
        if r == bloc or typ(t, r) not in ("SIVisible", "VisualElement", "BindableSwitchElement", "FMTacticsPanel"):
            continue
        o.st.style(t, r, dict(etire, **{"width": CENT, "max-width": CENT}))
        if typ(t, r) == "FMTacticsPanel":
            o.st.style(t, r, {"height": CENT, "max-height": CENT})
    return None


_LIGUE = []


def source_ligue():
    """arbre d'origine de la page championnat (lecture seule) : sa colonne du 11, recopiée en coupe"""
    if not _LIGUE:
        o = ouvrir(LIGUE, depart_original=True)
        if o is None:
            return None
        _LIGUE.append(o[3])
    return _LIGUE[0]


def ligue(t):
    """v14 (repart de zéro) : classement FM | centre = stats en grille puis 11 de la semaine dessous | transferts FM ;
    articles cachés. Tout le reste de FM à sa place."""
    o = Outils(t)
    nom = lambda n: first(t, lambda r: t.name(r) == n)  # noqa: E731
    rang, table, onze = nom("ActiveNoParent"), nom("LeagueTable"), nom("TeamOfTheWeek")
    transferts, div3, news = nom("TransferNewsVisible"), nom("Divider3"), nom("CompNews")
    if None in (rang, table, onze, transferts, news, o.vide):
        return None, "éléments FM introuvables (classement, 11 de la semaine, transferts, articles)"
    x = rang
    while x is not None and t.name(x) != "Container":
        o.st.style(t, x, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        x = t.parent.get(x)
    # articles (et le trait avant eux, dans les transferts) : boîte cachée
    cache = o.cache(rang)
    for x in (div3, news):
        if x is not None:
            cpb.move(t, x, cache)
    base = {"flex-shrink": 1, "flex-basis": 0, "min-width": 0, "min-height": 0}
    o.st.style(t, table, dict(base, **{"flex-grow": PART_TABLE}))
    o.st.style(t, transferts, dict(base, **{"flex-grow": PART_DROITE}))
    # centre à la place de la colonne du 11 (entre Divider1 et Divider2 de FM)
    centre = o.colonne(rang, PART_CENTRE, t.children(rang).index(onze), NOM)
    err = bloc_stats(o, centre)
    if err:
        return None, err
    # rangée sous les stats : Rencontres | Réputation ; v18 : 11 de la semaine retiré (trop haut, débordait en cours
    # de saison) : sa colonne de FM va dans la boîte cachée
    if o.trait is None:
        return None, "trait de FM introuvable"
    _, small = rangee_bas(o, centre, petit=True)
    if small is None:
        return None, "bascule Small du skin (notes_installations) introuvable"
    err = onze_small(o, small, t, onze)
    if err:
        return None, err
    cpb.move(t, onze, cache)
    return ("championnat : classement | stats (%d joueurs, %d équipes, %d étages, sans Récompenses) + Vainqueurs | "
            "Réputation dessous (Small : Réputation / Vainqueurs empilés | 11) | transferts ; articles cachés"
            % (len(STATS_JOUEURS), len(STATS_EQUIPES), ETAGES)), None


def coupe(t):
    """v15 : comme le championnat, compétition commencée (#CompHasStarted) : classement FM | stats en grille (bloc
    recopié) | articles FM (pas de transferts ni de 11 en coupe). Avant le début (#Preseason) : FM intouché."""
    o = Outils(t)
    started = first(t, lambda r: t.name(r) == "CompHasStarted")
    if started is None or o.vide is None:
        return None, "coupe : #CompHasStarted introuvable"
    nom = lambda n: first_in(t, started, lambda r: t.name(r) == n)  # noqa: E731
    joueurs, div2, equipes, news = nom("PlayerStats"), nom("Divider2"), nom("TeamStatsVisible"), nom("CompNews")
    switch = t.parent.get(started)
    if None in (joueurs, div2, equipes, news, switch):
        return None, "coupe : stats joueurs / équipes / articles introuvables"
    # partie droite (stats + articles) : 74 % au lieu de 66 % -> classement 26 comme en championnat
    o.st.style(t, switch, {"width": {"unit": 2, "value": float(PART_CENTRE + PART_DROITE)}})
    base = {"flex-shrink": 1, "flex-basis": 0, "min-width": 0, "min-height": 0}
    centre = o.colonne(started, PART_CENTRE, t.children(started).index(joueurs), NOM)
    err = bloc_stats(o, centre)
    if err:
        return None, err
    if o.trait is None:
        return None, "coupe : trait de FM introuvable"
    # v30 (le joueur) : coupe nationale = TUILES_NAT côte à côte dans tous les modes (vainqueurs 4x8 | classements),
    # plus de 11 (FM n'en a pas en coupe : place vide) ; continentale (v25-v29) = TUILES_INTER
    bas = o.boite(centre, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                           "min-height": 0, "min-width": 0, "margin-top": ECART}, nom=f"{PREFIXE}Bas")
    modele_vis = first(t, lambda r: typ(t, r) == "SIVisible")
    if modele_vis is None:
        return None, "coupe : SIVisible de FM introuvable"
    ligne = {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
             "min-width": 0}
    nat = o.boite(bas, ligne)
    tuiles(o, nat, "row", TUILES_NAT[:1])
    # v31 (le joueur) : à droite, Classements puis Records (tuile maison qui défile) empilés
    droite_nat = o.boite(nat, {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                               "min-height": 0, "min-width": 0, "margin-left": ECART})
    err = tuiles(o, droite_nat, "column", TUILES_NAT[1:])
    if err:
        return None, err
    # v26 : comp.IsInternational faux en Europa League (= sélections) -> comp.Nation, comme l'en-tête de FM
    # (#nation-switch) : coupe nationale = a un pays ; continentale = sans pays (visible si nul : inversé)
    t.to_visible(nat, modele_vis, "comp.Nation", False, f"{PREFIXE}Nationale")
    inter = o.boite(bas, ligne)
    err = tuiles(o, inter, "row", TUILES_INTER)
    if err:
        return None, err
    t.to_visible(inter, modele_vis, "comp.Nation", True, f"{PREFIXE}Internationale")
    cache = o.cache(started)
    for x in (joueurs, equipes):
        cpb.move(t, x, cache)
    o.st.style(t, news, dict(base, **{"flex-grow": PART_DROITE}))
    return ("coupe : classement | stats (%d étages) + nationale Vainqueurs 4x8 | Réputation, continentale "
            "Vainqueurs 4x8 | Records (tous modes) | articles" % ETAGES), None


def ligne_stat(t):
    """v10 : ligne d'une stat (CompPlayerStatRow / CompTeamStatRow, de FM : aussi Vue d'ensemble d'origine et article)
    : le bloc du nombre (bascule de FM, sans classe) ne rétrécit plus -> nombres à 2-3 chiffres plus à la ligne ;
    le nom rétrécit (points de suspension de FM)"""
    ligne = first(t, lambda r: t.name(r) == "RowContent")
    kids = t.children(ligne) if ligne is not None else []
    nom_ = next((k for k in kids if typ(t, k) == "BindingRemapper"), None)
    valeur = next((k for k in kids if typ(t, k) == "BindableSwitchElement"), None)
    if None in (nom_, valeur):
        return None, "ligne de stat : nom / nombre introuvables"
    t.sd(valeur)["name"], t.sd(valeur)["name_UxmlAttributeFlags"] = NOM, 1
    t.styles.style(t, valeur, {"flex-shrink": 0, "margin-left": 4})
    t.styles.style(t, nom_, {"flex-shrink": 1, "min-width": 0, "overflow": "hidden"})
    return "ligne de stat : nombre sans retour à la ligne", None


INFO_JOUEUR = ("PlayerReportPreviewTooltip", "227dd12a280d2244c9ec015a4064c3a1")   # « i » de FM (aperçu + fiche)


TYPE_PERSONNE = 1145176065   # type de « binding » attendu par le « i » (TopPlayerRow, CompPlayerStatRow)


def joueur_terrain(t):
    """v24 (le joueur) : joueur du 11 de la semaine sur le terrain (modèle de position du FMTacticsPanel : maillot +
    nom), « i » de FM à gauche du nom : BindingRemapper binding -> position.Player avec PlayerReportPreviewTooltip
    dedans (comme TopPlayerRow). Modèle aussi utilisé par le 11 d'un article de FM (même « i »)."""
    texte = first(t, lambda r: t.name(r) == "text" and typ(t, r).endswith("SIText"))
    modele_rm = first(t, lambda r: typ(t, r) == "BindingRemapper")
    inst = first(t, lambda r: bool(t.elem(r).get("m_TemplateAlias")))
    if None in (texte, modele_rm, inst):
        return None, "joueur du 11 : nom / remapper / instance de FM introuvables"
    ligne = t.parent[texte]
    rm = t.clone_shallow(modele_rm, ligne, t.children(ligne).index(texte))
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = [], -1
    t.sd(rm)["name"], t.sd(rm)["name_UxmlAttributeFlags"] = NOM, 1
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": "binding", "to": {"m_path": "position.Player"},
                             "type": {"id": TYPE_PERSONNE}}]
    t.styles.style(t, rm, {"flex-shrink": 0, "margin-right": 2, "align-self": "center"})
    i = t.clone_shallow(inst, rm)
    modele, guid = INFO_JOUEUR
    t.elem(i)["m_TemplateAlias"], t.sd(i)["templateId"] = modele, modele
    t.elem(i)["m_Classes"], t.elem(i)["m_RuleIndex"] = [], -1
    us = t.tt.setdefault("m_Usings", [])
    if not any(u.get("alias") == modele for u in us):
        us.append({"alias": modele, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
    return "joueur du 11 : « i » à gauche du nom", None


LIGNES_STATS = ("CompPlayerStatRow", "CompTeamStatRow")
JOUEUR_TERRAIN = "_data_display-totw-overview-pitch-indicator-large-awardwinner"
MODELES = ((LIGUE, ligue), (COUPE, coupe), (JOUEUR_TERRAIN, joueur_terrain)) \
    + tuple((m, ligne_stat) for m in LIGNES_STATS)
A_RETIRER = MODELES + ((MODELE_LIGNE, None),)   # v3-v5 posaient aussi la ligne


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
    # anciennes versions : la coupe (v1-v6) et la ligne (v3-v5) remises d'origine
    retirer((MODELE_LIGNE,))
    nb.save_all()


def retirer(modeles):
    rien = True
    for modele in modeles:
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
    return rien


def cmd_retirer():
    if retirer([m for m, _ in A_RETIRER]):
        print("essai vue d'ensemble compétition : rien à retirer")
    nb.save_all()


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
