"""Match : cartons, buts et passes D sur les cartes des joueurs du terrain (demande du joueur, 2026-11-09).

- carton jaune : la pastille du poste (à droite de la note) passe en jaune léger ;
- buts : ballon + nombre collé à gauche de la pastille note | poste, seulement s'il en a ;
- passes D : icône passe D + nombre collé à droite de la pastille, seulement s'il en a.
(Les parents de la pastille passent en overflow visible : pas remis par « retirer », sans effet sans nos ajouts.)

Cartes : terrain du match (formations, TacticsMatchPositionFilled) et tuile Formation du résumé
(FormationPositionFilled). Ces cartes appartiennent à photos_match (qui repart de l'original) : ce script ne fait
qu'AJOUTER des éléments à la carte telle qu'elle est et passe après lui (catalogue : ORDRE_SKIN, SUIVANTS).
Retirer = enlever nos éléments (repérés par leur nom).

Usage (jeu fermé) : match_cartons_buts.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import make_visible  # noqa: E402
from elements import first, typ, plain, visible_model  # noqa: E402
import moteur_photos as mp  # noqa: E402  (ouvrir : modèle actuel + sa feuille de style ; propriétés de position)
import notes_installations as ni  # noqa: E402  (SIVisible « entier > 0 » de FM, textes liés)

for k, v in {"border-top-right-radius": (458765, 3), "border-bottom-right-radius": (458760, 3),
             "border-top-left-radius": (458764, 3), "border-bottom-left-radius": (458759, 3),
             "margin-top": (131093, 3), "align-self": (131074, 7), "padding-left": (131099, 3),
             "padding-right": (131100, 3), "font-size": (65537, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
JAUNE = (1.0, 0.82, 0.10, 0.55)   # fond de la pastille du poste après un jaune (r, g, b, opacité) : jaune léger
RAYON = 7                         # px des coins droits du fond jaune (pastille FM : 8, moins son bord de 1)
TEXTE = "body-xs-strong"          # classe du nombre de buts / passes D
TEXTE_HAUT = -2                   # px : nombre remonté contre son icône
ICONE_BUT = "game-concepts-goal_small"
ICONE_PASSE = "game-concepts-assist_small"
ICONE = 10                        # px des icônes but / passe D (v3 : 10 -> 12, « grossis légèrement » ; v4 : 11,
                                  # « un poil plus petit » ; v5 : 10, « encore 1 pixel »)
TEXTE_STAT = "body-sm-strong"     # classe du nombre de buts / passes D (celle de la barre du bas de FM)
TAILLE_STAT = 10                  # px du nombre (v4 : 11, body-sm de FM un peu trop gros ; v5 : 10)
ECART = 2                         # px entre la pastille note | poste et les buts / passes D (v6 : collés à la pastille
                                  # au lieu du nom ; v4-v5 : RENTRE 8 px dans la marge à côté du nom)
HAUT_NB = 11                      # px de la ligne du nombre, au-dessus de l'icône (v7 : empilés)
# cartes : (modèle, chemin du joueur du match)
CIBLES = [
    ("TacticsMatchPositionFilled", "Position.MatchPlayer"),
    ("FormationPositionFilled", "Position.MatchPlayer"),
]
# =====================================================================================================

NOM = "UIPickerCartonsButs"
VERSION = "uipicker-cartons-buts-v7"   # v2 : buts / passes D en pastilles sombres posées par-dessus (v1 cachés) ;
                                       # v3 : à gauche / à droite du nom, hors de la carte, sans fond ;
                                       # v4 : un peu plus petits (11 px), rentrés de 8 px ; v5 : 10 px ;
                                       # v6 : remontés, collés à gauche / à droite de la pastille note | poste ;
                                       # v7 : nombre au-dessus de l'icône (moins large, plus de chevauchement)
MARKER = os.path.join(backup.BACKUP_DIR, "match_cartons_buts.actif")
GAUCHE = sm.PROPRIETES["left"][0]


def nos(t):
    return [r for r in t.walk() if t.name(r).startswith(NOM)]


def chemin_de(t, r):
    b = t.sd(r).get("Binding") or {}
    return ((b.get("m_direct") or {}).get("Path") or {}).get("m_path") or ""


def nommer(t, r, suffixe):
    t.sd(r)["name"] = f"{NOM}-{suffixe}"
    t.sd(r)["name_UxmlAttributeFlags"] = 1
    t.elem(r)["m_Classes"] = list(t.elem(r).get("m_Classes") or []) + [VERSION]


def nombre(t, modele, parent, chemin, suffixe):
    """nombre lié (copie du texte du nom de la carte, petit, centré sous l'icône)"""
    txt = ni.text_direct(t, modele, parent, chemin)
    t.elem(txt)["m_Classes"] = [TEXTE, "text-middle-center"]
    t.elem(txt)["m_RuleIndex"] = -1
    t.styles.style(t, txt, {"align-self": "center", "margin-top": TEXTE_HAUT, "flex-shrink": 0})
    nommer(t, txt, suffixe)
    return txt


def poser(t, joueur, s_int, v_int):
    """fond jaune, nombre de buts, passes D ; renvoie un message"""
    poste = first(t, lambda r: t.name(r) == "PositionContainer")
    but = first(t, lambda r: typ(t, r).endswith("SIVisible") and chemin_de(t, r).lower().endswith("scoredinmatch"))
    nom = first(t, lambda r: typ(t, r).endswith("SIText")
                and (t.sd(r).get("TextBinding") or {}).get("m_kind") == 1
                and chemin_de_texte(t, r).lower().endswith("shirtname"))
    modele_vis = visible_model(t)
    if None in (poste, but, nom, modele_vis) or not t.children(but):
        return "repère introuvable (pastille du poste, ballon, nom)"
    # 1) jaune : fond plein cadre DANS la pastille, en premier (le texte du poste reste dessus) ; SIVisible = fond
    #    ignoré -> fond sur un enfant
    vis = make_visible(t, modele_vis, poste, 0, f"{joueur}.YellowCardedInMatch", "", [])
    t.elem(vis)["m_RuleIndex"] = -1
    nommer(t, vis, "jaune")
    plein = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}
    t.styles.style(t, vis, plein)
    fond = plain(t, vis, None, [])
    t.elem(fond)["m_RuleIndex"] = -1
    t.styles.style(t, fond, {**plein, "background-color": JAUNE,
                             "border-top-right-radius": RAYON, "border-bottom-right-radius": RAYON})
    # 2) / 3) buts (bas gauche) et passes D (bas droite) : pastille sombre [icône + nombre] posée EN DERNIER dans la
    #    rangée du maillot (v1 : sous le ballon de FM, caché par la photo de photos_match ; passes D blanches sur le
    #    maillot = illisibles). Visibles si Goals / Assists > 0 (même condition que la barre du bas de FM).
    #    v3 (le joueur : « ça gâche maillots et photos ») : à gauche / à droite du NOM, juste hors de la carte (le nom
    #    le plus long, « Matheus N. », la remplit) : right / left 100 % de la rangée du nom, RENTRE px dans sa marge.
    #    v6 (le joueur : « remonte-les, colle-les à gauche et à droite du poste plutôt que du nom ») : accrochés à la
    #    pastille note | poste (#RatingBG, parent de #PositionContainer), right / left 100 % + ECART px.
    rangee = t.parent[poste]
    for cote, chemin, icone, suffixe in (("right", f"{joueur}.Goals", ICONE_BUT, "buts"),
                                         ("left", f"{joueur}.Assists", ICONE_PASSE, "passes")):
        vis = ni.new_visible(t, s_int, v_int, rangee, None, "",
                             ni.make_binding(s_int.sd(v_int)["Binding"], 4, [chemin], 0), [])
        nommer(t, vis, suffixe)
        t.styles.style(t, vis, {"position": "absolute", "top": 0, "bottom": 0, cote: {"unit": 2, "value": 100.0},
                                f"margin-{cote}": ECART, "justify-content": "center"})
        # v7 (le joueur : « buts et passes D se chevauchent quand les joueurs sont proches ») : nombre AU-DESSUS,
        #    icône dessous (colonne) = moitié moins large
        p = plain(t, vis, None, ["column-direction-normal", "align-items-center"])
        t.elem(p)["m_RuleIndex"] = -1
        t.styles.style(t, p, {"flex-shrink": 0})
        n = nombre(t, nom, p, chemin, suffixe + "-nb")
        t.elem(n)["m_Classes"] = [TEXTE_STAT if c == TEXTE else c for c in t.elem(n)["m_Classes"]]
        t.styles.style(t, n, {"margin-top": 0, "margin-left": 0, "font-size": TAILLE_STAT,
                              "height": HAUT_NB, "padding-left": 0, "padding-right": 0})
        i = plain(t, p, None, [icone])
        t.elem(i)["m_RuleIndex"] = -1
        t.styles.style(t, i, {"width": ICONE, "height": ICONE, "flex-shrink": 0})
    # rien ne rogne entre la pastille et la racine de la carte (infos_cartes_terrain v3)
    r = rangee
    while r in t.parent and not typ(t, r).endswith("UXML"):
        if not typ(t, r).endswith("Component"):
            t.styles.style(t, r, {"overflow": "visible"})
        r = t.parent[r]
    return "jaune (pastille du poste), buts (gauche de la pastille), passes D (droite de la pastille)"


def chemin_de_texte(t, r):
    return (((t.sd(r).get("TextBinding") or {}).get("m_direct") or {}).get("Path") or {}).get("m_path") or ""


def cmd_appliquer():
    s_int, v_int = ni.visible_model()
    if v_int is None:
        print("SIVisible « entier » de FM introuvable (mise à jour du jeu ?) : rien fait")
        return
    a_enregistrer = []
    for modele, joueur in CIBLES:
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
            if r in t.refs:
                t.remove(r)
        msg = poser(t, joueur, s_int, v_int)
        print(f"{modele} : {msg}")
        if "introuvable" in msg:
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
    for modele, _ in CIBLES:
        o = mp.ouvrir(modele)
        if o is None or not nos(o[3]):
            continue
        bundle, obj, tt, t = o
        for r in nos(t):
            if r in t.refs:
                t.remove(r)
        t.finish()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        fait = True
        print(f"{modele} : cartons / buts / passes D retirés")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele, _ in CIBLES:
        o = mp.ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
            continue
        t = o[3]
        v = sorted({c for r in nos(t) for c in t.elem(r).get("m_Classes") or [] if c.startswith("uipicker-")})
        print(f"{modele} : " + (f"posé ({', '.join(v)} ; actuelle {VERSION})" if v else "pas posé"))
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
            print("cartons / buts / passes D du match : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
