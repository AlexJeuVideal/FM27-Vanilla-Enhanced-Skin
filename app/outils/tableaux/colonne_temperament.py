"""Colonnes « Tempérament » et « Tempérament (logo) » (Bosseur / Penseur / Relaxé / Leader) dans le menu
Insérer colonne > Infos générales.

- Tempérament : la colonne existe déjà dans le jeu (PlayerTableFactory, id « mindset », celle de Dynamique de
  groupe > Tempéraments), mais aucun menu de colonnes de joueurs ne la propose. Entrée ajoutée juste après
  « Personnalité » (FM ou colonne_personnalite), sinon après « Rapports avec les médias ».
- Tempérament (logo) (2026-11-13, le joueur : « juste le logo, ça prend moins de place ») : logo seul, colonne
  étroite. Cellule = modèle FM cité par rien (PlayerMindsetStatusWithIcon) réécrit en copie de PlayerMindsetCell
  sans le texte ; colonne ajoutée aux fabriques qui ont « mindset » (id = nom affiché, langue du skin : FM montre le
  PropertyValue quand le numéro de texte est inconnu, comme colonnes_separateur) ; entrée juste après Tempérament.

Bundles :
- ui-tableviews (partagé) : entrées ajoutées sur le bundle actuel (repère debug_name), retirées par repère.
- ui-tablefactories : moral_icone_seule (propriétaire, repart de l'original) rappelle fabrique_appliquer() quand ce
  script est actif ; sinon ce script écrit le bundle actuel.
- modèle PlayerMindsetStatusWithIcon (seul propriétaire) : repart de l'original, retirer le remet.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\tableaux\\colonne_temperament.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\tableaux\\colonne_temperament.py retirer [--dry-run]
  .venv\\Scripts\\python.exe outils\\tableaux\\colonne_temperament.py etat
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
#  RÉGLAGES (changer la cellule -> augmenter VERSION)
# =====================================================================================================
APRES = ["personality", "media-handling"]   # Tempérament placé après la 1re trouvée
LOGO = True                # ajoute aussi « Tempérament (logo) » juste après Tempérament
LARGEUR = 40               # px, colonne logo (largeur par défaut)
LARGEUR_MIN = 30           # px
# =====================================================================================================

VERSION = 1
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
INFOS = "media-handling"           # repère d'un menu de joueurs avec Infos générales
COLONNE = "mindset"                # id de la colonne dans PlayerTableFactory
LIBELLE = 3115                     # texte traduit de l'en-tête de la colonne du jeu (Tempérament)
LIBELLE_INCONNU = 330444           # numéro inconnu de l'interface : FM montre le PropertyValue (colonnes_separateur)
REPERE = "UIPickerTemperament"     # debug_name de nos entrées
REPERE_LOGO = "UIPickerTemperamentLogo"
NOMS_LOGO = {"fr": "Tempérament (logo)", "en": "Mindset (icon)"}   # id de la colonne logo = nom affiché
SOURCE_CELLULE = "PlayerMindsetCell"               # cellule FM (logo + texte)
CELLULE = ("PlayerMindsetStatusWithIcon", "1e968bfc663bbb14eafcf6c0e9364ff8")   # FM, citée par rien : réécrite
NOM_CELLULE = f"UIPickerTemperamentLogo-v{VERSION}"
CLASSE = f"uipicker-temperament-logo-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "colonne_temperament.actif")
DRY_RUN = "--dry-run" in sys.argv

for _k, _v in {"align-items": (131073, 7), "justify-content": (131088, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


def lg():
    import langue
    return "fr" if langue.LANGUE == "fr" else "en"


def id_logo():
    return NOMS_LOGO[lg()]


def monos(env, pred):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if pred(tt):
            yield o, tt


# ---------- menus Insérer colonne (ui-tableviews) ----------
def menus(env):
    """[(objet, typetree)] des collections de vues qui ont un menu de colonnes"""
    return list(monos(env, lambda tt: tt.get("m_contextMenuData") and "references" in tt))


def entrees(tt):
    """{rid: données} des entrées du menu"""
    return {r["rid"]: r for r in tt["references"]["RefIds"] if isinstance(r.get("data"), dict)}


def a_colonne(tt, valeur):
    return any(r["data"].get("PropertyValue") == valeur for r in entrees(tt).values())


def a_repere(tt, repere=REPERE):
    return any(r["data"].get("debug_name") == repere for r in entrees(tt).values())


def parent_de(tt, rid):
    """liste ChildList qui contient rid (racine ou sous-menu)"""
    for d in tt["m_contextMenuData"] + [r["data"] for r in entrees(tt).values()]:
        for i, c in enumerate(d.get("ChildList", [])):
            if c.get("rid") == rid:
                return d["ChildList"], i
    return None, None


def ajouter(tt, apres_liste, repere, nom, valeur, libelle):
    refs = entrees(tt)
    for apres in apres_liste:
        modele = next((r for r in refs.values() if r["data"].get("PropertyValue") == apres), None)
        if modele is None:
            continue
        liste, i = parent_de(tt, modele["rid"])
        if liste is None:
            continue
        rid = max(refs) + 1
        neuf = copy.deepcopy(modele)
        neuf["rid"] = rid
        neuf["data"].update(debug_name=repere, name=nom, PropertyValue=valeur,
                            DisplayValue={"GameID": libelle}, AddSpacerBefore=0)
        tt["references"]["RefIds"].append(neuf)
        liste.insert(i + 1, {"rid": rid})
        return apres
    return None


def retirer_repere(tt, repere):
    refs = entrees(tt)
    nos = {rid for rid, r in refs.items() if r["data"].get("debug_name") == repere}
    if not nos:
        return False
    for d in tt["m_contextMenuData"] + [r["data"] for r in refs.values()]:
        if d.get("ChildList"):
            d["ChildList"] = [c for c in d["ChildList"] if c.get("rid") not in nos]
    tt["references"]["RefIds"] = [r for r in tt["references"]["RefIds"] if r.get("rid") not in nos]
    return True


def menu_logo(tt):
    """entrée « Tempérament (logo) » remise (langue du skin) ; True si changé"""
    avant = json.dumps(tt)
    retirer_repere(tt, REPERE_LOGO)
    if LOGO and a_colonne(tt, COLONNE):
        ajouter(tt, [COLONNE], REPERE_LOGO, "Mindset (icon)", id_logo(), LIBELLE_INCONNU)
    return json.dumps(tt) != avant


def menus_appliquer():
    env = UnityPy.load(VUES)
    change = 0
    for o, tt in menus(env):
        nom = tt["m_Name"]
        if not a_colonne(tt, INFOS):
            continue   # pas un menu de joueurs avec Infos générales
        fait = False
        if a_colonne(tt, COLONNE):
            print(f"{nom} : {'déjà appliqué' if a_repere(tt) else 'Tempérament déjà proposé par FM'}")
        else:
            apres = ajouter(tt, APRES, REPERE, "Mindset", COLONNE, LIBELLE)
            print(f"{nom} : " + (f"Tempérament ajouté après « {apres} »" if apres else "emplacement introuvable, ignoré"))
            fait = bool(apres)
        if menu_logo(tt):
            fait = True
            print(f"{nom} : « {id_logo()} » mis après Tempérament")
        if fait:
            o.save_typetree(tt)
            change += 1
    if change:
        ecrire(env, VUES)
        print(f"\n{change} menu(s) de colonnes mis à jour.")
    else:
        print("menus : rien à changer")


def menus_retirer():
    env = UnityPy.load(VUES)
    change = False
    for o, tt in menus(env):
        a, b = retirer_repere(tt, REPERE), retirer_repere(tt, REPERE_LOGO)
        if a or b:
            o.save_typetree(tt)
            change = True
            print(f"{tt['m_Name']} : Tempérament retiré")
    if change:
        ecrire(env, VUES)
    else:
        print("menus : rien à retirer")


# ---------- colonne logo (ui-tablefactories) ----------
def a_nous(cid):
    return cid in NOMS_LOGO.values()


def colonne_logo(src, cid):
    r = copy.deepcopy(src)
    r.update({"m_id": cid, "m_defaultWidth": float(LARGEUR), "m_minimumWidth": float(LARGEUR_MIN),
              "m_allowWidthAutoResizing": 0, "m_cellClass": ""})
    r["m_uxmlRef"] = dict(r["m_uxmlRef"], m_AssetGUID=CELLULE[1])
    return r


def fabrique_appliquer(env, retirer=False):
    """colonnes logo (deux langues) dans chaque fabrique qui a « mindset » (env déjà chargé) ; True si changé"""
    change = 0
    for o, tt in monos(env, lambda tt: bool(tt.get("m_rowData"))):
        rows = tt["m_rowData"]
        src = next((r for r in rows if r["m_id"] == COLONNE), None)
        if src is None:
            continue
        reste = [r for r in rows if not a_nous(r["m_id"])]
        voulu = reste if (retirer or not LOGO) else reste + [colonne_logo(src, c) for c in NOMS_LOGO.values()]
        if json.dumps(voulu) != json.dumps(rows):
            tt["m_rowData"] = voulu
            o.save_typetree(tt)
            change += 1
    if change:
        print(f"Tempérament (logo) : {change} fabrique(s) de colonnes {'remises' if retirer else 'mises à jour'}")
    return bool(change)


# ---------- la cellule logo seul (PlayerMindsetStatusWithIcon réécrite) ----------
def marques(t):
    return [r for r in t.walk() if t.name(r) == NOM_CELLULE]


def construire(t):
    s = hp.src_tree(SOURCE_CELLULE)
    if s is None:
        return f"{SOURCE_CELLULE} introuvable"
    be_src = next((r for r in s.children(s.tt["m_VisualTree"]["rid"]) if typ(s, r) == "BindingExpect"), None)
    if be_src is None or not any(typ(s, r) == "SIImage" for r in s.children(be_src)):
        return f"{SOURCE_CELLULE} : structure FM inattendue"
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    be = t.clone(be_src, racine, src=s)
    t.styles.copy_from(hp.ouvrir(SOURCE_CELLULE)[3].styles, t, be)
    textes = [r for r in t.children(be) if typ(t, r) != "SIImage"]
    for r in textes:
        t.remove(r)
    # logo centré dans la colonne : pleine largeur, sans « align-self-start »
    t.elem(be)["m_Classes"] = [c for c in t.elem(be).get("m_Classes") or [] if c != "align-self-start"] + [CLASSE]
    t.sd(be)["name"], t.sd(be)["name_UxmlAttributeFlags"] = NOM_CELLULE, 1
    t.styles.style(t, be, {"flex-grow": 1, "justify-content": "center", "align-items": "center"})
    return None


def cellule_appliquer():
    o = ouvrir(CELLULE[0])
    if o is None:
        print(f"{CELLULE[0]} introuvable (renommée par une mise à jour ?), ignoré")
        return False
    if marques(o[3]):
        print(f"{CELLULE[0]} : logo seul déjà en place")
        return True
    bundle, obj, tt, t = ouvrir(CELLULE[0], depart_original=True)
    if any(t.name(r).startswith("UIPickerTemperamentLogo") for r in t.walk()):
        print(f"{CELLULE[0]} : pas de sauvegarde d'origine propre, ignoré")
        return False
    erreur = construire(t)
    if erreur:
        print(f"{CELLULE[0]} : {erreur}, rien enregistré")
        return False
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{CELLULE[0]} : réécrite en logo de tempérament seul")
    return True


def cellule_retirer():
    o = ouvrir(CELLULE[0])
    if o is None or not any(o[3].name(r).startswith("UIPickerTemperamentLogo") for r in o[3].walk()):
        return
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{CELLULE[0]} : pas de sauvegarde d'origine")
        return
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{CELLULE[0]} : remise d'origine")


# ---------- commandes ----------
def ecrire(env, bundle):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(bundle)} ferait {len(data) / 1e6:.2f} Mo)")
        return
    backup.write_bundle(bundle, data)


def cmd_appliquer():
    # la cellule d'abord : une colonne ne doit jamais pointer vers une cellule pas réécrite
    if LOGO and not cellule_appliquer():
        print("Tempérament (logo) pas posé")
        return
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env):
        ecrire(env, FABRIQUES)
    elif LOGO:
        print("Tempérament (logo) : colonnes déjà en place")
    menus_appliquer()
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    menus_retirer()   # les menus d'abord : plus d'entrée vers une colonne absente
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env, retirer=True):
        ecrire(env, FABRIQUES)
    cellule_retirer()   # après les colonnes : plus aucune ne pointe vers elle


def cmd_etat():
    env = UnityPy.load(VUES)
    for _, tt in menus(env):
        if not a_colonne(tt, INFOS):
            continue
        if a_repere(tt):
            etat = "Tempérament ajouté"
        elif a_colonne(tt, COLONNE):
            etat = "Tempérament proposé par FM"
        else:
            etat = "pas de Tempérament"
        if a_repere(tt, REPERE_LOGO):
            etat += " + logo"
        print(f"{tt['m_Name']} : {etat}")
    env = UnityPy.load(FABRIQUES)
    avec = [tt["m_Name"] for _, tt in monos(env, lambda tt: bool(tt.get("m_rowData")))
            if any(a_nous(r["m_id"]) for r in tt["m_rowData"])]
    print("fabriques avec la colonne logo :", ", ".join(avec) or "aucune")
    o = ouvrir(CELLULE[0])
    if o is not None:
        print(f"{CELLULE[0]} :", "logo seul (à jour)" if marques(o[3]) else
              ("ANCIENNE version" if any(o[3].name(r).startswith("UIPickerTemperamentLogo") for r in o[3].walk())
               else "d'origine"))
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
        if actif():
            cmd_appliquer()
        else:
            print("colonne Tempérament : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
