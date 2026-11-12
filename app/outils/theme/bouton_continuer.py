"""Bouton Continuer (en haut à droite, modèle continue-button, partagé : barre du haut, rubans, match) : couleur du thème
ou du club quand il dit simplement « Continuer » ; les états où FM attend quelque chose gardent le bouton de FM.

Appelé par couleurs_interface (clé « continuer », seul écrivain de ce modèle) :
- None / « fm » : bouton de FM (modèle d'origine).
- « theme »     : aplat de la couleur des boutons du thème (boutons, sinon accent) ; texte et flèche blancs (noirs
                  seulement sur un aplat presque blanc).
- « club »      : couleur principale du club (human.team.club.PrimaryColor), texte et flèche à la couleur secondaire.
Histoire (essai essai_continuer_club v1-v7, 2026-11-11, demande du joueur, thème FM 24 Kojuro) : les dégradés du bouton
suivent la règle « .continue-button---default .sigradient » (une liaison n'y passe pas devant) -> couche pleine posée
dans le bouton, juste au-dessus du fond et des dégradés de FM, SOUS le clignotement d'alerte, le texte et l'icône (le
joueur : « la couleur du bouton passe toujours sous les alertes »). Club : SIStyleSetter « couleur -> fond » 76b11a74
(couleur posée en code, comme FeedbackMatchBlock …Club.PrimaryColor) ; texte : liens Primary / SecondaryColorDataLink du
SIStyleSetter parent + classe fm-club-secondary-color (comme MatchCommentaryBar).
Couche visible seulement dans les états « default » de ContinueStateStyleDataCollection (continue.State) : SIVisible
imbriqués « ≠ n » pour chaque état d'alerte (must-respond 1-3 orange), de match (jour de match, Confirmer la sélection :
rouge de FM) et de traitement (8). Bords du bouton retirés (sinon liseré de FM autour de la couleur).
Le rouge de base de FM (--continue-button-default-*) n'est plus recoloré par le thème (couleurs_interface).

En plus (clés continuer_alerte / _traitement / _match de couleurs_interface) : aplat dans les états d'alerte (1-3) /
de traitement (8) / de match (ETATS_EN_PLUS), sous le clignotement et le texte de FM.

Usage (test, jeu fermé) : bouton_continuer.py theme=#3DA0E6 | club | fm [alerte=#RRGGBB] [traitement=#RRGGBB]
                          [match=#RRGGBB] [--dry-run]
"""
import copy
import os
import struct
import sys

import UnityPy

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402

MODELE = "continue-button"
SOURCE = "FeedbackMatchBlock"        # son SIStyleSetter …Club.PrimaryColor (fonction « couleur -> fond »)
FN_FOND = "76b11a74"
FN_VISIBLE = "d52cf0b2"
CHEMIN_FOND = "human.team.club.PrimaryColor"
CHEMIN_TEXTE = "human.team.club.SecondaryColor"
TEXTES = ("text", "countdown-text", "primary-icon-image")
CLASSE_TEXTE = "fm-club-secondary-color"
BOUTON, DEGRADE, FOND, VISIBLE = "continue-button", "continue-button-gradient", "continue-button-background", "countdown-visible"
ETAT = "continue.State"
# états qui gardent le bouton de FM (ContinueStateStyleDataCollection : tout sauf « continue-button---default »)
ETATS_FM = (1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 15, 16, 17, 18, 24, 28, 29, 30, 31, 45)
ETATS_DEFAUT = tuple(n for n in range(46) if n not in ETATS_FM)   # les autres (« continue-button---default »)
CONTENU = ("text", "spacer", "primary-icon-visible", "countdown-visible")   # enfants du bouton : texte, icône
DIFFERENT = 5                        # opérateur ≠
EGAL = 2                             # opérateur = (technique.md : 0 <, 1 ≤, 2 =, 3 ≥, 4 >, 5 ≠)
# couleurs à part (2026-11-11, le joueur) : bouton en alerte (must-respond, orange de FM) / pendant le traitement
# (8, « Traitement… ») ; aplat sous le clignotement et le texte de FM, quel que soit le mode
ETATS_EN_PLUS = {"alerte": (1, 2, 3), "traitement": (8,),
                 # jours de match (Confirmer la sélection, Passer au match… : rose / rouge de FM) = les autres états de FM
                 "match": (4, 5, 6, 7, 10, 14, 15, 16, 17, 18, 24, 28, 29, 30, 31, 45)}
# thème : texte noir au-dessus de cette luminance (0..1) ; v3 (2026-11-11, le joueur : « couleur et blanc à
# l'intérieur ») : blanc partout, noir seulement sur un aplat presque blanc (Tato FM 24, sinon illisible)
SEUIL_CLAIR = 0.85
NOIR = (0.0, 0.0, 0.0, 1.0)
VERSION = 7   # v2 (2026-11-11) : texte de FM (blanc) dans ses états, copie colorée seulement sur « Continuer »
#               v4 : texte toujours à gauche (certains libellés de FM se centraient) ; v5 : couleurs alerte / traitement
#               v7 (2026-11-11, retour Discord : mauve pendant le traitement, plus d'effet au survol) : traitement sans
#               couleur + mode theme = nuance du bouton (comme page.html nuanceContinuer) ; voile blanc au survol
# nuance auto (page.html nuanceContinuer) : plus foncée si la couleur est claire, plus claire sinon
NUANCE_SEUIL, NUANCE_ECART = 0.5, 0.14
# survol (FM éclaircit son dégradé, caché sous notre aplat) : voile blanc dans la couche, règle « .BOUTON:hover .VOILE »
CLASSE_BOUTON, CLASSE_VOILE = "uipicker-continuer-bouton", "uipicker-continuer-voile"
VOILE = (1.0, 1.0, 1.0, 0.14)
A_GAUCHE = {"-unity-text-align": "middle-left"}
PREFIXE = "UIPickerContinuer"
MARQUE = f"uipicker-continuer-v{VERSION}"
MODES = ("theme", "club")
for k, v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "right": (131103, 3),
             "bottom": (131080, 3), "color": (65536, 4), "tint": (196610, 4), "flex-direction": (131083, 7),
             "align-items": (131073, 7), "justify-content": (131088, 7), "align-self": (131074, 7),
             "-unity-text-align": (65546, 7)}.items():
    sm.PROPRIETES.setdefault(k, v)
for k, v in {"padding-left": (131099, 3), "padding-right": (131100, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)
REMPLIT = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}
# v6 (2026-11-11, le joueur : « Messages », « Dans le monde » centrés) : lignes du texte en flux = mal étirées ->
# chaque niveau remplit le bouton en absolu (largeur fixe, .continue-button) ; le dernier refait la rangée du bouton
# de FM (vu en jeu par le mod : texte à +12, spacer qui pousse, icône à droite)
LIGNE = {**REMPLIT, "flex-direction": "row", "align-items": "center", "justify-content": "space-between",
         "padding-left": 12, "padding-right": 12}
SANS_BORD = {f"border-{c}-width": 0 for c in ("top", "bottom", "left", "right")}
IGNORE = 1                           # pickingMode Ignore : les clics passent au bouton


def _original(bundle, path_id):
    p = backup.backup_path(bundle)
    if not os.path.exists(p):
        return None
    o = next((x for x in UnityPy.load(p).objects if x.path_id == path_id), None)
    return o.read_typetree() if o is not None else None


def _chemin(ch):
    return b"\x01" + _enc_varint(len(ch)) + ch.encode()


def _fonction_fond():
    """BindFunction « couleur -> fond de l'enfant » (76b11a74) de FeedbackMatchBlock, chemin = CHEMIN_FOND"""
    _, _, tt = nb.find_vta(SOURCE)
    if tt is None:
        return None
    s = Tree(tt)
    for r in s.walk():
        f = s.sd(r).get("BindFunction")
        if not (isinstance(f, dict) and f["m_target"]["m_guid"].startswith(FN_FOND)):
            continue
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        if len(args) == 2 and bytes(args[0][1]).endswith(b"Club.PrimaryColor") and bytes(args[1][1]) == b"\x01":
            f = copy.deepcopy(f)
            args[0][1] = _chemin(CHEMIN_FOND)
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
            return f
    return None


def _ignore(t, r):
    t.sd(r)["pickingMode"] = IGNORE
    if "pickingMode_UxmlAttributeFlags" in t.sd(r):
        t.sd(r)["pickingMode_UxmlAttributeFlags"] = 1


def _a_nous(t, sh, r, nom, style=None):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1
    _ignore(t, r)
    t.elem(r)["m_Classes"] = [MARQUE]
    t.elem(r)["m_RuleIndex"] = -1
    sh.style(t, r, style or REMPLIT)


def _chaine(t, sh, vis, parent, index, etats, nom, style=None, op=DIFFERENT):
    """SIVisible imbriqués « continue.State <op> n » pour chaque n (copies de #countdown-visible) ; renvoie le dernier"""
    cur = parent
    for n in etats:
        v = t.clone_shallow(vis, cur, index if cur == parent else None)
        f_vis = t.sd(v)["Binding"]["m_visualFunction"]
        args = decode_args(f_vis["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"ComparisonOperator]"):
                a[1] = struct.pack("<i", op)
            elif a[0].endswith(b"Int32VisualArg"):
                a[1] = struct.pack("<i", n)
            elif a[0].endswith(b"BindingPath]"):
                a[1] = _chemin(ETAT)
        f_vis["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        _a_nous(t, sh, v, f"{nom}{n}", style)
        cur = v
    return cur


def _rgba(c):
    rgb, a = c[:3], c[3] if len(c) > 3 else 1.0
    return tuple(v / 255 for v in rgb) + (a,)


def nuance(c):
    """couleur (r, g, b[, a]) 0..255 -> nuance du bouton (r, g, b, 1.0), comme page.html nuanceContinuer"""
    import colorsys
    r, g, b = (v / 255 for v in c[:3])
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    l = max(0.0, min(1.0, l - NUANCE_ECART if lum >= NUANCE_SEUIL else l + NUANCE_ECART))
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s)) + (1.0,)


def poser_voile(t, sh, bouton, fond, parent):
    """voile blanc transparent sous parent (couche « Continuer »), visible quand la souris est sur le bouton"""
    voile = t.clone_shallow(fond, parent)
    _a_nous(t, sh, voile, PREFIXE + "Voile")
    t.elem(voile)["m_Classes"] = [MARQUE, CLASSE_VOILE]
    t.elem(bouton)["m_Classes"] = list(t.elem(bouton).get("m_Classes") or []) + [CLASSE_BOUTON]
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(bouton).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)
    p = sm.PROPRIETES["background-color"]
    idx = sh.add_rule([(p[0], "", [(p[1], VOILE)])])
    sh.sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": 21, "ruleIndex": idx, "m_Selectors": [
        {"m_Parts": [{"m_Value": CLASSE_BOUTON, "m_Type": 3}, {"m_Value": "hover", "m_Type": 4}],
         "m_PreviousRelationship": 0},
        {"m_Parts": [{"m_Value": CLASSE_VOILE, "m_Type": 3}], "m_PreviousRelationship": 2}]}]


def poser_en_plus(t, sh, en_plus):
    """aplats des états d'alerte / de traitement (ETATS_EN_PLUS) : un SIVisible « continue.State = n » par état, juste
    après les dégradés (sous le clignotement et le texte) ; en_plus = {clé: (r, g, b, a)}"""
    bouton = next((r for r in t.walk() if t.name(r) == BOUTON), None)
    vis = next((r for r in t.walk() if t.name(r) == VISIBLE), None)
    fond = next((r for r in t.walk() if t.name(r) == FOND), None)
    deg = next((r for r in t.walk() if t.name(r) == DEGRADE), None)
    if None in (bouton, vis, fond, deg) or t.parent.get(deg) != bouton:
        return [f"{MODELE} : bouton / dégradé introuvable (le jeu a changé ?)"]
    msgs = []
    for cle, etats in ETATS_EN_PLUS.items():
        c = en_plus.get(cle)
        if not c:
            continue
        for n in etats:
            index = [k["rid"] for k in t.elem(bouton)["m_Children"]].index(deg) + 1
            v = _chaine(t, sh, vis, bouton, index, (n,), f"{PREFIXE}{cle.capitalize()}", op=EGAL)
            plein = t.clone_shallow(fond, v)
            _a_nous(t, sh, plein, f"{PREFIXE}{cle.capitalize()}Fond{n}")
            sh.style(t, plein, {"background-color": _rgba(c)})
        msgs.append(f"{cle} #%02X%02X%02X" % tuple(c[:3]))
    return msgs


def poser(t, sh, mode, couleur=None):
    """couche « mode » dans le modèle (original) ; couleur = (r, g, b, a) 0..255 / 0..1 pour « theme »"""
    trouve = {n: next((r for r in t.walk() if t.name(r) == n), None) for n in (BOUTON, DEGRADE, FOND, VISIBLE)}
    setter = next((r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("SIStyleSetter")), None)
    if None in trouve.values() or setter is None or t.parent.get(trouve[DEGRADE]) != trouve[BOUTON]:
        return [f"{MODELE} : bouton / dégradé / fond introuvable (le jeu a changé ?)"]
    vis = trouve[VISIBLE]
    if not (t.sd(vis).get("Binding") or {}).get("m_visualFunction", {}).get("m_target", {}).get("m_guid", "").startswith(FN_VISIBLE):
        return [f"{MODELE} : #{VISIBLE} a changé (le jeu a changé ?)"]
    bouton = trouve[BOUTON]
    parent = t.parent.get(bouton)
    if parent is None or not (t.elem(parent).get("m_FullTypeName") or "").endswith("SIStyleSetter"):
        return [f"{MODELE} : setter autour du bouton introuvable (le jeu a changé ?)"]
    f = None
    if mode == "club":
        f = _fonction_fond()
        if f is None:
            return [f"{SOURCE} : setter …Club.PrimaryColor introuvable (le jeu a changé ?)"]
    contenu = [next((k["rid"] for k in t.elem(bouton)["m_Children"] if t.name(k["rid"]) == n), None) for n in CONTENU]
    if None in contenu:
        return [f"{MODELE} : texte / icône du bouton introuvables (le jeu a changé ?)"]
    # fond : SIVisible imbriqués, seulement hors des états de FM ; juste après les dégradés (sous l'alerte et le texte)
    cur = _chaine(t, sh, vis, bouton, [k["rid"] for k in t.elem(bouton)["m_Children"]].index(trouve[DEGRADE]) + 1,
                  ETATS_FM, f"{PREFIXE}Etat")
    msgs = []
    if mode == "club":
        couche = t.clone_shallow(setter, cur)           # SIStyleSetter (même type), fonction « couleur -> fond »
        t.sd(couche)["BindFunction"] = f
        _a_nous(t, sh, couche, PREFIXE)
        plein = t.clone_shallow(trouve[FOND], couche)   # élément simple : reçoit la couleur en code
        _a_nous(t, sh, plein, PREFIXE + "Fond")
        sd = t.sd(parent)
        sd["PrimaryColorDataLink"], sd["PrimaryColorDataLink_UxmlAttributeFlags"] = {"m_path": CHEMIN_FOND}, 1
        sd["SecondaryColorDataLink"], sd["SecondaryColorDataLink_UxmlAttributeFlags"] = {"m_path": CHEMIN_TEXTE}, 1
        msgs += [f"couleur du club ({CHEMIN_FOND}), texte {CHEMIN_TEXTE}"]
        noir = False
    else:
        plein = t.clone_shallow(trouve[FOND], cur)
        _a_nous(t, sh, plein, PREFIXE + "Fond")
        rgb, a = couleur[:3], couleur[3] if len(couleur) > 3 else 1.0
        sh.style(t, plein, {"background-color": tuple(v / 255 for v in rgb) + (a,)})
        noir = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255 >= SEUIL_CLAIR
        msgs += ["couleur du thème #%02X%02X%02X" % tuple(rgb) + (", texte noir" if noir else "")]
    poser_voile(t, sh, bouton, trouve[FOND], cur)   # v7 : éclaircit au survol, comme le bouton de FM
    msgs += ["voile au survol"]
    t.elem(bouton)["m_Classes"] = list(t.elem(bouton).get("m_Classes") or []) + [MARQUE]
    sh.style(t, bouton, SANS_BORD)
    fin = [f"bouton de FM gardé dans {len(ETATS_FM)} états (alertes, match, traitement)", "bords retirés"]
    if mode != "club" and not noir:   # v6 : texte blanc partout -> contenu de FM laissé tel quel (placement de FM)
        return msgs + ["texte de FM laissé en place"] + fin
    # texte (2026-11-11, le joueur : « texte blanc dans l'alerte ») : celui de FM (blanc) dans les états de FM, une
    # copie colorée seulement quand le bouton dit « Continuer » ; deux lignes (une seule affichée à la fois)
    index = [k["rid"] for k in t.elem(bouton)["m_Children"]].index(contenu[0])
    garde = _chaine(t, sh, vis, bouton, index, ETATS_DEFAUT, f"{PREFIXE}TexteFM")
    copie = _chaine(t, sh, vis, bouton, index + 1, ETATS_FM, f"{PREFIXE}Texte")
    sh.style(t, garde, LIGNE)
    sh.style(t, copie, LIGNE)
    for r in contenu:   # le texte de FM, déplacé tel quel
        t.elem(bouton)["m_Children"] = [k for k in t.elem(bouton)["m_Children"] if k["rid"] != r]
        t.elem(garde)["m_Children"].append({"rid": r})
        t.elem(r)["m_Parent"] = {"rid": garde}
        t.parent[r] = garde
    # v4 (2026-11-11, le joueur : « Messages » centré, « Continuer » à gauche) : texte calé à gauche dans sa boîte
    sh.style(t, contenu[0], A_GAUCHE)
    for r in contenu:   # la copie colorée
        c = t.clone(r, copie)
        for x in t.walk(c):
            _ignore(t, x)
            if t.name(x) not in TEXTES:
                continue
            t.elem(x)["m_Classes"] = list(t.elem(x).get("m_Classes") or []) + [MARQUE]
            if mode == "club":
                t.elem(x)["m_Classes"].append(CLASSE_TEXTE)
            elif noir:
                sh.style(t, x, {"tint": NOIR} if t.name(x) == "primary-icon-image" else {"color": NOIR})
    msgs += ["texte de FM gardé dans ses états, copie colorée sinon"]
    return msgs + fin


def appliquer(mode, couleur=None, ecrire=False, en_plus=None):
    """modèle repris de l'original puis couche « mode » (None = bouton de FM) et aplats en_plus ({alerte / traitement:
    (r, g, b, a)}) ; ecrire : nb.save_all() à la fin"""
    mode = mode if mode in MODES else None
    if mode == "theme" and couleur is None:
        mode = None
    en_plus = {k: v for k, v in (en_plus or {}).items() if k in ETATS_EN_PLUS and v}
    if mode == "theme" and "traitement" not in en_plus:   # v7 : plus de violet de FM pendant le traitement
        en_plus["traitement"] = nuance(couleur)
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        print(f"{MODELE} (bouton Continuer) : introuvable (le jeu a changé ?)")
        return
    t = Tree(tt)
    prefs = (MARQUE.rsplit("-v", 1)[0] + "-v", "uipicker-essai-continuer-club-v")   # + l'ancien essai (124)
    pose = any(c.startswith(prefs) for r in t.walk() for c in (t.elem(r).get("m_Classes") or []))
    if mode is None and not en_plus and not pose:
        return   # d'origine et rien à faire
    orig = _original(bundle, obj.path_id)
    if orig is None:
        if pose:
            print(f"{MODELE} (bouton Continuer) : pas de sauvegarde d'origine, laissé tel quel")
            return
        orig = tt   # jamais touché : le modèle est celui de FM
    tt, t = orig, Tree(orig)
    sh = Styles(bundle, tt)
    feuille = _original(bundle, tt["inlineSheet"]["m_PathID"])
    if feuille is not None:   # feuille d'origine aussi : les règles des passages précédents ne s'empilent pas
        sh.sh = feuille
    msgs = poser(t, sh, mode, couleur) if mode else ["bouton de FM" if en_plus else "remis d'origine"]
    if en_plus and not ("introuvable" in msgs[0] or "a changé" in msgs[0]):
        msgs += poser_en_plus(t, sh, en_plus)
    print(f"{MODELE} (bouton Continuer) : " + ", ".join(msgs))
    if any("introuvable" in m or "a changé" in m for m in msgs):
        return
    t.finish()
    sh.changed = True
    sh.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    if ecrire:
        nb.save_all()


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    if not argv:
        sys.exit(__doc__)
    import theme_fond

    def rgba(c):
        return tuple(theme_fond.to_rgb(c)) + (theme_fond.alpha(c),)
    a = argv[0]
    en_plus = {k: rgba(v) for k, v in (x.split("=", 1) for x in argv[1:] if "=" in x) if k in ETATS_EN_PLUS}
    if a.startswith("theme="):
        appliquer("theme", rgba(a.split("=", 1)[1]), ecrire=True, en_plus=en_plus)
    elif a in ("club", "fm"):
        appliquer(a, ecrire=True, en_plus=en_plus)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
