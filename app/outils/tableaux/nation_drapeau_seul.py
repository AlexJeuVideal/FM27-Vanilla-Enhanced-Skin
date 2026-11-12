"""Tableaux (effectif, tactiques, staff, recherche, transferts…) : colonnes Nationalité et 2e nationalité en logo seul,
plus grand, sans les 3 lettres — ou en logo + 3 lettres (options du skin, page 500 : nationalite / nationalite_2 ;
défaut = logo seul). Les colonnes sont toujours refaites depuis celles d'origine (sauvegarde) selon les options.

- Colonnes « logo + 3 lettres » (cellule FM nation-cell-medium, primarytext = ThreeLetterName), colonne Nation des
  tactiques (même cellule avec le nom, trop étroite : logo seul à l'écran) et colonnes « Drapeau » de FM (cellule
  data_display-cell-country-flag) -> une seule cellule « grand logo » (titre et tri gardés, largeur LARGEUR).
- Cellule « grand logo » = WageCashCell (cellule FM inutilisée, citée par aucun bundle) réécrite : copie de
  data_display-cell-country-flag, dont l'image (modèle NationFlag_Small, partagé par tout le jeu : pas touché) est
  recopiée dedans et agrandie à TAILLE px. Ailleurs (fiches, infobulles, recrutement) rien ne change.
Pas touché : LeaguesSummaryTableFactory (choix des championnats en début de partie).

Bundles :
- ui-tablefactories : moral_icone_seule (propriétaire, repart de l'original) rappelle fabrique_appliquer() quand ce
  script est actif ; sinon ce script écrit le bundle actuel. Retirer remet les colonnes d'origine (sauvegarde).
- bundle de modèles : WageCashCell (seul propriétaire : appliquer repart de l'original, retirer le remet).
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
import options  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer TAILLE -> augmenter VERSION)
# =====================================================================================================
TAILLE = 26             # px, taille du logo dans les tableaux (FM : 16 ; 22 vu en jeu : « encore un peu »)
LARGEUR = 48            # px, largeur par défaut et minimale des colonnes (= colonne FM « nation-flag-small »)
LARGEUR_3 = 70          # px, colonnes passées du nom complet aux 3 lettres (option « logo + 3 lettres »)
# options du skin (page 500) : nationalite / nationalite_2 = "logo" (défaut : logo seul, plus grand) | "3lettres"
EXCLURE = {"LeaguesSummaryTableFactory"}   # fabriques pas touchées
TACTIQUES = ("TacticTeamSelectionTableFactory", "nation")   # colonne Nation des tactiques (préfixe fabrique, id)
# =====================================================================================================

VERSION = 3   # v1 : cellule FM data_display-cell-country-flag (logo 16 px) ; v2 : cellule « grand logo »
              # v3 : v2 vue en jeu, logos pas plus gros (seul le cadre agrandi) -> l'image aussi
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
CELLULE_TEXTE = "c73088b9c5038f94f821ad13d945a8ba"     # nation-cell-medium (image + texte)
CELLULE_DRAPEAU = "69efafdc7cba8bd48a1c61b3de81f6cd"   # data_display-cell-country-flag (image seule, param binding)
GRANDE = "WageCashCell"                                # cellule FM inutilisée, réécrite en « grand logo »
GUID_GRANDE = "6d8a39e7b2fd7924db0b38213493e349"
SOURCE_CELLULE = "data_display-cell-country-flag"
SOURCE_IMAGE = "NationFlag_Small"
CLASSE_IMAGE = "nation-flag-small-16px"
NOM = f"UIPickerGrandLogo-v{VERSION}-{TAILLE}"
MARKER = os.path.join(backup.BACKUP_DIR, "nation_drapeau_seul.actif")
DRY_RUN = "--dry-run" in sys.argv

for _k, _v in {"width": (131105, 3), "height": (131087, 3), "max-height": (131094, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


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


def classer(fabrique, r):
    """colonne d'ORIGINE (FM) -> ("nat" | "nat2", liaison de la nation) ou None"""
    g = (r.get("m_uxmlRef") or {}).get("m_AssetGUID")
    vb = {b.get("from"): b for b in r.get("m_valueBindings") or []}
    if r["m_id"] == "second-nationality":   # joueurs : image + nom complet ; staff : image + 3 lettres (f5cd6927)
        n = vb.get("nation") or vb.get("binding")
        return ("nat2", n) if n is not None else None
    if g == CELLULE_DRAPEAU:
        n = vb.get("binding") or vb.get("nation")
        return ("nat", n) if n is not None else None
    if g != CELLULE_TEXTE:
        return None
    p, n = vb.get("primarytext"), vb.get("nation")
    if p is None or n is None:
        return None
    if p["to"]["m_path"].lower().endswith("threelettername") or \
            (fabrique.startswith(TACTIQUES[0]) and r["m_id"] == TACTIQUES[1]):
        return "nat", n
    return None


def grand_logo(r, n):
    b = copy.deepcopy(n)
    b["from"] = "binding"
    r["m_valueBindings"] = [b]
    r["m_uxmlRef"]["m_AssetGUID"] = GUID_GRANDE
    r["m_defaultWidth"] = r["m_minimumWidth"] = float(LARGEUR)


def trois_lettres(r):
    """colonne image + texte de FM : texte = 3 lettres (rien à faire si elle les a déjà ou n'a pas de texte)"""
    for b in r.get("m_valueBindings") or []:
        if b.get("from") == "primarytext" and not b["to"]["m_path"].lower().endswith("threelettername"):
            b["to"]["m_path"] = b["to"]["m_path"].rsplit(".", 1)[0] + ".ThreeLetterName"
            r["m_defaultWidth"] = r["m_minimumWidth"] = float(LARGEUR_3)


def origine_colonnes():
    """{(fabrique, id): colonne d'origine} des colonnes Nationalité (sauvegarde, sinon bundle actuel jamais modifié)"""
    orig = backup.backup_path(FABRIQUES)
    env = UnityPy.load(orig if os.path.exists(orig) else FABRIQUES)
    return {(tt["m_Name"], r["m_id"]): r for _, tt in fabriques(env) for r in tt["m_rowData"]
            if classer(tt["m_Name"], r)}


def fabrique_appliquer(env):
    """colonnes Nationalité de env (déjà chargé) refaites depuis l'origine selon les options ; True si changé"""
    modes = {"nat": options.get("nationalite"), "nat2": options.get("nationalite_2")}
    origine = origine_colonnes()
    change = False
    for o, tt in fabriques(env):
        faits = []
        for i, r in enumerate(tt["m_rowData"]):
            d = origine.get((tt["m_Name"], r["m_id"]))
            if d is None:
                continue
            quoi, n = classer(tt["m_Name"], d)
            neuf = copy.deepcopy(d)
            if modes[quoi] == "logo":
                grand_logo(neuf, n)
            else:
                trois_lettres(neuf)
            if json.dumps(neuf) != json.dumps(r):
                tt["m_rowData"][i] = neuf
                faits.append(r["m_id"])
        if faits:
            o.save_typetree(tt)
            change = True
            print(f"{tt['m_Name']} : nationalités refaites ({', '.join(faits)})")
    return change


def deja(env):
    return [(tt["m_Name"], r["m_id"]) for _, tt in fabriques(env) for r in tt["m_rowData"]
            if (r.get("m_uxmlRef") or {}).get("m_AssetGUID") == GUID_GRANDE]


# ---------- la cellule « grand logo » (WageCashCell réécrite) ----------
def marques(t):
    return [r for r in t.walk() if t.name(r).startswith("UIPickerGrandLogo")]


def construire(t):
    s, img = hp.src_tree(SOURCE_CELLULE), hp.src_tree(SOURCE_IMAGE)
    if s is None or img is None:
        return f"{SOURCE_CELLULE} / {SOURCE_IMAGE} introuvables"
    s_bundle, _, s_tt = nb.find_vta(SOURCE_CELLULE)
    i_bundle, _, i_tt = nb.find_vta(SOURCE_IMAGE)
    s.styles, img.styles = sm.Styles(s_bundle, s_tt), sm.Styles(i_bundle, i_tt)
    racine = t.tt["m_VisualTree"]["rid"]
    s_comp = next((r for r in s.children(s.tt["m_VisualTree"]["rid"]) if typ(s, r) == "ComponentElement"), None)
    i_racine = next(iter(img.children(img.tt["m_VisualTree"]["rid"])), None)
    if s_comp is None or i_racine is None:
        return "structure FM inattendue"
    for k in list(t.children(racine)):
        t.remove(k)
    comp = t.clone(s_comp, racine, src=s)
    t.styles.copy_from(s.styles, t, comp)
    t.sd(comp)["name"], t.sd(comp)["name_UxmlAttributeFlags"] = NOM, 1
    tpl = next((r for r in t.children(comp) if t.elem(r).get("m_TemplateAlias") == SOURCE_IMAGE), None)
    if tpl is None:
        return "image de la cellule FM introuvable"
    index = t.children(comp).index(tpl)
    t.remove(tpl)
    copie = t.clone(i_racine, comp, index, src=img)   # contenu de NationFlag_Small recopié (paramètre nation)
    t.styles.copy_from(img.styles, t, copie)
    cadres = [r for r in t.walk(copie) if CLASSE_IMAGE in (t.elem(r).get("m_Classes") or [])]
    if not cadres:
        return f"cadre .{CLASSE_IMAGE} introuvable"
    taille = {"width": TAILLE, "height": TAILLE, "min-width": TAILLE, "min-height": TAILLE,
              "max-width": TAILLE, "max-height": TAILLE}
    for r in cadres:   # cadre : USS FM 16 x 10 px
        t.styles.style(t, r, taille)
        for k in t.walk(r):   # l'image elle-même : hauteur 10 px en style intégré FM (v2 : seul le cadre agrandi)
            if k != r and typ(t, k).endswith("SIImage"):
                t.styles.style(t, k, taille)
    t.tt["m_Usings"] = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") != SOURCE_IMAGE]
    return None


def cellule_appliquer():
    """True si la cellule est (ou a été mise) à jour"""
    o = ouvrir(GRANDE)
    if o is None:
        print(f"{GRANDE} introuvable (renommée par une mise à jour ?), ignoré")
        return False
    if any(o[3].name(r) == NOM for r in marques(o[3])):
        print(f"{GRANDE} : grand logo déjà en place")
        return True
    bundle, obj, tt, t = ouvrir(GRANDE, depart_original=True)
    if marques(t):
        print(f"{GRANDE} : pas de sauvegarde d'origine propre, ignoré")
        return False
    erreur = construire(t)
    if erreur:
        print(f"{GRANDE} : {erreur}, rien enregistré")
        return False
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{GRANDE} : réécrite en grand logo ({TAILLE} px)")
    return True


def cellule_retirer():
    o = ouvrir(GRANDE)
    if o is None or not marques(o[3]):
        return
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{GRANDE} : pas de sauvegarde d'origine")
        return
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{GRANDE} : remise d'origine")


# ---------- commandes ----------
def _ecrire(env):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(FABRIQUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(FABRIQUES, data)


def cmd_appliquer():
    # la cellule d'abord : une colonne ne doit jamais pointer vers une cellule pas réécrite
    if not cellule_appliquer():
        return
    if not origine_colonnes():
        print("nationalités : aucune colonne trouvée (le jeu a changé ?), rien fait")
        return
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env):
        _ecrire(env)
    else:
        print("nationalités : colonnes déjà comme les options le demandent")
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    if os.path.exists(backup.backup_path(FABRIQUES)):
        origine = origine_colonnes()
        env = UnityPy.load(FABRIQUES)
        change = False
        for o, tt in fabriques(env):
            faits = []
            for i, r in enumerate(tt["m_rowData"]):
                d = origine.get((tt["m_Name"], r["m_id"]))
                if d is not None and json.dumps(d) != json.dumps(r):
                    tt["m_rowData"][i] = copy.deepcopy(d)
                    faits.append(r["m_id"])
            if faits:
                o.save_typetree(tt)
                change = True
                print(f"{tt['m_Name']} : colonnes d'origine remises ({', '.join(faits)})")
        if change:
            _ecrire(env)
    cellule_retirer()   # après les colonnes : plus aucune ne pointe vers elle


def cmd_etat():
    env = UnityPy.load(FABRIQUES)
    print("options : nationalité =", options.get("nationalite"), "| 2e nationalité =", options.get("nationalite_2"))
    print("colonnes en grand logo :", ", ".join(f"{f}/{c}" for f, c in deja(env)) or "aucune")
    a_jour = not fabrique_appliquer(UnityPy.load(FABRIQUES))
    print("colonnes conformes aux options :", "oui" if a_jour else "NON (appliquer)")
    o = ouvrir(GRANDE)
    if o is not None:
        t = o[3]
        etat = "à jour" if any(t.name(r) == NOM for r in marques(t)) else "ANCIENNE version"
        print(f"{GRANDE} :", f"grand logo ({etat})" if marques(t) else "d'origine")
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
            print("nationalité en grand logo : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
