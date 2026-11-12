"""Haut du jeu (encadré date + prochaine rencontre, à gauche de « Continuer ») : lettre Domicile / Extérieur
après l'adversaire (« Spezia (D) » / « Spezia (E) » ; en anglais « (H) » / « (A) » ; v1 : devant, réglage APRES).

Modèle touché (ce script est son seul propriétaire, appliquer repart toujours de l'original sauvegardé) :
- CurrentDayWidget : #HasFixture (texte FM « adversaire » + « dans X jours ») ; on ajoute devant deux SIVisible
  (comparaison FM a7578b80, « = ») : équipe à domicile de la prochaine rencontre = équipe du joueur -> D, équipe
  à l'extérieur = équipe du joueur -> E.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\haut_du_jeu\\prochain_match_domicile.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\haut_du_jeu\\prochain_match_domicile.py retirer
  .venv\\Scripts\\python.exe outils\\haut_du_jeu\\prochain_match_domicile.py etat
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import ouvrir  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
from notes_installations import (first, visible_model, make_binding, new_visible, text_static,  # noqa: E402
                                 SOURCE_COMPARE, FN_COMPARE)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
DOMICILE = L("(D)", "(H)")
EXTERIEUR = L("(E)", "(A)")
APRES = True   # v2 : lettre APRÈS l'adversaire (« Spezia (E) », demande du joueur) ; False = devant (v1)
# =====================================================================================================

VERSION = f"2{SUFFIXE}"
MODELE = "CurrentDayWidget"
EQUIPE = "teamrequestingreport"   # équipe du joueur (BindingRemapper FM : human.team)
MATCH = f"{EQUIPE}.NextFixture"
PREFIXE = "UIPickerDomicile"
NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "prochain_match_domicile.actif")
OP_EGAL = 2


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def construire(t):
    zone = first(t, lambda r: t.name(r) == "HasFixture")
    adversaire = zone and first(t, lambda r: t.name(r) == "text", zone)
    s, vis = visible_model(SOURCE_COMPARE, FN_COMPARE)
    if adversaire is None or vis is None:
        return ["prochaine rencontre (#HasFixture) ou comparaison FM introuvable"]
    parent = t.parent[adversaire] if APRES else zone
    for k, (cote, lettre) in enumerate((("HomeTeam", DOMICILE), ("AwayTeam", EXTERIEUR))):
        b = make_binding(s.sd(vis)["Binding"], OP_EGAL, [f"{MATCH}.{cote}.UniqueId", f"{EQUIPE}.UniqueId"])
        index = t.children(parent).index(adversaire) + 1 + k if APRES else k
        v = new_visible(t, s, vis, parent, index, NOM if k == 0 else f"{PREFIXE}-exterieur", b,
                        ["row-direction-normal", "align-items-center"])
        t.sd(v)["name_UxmlAttributeFlags"] = 1
        txt = text_static(t, adversaire, v, lettre)
        t.sd(txt)["name"], t.sd(txt)["name_UxmlAttributeFlags"] = "", 0
        t.elem(txt)["m_Classes"] = ["content-no-wrap", "body-sm", "global-text-primary", "sitext-hover-cursor",
                                    "margin-right-global-gap-small"]   # après : le nom FM a déjà sa marge à droite
        t.elem(txt)["m_RuleIndex"] = -1
    return [f"« {DOMICILE} » / « {EXTERIEUR} » " + ("après" if APRES else "devant")
            + " l'adversaire de la prochaine rencontre"]


def cmd_appliquer():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    if any(o[3].name(r) == NOM for r in marques(o[3])):
        print("domicile / extérieur : déjà appliqué")
    else:
        bundle, obj, tt, t = ouvrir(MODELE, depart_original=True)
        if marques(t):
            print("domicile / extérieur : pas de sauvegarde d'origine propre, ignoré")
            return
        msgs = construire(t) + (["ancienne version remplacée"] if marques(o[3]) else [])
        for m in msgs:
            print(f"domicile / extérieur : {m}")
        if any("introuvable" in m for m in msgs):
            print("domicile / extérieur : rien enregistré")
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
        m = marques(o[3])
        etat = "à jour" if any(o[3].name(r) == NOM for r in m) else "ANCIENNE version"
        print(f"{MODELE} : " + (f"appliqué ({etat}, v{VERSION})" if m else "d'origine"))
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
            print("domicile / extérieur : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
