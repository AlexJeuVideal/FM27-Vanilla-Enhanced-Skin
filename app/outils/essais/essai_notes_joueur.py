"""ESSAI : notes par joueur (2026-11-12, demande du joueur). FR seul tant que pas validé en jeu.

FM27 n'a plus de notes (aucune donnée, aucun écran) et le skin ne peut rien enregistrer : les notes sont écrites
hors du jeu (backups\\notes_joueurs.json, {"<UniqueId du joueur>": "texte"} ; plus tard dans l'app), puis gravées
dans le modèle de l'écran ; en jeu elles se lisent seulement.

1. Onglet : PlayerEntitySubtabs (gamemodules_assets_gameworld.bundle) = la barre « Vue d'ensemble … Comparaison » de
   la fiche joueur (données, pas du code ; sans doute aussi le menu du clic droit). Entrée ajoutée après
   « Comparison », copiée d'elle, qui ouvre l'écran PlayerReportPerformance.
   Libellé = un numéro de texte de FM (pas de texte libre) : « Notes » seul n'existe pas dans les modèles ->
   essai avec 25524 « Comments » (« Commentaires » en français).
2. Écran : PlayerReportPerformance (ui-panelids, paramètres player / team / comp) n'est ouvert par rien dans le jeu
   (0 citation) et son modèle (même nom, 5015fd18…) n'est utilisé que par lui -> réécrit : la grille de tuiles
   (#PerformanceGridLayoutElements) remplacée par un bloc Notes ; l'en-tête (FigmaBaseToolTabGroupTemplate) gardé.
   BindingExpect « playerhistory » (jamais fourni par l'onglet) vidé.
   Bloc : titre, identifiant FM du joueur (player.UniqueId, pour noter les jeunes générés), une note par joueur
   (SIVisible BindIntToVisible player.UniqueId == n, texte fixe), rappel « notes écrites hors du jeu ».
À voir en jeu : l'onglet apparaît (barre + clic droit) ? l'écran s'ouvre avec l'en-tête ? identifiant affiché ?

Seul propriétaire des deux : appliquer repart des originaux, retirer les remet.
Outils FM.bat : 124 (essais pas validés) ; retrait : 105 (catalogue.ESSAIS).
Usage : essai_notes_joueur.py appliquer [--dry-run] | retirer [--dry-run] | etat
"""
import copy
import hashlib
import json
import os
import sys

import UnityPy

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
import notes_installations as ni  # noqa: E402
from hierarchie_pyramide import ouvrir, original  # noqa: E402

VERSION = 1
PREFIXE = "UIPickerEssaiNotes"
MARQUE = f"uipicker-essai-notes-joueur-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "essai_notes_joueur.actif")
NOTES = os.path.join(backup.BACKUP_DIR, "notes_joueurs.json")

MENU = os.path.join(nb.AA, "gamemodules_assets_gameworld.bundle")
DONNEES = "PlayerEntitySubtabs"
APRES = "Comparison"
ENTREE = "UIPicker Notes"
LIBELLE = 25524                                   # « Comments » (essai)
PANEL_GUID = "7c62a62f1b26184428003661745ec880"   # PanelId PlayerReportPerformance
PANEL_UID = 3752957440

MODELE = "PlayerReportPerformance"
GRILLE = "PerformanceGridLayoutElements"
SOURCE_TEXTE = "PersonNicknameDialog"             # ses 2 SIText #text : titre, corps
SOURCE_CADRE = "Frame"
CHEMIN_ID = "player.UniqueId"

for k, v in {"padding-left": (131099, 3), "padding-right": (131100, 3), "padding-top": (131101, 3),
             "padding-bottom": (131098, 3), "margin-top": (131093, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)


def lire_notes():
    try:
        with open(NOTES, encoding="utf-8-sig") as f:
            brut = json.load(f)
    except (OSError, ValueError):
        return []
    out = []
    for k, v in brut.items():
        if str(k).lstrip("-").isdigit() and isinstance(v, str) and v.strip():
            out.append((int(k), v.strip()))
    return sorted(out)


def signature(notes):
    return hashlib.sha1(json.dumps([VERSION, notes], ensure_ascii=False).encode()).hexdigest()[:10]


# ---------- 1. l'onglet ----------
def objet_menu():
    if not os.path.exists(MENU):
        return None
    return next((o for o in nb.env_of(MENU).objects
                 if o.type.name == "MonoBehaviour" and o.peek_name() == DONNEES), None)


def menu_original(obj):
    p = backup.backup_path(MENU)
    if not os.path.exists(p):
        return None
    o = next((x for x in UnityPy.load(p).objects if x.path_id == obj.path_id), None)
    return o.read_typetree() if o is not None else None


def a_entree(tt):
    return any(s.get("debug_name") == ENTREE for s in tt.get("m_submenus") or [])


def poser_entree(tt):
    subs = tt["m_submenus"]
    modeles = [i for i, s in enumerate(subs) if s.get("debug_name") == APRES]
    if len(modeles) != 1:
        return f"{len(modeles)} entrée(s) « {APRES} » au lieu d'une"
    i = modeles[0]
    e = copy.deepcopy(subs[i])
    e["debug_name"] = e["name"] = ENTREE
    e["ChildList"] = []
    pv = e["PropertyValue"]
    pv["m_displayValue"]["GameID"] = LIBELLE
    pv["m_panelIDRef"]["m_AssetGUID"] = PANEL_GUID
    pv["m_panelUID"] = PANEL_UID
    ev = pv["m_openEvent"]
    ev["m_panelReference"]["asset"]["m_AssetGUID"] = PANEL_GUID
    ev["m_argumentBindings"] = [
        {"name": "player", "path": {"m_path": "gameworldsubtabsandbookmarks.CurrentViewedPlayer"}, "method": 0},
        {"name": "team", "path": {"m_path": "gameworldsubtabsandbookmarks.CurrentViewedPlayer.team"}, "method": 0}]
    subs.insert(i + 1, e)
    return None


# ---------- 2. l'écran ----------
def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def _sources():
    s_txt = ni.src_tree(SOURCE_TEXTE)[0]
    if s_txt is None:
        return None
    textes = [r for r in s_txt.walk() if (s_txt.elem(r).get("m_FullTypeName") or "").endswith("SIText")]
    cadres = [r for r in s_txt.walk() if s_txt.name(r) == SOURCE_CADRE]
    s_vis, vis = ni.visible_model()
    if len(textes) < 2 or not cadres or vis is None:
        return None
    return s_txt, textes[0], textes[1], cadres[-1], s_vis, vis


def construire(t, notes):
    src = _sources()
    if src is None:
        return "morceaux de FM (textes, cadre, SIVisible) introuvables"
    s_txt, titre_src, corps_src, cadre_src, s_vis, vis = src
    grilles = [r for r in t.walk() if t.name(r) == GRILLE]
    attendus = [r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("BindingExpect")]
    if len(grilles) != 1:
        return f"{len(grilles)} grille(s) #{GRILLE} au lieu d'une"
    for r in attendus:
        t.sd(r)["Parameters"] = []
    g = grilles[0]
    parent = t.parent[g]
    index = t.children(parent).index(g)
    t.remove(g)

    # cadre : un VisualElement de FM vidé
    cadre = t.clone(cadre_src, parent, index, src=s_txt)
    for c in list(t.children(cadre)):
        t.remove(c)
    sm.no_styles(t, cadre)
    t.sd(cadre)["name"] = f"{PREFIXE}-{signature(notes)}"
    t.elem(cadre)["m_Classes"] = [MARQUE]
    t.styles.style(t, cadre, {"flex-grow": 1, "padding-left": 24, "padding-right": 24, "padding-top": 16,
                              "padding-bottom": 16})

    def texte(parent_, modele, contenu, nom, haut=0):
        x = t.clone(modele, parent_, None, src=s_txt)
        sm.no_styles(t, x)
        if contenu is None:
            return x
        ni.text_static(t, x, parent_, contenu)   # copie au texte fixe, puis l'originale retirée
        y = t.children(parent_)[-1]
        t.remove(x)
        t.sd(y)["name"] = nom
        if haut:
            t.styles.style(t, y, {"margin-top": haut})
        return y

    texte(cadre, titre_src, "Notes du joueur", f"{PREFIXE}Titre")
    texte(cadre, corps_src, "Identifiant FM du joueur :", f"{PREFIXE}IdLibelle", 8)
    ident = t.clone(corps_src, cadre, None, src=s_txt)
    sm.no_styles(t, ident)
    sd = t.sd(ident)
    sd["name"], sd["text"], sd["text_UxmlAttributeFlags"] = f"{PREFIXE}Id", "", 0
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = CHEMIN_ID
    sd["TextBinding"]["m_visualFunction"]["m_target"]["m_guid"] = ""
    sd["TextBinding"]["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []

    for uid, note in notes:
        v = ni.new_visible(t, s_vis, vis, cadre, None, f"{PREFIXE}Note{uid}",
                           ni.equal_binding(s_vis.sd(vis)["Binding"], CHEMIN_ID, uid))
        t.styles.style(t, v, {"margin-top": 16})
        texte(v, corps_src, note, f"{PREFIXE}Texte{uid}")
    texte(cadre, corps_src, f"Notes écrites hors du jeu, FM fermé ({len(notes)} joueur(s) noté(s)).",
          f"{PREFIXE}Rappel", 24)
    return None


def ecran_applique(notes):
    o = ouvrir(MODELE)
    return o is not None and any(o[3].name(r) == f"{PREFIXE}-{signature(notes)}" for r in marques(o[3]))


# ---------- commandes ----------
def cmd_appliquer():
    notes = lire_notes()
    obj = objet_menu()
    if obj is None:
        print(f"essai notes : données {DONNEES} introuvables (renommées par une mise à jour ?), rien enregistré")
        return
    tt_menu = obj.read_typetree()
    if a_entree(tt_menu) and ecran_applique(notes):
        print("essai notes : déjà appliqué")
    else:
        msgs, menu_change = [], False
        if not a_entree(tt_menu):
            menu_change = True
            tt_menu = menu_original(obj) or tt_menu
            err = poser_entree(tt_menu)
            if err:
                print(f"essai notes : {err}, rien enregistré")
                return
            msgs.append(f"onglet ajouté après « {APRES} » (fiche joueur)")
        if not ecran_applique(notes):
            o = ouvrir(MODELE, depart_original=True)
            if o is None or marques(o[3]):
                print(f"essai notes : {MODELE} introuvable ou sans original propre, rien enregistré")
                return
            bundle, vobj, tt, t = o
            err = construire(t, notes)
            if err:
                print(f"essai notes : {err}, rien enregistré")
                return
            t.finish()
            t.styles.save()
            vobj.save_typetree(tt)
            nb._dirty.add(bundle)
            msgs.append(f"écran Notes ({len(notes)} joueur(s) noté(s))")
        if menu_change:
            obj.save_typetree(tt_menu)
            nb._dirty.add(MENU)
        for m in msgs:
            print(f"essai notes : {m}")
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    msgs = []
    obj = objet_menu()
    if obj is not None and a_entree(obj.read_typetree()):
        orig = menu_original(obj)
        if orig is None:
            print(f"{DONNEES} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        else:
            obj.save_typetree(orig)
            nb._dirty.add(MENU)
            msgs.append(f"{DONNEES} remis d'origine")
    o = ouvrir(MODELE)
    if o is not None and marques(o[3]):
        bundle, vobj, tt, t = o
        orig = original(bundle, vobj)
        if orig is None:
            print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        else:
            vobj.save_typetree(orig)
            sheet = original(bundle, vobj, orig["inlineSheet"]["m_PathID"])
            if sheet is not None:
                t.styles.sh, t.styles.changed = sheet, True
                t.styles.save()
            nb._dirty.add(bundle)
            msgs.append(f"{MODELE} remis d'origine")
    if msgs:
        for m in msgs:
            print(f"essai notes : {m}")
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    obj = objet_menu()
    print(f"{DONNEES} :", "introuvable" if obj is None else
          ("onglet Notes posé" if a_entree(obj.read_typetree()) else "d'origine"))
    o = ouvrir(MODELE)
    print(f"{MODELE} :", "introuvable" if o is None else ("écran Notes posé" if marques(o[3]) else "d'origine"))
    print(f"notes : {len(lire_notes())} joueur(s) dans {NOTES}")


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
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
