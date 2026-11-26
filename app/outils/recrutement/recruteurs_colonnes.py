"""Recrutement > Recherches ciblées > Recruteur / Analyste affecté : tableaux des recruteurs et des analystes
déverrouillés (largeur et ordre des colonnes, clic droit sur les en-têtes) et toutes les colonnes de FM.

Relevé dans le jeu (2026-11-26, rien de deviné) : la fenêtre « Recruteur affecté » / « Analyste affecté » =
RecruitmentFocusAssignScoutAnalystDialog (bundle gameworld preload), deux StreamedTable #scouts-table et
#analysts-table (fabrique RecruitmentFocusStaffTableFactory, 9 colonnes), chacun sur UNE vue fixe (InitFunction
446475dd, pas de collection : pas de menu des vues) : RecruitmentFocusScoutsTable / RecruitmentFocusAnalystsTable
(ui-tableviews). Tout y est coupé : AllowColumnResizing 0, AllowColumnReordering 0, ResizeColumnWidthsToFit 0, pas de
ContextMenuData.
- Tableaux : réglages de NationScreenOverviewBlock #StaffContractsTable de FM (tableau de staff à vue unique, le même
  cas) : AllowColumnResizing 1, ResizeColumnWidthsToFit 1, ContextMenuData bd30edff… (menu des en-têtes) ; plus
  AllowColumnReordering 1 (comme SquadRegistrationSelectionTableBlock, vue unique aussi). Défilement non touché.
- Vues : les 2 colonnes de la fabrique absentes de chaque vue ajoutées avant « Connaissance du monde » (recruteurs :
  Analyse de données, Connaissance tactique ; analystes : Év. P, Adaptabilité), réglages recopiés d'une colonne de FM.
Fichiers : le modèle (seul propriétaire : appliquer repart de l'original, retirer le remet) ; ui-tableviews (partagé) :
seulement ces deux vues, refaites depuis leur original.
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
import colonnes_reglables as cr  # noqa: E402

VERSION = 2   # v2 (2026-11-26, le joueur) : chaque colonne réductible jusqu'à 16 px (colonnes_reglables.MINIMUM)
MODELE = "RecruitmentFocusAssignScoutAnalystDialog"
TABLEAUX = ("scouts-table", "analysts-table")
FABRIQUE = "5e888faab463ba740956f9230aa5fe90"            # RecruitmentFocusStaffTableFactory
SOURCE_TABLEAU = ("NationScreenOverviewBlock", "StaffContractsTable")
REGLAGES = {"AllowColumnResizing": 1, "AllowColumnReordering": 1, "ResizeColumnWidthsToFit": 1}
MENU = "ContextMenuData"                                  # recopié du tableau source
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
AJOUTS = {   # vue -> colonnes ajoutées (avant AVANT)
    "RecruitmentFocusScoutsTable": ["analysingdata", "tacticalknowledge"],
    "RecruitmentFocusAnalystsTable": ["judgepotential", "adaptability"],
}
AVANT = "worldknowledge"
MARKER = os.path.join(backup.BACKUP_DIR, "recruteurs_colonnes.actif")


def tableaux(t):
    return [r for r in t.walk() if typ(t, r) == "StreamedTable" and t.sd(r).get("name") in TABLEAUX]


def menu_source():
    o = ouvrir(SOURCE_TABLEAU[0], depart_original=True)
    if o is None:
        return None
    t = o[3]
    r = next((r for r in t.walk() if typ(t, r) == "StreamedTable" and t.sd(r).get("name") == SOURCE_TABLEAU[1]), None)
    m = r is not None and t.sd(r).get(MENU)
    return copy.deepcopy(m) if m and m.get("m_AssetGUID") else None


def tableau_a_jour(t, r, menu):
    d = t.sd(r)
    return all(d.get(k) == v for k, v in REGLAGES.items()) and d.get(MENU) == menu


def mono(env, nom):
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                if o.peek_name() == nom:
                    return o
            except Exception:
                continue
    return None


def ids(tt):
    return [c["m_columnID"] for c in tt["m_tableView"]["m_tableConfig"]]


def vue_a_jour(tt, nom):
    cfg = tt["m_tableView"]["m_tableConfig"]
    return all(c in ids(tt) for c in AJOUTS[nom]) and cr.minimums_petits(copy.deepcopy(cfg)) == cfg


def construire_vue(tt, nom):
    """tt : la vue d'origine. Ajoute les colonnes manquantes avant AVANT (réglages d'une colonne de FM)."""
    cfg = tt["m_tableView"]["m_tableConfig"]
    if AVANT not in ids(tt) or not cfg:
        return f"{nom} : colonne {AVANT} introuvable"
    modele = next(c for c in cfg if c["m_columnID"] == "judgeability") if "judgeability" in ids(tt) else cfg[-1]
    for col in AJOUTS[nom]:
        if col in ids(tt):
            continue
        c = copy.deepcopy(modele)
        c["m_columnID"] = col
        c["m_columnMetadata"]["m_titleTranslationIdOverride"] = {"GameID": 0}
        cfg.insert(ids(tt).index(AVANT), c)
    cr.minimums_petits(cfg)   # v2 : colonnes réductibles jusqu'à 16 px
    return None


def cmd_appliquer():
    menu = menu_source()
    o = ouvrir(MODELE)
    env = nb.env_of(VUES)
    vues = {n: mono(env, n) for n in AJOUTS}
    if menu is None or o is None or None in vues.values():
        print("Recruteurs / analystes affectés : morceaux de FM introuvables (fenêtre, vues ou menu des en-têtes), "
              "rien enregistré")
        return
    if (len(tableaux(o[3])) == 2 and all(tableau_a_jour(o[3], r, menu) for r in tableaux(o[3]))
            and all(vue_a_jour(v.read_typetree(), n) for n, v in vues.items())):
        print("Recruteurs / analystes affectés : déjà appliqué")
    else:
        o = ouvrir(MODELE, depart_original=True)
        bundle, obj, tto, t = o
        rs = tableaux(t)
        if len(rs) != 2 or any((t.sd(r).get("FactoryAsset") or {}).get("m_AssetGUID") != FABRIQUE for r in rs):
            print(f"Recruteurs / analystes affectés : tableaux de {MODELE} introuvables ou d'une autre fabrique, "
                  "rien enregistré")
            return
        for r in rs:
            d = t.sd(r)
            for k, v in REGLAGES.items():
                d[k], d[k + "_UxmlAttributeFlags"] = v, 1
            d[MENU], d[MENU + "_UxmlAttributeFlags"] = copy.deepcopy(menu), 1
        nouvelles = {}
        for n, v in vues.items():
            tt = hp.original(VUES, v) or v.read_typetree()
            err = construire_vue(tt, n)
            if err:
                print(f"Recruteurs / analystes affectés : {err}, rien enregistré")
                return
            nouvelles[n] = tt
        t.finish()
        t.styles.save()
        obj.save_typetree(tto)
        nb._dirty.add(bundle)
        for n, tt in nouvelles.items():
            vues[n].save_typetree(tt)
        nb._dirty.add(VUES)
        nb.save_all()
        print(f"Recruteurs / analystes affectés : {MODELE} : colonnes redimensionnables et déplaçables, menu du clic "
              "droit sur les en-têtes")
        for n, tt in nouvelles.items():
            print(f"Recruteurs / analystes affectés : {n} : colonnes {', '.join(ids(tt))}")
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    o = ouvrir(MODELE)
    if o is not None:
        bundle, obj, tt, t = o
        if any(t.sd(r).get("AllowColumnResizing") for r in tableaux(t)):
            orig = hp.original(bundle, obj)
            if orig is None:
                print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            else:
                obj.save_typetree(orig)
                nb._dirty.add(bundle)
                fait = True
                print(f"{MODELE} : remis d'origine")
    env = nb.env_of(VUES)
    for n in AJOUTS:
        v = mono(env, n)
        if v is None:
            continue
        orig = hp.original(VUES, v)
        if orig is not None and v.read_typetree()["m_tableView"] != orig["m_tableView"]:
            v.save_typetree(orig)
            nb._dirty.add(VUES)
            fait = True
            print(f"{n} : remise d'origine (le reste de ui-tableviews n'est pas touché)")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    menu = menu_source()
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        rs = tableaux(o[3])
        ok = len(rs) == 2 and menu is not None and all(tableau_a_jour(o[3], r, menu) for r in rs)
        print(f"{MODELE} : " + ("tableaux déverrouillés" if ok else "tableaux d'origine"))
    env = nb.env_of(VUES)
    for n in AJOUTS:
        v = mono(env, n)
        print(f"{n} : " + ("introuvable" if v is None else ", ".join(ids(v.read_typetree()))))
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
            print("Recruteurs / analystes affectés : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
