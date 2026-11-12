"""Entraînement individuel : Féliciter / Critiquer / Rapport d'entraînement à droite des onglets Attributs / Rapport du
préparateur, légende (Clé / Préférables / Priorité) en bas du tableau d'attributs.

Repérage par contenu (noms FM, chemins de données) : valable après une mise à jour du jeu.
Depuis le 2026-11-12 (fusion demandée par le joueur) : l'ajout Kinito 26.16 outils\\kinito\\kinito_terrain_postes.py
(terrain des postes agrandi, sans la légende ; gardé tel quel) est lancé après ce script, dans son propre processus ;
retirer cette fonction le retire aussi. Avec 26.14 (lancé par entrainement_individuel_equipes), le groupe Féliciter /
Critiquer / Rapport est masqué (ses pouces et son onglet à la place), dans tous les modes.
Usage (jeu fermé) : entrainement_individuel_boutons.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import (Tree, named, make_visible, polygon_visible,  # noqa: E402,F401
                   polygon_button, CLASSE_SI_POLYGONE, Styles, no_styles,
                   LARGEUR_MAX, MOITIE, FIXE, PROPRIETES)
from elements import (src_tree, add_using, copy_usings, first, typ, move, plain, visible_model,  # noqa: E402,F401
                      action_buttons, set_text_binding, appliquer_jobs)
import lancer  # noqa: E402  (retirer : modèles d'origine remis puis tout le skin refait)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (True = activé, False = désactivé)
# =====================================================================================================
RAPPORT_ENTRAINEMENT = True                  # 3e bouton "Rapport d'entraînement" après Féliciter / Critiquer
BOUTONS_ENTRAINEMENT_INDIVIDUEL = True       # Entraînement individuel : légende à gauche + Féliciter / Critiquer
BOUTONS_INDIV_EN_HAUT = True                 # ... boutons à droite des onglets (False : en bas, à côté de la légende)
                                             # en bas du tableau d'attributs
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "entrainement_individuel_boutons.actif")
ENTETES_INDIV = ["IndividualTrainingPlayerHeaderContent",   # en-tête réellement affiché dans Entraîn. individuel
                 "IndividualTrainingPlayerHeaderBlock_10x1", "IndividualTrainingPlayerHeaderBlock_8x1"]
TABLEAU_INDIV = "AttributesTableTemplateIndividualTraining"   # tableau d'attributs de l'entraînement individuel
ONGLETS_INDIV = "PlayerAttributesAndCoachReportIndividualTrainingContent"   # onglets Attributs / Rapport du préparateur
NOM_BOUTONS_ONGLETS = "UIPickerBoutonsOnglets"
VERSION_LIGNE_INDIV = "uipicker-ligne-indiv-v4"
NOM_LIGNE_INDIV = "UIPickerLigneIndiv"
PERSONNE_INDIV = None   # entraînement individuel : l'écran fournit déjà "player" (son menu Actions le lit)
NOM_BOUTONS_INDIV = "UIPickerBoutonsIndiv"


# ---------- 3. entraînement individuel : boutons à droite du nom ----------
def remove_header_buttons(t):
    """anciennes versions : boutons dans l'en-tête de l'entraînement individuel (remplacés par la ligne du bas)"""
    old = named(t, NOM_BOUTONS_INDIV)
    for r in old:
        t.remove(r)
    return ["anciens boutons de l'en-tête retirés"] if old else []


def indiv_table_row(t):
    """tableau d'attributs de l'entraînement individuel : en bas, une ligne avec la légende (Clé / Préférables /
    Priorité) à gauche puis Féliciter / Critiquer en boutons longs (champ et gardiens)"""
    rows = named(t, NOM_LIGNE_INDIV)
    if any(VERSION_LIGNE_INDIV in (t.elem(r).get("m_Classes") or []) for r in rows):
        return []
    for row in rows:   # version précédente : on remet la légende à sa place puis on refait la ligne
        for key in [k for k in t.children(row) if t.elem(k).get("m_TemplateAlias") == "AttributesKey"]:
            move(t, key, t.parent[row], t.children(t.parent[row]).index(row))
        t.remove(row)
    switch = first(t, lambda r: t.name(r) == "IsGoalkeeperSwitch")
    keys = [r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == "AttributesKey"]
    if switch is None or not keys:
        return ["légende ou tableau introuvable, ignoré"]
    for key in keys:
        branch = key   # version champ / gardien : l'enfant du switch qui contient la légende
        while t.parent.get(branch) != switch:
            branch = t.parent[branch]
        row = plain(t, branch, None, ["row-direction-normal", "align-items-center", "align-self-stretch",
                                      "margin-top-global-gap-regular", VERSION_LIGNE_INDIV], NOM_LIGNE_INDIV)
        move(t, key, row)
        t.elem(key)["m_Classes"] = ["margin-right-global-gap-large"]
        t.styles.style(t, key, FIXE)
        if not BOUTONS_INDIV_EN_HAUT:
            action_buttons(t, row, None, [], long=True, person=PERSONNE_INDIV, rapport=RAPPORT_ENTRAINEMENT)
    what = "légende seule" if BOUTONS_INDIV_EN_HAUT else "légende à gauche + Féliciter / Critiquer / Rapport"
    return [what + " en bas du tableau" + (" (refait)" if rows else "")]


def indiv_tab_buttons(t):
    """entraînement individuel : Féliciter / Critiquer / Rapport d'entraînement dans la ligne des onglets
    (à droite de Attributs / Rapport du préparateur, avant le lien Rapport de progrès)"""
    if named(t, NOM_BOUTONS_ONGLETS):
        return []
    tabs = first(t, lambda r: t.name(r) == "TabRow")
    if tabs is None or not t.children(tabs):
        return ["ligne des onglets introuvable, ignoré"]
    action_buttons(t, tabs, 1, ["margin-horizontal-global-gap-large"], NOM_BOUTONS_ONGLETS, long=True,
                   person=PERSONNE_INDIV, rapport=RAPPORT_ENTRAINEMENT)
    return ["Féliciter / Critiquer / Rapport à droite des onglets"]

def jobs():
    lst = [(m, remove_header_buttons) for m in ENTETES_INDIV]
    if BOUTONS_ENTRAINEMENT_INDIVIDUEL:
        lst.append((TABLEAU_INDIV, indiv_table_row))
        if BOUTONS_INDIV_EN_HAUT:
            lst.append((ONGLETS_INDIV, indiv_tab_buttons))
    return lst


def cmd_etat():
    for model in ENTETES_INDIV + [TABLEAU_INDIV, ONGLETS_INDIV]:
        _, _, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable")
            continue
        t = Tree(tt)
        have = [n for n in (NOM_BOUTONS_INDIV, NOM_LIGNE_INDIV, NOM_BOUTONS_ONGLETS) if named(t, n)]
        print(f"{model} : " + (", ".join(have) if have else "rien"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


KINITO = os.path.join(chemins.OUTILS, "kinito", "kinito_terrain_postes.py")   # 26.16, fusionné le 2026-11-12
MARKER_KINITO = os.path.join(backup.BACKUP_DIR, "kinito_terrain_postes.actif")


def _kinito(*args):
    sys.stdout.flush()
    return subprocess.run([sys.executable, KINITO, *args, *(["--dry-run"] if nb.DRY_RUN else [])]).returncode


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        appliquer_jobs(jobs(), MARKER)
        _kinito("appliquer")   # terrain des postes (déjà appliqué s'il est à jour)
    elif op == "retirer":
        if os.path.exists(MARKER_KINITO):
            _kinito("retirer")
        lancer.retirer_par_restauration(MARKER)   # ajouts retirés en remettant les modèles d'origine
    elif op == "etat":
        cmd_etat()
        if os.path.exists(MARKER_KINITO):
            _kinito("etat")
    elif op == "si-actif":
        if os.path.exists(MARKER):
            appliquer_jobs(jobs(), MARKER)
            _kinito("appliquer")
        else:
            print("boutons de l'entraînement individuel : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
