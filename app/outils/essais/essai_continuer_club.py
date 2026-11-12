"""ESSAI : bouton Continuer à la couleur du club, comme dans FM24 (2026-11-11, demande du joueur, thème FM 24 Kojuro).

FM27 : bouton violet (variables --continue-button-default-*, ou le style d'une compétition sous licence), modèle
continue-button (partagé : barre du haut, rubans, match).
v1 (en jeu : RATÉ, bouton inchangé) : ses 2 SIGradient branchés sur human.team.club.TitlebarBackgroundColour (liaison
de la barre du haut) -> la règle « .continue-button---default .sigradient » de FM passe devant.
v2 (le joueur : « la couleur principale direct ») : une couche pleine posée dans le bouton, au-dessus de son fond et
de ses dégradés, sous le texte et l'icône : SIStyleSetter « couleur -> fond » (76b11a74, booléen 1 = sur l'enfant,
la couleur est posée en code, devant tout style) sur human.team.club.PrimaryColor (comme FeedbackMatchBlock
…Club.PrimaryColor), enfant = élément vide qui remplit le bouton (position absolue, 0 partout, clics ignorés).
v3 : couleur de la barre du haut (TitlebarBackgroundColour) ; v4 : texte / icône = TitlebarTextColour (liens Primary /
SecondaryColorDataLink du setter parent du bouton + classe fm-club-secondary-color), bords retirés.
Réussi = bouton Continuer à la couleur principale du club. À surveiller : texte blanc sur club clair, plus de survol,
plus d'orange « doit répondre » ni d'image de compétition sous licence (la couche les couvre).
Sélection nationale / sans club : chemin vide, normalement couche vide = bouton de FM.

Outils FM.bat : 124 (essais pas validés) ; retrait : 105 (catalogue.ESSAIS).
Usage : essai_continuer_club.py appliquer [--dry-run] | retirer [--dry-run]
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
FN_FOND = "76b11a74"                 # début du GUID
# v2 en jeu (2026-11-11) : la couche marche (Aachen jaune, ITU blanc) mais PrimaryColor = pas forcément la couleur
# que le joueur attend (ITU) -> v3 : la couleur que FM met dans la barre du haut (comme FM24)
# v3 en jeu : couleur OK mais texte blanc sur club clair, bords bleus (accent) -> v4 : texte = couleur du texte de la
# barre du club (TitlebarTextColour), bords retirés. v4 en jeu : texte et flèche suivent bien (Aachen noir / jaune,
# City bleu ciel / blanc) ; le joueur préfère les couleurs de v2 -> v5 : fond = couleur principale, texte = secondaire
CHEMIN = "human.team.club.PrimaryColor"
CHEMIN_TEXTE = "human.team.club.SecondaryColor"
TEXTES = ("text", "countdown-text", "primary-icon-image")
# v5 en jeu : « bouton pâle » = état d'alerte (Confirmer la sélection) -> v6 (joueur : laisser le bouton d'alerte de
# FM) : couche du club cachée dans les états continue-button---must-respond (ContinueStateStyleDataCollection : 1-3)
# v6 en jeu : « Confirmer la sélection » toujours pâle = pas une alerte (orange de FM intact) mais un état « match »
# (jour de match) -> v7 : couche du club seulement dans les états « default » de la table ; cachée pour tous les
# autres (must-respond 1-3, match, processing 8)
ETAT = "continue.State"
ALERTES = (1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 15, 16, 17, 18, 24, 28, 29, 30, 31, 45)
FN_VISIBLE = "d52cf0b2"
DIFFERENT = 5                        # opérateur ≠
CLASSE_TEXTE = "fm-club-secondary-color"
SANS_BORD = {f"border-{c}-width": 0 for c in ("top", "bottom", "left", "right")}
BOUTON, DEGRADE, FOND = "continue-button", "continue-button-gradient", "continue-button-background"
VERSION = 7
PREFIXE = "UIPickerEssaiContinuerClub"
MARQUE = f"uipicker-essai-continuer-club-v{VERSION}"
for k, v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "right": (131103, 3),
             "bottom": (131080, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)
REMPLIT = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}
IGNORE = 1                           # pickingMode Ignore : les clics passent au bouton


def _original(bundle, path_id):
    p = backup.backup_path(bundle)
    if not os.path.exists(p):
        return None
    o = next((x for x in UnityPy.load(p).objects if x.path_id == path_id), None)
    return o.read_typetree() if o is not None else None


def _fonction_fond():
    """BindFunction d'un SIStyleSetter « couleur -> fond » de FeedbackMatchBlock (…Club.PrimaryColor, sur l'enfant),
    chemin remplacé par CHEMIN"""
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
            args[0][1] = b"\x01" + _enc_varint(len(CHEMIN)) + CHEMIN.encode()
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
            return f
    return None


def poser(t, sh):
    f = _fonction_fond()
    if f is None:
        return [f"{SOURCE} : setter …Club.PrimaryColor introuvable (le jeu a changé ?)"]
    trouve = {n: next((r for r in t.walk() if t.name(r) == n), None) for n in (BOUTON, DEGRADE, FOND)}
    setter = next((r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("SIStyleSetter")), None)
    if None in trouve.values() or setter is None or t.parent.get(trouve[DEGRADE]) != trouve[BOUTON]:
        return [f"{MODELE} : bouton / dégradé / fond introuvable (le jeu a changé ?)"]
    bouton = trouve[BOUTON]
    index = [k["rid"] for k in t.elem(bouton)["m_Children"]].index(trouve[DEGRADE]) + 1
    # v6 : couche seulement hors alerte (états ALERTES = orange de FM : message à lire, interaction à faire) :
    # SIVisible imbriqués « continue.State ≠ n » (copies de #countdown-visible, fonction d52cf0b2 comme HomeRibbon)
    vis = next((r for r in t.walk() if t.name(r) == "countdown-visible"
                and (t.sd(r).get("Binding") or {}).get("m_visualFunction", {}).get("m_target", {}).get("m_guid", "")
                .startswith(FN_VISIBLE)), None)
    if vis is None:
        return [f"{MODELE} : #countdown-visible introuvable (le jeu a changé ?)"]
    cur = bouton
    for n in ALERTES:
        v = t.clone_shallow(vis, cur, index if cur == bouton else None)
        f_vis = t.sd(v)["Binding"]["m_visualFunction"]
        args = decode_args(f_vis["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"ComparisonOperator]"):
                a[1] = struct.pack("<i", DIFFERENT)
            elif a[0].endswith(b"Int32VisualArg"):
                a[1] = struct.pack("<i", n)
            elif a[0].endswith(b"BindingPath]"):
                a[1] = b"\x01" + _enc_varint(len(ETAT)) + ETAT.encode()
        f_vis["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = f"{PREFIXE}Etat{n}", 1
        t.sd(v)["pickingMode"] = IGNORE
        if "pickingMode_UxmlAttributeFlags" in t.sd(v):
            t.sd(v)["pickingMode_UxmlAttributeFlags"] = 1
        t.elem(v)["m_Classes"] = [MARQUE]
        t.elem(v)["m_RuleIndex"] = -1
        sh.style(t, v, REMPLIT)
        cur = v
    couche = t.clone_shallow(setter, cur)               # SIStyleSetter (même type), fonction remplacée
    plein = t.clone_shallow(trouve[FOND], couche)       # élément simple : reçoit la couleur
    t.sd(couche)["BindFunction"] = f
    for r, nom in ((couche, PREFIXE), (plein, PREFIXE + "Fond")):
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1
        t.sd(r)["pickingMode"] = IGNORE
        if "pickingMode_UxmlAttributeFlags" in t.sd(r):
            t.sd(r)["pickingMode_UxmlAttributeFlags"] = 1
        t.elem(r)["m_Classes"] = [MARQUE]
        t.elem(r)["m_RuleIndex"] = -1
        sh.style(t, r, REMPLIT)
    # v4 : texte (et icône) = couleur du texte de la barre du club : liens du SIStyleSetter parent du bouton (comme
    # la barre de commentaire : secondaire -> éléments .fm-club-secondary-color) ; bords (bleus / violets) retirés
    parent = t.parent.get(bouton)
    if parent is None or not (t.elem(parent).get("m_FullTypeName") or "").endswith("SIStyleSetter"):
        return [f"{MODELE} : setter autour du bouton introuvable (le jeu a changé ?)"]
    sd = t.sd(parent)
    sd["PrimaryColorDataLink"], sd["PrimaryColorDataLink_UxmlAttributeFlags"] = {"m_path": CHEMIN}, 1
    sd["SecondaryColorDataLink"], sd["SecondaryColorDataLink_UxmlAttributeFlags"] = {"m_path": CHEMIN_TEXTE}, 1
    textes = [r for r in t.walk(bouton) if t.name(r) in TEXTES]
    for r in textes:
        t.elem(r)["m_Classes"] = list(t.elem(r).get("m_Classes") or []) + [CLASSE_TEXTE, MARQUE]
    sh.style(t, bouton, SANS_BORD)
    return [f"couche {CHEMIN} posée dans le bouton (au-dessus du fond et des dégradés)",
            f"texte {CHEMIN_TEXTE} ({len(textes)} éléments)", "bords retirés"]


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    cmd = argv[0] if argv else ""
    if cmd not in ("appliquer", "retirer"):
        sys.exit(__doc__)
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        sys.exit(f"{MODELE} introuvable")
    t = Tree(tt)
    classes = [c for r in t.walk() for c in (t.elem(r).get("m_Classes") or [])]
    pose = any(c.startswith(MARQUE.rsplit("-v", 1)[0]) for c in classes)
    if cmd == "appliquer" and MARQUE in classes:
        print(f"{MODELE} : déjà appliqué")
        return
    if cmd == "retirer" and not pose:
        print(f"{MODELE} : rien à retirer")
        return
    # seul écrivain de ce modèle : on repart toujours de l'original (modèle + feuille de style intégrée)
    orig = _original(bundle, obj.path_id)
    if orig is None and pose:
        sys.exit(f"{MODELE} : pas de sauvegarde d'origine, laissé tel quel")
    if orig is not None:
        tt, t = orig, Tree(orig)
    sh = Styles(bundle, tt)
    feuille = _original(bundle, tt["inlineSheet"]["m_PathID"])
    if feuille is not None:
        sh.sh = feuille
    msgs = poser(t, sh) if cmd == "appliquer" else ["remis d'origine"]
    print(f"{MODELE} : " + ", ".join(msgs))
    if "introuvable" in msgs[0]:
        return
    t.finish()
    sh.changed = True
    sh.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    nb.save_all()


if __name__ == "__main__":
    main(sys.argv[1:])
