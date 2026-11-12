"""Statut de tout le skin (choix 116 de Outils FM.bat) : n'affiche que ce qui n'est PAS actif ou pas à jour.

Pour chaque fonction du catalogue : pas de marqueur (backups\\<nom>.actif) = pas activée ; sinon son « si-actif » est
lancé en essai à blanc (rien n'est écrit) : s'il voudrait écrire quelque chose, la fonction est activée mais pas (ou
plus) à jour dans le jeu (après une mise à jour de FM, une nouvelle version du skin...) -> relancer le choix 1.
Lecture seule : ne modifie aucun fichier.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401
import sauvegarde_originaux as backup  # noqa: E402
from langue import texte as L  # noqa: E402
import catalogue as cat  # noqa: E402
import lancer  # noqa: E402


def ou(nom):
    """« menu 12, fonction 3 » : où la trouver dans Outils FM.bat"""
    f = cat.FONCTIONS[nom]
    i = [c[0] for c in cat.CATEGORIES].index(f["cat"])
    return f"{L('menu', 'menu')} {cat.PREMIER_NUMERO + i}, {L('fonction', 'feature')} {lancer.fonctions(f['cat']).index(nom) + 1}"


def nom_affiche(nom):
    f = cat.FONCTIONS[nom]
    c = next(x for x in cat.CATEGORIES if x[0] == f["cat"])
    return f"{L(c[1], c[2])} : {L(f['fr'], f['en'])}"


def main():
    print(L("Vérification de tout le skin (rien n'est écrit), patiente un peu...",
            "Checking the whole skin (nothing is written), please wait..."))
    pas_actives, pas_a_jour, erreurs = [], [], []
    for nom in cat.ORDRE_SKIN:
        f = cat.FONCTIONS[nom]
        print(".", end="", flush=True)
        if lancer.hors_guru(nom):   # mode FM Guru : jamais posée, rien à vérifier
            continue
        if not lancer.actif(nom):
            if not f.get("facultatif"):
                pas_actives.append(nom)
            continue
        if f.get("toujours"):
            continue
        r = subprocess.run([sys.executable, lancer.chemin_script(nom), "si-actif", "--dry-run"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        sortie = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 or "Traceback" in sortie:
            erreurs.append(nom)
        elif "essai à blanc : rien écrit" in sortie or "introuvable" in sortie:
            pas_a_jour.append(nom)
    print()
    print()
    if pas_actives:
        print(L("PAS ACTIVÉ (pas installé, et pas remis par le choix 1) :", "NOT ENABLED (not installed, and not reapplied by choice 1):"))
        for nom in pas_actives:
            print(f"   - {nom_affiche(nom)}  ->  {ou(nom)}")
        print()
    if pas_a_jour:
        print(L("ACTIVÉ MAIS PAS À JOUR dans le jeu (ou morceau de FM introuvable) -> relance le choix 1 :",
                "ENABLED BUT NOT UP TO DATE in the game (or FM part not found) -> run choice 1 again:"))
        for nom in pas_a_jour:
            print(f"   - {nom_affiche(nom)}  ({ou(nom)})")
        print()
    if erreurs:
        print(L("ERREUR pendant la vérification (dis-le) :", "ERROR during the check (report it):"))
        for nom in erreurs:
            print(f"   - {nom_affiche(nom)}  ({ou(nom)})")
        print()
    restes = lancer.restes_guru()
    if restes:
        print(L("MODE FM GURU : fonctions hors de la fiche joueur encore activées (le jeu doit rester celui de FM) -> "
                "« Réinstaller » sur la carte FM Guru (FM fermé) :",
                "FM GURU MODE: features outside the player profile still enabled (the game must stay FM's) -> "
                "« Reinstall » on the FM Guru card (FM closed):"))
        for nom in restes:
            print(f"   - {nom_affiche(nom)}")
        print()
        pas_a_jour.extend(restes)   # pas « tout est à jour »
    if not lancer.actif("theme_fond") and not lancer.hors_guru("theme_fond"):
        print(L("(Couleur du fond : pas choisie, fond de FM gardé - choix 30 si tu veux une couleur.)",
                "(Background colour: not chosen, FM background kept - choice 30 if you want a colour.)"))
    if not (pas_actives or pas_a_jour or erreurs):
        print(L("TOUT EST ACTIF ET À JOUR : tout le reste marche comme ça, rien à faire.",
                "EVERYTHING IS ENABLED AND UP TO DATE: everything works as it is, nothing to do."))
    else:
        print(L("Tout ce qui n'est pas listé ici est actif, à jour, et marche comme ça.",
                "Everything not listed here is enabled, up to date, and works as it is."))


if __name__ == "__main__":
    main()
