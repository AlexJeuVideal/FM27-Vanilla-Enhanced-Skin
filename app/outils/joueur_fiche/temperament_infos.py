"""Fiche joueur, colonne Infos : logo du tempérament (Bosseur / Penseur / Relaxé / Leader) collé à droite du texte
de « Personnalité » (suit sa longueur), calé sur la ligne du texte, nom au survol (infobulle de FM). Tous les modes.
(v1-v5 : Medium / Small = titre + logo + nom à droite ; le joueur, 2026-11-13 : « le logo à droite de la perso
c'est mieux », partout, taille FM gardée.)
Aussi dans l'infobulle du joueur (survol, PlayerAttributesTooltipBlock, ligne Personnalité) : logo seul, sans nom au
survol (une infobulle dans l'infobulle la ferme).
Logo et nom recopiés du bloc FM PlayerInfoBlock_4x6 (MindsetFrame : Player.Mindset, IconSmall / Name).
Pas dans la vue FM Guru (fonction hors AVEC_GURU : la vue Guru refait le gros bloc depuis l'original).

Repérage par contenu (ligne Personnalité, cadre MindsetFrame) : valable après une mise à jour du jeu.
Retirer : le texte Personnalité est remis à sa place, notre rangée enlevée (pas besoin des originaux).
Usage (jeu fermé) : temperament_infos.py appliquer [--dry-run] | retirer [--dry-run] | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import Tree, Styles, PROPRIETES, no_styles  # noqa: E402
from elements import src_tree, copy_usings, typ, move, plain  # noqa: E402
import style_mediatique as sm  # noqa: E402  (ligne Personnalité)

for _k, _v in {"margin-left": (131091, 3), "flex-shrink": (131085, 2), "align-items": (131073, 7),
               "top": (131104, 3)}.items():
    PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES (changer la construction -> augmenter VERSION)
# =====================================================================================================
ECART = 6           # px entre le texte de Personnalité et le logo
REMONTE = 1         # px : logo remonté. Mesures (milieu du logo / milieu des lettres hors jambages, px écran) :
                    # 0 -> ~1 trop bas (v5) ; 3 -> ~2,5 trop haut (v6, 4 captures du joueur) ; ~1,2 px écran par
                    # px FM -> 1 = centré
# =====================================================================================================

VERSION = 7         # v6 : logo seul à droite de la perso dans tous les modes, taille FM, remonté ; v7 : 1 px au
                    # lieu de 3 (trop haut)
ETIRE = "align-self-stretch-class"   # classe FM posée par v4 / v5 sur le conteneur de la ligne (retirée)
MODELE = "PlayerAttributesLargeBlock"     # fiche (aussi : source de l'infobulle de FM)
INFOBULLE = "PlayerAttributesTooltipBlock"   # infobulle du joueur (survol), 2026-11-13 (le joueur)
MODELES = {MODELE: True, INFOBULLE: False}   # modèle : nom au survol du logo
# vue FM Guru : jamais posée, ni fiche ni infobulle (hors AVEC_GURU ; le joueur, 2026-11-13)
SOURCE = "PlayerInfoBlock_4x6"            # bloc FM qui affiche déjà Tempérament (logo + nom)
SOURCE_CADRE = "MindsetFrame"
NOM = "UIPickerTemperamentInfos"          # v1-v5 : rangée [ligne Personnalité][Tempérament M / S] ; préfixe
NOM_TEXTE = NOM + "Texte"                 # rangée [texte Personnalité][logo]
CLASSE = f"uipicker-temperament-infos-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "temperament_infos.actif")


def wrappers(t):
    return [r for r in t.walk() if t.name(r) in (NOM, NOM_TEXTE)]


def defaire(t):
    """texte remis à la place de notre rangée (v1 : la ligne Personnalité entière)"""
    for w in wrappers(t):
        p = t.parent[w]
        if t.name(w) == NOM and ETIRE in (t.elem(p).get("m_Classes") or []):
            t.elem(p)["m_Classes"].remove(ETIRE)   # posée par nous (FM : aucune classe)
        i = t.children(p).index(w)
        for k in [k for k in t.children(w) if not t.name(k).startswith(NOM)]:
            move(t, k, p, i)
            i += 1
        t.remove(w)


def tooltip_source(t):
    """élément Tooltip de FM (un seul SIText dedans) : ce modèle, sinon son original"""
    def cherche(s):
        return next((r for r in s.walk() if typ(s, r).endswith("Tooltip") and len(s.children(r)) == 1
                     and typ(s, s.children(r)[0]).endswith("SIText")), None)
    r = cherche(t)
    if r is not None:
        return t, r
    import hierarchie_pyramide as hp
    o = hp.ouvrir(MODELE, depart_original=True)
    if o is None:
        return None, None
    return o[3], cherche(o[3])


def construire(t, survol_nom=True):
    """survol_nom : nom au survol du logo (fiche) ; pas dans l'infobulle du joueur (une infobulle dans l'infobulle
    la ferme : piège vu avec les caractéristiques, infobulle_pieds v21)"""
    value, frame = sm.personality_row(t)
    if value is None:
        return ["ligne Personnalité introuvable, ignoré"]
    s = src_tree(SOURCE)
    cadre = s and next((r for r in s.walk() if s.name(r) == SOURCE_CADRE), None)
    if cadre is None or len(s.children(cadre)) < 2:
        return [f"{SOURCE} : {SOURCE_CADRE} introuvable (le jeu a changé ?), ignoré"]
    ligne_src = s.children(cadre)[1]
    image_src = next((r for r in s.children(ligne_src) if typ(s, r).endswith("SIImage")), None)
    nom_src = next((r for r in s.children(ligne_src) if typ(s, r).endswith("SIText")), None)
    tip_s, tip = tooltip_source(t)
    if image_src is None or nom_src is None or tip is None:
        return ["logo / nom du tempérament ou infobulle de FM introuvables, ignoré"]

    # rangée [texte Personnalité][logo] dans la ligne : le logo suit la longueur du texte, centré sur la ligne
    wt = plain(t, frame, t.children(frame).index(value), ["row-direction-normal", CLASSE], NOM_TEXTE)
    t.elem(wt)["m_RuleIndex"] = -1
    t.styles.style(t, wt, {"align-items": "center"})
    move(t, value, wt)
    t.styles.style(t, value, {"flex-shrink": 1})
    survol = plain(t, wt, None, [], NOM + "Survol")
    t.elem(survol)["m_RuleIndex"] = -1
    t.styles.style(t, survol, {"flex-shrink": 0, "margin-left": ECART, "top": -REMONTE})   # remonté sans
    img = t.clone(image_src, survol, src=s)                                                # changer la ligne
    no_styles(t, img)
    t.elem(img)["m_Classes"] = []
    copy_usings(t, s, cadre)
    if not survol_nom:
        return ["logo du tempérament à droite de Personnalité"]
    bulle = t.clone(tip, survol, src=tip_s)
    no_styles(t, bulle)
    texte = t.children(bulle)[0]
    t.sd(texte)["name"] = ""
    t.sd(texte)["TextBinding"] = json.loads(json.dumps(s.sd(nom_src)["TextBinding"]))
    return ["logo du tempérament à droite de Personnalité (nom au survol)"]


def a_jour(t):
    """notre seule rangée, version actuelle, autour du texte Personnalité"""
    ws = wrappers(t)
    return (len(ws) == 1 and t.name(ws[0]) == NOM_TEXTE and CLASSE in (t.elem(ws[0]).get("m_Classes") or [])
            and any(sm.text_path_ends(t, k, "Personality") for k in t.children(ws[0])))


def travail(t, modele):
    if a_jour(t):
        return []
    defaire(t)   # ancienne version, ou rangée recopiée par un autre script (ligne Média)
    return construire(t, survol_nom=MODELES[modele])


def ecrire(fn):
    """fn(t, modele) -> messages, sur chaque modèle de MODELES ; un seul enregistrement à la fin"""
    change = False
    for modele in MODELES:
        bundle, obj, tt = nb.find_vta(modele)
        if tt is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        t = Tree(tt)
        t.styles = Styles(bundle, tt)
        msgs = fn(t, modele)
        for m in msgs:
            print(f"{modele} : {m}")
        if not msgs or all("ignoré" in m for m in msgs):
            continue
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        change = True
    if change:
        nb.save_all()
    return change


def cmd_appliquer():
    if not ecrire(travail):
        print("rien à changer")
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION}, f)


def cmd_retirer():
    def fn(t, modele):
        if not wrappers(t):
            return []
        defaire(t)
        return ["Tempérament retiré, ligne Personnalité remise"]
    if not ecrire(fn):
        print("rien à retirer")
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)


def cmd_etat():
    for modele in MODELES:
        _, _, tt = nb.find_vta(modele)
        ws = [] if tt is None else wrappers(Tree(tt))
        print(f"{modele} : " + ("introuvable" if tt is None else
                                f"tempérament dans Infos : {'oui' if ws else 'non'}"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
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
            print("tempérament dans Infos : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
