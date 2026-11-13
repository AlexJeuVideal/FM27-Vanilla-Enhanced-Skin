"""ESSAI : messages « NXGN » (50 meilleurs jeunes) et « 50 meilleurs joueurs du monde » (TopPlayersInTheWorldNews,
un seul modèle pour les deux : TopPlayersInTheWorldNewsStoryBlock) : un bouton au-dessus de la liste qui ajoute les
50 joueurs à la sélection (shortlist), pour les faire observer ensuite depuis l'écran Sélection.

Bouton = FMActionButton « Ajouter à la sélection » de FM (action 1097488485, gabarit d'actions 23461237…), copié de
l'outil Recrutement (RecruitmentFocusToolMainBlock #matched-add-to-shortlist-button, où FM le branche déjà sur une
LISTE de joueurs). Libellé = celui de l'action FM (traduit par le jeu).

v1 (2026-11-13) : RecordsBinding = `TopPlayers.Players` (liste de la grille #PlayersGrid). Inconnu : ses éléments sont
  des « joueur + rang » (playerWithRank, .Player = la personne), pas des personnes ; si FM refuse, bouton invisible.
  Aussi caché par FM si un seul joueur ne peut pas être ajouté (déjà dans la sélection ?).
Menu Outils FM.bat (jeu fermé) : 124 ; retiré par 105 / choix 1.
Usage : essai_selection_top50.py appliquer [--dry-run] | retirer
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import feliciter_coches as fc  # noqa: E402  (ouvrir, enregistrer, nommer)
from elements import src_tree, first, typ, copy_usings, plain  # noqa: E402

MODELE = "TopPlayersInTheWorldNewsStoryBlock"
VERSION = 1
NOM = "UIPickerEssaiSelectionTop50"
CLASSE = f"uipicker-essai-selection-top50-v{VERSION}"
SOURCE, BOUTON = "RecruitmentFocusToolMainBlock", "matched-add-to-shortlist-button"
LISTE = "TopPlayers.Players"
AVANT = "players-list"          # le bouton se pose juste au-dessus de la liste (#Body)


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
        return [f"{MODELE} : essai Sélection top 50 retiré"]
    return []


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    print("\n".join(fn()) or "rien à faire")


if __name__ == "__main__":
    main(sys.argv[1:])
