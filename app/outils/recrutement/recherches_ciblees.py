"""Recrutement > Recherches ciblées : tableau des joueurs trouvés avec la tête du joueur (après le nom / la nation) et
vues 100 % personnalisables (menu « Insérer colonne » rempli).

- Vues de FM RecruitmentFocusPlayerPoolTable* (collection RecruitmentFocusPlayerPoolTableViewCollection, ui-tableviews) :
  colonne « name » remplacée par la colonne FM « portrait-name » (PlayerTableFactory, tête + nom) (v2 ; v1 : colonne
  « portrait » à part, titre « Nom » en double).
- La collection a déjà ses vues personnalisées (nom / préfixe FM) mais son menu « Insérer colonne » est vide : il est
  recopié de la Base de données des joueurs (PlayerSearchResultsViewCollection, telle qu'elle est dans le jeu, avec la
  Personnalité si colonne_personnalite est active), SANS les entrées à condition (Requirement : Efficacité tactique,
  Hidden) qui faisaient planter FM avec les vues perso des rapports (kinito_rapports_vues v6, 2026-11-01).
  Même tableau des deux côtés (fabrique PlayerTableFactory) : toutes les colonnes du menu existent ici.
Bundle ui-tableviews (partagé, bundle actuel) : seulement ces objets, refaits depuis leur original.
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

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
LARGEUR_TETE = 30       # px ajoutés à la colonne du nom pour la tête
# =====================================================================================================

VERSION = 2
TITRE_NOM = 0           # titre de la colonne : celui de la vue, sinon celui de FM pour portrait-name (« Nom »)
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
COLLECTION = "RecruitmentFocusPlayerPoolTableViewCollection"
PREFIXE_VUES = "RecruitmentFocusPlayerPoolTable"     # ses vues (pas les Compact du carrousel, ni celles du TransferRoom)
SOURCE = "PlayerSearchResultsViewCollection"
TETE = "portrait-name"   # v2 : colonne FM tête + nom, à la place de « name »
REPERE = f"UIPicker-recherches-v{VERSION}"           # debug_name de la 1re rubrique du menu
MARKER = os.path.join(backup.BACKUP_DIR, "recherches_ciblees.actif")
DRY_RUN = "--dry-run" in sys.argv


def _monos(env):
    out = {}
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                out[o.path_id] = (o, o.peek_name())
            except Exception:
                continue
    return out


def _par_nom(monos, nom):
    return next((o for o, n in monos.values() if n == nom), None)


def _origine():
    src = backup.backup_path(VUES)
    return {pid: o for pid, (o, _) in _monos(UnityPy.load(src if os.path.exists(src) else VUES)).items()}


def avec_condition(e):
    req = (e or {}).get("Requirement")
    return isinstance(req, dict) and bool(req.get("m_PathID") or req.get("m_FileID"))


def menu(tt, src):
    """menu « Insérer colonne » de src recopié dans tt (sans les entrées à condition) ; message ou erreur"""
    rubriques = src.get("m_contextMenuData") or []
    if not rubriques:
        return None, "menu de la Base de données introuvable"
    refs_src = {r["rid"]: r for r in src["references"]["RefIds"]}
    sans, pile = set(), [rid for rid, r in refs_src.items() if avec_condition(r.get("data"))]
    while pile:   # une entrée à condition part avec ses sous-entrées
        rid = pile.pop()
        if rid in sans or rid not in refs_src:
            continue
        sans.add(rid)
        pile += [c["rid"] for c in (refs_src[rid].get("data") or {}).get("ChildList") or []]
    a_copier, pile = [], [c["rid"] for e in rubriques if not avec_condition(e) for c in e.get("ChildList") or []]
    while pile:
        rid = pile.pop()
        if rid in a_copier or rid in sans or rid not in refs_src:
            continue
        a_copier.append(rid)
        pile += [c["rid"] for c in (refs_src[rid].get("data") or {}).get("ChildList") or []]
    refs = tt.setdefault("references", {"version": 2, "RefIds": []})
    base = max([r["rid"] for r in refs["RefIds"]] + [0]) + 1
    nouveaux = {old: base + i for i, old in enumerate(sorted(a_copier))}

    def epurer(x):
        if isinstance(x, dict):
            if set(x) == {"rid"}:
                return {"rid": nouveaux[x["rid"]]}
            out = {}
            for k, v in x.items():
                if k == "ChildList":
                    v = [c for c in v if c["rid"] in nouveaux]
                out[k] = epurer(v)
            return out
        if isinstance(x, list):
            return [epurer(v) for v in x]
        return x

    for old in sorted(a_copier):
        r = copy.deepcopy(refs_src[old])
        r["data"] = epurer(r.get("data") or {})
        r["rid"] = nouveaux[old]
        refs["RefIds"].append(r)
    tt["m_contextMenuData"] = [epurer(e) for e in rubriques if not avec_condition(e)]
    tt["m_contextMenuData"][0]["debug_name"] = REPERE
    return (f"menu « Insérer colonne » ({len(tt['m_contextMenuData'])} rubriques, {len(a_copier)} entrées, "
            f"{len(sans)} à condition laissées de côté)"), None


def tete(vt):
    """v2 (le joueur : « juste l'ajouter dans le bloc de nom de base ») : la colonne « name » devient la colonne FM
    « portrait-name » (tête + nom dans la même cellule), même titre, LARGEUR_TETE de plus ; True si changée"""
    cfg = vt["m_tableView"]["m_tableConfig"]
    ids = [c["m_columnID"] for c in cfg]
    if TETE in ids or "name" not in ids:
        return False
    m = cfg[ids.index("name")]
    m["m_columnID"] = TETE
    md = m["m_columnMetadata"]
    if not md["m_titleTranslationIdOverride"].get("GameID"):
        md["m_titleTranslationIdOverride"] = {"GameID": TITRE_NOM}
    for k in ("m_widthOverride", "m_minWidthOverride"):
        if md.get(k):
            md[k] = float(md[k]) + LARGEUR_TETE
    return True


def _ecrire(env, msgs):
    data = env.file.save(packer="original")
    if DRY_RUN:
        msgs.append(f"(essai à blanc : rien écrit, {os.path.basename(VUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(VUES, data)


def faire(retirer):
    env = UnityPy.load(VUES)
    monos = _monos(env)
    origine = _origine()
    col = _par_nom(monos, COLLECTION)
    if col is None or col.path_id not in origine:
        return [f"{COLLECTION} introuvable (renommée par une mise à jour ?), rien fait"]
    voulu = {}   # path_id -> typetree voulu
    msgs = []
    tt = origine[col.path_id].read_typetree()
    if not retirer:
        src = _par_nom(monos, SOURCE)
        if src is None:
            return [f"{SOURCE} introuvable, rien fait"]
        m, err = menu(tt, src.read_typetree())
        if err:
            return [f"{COLLECTION} : {err}, rien fait"]
        msgs.append(f"{COLLECTION} : {m}")
    voulu[col.path_id] = tt
    for v in tt["m_tableViewSettings"]:
        pid = v["PropertyValue"]["m_PathID"]
        if pid not in monos or pid not in origine or not monos[pid][1].startswith(PREFIXE_VUES):
            continue
        vt = origine[pid].read_typetree()
        if not retirer and tete(vt):
            msgs.append(f"{monos[pid][1]} : tête du joueur ajoutée")
        voulu[pid] = vt
    change = False
    for pid, vt in voulu.items():
        o = monos[pid][0]
        if json.dumps(o.read_typetree(), sort_keys=True) != json.dumps(vt, sort_keys=True):
            o.save_typetree(vt)
            change = True
    if not change:
        return [f"recherches ciblées : déjà {'d’origine' if retirer else 'appliqué'}"]
    if retirer:
        msgs.append("recherches ciblées : vues et menu d'origine remis")
    _ecrire(env, msgs)
    return msgs


def cmd_etat():
    monos = _monos(UnityPy.load(VUES))
    col = _par_nom(monos, COLLECTION)
    if col is None:
        print(f"{COLLECTION} introuvable")
        return
    tt = col.read_typetree()
    rep = (tt.get("m_contextMenuData") or [{}])[0].get("debug_name", "")
    print(f"{COLLECTION} : menu « Insérer colonne »",
          f"{len(tt.get('m_contextMenuData') or [])} rubriques" + (f" ({rep})" if rep else ""))
    for v in tt["m_tableViewSettings"]:
        pid = v["PropertyValue"]["m_PathID"]
        if pid in monos and monos[pid][1].startswith(PREFIXE_VUES):
            ids = [c["m_columnID"] for c in monos[pid][0].read_typetree()["m_tableView"]["m_tableConfig"]]
            print(f"  {monos[pid][1]} : tête", "oui" if TETE in ids else "non")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def actif():
    return os.path.exists(MARKER)


def main(argv):
    global DRY_RUN
    if "--dry-run" in argv:
        DRY_RUN = nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op in ("appliquer", "si-actif"):
        if op == "si-actif" and not actif():
            print("recherches ciblées : non activé, rien à faire")
            return
        for m in faire(False):
            print(m)
        if not DRY_RUN:
            with open(MARKER, "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)
    elif op == "retirer":
        if os.path.exists(MARKER) and not DRY_RUN:
            os.remove(MARKER)
        for m in faire(True):
            print(m)
    elif op == "etat":
        cmd_etat()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
