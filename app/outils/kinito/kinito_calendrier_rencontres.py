"""[AJOUT KINITO] Portail > Calendrier ouvre l'onglet Rencontres au lieu de Général.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Le menu du Portail n'est pas fabriqué par le code : il est décrit dans les données PortalSubtabs
(bundle gamemodules_assets_gameworld). Son entrée « Calendar » ouvre l'écran CalendarTool avec
calendartab = const.zero (Général). Son menu déroulant ▾ a déjà une entrée « Rencontres » (« Fixture Schedule
(Tab) » : écran CalendarToolFixturesTab, calendartab = const.Two). Ce script donne au clic sur « Calendrier »
exactement l'action de cette entrée (m_openEvent recopié) ; tout le reste de l'entrée (nom, écran de référence
pour la surbrillance, menu déroulant) ne bouge pas. L'entrée « Calendar (Unemployed) » (sans club : pas d'onglet
Rencontres) n'est pas touchée. Tout autre lien vers le calendrier ouvre toujours l'onglet qu'il demande.

v1 (2026-11-12, retirée) : DefaultSelection du TabbedGridLayoutElement de CalendarTool, sans effet en jeu (le menu
impose l'onglet 0). Appliquer remet CalendarTool d'origine s'il porte encore la v1.

Données touchées (ce script est leur seul propriétaire, appliquer repart toujours de l'original sauvegardé) :
- PortalSubtabs (gamemodules_assets_gameworld.bundle ; depuis, ui-globalnavigation_assets_all.bundle : v3) :
  m_openEvent de l'entrée « Calendar ».

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_calendrier_rencontres.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_calendrier_rencontres.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_calendrier_rencontres.py etat
"""
import copy
import json
import os
import sys

import UnityPy

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (aussi : correctif UnityPy des références vides)
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import ouvrir  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
#  onglet ouvert par Portail > Calendrier : celui de l'entrée du menu déroulant qui passe ce calendartab
#  (const.Zero = Général, const.One = Entraînement, const.Two = Rencontres)
ONGLET = "const.two"
# =====================================================================================================

DONNEES = "PortalSubtabs"
# v3 (Alex, 12/11) : PortalSubtabs a quitté gamemodules_assets_gameworld (déjà absent avant) : maintenant dans
# ui-globalnavigation_assets_all ; le 1er des deux qui l'a
MENUS = [os.path.join(nb.AA, n) for n in ("gamemodules_assets_gameworld.bundle", "ui-globalnavigation_assets_all.bundle")]


def _menu():
    for b in MENUS:
        if os.path.exists(b) and any(o.type.name == "MonoBehaviour" and _nom(o) == DONNEES for o in nb.env_of(b).objects):
            return b
    return MENUS[0]


def _nom(o):
    try:
        return o.peek_name()
    except Exception:
        return None


MENU = _menu()
ENTREE = "Calendar"                 # entrée du menu (debug_name), pas « Calendar (Unemployed) »
MODELE_V1 = "CalendarTool"          # touché par la v1, remis d'origine
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_calendrier_rencontres.actif")


# ---------- les données du menu ----------
def objet_menu(bundle):
    env = nb.env_of(bundle)
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == DONNEES:
                return o
        except Exception:
            continue
    return None


def original_menu(bundle, obj):
    """typetree d'origine des données du menu (sauvegarde des originaux), ou None"""
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    o = next((x for x in UnityPy.load(backup.backup_path(bundle)).objects if x.path_id == obj.path_id), None)
    return o.read_typetree() if o is not None else None


def tab_de(evenement):
    for a in evenement.get("m_argumentBindings") or []:
        if a.get("name", "").lower() == "calendartab":
            return a["path"]["m_path"]
    return None


def calendrier(tt):
    """(entrée « Calendar », son entrée de menu déroulant qui ouvre ONGLET) ; (None, raison) sinon"""
    entrees = [s for s in tt.get("m_submenus") or [] if s.get("debug_name") == ENTREE]
    if len(entrees) != 1:
        return None, f"{len(entrees)} entrée(s) « {ENTREE} » au lieu d'une"
    e = entrees[0]
    refs = {r["rid"]: r for r in (tt.get("references") or {}).get("RefIds") or []}
    enfants = [refs[c["rid"]]["data"] for c in e.get("ChildList") or [] if c["rid"] in refs]
    cibles = [c for c in enfants if (tab_de(c["PropertyValue"]["m_openEvent"]) or "").lower() == ONGLET.lower()]
    if len(cibles) != 1:
        return None, f"{len(cibles)} entrée(s) du menu déroulant avec calendartab = {ONGLET} au lieu d'une"
    return e, cibles[0]


def applique(e, cible):
    return e["PropertyValue"]["m_openEvent"] == cible["PropertyValue"]["m_openEvent"]


# ---------- v1 : remettre CalendarTool d'origine ----------
def nettoyer_v1():
    o = ouvrir(MODELE_V1)
    if o is None:
        return []
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        return []
    def defaut(x):
        return next((r["data"].get("DefaultSelection") for r in x["references"]["RefIds"]
                     if (r.get("type") or {}).get("class") == "TabbedGridLayoutElement/UxmlSerializedData"
                     and r.get("data")), None)
    if defaut(tt) == defaut(orig):
        return []
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    return [f"{MODELE_V1} remis d'origine (essai v1, sans effet en jeu)"]


# ---------- commandes ----------
def cmd_appliquer():
    msgs = nettoyer_v1()
    obj = objet_menu(MENU)
    if obj is None:
        print(f"[Kinito] calendrier sur Rencontres : données {DONNEES} introuvables (renommées par une mise à jour ?), "
              "rien enregistré")
        return
    e, cible = calendrier(obj.read_typetree())
    if e is None:
        print(f"[Kinito] calendrier sur Rencontres : {cible}, rien enregistré")
        return
    if applique(e, cible) and not msgs:
        print("[Kinito] calendrier sur Rencontres : déjà appliqué")
    else:
        if not applique(e, cible):
            tt = original_menu(MENU, obj) or obj.read_typetree()
            e, cible = calendrier(tt)
            if e is None:
                print(f"[Kinito] calendrier sur Rencontres : original sauvegardé illisible ({cible}), rien enregistré")
                return
            avant = tab_de(e["PropertyValue"]["m_openEvent"])
            e["PropertyValue"]["m_openEvent"] = copy.deepcopy(cible["PropertyValue"]["m_openEvent"])
            obj.save_typetree(tt)
            nb._dirty.add(MENU)
            msgs.append(f"Portail > Calendrier : calendartab {avant} -> {ONGLET} (même action que l'entrée "
                        f"« {cible.get('debug_name')} » du menu déroulant)")
        for m in msgs:
            print(f"[Kinito] calendrier sur Rencontres : {m}")
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    msgs = nettoyer_v1()
    obj = objet_menu(MENU)
    if obj is not None:
        e, cible = calendrier(obj.read_typetree())
        orig = original_menu(MENU, obj)
        if e is not None and applique(e, cible):
            if orig is None:
                print(f"{DONNEES} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            else:
                obj.save_typetree(orig)
                nb._dirty.add(MENU)
                msgs.append(f"{DONNEES} remis d'origine (Portail > Calendrier ouvre de nouveau Général)")
    if msgs:
        for m in msgs:
            print(m)
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    obj = objet_menu(MENU)
    if obj is None:
        print(f"{DONNEES} : introuvable")
    else:
        e, cible = calendrier(obj.read_typetree())
        if e is None:
            print(f"{DONNEES} : {cible}")
        else:
            print(f"{DONNEES} : Portail > Calendrier ouvre calendartab = {tab_de(e['PropertyValue']['m_openEvent'])}"
                  + (" (appliqué)" if applique(e, cible) else " (d'origine)"))
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
            print("[Kinito] calendrier sur Rencontres : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
