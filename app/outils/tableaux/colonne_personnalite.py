"""Colonne « Personnalité » dans le menu Insérer colonne > Infos générales des tableaux de joueurs.

La colonne existe déjà dans le jeu (PlayerTableFactory, id « personality », utilisée par l'écran Effectif),
mais le menu de la Base de données des joueurs (et d'autres listes) ne la propose pas. Ce script ajoute
l'entrée au sous-menu Infos générales de chaque menu de colonnes de joueurs qui ne l'a pas encore.

Seul script à toucher le bundle ui-tableviews : retirer remet son original.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\tableaux\\colonne_personnalite.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\tableaux\\colonne_personnalite.py retirer
  .venv\\Scripts\\python.exe outils\\tableaux\\colonne_personnalite.py etat
"""
import copy
import json
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (correctif UnityPy, chemins du jeu)
import sauvegarde_originaux as backup  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
APRES = "media-handling"   # l'entrée est placée juste après « Rapports avec les médias »
# =====================================================================================================

BUNDLE = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
COLONNE = "personality"            # id de la colonne dans PlayerTableFactory
LIBELLE = 34579                    # texte traduit « Personnalité » (celui du menu de l'écran Effectif)
REPERE = "UIPicker"                # debug_name de notre entrée
MARKER = os.path.join(backup.BACKUP_DIR, "colonne_personnalite.actif")
DRY_RUN = "--dry-run" in sys.argv


def menus(env):
    """[(objet, typetree)] des collections de vues qui ont un menu de colonnes"""
    out = []
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if tt.get("m_contextMenuData") and "references" in tt:
            out.append((o, tt))
    return out


def entrees(tt):
    """{rid: données} des entrées du menu"""
    return {r["rid"]: r for r in tt["references"]["RefIds"] if isinstance(r.get("data"), dict)}


def a_colonne(tt, valeur):
    return any(r["data"].get("PropertyValue") == valeur for r in entrees(tt).values())


def parent_de(tt, rid):
    """liste ChildList qui contient rid (racine ou sous-menu)"""
    for d in tt["m_contextMenuData"] + [r["data"] for r in entrees(tt).values()]:
        for i, c in enumerate(d.get("ChildList", [])):
            if c.get("rid") == rid:
                return d["ChildList"], i
    return None, None


def ajouter(tt):
    refs = entrees(tt)
    modele = next((r for r in refs.values() if r["data"].get("PropertyValue") == APRES), None)
    if modele is None:
        return False
    liste, i = parent_de(tt, modele["rid"])
    if liste is None:
        return False
    rid = max(refs) + 1
    neuf = copy.deepcopy(modele)
    neuf["rid"] = rid
    neuf["data"].update(debug_name=REPERE, name="Personality", PropertyValue=COLONNE,
                        DisplayValue={"GameID": LIBELLE}, AddSpacerBefore=0)
    tt["references"]["RefIds"].append(neuf)
    liste.insert(i + 1, {"rid": rid})
    return True


def cmd_appliquer():
    env = UnityPy.load(BUNDLE)
    change = 0
    for o, tt in menus(env):
        nom = tt["m_Name"]
        if not a_colonne(tt, APRES):
            continue   # pas un menu de joueurs avec Infos générales
        if a_colonne(tt, COLONNE):
            deja = any(r["data"].get("debug_name") == REPERE for r in entrees(tt).values())
            print(f"{nom} : {'déjà appliqué' if deja else 'Personnalité déjà proposée par FM'}")
            continue
        if ajouter(tt):
            o.save_typetree(tt)
            change += 1
            print(f"{nom} : Personnalité ajoutée après « {APRES} »")
        else:
            print(f"{nom} : emplacement introuvable, ignoré")
    if not change:
        print("rien à changer")
        return
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(BUNDLE)} ferait {len(data) / 1e6:.2f} Mo)")
        return
    backup.write_bundle(BUNDLE, data)
    with open(MARKER, "w", encoding="utf-8") as f:
        json.dump({"actif": True}, f)
    print(f"\n{change} menu(s) de colonnes : Personnalité ajoutée dans Infos générales.")


def cmd_retirer():
    if not os.path.exists(backup.backup_path(BUNDLE)):
        sys.exit("ui-tableviews n'a jamais été modifié : rien à retirer")
    backup.restore(BUNDLE)
    if os.path.exists(MARKER):
        os.remove(MARKER)
    print("Menus de colonnes d'origine remis.")


def cmd_etat():
    env = UnityPy.load(BUNDLE)
    for _, tt in menus(env):
        if not a_colonne(tt, APRES):
            continue
        refs = entrees(tt).values()
        if any(r["data"].get("debug_name") == REPERE for r in refs):
            etat = "Personnalité ajoutée"
        elif a_colonne(tt, COLONNE):
            etat = "Personnalité proposée par FM"
        else:
            etat = "pas de Personnalité"
        print(f"{tt['m_Name']} : {etat}")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
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
            print("colonne Personnalité : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
