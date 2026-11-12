"""Fiche staff : Rapports avec les médias puis Réputation sous Personnalité. Infobulle staff : Personnalité, Rapports
avec les médias, Réputation sous la liste des postes.

Repérage par contenu (noms FM, chemins de données) : valable après une mise à jour du jeu.
Usage (jeu fermé) : staff_fiche.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import os
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
STAFF_MEDIAS_ET_REPUTATION = True            # fiche staff : sous Personnalité
INFOBULLE_STAFF = True                       # infobulle staff : Personnalité, médias, réputation sous les postes
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "staff_fiche.actif")
GROS_BLOC = "PlayerAttributesLargeBlock"
STAFF = "NonPlayerAttributesBlock"
STAFF_INFOBULLE = "NonPlayerAttributesBlock_Tooltip"
VERSION_STAFF_INFOBULLE = "uipicker-staff-infobulle-v3"   # changer le numéro refait le bloc de l'infobulle
NOM_STAFF_MEDIAS = "UIPickerStaffMedias"
NOM_STAFF_REPUTATION = "UIPickerStaffReputation"
NOM_STAFF_BLOC = "UIPickerStaffInfos"


# ---------- 4. fiche staff ----------
def staff_infos(t):
    if named(t, NOM_STAFF_BLOC):
        return []
    redo = bool(named(t, NOM_STAFF_MEDIAS))
    for r in named(t, NOM_STAFF_MEDIAS) + named(t, NOM_STAFF_REPUTATION):   # ancienne version (lignes éparpillées)
        t.remove(r)
    pers = first(t, lambda r: t.name(r) == "personality")
    big = src_tree(GROS_BLOC)
    personal = src_tree("PersonPersonalBlock")
    rep_frame = first(big, lambda r: big.name(r) == "PlayerReputationTextFrame") if big else None
    media_title = first(personal, lambda r: personal.name(r) == "MediaHandlingStyleFrameText") if personal else None
    if None in (pers, rep_frame, media_title):
        return ["Personnalité / Réputation / Style médiatique introuvables, ignoré"]
    # la colonne répartit ses éléments sur toute la hauteur : Personnalité, Médias et Réputation vont dans un
    # seul bloc, espacés comme dans la fiche joueur (titre, petit écart, valeur ; écart normal entre les lignes)
    outer = t.parent[pers]
    box = plain(t, outer, t.children(outer).index(pers), ["column-direction-normal", "align-items-start"], NOM_STAFF_BLOC)
    move(t, pers, box)
    staff_rows(t, pers, big, rep_frame, personal, media_title)
    return [("lignes regroupées : " if redo else "") + "Rapports avec les médias + Réputation sous Personnalité"]


def staff_tooltip(t):
    """infobulle staff (liste du staff...) : Personnalité, Rapports avec les médias, Réputation sous la liste des
    postes, copiés de la fiche staff (même contexte "person")"""
    old = named(t, NOM_STAFF_BLOC)
    if any(VERSION_STAFF_INFOBULLE in (t.elem(r).get("m_Classes") or []) for r in old):
        return []
    for r in old:   # version précédente : on refait
        t.remove(r)
    roles = first(t, lambda r: t.name(r) == "staff-role")
    div_model = first(t, lambda r: "layout-layout-divider-solid-horizontal" in (t.elem(r).get("m_Classes") or []))
    s = src_tree(STAFF)
    pers_src = first(s, lambda r: s.name(r) == "personality") if s else None
    big = src_tree(GROS_BLOC)
    personal = src_tree("PersonPersonalBlock")
    rep_frame = first(big, lambda r: big.name(r) == "PlayerReputationTextFrame") if big else None
    media_title = first(personal, lambda r: personal.name(r) == "MediaHandlingStyleFrameText") if personal else None
    if None in (roles, div_model, pers_src, rep_frame, media_title):
        return ["liste des postes / trait / Personnalité / Réputation / Style médiatique introuvables, ignoré"]
    # étiré à la largeur de la colonne des postes (180 px) : les textes longs passent à la ligne au lieu de
    # déborder sur les attributs ; le trait suit la liste des postes (sa longueur dépend du type de staff)
    box = plain(t, roles, None, ["column-direction-normal", "align-items-stretch", "align-self-stretch",
                                 VERSION_STAFF_INFOBULLE], NOM_STAFF_BLOC)
    t.elem(box)["m_RuleIndex"] = -1   # plain() recopie le style intégré de son modèle (#main-block : largeur 798 px)
    d = t.clone_shallow(div_model, box)
    t.sd(d)["name"] = ""
    t.elem(d)["m_Classes"] = ["layout-layout-divider-solid-horizontal", "margin-vertical-global-gap-large"]
    pers = t.clone(pers_src, box, src=s)
    no_styles(t, pers)
    staff_rows(t, pers, big, rep_frame, personal, media_title, wrap=True)
    return ["trait + Personnalité + Rapports avec les médias + Réputation sous la liste des postes"
            + (" (refait)" if old else "")]


def staff_rows(t, pers, big, rep_frame, personal, media_title, wrap=False):
    """pers (Personnalité, dans son bloc) : espacements, puis Rapports avec les médias et Réputation à la suite.
    wrap : les textes passent à la ligne (colonne étroite)"""
    rep_title, rep_value = big.children(rep_frame)[:2]
    parent = t.parent[pers]
    i = t.children(parent).index(pers)
    t.elem(pers)["m_Classes"] = [c for c in t.elem(pers).get("m_Classes") or [] if not c.startswith("margin-")] \
        + ["margin-bottom-global-gap-large"]
    head = t.children(pers)[0]
    if "margin-bottom-global-gap-small" not in (t.elem(head).get("m_Classes") or []):
        t.elem(head)["m_Classes"] = (t.elem(head).get("m_Classes") or []) + ["margin-bottom-global-gap-small"]
    for k, (nm, title_b, value_b) in enumerate([
            (NOM_STAFF_MEDIAS, personal.sd(media_title)["TextBinding"],
             {"m_kind": 1, "m_direct": {"Path": {"m_path": "Person.MediaHandling"}, "Nullable": 0},
              "m_visualFunction": copy.deepcopy(personal.sd(media_title)["TextBinding"]["m_visualFunction"])}),
            (NOM_STAFF_REPUTATION, big.sd(rep_title)["TextBinding"], big.sd(rep_value)["TextBinding"])]):
        new = t.clone(pers, parent, i + 1 + k)
        t.sd(new)["name"] = nm
        last = nm == NOM_STAFF_REPUTATION
        t.elem(new)["m_Classes"] = [c for c in t.elem(new).get("m_Classes") or [] if not c.startswith("margin-")] \
            + ([] if last else ["margin-bottom-global-gap-large"])
        head, val = t.children(new)[:2]
        set_text_binding(t, head, title_b)
        vb = copy.deepcopy(value_b)
        if vb.get("m_kind") == 1:
            vb["m_visualFunction"]["m_target"]["m_guid"] = ""
            vb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
        set_text_binding(t, val, vb)
    if wrap:
        for row in t.children(parent)[i:i + 3]:
            for txt in t.children(row)[:2]:
                cls = [c for c in t.elem(txt).get("m_Classes") or [] if c not in ("content-no-wrap", "content-ellipsis")]
                t.elem(txt)["m_Classes"] = cls + ["content-wrap"]

def jobs():
    lst = []
    if STAFF_MEDIAS_ET_REPUTATION:
        lst.append((STAFF, staff_infos))
    if INFOBULLE_STAFF:
        lst.append((STAFF_INFOBULLE, staff_tooltip))
    return lst


def cmd_etat():
    for model in [STAFF, STAFF_INFOBULLE]:
        _, _, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable")
            continue
        t = Tree(tt)
        have = [n for n in (NOM_STAFF_MEDIAS, NOM_STAFF_REPUTATION, NOM_STAFF_BLOC) if named(t, n)]
        print(f"{model} : " + (", ".join(have) if have else "rien"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        appliquer_jobs(jobs(), MARKER)
    elif op == "retirer":
        lancer.retirer_par_restauration(MARKER)   # ajouts retirés en remettant les modèles d'origine
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            appliquer_jobs(jobs(), MARKER)
        else:
            print("ajouts de la fiche staff : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
