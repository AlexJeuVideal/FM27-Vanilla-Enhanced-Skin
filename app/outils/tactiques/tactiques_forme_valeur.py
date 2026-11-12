"""Tactiques : colonne « Forme avec valeur » (barres des 5 derniers matchs + note) dans Insérer colonne.

FM a cette colonne pour l'effectif (PlayerTableFactory, « form-with-value », menu Stats (Général)), mais les tableaux
des tactiques lisent TacticTeamSelectionTableFactory, qui ne l'a pas (seulement « form » : barres sans la note).
Une colonne absente de la fabrique du tableau est ignorée sans erreur : elle est donc recopiée dans cette fabrique
(chemins binding.X -> binding.Player.X, comme la colonne « form » des tactiques ; types des paramètres repris de
cette colonne), puis proposée dans les menus Insérer colonne des tactiques (Stats (Général) > Général, après
« Expected Goals per 90 »). Pas dans les tactiques en match (autre fabrique, 27 colonnes).

Bundles :
- ui-tablefactories : moral_icone_seule (propriétaire, repart de l'original) rappelle fabrique_appliquer() quand ce
  script est actif ; sinon ce script écrit le bundle actuel.
- ui-tableviews : entrées de menu ajoutées sur le bundle actuel (repère debug_name), retirées par nom.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\tactiques\\tactiques_forme_valeur.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\tactiques\\tactiques_forme_valeur.py retirer
  .venv\\Scripts\\python.exe outils\\tactiques\\tactiques_forme_valeur.py etat
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
COLONNE = "form-with-value"       # id FM (PlayerTableFactory)
LIBELLE = 45445                   # traduction FM « Form with Value » (menu de l'effectif)
SOUS_MENU = "general"             # Stats (Général) > Général (menu des tactiques)
APRES = "expected-goals-per90"    # entrée placée juste après
MENUS = ["TacticTeamSelectionTableViewCollectionOverview", "TacticTeamSelectionTableViewCollectionOverviewCollapsed",
         "TacticTeamSelectionTableViewCollectionPossession", "TacticTeamSelectionTableViewCollectionPossessionCollapsed",
         "TacticTeamSelectionTableViewCollectionBoth"]
# =====================================================================================================

VUES_BUNDLE = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
SOURCE = "PlayerTableFactory"
FABRIQUE = "TacticTeamSelectionTableFactory"
MODELE_COLONNE = "form"           # colonne « form » des tactiques : chemins et types des paramètres
REPERE = "UIPickerFormeValeur"    # debug_name de nos entrées de menu
MARKER = os.path.join(backup.BACKUP_DIR, "tactiques_forme_valeur.actif")
DRY_RUN = "--dry-run" in sys.argv


def monos(env, noms):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if tt.get("m_Name") in noms:
            yield o, tt


def _chemins(x):
    """binding -> binding.Player, binding.X -> binding.Player.X (partout dans la colonne)"""
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "m_path" and isinstance(v, str):
                if v.lower() == "binding":
                    x[k] = "binding.Player"
                elif v.lower().startswith("binding.") and not v.lower().startswith("binding.player."):
                    x[k] = "binding.Player." + v[len("binding."):]
            else:
                _chemins(v)
    elif isinstance(x, list):
        for v in x:
            _chemins(v)


def fabrique_appliquer(env):
    """recopie la colonne de SOURCE dans FABRIQUE (env déjà chargé) ; True si changé"""
    src = next((r for _, tt in monos(env, {SOURCE}) for r in tt["m_rowData"] if r["m_id"] == COLONNE), None)
    if src is None:
        print(f"{SOURCE} : colonne {COLONNE} introuvable (le jeu a changé ?), fabrique pas touchée")
        return False
    change = False
    for o, tt in monos(env, {FABRIQUE}):
        rows = tt["m_rowData"]
        modele = next((r for r in rows if r["m_id"] == MODELE_COLONNE), None)
        if modele is None:
            print(f"{FABRIQUE} : colonne {MODELE_COLONNE} introuvable, fabrique pas touchée")
            return False
        types = {b["from"]: b["type"] for b in modele["m_valueBindings"]}
        r = copy.deepcopy(src)
        _chemins(r)
        for b in r["m_valueBindings"] + r.get("m_footerValueBindings", []):
            if b["from"] in types:
                b["type"] = copy.deepcopy(types[b["from"]])
        vieux = next((x for x in rows if x["m_id"] == COLONNE), None)
        if vieux is not None and json.dumps(vieux) == json.dumps(r):
            continue
        if vieux is not None:
            rows.remove(vieux)
        rows.append(r)
        o.save_typetree(tt)
        change = True
        print(f"{FABRIQUE} : colonne {COLONNE} recopiée (binding -> binding.Player)")
    return change


def fabrique_retirer(env):
    change = False
    for o, tt in monos(env, {FABRIQUE}):
        avant = len(tt["m_rowData"])
        tt["m_rowData"] = [r for r in tt["m_rowData"] if r["m_id"] != COLONNE]
        if len(tt["m_rowData"]) != avant:
            o.save_typetree(tt)
            change = True
    return change


def _ecrire(env, bundle):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(bundle)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(bundle, data)


# ---------- menus Insérer colonne ----------
def _refs(tt):
    return {r["rid"]: r for r in tt["references"]["RefIds"] if isinstance(r.get("data"), dict)}


def _sous_menu(tt):
    """ChildList de Stats (Général) > Général"""
    refs = _refs(tt)
    stats = next((d for d in tt["m_contextMenuData"] if d.get("PropertyValue") == "statsgeneral"), None)
    for c in (stats or {}).get("ChildList", []):
        d = refs.get(c["rid"], {}).get("data") or {}
        if d.get("PropertyValue") == SOUS_MENU:
            return d["ChildList"]
    return None


def menu_ajouter(tt):
    refs = _refs(tt)
    liste = _sous_menu(tt)
    if liste is None:
        return "sous-menu Stats (Général) > Général introuvable"
    if any(refs[c["rid"]]["data"].get("debug_name") == REPERE for c in liste if c["rid"] in refs):
        return None
    ids = [refs[c["rid"]]["data"].get("PropertyValue") for c in liste]
    if APRES not in ids:
        return f"entrée {APRES} introuvable"
    i = ids.index(APRES)
    neuf = copy.deepcopy(refs[liste[i]["rid"]])
    neuf["rid"] = max(refs) + 1
    neuf["data"].update(debug_name=REPERE, name="Form with Value", PropertyValue=COLONNE,
                        DisplayValue={"GameID": LIBELLE}, AddSpacerBefore=0)
    tt["references"]["RefIds"].append(neuf)
    liste.insert(i + 1, {"rid": neuf["rid"]})
    return "ajouté"


def menu_retirer(tt):
    refs = _refs(tt)
    nos = {rid for rid, r in refs.items() if r["data"].get("debug_name") == REPERE}
    if not nos:
        return False
    for d in tt["m_contextMenuData"] + [r["data"] for r in refs.values()]:
        if d.get("ChildList"):
            d["ChildList"] = [c for c in d["ChildList"] if c.get("rid") not in nos]
    tt["references"]["RefIds"] = [r for r in tt["references"]["RefIds"] if r.get("rid") not in nos]
    return True


# ---------- commandes ----------
def cmd_appliquer():
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env):
        _ecrire(env, FABRIQUES)
    elif not any(r["m_id"] == COLONNE for _, tt in monos(env, {FABRIQUE}) for r in tt["m_rowData"]):
        print("rien fait")
        return
    else:
        print(f"{FABRIQUE} : colonne déjà là")
    env = UnityPy.load(VUES_BUNDLE)
    change, vus = False, set()
    for o, tt in monos(env, set(MENUS)):
        vus.add(tt["m_Name"])
        r = menu_ajouter(tt)
        if r == "ajouté":
            o.save_typetree(tt)
            change = True
            print(f"{tt['m_Name']} : « Form with Value » ajoutée (Stats (Général) > Général)")
        elif r is None:
            print(f"{tt['m_Name']} : déjà appliqué")
        else:
            print(f"{tt['m_Name']} : {r}, ignoré")
    for m in set(MENUS) - vus:
        print(f"{m} : menu introuvable (le jeu a changé ?)")
    if change:
        _ecrire(env, VUES_BUNDLE)
    if not DRY_RUN and vus:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    env = UnityPy.load(VUES_BUNDLE)
    change = False
    for o, tt in monos(env, set(MENUS)):
        if menu_retirer(tt):
            o.save_typetree(tt)
            change = True
            print(f"{tt['m_Name']} : entrée retirée")
    if change:
        _ecrire(env, VUES_BUNDLE)
    env = UnityPy.load(FABRIQUES)
    if fabrique_retirer(env):
        _ecrire(env, FABRIQUES)
        print(f"{FABRIQUE} : colonne {COLONNE} retirée")
    if not change:
        print("menus : rien à retirer")


def cmd_etat():
    for _, tt in monos(UnityPy.load(VUES_BUNDLE), set(MENUS)):
        refs = _refs(tt)
        print(f"{tt['m_Name']} :", "proposée" if any(r["data"].get("debug_name") == REPERE for r in refs.values())
              else "pas proposée")
    for _, tt in monos(UnityPy.load(FABRIQUES), {FABRIQUE}):
        print(f"{FABRIQUE} :", "colonne présente" if any(r["m_id"] == COLONNE for r in tt["m_rowData"]) else "pas de colonne")
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
            print("tactiques, forme avec valeur : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
