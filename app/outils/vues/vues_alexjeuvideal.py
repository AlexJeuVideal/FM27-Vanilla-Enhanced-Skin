"""Vues de tableaux d'AlexJeuVideal (optimisées pour l'affichage Small) : de base (2026-10-31), page Features additionnelles.

Les vues perso de FM27 sont des fichiers .json dans LocalLow\\Sports Interactive\\Football Manager 27\\<Collection>\\
(un dossier par type de tableau ; le nom du fichier = le nom affiché dans le menu des vues). Ce script y COPIE nos
vues (outils\\vues\\fichiers\\<Collection>\\*.json) : aucun fichier du jeu n'est touché.

- Une vue du joueur du même nom (contenu différent, pas posée par nous) n'est jamais écrasée.
- Une vue posée par nous et pas modifiée depuis est mise à jour ; retirer = effacer seulement celles-là.
  (empreintes de ce qu'on a posé : backups\\vues_alexjeuvideal.json)

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\vues\\vues_alexjeuvideal.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\vues\\vues_alexjeuvideal.py retirer
  .venv\\Scripts\\python.exe outils\\vues\\vues_alexjeuvideal.py etat
"""
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import sauvegarde_originaux as backup  # noqa: E402
import chemin_jeu  # noqa: E402

DRY_RUN = "--dry-run" in sys.argv
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fichiers")
# dossier des vues de FM (variable UIPICKER_VUES : banc d'essai ; Linux : dans le préfixe Proton)
CIBLE = os.environ.get("UIPICKER_VUES") or chemin_jeu.donnees_fm()   # Mac : ~/Library/Application Support/...
MARKER = os.path.join(backup.BACKUP_DIR, "vues_alexjeuvideal.actif")
POSEES = os.path.join(backup.BACKUP_DIR, "vues_alexjeuvideal.json")   # {chemin relatif : empreinte posée}


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def nos_vues():
    """{chemin relatif (Collection\\nom.json) : chemin source}"""
    out = {}
    for d, _, fichiers in os.walk(SOURCE):
        for f in fichiers:
            if f.lower().endswith(".json"):
                p = os.path.join(d, f)
                out[os.path.relpath(p, SOURCE)] = p
    return out


def lire_posees():
    try:
        with open(POSEES, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def ecrire_posees(d):
    if DRY_RUN:
        return
    if d:
        with open(POSEES, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    elif os.path.exists(POSEES):
        os.remove(POSEES)


def effacer_si_notre(rel, empreinte):
    """efface la vue rel si elle est encore celle qu'on a posée ; True si effacée"""
    p = os.path.join(CIBLE, rel)
    if not os.path.exists(p):
        return False
    if sha(p) != empreinte:
        print(f"{rel} : modifiée dans le jeu depuis, gardée")
        return False
    if not DRY_RUN:
        os.remove(p)
    print(f"{rel} : retirée")
    return True


def cmd_appliquer():
    if not os.path.isdir(CIBLE):
        sys.exit(f"dossier des vues de FM introuvable : {CIBLE} (lancer FM une fois)")
    posees = lire_posees()
    vues = nos_vues()
    poses = gardes = 0
    for rel, src in sorted(vues.items()):
        dst = os.path.join(CIBLE, rel)
        neuf = sha(src)
        if os.path.exists(dst):
            actuel = sha(dst)
            if actuel == neuf:   # déjà là à l'identique ; pas posée par nous = celle du joueur (jamais effacée)
                continue
            if posees.get(rel) != actuel:   # pas posée par nous (ou modifiée depuis) : vue du joueur
                print(f"{rel} : une vue du même nom existe déjà, gardée (la nôtre n'est pas posée)")
                gardes += 1
                continue
        if not DRY_RUN:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
        posees[rel] = neuf
        print(f"{rel} : posée")
        poses += 1
    # vues retirées du skin depuis une version précédente
    for rel in [r for r in posees if r not in vues]:
        effacer_si_notre(rel, posees[rel])
        del posees[rel]
    ecrire_posees(posees)
    deja = len(vues) - poses - gardes
    print(f"{poses} vue(s) posée(s), {deja} déjà en place, {gardes} gardée(s)")
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    posees = lire_posees()
    n = sum(effacer_si_notre(rel, posees[rel]) for rel in sorted(posees))
    ecrire_posees({})
    print(f"{n} vue(s) d'AlexJeuVideal retirée(s) (tes vues à toi ne sont pas touchées)")


def cmd_etat():
    posees = lire_posees()
    for rel in sorted(nos_vues()):
        p = os.path.join(CIBLE, rel)
        print(f"{rel} : " + ("absente" if not os.path.exists(p) else "posée" if posees.get(rel) == sha(p)
                             else "vue du joueur du même nom (gardée)"))
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
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("vues d'AlexJeuVideal : non activées, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
