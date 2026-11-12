"""ESSAI : débloquer les affichages Medium / Small en dessous de la 2K (1080p).

Préférences de FM > affichage (modèle AdaptiveLayoutPreferences) : les boutons Medium et Small sont chacun dans un
SIEnabled lié à `settings.MediumScalingAvailable` / `settings.SmallScalingAvailable` (faux sous la 2K = grisés).
Le clic sur le bouton écrit directement `settings.AdaptiveScalingLevelIndex` (1 Medium, 2 Small).
v1 (2026-11-10) : liaisons -> const.True. Inconnue : le code de FM (UpdateScreenScaling) remet-il Large quand même ?

Outils FM.bat : 124 (essais pas validés) ; retrait : 105 (catalogue.ESSAIS).
Usage : essai_echelle_1080p.py appliquer [--dry-run] | retirer [--dry-run]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
from arbre import Tree  # noqa: E402

MODELE = "AdaptiveLayoutPreferences"
CLASSE = "uipicker-echelle-v1"
CIBLES = {"MediumEnabled": "settings.MediumScalingAvailable", "SmallEnabled": "settings.SmallScalingAvailable"}
TOUJOURS = "const.True"


def _elements(t):
    return {t.name(r): r for r in t.walk() if t.name(r) in CIBLES}


def appliquer(t):
    els = _elements(t)
    if len(els) != len(CIBLES):
        return [f"{MODELE} : boutons Medium / Small introuvables, ignoré"]
    msgs = []
    for nom, r in els.items():
        b = t.sd(r)["Binding"]
        chemin = b["m_direct"]["Path"]["m_path"]
        if chemin not in (CIBLES[nom], TOUJOURS):
            return [f"{MODELE} : liaison inattendue sur {nom} ({chemin}), ignoré"]
        classes = t.elem(r).get("m_Classes") or []
        if chemin == TOUJOURS and CLASSE in classes:
            continue
        b["m_direct"]["Path"]["m_path"] = TOUJOURS
        t.elem(r)["m_Classes"] = [c for c in classes if not c.startswith("uipicker-echelle-")] + [CLASSE]
        msgs.append(f"{nom} : {chemin} -> {TOUJOURS}")
    return msgs


def retirer(t):
    msgs = []
    for nom, r in _elements(t).items():
        b = t.sd(r)["Binding"]
        classes = t.elem(r).get("m_Classes") or []
        if b["m_direct"]["Path"]["m_path"] == CIBLES[nom] and not any(c.startswith("uipicker-echelle-") for c in classes):
            continue
        b["m_direct"]["Path"]["m_path"] = CIBLES[nom]
        t.elem(r)["m_Classes"] = [c for c in classes if not c.startswith("uipicker-echelle-")]
        msgs.append(f"{nom} : remis sur {CIBLES[nom]}")
    return msgs


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        sys.exit(f"{MODELE} introuvable")
    t = Tree(tt)
    msgs = fn(t)
    print("\n".join(msgs) or "rien à faire (déjà fait)")
    if msgs and "ignoré" not in msgs[0]:
        t.finish()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        nb.save_all()


if __name__ == "__main__":
    main(sys.argv[1:])
