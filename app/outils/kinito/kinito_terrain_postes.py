"""[AJOUT KINITO] 26.16 — Entraînement > Entraîn. individuel : en haut de la fiche du joueur, la légende des postes
(Naturel, Accompli, Correct, Médiocre, Mal à l'aise, Peut dépanner) est retirée et le petit terrain des postes est
agrandi : sa ligne de touche du bas est alignée sur le bas du menu du rôle (« Rôle ALB », ex. « M (C) - Poste en
match »), à toutes les tailles de texte.
Demande de Kinito (12/11/2026, sur sa capture) : « tu vires le contenu [la légende] ; agrandir le terrain pour le faire
coller un peu plus à la ligne du bas ; aligne la ligne de touche du bas avec le bas de la tuile M (C) - Poste en match ».

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu.

Comment (tout mesuré le 12/11/2026) :
- L'ÉCRAN : le modèle de FM IndividualTrainingPlayerHeaderContent (gameworld), cité par le SEUL TeamIndividualTrainingBlock
  (guid_partout.py, tous les bundles, scènes comprises) : rien ne change ailleurs. Sa rangée du bas
  (justify-content-space-between) : à gauche #Position (le terrain #data_display-positions-suitability-large-default,
  puis la légende, un ComponentElement), à droite une colonne width-50-percent (Priorité / Intensité, puis Rôle ALB /
  Rôle SLB ; chaque case en margin-bottom-global-gap-large).
- LA LÉGENDE : classe de FM hidden-item (display: none) sur son ComponentElement ; rien n'est supprimé.
- LA HAUTEUR DU TERRAIN : la classe de FM de la boîte (…landscape-no-image_container) la fixe à 120 × 84 ; la hauteur
  est rendue à « auto » (style intégré, mot-clé Auto) : dans #Position (rangée, align-items stretch par défaut), la
  boîte prend toute la hauteur de la rangée, donc celle de la colonne de droite ; on lui donne la MÊME marge du bas que
  les cases de droite (classe de FM margin-bottom-global-gap-large) : son bas tombe sur le bas du menu « Rôle ALB » à
  toutes les tailles de texte (les libellés grandissent avec le texte, les menus non : c'est la mise en page qui
  aligne, pas un chiffre). Le haut ne bouge pas (le haut de la rangée, comme avant).
- L'IMAGE : la texture de FM flat-pitch-thematic-84px (256 × 128) a ses lignes de touche AU BORD de l'image (mesuré :
  lignes 0-1 et 126-127) ; le SIImage, en absolu, prend 100 % de la boîte (ScaleMode 0 = étirée, comme chez FM qui
  l'affiche déjà en 120 × 84) : bord de l'image = ligne de touche.
- LES POSTES : le FMTacticsPanel de FM (#PositionSelector) dimensionne son terrain (#Pitch) sur sa propre taille
  (journaux de la sonde : 70 × 119,9 ici, 444,5 × 651 et 452,4 × 486,5 ailleurs) ; FM le centre dans la boîte avec 70
  de haut sur 84 (max-height 70, justify-content space-around). Gardé à la même part : deux cales à nous (flex-grow 1)
  au-dessus et au-dessous du panneau (flex-grow 10, flex-basis 0, sans max-height) : 7 / 70 / 7, à toute hauteur.
- LA LARGEUR : fixe (LARGEUR), pour garder la proportion de FM (120 / 84) à la hauteur mesurée sur la capture de
  Kinito (texte de sa partie) : ~123 px réels du haut de la rangée au bas du menu, soit ~107,2 unités (1 u = 1,1428 px
  en 1920 × 1080) -> 153. À une autre taille de texte, la hauteur suit, la largeur non (proportion un peu différente).

Touché : IndividualTrainingPlayerHeaderContent (gameworld) : la classe hidden-item sur la légende ; sur la boîte du
terrain, la classe margin-bottom-global-gap-large et son style intégré (largeur, hauteur auto) ; le style intégré de son
SIImage et de son FMTacticsPanel ; nos deux cales (par leur nom, UIPickerKinito-terrain-postes-...). Retirer rend les
classes et les styles d'après l'original et enlève nos cales et nos règles. Lus seulement : le modèle d'origine. Les
fonctions d'Alex qui citent ce modèle : entrainement_individuel_boutons (retire seulement ses anciens boutons d'en-tête,
UIPickerBoutonsIndiv), elements / fiche_joueur_plus (LISENT la note à l'entraînement, PlayerTrainingRatingCell : pas
touchée).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_terrain_postes.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_terrain_postes.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_terrain_postes.py etat
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
MODELE = "IndividualTrainingPlayerHeaderContent"
POSITION = "Position"                                   # #Position : le terrain et la légende
CADRE = "data_display-positions-suitability-large-default"   # la boîte du terrain (120 × 84 par sa classe de FM)
PANNEAU = "PositionSelector"                            # FMTacticsPanel de FM : les postes
ROLE = "iprole"                                         # la case « Rôle ALB » (colonne de droite)
CLASSE_CACHEE = "hidden-item"                           # classe de FM : display: none
CLASSE_MARGE_BAS = "margin-bottom-global-gap-large"     # celle des cases de droite (#iprole, #ooprole…)
LARGEUR = 153            # largeur de la boîte du terrain (unités) : 120 / 84 × ~107,2 (hauteur mesurée, voir en tête)
PARTS = (1, 10, 1)       # cale du haut, panneau, cale du bas : 7 / 70 / 7 comme FM (84 de haut, panneau de 70)
AUTO = 2                 # StyleValueKeyword.Auto d'Unity (Inherit 0, Initial 1, Auto 2, Unset 3, True 4, False 5,
#                          None 6 : arbre.MOT_CLE_AUCUN)
# =====================================================================================================

VERSION = 1   # v1 (12/11/2026) : première version
PREFIXE = "UIPickerKinito-terrain-postes"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_terrain_postes.actif")
NOMS_CALES = (f"{PREFIXE}-v{VERSION}-cale-haut", f"{PREFIXE}-v{VERSION}-cale-bas")

for _k, _v in {"position": (131102, 7), "width": (131105, 3), "height": (131087, 3), "left": (131089, 3),
               "top": (131104, 3), "height-mot-cle": (131087, 1)}.items():
    sm.PROPRIETES.setdefault(_k, _v)   # StylePropertyId d'Unity 6 (comme 26.13)
ID_MAX_HAUTEUR, ID_FLEX_GROW, ID_FLEX_SHRINK, ID_FLEX_BASIS, ID_MIN_HAUTEUR = 131094, 131084, 131085, 131082, 131096


# ---------- outils ----------
def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def nommer(t, r, nom):
    sd = t.sd(r)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    """clone_shallow() ne refait que m_Parent : l'identifiant du parent aussi, s'il existe"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def pc(v):
    return {"unit": 2, "value": float(v)}   # Dimension.Unit : 1 px, 2 %


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def pieces(t):
    """les éléments de FM touchés : {position, cadre, legende, image, panneau, role} ; None si la forme a changé"""
    pos = first(t, lambda r: t.name(r) == POSITION and typ(t, r) == "VisualElement")
    if pos is None:
        return None
    enfants = t.children(pos)
    cadre = next((k for k in enfants if t.name(k) == CADRE), None)
    legendes = [k for k in enfants if typ(t, k) == "ComponentElement"]
    role = first(t, lambda r: t.name(r) == ROLE)
    if cadre is None or len(legendes) != 1 or role is None:
        return None
    images = [k for k in t.children(cadre) if typ(t, k) == "SIImage"]
    panneaux = [k for k in t.children(cadre) if typ(t, k) == "FMTacticsPanel" and t.name(k) == PANNEAU]
    if len(images) != 1 or len(panneaux) != 1 or CLASSE_MARGE_BAS not in (t.elem(role).get("m_Classes") or []):
        return None
    return {"position": pos, "cadre": cadre, "legende": legendes[0], "image": images[0], "panneau": panneaux[0],
            "role": role}


def valeurs(t, r):
    """{StylePropertyId : [(type, valeur)]} du style intégré de r"""
    i = t.elem(r).get("m_RuleIndex", -1)
    return {pid: vals for pid, _, vals in t.styles.values(i)} if i >= 0 else {}


def retirer_regles(t, enlever):
    """retire les règles de la feuille intégrée dont les numéros sont dans enlever et que plus rien n'utilise, puis
    les valeurs qu'elles avaient ajoutées en fin de table (comme retirer_racines de 26.14 / 26.15)"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = set(enlever) - utilisees - {-1}
    if not enlever:
        return
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
    servies = {}
    for regle in t.styles.sh["m_Rules"]:
        for p in regle["m_Properties"]:
            for v in p["m_Values"]:
                if v["m_ValueType"] in tables:
                    servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
    for nom in set(tables.values()):
        vals = t.styles.sh.get(nom) or []
        while vals and len(vals) - 1 not in servies.get(nom, set()):
            vals.pop()
    t.styles.changed = True


# ---------- poser / retirer ----------
def poser(t):
    """la légende cachée, la boîte du terrain à la hauteur de la rangée (marge du bas des cases de droite) et à
    LARGEUR, l'image à 100 %, le panneau des postes entre nos deux cales ; messages"""
    p = pieces(t)
    if p is None:
        return ["en-tête de FM : forme inattendue (le jeu a changé ?) : introuvable"]
    leg = t.elem(p["legende"])
    leg["m_Classes"] = list(leg.get("m_Classes") or []) + [CLASSE_CACHEE]
    cad = t.elem(p["cadre"])
    cad["m_Classes"] = list(cad.get("m_Classes") or []) + [CLASSE_MARGE_BAS]
    t.styles.style(t, p["cadre"], {"width": LARGEUR, "height-mot-cle": AUTO, "flex-shrink": 0})
    t.styles.style(t, p["image"], {"width": pc(100), "height": pc(100), "left": 0, "top": 0})
    # le panneau : son style de FM (flex-grow 1, max-height 70) sans la hauteur maximale, à sa part des 84
    pan = p["panneau"]
    garde = [x for x in t.styles.values(t.elem(pan)["m_RuleIndex"])
             if x[0] not in (ID_MAX_HAUTEUR, ID_FLEX_GROW, ID_FLEX_SHRINK, ID_FLEX_BASIS, ID_MIN_HAUTEUR)] \
        if t.elem(pan).get("m_RuleIndex", -1) >= 0 else []
    t.elem(pan)["m_RuleIndex"] = t.styles.add_rule(garde + [(ID_FLEX_GROW, "", [(2, float(PARTS[1]))]),
                                                           (ID_FLEX_SHRINK, "", [(2, 1.0)]),
                                                           (ID_FLEX_BASIS, "", [(3, 0.0)]),
                                                           (ID_MIN_HAUTEUR, "", [(3, 0.0)])])
    # nos deux cales, avant et après le panneau (copies vides d'un VisualElement de FM du même modèle)
    proto = t.parent[p["position"]]
    for j, nom in enumerate(NOMS_CALES):
        rang = t.children(p["cadre"]).index(pan) + j
        c = t.clone_shallow(proto, p["cadre"], rang)
        recaler_parent(t, c)
        t.elem(c)["m_Classes"], t.elem(c)["m_RuleIndex"] = [], -1
        nommer(t, c, nom)
        sd = t.sd(c)
        sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1   # PickingMode.Ignore : laisse passer les clics
        t.styles.style(t, c, {"flex-grow": PARTS[0 if j == 0 else 2], "flex-shrink": 1, "flex-basis": 0,
                              "min-height": 0})
    return [f"légende des postes masquée ; terrain de {LARGEUR} de large, du haut de la rangée jusqu'au bas du menu "
            f"du rôle (marge {CLASSE_MARGE_BAS}), postes à {PARTS[1]}/{sum(PARTS)} de sa hauteur"]


def retirer(t):
    """les classes et le style intégré des éléments de FM touchés rendus d'après l'original ; nos cales et nos règles
    retirées ; True si quelque chose a changé"""
    p = pieces(t)
    o = ouvrir(MODELE, depart_original=True)
    po = pieces(o[3]) if o is not None else None
    fait = False
    enlever = set()
    for r in marques(t):
        enlever.add(t.elem(r).get("m_RuleIndex", -1))
        t.remove(r)
        fait = True
    if p is not None and po is not None:
        n0 = len(o[3].styles.sh["m_Rules"])
        for cle in ("legende", "cadre", "image", "panneau"):
            e, eo = t.elem(p[cle]), o[3].elem(po[cle])
            classes, regle = list(eo.get("m_Classes") or []), eo.get("m_RuleIndex", -1)
            if list(e.get("m_Classes") or []) != classes or e.get("m_RuleIndex", -1) != regle:
                if e.get("m_RuleIndex", -1) >= n0:
                    enlever.add(e["m_RuleIndex"])
                e["m_Classes"], e["m_RuleIndex"] = classes, regle
                fait = True
    retirer_regles(t, enlever)
    return fait


def a_jour(t):
    p = pieces(t)
    if p is None:
        return False
    v = valeurs(t, p["cadre"])
    largeur = (v.get(131105) or [(0, {})])[0][1]
    return ({t.name(r) for r in marques(t)} == set(NOMS_CALES)
            and all(t.parent.get(r) == p["cadre"] for r in marques(t))
            and CLASSE_CACHEE in (t.elem(p["legende"]).get("m_Classes") or [])
            and CLASSE_MARGE_BAS in (t.elem(p["cadre"]).get("m_Classes") or [])
            and isinstance(largeur, dict) and largeur.get("value") == float(LARGEUR)
            and ID_MAX_HAUTEUR not in valeurs(t, p["panneau"]))


# ---------- commandes ----------
def cmd_appliquer():
    o = ouvrir(MODELE)
    if o is None:
        print(f"[Kinito] Terrain des postes : {MODELE} introuvable (renommé par une mise à jour ?), ignoré")
        return
    t = o[3]
    if a_jour(t):
        print("[Kinito] Terrain des postes : déjà appliqué")
    else:
        retirer(t)   # une ancienne version, s'il y en a une
        msgs = poser(t)
        for m in msgs:
            print(f"[Kinito] Terrain des postes : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Terrain des postes : rien enregistré")
            return
        enregistrer(*o)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    o = ouvrir(MODELE)
    if o is not None and retirer(o[3]):
        enregistrer(*o)
        nb.save_all()
        print(f"{MODELE} : légende des postes et terrain de FM rendus")
    else:
        print("rien à retirer")


def cmd_etat():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        t = o[3]
        print(f"{MODELE} : " + ("en-tête de FM introuvable (forme inattendue)" if pieces(t) is None else
                                f"terrain agrandi, légende masquée (à jour, v{VERSION})" if a_jour(t) else
                                "ANCIENNE version" if marques(t) else "terrain et légende de FM"))
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
            print("[Kinito] Terrain des postes : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
