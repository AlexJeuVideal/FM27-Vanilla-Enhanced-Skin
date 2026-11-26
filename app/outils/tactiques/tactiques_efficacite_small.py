"""Tactiques : infos d'efficacité tactique dans le vert vide sous le terrain (affichage Small seulement).

2026-11-26 (le joueur, capture Positionnement de l'équipe en Small : « ajoute l'efficacité tactique sous la tactique,
là où il y a l'espace vide en bas à gauche »). v1 : tuile 4x2 entre le panneau et les Remplaçants (panneau rétréci :
« pas qu'il remplace », « pas une tuile à proprement parler, juste les infos dans l'espace vide », « le max d'infos »).
v2 : le tableau de FM TacticalEffectivenessTileTable (celui des tuiles 4x4 / 8x4, sans cadre : nom de la tactique,
niveau global, compréhension / capacité / adhésion / infos du match, jauges), en ABSOLU en bas de la colonne du 1er
terrain (le vert = fond du terrain de FM, plus haut que le terrain dessiné) : rien ne bouge, un seul exemplaire même
en mode « Les deux ». Caché en Large / Medium et pendant un match.

Modèle (seul écrivain : appliquer repart de l'original sauvegardé, retirer le remet) :
TacticalPlannerCollapsablePitchesDouble (colonne terrain + remplaçants).
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import (first, make_binding, new_visible, visible_model,  # noqa: E402
                                 SOURCE_VISIBLE, FN_EGAL)
from arbre import no_styles  # noqa: E402
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
TUILE = ("TacticalEffectivenessTileTable", "97b3a214fcd121c40b75a6a76e4773dc")
BAS = 28                # px entre le bas de la colonne et les infos (16 sous le panneau vert de FM + 12 dans le vert)
COTES = 16              # px à gauche / à droite (dans le vert)
FOND = (0, 0, 0, 0.25)  # v3 (le joueur : « ça ressort pas assez ») : voile sombre derrière ; None = rien
#                         v4 : 0,35 -> 0,25 (le joueur : « un poil trop sombre »)
MARGE_FOND = 10         # px entre le bord du voile et les infos
RAYON = 6               # coins du voile
MODE = 2                # settings.AdaptiveScalingLevelIndex : Large 0, Medium 1, Small 2
OP_EGAL = 2             # ComparisonOperator de FM « = »
HORS_MATCH = True
TITRE = True            # v3 (le joueur : « pas de titre ») : titre de FM « Efficacité tactique » au-dessus
# paramètres du tableau de FM (types de son BindingExpect)
PASSAGES = [("effectiveness", "tactic.TacticalEffectiveness", 842556533), ("tactic", "tactic", 2003981122),
            ("showheader", "const.true", 0)]
# =====================================================================================================

VERSION = 4
MODELE = "TacticalPlannerCollapsablePitchesDouble"
SOURCE_REMAP = "ClubStatsShortBlock"      # remappeur FM + modèle inclus dedans (#Goals-Remapper)
SOURCE_TITRE = "TacticalEffectivenessBlock"   # SIText « Tactical Effectiveness » (traduit par FM)
PREFIXE = "UIPickerEfficaciteSmall"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
CLASSE = f"uipicker-efficacite-small-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "tactiques_efficacite_small.actif")

for _k, _v in {"position": (131102, 7), "left": (131089, 3), "right": (131103, 3), "bottom": (131080, 3),
               "padding-left": (131099, 3), "padding-right": (131100, 3), "padding-top": (131101, 3),
               "padding-bottom": (131098, 3), "border-top-left-radius": (458764, 3),
               "border-top-right-radius": (458765, 3), "border-bottom-left-radius": (458759, 3),
               "border-bottom-right-radius": (458760, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def nommer(t, r, nom):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1


class Morceaux:
    def __init__(self):
        self.src = hp.src_tree(SOURCE_REMAP)
        s = self.src
        self.remap = s and first(s, lambda r: s.name(r) == "Goals-Remapper")
        self.s_int, self.int = visible_model(SOURCE_VISIBLE, FN_EGAL)
        self.src_titre = hp.src_tree(SOURCE_TITRE)
        st = self.src_titre
        self.titre = st and first(st, lambda r: typ(st, r).endswith("SIText")
                                  and t_debug(st, r) == "Tactical Effectiveness")

    def manquants(self):
        return [k for k, v in {"remappeur FM": self.remap, "visibilité FM": self.int,
                               "titre FM": self.titre}.items() if v is None]


def t_debug(t, r):
    return (t.sd(r) or {}).get("DebugDisplay")


def construire(t, mx):
    direct = first(t, lambda r: t.name(r) == "ShowFMCHeader")
    colonne = direct and t.parent.get(direct)   # colonne du 1er terrain (en-tête + terrain de FM)
    if colonne is None or not any(t.elem(k).get("m_TemplateAlias") == "TacticalPlannerCollapsablePitches"
                                  for k in t.children(colonne)):
        return ["colonne du terrain de FM introuvable"]

    # SIVisible Small (absolu, en bas de la colonne) > [SIVisible hors match] > remappeur > tableau de FM
    b = make_binding(mx.s_int.sd(mx.int)["Binding"], OP_EGAL, ["settings.AdaptiveScalingLevelIndex"], MODE)
    mode = new_visible(t, mx.s_int, mx.int, colonne, None, NOM_RACINE, b, [CLASSE])
    t.sd(mode)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, mode, {"position": "absolute", "left": COTES, "right": COTES, "bottom": BAS,
                             **({"background-color": FOND,
                                 **{f"padding-{c}": MARGE_FOND for c in ("left", "right", "top", "bottom")},
                                 **{f"border-{c}-radius": RAYON for c in ("top-left", "top-right", "bottom-left",
                                                                          "bottom-right")}} if FOND else {})})
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

    if TITRE:   # v3 : titre de FM « Efficacité tactique », style du titre des Remplaçants
        ti = t.clone(mx.titre, parent, src=mx.src_titre)
        no_styles(t, ti)
        t.sd(ti)["name"] = ""
        t.elem(ti)["m_Classes"], t.elem(ti)["m_RuleIndex"] = ["thematic-sm", "padding-bottom-global-padding-small"], -1

    rm = t.clone(mx.remap, parent, src=mx.src)
    nommer(t, rm, f"{PREFIXE}-tuile")
    no_styles(t, rm)
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = [], -1
    sd = t.sd(rm)
    m0 = sd["Mappings"][0]
    sd["Mappings"] = [dict(copy.deepcopy(m0), **{"from": de, "to": {"m_path": vers}, "type": {"id": ty}})
                      for de, vers, ty in PASSAGES]
    if "Mappings_UxmlAttributeFlags" in sd:
        sd["Mappings_UxmlAttributeFlags"] = 1
    tpl = t.children(rm)[0]
    for k in list(t.children(rm))[1:]:
        t.remove(k)
    alias, guid = TUILE
    e = t.elem(tpl)
    e["m_TemplateAlias"], e["m_SerializedDataOverride"], e["m_Classes"], e["m_RuleIndex"] = alias, [], [], -1
    st = t.sd(tpl)
    if "templateId" in st:
        st["templateId"] = alias
    st["name"], st["name_UxmlAttributeFlags"] = "", 0
    usings = t.tt.setdefault("m_Usings", [])
    if not any(u.get("alias") == alias for u in usings):
        modele_u = next(x for x in mx.src.tt["m_Usings"] if x.get("alias") == "ClubStatsStatWithPercentRow")
        u = copy.deepcopy(modele_u)
        u["alias"], u["path"] = alias, guid
        usings.append(u)
    return ["tableau Efficacité tactique de FM dans le vert sous le terrain ; affichage Small"
            + (", hors match" if HORS_MATCH else "")]


# ---------- commandes ----------
def cmd_appliquer():
    actuel = ouvrir(MODELE)
    if actuel is None:
        print("modèle du terrain des tactiques introuvable (renommé par une mise à jour ?), ignoré")
        return
    if any(actuel[3].name(r) == NOM_RACINE for r in marques(actuel[3])):
        print("efficacité tactique (Small) : déjà appliqué")
    else:
        ancien = bool(marques(actuel[3]))
        bundle, obj, tt, t = ouvrir(MODELE, depart_original=True)
        if marques(t):
            print("efficacité tactique (Small) : pas de sauvegarde d'origine propre, ignoré")
            return
        mx = Morceaux()
        manque = mx.manquants()
        if manque:
            print("efficacité tactique (Small) : morceaux de FM introuvables (" + ", ".join(manque) + "), rien enregistré")
            return
        msgs = construire(t, mx) + (["ancienne version remplacée"] if ancien else [])
        for m in msgs:
            print(f"efficacité tactique (Small) : {m}")
        if any("introuvable" in m for m in msgs):
            print("efficacité tactique (Small) : rien enregistré")
            return
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
    o = ouvrir(MODELE)
    if o is None or not marques(o[3]):
        print("rien à retirer")
        return
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{MODELE} : remis d'origine")


def cmd_etat():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        t = o[3]
        etat = "à jour" if any(t.name(r) == NOM_RACINE for r in marques(t)) else "ANCIENNE version"
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
            print("efficacité tactique (Small) : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
