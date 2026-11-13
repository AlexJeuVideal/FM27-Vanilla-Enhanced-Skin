"""Messages « NXGN » (50 meilleurs jeunes) et « 50 meilleurs joueurs du monde » (news TopPlayersInTheWorldNews, un
seul modèle pour les deux : TopPlayersInTheWorldNewsStoryBlock) : un bouton au-dessus de la liste ajoute les 50
joueurs à la sélection (shortlist), pour les faire observer ensuite depuis l'écran Sélection.

Bouton = FMActionButton « Ajouter à la sélection » de FM (action 1097488485, gabarit d'actions 23461237…), copié de
l'outil Recrutement (RecruitmentFocusToolMainBlock #matched-add-to-shortlist-button, où FM le branche déjà sur une
LISTE de joueurs). Libellé = celui de l'action FM (traduit par le jeu) : pas de texte du skin.

v1 (2026-11-13, né de l'essai essai_selection_top50 v1, PAS VU EN JEU : tuile « WIP ») : RecordsBinding =
  `TopPlayers.Players` (liste de la grille #PlayersGrid). Inconnu : ses éléments sont des « joueur + rang »
  (playerWithRank, .Player = la personne), pas des personnes ; si FM refuse, bouton invisible. Aussi caché par FM si
  un seul joueur ne peut pas être ajouté (déjà dans la sélection ?).
Usage : selection_top50.py appliquer | si-actif | retirer | etat [--dry-run]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import feliciter_coches as fc  # noqa: E402  (ouvrir, enregistrer)
from elements import src_tree, first, typ, copy_usings, plain  # noqa: E402

MODELE = "TopPlayersInTheWorldNewsStoryBlock"
VERSION = 1
NOM = "UIPickerSelectionTop50"
CLASSE = f"uipicker-selection-top50-v{VERSION}"
SOURCE, BOUTON = "RecruitmentFocusToolMainBlock", "matched-add-to-shortlist-button"
LISTE = "TopPlayers.Players"
AVANT = "players-list"          # le bouton se pose juste au-dessus de la liste (#Body)
MARKER = os.path.join(backup.BACKUP_DIR, "selection_top50.actif")


def retirer_ecran(t):
    old = [r for r in t.walk() if t.name(r).startswith(NOM)]
    dedans = {k for r in old for k in t.walk(r) if k != r}
    for r in old:
        if r not in dedans:
            t.remove(r)
    return bool(old)


def construire(t):
    if any(CLASSE in (t.elem(r).get("m_Classes") or []) for r in t.walk() if t.name(r) == NOM):
        return []
    retirer_ecran(t)
    s = src_tree(SOURCE)
    src = s and first(s, lambda r: s.name(r) == BOUTON and typ(s, r) == "FM.UI.FMActionButton")
    liste = first(t, lambda r: t.name(r) == AVANT)
    if src is None or liste is None:
        return [f"{'bouton FM (' + SOURCE + ')' if src is None else '#' + AVANT} introuvable"]
    corps = t.parent[liste]
    rangee = plain(t, corps, t.children(corps).index(liste), ["row-direction-normal", "align-items-center", CLASSE],
                   NOM)
    t.elem(rangee)["m_RuleIndex"] = -1
    b = t.clone(src, rangee, src=s)
    copy_usings(t, s, src)
    for r in t.walk(b):
        t.elem(r)["m_RuleIndex"] = -1
    sd = t.sd(b)
    sd["name"] = ""
    sd["RecordsBinding"], sd["RecordsBinding_UxmlAttributeFlags"] = {"m_path": LISTE}, 1
    t.elem(b)["m_Classes"] = []
    return [f"bouton FM « Ajouter à la sélection » posé au-dessus de la liste ({LISTE})"]


def appliquer():
    o = fc.ouvrir(MODELE)
    if o is None:
        return [f"{MODELE} introuvable"]
    m = construire(o[3])
    if m and not any("introuvable" in x for x in m):
        fc.enregistrer(*o)
        nb.save_all()
    return [f"{MODELE} : {x}" for x in m]


def retirer():
    o = fc.ouvrir(MODELE)
    if o and retirer_ecran(o[3]):
        fc.enregistrer(*o)
        nb.save_all()
        return [f"{MODELE} : bouton « Ajouter à la sélection » retiré"]
    return []


def etat():
    o = fc.ouvrir(MODELE)
    pose = bool(o) and any(o[3].name(r) == NOM for r in o[3].walk())
    print(f"{MODELE} : bouton « Ajouter à la sélection »", "posé" if pose else "absent")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op in ("appliquer", "si-actif"):
        if op == "si-actif" and not os.path.exists(MARKER):
            print("sélection top 50 : non activé, rien à faire")
            return
        print("\n".join(appliquer()) or "rien à faire")
        if not nb.DRY_RUN:
            with open(MARKER, "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)
    elif op == "retirer":
        if os.path.exists(MARKER) and not nb.DRY_RUN:
            os.remove(MARKER)
        print("\n".join(retirer()) or "rien à faire")
    elif op == "etat":
        etat()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
