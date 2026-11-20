"""Tuile « Forme » de la fiche joueur (5 derniers matchs) mieux remplie en Medium / Small (demande du joueur,
2026-11-20 : « en petit les stats sont trop hautes par rapport à la forme, remplis mieux la tuile, en grand touche
pas »).

- Medium (PlayerFormTile_2x2) : graphique des 5 notes sur toute la largeur et toute la hauteur libre ; dessous, sur une
  ligne : note moyenne + « 5 derniers matchs (en club) ».
- Small (PlayerFormTile_4x2 dans une place de 2) : graphique sur toute la hauteur libre ; dessous, la rangée buts |
  passes D | note (gardien : clean sheets | encaissés | note) à la largeur de la tuile (FM : 288 px fixes, plus large
  que la tuile = colonnes décalées), icônes / note dans une case de même hauteur = textes alignés.
- Large : tuile de FM (aiguillage sur le mode d'affichage : copie de FM en Large, la nôtre en Medium / Small).

Repart toujours du modèle d'origine (sauvegarde). Repérage par noms de FM (#MatchRating, #Outfield...).
Usage (jeu fermé) : tuile_forme_matchs.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import FIXE, PROPRIETES  # noqa: E402
from elements import first, typ, move, plain  # noqa: E402
from attributs_tout_cocher import ouvrir  # noqa: E402  (modèle d'origine + sa feuille de style)
from tuile_forme import si_large  # noqa: E402  (SIVisible selon le mode Large / Medium-Small)

for _k, _v in {"align-self": (131074, 7), "align-items": (131073, 7), "justify-content": (131088, 7),
               "width": (131105, 3), "height": (131087, 3), "margin-top": (131093, 3),
               "margin-right": (131092, 3)}.items():
    PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
GRAPHE_MIN = 56     # px : hauteur minimum du graphique (FM : 56 fixes) ; il prend toute la place libre au-dessus
CASE_HAUT = 24      # px : case des icônes / de la note (Small) : textes en dessous tous à la même hauteur
ECART_NOTE = 8      # px : entre la note et « 5 derniers matchs » (Medium)
ECART_RANGEE = 6    # px : au-dessus de la rangée du bas (sous le graphique)
# =====================================================================================================

T2X2 = "PlayerFormTile_2x2"
T4X2 = "PlayerFormTile_4x2"
MODELES = [T2X2, T4X2]
MARKER = os.path.join(backup.BACKUP_DIR, "tuile_forme_matchs.actif")
PREFIXE = "UIPickerFormeMatchs"
VERSION = "uipicker-forme-matchs-v1"   # changer le numéro refait les tuiles
AUTO = (1, 2)                          # mot-clé auto (style intégré)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def a_jour(t):
    return any(VERSION in (t.elem(m).get("m_Classes") or []) for m in marques(t))


def regle(t, rid, props):
    """style intégré : props [(nom CSS, (type, valeur))] (mots-clés compris), ajoutés / remplacés"""
    e = t.elem(rid)
    old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    new = {PROPRIETES[k][0]: (PROPRIETES[k][0], "", [v]) for k, v in props}
    e["m_RuleIndex"] = t.styles.add_rule([p for p in old if p[0] not in new] + list(new.values()))


def sans_classes(t, rid, retirer):
    e = t.elem(rid)
    e["m_Classes"] = [c for c in e.get("m_Classes") or [] if c not in retirer]


def chemin(t, r):
    out = []
    while r is not None:
        out.append(r)
        r = t.parent.get(r)
    return out


def graphe(t, liste):
    """graphique des 5 notes : toute la largeur, toute la hauteur libre (barres en % de la hauteur)"""
    t.styles.style(t, liste, {"flex-grow": 1, "flex-shrink": 1, "min-height": GRAPHE_MIN})
    regle(t, liste, [("align-self", (7, "stretch"))])


def aiguillage(t):
    """contenu de FM (enfant de la tuile) -> [Large : celui de FM] [Medium / Small : copie] ; renvoie la copie"""
    tuile = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "").startswith("tile-"))
    if tuile is None or not t.children(tuile):
        return None
    contenu = t.children(tuile)[0]
    boites = []
    for large in (True, False):
        v = si_large(t, tuile, None, large, ["column-direction-normal"])
        t.sd(v)["name"] = PREFIXE + ("Large" if large else "Petit")
        t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        regle(t, v, [("align-self", (7, "stretch"))])
        boites.append(v)
    t.elem(boites[1])["m_Classes"] += [VERSION]
    copie = t.clone(contenu, boites[1])
    move(t, contenu, boites[0])
    return copie


def tuile_2x2(t):
    copie = aiguillage(t)
    if copie is None:
        return ["cadre de la tuile introuvable (le jeu a changé ?), ignoré"]
    note = first(t, lambda r: t.name(r) == "MatchRating" and copie in chemin(t, r))
    if note is None:
        return ["#MatchRating introuvable (le jeu a changé ?), ignoré"]
    kids = t.children(note)
    liste = next((k for k in kids if typ(t, k).endswith("StreamedObjectList")), None)
    remap = next((k for k in kids if typ(t, k).endswith("BindingRemapper")), None)
    texte = next((k for k in kids if typ(t, k).endswith("SIText")), None)
    if liste is None or remap is None or texte is None:
        return ["graphique / note / texte introuvables (le jeu a changé ?), ignoré"]
    # FM : align-self-start = colonne à la largeur du graphique (5 x 25 px), calée à gauche
    sans_classes(t, note, ["align-self-start"])
    regle(t, note, [("align-self", (7, "stretch")), ("justify-content", (7, "flex-start"))])
    graphe(t, liste)
    rang = plain(t, note, None, ["row-direction-normal", "align-items-center"], PREFIXE + "Note")
    t.elem(rang)["m_RuleIndex"] = -1
    t.styles.style(t, rang, {**FIXE, "margin-top": ECART_RANGEE})
    move(t, remap, rang)
    t.elem(remap)["m_Classes"] = []
    t.styles.style(t, remap, {**FIXE, "margin-right": ECART_NOTE})
    move(t, texte, rang)
    sans_classes(t, texte, ["margin-bottom-global-gap-small", "align-self-start"])
    t.styles.style(t, texte, {"flex-shrink": 1, "min-width": 0})
    return ["Medium / Small : graphique sur toute la tuile, note + « 5 derniers matchs » sur une ligne dessous",
            "Large : tuile de FM"]


def tuile_4x2(t):
    copie = aiguillage(t)
    if copie is None:
        return ["cadre de la tuile introuvable (le jeu a changé ?), ignoré"]
    liste = first(t, lambda r: typ(t, r).endswith("StreamedObjectList") and copie in chemin(t, r))
    if liste is None:
        return ["graphique introuvable (le jeu a changé ?), ignoré"]
    cadre = t.parent[liste]
    regle(t, cadre, [("align-items", (7, "stretch"))])
    graphe(t, liste)
    sans_classes(t, liste, ["padding-bottom-global-padding-regular"])
    stats = next((k for k in t.children(cadre) if k != liste), None)
    if stats is not None:
        sans_classes(t, stats, ["flex-grow-class"])
        t.styles.style(t, stats, {**FIXE, "margin-top": ECART_RANGEE})
    rangs = [r for r in t.walk(copie) if t.name(r) in ("NoMatches", "Outfield", "Goalkeeper")]
    for r in rangs:
        # FM : 288 x 40 px fixes (plus large que la tuile en Small)
        regle(t, r, [("width", AUTO), ("height", AUTO), ("align-self", (7, "stretch")),
                     ("align-items", (7, "flex-start"))])
        sans_classes(t, r, ["margin-bottom-global-gap-regular"])
        for col in t.children(r):
            if t.name(col) != "Frame":
                if t.elem(col).get("m_TemplateAlias") == "layout-divider-solid-vertical":
                    regle(t, col, [("align-self", (7, "stretch"))])
                continue
            regle(t, col, [("justify-content", (7, "flex-start")), ("align-items", (7, "center"))])
            haut = t.children(col)[0] if t.children(col) else None
            if haut is None or typ(t, haut).endswith("SIText"):
                continue
            case = plain(t, col, 0, ["align-items-center", "justify-content-center"], PREFIXE + "Case")
            t.elem(case)["m_RuleIndex"] = -1
            t.styles.style(t, case, {**FIXE, "height": CASE_HAUT, "min-height": CASE_HAUT, "margin-bottom": 2})
            regle(t, case, [("align-self", (7, "stretch"))])
            move(t, haut, case)
            sans_classes(t, haut, ["margin-bottom-global-gap-small"])
            for k in t.walk(haut):
                sans_classes(t, k, ["margin-bottom-global-gap-small", "margin-bottom-global-gap-extra-small"])
    if not rangs:
        return ["rangée des stats introuvable (le jeu a changé ?), ignoré"]
    return ["Small : graphique sur toute la hauteur libre, buts | passes D | note à la largeur de la tuile, alignés",
            "Large : tuile de FM"]


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre(modeles):
    change = False
    for modele in modeles:
        o = ouvrir(modele)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marques(t):
            print(f"{modele} : pas de sauvegarde d'origine, rien retiré")
            continue
        enregistrer(bundle, obj, tt, t)
        change = True
        print(f"{modele} : remis d'origine")
    return change


def cmd_appliquer():
    change = False
    for modele, fn in [(T2X2, tuile_2x2), (T4X2, tuile_4x2)]:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        if a_jour(o[3]):
            print(f"{modele} : déjà appliqué")
            continue
        old = bool(marques(o[3]))
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marques(t):
            print(f"{modele} : ancienne version présente et pas d'original, retirer d'abord")
            continue
        msgs = fn(t)
        for m in msgs + (["ancienne version remplacée"] if old else []):
            print(f"{modele} : {m}")
        if not any("ignoré" in m for m in msgs):
            enregistrer(bundle, obj, tt, t)
            change = True
    if change:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    if remettre(MODELES):
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele in MODELES:
        o = ouvrir(modele)
        print(f"{modele} : " + ("introuvable" if o is None else "appliqué" if marques(o[3]) else "d'origine"))
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
            print("tuile forme (5 derniers matchs) : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
