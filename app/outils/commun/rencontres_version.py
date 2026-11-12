"""Option « rencontres » (options.py) : Calendrier > Rencontres en version Kinito (choix de base depuis le 2026-11-12)
ou en version du skin.

Version du skin : rangée d'équipes à droite d'« Organiser amical » (entrainement_equipes) et colonnes Stade /
Spectateurs dans la liste de FM (rencontres_stade_spectateurs).
Version Kinito : deux scripts de Kinito, gardés tels quels dans outils\\kinito\\ :
- kinito_rencontres_boutons (26.2) : boutons des équipes dans le bandeau du programme ; la rangée du skin de cet onglet
  n'est alors pas posée (entrainement_equipes lit kinito()) ;
- kinito_rencontres_vues (26.9) : le programme en tableau FM (vues perso, 12 colonnes, filtre) à la place de la liste de
  FM et des colonnes Stade / Spectateurs (petite fenêtre : la liste de FM et les colonnes restent).

L'option est portée par rencontres_stade_spectateurs (passe en dernier au choix 1) : sa fonction pas activée = version
du skin. accorder() met le jeu d'accord avec l'option, un processus par script (un passage par modèle) :
- Kinito : entrainement_equipes (rangée retirée de l'onglet), puis 26.2, puis 26.9 (bloc partagé, après 26.2) ;
- skin : si un ajout Kinito est posé (marqueur backups\\kinito_rencontres_*.actif), 26.9 puis 26.2 retirés, puis
  entrainement_equipes (rangée remise).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402
import options  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402

OPTION = "rencontres"
SCRIPTS_KINITO = ["kinito_rencontres_boutons", "kinito_rencontres_vues"]   # ordre d'application (retrait : à l'envers)
PORTEUR = os.path.join(backup.BACKUP_DIR, "rencontres_stade_spectateurs.actif")
EQUIPES = os.path.join(chemins.OUTILS, "entrainement", "entrainement_equipes.py")


def kinito():
    """version Kinito voulue : option sur « kinito » et fonction porteuse activée"""
    return options.get(OPTION) == "kinito" and os.path.exists(PORTEUR)


def _lancer(chemin, *args):
    sys.stdout.flush()
    return subprocess.run([sys.executable, chemin] + list(args)).returncode


def _kinito(nom):
    return os.path.join(chemins.OUTILS, "kinito", nom + ".py")


def accorder(dry_run=False):
    dr = ["--dry-run"] if dry_run else []
    if kinito():
        print("\nRencontres : version Kinito (option)")
        _lancer(EQUIPES, "si-actif", *dr)
        for nom in SCRIPTS_KINITO:
            _lancer(_kinito(nom), "appliquer", *dr)
        return
    poses = [n for n in SCRIPTS_KINITO if os.path.exists(os.path.join(backup.BACKUP_DIR, n + ".actif"))]
    if not poses:
        return
    print("\nRencontres : retour à la version du skin (ajouts Kinito retirés)")
    for nom in reversed(SCRIPTS_KINITO):
        _lancer(_kinito(nom), "retirer", *dr)
    _lancer(EQUIPES, "si-actif", *dr)
