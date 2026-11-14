"""Messages « NXGN » (50 meilleurs jeunes) et « 50 meilleurs joueurs du monde » (news TopPlayersInTheWorldNews, un
seul modèle pour les deux : TopPlayersInTheWorldNewsStoryBlock, cartes TopPlayerRow) : un bouton « Ajouter à la
sélection » sous chaque joueur, un clic = ajouté à la sélection (shortlist).

Bouton = FMActionButton « Ajouter à la sélection » de FM (action 1097488485, gabarit d'actions 23461237…), copié de
l'outil Recrutement (RecruitmentFocusToolMainBlock #matched-add-to-shortlist-button). Libellé = celui de l'action FM
(traduit par le jeu) : pas de texte du skin.

v1 (2026-11-13) : un bouton au-dessus de la liste, RecordsBinding `TopPlayers.Players` : INVISIBLE en jeu (2026-11-14,
  essai A / B : FM refuse les éléments « joueur + rang », accepte `playerWithRank.Player`). Retiré par la v2.
v2 (2026-11-14) : bouton en bas de chaque carte (TopPlayerRow, utilisée seulement par ce message), RecordsBinding
  `playerWithRank.Player`, ShowOnlyFirstButton (sans la flèche des durées : 1er choix = Indéfiniment ?) ; la carte
  passe en hauteur auto (#player) et le bas (#2ndHalf) en flex 0 0 auto : sinon nom / club / âge écrasés.
  VU : cartes OK, mais la flèche reste et un clic sur le texte ouvre aussi le menu des durées.
v3 (2026-11-14) : gabarit d'actions ActionsListSplitLeftWidget (c2457fe0…, celui du #PrimaryAction du bouton divisé
  de FM, ActionSplitButtonWidget, avec ShowOnlyFirstButton) au lieu d'ActionsListRegularWidget : espoir = un seul
  bouton qui fait la 1re durée (Indéfiniment) en un clic.
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
import moteur_photos as mp  # noqa: E402  (ouvrir depuis l'original, original)
from elements import src_tree, first, typ, copy_usings, plain  # noqa: E402

CARTE = "TopPlayerRow"
ANCIEN = "TopPlayersInTheWorldNewsStoryBlock"   # v1 : bouton au-dessus de la liste, seulement à retirer
MODELES = [CARTE, ANCIEN]
VERSION = 3
GABARIT = "c2457fe00d1f4526b3f9db9cd9513a93"   # ActionsListSplitLeftWidget
NOM = "UIPickerSelectionTop50"
CLASSE = f"uipicker-selection-top50-v{VERSION}"
SOURCE, BOUTON = "RecruitmentFocusToolMainBlock", "matched-add-to-shortlist-button"
JOUEUR = "playerWithRank.Player"
MARKER = os.path.join(backup.BACKUP_DIR, "selection_top50.actif")
HAUTEUR, FLEX, FLEX_GROW, FLEX_SHRINK, FLEX_BASIS = 131087, 262149, 131084, 131085, 131082
MOT_CLE, AUTO, NOMBRE = 1, 2, 2


def retirer_ecran(t):
    old = [r for r in t.walk() if t.name(r).startswith(NOM)]
    dedans = {k for r in old for k in t.walk(r) if k != r}
    for r in old:
        if r not in dedans:
            t.remove(r)
    return bool(old)


def _regle(st, t, rid, enlever, ajouter):
    """style intégré de rid : propriétés `enlever` ôtées, `ajouter` [(id, [(type, valeur)])] posées"""
    e = t.elem(rid)
    old = st.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    ids = set(enlever) | {i for i, _ in ajouter}
    e["m_RuleIndex"] = st.add_rule([p for p in old if p[0] not in ids] + [(i, "", v) for i, v in ajouter])


def construire(t, st):
    s = src_tree(SOURCE)
    src = s and first(s, lambda r: s.name(r) == BOUTON and typ(s, r) == "FM.UI.FMActionButton")
    carte = first(t, lambda r: t.name(r) == "player")
    bas = first(t, lambda r: t.name(r) == "2ndHalf")
    if src is None or carte is None or bas is None:
        return [f"{'bouton FM (' + SOURCE + ')' if src is None else '#player / #2ndHalf'} introuvable"]
    retirer_ecran(t)
    rangee = plain(t, carte, len(t.children(carte)), ["row-direction-normal", "align-items-center",
                                                       "justify-content-center", CLASSE], NOM)
    t.elem(rangee)["m_RuleIndex"] = -1
    b = t.clone(src, rangee, src=s)
    copy_usings(t, s, src)
    for r in t.walk(b):
        t.elem(r)["m_RuleIndex"] = -1
    sd = t.sd(b)
    sd["name"] = ""
    sd["RecordsBinding"], sd["RecordsBinding_UxmlAttributeFlags"] = {"m_path": JOUEUR}, 1
    sd["ShowOnlyFirstButton"], sd["ShowOnlyFirstButton_UxmlAttributeFlags"] = 1, 1
    sd["ActionsListWidget"] = {"m_AssetGUID": GABARIT, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["ActionsListWidget_UxmlAttributeFlags"] = 1
    t.elem(b)["m_Classes"] = []
    # carte à la hauteur de son contenu (sinon le bouton écrase nom / club / âge)
    _regle(st, t, carte, [], [(HAUTEUR, [(MOT_CLE, AUTO)])])
    _regle(st, t, bas, [FLEX], [(FLEX_GROW, [(NOMBRE, 0.0)]), (FLEX_SHRINK, [(NOMBRE, 0.0)]),
                                (FLEX_BASIS, [(MOT_CLE, AUTO)])])
    return ["bouton FM « Ajouter à la sélection » sous chaque joueur"]


def _pose(t):
    return any(CLASSE in (t.elem(r).get("m_Classes") or []) for r in t.walk() if t.name(r) == NOM)


def _ecrire(bundle, obj, tt, t):
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def appliquer():
    out = []
    o = fc.ouvrir(ANCIEN)
    if o and retirer_ecran(o[3]):
        fc.enregistrer(*o)
        out.append(f"{ANCIEN} : ancien bouton au-dessus de la liste (v1) retiré")
    o = mp.ouvrir(CARTE)
    if o is None:
        out.append(f"{CARTE} introuvable")
    elif not _pose(o[3]):
        o = mp.ouvrir(CARTE, depart_original=True)   # seul propriétaire de la carte : repartir de l'original
        m = construire(o[3], o[3].styles)
        if m and not any("introuvable" in x for x in m):
            _ecrire(*o)
        out += [f"{CARTE} : {x}" for x in m]
    if any("introuvable" not in x for x in out):
        nb.save_all()
    return out


def retirer():
    out = []
    o = fc.ouvrir(ANCIEN)
    if o and retirer_ecran(o[3]):
        fc.enregistrer(*o)
        out.append(f"{ANCIEN} : bouton « Ajouter à la sélection » (v1) retiré")
    o = mp.ouvrir(CARTE)
    if o and any(o[3].name(r) == NOM for r in o[3].walk()):
        bundle, obj, _, _ = o
        orig = mp.original(bundle, obj)
        if orig is None:
            out.append(f"{CARTE} : pas de sauvegarde d'origine, rien fait")
        else:
            o = mp.ouvrir(CARTE, depart_original=True)
            _ecrire(*o)
            out.append(f"{CARTE} : boutons « Ajouter à la sélection » retirés, carte d'origine")
    if any("rien fait" not in x for x in out):
        nb.save_all()
    return out


def etat():
    o = fc.ouvrir(CARTE)
    pose = bool(o) and any(o[3].name(r) == NOM for r in o[3].walk())
    print(f"{CARTE} : bouton « Ajouter à la sélection »", "posé" if pose else "absent")
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
