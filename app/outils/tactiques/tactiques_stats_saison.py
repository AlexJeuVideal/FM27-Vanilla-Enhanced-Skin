"""Tactiques : bloc « Saison » sous le terrain, au-dessus des Remplaçants (affichages Medium et Small seulement).

Même cadre et même titre que le bloc Remplaçants de FM (`tactics-subs-block`, titre `thematic-sm`) :
- en-tête : « Saison » + nom du championnat ;
- ligne du championnat (classement FM) : Pos | J | G | N | P | BP | BC | Diff | Pts ;
- forme des 5 derniers matchs (case FM TeamLastFiveMatchesFormCell, celle des classements) ;
- stats de la saison de la page Stats du club (lignes FM ClubStatsStat*Row avec barre : buts par tir, tirs cadrés,
  passes, centres, têtes, tacles, distance, clean sheets, fautes, cartons…), en deux colonnes.
Caché en affichage Large (pas la place) et pendant un match.

Ligne du championnat : FM n'a pas de chemin « ligne de mon équipe » ; une liste FM (WrappedObjectList) parcourt le
classement `team.Division.CurrentStage.LeagueTable` et chaque case n'affiche rien sauf celle de l'équipe affichée
(row.Team.UniqueId == uipickerequipe.UniqueId). Case = LeagueTableTooltipGamesWonCell (cellule FM inutilisée, déjà
faite pour une ligne de classement : paramètre `row` de type 1668115573), réécrite.

Modèles (seul propriétaire : appliquer repart des originaux sauvegardés, retirer les remet) :
TacticalPlannerCollapsablePitchesDouble (colonne terrain + remplaçants), LeagueTableTooltipGamesWonCell.
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
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
                                 new_visible, SOURCE_COMPARE, FN_COMPARE, SOURCE_VISIBLE, FN_EGAL)
from arbre import no_styles  # noqa: E402
import arbre as sm  # noqa: E402
from elements import copy_usings  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
TITRE = 9544            # traduction FM « Season » (titre du bloc)
# ligne du championnat : (traduction FM de l'en-tête de colonne du classement, chemin dans la ligne)
CHAMPIONNAT = [
    (14516, "row.TablePosition"), (15884, "row.LeagueGamesPlayed"), (15886, "row.LeagueGamesWon"),
    (15887, "row.LeagueGamesDrawn"), (15888, "row.LeagueGamesLost"), (15889, "row.LeagueGoalsFor"),
    (15890, "row.LeagueGoalsAgainst"), (14525, "row.LeagueGoalDifference"), (15188, "row.LeaguePoints"),
]
FORME = 1229            # traduction FM « Form »
# stats de la page Stats du club (noms des lignes de ClubStatsShortBlock), réparties sur 2 colonnes
STATS = ["Goals", "Shots", "Penalties", "Passes", "Crosses", "Ariel",
         "Tackles", "Distance", "CleanSheets", "Fouls", "YellowCards", "RedCards"]
COLONNES = 2
MODES = 0               # affiché si settings.AdaptiveScalingLevelIndex > MODES (0 = Large : caché en Large)
HORS_MATCH = True
ECART = 16              # px sous le bloc (= écart FM terrain | Remplaçants, margin-bottom-16)
# =====================================================================================================

VERSION = 1
MODELE = "TacticalPlannerCollapsablePitchesDouble"
CELLULE = "LeagueTableTooltipGamesWonCell"
GUID_CELLULE = "327c1561d33a2e7469e64363924df25a"
GUID_FORME = "e0b64b86c2cb9f14681ffdca54c6f3d3"     # TeamLastFiveMatchesFormCell
SOURCE_STATS = "ClubStatsShortBlock"                # lignes de stats (page Stats du club)
SOURCE_LIGNE = "ClubStatsStatWithPercentRow"        # textes FM (libellé body-sm, valeur body-sm)
SOURCE_REMPLACANTS = "TacticalPlannerSubsBlock"     # en-tête du bloc Remplaçants
SOURCE_LISTE = "TeamMeetingBlock"                   # WrappedObjectList #Players
TYPE_EQUIPE = 1145176088
TYPE_COMPETITION = 1145176089
TYPE_STAT = 1181502314
PARAM_EQUIPE = "uipickerequipe"
PREFIXE = "UIPickerStatsSaison"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "tactiques_stats_saison.actif")

for _k, _v in {"width": (131105, 3), "margin-bottom": (131090, 3), "margin-left": (131091, 3),
               "margin-right": (131092, 3), "flex-direction": (131083, 7), "flex-wrap": (131086, 7),
               "align-items": (131073, 7), "text-align": (65546, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def nommer(t, r, nom):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1


def traduction(t, r, numero):
    """SIText FM (fonction de traduction eae2be94) -> texte FM <numero>"""
    sd = t.sd(r)
    f = sd["TextBinding"]["m_visualFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0].endswith(b"TranslationID]"):
            repere = f"UIPicker {numero}".encode()
            a[1] = struct.pack("<i", numero) + b"\x01" + _enc_varint(len(repere)) + repere
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["TextBinding_UxmlAttributeFlags"] = 1


def chemin_direct(t, r, chemin):
    sd = t.sd(r)
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["TextBinding_UxmlAttributeFlags"] = 1


class Morceaux:
    def __init__(self):
        self.ligne = hp.src_tree(SOURCE_LIGNE)
        lg = self.ligne
        self.libelle = lg and first(lg, lambda r: lg.name(r) == "Name")
        self.valeur = lg and first(lg, lambda r: lg.name(r) == "ValueText")
        self.stats = hp.src_tree(SOURCE_STATS)
        st = self.stats
        self.lignes = {n: st and first(st, lambda r, n=n: st.name(r) == f"{n}-Remapper") for n in STATS}
        self.rempl = hp.src_tree(SOURCE_REMPLACANTS)
        rp = self.rempl
        self.entete = rp and first(rp, lambda r: rp.name(r) == "Header")
        self.wlst = hp.src_tree(SOURCE_LISTE)
        w = self.wlst
        self.wliste = w and first(w, lambda r: w.name(r) == "Players" and typ(w, r).endswith("WrappedObjectList"))
        self.s_cmp, self.cmp = visible_model(SOURCE_COMPARE, FN_COMPARE)
        self.s_int, self.int = visible_model(SOURCE_VISIBLE, FN_EGAL)

    def manquants(self):
        noms = {"libellé / valeur FM": (self.libelle, self.valeur), "en-tête des Remplaçants": (self.entete,),
                "liste FM": (self.wliste,), "visibilités FM": (self.cmp, self.int)}
        noms.update({f"ligne de stats {n}": (r,) for n, r in self.lignes.items()})
        return [k for k, v in noms.items() if None in v]


def texte(t, mx, parent, modele, classes):
    x = t.clone(modele, parent, src=mx.ligne)
    no_styles(t, x)
    t.elem(x)["m_Classes"] = list(classes)
    return x


# ---------- la case du classement (LeagueTableTooltipGamesWonCell réécrite) ----------
def construire_cellule(t, mx):
    racine = t.tt["m_VisualTree"]["rid"]
    comp = next((r for r in t.children(racine) if typ(t, r) == "ComponentElement"), None)
    if comp is None:
        return ["cellule du classement : structure FM inattendue"]
    composants = [c["rid"] for c in t.sd(comp).get("m_components") or []]
    attente = next((c for c in composants if "BindingExpect" in t.refs[c]["type"]["class"]), None)
    if attente is None:
        return ["cellule du classement : paramètres FM introuvables"]
    params = t.refs[attente]["data"]["Parameters"]
    row = next((p for p in params if p["name"] == "row"), None)
    if row is None:
        return ["cellule du classement : paramètre row introuvable"]
    eq = copy.deepcopy(row)
    eq["name"], eq["type"]["id"], eq["isOptional"] = PARAM_EQUIPE, TYPE_EQUIPE, 1
    params[:] = [row, eq]   # « comp » (infobulle FM) retiré
    for k in list(t.children(comp)):
        t.remove(k)
    t.styles.style(t, comp, {"flex-grow": 1})

    b = make_binding(mx.s_cmp.sd(mx.cmp)["Binding"], 2, ["row.Team.UniqueId", f"{PARAM_EQUIPE}.UniqueId"])
    vis = new_visible(t, mx.s_cmp, mx.cmp, comp, None, f"{PREFIXE}-ligne", b, ["row-direction-normal"])
    t.sd(vis)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, vis, {"flex-grow": 1})
    for numero, chemin in CHAMPIONNAT:
        col = sm_plain(t, vis, mx)
        t.styles.style(t, col, {"flex-grow": 1, "flex-basis": 0, "align-items": "center"})
        tete = texte(t, mx, col, mx.libelle, ["body-xs", "global-text-secondary"])
        traduction(t, tete, numero)
        val = texte(t, mx, col, mx.valeur, ["body-md", "global-text-primary"])
        chemin_direct(t, val, chemin)
    return [f"case du classement : {CELLULE} réécrite (ligne de l'équipe affichée seulement)"]


def t_nameframe(mx):
    return first(mx.ligne, lambda r: mx.ligne.name(r) == "NameFrame")


def sm_plain(t, parent, mx):
    """VisualElement vide (copie du #NameFrame des lignes de stats FM, vidé), sans règle de style héritée"""
    v = t.clone(t_nameframe(mx), parent, src=mx.ligne)
    for k in list(t.children(v)):
        t.remove(k)
    no_styles(t, v)
    t.sd(v)["name"] = ""
    t.elem(v)["m_Classes"] = []
    t.elem(v)["m_RuleIndex"] = -1
    return v


# ---------- le bloc ----------
def construire_bloc(t, mx):
    racine = t.tt["m_VisualTree"]["rid"]
    colonne = next((r for r in t.children(racine) if typ(t, r) == "ComponentElement"), None)
    rempl = colonne and next((r for r in t.children(colonne) if any(
        t.elem(k).get("m_TemplateAlias") == "TacticalPlannerSubsBlock" for k in t.children(r))), None)
    direct = first(t, lambda r: t.name(r) == "ShowFMCHeader")
    if rempl is None or direct is None:
        return ["colonne terrain / Remplaçants de FM introuvable"]

    # SIVisible mode d'affichage > [SIVisible hors match] > cadre des Remplaçants
    b = make_binding(mx.s_int.sd(mx.int)["Binding"], 4, ["settings.AdaptiveScalingLevelIndex"], MODES)
    mode = new_visible(t, mx.s_int, mx.int, colonne, t.children(colonne).index(rempl), NOM_RACINE, b)
    t.sd(mode)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, mode, {"flex-shrink": 0})
    parent = mode
    if HORS_MATCH:
        m = t.clone(direct, mode)
        for k in list(t.children(m)):
            t.remove(k)
        no_styles(t, m)
        t.elem(m)["m_Classes"] = []
        nommer(t, m, f"{PREFIXE}-hors-match")
        sd = t.sd(m)
        sd["Binding"]["m_direct"]["Path"]["m_path"] = "tactic.IsDuringMatch"
        sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 1, 1
        parent = m
    cadre = sm_plain(t, parent, mx)
    t.elem(cadre)["m_Classes"] = ["tactics-subs-block"]
    nommer(t, cadre, f"{PREFIXE}-cadre")
    t.styles.style(t, cadre, {"margin-bottom": ECART, "flex-shrink": 0})

    # en-tête : « Saison » à gauche, championnat à droite (comme « Remplaçants » | « 6 sur 12 »)
    ent = t.clone(mx.entete, cadre, src=mx.rempl)
    for k in list(t.children(ent)):
        t.remove(k)
    titre = texte(t, mx, ent, mx.libelle, ["thematic-sm"])
    traduction(t, titre, TITRE)
    champ = texte(t, mx, ent, mx.valeur, ["body-sm", "secondary-text-colour"])
    chemin_direct(t, champ, "team.Division.Name")

    # ligne du championnat : liste FM sur le classement, seule la case de l'équipe affichée s'affiche
    remap = t.clone(mx.lignes[STATS[0]], cadre, src=mx.stats)
    for k in list(t.children(remap)):
        t.remove(k)
    no_styles(t, remap)
    t.elem(remap)["m_Classes"] = []
    nommer(t, remap, f"{PREFIXE}-championnat")
    mp = t.sd(remap)["Mappings"][0]
    mp["from"], mp["to"]["m_path"], mp["type"]["id"] = PARAM_EQUIPE, "team", TYPE_EQUIPE
    w = t.clone(mx.wliste, remap, src=mx.wlst)
    for k in list(t.children(w)):
        t.remove(k)
    no_styles(t, w)
    wd = t.sd(w)
    wd["name"] = ""
    wd["ItemTemplate"] = {"m_AssetGUID": GUID_CELLULE, "m_SubObjectName": "", "m_SubObjectType": ""}
    wd["VisualFuncBinding"] = path_arg(wd["VisualFuncBinding"], "team.Division.CurrentStage.LeagueTable")
    wd["ItemParamName"] = "row"
    t.styles.style(t, w, {"flex-direction": "column", "flex-wrap": "nowrap"})

    # forme : libellé + case FM des 5 derniers matchs
    ligne_forme = sm_plain(t, cadre, mx)
    t.elem(ligne_forme)["m_Classes"] = ["row-direction-normal", "align-items-center", "padding-horizontal-global-padding-regular"]
    t.styles.style(t, ligne_forme, {"margin-bottom": 4})
    lib = texte(t, mx, ligne_forme, mx.libelle, ["body-sm", "global-text-secondary", "margin-right-global-gap-regular"])
    traduction(t, lib, FORME)
    rf = t.clone(mx.lignes[STATS[0]], ligne_forme, src=mx.stats)
    nommer(t, rf, f"{PREFIXE}-forme")
    t.sd(rf)["Mappings"] = [
        dict(copy.deepcopy(t.sd(rf)["Mappings"][0]), **{"from": "binding"}),
        dict(copy.deepcopy(t.sd(rf)["Mappings"][0]), **{"from": "competition"})]
    for m_, chemin, ident in zip(t.sd(rf)["Mappings"], ("team", "team.Division"), (TYPE_EQUIPE, TYPE_COMPETITION)):
        m_["to"] = {"m_path": chemin}
        m_["type"] = {"id": ident}
    tpl = t.children(rf)[0]
    e = t.elem(tpl)
    e["m_TemplateAlias"] = "TeamLastFiveMatchesFormCell"
    e["m_SerializedDataOverride"] = []
    e["m_Classes"] = []
    t.sd(tpl)["templateId"] = "TeamLastFiveMatchesFormCell"
    u = copy.deepcopy(next(x for x in mx.stats.tt["m_Usings"] if x.get("alias") == "ClubStatsStatWithPercentRow"))
    u["alias"], u["path"] = "TeamLastFiveMatchesFormCell", GUID_FORME
    if not any(x.get("alias") == u["alias"] for x in t.tt.setdefault("m_Usings", [])):
        t.tt["m_Usings"].append(u)

    # stats de la saison (lignes FM de la page Stats du club) en colonnes
    grille = sm_plain(t, cadre, mx)
    t.elem(grille)["m_Classes"] = ["row-direction-normal"]
    cols = []
    for i in range(COLONNES):
        c = sm_plain(t, grille, mx)
        t.styles.style(t, c, {"flex-grow": 1, "flex-basis": 0})
        if i:
            t.styles.style(t, c, {"margin-left": 8})
        cols.append(c)
    par_col = -(-len(STATS) // COLONNES)
    for i, n in enumerate(STATS):
        col = cols[i // par_col]
        r = t.clone(mx.lignes[n], col, src=mx.stats)
        m0 = t.sd(r)["Mappings"][0]
        m0["to"]["m_path"] = m0["to"]["m_path"].replace("stats.", "team.ReportStatsData.", 1)
        copy_usings(t, mx.stats, mx.lignes[n])
        tp = t.children(r)[0]   # rangées alternées dans chaque colonne
        t.elem(tp)["m_Classes"] = ["generic-row-odd" if (i % par_col) % 2 == 0 else "generic-row-even"]
    return [f"bloc « Saison » au-dessus des Remplaçants : championnat ({len(CHAMPIONNAT)} colonnes), forme, "
            f"{len(STATS)} stats ; affichages Medium / Small" + (", hors match" if HORS_MATCH else "")]


# ---------- commandes ----------
MODELES = [MODELE, CELLULE]


def cmd_appliquer():
    actuels = {m: ouvrir(m) for m in MODELES}
    if None in actuels.values():
        print("modèles du terrain des tactiques introuvables (renommés par une mise à jour ?), ignoré")
        return
    if any(actuels[MODELE][3].name(r) == NOM_RACINE for r in marques(actuels[MODELE][3])):
        print("stats de la saison (tactiques) : déjà appliqué")
    else:
        ancien = any(marques(v[3]) for v in actuels.values())
        travail = {m: ouvrir(m, depart_original=True) for m in MODELES}
        if any(marques(v[3]) for v in travail.values()):
            print("stats de la saison (tactiques) : pas de sauvegarde d'origine propre, ignoré")
            return
        mx = Morceaux()
        manque = mx.manquants()
        if manque:
            print("stats de la saison (tactiques) : morceaux de FM introuvables (" + ", ".join(manque) + "), rien enregistré")
            return
        msgs = construire_cellule(travail[CELLULE][3], mx) + construire_bloc(travail[MODELE][3], mx)
        msgs += ["ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"stats de la saison (tactiques) : {m}")
        if any("introuvable" in m or "inattendue" in m for m in msgs):
            print("stats de la saison (tactiques) : rien enregistré")
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
    for m in MODELES:
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
    for m in MODELES:
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        cible = NOM_RACINE if m == MODELE else f"{PREFIXE}-ligne"
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
            print("stats de la saison (tactiques) : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
