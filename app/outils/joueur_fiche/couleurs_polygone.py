"""Chiffres du POLYGONE (fiche, infobulle, vue FM Guru) = mêmes couleurs et mêmes seuils que les attributs des joueurs.

FM colore les chiffres du polygone avec sa propre table (binding.SpiderChartPointColour). Ce script fait appeler à
l'étiquette du polygone la fonction de couleur du texte des attributs (celle d'AttributeBadge), avec la note du point
en entrée (binding.SubjectStatValue) : les couleurs et les seuils se changent DANS LE JEU (couleurs des attributs) et
le polygone suit, comme le staff (staff\\couleurs_staff_comme_joueurs.py, même mécanique).

Seuls les chiffres changent : la forme du polygone est dessinée par le code de FM.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\couleurs_polygone.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\couleurs_polygone.py retirer
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\couleurs_polygone.py etat
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)
import sauvegarde_originaux as backup  # noqa: E402
import couleurs_staff_comme_joueurs as cs  # noqa: E402  (arguments des fonctions visuelles, couleurs des joueurs)

# étiquettes du polygone de FM (LabelsTemplate de FMSpiderChart ; le skin recopie aussi le 10px dans la vue FM Guru)
MODELES = ["SpiderChartColourGradedLabel_10px", "SpiderChartColourGradedLabel_18px"]
COULEUR_FM = "binding.SpiderChartPointColour"   # entrée de la fonction de couleur d'origine
NOTE = "binding.SubjectStatValue"               # note du point (texte « Value » du modèle)
MARKER = os.path.join(backup.BACKUP_DIR, "couleurs_polygone.actif")


def setters(tt):
    """[data] : SIStyleSetter de couleur d'origine du polygone dans ce modèle"""
    res = []
    for r in tt["references"]["RefIds"]:
        d = r.get("data") or {}
        fn = cs.bind_fn(d)
        if not fn:
            continue
        try:
            args = cs.parse_args(fn["m_inputs"]["m_variable"]["m_argumentBytes"])
        except Exception:
            continue
        if any(cs.arg_string(a) == COULEUR_FM for a in args):
            res.append(d)
    return res


def cmd_appliquer():
    guid, args = cs.source_functions()["texte"]
    nouveaux = [cs.with_string(a, NOTE) if cs.arg_string(a) == cs.SOURCE_INPUT else a for a in args]
    changed = 0
    for model in MODELES:
        bundle, obj, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        trouves = setters(tt)
        if not trouves:
            print(f"{model} : " + ("déjà appliqué" if cs.already_done(tt, {guid}) else
                                   "aucune couleur du polygone trouvée, ignoré"))
            continue
        for d in trouves:
            fn = cs.bind_fn(d)
            fn["m_target"]["m_guid"] = guid
            fn["m_inputs"]["m_variable"]["m_argumentBytes"] = cs.build_args(nouveaux)
            print(f"{model} : couleur du chiffre  ->  couleur du texte des attributs, note = {NOTE}")
            changed += 1
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    if changed:
        nb.save_all()
        if not nb.DRY_RUN:
            with open(MARKER, "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)
            print("\nChiffres du polygone = couleurs des attributs. Elles se règlent dans le jeu.")
    else:
        print("rien à changer")


def cmd_retirer():
    """remet les modèles d'origine puis refait tout le reste du skin (qui touche les mêmes fichiers)"""
    import lancer
    lancer.retirer_par_restauration(MARKER)
    print("\nCouleurs d'origine du polygone remises.")


def cmd_etat():
    guid = cs.source_functions()["texte"][0]
    for model in MODELES:
        _, _, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable")
        else:
            print(f"{model} : " + ("couleurs des attributs" if cs.already_done(tt, {guid}) else "couleurs de FM"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":   # utilisé par le menu après une mise à jour
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("couleurs du polygone : non activées, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
