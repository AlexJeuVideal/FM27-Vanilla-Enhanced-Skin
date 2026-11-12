"""Cartes des joueurs sur les terrains (demande du joueur, 2026-10-30, « partout », « en match aussi ») : une rangée de
plus sous le nom : en bas à gauche la note moyenne des 5 derniers matchs (pastille de couleur de FM, celle de la
colonne « Forme avec valeur »), à droite la condition (cœur) puis la fatigue (icônes des tableaux de joueurs).

Cartes : tactiques (vue Combinée, En / Hors possession et compo conseillée, version tactile) et terrain du match (vue
d'ensemble, formations). Ces cartes appartiennent à photos_tactiques / photos_match (qui repartent de l'original) :
ce script travaille sur la carte telle qu'elle est et passe après elles (catalogue : ORDRE_SKIN, SUIVANTS).
Retirer = enlever la rangée (repérée par son nom).

Usage (jeu fermé) : infos_cartes_terrain.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, FIXE, make_visible  # noqa: E402
from elements import src_tree, first, typ, plain, copy_usings, visible_model  # noqa: E402
import moteur_photos as mp  # noqa: E402  (ouvrir : modèle actuel + sa feuille de style)
import tuile_forme as tf  # noqa: E402  (icônes condition / fatigue des tableaux, liées à une personne)

for k, v in {"height": (131087, 3), "padding-left": (131099, 3), "padding-right": (131100, 3),
             "margin-top": (131093, 3), "flex-direction": (131083, 7), "align-items": (131073, 7),
             "justify-content": (131088, 7), "max-height": (131094, 3), "position": (131102, 7),
             "left": (131089, 3), "right": (131103, 3), "bottom": (131080, 3), "padding-top": (131101, 3),
             "padding-bottom": (131098, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
# v1 en jeu : BEAUCOUP trop gros, et la carte de FM a une hauteur fixe (la rangée écrasait le nom) -> v2 : rangée
# en position absolue juste SOUS la carte (rien n'est poussé), plus petite, pastille recopiée en ligne (texte xs)
HAUTEUR = 13          # px de la rangée ajoutée (« étendre légèrement » le bas de la carte)
ICONE = 10            # px du cœur et de la fatigue (tableaux de FM : 16)
CASE = 12             # px de la case de chaque icône
MARGE = 2             # px à gauche / à droite dans la rangée
NOTE_LARGEUR = 24     # px mini de la pastille de note
NOTE_TEXTE = "body-xs-strong"   # classe du chiffre de la note (FM : body-sm-strong + marges haut / bas)
ICONES = ["PlayerConditionIconCell", "PlayerFatigueIconCell"]
# cartes : (modèle, chemin de la personne, repère = la rangée est posée juste après lui)
#   ".classe" = 1er élément qui porte la classe ; "#nom" = élément nommé ; ">#nom" = DANS l'élément, en dernier
#   v3 tactiques : dans la carte #tactics-draggable, comme les logos de rôle (qui dépassent et restent visibles)
CIBLES = [
    ("TacticsPositionCombined", "position.Player", ">#tactics-draggable"),
    ("TacticsPositionDetailed", "position.Player", ">#tactics-draggable"),
    ("TacticsMatchPositionFilled", "position.MatchPlayer.Person", "#Player"),
    ("FormationPositionFilled", "Position.MatchPlayer.Person", "#NameBlock"),
]
ANCIENS = ["PositionIndicatorDetails", "PositionIndicatorDetailsTouch"]   # v1 / v2 : bande retirée (retirer, appliquer)
# =====================================================================================================

NOM = "UIPickerInfosCarte"
VERSION = "uipicker-infos-carte-v3"   # changer le numéro refait la rangée (v2 : sous la carte, plus petite ;
                                      # v3 : overflow visible sur ses parents, v2 rognée)
NOTE_SOURCE = "PlayerLastFiveMatchesChartFormWithValueSmallCell"   # colonne « Forme avec valeur » : pastille de note
NOTE_CHEMIN = ".lastfivematchesform.LastFiveMatchesRating"
PASTILLE = "data_display-average_rating-default-default"   # pastille de FM, recopiée en ligne
MARKER = os.path.join(backup.BACKUP_DIR, "infos_cartes_terrain.actif")


def repere(t, rep):
    rep = rep.lstrip(">")
    if rep.startswith("#"):
        return first(t, lambda r: t.name(r) == rep[1:])
    return first(t, lambda r: rep[1:] in (t.elem(r).get("m_Classes") or []))


def nos(t):
    return [r for r in t.walk() if t.name(r) == NOM]


def source_note():
    """(arbre, BindingRemapper binding -> matchrating + pastille de FM) de la colonne Forme avec valeur"""
    s = src_tree(NOTE_SOURCE)
    rm = first(s, lambda r: typ(s, r).endswith("BindingRemapper")
               and any(m.get("from") == "binding" for m in s.sd(r).get("Mappings") or [])) if s else None
    bundle, _, ptt = nb.find_vta(PASTILLE)
    if rm is None or ptt is None:
        return None
    ps = Tree(ptt)
    return (s, rm), (ps, Styles(bundle, ptt), ps.children(ps.tt["m_VisualTree"]["rid"])[0])


def poser(t, chemin, rep, note, liaison):
    """rangée [note 5 matchs ... cœur fatigue] après le repère ; renvoie un message"""
    cible = repere(t, rep)
    vis_modele = visible_model(t)
    if cible is None or vis_modele is None:
        return f"repère {rep} introuvable"
    if rep.startswith(">"):
        parent, index = cible, None
    else:
        parent = t.parent[cible]
        index = t.children(parent).index(cible) + 1
    # visible seulement s'il y a un joueur (poste vide : rien) ; fond sur un enfant (SIVisible : fond ignoré)
    vis = make_visible(t, vis_modele, parent, index, chemin, NOM, [VERSION])
    t.sd(vis)["name_UxmlAttributeFlags"] = 1
    t.elem(vis)["m_RuleIndex"] = -1
    # sous la carte (hauteur fixe chez FM) : absolue, collée au bas, rien n'est écrasé ni poussé
    t.styles.style(t, vis, {"position": "absolute", "left": 0, "right": 0, "bottom": -HAUTEUR,
                            "height": HAUTEUR})
    # v2 en jeu : bande invisible (rognée par la carte) -> v3 : rien ne rogne entre elle et la racine de la carte
    r = parent
    while r in t.parent and not typ(t, r).endswith("UXML"):
        if not typ(t, r).endswith("Component"):
            t.styles.style(t, r, {"overflow": "visible"})
        r = t.parent[r]
    rang = plain(t, vis, None, ["row-direction-normal", "align-items-center", "background-black"])
    t.elem(rang)["m_RuleIndex"] = -1
    t.styles.style(t, rang, {"justify-content": "space-between", "height": HAUTEUR, "min-height": HAUTEUR,
                             "padding-left": MARGE,
                             "padding-right": MARGE, **FIXE})
    # à gauche : note moyenne des 5 derniers matchs
    (s, rm_note), (ps, pst, pracine) = note
    rm = t.clone(rm_note, rang, src=s)
    for k in list(t.children(rm)):   # sa pastille (modèle inclus) : remplacée par la copie en ligne
        t.remove(k)
    t.sd(rm)["name"] = ""
    for m in t.sd(rm)["Mappings"]:
        if m.get("from") == "binding":
            m["to"]["m_path"] = chemin + NOTE_CHEMIN
    t.elem(rm)["m_Classes"] = ["justify-content-center"]
    t.elem(rm)["m_RuleIndex"] = -1
    t.styles.style(t, rm, {"min-width": NOTE_LARGEUR, "height": HAUTEUR - 2, "max-height": HAUTEUR - 2, **FIXE})
    # pastille de FM recopiée en ligne (modèle inclus = ses classes intouchables) : chiffre plus petit
    p = t.clone(pracine, rm, src=ps)
    copy_usings(t, ps, pracine)
    t.styles.copy_from(pst, t, p)
    for r in t.walk(p):
        cls = t.elem(r).get("m_Classes") or []
        if typ(t, r).endswith(("SIText", "Label")):
            cls = [NOTE_TEXTE if c.startswith("body-") else c for c in cls if not c.startswith("padding-")]
        t.elem(r)["m_Classes"] = cls
        if typ(t, r).endswith(("SIStyleSetter", "VisualElement", "SIText", "Label")):
            t.styles.style(t, r, {"padding-top": 0, "padding-bottom": 0, "max-height": HAUTEUR - 2})
    # à droite : condition puis fatigue
    ic = plain(t, rang, None, ["row-direction-normal", "align-items-center"])
    t.elem(ic)["m_RuleIndex"] = -1
    t.styles.style(t, ic, FIXE)
    ns, rm_src = liaison
    err = tf.icones(t, ic, ICONES, ns, rm_src, ICONE, CASE, base=chemin)
    if err:
        return err
    return f"rangée note 5 matchs / condition / fatigue après {rep} ({chemin})"


def retirer_anciens():
    """bandes des versions passées posées dans des modèles plus ciblés : retirées ; renvoie les modèles à écrire"""
    out = []
    for modele in ANCIENS:
        o = mp.ouvrir(modele)
        if o is None or not nos(o[3]):
            continue
        for r in nos(o[3]):
            o[3].remove(r)
        print(f"{modele} : rangée retirée")
        out.append(o)
    return out


def cmd_appliquer():
    note = source_note()
    liaison = tf.sources_liaison()
    if note is None or liaison[0] is None:
        print("pastille de note ou modèle de liaison de FM introuvable (mise à jour du jeu ?) : rien fait")
        return
    a_enregistrer = retirer_anciens()
    for modele, chemin, rep in CIBLES:
        o = mp.ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable, ignoré")
            continue
        bundle, obj, tt, t = o
        vieux = nos(t)
        if any(VERSION in (t.elem(r).get("m_Classes") or []) for r in vieux):
            print(f"{modele} : déjà appliqué")
            continue
        for r in vieux:   # ancienne version
            t.remove(r)
        msg = poser(t, chemin, rep, note, liaison)
        print(f"{modele} : {msg}")
        if "introuvable" in msg or "absent" in msg:
            continue
        a_enregistrer.append(o)
    for bundle, obj, tt, t in a_enregistrer:
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    if a_enregistrer:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for modele in [c[0] for c in CIBLES] + ANCIENS:
        o = mp.ouvrir(modele)
        if o is None or not nos(o[3]):
            continue
        bundle, obj, tt, t = o
        for r in nos(t):
            t.remove(r)
        t.finish()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        fait = True
        print(f"{modele} : rangée retirée")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele, *_ in CIBLES:
        o = mp.ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
            continue
        t = o[3]
        v = sorted({c for r in nos(t) for c in t.elem(r).get("m_Classes") or [] if c.startswith("uipicker-")})
        print(f"{modele} : " + (f"rangée posée ({', '.join(v)} ; actuelle {VERSION})" if v else "pas de rangée"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
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
            print("infos des cartes du terrain : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
