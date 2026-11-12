"""Entraînement > Entraîn. individuel : pouces Féliciter / Critiquer à droite de la note, dans la liste des joueurs.

FM a ces colonnes dans PlayerTableFactory (« praise- / criticise-training-development-button », cellules boutons
pouce, utilisées dans les meilleurs / pires joueurs à l'entraînement), mais la liste de l'entraînement individuel
(TeamIndividualTrainingBlock) lit PlayerIndividualTrainingTableFactory : v1 (colonnes seulement dans la vue) = rien
en jeu. v2 : les deux colonnes sont recopiées dans cette fabrique (type du paramètre binding de cette fabrique),
puis ajoutées aux vues de la liste.
2026-10-30 : + réponse automatique de la conversation qui s'ouvre au clic (sujet « Niveau d'entraînement » : 1re
réponse, puis « Terminer la conversation ») : pouces_reponse_auto.py, appelé ici.
+ bouton « Féliciter les cochés » (vue Résumé, un clic, joueurs un par un) : feliciter_coches.py, appelé ici
(et par entrainement_individuel_equipes, qui refait l'écran depuis l'original).

Bundles :
- ui-tableviews : vues modifiées sur le bundle actuel ; retirer remet leur liste d'origine.
- ui-tablefactories : moral_icone_seule (propriétaire, repart de l'original) rappelle fabrique_appliquer() quand ce
  script est actif (marqueur) ; sinon ce script écrit le bundle actuel.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\entrainement\\entrainement_pouces.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\entrainement\\entrainement_pouces.py retirer
  .venv\\Scripts\\python.exe outils\\entrainement\\entrainement_pouces.py etat
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
import pouces_reponse_auto as reponse_auto  # noqa: E402
import feliciter_coches  # noqa: E402
import pouces_rapport  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
APRES = "training-rating"   # les pouces vont juste après la note à l'entraînement
# (id de colonne FM, largeur, largeur min) ; FM : 50 / 50
COLONNES = [
    ("praise-training-development-button", 44, 44),
    ("criticise-training-development-button", 44, 44),
]
# PlayerIndividualTrainingOverviewTable = liste « Détails » (nom + temps de jeu | position | note) ;
# IndividualTrainingDetailedViewTable = autre liste de l'entraînement individuel (nom + poste)
VUES = ["PlayerIndividualTrainingOverviewTable", "IndividualTrainingDetailedViewTable"]
# =====================================================================================================

BUNDLE = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
SOURCE = "PlayerTableFactory"                      # fabrique FM qui a les colonnes pouce
FABRIQUE = "PlayerIndividualTrainingTableFactory"   # fabrique de la liste de l'entraînement individuel
MARKER = os.path.join(backup.BACKUP_DIR, "entrainement_pouces.actif")
DRY_RUN = "--dry-run" in sys.argv
NOS = {c[0] for c in COLONNES}
# cellules pouces de Kinito (kinito_rapport_entrainement.CELLULES) : posées par-dessus les nôtres, à laisser
POUCES_KINITO = {"70aaa375780224b4baff5f69b5d8c699", "6d83d418fa75ed749a6c20fec10289cf"}


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


def config_origine(nom):
    orig = backup.backup_path(BUNDLE)
    if not os.path.exists(orig):
        return None
    for _, tt in monos(UnityPy.load(orig), {nom}):
        return tt["m_tableView"]["m_tableConfig"]


def _type_binding(tt):
    """type du paramètre « binding » de la fabrique cible (personne)"""
    return next((p["type"]["id"] for p in tt.get("m_parameters") or [] if p.get("name") == "binding"), None)


def fabrique_appliquer(env):
    """recopie les colonnes pouce de SOURCE dans FABRIQUE (env déjà chargé) ; True si changé"""
    src = {r["m_id"]: r for _, tt in monos(env, {SOURCE}) for r in tt["m_rowData"] if r["m_id"] in NOS}
    if set(src) != NOS:
        print(f"{SOURCE} : colonnes pouce introuvables (le jeu a changé ?), fabrique pas touchée")
        return False
    change = False
    for o, tt in monos(env, {FABRIQUE}):
        typ = _type_binding(tt)
        rows = tt["m_rowData"]
        for cid in [c[0] for c in COLONNES]:
            r = copy.deepcopy(src[cid])
            for b in r["m_valueBindings"] + r["m_footerValueBindings"]:
                if b["from"] == "binding" and typ is not None:
                    b["type"]["id"] = typ
            vieux = next((x for x in rows if x["m_id"] == cid), None)
            if vieux is not None and json.dumps(vieux) == json.dumps(r):
                continue
            if vieux is not None and vieux["m_uxmlRef"]["m_AssetGUID"] in POUCES_KINITO:
                v2 = copy.deepcopy(vieux)   # cellule remplacée par celle de Kinito (kinito_rapport_entrainement) :
                v2["m_uxmlRef"] = r["m_uxmlRef"]   # voulu, pas « à refaire » (2026-11-12 : Vérifier la signalait)
                if json.dumps(v2) == json.dumps(r):
                    continue
            if vieux is not None:
                rows.remove(vieux)
            rows.append(r)
            change = True
            print(f"{FABRIQUE} : colonne {cid} recopiée")
        if change:
            o.save_typetree(tt)
    return change


def fabrique_retirer(env):
    change = False
    for o, tt in monos(env, {FABRIQUE}):
        avant = len(tt["m_rowData"])
        tt["m_rowData"] = [r for r in tt["m_rowData"] if r["m_id"] not in NOS]
        if len(tt["m_rowData"]) != avant:
            o.save_typetree(tt)
            change = True
    return change


def ecrire_fabriques(env):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(FABRIQUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(FABRIQUES, data)


def voulue(nom, cfg_actuel):
    origine = config_origine(nom)
    cfg = copy.deepcopy(origine if origine is not None else cfg_actuel)
    cfg = [c for c in cfg if c["m_columnID"] not in NOS]
    ids = [c["m_columnID"] for c in cfg]
    if APRES not in ids:
        print(f"{nom} : colonne {APRES} introuvable, vue ignorée")
        return None
    pos = ids.index(APRES) + 1
    modele = cfg[pos - 1]
    for cid, w, wmin in COLONNES:
        c = copy.deepcopy(modele)
        c["m_columnID"] = cid
        m = c["m_columnMetadata"]
        m["m_widthOverride"], m["m_minWidthOverride"] = float(w), float(wmin)
        m["m_titleTranslationIdOverride"] = {"GameID": 0}
        m["m_sortingDisabled"] = 1
        cfg.insert(pos, c)
        pos += 1
    return cfg


def ecrire(env):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(BUNDLE)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(BUNDLE, data)


def cmd_appliquer():
    # 1. fabrique, avant les vues qui citent ses colonnes
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env):
        ecrire_fabriques(env)
    elif not any(r["m_id"] in NOS for _, tt in monos(env, {FABRIQUE}) for r in tt["m_rowData"]):
        print("rien fait")
        return
    else:
        print(f"{FABRIQUE} : colonnes déjà là")
    # 2. vues
    env = UnityPy.load(BUNDLE)
    change, vues = False, set()
    for o, tt in monos(env, set(VUES)):
        vues.add(tt["m_Name"])
        if NOS <= {c["m_columnID"] for c in tt["m_tableView"]["m_tableConfig"]}:
            # nos colonnes y sont : la vue est laissée telle quelle (Kinito la retouche ensuite : colonnes Personnalité /
            # Rapports médias, largeurs ; la refaire ici effaçait son travail et Vérifier la disait « pas à jour »)
            print(f"{tt['m_Name']} : déjà appliqué")
            continue
        cfg = voulue(tt["m_Name"], tt["m_tableView"]["m_tableConfig"])
        if cfg is None:
            continue
        if json.dumps(cfg) != json.dumps(tt["m_tableView"]["m_tableConfig"]):
            tt["m_tableView"]["m_tableConfig"] = cfg
            o.save_typetree(tt)
            change = True
            print(f"{tt['m_Name']} :", " | ".join(c["m_columnID"] for c in cfg))
        else:
            print(f"{tt['m_Name']} : déjà appliqué")
    for v in set(VUES) - vues:
        print(f"{v} : vue introuvable (le jeu a changé ?)")
    if change:
        ecrire(env)
    # 3. réponse automatique de la conversation (modèles de conversation, bundle des modèles)
    print("\n".join(reponse_auto.appliquer()) or "réponse automatique : déjà appliqué")
    # 4. bouton « Féliciter les cochés » (écran de l'entraînement individuel, bundle des modèles)
    print("\n".join(feliciter_coches.appliquer()) or "Féliciter les cochés : déjà appliqué")
    # 5. pouces du message Rapport d'entraînement (cellules de FM, gabarits de Kinito)
    print("\n".join(pouces_rapport.appliquer()) or "pouces du Rapport d'entraînement : déjà appliqué")
    if not DRY_RUN and vues:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
        print("\nPouces Féliciter / Critiquer en place dans l'entraînement individuel, réponse automatique et "
              "« Féliciter les cochés » compris.")


def cmd_retirer():
    if os.path.exists(MARKER):
        os.remove(MARKER)
    env = UnityPy.load(BUNDLE)
    change = False
    for o, tt in monos(env, set(VUES)):
        cfg = tt["m_tableView"]["m_tableConfig"]
        if not any(c["m_columnID"] in NOS for c in cfg):
            continue
        origine = config_origine(tt["m_Name"])
        tt["m_tableView"]["m_tableConfig"] = origine if origine is not None else \
            [c for c in cfg if c["m_columnID"] not in NOS]
        o.save_typetree(tt)
        change = True
        print(f"{tt['m_Name']} : liste d'origine remise")
    if change:
        ecrire(env)
    env = UnityPy.load(FABRIQUES)
    if fabrique_retirer(env):
        ecrire_fabriques(env)
        print(f"{FABRIQUE} : colonnes pouce retirées")
    for m in reponse_auto.retirer() + feliciter_coches.retirer() + pouces_rapport.retirer():
        print(m)


def cmd_etat():
    for _, tt in monos(UnityPy.load(BUNDLE), set(VUES)):
        print(f"{tt['m_Name']} :", " | ".join(c["m_columnID"] for c in tt["m_tableView"]["m_tableConfig"]))
    for _, tt in monos(UnityPy.load(FABRIQUES), {FABRIQUE}):
        nos = [r["m_id"] for r in tt["m_rowData"] if r["m_id"] in NOS]
        print(f"{FABRIQUE} : colonnes pouce :", ", ".join(nos) or "aucune")
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
            print("pouces de l'entraînement individuel : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
