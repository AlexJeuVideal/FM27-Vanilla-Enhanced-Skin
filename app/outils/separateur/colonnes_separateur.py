"""Tableaux : colonnes « Séparateur » = un trait vertical (couleur du bord des tuiles), fin ou épais, à poser où on
veut dans n'importe quelle vue par Insérer colonne > Séparateur (demande du joueur, 2026-11-07 ; v1 validée en jeu
le jour même, « ça marche parfaitement » ; v2 : trait épais en plus, colonne plus large pour l'attraper).

- Fabriques (ui-tablefactories) : v3 = une colonne fine + une épaisse au menu, id = nom affiché (NOMS, langue du
  skin) ; celles de l'autre langue et les anciennes (ANCIENS, v1 / v2 : 4 + 4) restent dans les fabriques sans être
  au menu (vues perso déjà enregistrées). En-tête vide, pas de tri, pas de
  liaison (comme les colonnes de sélection de FM). moral_icone_seule (propriétaire, repart de l'original) rappelle
  fabrique_appliquer() quand ce script est actif ; sinon ce script écrit le bundle actuel.
- Menus « Insérer colonne » (ui-tableviews, partagé : seulement nos entrées) : rubrique « Séparateur » (texte du jeu
  à la fin, avec Séparateur fin puis Séparateur épais (noms en PropertyValue : voir NOMS).
- Cellules FM inutilisées (citées par aucun bundle) réécrites : un trait de TAILLES[..] px, couleur COULEUR
  (= --colours-alpha-light-20 du bord des tuiles, .surfaces-card-tile-border), hauteur de la ligne.
Pas touché : LeaguesSummaryTableFactory (choix des championnats en début de partie).
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
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage de la cellule -> augmenter VERSION)
# =====================================================================================================
TAILLES = {"fin": 1, "epais": 3}   # px (fin = bord des tuiles : --global-border-width-tile-card)
COULEUR = (1.0, 1.0, 1.0, 0.2)  # bord des tuiles : --colours-alpha-light-20 (blanc à 20 %)
LARGEUR = 24                   # px, largeur par défaut de la colonne (trait centré ; v1 12 : en-tête dur à attraper)
LARGEUR_MIN = 16               # px
EXCLURE = {"LeaguesSummaryTableFactory"}
# =====================================================================================================

VERSION = 2   # v1 : trait fin seul, colonne 12 px ; v2 : + trait épais, colonne 24 px (cellules inchangées en v3)
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
# taille : (cellule FM inutilisée réécrite, son GUID)
CELLULES = {"fin": ("CompCellNoBorderStart", "e236ff867a9e161488f904e9ec5513ba"),
            "epais": ("CompCellNoBorder", "701b8e3e40597284894afc5531d11f13")}
SOURCE_TRAIT = "tile-figma-base-template"   # son #Border_TIle = VisualElement simple, recopié (sans classe ni style)
NOM_TRAIT = "Border_TIle"
CLASSE = f"uipicker-separateur-v{VERSION}"
# v3 (le joueur, 2026-11-07 : « 1 fin, 1 épais, 8 c'est trop » + noms propres) : les numéros de texte du jeu essayés
# (330444, 396164 / 396163 : table des textes de la partie, pas celle de l'interface) ne sont pas trouvés par FM, qui
# affiche alors le PropertyValue (= id de la colonne / clé de la rubrique) : on y met donc le nom affiché, dans la
# langue du skin (textes=True : refait au changement de langue)
NOMS = {"fr": {"rubrique": "Séparateur", "fin": "Séparateur fin", "epais": "Séparateur épais"},
        "en": {"rubrique": "Separator", "fin": "Thin separator", "epais": "Thick separator"}}
# 2026-11-07, demande « un seul bouton qui reste même s'il est déjà dans la vue » : PAS faisable par les bundles
# (c'est le code de FM qui retire du menu une colonne déjà dans la vue et refuse deux fois la même).
# v4 (le joueur : « met juste 15 épais ») : au menu, seulement l'épais, en NOMBRE copies au même nom (id = nom +
# i espaces à la fin, invisibles ; la 1re = l'id v3 sans espace). Le fin n'est plus au menu (gardé dans les fabriques).
NOMBRE = 15
AU_MENU = ("epais",)
LIBELLE = 330444   # numéro inconnu de l'interface : FM montre le PropertyValue (vu en jeu)
# colonnes plus proposées au menu, gardées dans les fabriques : vues perso déjà enregistrées (v1 / v2)
ANCIENS = {**{f"uipicker-separateur-{i}": "fin" for i in range(1, 5)},
           **{f"uipicker-separateur-epais-{i}": "epais" for i in range(1, 5)}}
PREFIXE_ID = "uipicker-separateur-"
REPERE = "UIPickerSeparateur"   # debug_name de nos entrées de menu
MARKER = os.path.join(backup.BACKUP_DIR, "colonnes_separateur.actif")
DRY_RUN = "--dry-run" in sys.argv

for _k, _v in {"width": (131105, 3), "height": (131087, 3), "align-items": (131073, 7),
               "justify-content": (131088, 7), "align-self": (131074, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


def nom_cellule(taille):
    return f"UIPickerSeparateur-v{VERSION}-{taille}-{TAILLES[taille]}"


def lg():
    import langue
    return "fr" if langue.LANGUE == "fr" else "en"


def noms():
    return NOMS[lg()]


def copies(nom, taille):
    return [(nom + " " * i, taille) for i in range(NOMBRE)]


def ids():
    """[(id de colonne, taille)] du menu, dans la langue du skin"""
    return [c for k in AU_MENU for c in copies(noms()[k], k)]


def toutes():
    """{id: taille} de toutes nos colonnes : menu, autre langue, fin (v3), anciennes v1 / v2 (rien ne casse dans
    une vue enregistrée)"""
    out = {}
    for n in NOMS.values():
        for k in TAILLES:
            out.update(copies(n[k], k) if k in AU_MENU else [(n[k], k)])
    out.update(ANCIENS)
    return out


def a_nous(cid):
    return cid in toutes() or cid.startswith(PREFIXE_ID)


# ---------- colonnes (ui-tablefactories) ----------
def fabriques(env):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if tt.get("m_rowData") and tt.get("m_Name") not in EXCLURE:
            yield o, tt


def colonne(modele, cid, taille):
    r = copy.deepcopy(modele)
    vide = {"m_AssetGUID": "", "m_SubObjectName": "", "m_SubObjectType": ""}
    r.update({"m_id": cid, "m_headerLabelBinding": {"m_path": ""}, "m_hintLabelBinding": {"m_path": ""},
              "m_translationID": {"GameID": 0}, "m_translationArgs": [], "m_hintID": {"GameID": -1},
              "m_hintArgs": [], "m_sortBinding": {"m_path": ""}, "m_sortBindingPlugin": 0, "m_sortAscending": 0,
              "m_defaultWidth": float(LARGEUR), "m_minimumWidth": float(LARGEUR_MIN),
              "m_allowWidthAutoResizing": 0, "m_autoSizeCellPadding": 0.0, "m_cellClass": "",
              "m_valueBindings": [], "m_headerValueBindings": [], "m_enableFooter": 0, "m_footerValueBindings": [],
              "m_uxmlRef": dict(vide, m_AssetGUID=CELLULES[taille][1]), "m_headerUxmlRef": dict(vide),
              "m_footerUxmlRef": dict(vide), "m_cellShortcuts": []})
    return r


def fabrique_appliquer(env, retirer=False):
    """colonnes séparateur de chaque fabrique de env (déjà chargé) mises comme voulu ; True si changé"""
    change = 0
    for o, tt in fabriques(env):
        reste = [r for r in tt["m_rowData"] if not a_nous(r["m_id"])]
        voulu = reste if retirer else reste + [colonne(reste[0], c, k) for c, k in toutes().items()]
        if json.dumps(voulu) != json.dumps(tt["m_rowData"]):
            tt["m_rowData"] = voulu
            o.save_typetree(tt)
            change += 1
    if change and retirer:
        print(f"séparateurs : {change} fabrique(s) de colonnes remises")
    elif change:
        print(f"séparateurs : {change} fabrique(s) de colonnes mises à jour")
    return bool(change)


# ---------- menus Insérer colonne (ui-tableviews) ----------
def menus(env):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if tt.get("m_contextMenuData") and "references" in tt:
            yield o, tt


def entrees(tt):
    return [r for r in tt["references"]["RefIds"] if isinstance(r.get("data"), dict)]


def menu_voulu(tt, retirer=False):
    """tt modifié (nos entrées retirées puis remises) ; False si pas un menu de colonnes"""
    feuille = next((r for r in entrees(tt) if isinstance(r["data"].get("PropertyValue"), str)
                    and r["data"]["PropertyValue"] and not r["data"].get("ChildList")
                    and r["data"].get("debug_name") != REPERE), None)
    if feuille is None:
        return False
    tt["m_contextMenuData"] = [d for d in tt["m_contextMenuData"] if d.get("debug_name") != REPERE]
    nos = {r["rid"] for r in entrees(tt) if r["data"].get("debug_name") == REPERE}
    tt["references"]["RefIds"] = [r for r in tt["references"]["RefIds"] if r.get("rid") not in nos]
    if retirer:
        return True
    rid = max([r["rid"] for r in tt["references"]["RefIds"]] + [0]) + 1

    def entree(nom, valeur, enfants_):
        nonlocal rid
        e = copy.deepcopy(feuille)
        e["rid"] = rid
        e["data"].update(debug_name=REPERE, name=nom, ChildList=enfants_, Disable=0, AddSpacerBefore=0,
                         DisplayValue={"GameID": LIBELLE}, PropertyValue=valeur,
                         Requirement={"m_FileID": 0, "m_PathID": 0})
        tt["references"]["RefIds"].append(e)
        rid += 1
        return {"rid": e["rid"]}

    enfants = [entree(NOMS["en"][k], cid, []) for cid, k in ids()]
    rub = copy.deepcopy(tt["m_contextMenuData"][0])
    rub.update(debug_name=REPERE, name="Separators", ChildList=enfants, Disable=0, AddSpacerBefore=1,
               DisplayValue={"GameID": LIBELLE}, PropertyValue=noms()["rubrique"],
               Requirement={"m_FileID": 0, "m_PathID": 0})
    tt["m_contextMenuData"].append(rub)
    return True


def menus_appliquer(retirer=False):
    env = UnityPy.load(VUES)
    change = 0
    for o, tt in menus(env):
        avant = json.dumps(tt)
        if menu_voulu(tt, retirer) and json.dumps(tt) != avant:
            o.save_typetree(tt)
            change += 1
    if not change:
        print("séparateurs : menus Insérer colonne déjà à jour")
        return
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(VUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(VUES, data)
    if retirer:
        print(f"séparateurs : {change} menu(s) Insérer colonne remis")
    else:
        print(f"séparateurs : {change} menu(s) Insérer colonne mis à jour")


# ---------- les cellules (cellules FM inutilisées réécrites, une par taille) ----------
def marques(t):
    return [r for r in t.walk() if t.name(r).startswith("UIPickerSeparateur")]


def construire(t, taille):
    epaisseur = TAILLES[taille]
    s = hp.src_tree(SOURCE_TRAIT)
    if s is None:
        return f"{SOURCE_TRAIT} introuvable"
    trait_src = next((r for r in s.walk() if s.name(r) == NOM_TRAIT and typ(s, r) == "VisualElement"), None)
    racine = t.tt["m_VisualTree"]["rid"]
    be = next((r for r in t.children(racine) if typ(t, r) == "BindingExpect"), None)
    if trait_src is None or be is None:
        return "structure FM inattendue"
    for k in list(t.children(be)):
        t.remove(k)
    t.sd(be)["Parameters"] = []   # aucune donnée (colonne sans liaison)
    trait = t.clone(trait_src, be, src=s)
    for k in list(t.children(trait)):
        t.remove(k)
    sm.no_styles(t, trait)
    t.elem(trait)["m_Classes"] = [CLASSE]
    t.sd(trait)["name"], t.sd(trait)["name_UxmlAttributeFlags"] = nom_cellule(taille), 1
    t.styles.style(t, be, {"flex-grow": 1, "height": {"unit": 2, "value": 100.0}, "align-self": "stretch",
                           "align-items": "center", "justify-content": "center"})
    t.styles.style(t, trait, {"width": epaisseur, "min-width": epaisseur, "max-width": epaisseur,
                              "height": {"unit": 2, "value": 100.0}, "flex-shrink": 0, "flex-grow": 0,
                              "background-color": COULEUR})
    return None


def cellules_appliquer():
    """True si les deux cellules sont (ou ont été mises) à jour ; un seul enregistrement du bundle"""
    ok, ecrire = True, False
    for taille, (cellule, _) in CELLULES.items():
        o = ouvrir(cellule)
        if o is None:
            print(f"{cellule} introuvable (renommée par une mise à jour ?), ignoré")
            ok = False
            continue
        if any(o[3].name(r) == nom_cellule(taille) for r in marques(o[3])):
            print(f"{cellule} : séparateur déjà en place")
            continue
        bundle, obj, tt, t = ouvrir(cellule, depart_original=True)
        if marques(t):
            print(f"{cellule} : pas de sauvegarde d'origine propre, ignoré")
            ok = False
            continue
        erreur = construire(t, taille)
        if erreur:
            print(f"{cellule} : {erreur}, rien enregistré")
            ok = False
            continue
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        ecrire = True
        print(f"{cellule} : réécrite en séparateur ({TAILLES[taille]} px)")
    if ecrire:
        nb.save_all()
    return ok


def cellules_retirer():
    ecrire = False
    for cellule, _ in CELLULES.values():
        o = ouvrir(cellule)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{cellule} : pas de sauvegarde d'origine")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        ecrire = True
        print(f"{cellule} : remise d'origine")
    if ecrire:
        nb.save_all()


# ---------- commandes ----------
def _ecrire_fabriques(env):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(FABRIQUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(FABRIQUES, data)


def cmd_appliquer():
    # la cellule d'abord : une colonne ne doit jamais pointer vers une cellule pas réécrite
    if not cellules_appliquer():
        return
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env):
        _ecrire_fabriques(env)
    else:
        print("séparateurs : colonnes déjà en place")
    menus_appliquer()
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    menus_appliquer(retirer=True)   # les menus d'abord : plus d'entrée vers une colonne absente
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env, retirer=True):
        _ecrire_fabriques(env)
    cellules_retirer()   # après les colonnes : plus aucune ne pointe vers elles


def cmd_etat():
    env = UnityPy.load(FABRIQUES)
    avec = [tt["m_Name"] for _, tt in fabriques(env) if any(a_nous(r["m_id"]) for r in tt["m_rowData"])]
    print(f"fabriques avec séparateurs : {len(avec)}")
    env = UnityPy.load(VUES)
    m = [tt["m_Name"] for _, tt in menus(env) if any(d.get("debug_name") == REPERE for d in tt["m_contextMenuData"])]
    print(f"menus Insérer colonne avec Séparateur : {len(m)}")
    for taille, (cellule, _) in CELLULES.items():
        o = ouvrir(cellule)
        if o is not None:
            t = o[3]
            etat = "à jour" if any(t.name(r) == nom_cellule(taille) for r in marques(t)) else "ANCIENNE version"
            print(f"{cellule} :", f"séparateur ({etat})" if marques(t) else "d'origine")
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
            print("séparateurs : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
