"""Cercles d'amis (Effectif > Dynamique de groupe > Cercles d'amis) en cartes joueur, comme dans FM24.

Pour chaque cercle (Noyau dur, Secondaire A, Secondaire B, Autres) :
  [ logo + titre FM ]   [carte] [carte] [carte] [carte] ...
  [ description FM  ]   [carte] [carte] ...                 (cartes à la ligne dans la place restante)
Carte = celle de la pyramide de la hiérarchie (photo, « i » d'infobulle, nom, personnalité, brassard ; clic = profil ;
taille selon le mode d'affichage FM) + logo de hiérarchie en haut à gauche (Leader, Très influent, Influent…).
Le tableau FM et sa sélection disparaissent (plus de panneau joueur à droite, ni du menu « Parler à » qui en dépend).

Modèles touchés (ce script est leur seul propriétaire, appliquer repart toujours des originaux sauvegardés) :
- SquadSocialGroupsBlock : l'écran ; chaque tableau devient une liste à la ligne (WrappedObjectList de TeamMeetingBlock).
- NonClickablePortraitNameCell : cellule de tableau FM inutilisée (citée par aucun bundle), réécrite en carte.
  (la pyramide utilise PlayerHierarchyCell : elle n'est pas touchée ici)

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\effectif\\cercles_amis_cartes.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\effectif\\cercles_amis_cartes.py retirer
  .venv\\Scripts\\python.exe outils\\effectif\\cercles_amis_cartes.py etat
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (carte joueur, liste à la ligne, ouverture des modèles)
from hierarchie_pyramide import typ, src_tree, path_arg, ouvrir, POURCENT  # noqa: E402
from notes_installations import first, decode_args, encode_args, _enc_varint  # noqa: E402
from arbre import no_styles  # noqa: E402
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
DISPOSITION = "cote"          # "cote" : titre + description à gauche, cartes à droite (FM24)
                              # "dessus" : titre + description au-dessus des cartes (comme FM26)
TITRE_LARGEUR = 300           # px, largeur de la colonne titre + description ("cote")
LOGO_HIERARCHIE = True        # logo de hiérarchie en haut à gauche de la carte
PERSONNALITE = True           # personnalité sous le nom
# taille des cartes : celle de la pyramide (hierarchie_pyramide.MODES / TEXTE_PLUS_GRAND)
# =====================================================================================================

VERSION = 2   # v2 (2026-11-12) : reportcontextteam = team donné aux cartes (fiche complète au clic, comme pyramide v11)
MODELE = "SquadSocialGroupsBlock"
CARTE = "NonClickablePortraitNameCell"
GUID_CARTE = "869034f386855d149b8b7f399b173e92"   # NonClickablePortraitNameCell (catalogue Addressables)
CERCLES = ["CoreSocialGroupPlayersList", "SecondarySocialGroup1PlayersList", "SecondarySocialGroup2PlayersList",
           "OtherSocialGroupPlayersList"]
LOGO_SOURCE = "hierarchy-influence-icon"   # SIImage de SquadSocialGroupsBlock (panneau du joueur sélectionné)
PREFIXE = "UIPickerCercles"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
NOM_CARTE = f"UIPickerCarteCercle-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "cercles_amis_cartes.actif")

sm.PROPRIETES.setdefault("left", (131089, 3))
sm.PROPRIETES.setdefault("align-items", (131073, 7))


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE) or t.name(r).startswith("UIPickerCarteCercle")]


# ---------- la carte (carte de la pyramide + logo de hiérarchie) ----------
def logo_hierarchie(t, carte, logo, ecart):
    """logo FM de la hiérarchie (image d'après person.HierarchyInfluenceCategory) en haut à gauche de la carte"""
    s, src = logo
    x = t.clone(src, carte, src=s)
    no_styles(t, x)
    t.sd(x)["name"] = ""
    b = copy.deepcopy(t.sd(x)["Binding"])
    vf = b["m_visualFunction"]
    args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0].endswith(b"GenericVisualArg`1[SI.Bindable.BindingPath]"):
            p = b"binding.HierarchyInfluenceCategory"
            a[1] = b"\x01" + _enc_varint(len(p)) + p
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.sd(x)["Binding"] = b
    t.elem(x)["m_Classes"] = [c for c in t.elem(x).get("m_Classes") or [] if c.startswith("game-concepts-")]
    t.styles.style(t, x, {"position": "absolute", "top": ecart + 2, "left": ecart + 2})


def construire_carte(t, src, logo):
    root = t.children(t.tt["m_VisualTree"]["rid"])
    expect = next((r for r in root if typ(t, r) == "BindingExpect"), None)
    if expect is None:
        return ["modèle de carte introuvable"]
    t.elem(expect)["m_Classes"] = []
    for k in list(t.children(expect)):
        t.remove(k)
    # contexte d'équipe de la fiche ouverte par la carte, lu dans le bloc (voir construire_bloc)
    params = t.sd(expect).setdefault("Parameters", [])
    if not any(p["name"] == hp.CONTEXTE for p in params):
        p = copy.deepcopy(params[0])
        p.update({"name": hp.CONTEXTE, "type": {"id": hp.TYPE_EQUIPE}, "isOptional": 1})
        params.append(p)
    remplir = hp.remplir_carte

    def remplir_cercle(t_, parent, src_, nom, largeur, photo, taille, ecart, **kw):
        c = remplir(t_, parent, src_, nom, largeur, photo, taille, ecart, **kw)
        if LOGO_HIERARCHIE:
            logo_hierarchie(t_, c, logo, ecart)
        return c

    hp.remplir_carte = remplir_cercle   # cartes_par_mode appelle hp.remplir_carte
    try:
        hp.cartes_par_mode(t, expect, src, NOM_CARTE, perso=PERSONNALITE)
    finally:
        hp.remplir_carte = remplir
    return ["carte : celle de la pyramide" + (" + logo de hiérarchie" if LOGO_HIERARCHIE else "")
            + ("" if PERSONNALITE else ", sans personnalité")]


# ---------- l'écran (SquadSocialGroupsBlock) ----------
def construire_bloc(t):
    lst = src_tree(hp.LISTE_SOURCE)
    modele_liste = lst and first(lst, lambda r: lst.name(r) == hp.LISTE and typ(lst, r) == "WrappedObjectList")
    if modele_liste is None:
        return ["liste à la ligne de FM introuvable"]
    msgs = []
    for k, nom in enumerate(CERCLES):
        chemin = f"Team.SocialGroupList.{nom}"
        rm = next((r for r in t.walk() if typ(t, r) == "BindingRemapper"
                   and any(m["to"]["m_path"] == chemin for m in t.sd(r).get("Mappings") or [])), None)
        # avant la MAJ du 2026-11-12 : switch (#NoSelection / #HasSelection) de deux tableaux ; depuis : un seul tableau
        switch = rm and (next((r for r in t.walk(rm) if typ(t, r) == "BindableSwitchElement"), None)
                         or next((r for r in t.walk(rm) if typ(t, r) == "StreamedTable"), None))
        if switch is None:
            msgs.append(f"cercle {nom} introuvable")
            continue
        if not any(m["from"] == hp.CONTEXTE for m in t.sd(rm)["Mappings"]):
            t.sd(rm)["Mappings"].append(hp.contexte_equipe())
        frame = t.parent[switch]
        titre = t.children(frame)[0]
        w = t.clone(modele_liste, frame, t.children(frame).index(switch), src=lst)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = NOM_RACINE if k == 0 else f"{PREFIXE}-{k}"
        sd["name_UxmlAttributeFlags"] = 1
        sd["ItemTemplate"] = {"m_AssetGUID": GUID_CARTE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], chemin)
        sd["ItemParamName"] = "binding"
        sd["ItemUssClassName"] = "flex-no-shrink-class"
        t.elem(w)["m_Classes"] = []
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "wrap", "justify-content": "flex-start",
                              "flex-grow": 1, "flex-shrink": 1, "min-width": 0})
        t.remove(switch)
        if DISPOSITION == "cote":
            t.elem(frame)["m_Classes"] = [c for c in t.elem(frame).get("m_Classes") or []
                                          if not c.startswith("row-direction")] + ["row-direction-normal"]
            t.styles.style(t, frame, {"align-items": "flex-start"})
            t.styles.style(t, titre, {"width": TITRE_LARGEUR, "flex-shrink": 0, "margin-right": 16})
        msgs.append(f"{nom} : cartes" + (" à droite du titre" if DISPOSITION == "cote" else " sous le titre"))
    return msgs


# ---------- commandes ----------
def cmd_appliquer():
    actuels = {m: ouvrir(m) for m in (MODELE, CARTE)}
    if None in actuels.values():
        print("modèles des cercles d'amis introuvables (renommés par une mise à jour ?), ignoré")
        return
    t_bloc, t_carte = actuels[MODELE][3], actuels[CARTE][3]
    if any(t_bloc.name(r) == NOM_RACINE for r in marques(t_bloc)) and \
            any(t_carte.name(r) == NOM_CARTE for r in marques(t_carte)):
        print("cercles d'amis en cartes : déjà appliqué")
    else:
        ancien = bool(marques(t_bloc) or marques(t_carte))
        travail = {m: ouvrir(m, depart_original=True) for m in (MODELE, CARTE)}
        if any(marques(v[3]) for v in travail.values()):
            print("cercles d'amis : pas de sauvegarde d'origine propre, ignoré")
            return
        src = hp.Sources()
        t_src = travail[MODELE][3]
        logo = (t_src, first(t_src, lambda r: t_src.name(r) == LOGO_SOURCE))
        if not src.ok() or logo[1] is None:
            print("cercles d'amis : morceaux de FM (carte, logo de hiérarchie) introuvables, rien enregistré")
            return
        msgs = construire_carte(travail[CARTE][3], src, logo) + construire_bloc(travail[MODELE][3])
        msgs += ["ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"cercles d'amis : {m}")
        if any("introuvable" in m for m in msgs):
            print("cercles d'amis : rien enregistré")
            return
        for bundle, obj, tt, t in travail.values():
            t.finish()
            t.styles.save()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for m in (MODELE, CARTE):
        o = ouvrir(m)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{m} : remis d'origine")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for m in (MODELE, CARTE):
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        cible = NOM_RACINE if m == MODELE else NOM_CARTE
        etat = "à jour" if any(t.name(r) == cible for r in marques(t)) else "ANCIENNE version"
        print(f"{m} : " + (f"appliqué ({etat}, v{VERSION})" if marques(t) else "d'origine"))
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
            print("cercles d'amis en cartes : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
