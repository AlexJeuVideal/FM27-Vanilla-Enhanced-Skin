"""Fiche joueur : ligne « Style médiatique » sous « Personnalité », Réputation en bas de la colonne Infos, pieds
gauche / droit écartés sous le tableau d'attributs.

1. Gros bloc d'attributs (Rapport joueur) : ajoute la ligne "Style médiatique" sous "Personnalité" (titre traduit par
   le jeu, valeur person.MediaHandling), avec le même écart entre les lignes que Taille / Réputation.
2. Tableau d'attributs : "Pied gauche / Pied droit" répartis sur la largeur.
(Infobulle du joueur : joueur_infobulle\\infobulle_pieds.py, qui réutilise les fonctions de ce script.)

Les éléments sont repérés par leur contenu (données affichées), pas par des numéros internes :
le script reste valable après une mise à jour du jeu.

Usage (jeu fermé) : style_mediatique.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)
import sauvegarde_originaux as backup  # noqa: E402
from arbre import Tree, named, Styles  # noqa: E402,F401
import lancer  # noqa: E402  (retirer : tout le skin refait après la restauration)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (True = activé, False = désactivé)
# =====================================================================================================
STYLE_MEDIATIQUE = True                      # ligne "Style médiatique" sous "Personnalité"
STYLE_MEDIATIQUE_MODELES = [
    "PlayerAttributesLargeBlock",            # gros bloc du Rapport joueur
    # "PlayerAttributesStandardBlock",
    # "PlayerAttributesSmallBlock",
    # "PlayerAttributesCompactBlock",
]
REPUTATION_EN_BAS = True                     # Infos : Taille, Personnalité, Style médiatique, puis Réputation en bas
                                             # (mêmes blocs que STYLE_MEDIATIQUE_MODELES)
RAPPORT_PIEDS_CENTRES = True                 # pieds centrés dans le gros bloc de la fiche joueur (tableau d'attributs)
RAPPORT_PIEDS_ECARTES = True                 # fiche joueur : pieds répartis sur la largeur (remplace le centrage)
                                             # (options d'entraînement sous les attributs : voir hors_defaut.py)
# =====================================================================================================

TITRE_MODELE = "PersonPersonalBlock"       # bloc où FM affiche déjà le titre traduit "Media Handling Style"
TITRE_DONNEE = "Person.MediaHandling"
MARKER = os.path.join(backup.BACKUP_DIR, "style_mediatique.actif")
PIEDS_SOURCE = "AttributesTableTemplate"     # tableau d'attributs du Rapport joueur : contient le bloc des deux pieds
PIEDS_MODELE = "PlayerReportFootednessBlock"
NOM_PIEDS_ECARTES = "UIPickerPiedsEcartes"


# ---------- 1. style médiatique ----------
def find_title_binding():
    """liaison du titre traduit "Media Handling Style" : le texte qui précède la valeur Person.MediaHandling"""
    _, _, tt = nb.find_vta(TITRE_MODELE)
    if tt is None:
        sys.exit(f"{TITRE_MODELE} introuvable (mise à jour du jeu ?)")
    t = Tree(tt)
    for rid in t.walk():
        kids = t.children(rid)
        for i, k in enumerate(kids):
            if (t.binding(k, "TextBinding") or "").lower() == TITRE_DONNEE.lower() and i > 0 and t.sd(kids[i - 1]).get("TextBinding"):
                return copy.deepcopy(t.sd(kids[i - 1])["TextBinding"])
    sys.exit(f"titre 'Media Handling Style' introuvable dans {TITRE_MODELE} (le jeu a changé)")


def personality_row(t):
    """(valeur, cadre) de la ligne Personnalité (cadre de FM : la rangée de temperament_infos autour du texte est
    sautée)"""
    for rid in t.walk():
        p = t.binding(rid, "TextBinding")
        if p and p.split(".")[-1].lower() == "personality":
            cadre = t.parent[rid]
            while t.name(cadre).startswith("UIPickerTemperamentInfos") and cadre in t.parent:
                cadre = t.parent[cadre]
            return rid, cadre
    return None, None


def has_media(t):
    return any((t.binding(r, "TextBinding") or "").split(".")[-1].lower() == "mediahandling" for r in t.walk())


def gap_class(t, frame):
    """classe d'écart utilisée par les lignes au-dessus (margin-bottom-...)"""
    node = frame
    while node in t.parent:
        p = t.parent[node]
        kids = t.children(p)
        i = kids.index(node)
        if i > 0:
            for c in t.elem(kids[i - 1]).get("m_Classes") or []:
                if c.startswith("margin-bottom"):
                    return c
        node = p
    return None


def add_media(t, title):
    msgs = []
    value, frame = personality_row(t)
    if value is None:
        return ["ligne Personnalité introuvable, ignoré"]
    if not has_media(t):
        parent = t.parent[frame]
        new = t.clone(frame, parent, t.children(parent).index(frame) + 1)   # copié AVANT l'écart : il n'en hérite pas
        for r in t.walk(new):
            d = t.sd(r)
            if d.get("name"):
                d["name"] = d["name"].replace("Personality", "MediaHandling")
            tb = d.get("TextBinding")
            if not tb:
                continue
            if tb.get("m_kind") == 1 and tb["m_direct"]["Path"]["m_path"].split(".")[-1].lower() == "personality":
                old = tb["m_direct"]["Path"]["m_path"]
                tb["m_direct"]["Path"]["m_path"] = old[: -len("Personality")] + "MediaHandling"
                d["DebugDisplay"] = "Media-friendly"
            else:
                d["TextBinding"] = copy.deepcopy(title)
                d["DebugDisplay"] = "Media Handling Style"
        msgs.append("ligne 'Style médiatique' ajoutée sous Personnalité")
    gap = gap_class(t, frame)
    classes = t.elem(frame).setdefault("m_Classes", [])
    if gap and gap not in classes:
        classes.append(gap)
        msgs.append(f"écart sous Personnalité ({gap}, comme les lignes au-dessus)")
    return msgs


def text_path_ends(t, rid, suffix):
    """True si le texte affiche une donnée finissant par .<suffix> (en direct ou via une fonction)"""
    b = t.sd(rid).get("TextBinding")
    if not isinstance(b, dict):
        return False
    if b.get("m_kind") == 1:
        paths = [b["m_direct"]["Path"]["m_path"]]
    else:
        paths = nb.paths_in(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    return any(p.split(".")[-1].lower() == suffix.lower() for p in paths)


def ancestors(t, rid):
    out = [rid]
    while out[-1] in t.parent:
        out.append(t.parent[out[-1]])
    return out


def reputation_last(t):
    """met la ligne Réputation en dernier dans la colonne Infos, et garde le même écart entre les lignes"""
    value, _ = personality_row(t)
    rep = next((r for r in t.walk() if text_path_ends(t, r, "Reputation")), None)
    if value is None or rep is None:
        return ["lignes Personnalité / Réputation introuvables, ordre inchangé"]
    pa, ra = ancestors(t, value), ancestors(t, rep)
    common = next(a for a in pa if a in ra)                      # conteneur des lignes de la colonne Infos
    rep_row = ra[ra.index(common) - 1]
    rows = t.children(common)
    msgs = []
    if rows[-1] != rep_row:
        gap = next((c for r in rows for c in t.elem(r).get("m_Classes") or [] if c.startswith("margin-bottom")), None)
        kids = t.elem(common)["m_Children"]
        kids[:] = [k for k in kids if k["rid"] != rep_row] + [{"rid": rep_row}]
        msgs.append("Réputation déplacée en bas (Taille, Personnalité, Style médiatique, Réputation)")
        if gap:   # écart sous chaque ligne sauf la dernière, comme à l'origine
            rows = t.children(common)
            for r in rows:
                cls = t.elem(r).setdefault("m_Classes", [])
                if r != rows[-1] and gap not in cls:
                    cls.append(gap)
                elif r == rows[-1] and gap in cls:
                    cls.remove(gap)
    return msgs



def spread_report_feet(t):
    """fiche joueur : "Pied gauche / Pied droit" répartis sur la largeur (espaces égaux, sans toucher les bords).
    Le bloc est un modèle inclus dont on ne peut pas changer les classes : on recopie son contenu à sa place."""
    targets = [r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == PIEDS_MODELE]
    if not targets:
        return []
    _, _, stt = nb.find_vta(PIEDS_MODELE)
    if stt is None:
        return [f"{PIEDS_MODELE} introuvable, pieds non écartés"]
    s = Tree(stt)
    frame = next((r for r in s.walk() if s.name(r) == "FootednessFrame"), None)
    if frame is None:
        return ["bloc des pieds introuvable, pieds non écartés"]
    for r in targets:
        parent = t.parent[r]
        new = t.clone(frame, parent, t.children(parent).index(r), src=s)
        t.remove(r)
        t.sd(new)["name"] = NOM_PIEDS_ECARTES
        t.elem(new)["m_Classes"] = ["row-direction-normal", "justify-content-space-evenly", "align-self-stretch-class"]
        for k in t.children(new):   # chaque pied à la taille de son contenu
            t.elem(k)["m_Classes"] = [c for c in t.elem(k).get("m_Classes") or []
                                      if c not in ("flex-grow-class", "margin-right-global-gap-large")]
    aliases = {s.elem(r).get("m_TemplateAlias") for r in s.walk(frame)} - {None, ""}
    for u in stt.get("m_Usings") or []:
        if u.get("alias") in aliases and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
            t.tt["m_Usings"].append(copy.deepcopy(u))
    return [f"pieds écartés ({len(targets)} bloc(s))"]


def center_report_feet(t):
    """gros bloc de la fiche joueur : centre le bloc "Pied gauche / Pied droit" (versions champ et gardien)"""
    if RAPPORT_PIEDS_ECARTES:
        return spread_report_feet(t)
    msgs = []
    for r in t.walk():
        if t.elem(r).get("m_TemplateAlias") != PIEDS_MODELE:
            continue
        cls = t.elem(r).setdefault("m_Classes", [])
        if RAPPORT_PIEDS_CENTRES and "align-items-center" not in cls:
            cls.append("align-items-center")
            msgs.append("pieds centrés")
        elif not RAPPORT_PIEDS_CENTRES and "align-items-center" in cls:
            cls.remove("align-items-center")
            msgs.append("pieds recalés à gauche")
    return msgs

# ---------- commandes ----------
def appliquer_modeles(models, travail, marker):
    """models : modèles à traiter ; travail(model, t) -> messages. Écrit le marqueur s'il y a eu un changement."""
    changed = 0
    for model in models:
        bundle, obj, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        t = Tree(tt)
        t.styles = Styles(bundle, tt)   # feuille intégrée (règles recopiées : bouton du polygone de l'infobulle)
        msgs = travail(model, t)
        done = [m for m in msgs if "introuvable" not in m and "inchangé" not in m]
        for m in msgs:
            print(f"{model} : {m}")
        if not done:
            if not msgs:
                print(f"{model} : déjà appliqué")
            continue
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        changed += 1
    if changed:
        nb.save_all()
        if not nb.DRY_RUN:
            with open(marker, "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)
    else:
        print("rien à changer")


def media_et_reputation(model, t, title):
    msgs = []
    if STYLE_MEDIATIQUE:
        msgs += add_media(t, title)
    if REPUTATION_EN_BAS:
        msgs += reputation_last(t)
    return msgs


def cmd_appliquer():
    models = list(STYLE_MEDIATIQUE_MODELES if STYLE_MEDIATIQUE or REPUTATION_EN_BAS else [])
    models.append(PIEDS_SOURCE)
    title = find_title_binding() if STYLE_MEDIATIQUE else None

    def travail(model, t):
        msgs = media_et_reputation(model, t, title) if model in STYLE_MEDIATIQUE_MODELES else []
        if model == PIEDS_SOURCE:
            msgs += center_report_feet(t)
        return msgs
    appliquer_modeles(models, travail, MARKER)


def cmd_etat():
    for model in STYLE_MEDIATIQUE_MODELES:
        _, _, tt = nb.find_vta(model)
        print(f"{model} : " + ("introuvable" if tt is None else
                               "style médiatique : " + ("oui" if has_media(Tree(tt)) else "non")))
    _, _, tt = nb.find_vta(PIEDS_SOURCE)
    if tt is not None:
        print(f"{PIEDS_SOURCE} : pieds écartés : " + ("oui" if named(Tree(tt), NOM_PIEDS_ECARTES) else "non"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        lancer.retirer_par_restauration(MARKER)   # ces lignes ne se retirent qu'en remettant les modèles d'origine
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("style médiatique : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
