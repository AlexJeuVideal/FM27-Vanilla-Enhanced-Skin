"""Fiche joueur, bloc « Suspensions » (colonne Infos) : nom court des compétitions (« C/B », « CSC », comme dans
Stats saison) au lieu du nom long (« Série C/B », « Coupe de Série C ») — demande du joueur, 2026-11-12.

Colonne « comp » de la fabrique PlayerBansOverviewTableFactory (seul tableau du bloc PlayerReportBansBlock) :
cellule FM CompCell (comp.Name) -> CompCellShort (comp.shortname, la cellule de la colonne « compshort » de Stats
saison, même paramètre comp), largeur de cette colonne-là (COLONNE_COURTE).

Bundle ui-tablefactories : moral_icone_seule (propriétaire, repart de l'original) rappelle fabrique_appliquer() quand ce
script est actif ; sinon ce script écrit le bundle actuel. Retirer remet la colonne d'origine (sauvegarde).
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
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

FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
FABRIQUE = "PlayerBansOverviewTableFactory"
COLONNE = "comp"
CELLULE_LONGUE = "445e4545c7243524faffc35466380f60"    # CompCell (comp.Name)
CELLULE_COURTE = "cbaf589f9a17d494982cd60352fbe11a"    # CompCellShort (comp.shortname)
COLONNE_COURTE = 65.0   # px, largeur et minimum de la colonne « compshort » de Stats saison (FM : 153 / 85 ici)
MARKER = os.path.join(backup.BACKUP_DIR, "suspensions_noms_courts.actif")
DRY_RUN = "--dry-run" in sys.argv


def colonne(env):
    """(objet, typetree, index) de la colonne comp de la fabrique des suspensions, ou None"""
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != FABRIQUE:
                continue
            tt = o.read_typetree()
        except Exception:
            continue
        for i, r in enumerate(tt.get("m_rowData") or []):
            if r.get("m_id") == COLONNE:
                return o, tt, i
    return None


def origine():
    """colonne comp d'origine (sauvegarde, sinon bundle actuel)"""
    orig = backup.backup_path(FABRIQUES)
    c = colonne(UnityPy.load(orig if os.path.exists(orig) else FABRIQUES))
    return c and copy.deepcopy(c[1]["m_rowData"][c[2]])


def courte(d):
    r = copy.deepcopy(d)
    r["m_uxmlRef"]["m_AssetGUID"] = CELLULE_COURTE
    r["m_defaultWidth"] = r["m_minimumWidth"] = COLONNE_COURTE
    return r


def fabrique_appliquer(env):
    """colonne comp de env (déjà chargé) en nom court ; True si changé"""
    d, c = origine(), colonne(env)
    if d is None or c is None:
        print(f"{FABRIQUE} : colonne {COLONNE} introuvable (le jeu a changé ?), ignoré")
        return False
    if (d.get("m_uxmlRef") or {}).get("m_AssetGUID") != CELLULE_LONGUE:
        print(f"{FABRIQUE} : cellule de FM inattendue, ignoré")
        return False
    o, tt, i = c
    neuf = courte(d)
    if json.dumps(neuf) == json.dumps(tt["m_rowData"][i]):
        return False
    tt["m_rowData"][i] = neuf
    o.save_typetree(tt)
    print(f"{FABRIQUE} : suspensions en nom court des compétitions")
    return True


def _ecrire(env):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(FABRIQUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(FABRIQUES, data)


def cmd_appliquer():
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env):
        _ecrire(env)
    else:
        print("suspensions : déjà en nom court")
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    d = origine()
    env = UnityPy.load(FABRIQUES)
    c = colonne(env)
    if d is not None and c is not None and json.dumps(d) != json.dumps(c[1]["m_rowData"][c[2]]):
        o, tt, i = c
        tt["m_rowData"][i] = d
        o.save_typetree(tt)
        _ecrire(env)
        print(f"{FABRIQUE} : colonne d'origine remise")
    else:
        print("suspensions : déjà d'origine")


def cmd_etat():
    c = colonne(UnityPy.load(FABRIQUES))
    g = c and (c[1]["m_rowData"][c[2]].get("m_uxmlRef") or {}).get("m_AssetGUID")
    print("suspensions :", {CELLULE_COURTE: "nom court", CELLULE_LONGUE: "nom long (FM)"}.get(g, "introuvable"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def actif():
    return os.path.exists(MARKER)


def main(argv):
    global DRY_RUN
    if "--dry-run" in argv:
        DRY_RUN = nb.DRY_RUN = True
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
            print("suspensions en nom court : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
