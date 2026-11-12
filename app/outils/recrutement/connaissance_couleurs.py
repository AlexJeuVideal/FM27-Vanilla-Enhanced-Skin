"""Niveaux de connaissance en couleurs (2026-11-10, demande du joueur à la place d'une carte du monde).

FM colore le niveau de connaissance (Recrutement > tuile « Connaissance du monde » : pays et régions ; connaissance
des recruteurs…) par 10 classes de style (KnowledgeLevelDataCollection : valeur 0-100, paliers 5/10/15/20/25/30/45/
60/80/100), dont 5 en blanc (Exceptionnel, Superbe… selon la valeur). Ici : une échelle rouge (basique) -> vert
(inégalée), une couleur par palier (couleurs_interface.CONNAISSANCE).

Fichier : les 2 bundles de styles appartiennent à couleurs_interface (et theme_fond, qui passe par lui) : ce script
pose seulement son marqueur puis fait réécrire les styles par couleurs_interface.ecrire_styles(), qui ajoute les
règles tant que le marqueur existe. Retirer = marqueur enlevé + styles réécrits (le reste des couleurs gardé).

Menu Outils FM.bat : 27 (catégorie Recrutement), puis la fonction ; réappliqué par le choix 1.
Usage : connaissance_couleurs.py appliquer | retirer | etat | si-actif [--dry-run]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import couleurs_interface as ci  # noqa: E402

DRY_RUN = "--dry-run" in sys.argv


def cmd_appliquer():
    ci.connaissance_active = lambda: True   # aussi à blanc (marqueur pas encore écrit)
    ci.ecrire_styles()
    if not DRY_RUN:
        with open(ci.CONNAISSANCE_MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
    print("niveaux de connaissance : " + ", ".join(f"{k.split('_', 4)[-1]} {c}" for k, c in ci.CONNAISSANCE.items()))


def cmd_retirer():
    if not os.path.exists(ci.CONNAISSANCE_MARKER):
        print("niveaux de connaissance : rien à retirer")   # styles refaits depuis l'original par couleurs_interface
        return
    if not DRY_RUN:
        os.remove(ci.CONNAISSANCE_MARKER)
    ci.connaissance_active = lambda: False
    ci.ecrire_styles()
    print("niveaux de connaissance : couleurs de FM")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        print("niveaux de connaissance :", "en couleurs (skin)" if os.path.exists(ci.CONNAISSANCE_MARKER) else "FM")
    elif op == "si-actif":
        if os.path.exists(ci.CONNAISSANCE_MARKER):
            cmd_appliquer()
        else:
            print("niveaux de connaissance : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
