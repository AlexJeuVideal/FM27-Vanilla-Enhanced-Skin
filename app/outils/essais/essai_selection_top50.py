"""ESSAI : messages « NXGN » (50 meilleurs jeunes) et « 50 meilleurs joueurs du monde » (TopPlayersInTheWorldNews,
un seul modèle pour les deux : TopPlayersInTheWorldNewsStoryBlock). But : ajouter les 50 joueurs à la sélection d'un
coup. Le bouton de la fonction recrutement\\selection_top50 (RecordsBinding `TopPlayers.Players`) n'apparaît PAS en jeu
(2026-11-14) : liste de « joueur + rang » refusée, ou un joueur ne peut pas être ajouté ?

Bouton = FMActionButton « Ajouter à la sélection » de FM (action 1097488485), copié de l'outil Recrutement
(RecruitmentFocusToolMainBlock #matched-add-to-shortlist-button). Libellé = celui de l'action FM.

v1 (2026-11-13) : bouton au-dessus de la liste (devenu la fonction selection_top50).
v2 (2026-11-14) : test A / B sur chaque carte (TopPlayerRow, utilisé seulement par ce message) :
  A (EN HAUT de la carte) : RecordsBinding `playerWithRank` (l'élément « joueur + rang » de la liste) ;
  B (EN BAS de la carte)  : RecordsBinding `playerWithRank.Player` (le joueur).
  A visible -> FM accepte les « joueur + rang » : le bouton des 50 est caché par un joueur qui ne peut pas être ajouté.
  Seul B visible -> FM refuse ces éléments : pas de « 50 d'un coup » par le skin.
Menu Outils FM.bat (jeu fermé) : 124 ; retiré par 105 / choix 1.
Usage : essai_selection_top50.py appliquer [--dry-run] | retirer [--dry-run]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import feliciter_coches as fc  # noqa: E402  (ouvrir, enregistrer)
from elements import src_tree, first, typ, copy_usings, plain  # noqa: E402

MODELES = ["TopPlayerRow", "TopPlayersInTheWorldNewsStoryBlock"]   # le 2e : seulement pour retirer la v1
CARTE = "TopPlayerRow"
VERSION = 2
NOM = "UIPickerEssaiSelectionTop50"
CLASSE = f"uipicker-essai-selection-top50-v{VERSION}"
SOURCE, BOUTON = "RecruitmentFocusToolMainBlock", "matched-add-to-shortlist-button"
TESTS = [("A", "playerWithRank", 0), ("B", "playerWithRank.Player", None)]   # (nom, liaison, place dans #player)


def retirer_ecran(t):
    old = [r for r in t.walk() if t.name(r).startswith(NOM)]
    dedans = {k for r in old for k in t.walk(r) if k != r}
    for r in old:
        if r not in dedans:
            t.remove(r)
    return bool(old)


def construire(t):
    if any(CLASSE in (t.elem(r).get("m_Classes") or []) for r in t.walk() if t.name(r).startswith(NOM)):
        return []
    retirer_ecran(t)
    s = src_tree(SOURCE)
    src = s and first(s, lambda r: s.name(r) == BOUTON and typ(s, r) == "FM.UI.FMActionButton")
    carte = first(t, lambda r: t.name(r) == "player")
    if src is None or carte is None:
        return [f"{'bouton FM (' + SOURCE + ')' if src is None else '#player'} introuvable"]
    for nom, liaison, place in TESTS:
        index = len(t.children(carte)) if place is None else place
        rangee = plain(t, carte, index, ["row-direction-normal", "align-items-center", "justify-content-center",
                                         CLASSE], f"{NOM}{nom}")
        t.elem(rangee)["m_RuleIndex"] = -1
        b = t.clone(src, rangee, src=s)
        for r in t.walk(b):
            t.elem(r)["m_RuleIndex"] = -1
        sd = t.sd(b)
        sd["name"] = ""
        sd["RecordsBinding"], sd["RecordsBinding_UxmlAttributeFlags"] = {"m_path": liaison}, 1
        t.elem(b)["m_Classes"] = []
    copy_usings(t, s, src)
    return ["boutons d'essai A (haut, playerWithRank) / B (bas, playerWithRank.Player) posés sur chaque carte"]


def appliquer():
    out = []
    for modele in MODELES:
        o = fc.ouvrir(modele)
        if o is None:
            out.append(f"{modele} introuvable")
            continue
        if modele == CARTE:
            m = construire(o[3])
        else:
            m = ["essai v1 (bouton au-dessus de la liste) retiré"] if retirer_ecran(o[3]) else []
        if m and not any("introuvable" in x for x in m):
            fc.enregistrer(*o)
        out += [f"{modele} : {x}" for x in m]
    if out:
        nb.save_all()
    return out


def retirer():
    out = []
    for modele in MODELES:
        o = fc.ouvrir(modele)
        if o and retirer_ecran(o[3]):
            fc.enregistrer(*o)
            out.append(f"{modele} : essai Sélection top 50 retiré")
    if out:
        nb.save_all()
    return out


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    print("\n".join(fn()) or "rien à faire")


if __name__ == "__main__":
    main(sys.argv[1:])
