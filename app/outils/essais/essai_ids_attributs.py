"""ESSAI : numéro interne de chaque attribut (pour des boutons « tout cocher / tout décocher » sur la progression).

Les interrupteurs de la colonne « Sel. » (cellule AttributeSelectorTableItemSmall, commune aux tableaux Technique,
Coups de pied arrêtés, Mental, Physique et à ceux des gardiens) envoient EventFmxEnableTrainingAttribute /
EventFmxDisableTrainingAttribute avec `player.PlayerTraining` et `attribute.AttributeTypeInfo.ID`. Ce numéro n'est
pas lisible dans les fichiers : l'essai l'écrit par-dessus l'interrupteur (pavé noir, chiffres jaunes).

Menu Outils FM.bat (jeu fermé) : 63 appliquer, 64 retirer.
Usage : essai_ids_attributs.py appliquer [--dry-run] | retirer [--dry-run]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles  # noqa: E402

MODELES = ["AttributeSelectorTableItem", "AttributeSelectorTableItemSmall"]
# v1 posé seulement sur la Small : rien en jeu. Console (ls SetPiecesTable 9) : 4 colonnes 76 / 34 / 411 / 66 (pas
# la vue 48 / 90 / 48 de ui-tableviews) -> c'est la cellule normale (même fabrique) qui sert. v2 : les deux
SOURCE = ("PlayerAttributesAndCoachReportIndividualTrainingContent", "NoProgressionText")   # SIText à recopier
NOM = "UIPickerEssaiId"
CHEMIN = "attribute.AttributeTypeInfo.ID"
for k, v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "width": (131105, 3),
             "height": (131087, 3), "color": (65536, 4), "font-size": (65537, 3),
             "-unity-text-align": (65546, 7)}.items():
    sm.PROPRIETES.setdefault(k, v)


def appliquer(t, sh):
    retirer(t)
    racine = next(r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("ComponentElement"))
    _, _, tt_src = nb.find_vta(SOURCE[0])
    src = Tree(tt_src)
    texte = next((r for r in src.walk() if src.name(r) == SOURCE[1]), None)
    if texte is None:
        return [f"{SOURCE[0]} #{SOURCE[1]} introuvable"]
    r = t.clone(texte, racine, None, src=src)
    sd = t.sd(r)
    sd.update(name=NOM, name_UxmlAttributeFlags=1, text="", pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = CHEMIN
    t.elem(r)["m_Classes"] = []
    t.elem(r)["m_RuleIndex"] = -1
    sh.style(t, r, {"position": "absolute", "left": 0, "top": 0, "width": 56, "height": 24,
                    "background-color": (0, 0, 0, 1), "color": (1, 0.85, 0.1, 1), "font-size": 14,
                    "-unity-text-align": "middle-center"})
    return [f"numéro ({CHEMIN}) affiché sur chaque interrupteur des tableaux d'attributs"]


def retirer(t, sh=None):
    old = [r for r in t.walk() if t.name(r) == NOM]
    for r in old:
        t.remove(r)
    return ["essai retiré"] if old else []


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    for modele in MODELES:
        bundle, obj, tt = nb.find_vta(modele)
        if tt is None:
            print(f"{modele} introuvable")
            continue
        t, sh = Tree(tt), Styles(bundle, tt)
        msgs = fn(t, sh)
        print(f"{modele} : " + (", ".join(msgs) or "rien à faire"))
        if msgs and "introuvable" not in msgs[0]:
            t.finish()
            sh.changed = True
            sh.save()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
    nb.save_all()


if __name__ == "__main__":
    main(sys.argv[1:])
