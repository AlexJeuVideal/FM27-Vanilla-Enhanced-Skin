"""Compétition > Présentation de saison : colonne « Cotes » dans le pronostic du classement (à droite de « Infos ») et
bloc des équipes plus large (le bloc du bas et celui des transferts raccourcissent, l'Équipe type des médias garde
sa largeur).

- Colonne : OddsTableFactory (ui-tablefactories) reçoit la colonne « uipicker-odds » = cellule FM StandardLabelCell
  (celle de « Cl. » et « Infos ») sur binding.Odds (propriété FM de la ligne OddsLeagueTableRow), titre FM 230320
  « Odds » (traduit par le jeu). La vue SeasonPreviewOddsTableViewSettings (ui-tableviews) l'affiche après last-fate.
- Grilles (ui-tileslayouts) : CompetitionStagesCardSeasonPreview (bloc équipes | reste) : équipes +ELARGIR colonnes ;
  CompetitionSeasonPreviewCompView (blocs de droite) : Équipe type des médias recalculée pour garder sa largeur,
  transferts = le reste. Toujours recalculé depuis l'original (sauvegarde).
Bundles :
- ui-tablefactories : moral_icone_seule (propriétaire, repart de l'original) rappelle fabrique_appliquer() quand ce
  script est actif ; sinon ce script écrit le bundle actuel. Retirer enlève la colonne.
- ui-tableviews / ui-tileslayouts : seulement la vue / les compositions de cet écran (bundle actuel).
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
LARGEUR_COTES = 50      # px, colonne Cotes
ELARGIR = 1             # colonnes de grille ajoutées au bloc des équipes (prises au bloc de droite)
# =====================================================================================================

FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
TUILES = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
FABRIQUE = "OddsTableFactory"
VUE = "SeasonPreviewOddsTableViewSettings"
COLONNE = "uipicker-odds"
APRES = "last-fate"
TITRE = 230320                     # texte FM « Odds »
CHEMIN = "binding.Odds"
ENS_CADRE = "CompetitionStagesCardSeasonPreviewGridCompositionSet"
ENS_DROITE = "CompetitionSeasonPreviewCompViewGridCompositionSet"
EQUIPES, DROITE = "SeasonPreview_Teams", "SeasonPreview_CompView"
MEDIAS, TRANSFERTS = "SeasonPreview_MediaDreamTeam", "SeasonPreview_CompTransfers"
MARKER = os.path.join(backup.BACKUP_DIR, "saison_presentation.actif")
DRY_RUN = "--dry-run" in sys.argv
EN_COURS = False        # appliquer en cours : moral_icone_seule ajoute la colonne même sans marqueur
sys.modules.setdefault("saison_presentation", sys.modules[__name__])   # lancé en script : moral_icone_seule voit EN_COURS


def _objets(env, nom):
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                if o.peek_name() == nom:
                    return o, o.read_typetree()
            except Exception:
                continue
    return None, None


def _ecrire(env, bundle, msgs):
    data = env.file.save(packer="original")
    if nb.DRY_RUN or DRY_RUN:
        msgs.append(f"(essai à blanc : rien écrit, {os.path.basename(bundle)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(bundle, data)


def _origine(bundle):
    src = backup.backup_path(bundle)
    return UnityPy.load(src if os.path.exists(src) else bundle)


# ---------- colonne (ui-tablefactories) ----------
def fabrique_appliquer(env):
    """colonne Cotes dans OddsTableFactory de env (déjà chargé) ; True si ajoutée"""
    o, tt = _objets(env, FABRIQUE)
    if tt is None:
        print(f"{FABRIQUE} introuvable (renommée par une mise à jour ?), ignorée")
        return False
    lignes = tt["m_rowData"]
    if any(r["m_id"] == COLONNE for r in lignes):
        return False
    modele = next((r for r in lignes if r["m_id"] == APRES), None)
    if modele is None or not modele.get("m_valueBindings"):
        print(f"{FABRIQUE} : colonne {APRES} introuvable, ignorée")
        return False
    neuf = copy.deepcopy(modele)
    neuf["m_id"] = COLONNE
    neuf["m_translationID"] = {"GameID": TITRE}
    neuf["m_defaultWidth"] = neuf["m_minimumWidth"] = float(LARGEUR_COTES)
    b = neuf["m_valueBindings"][0]
    b["from"] = "binding"
    b["to"]["m_path"] = CHEMIN
    lignes.insert(lignes.index(modele) + 1, neuf)
    o.save_typetree(tt)
    print(f"{FABRIQUE} : colonne Cotes ajoutée")
    return True


def fabrique_retirer(env):
    o, tt = _objets(env, FABRIQUE)
    if tt is None or not any(r["m_id"] == COLONNE for r in tt["m_rowData"]):
        return False
    tt["m_rowData"] = [r for r in tt["m_rowData"] if r["m_id"] != COLONNE]
    o.save_typetree(tt)
    print(f"{FABRIQUE} : colonne Cotes retirée")
    return True


def _moral_actif():
    import moral_icone_seule as mi
    return os.path.exists(mi.MARKER)


# ---------- vue (ui-tableviews) ----------
def vue(retirer):
    env = UnityPy.load(VUES)
    o, tt = _objets(env, VUE)
    if tt is None:
        return [f"{VUE} introuvable, ignorée"]
    cfg = tt["m_tableView"]["m_tableConfig"]
    a = any(c["m_columnID"] == COLONNE for c in cfg)
    if retirer:
        if not a:
            return []
        tt["m_tableView"]["m_tableConfig"] = [c for c in cfg if c["m_columnID"] != COLONNE]
        msg = f"{VUE} : colonne Cotes retirée"
    else:
        if a:
            return [f"{VUE} : colonne Cotes déjà là"]
        modele = next((c for c in cfg if c["m_columnID"] == APRES), None)
        if modele is None:
            return [f"{VUE} : colonne {APRES} introuvable, ignorée"]
        neuf = copy.deepcopy(modele)
        neuf["m_columnID"] = COLONNE
        m = neuf["m_columnMetadata"]
        m["m_widthOverride"] = m["m_minWidthOverride"] = float(LARGEUR_COTES)
        m["m_titleTranslationIdOverride"] = {"GameID": 0}
        cfg.insert(cfg.index(modele) + 1, neuf)
        msg = f"{VUE} : colonne Cotes après « Infos »"
    o.save_typetree(tt)
    msgs = [msg]
    _ecrire(env, VUES, msgs)
    return msgs


# ---------- grilles (ui-tileslayouts) ----------
def _compositions(env, ensemble):
    objs = {o.path_id: o for o in env.objects}
    _, ens = _objets(env, ensemble)
    if ens is None:
        return []
    out = []
    for entry in ens["m_gridBreakpointCompositionData"]["m_values"]:
        for ref in entry["m_value"]:
            if ref["m_FileID"] == 0 and ref["m_PathID"] in objs:
                o = objs[ref["m_PathID"]]
                out.append((o, o.read_typetree()))
    return out


def _tuile(comps, nom):
    return next((c for c in comps if c["m_elementID"] == nom), None)


def _mini(c):
    l, mn = c["m_location"], c.get("m_minSize")
    if mn:
        mn["x"], mn["y"] = min(mn["x"], l["width"]), min(mn["y"], l["height"])


def _cadre(comps):
    """équipes + ELARGIR, reste - ELARGIR ; None si la composition n'a pas les deux"""
    e, d = _tuile(comps, EQUIPES), _tuile(comps, DROITE)
    if e is None or d is None or d["m_location"]["width"] <= ELARGIR + 4:
        return None
    ancien = d["m_location"]["width"]
    e["m_location"]["width"] += ELARGIR
    d["m_location"]["x"] += ELARGIR
    d["m_location"]["width"] -= ELARGIR
    _mini(e), _mini(d)
    return ancien, d["m_location"]["width"]


def _droite(comps, ancien, neuf):
    """Équipe type des médias : même largeur à l'écran (bloc de droite passé de ancien à neuf colonnes) ; transferts
    = le reste ; None si pas de transferts sur cette composition (rien à faire)"""
    m, t = _tuile(comps, MEDIAS), _tuile(comps, TRANSFERTS)
    if m is None or t is None:
        return None
    total = t["m_location"]["x"] + t["m_location"]["width"]
    if m["m_location"]["x"] != 0 or t["m_location"]["x"] != m["m_location"]["width"]:
        return None   # disposition FM inattendue
    w = round(m["m_location"]["width"] * ancien / neuf)
    w = max(m["m_location"]["width"], min(w, total - 3))
    m["m_location"]["width"] = w
    t["m_location"]["x"], t["m_location"]["width"] = w, total - w
    _mini(m), _mini(t)
    return w, total - w


def grilles(retirer):
    env = UnityPy.load(TUILES)
    orig = _origine(TUILES)
    msgs, change = [], False
    rapports = {}   # breakpoint -> (ancien, neuf) du bloc de droite
    for ensemble, faire in ((ENS_CADRE, "cadre"), (ENS_DROITE, "droite")):
        origine = {o.path_id: tt for o, tt in _compositions(orig, ensemble)}
        actuelles = _compositions(env, ensemble)
        if not actuelles:
            msgs.append(f"{ensemble} introuvable (renommé par une mise à jour ?), ignoré")
            continue
        for o, tt in actuelles:
            ori = origine.get(o.path_id)
            if ori is None:
                continue
            comps = copy.deepcopy(ori["m_gridComponents"])
            nom = tt["m_Name"]
            taille = nom.rsplit("-", 1)[-1]   # Small / Standard / Large
            if not retirer:
                if faire == "cadre":
                    r = _cadre(comps)
                    if r:
                        rapports[taille] = r
                        msgs.append(f"{nom} : équipes {_tuile(comps, EQUIPES)['m_location']['width']} colonnes")
                elif taille in rapports:
                    r = _droite(comps, *rapports[taille])
                    if r:
                        msgs.append(f"{nom} : Équipe type des médias {r[0]} colonnes, transferts {r[1]}")
            if tt["m_gridComponents"] != comps:
                tt["m_gridComponents"] = comps
                o.save_typetree(tt)
                change = True
                if retirer:
                    msgs.append(f"{nom} : d'origine")
    if change:
        _ecrire(env, TUILES, msgs)
    elif not retirer:
        msgs.append("grilles de la présentation de saison : déjà appliquées")
    return msgs


# ---------- commandes ----------
def cmd_appliquer():
    global EN_COURS
    if _moral_actif():   # le propriétaire repart de l'original et rappelle fabrique_appliquer (EN_COURS)
        import moral_icone_seule as mi
        EN_COURS = True
        mi.DRY_RUN = DRY_RUN
        mi.cmd_appliquer()
        EN_COURS = False
    else:
        env = UnityPy.load(FABRIQUES)
        if fabrique_appliquer(env):
            msgs = []
            _ecrire(env, FABRIQUES, msgs)
            print("\n".join(msgs))
        else:
            print(f"{FABRIQUE} : colonne Cotes déjà là")
    for m in vue(False) + grilles(False):
        print(m)
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
        print("\nPrésentation de saison : colonne Cotes et bloc des équipes élargi.")


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    env = UnityPy.load(FABRIQUES)
    if fabrique_retirer(env):
        msgs = []
        _ecrire(env, FABRIQUES, msgs)
        print("\n".join(msgs))
    for m in vue(True) + grilles(True):
        print(m)
    print("Présentation de saison d'origine remise.")


def cmd_etat():
    _, tt = _objets(UnityPy.load(FABRIQUES), FABRIQUE)
    print(f"{FABRIQUE} : colonne Cotes", "oui" if tt and any(r["m_id"] == COLONNE for r in tt["m_rowData"]) else "non")
    _, tt = _objets(UnityPy.load(VUES), VUE)
    print(f"{VUE} : colonne Cotes", "oui" if tt and any(c["m_columnID"] == COLONNE
                                                        for c in tt["m_tableView"]["m_tableConfig"]) else "non")
    env = UnityPy.load(TUILES)
    for ensemble in (ENS_CADRE, ENS_DROITE):
        for _, tt in _compositions(env, ensemble):
            print(f"{tt['m_Name']} : " + ", ".join(
                f"{c['m_elementID']} {c['m_location']['width']}" for c in tt["m_gridComponents"]))
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
            print("présentation de saison : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
