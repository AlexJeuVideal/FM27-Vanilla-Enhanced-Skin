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
Coupe : plus touchée depuis v7 (retirer remet aussi les modèles posés par v1-v6).
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

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
PART_CENTRE = 77        # parts de largeur : centre (haut + stats) | droite (transferts)
PART_DROITE = 23
# v13 : rangée du haut (hauteur du classement) = classement | 11 | Records | Rencontres | Classements (parts)
PART_TABLE = 9
PART_ONZE = 8
PART_TUILE = 6
COLONNES = 5            # stats par rangée (de gauche à droite)
# numéros des stats (titres donnés par FM), lus en jeu (v7) : 2 buts, 5 passes D, 46 tirs, 23 passes clés,
# 63 tacles remportés, 27 note moy., 12 homme du match, 13 passes réussies (%), 62 dribbles, 20 clean sheets.
# Ordre : le joueur le donnera.
STATS_JOUEURS = (2, 5, 46, 23, 63, 27, 12, 13, 62, 20)
STATS_EQUIPES = (5, 15, 28, 54, 55, 24, 25, 41, 16)    # celles de FM (onglet Stats équipes)
HAUT_CASE = 120         # px d'une stat (celle de FM)
ECART_CASE = 12         # px entre deux cases
ECART = 12              # px entre la rangée du haut et les stats, entre deux blocs
TUILES_HAUT = (("CompetitionSiteAboutRecordsTile_4x4", "7c7f3ff24678c48c8b8f2ca6fab3b813"),   # Records
               ("CompetitionSiteFixturesTile_4x4", "96ca4232ba738c946a7ea74b0f979cdd"),       # Rencontres
               ("CompetitionAboutRankingsTile_4x4", "a94aad0e16a943e44a736f9ad138d1c4"))      # Classements
# =====================================================================================================

VERSION = "13"
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
               "margin-left": (131091, 3), "max-height": (131094, 3), "align-self": (131074, 7)}.items():
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


def ligue(t):
    o = Outils(t)
    nom = lambda n: first(t, lambda r: t.name(r) == n)  # noqa: E731
    rang, table, div1, onze = nom("ActiveNoParent"), nom("LeagueTable"), nom("Divider1"), nom("TeamOfTheWeek")
    div2, transferts, div3, news = nom("Divider2"), nom("TransferNewsVisible"), nom("Divider3"), nom("CompNews")
    inst_onze = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == MODELE_ONZE)
    if None in (rang, table, div1, onze, div2, transferts, news, inst_onze, o.trait, o.vide, o.remap):
        return None, "éléments FM introuvables (classement, 11 de la semaine, transferts, articles)"
    src = source_detail()
    racine = src and first(src, lambda r: typ(src, r) == "ComponentElement" and src.parent.get(r) is not None
                           and typ(src, src.parent[r]) == "BindingExpect")
    racine = racine or (src and first(src, lambda r: typ(src, r) == "ComponentElement"))
    cell_j = src and first(src, lambda r: src.name(r) == "PlayerStatsContent")
    cell_e = src and first(src, lambda r: src.name(r) == "TeamStatsContent")
    if None in (src, racine, cell_j, cell_e):
        return None, f"{MODELE_DETAIL} : éléments introuvables (bloc, stats joueurs / équipes)"
    # articles (et le trait avant eux) : boîte cachée
    # la rangée et ses parents prennent toute la hauteur (v2)
    x = rang
    while x is not None and t.name(x) != "Container":
        o.st.style(t, x, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        x = t.parent.get(x)
    # v12 : centre (à la place du classement) = rangée du haut puis le bloc stats de FM recopié (stats en grille)
    centre = o.colonne(rang, PART_CENTRE, t.children(rang).index(table), NOM)
    # v13 : hauteur = celle du classement (pas étirée jusqu'aux stats)
    haut = o.boite(centre, {"flex-direction": "row", "flex-grow": 0, "flex-shrink": 0, "min-width": 0},
                   nom=f"{PREFIXE}Haut")
    bas = haut   # (11 et tuiles posés plus bas dans la rangée du haut)
    cpb.move(t, table, haut)
    o.st.style(t, table, {"flex-grow": PART_TABLE, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                          "min-height": 0})
    # articles et trait classement | centre : boîte cachée
    cache = o.cache(rang)
    for x in (div1, div3, news):
        if x is not None:
            cpb.move(t, x, cache)
    # v13 : stats centrées en hauteur dans la place restante (vide égal dessus / dessous)
    vide_css = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": ECART}
    o.boite(centre, vide_css)
    bloc = t.clone(racine, centre, src=src)
    t.styles.copy_from(src.styles, t, bloc)
    copy_usings(t, src, racine)
    o.st.style(t, bloc, {"flex-grow": 0, "flex-shrink": 0, "min-width": 0})
    o.boite(centre, vide_css)
    recomp = first_in(t, bloc, lambda r: t.name(r) == "Awards")
    if recomp is None:
        return None, "onglet Récompenses (#Awards) introuvable"
    o.st.style(t, recomp, {"display": 6})   # mot-clé None (display: none)
    mon_j = first_in(t, bloc, lambda r: t.name(r) == "PlayerStatsContent")
    mon_e = first_in(t, bloc, lambda r: t.name(r) == "TeamStatsContent")
    for contenu, cel, var, ids in ((mon_j, cell_j, "playerStatTypes", STATS_JOUEURS),
                                   (mon_e, cell_e, "teamStatTypes", STATS_EQUIPES)):
        err = grille(o, contenu, src, cel, var, ids)
        if err:
            return None, err
    # droite (Large seulement) : enveloppe = recopie de #TransferNewsVisible ; trait | 11 de la semaine + transferts
    j = t.children(rang).index(centre) + 1
    env = t.clone_shallow(transferts, rang, j)
    t.sd(env)["name"], t.sd(env)["name_UxmlAttributeFlags"] = f"{PREFIXE}Droite", 1
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    o.st.style(t, env, {"flex-direction": "row", "flex-grow": PART_DROITE, "flex-shrink": 1, "flex-basis": 0,
                        "min-width": 0, "min-height": 0})
    cpb.move(t, div2, env)
    droite = o.colonne(env, 1)
    # v8 : 11 dans une recopie de #TeamOfTheWeekTitleVisible (même condition que son titre : 11 de la semaine / des
    # médias connu) ; sans lui (v7 : fin de saison), la place vide va aux transferts
    titre_onze = first_in(t, onze, lambda r: t.name(r) == "TeamOfTheWeekTitleVisible")
    if titre_onze is None:
        return None, "#TeamOfTheWeekTitleVisible introuvable"
    env_onze = t.clone_shallow(titre_onze, bas)
    t.sd(env_onze)["name"], t.sd(env_onze)["name_UxmlAttributeFlags"] = f"{PREFIXE}Onze", 1
    t.elem(env_onze)["m_Classes"], t.elem(env_onze)["m_RuleIndex"] = [], -1
    for cle in ("StyleClassToApplyOnVisible", "StyleClassBindingToApplyOnVisible"):
        if isinstance(t.sd(env_onze).get(cle), str):
            t.sd(env_onze)[cle] = ""
    o.st.style(t, env_onze, {"flex-direction": "column", "flex-grow": PART_ONZE, "flex-shrink": 1,
                             "flex-basis": 0, "min-height": 0, "min-width": 0, "margin-left": ECART})
    cpb.move(t, onze, env_onze)
    o.st.style(t, onze, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
    for y in (onze, *[r for r in t.walk(onze) if "comp-site-totw-block" in (t.elem(r).get("m_Classes") or [])]):
        o.st.style(t, y, {"width": CENT, "min-width": 0, "max-width": CENT})
    parent = t.parent[inst_onze]
    rm = t.clone_shallow(o.remap, parent, t.children(parent).index(inst_onze))
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = ["flex-grow-class"], -1
    t.sd(rm)["name"], t.sd(rm)["name_UxmlAttributeFlags"] = f"{PREFIXE}SansListe", 1
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": "showDetails", "to": {"m_path": "const.False"},
                             "type": {"id": 0}}]
    cpb.move(t, inst_onze, rm)
    # v12 : tuiles 4x4 de FM dans la rangée du haut (Records | Rencontres), chacune sa part de largeur
    for modele, guid in TUILES_HAUT:
        col = o.boite(bas, {"flex-direction": "column", "flex-grow": PART_TUILE, "flex-shrink": 1, "flex-basis": 0,
                            "min-width": 0, "min-height": 0, "margin-left": ECART})
        tu = o.tuile(col, modele, guid)
        o.st.style(t, tu, {"flex-grow": 1, "min-height": 0, "min-width": 0})
    cpb.move(t, transferts, droite)
    o.st.style(t, transferts, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
    return ("championnat : haut = classement | 11 | Records | Rencontres | Classements ; stats centrées (%d joueurs, "
            "%d équipes, %d par rangée, sans Récompenses) | transferts (Large)"
            % (len(STATS_JOUEURS), len(STATS_EQUIPES), COLONNES)), None


def coupe(t):
    return None, "plus touchée depuis v7"


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


LIGNES_STATS = ("CompPlayerStatRow", "CompTeamStatRow")
MODELES = ((LIGUE, ligue),) + tuple((m, ligne_stat) for m in LIGNES_STATS)
A_RETIRER = MODELES + ((COUPE, coupe), (MODELE_LIGNE, None))   # v1-v6 posaient aussi la coupe / la ligne


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
    retirer((COUPE, MODELE_LIGNE))
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
