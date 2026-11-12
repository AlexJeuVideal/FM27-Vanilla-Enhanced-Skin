"""Écran Effectif > Vue d'ensemble (liste avec « Sél. », En possession / Hors possession) : boutons FM
« Entraînement », « Entraînement individuel » et « Programme des rencontres » à droite du menu des vues, pour l'équipe
affichée, seulement pour les équipes du club du joueur — les mêmes que sur l'écran Effectif de l'équipe
(effectif_boutons_entrainement.py).

v1 (2026-11-12) : un bouton par équipe du club (Réserve, U19…) ; vue en jeu, remplacée par les 3 boutons (v2,
demande du joueur : « pas les équipes »).
v3 (2026-11-12, demande du joueur : fusion avec l'ajout Kinito 26.10) : tout est fait par le script de Kinito
outils\\kinito\\kinito_effectif_vue.py (gardé tel quel, lancé d'ici) :
- Vue d'ensemble : les 3 boutons + des liens vers les autres équipes du club à la suite d'« Équipe première » ;
- écran Effectif de chaque équipe : les boutons des équipes à droite de « Avec / Sans le ballon » ;
- option « boutons_effectif » (options.py) : les boutons d'Alex en icônes (choix de base) ou écrits, partout où ils
  sont (Vue d'ensemble, écran Effectif = effectif_boutons_entrainement, Tactiques = tactiques_boutons). Ces deux
  fonctions réécrivent leur modèle seules : catalogue.SUIVANTS relance ce script après elles.

v4 (2026-11-12, demande du joueur) : écran Effectif, mode Large, texte Normal / Grand / Plus grand : la barre des postes
(GB … R15) passait sur deux lignes et décalait la rangée des équipes (« Youth Candid » coupé) -> boutons R11 à R15
masqués dans ce cas seulement (Medium / Small, texte Petit : tous gardés). Cellule FM TacticsPositionOverviewWidgetItem
(barre des postes de l'écran Effectif ET de la Vue d'ensemble, seuls à la citer) : son contenu (#DragObject) en 3 copies,
chacune sous une condition (pas de « ou » dans les SIVisible) : index <= 20 (GB, 10 titulaires, R1-R10) / index > 20 et
mode > 0 / index > 20, mode 0 et texte < 100.

Modèles touchés (par kinito_effectif_vue) : SquadOverviewTableBlock, ClubBigIconAndTextAndLeagueCell et CompNationCell
(seul propriétaire, repart des originaux) ; TeamSquadBlock et TacticalPlannerHeader (partagés : ses éléments seulement).
Par ce script (v4) : TacticsPositionOverviewWidgetItem (seul propriétaire, repart de l'original, retirer le remet).

Usage (jeu fermé) : effectif_equipes.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import ouvrir, typ  # noqa: E402
from notes_installations import make_binding, new_visible, visible_model  # noqa: E402
import elements as el  # noqa: E402
import options  # noqa: E402

MODELE = "SquadOverviewTableBlock"
BOUTON = "ClubBigIconAndTextAndLeagueCell"
PREFIXES_V2 = ("UIPickerEffectifEquipes", "UIPickerBoutonEffectif")   # v1 / v2 (avant Kinito) : remis d'origine
MARKER = os.path.join(backup.BACKUP_DIR, "effectif_equipes.actif")

# v4 : barre des postes, R11 à R15 masqués en mode Large avec le texte Normal ou plus grand
POSTES = "TacticsPositionOverviewWidgetItem"
VERSION_POSTES = 1
NOM_POSTES = f"UIPickerPostesCourts-v{VERSION_POSTES}"
INDEX_MAX = 20                  # binding.Index : 0 GB, 1-10 titulaires, 11-20 = R1-R10, 21+ = R11 et plus
MODE = "settings.AdaptiveScalingLevelIndex"   # 0 Large
TEXTE = "settings.TextScaling"                # 85 Petit, 100 Normal, 110 Grand, 120 Plus grand
TEXTE_MIN = 100                 # masqués à partir de cette taille de texte


def kinito():
    """le script de Kinito, réglé par l'option (icônes / écrits) : variable lue par son icones()"""
    os.environ["KINITO_BOUTONS"] = options.get("boutons_effectif")
    import kinito_effectif_vue as kev
    return kev


def retirer_v2():
    """anciennes versions de ce script (avant Kinito) : modèles remis d'origine"""
    fait = False
    for m in (MODELE, BOUTON):
        o = ouvrir(m)
        if o is None or not any(o[3].name(r).startswith(PREFIXES_V2) for r in o[3].walk()):
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
        print(f"{m} : ancienne version remise d'origine")
    if fait:
        nb.save_all()


def postes_marques(t):
    return [r for r in t.walk() if t.name(r).startswith("UIPickerPostesCourts")]


def construire_postes(t, s, vis):
    """#DragObject en 3 copies, chacune sous sa chaîne de SIVisible (conditions « et » imbriquées)"""
    drag = next((r for r in t.walk() if t.name(r) == "DragObject" and typ(t, r).endswith("FMDraggableObject")), None)
    if drag is None:
        return "#DragObject introuvable"
    parent = t.parent[drag]
    index = t.children(parent).index(drag)
    plus = (4, "binding.Index", INDEX_MAX)
    chaines = [[(1, "binding.Index", INDEX_MAX)],                 # GB, titulaires, R1-R10 : toujours
               [plus, (4, MODE, 0)],                              # R11+ : Medium / Small
               [plus, (2, MODE, 0), (0, TEXTE, TEXTE_MIN)]]       # R11+ : Large, texte Petit
    for k, chaine in enumerate(chaines):
        p, i = parent, index + k
        for j, (op, chemin, valeur) in enumerate(chaine):
            v = new_visible(t, s, vis, p, i, f"{NOM_POSTES}-{k}-{j}",
                            make_binding(s.sd(vis)["Binding"], op, [chemin], valeur))
            t.sd(v)["name_UxmlAttributeFlags"] = 1
            t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 0, "align-self": "stretch"})
            p, i = v, None
        if k < len(chaines) - 1:
            t.clone(drag, p)
        else:
            el.move(t, drag, p)
    return None


def appliquer_postes():
    o = ouvrir(POSTES)
    if o is None:
        print(f"{POSTES} introuvable (renommé par une mise à jour ?), barre des postes ignorée")
        return
    if any(t_.startswith(NOM_POSTES) for t_ in (o[3].name(r) for r in postes_marques(o[3]))):
        print(f"barre des postes : déjà appliqué (v{VERSION_POSTES})")
        return
    travail = ouvrir(POSTES, depart_original=True)
    s, vis = visible_model()
    if travail is None or postes_marques(travail[3]) or vis is None:
        print("barre des postes : original ou SIVisible de FM introuvable, rien fait")
        return
    bundle, obj, tt, t = travail
    erreur = construire_postes(t, s, vis)
    if erreur:
        print(f"barre des postes : {erreur}, rien fait")
        return
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"barre des postes : R11 à R15 masqués en mode Large avec le texte Normal ou plus grand (v{VERSION_POSTES})")


def retirer_postes():
    o = ouvrir(POSTES)
    if o is None or not postes_marques(o[3]):
        return
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{POSTES} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{POSTES} : remis d'origine (barre des postes complète)")


def cmd_appliquer():
    kinito().cmd_appliquer()   # repart des originaux : remplace aussi les anciennes versions de ce script
    appliquer_postes()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    kinito().cmd_retirer()
    retirer_v2()
    retirer_postes()


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
        kinito().cmd_etat()
        print("boutons :", options.libelle("boutons_effectif", options.get("boutons_effectif")))
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("boutons de la vue d'ensemble : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
