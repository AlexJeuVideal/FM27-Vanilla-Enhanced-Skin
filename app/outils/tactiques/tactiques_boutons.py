"""Tactiques : boutons « Entraînement », « Entraînement individuel » (v6), « Effectif » et « Programme des rencontres »
dans le bandeau du haut, 2e ligne, à gauche de « Conseil » (v1-v2 : 1re ligne, à droite de la Mentalité ; réglage
EMPLACEMENT).

Même bouton que ceux du bandeau (Intensité / Complexité / Efficacité : SIButton `buttons-button-base-default
button-size-medium`, texte `body-md`), écart FM de 4 px (celui entre Conseil et Annuler sél.).
Seulement pour les équipes du club du joueur (human.Club.Teams contient Team, v5) et hors match.
Clic : effectif de l'équipe (TeamSquadReport, comme la tuile FM Équipe première) / ses rencontres (calendrier, onglet
Rencontres, comme la tuile FM Programme des rencontres).

Modèle : TacticalPlannerHeader (seul propriétaire : appliquer repart de l'original sauvegardé, retirer le remet).
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
import entrainement_equipes as ee  # noqa: E402  (événement « ouvrir un écran »)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import (first, decode_args, encode_args, _enc_varint, visible_model, make_binding,  # noqa: E402
                                 new_visible, SOURCE_COMPARE, FN_COMPARE)
from arbre import no_styles  # noqa: E402
from notes_installations import text_static, text_direct  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402

sm.PROPRIETES.setdefault("justify-content", (131088, 7))

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
BOUTONS = [   # (nom, traduction FM, texte de repère, écran, paramètres) ; noms = ceux de l'écran Effectif (icônes Kinito)
    ("bouton", 1378, b"UIPicker Training",                     # 1378 = « Training » (v6) : calendrier, onglet Entraînement
     ee.ECRAN, [("calendartab", "const.one"), ("team", "Team")]),
    ("individuel", 8962, b"UIPicker Individual Training",      # 8962 = « Individual Training » (v6)
     ee.ECRAN_INDIVIDUEL, [("team", "Team"), ("selectedplayer", "null")]),
    ("effectif", 621, b"UIPicker Squad",                       # 621 = « Squad » de la barre de navigation
     "7957386accba7b44d81ac248d04efbac", [("team", "Team")]),  # TeamSquadReport
    ("programme", 8487, b"UIPicker Fixture Schedule",          # 8487 = « Fixture Schedule »
     ee.ECRAN_RENCONTRES, [("calendartab", "const.two"), ("team", "Team")]),
]
# "conseil" : 2e ligne, à gauche de « Conseil » (dans #HideDuringMatch de FM : déjà caché pendant un match) ;
# "mentalite" : 1re ligne, après la Mentalité (v1-v2)
EMPLACEMENT = "conseil"
ECART = {"conseil": 4, "mentalite": 8}   # px entre boutons (Conseil | Annuler sél. : 4 ; Style | Mentalité : 8)
DESCENDRE = 0           # px, décalage vertical si les boutons ne sont pas alignés en jeu
HORS_MATCH = True       # 1re ligne : cachés pendant un match (le clic quitterait l'écran du match)
# v7 (2026-11-05, demande du joueur) : 1re ligne, entre la Mentalité et l'Intensité, les prochains adversaires au
# format de la barre du haut (logo, nom, (D) / (E), « Dans X jours ») ; équipes du club du joueur, hors match
# v9 (2026-11-05, le joueur) : « tu peux virer » (jamais affiché en jeu) -> désactivé, code gardé
ADVERSAIRES = {"actif": False, "nombre": 2, "largeur": 250, "hauteur": 32, "marge": 16}
DOMICILE = L("(D)", "(H)")
EXTERIEUR = L("(E)", "(A)")
# =====================================================================================================

VERSION = f"9{SUFFIXE}"   # v7 : prochains adversaires (1re ligne) ; v8 : leur liste = Team.Next5Fixtures ; v9 : retirés
# v6 : + « Entraînement » et « Entraînement individuel » à gauche (demande du joueur, 2026-11-04) : + « Entraînement » et « Entraînement individuel » à gauche (demande du joueur, 2026-11-04)
              # v2 : clic réparé (Events_UxmlAttributeFlags 1 : le bouton Intensité copié ne l'a pas)
              # v3 : déplacés sur la 2e ligne, à gauche de « Conseil » (demande du joueur)
              # v4 : condition Team.IsHuman au lieu de « même club » (U23 / équipe B = club à part pour FM)
              # v5 : v4 cachait U19 / U23 -> « human.Club.Teams contient Team » (entrainement_equipes v12)
MODELE = "TacticalPlannerHeader"
PREFIXE = "UIPickerTactiquesBoutons"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
# prochains adversaires : ligne = cellule FM que RIEN ne cite (OpponentFixtureRow, vérifié le 2026-11-05), réécrite ;
# liste = StreamedObjectList de FM (SuggestedLineupCardUpcomingFixturesBlock), fonction « N éléments à partir de »
MODELE_LIGNE = "OpponentFixtureRow"
GUID_LIGNE = "a8b177aa6c93ae04f95697562624f69c"
NOM_LIGNE = f"{PREFIXE}-ligne-v{VERSION}"
SOURCE_LISTE = "SuggestedLineupCardUpcomingFixturesBlock"
FN_N_PREMIERS = "93cf103534f0ba14e9d0f749e99d316a"   # (clé, nombre, Team.Next5Fixtures) de la liste FM recopiée
TYPE_MATCH = 1718188148                              # FixtureReference (une ligne = un match, v8)
MODELES = (MODELE, MODELE_LIGNE)
MARKER = os.path.join(backup.BACKUP_DIR, "tactiques_boutons.actif")


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def construire(t):
    mentalite = first(t, lambda r: t.name(r) == "mentality-pending-state")
    remap = mentalite and t.parent.get(mentalite)
    rangee = remap and t.parent.get(remap)
    if rangee is None or typ(t, remap) != "BindingRemapper":
        return ["menu Mentalité du bandeau introuvable"]
    # bouton modèle : Intensité (SIButton du bandeau, texte body-md dans un switch par taille d'écran)
    texte = first(t, lambda r: typ(t, r) == "SIText" and t.sd(r).get("DebugDisplay") == "Intensity")
    bouton = texte
    while bouton is not None and typ(t, bouton) != "SIButton":
        bouton = t.parent.get(bouton)
    pas_match = first(t, lambda r: typ(t, r) == "SIVisible" and (t.sd(r).get("Binding") or {}).get("m_kind") == 1
                      and t.sd(r)["Binding"]["m_direct"]["Path"]["m_path"] == "config.ShowPhonePanels")
    s_vis, vis = visible_model(SOURCE_COMPARE, FN_COMPARE)
    if None in (texte, bouton, pas_match, vis):
        return ["bouton Intensité / visibilités de FM introuvables"]

    conseil = first(t, lambda r: t.name(r) == "AdviceDropdownVisible")
    if EMPLACEMENT == "conseil":
        if conseil is None:
            return ["menu « Conseil » du bandeau introuvable"]
        rangee, index = t.parent[conseil], t.children(t.parent[conseil]).index(conseil)
    else:
        index = t.children(rangee).index(remap) + 1
    ecart = ECART[EMPLACEMENT]

    # SIVisible équipe du club du joueur > [SIVisible hors match] > boutons
    # v5 : équipe du club du joueur = human.Club.Teams contient Team (U23 / équipe B comprises ; v4 Team.IsHuman :
    # seulement l'équipe entraînée par le joueur)
    x = ee.visible_equipe_geree(t, rangee, index, NOM_RACINE,
                                ["row-direction-normal", "align-items-center", "align-self-center-class"],
                                equipe="Team")
    if x is None:
        return ["morceaux de FM de la condition « équipe du club » (BindingSetter, fonction contient) introuvables"]
    haut, club = x
    t.elem(haut)["m_Classes"].append("align-self-center-class")
    t.styles.style(t, haut, {"flex-shrink": 0, "top": DESCENDRE})
    t.styles.style(t, club, {"flex-shrink": 0})
    parent = club
    if HORS_MATCH and EMPLACEMENT != "conseil":
        m = t.clone(pas_match, club)
        for k in list(t.children(m)):
            t.remove(k)
        no_styles(t, m)
        t.elem(m)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        sd = t.sd(m)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}-hors-match", 1
        sd["Binding"]["m_direct"]["Path"]["m_path"] = "game.IsDuringMatch"   # InvertDirectBinding gardé (1)
        parent = m

    for nom, numero, repere, ecran, params in BOUTONS:
        x = t.clone(bouton, parent)
        for k in list(t.children(x)):
            t.remove(k)
        no_styles(t, x)
        t.elem(x)["m_Classes"] = ["buttons-button-base-default", "button-size-medium"]
        sd = t.sd(x)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}-{nom}", 1
        sd["Events"]["m_bytes"] = ee.evenement_ecran(ecran, params)
        sd["Events_UxmlAttributeFlags"] = 1   # sans ce drapeau FM ignore l'événement (v1 : clic sans effet)
        # à gauche de Conseil : écart à droite de chaque bouton ; après la Mentalité : écart à gauche
        t.styles.style(t, x, {"margin-right" if EMPLACEMENT == "conseil" else "margin-left": ecart})
        txt = t.clone(texte, x)
        no_styles(t, txt)
        t.elem(txt)["m_Classes"] = ["body-md", "sitext-hover-cursor"]
        f = t.sd(txt)["TextBinding"]["m_visualFunction"]
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"TranslationID]"):
                a[1] = struct.pack("<i", numero) + b"\x01" + _enc_varint(len(repere)) + repere
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        t.sd(txt)["DebugDisplay"] = repere.decode()
    ou = "à gauche de « Conseil » (2e ligne)" if EMPLACEMENT == "conseil" else "après la Mentalité"
    msgs = [f"bandeau des tactiques : boutons « Entraînement », « Entraînement individuel », « Effectif » et "
            f"« Programme des rencontres » {ou} "
            "(équipes du club du joueur, hors match)"]
    if ADVERSAIRES["actif"]:
        msgs += adversaires(t, remap, pas_match)
    return msgs


def adversaires(t, remap, pas_match):
    """1re ligne, juste après la Mentalité : [équipe du club] > [hors match] > liste FM des N prochains matchs de
    l'équipe (les N premiers de Team.Next5Fixtures, v8), une ligne = OpponentFixtureRow
    réécrite (ligne())"""
    s = hp.src_tree(SOURCE_LISTE)
    liste = s and first(s, lambda r: typ(s, r) == "StreamedObjectList")
    if liste is None:
        return [f"liste des prochains matchs de FM ({SOURCE_LISTE}) introuvable"]
    rangee = t.parent[remap]
    x = ee.visible_equipe_geree(t, rangee, t.children(rangee).index(remap) + 1, f"{PREFIXE}-adversaires",
                                ["row-direction-normal", "align-items-center"], equipe="Team")
    if x is None:
        return ["morceaux de FM de la condition « équipe du club » (BindingSetter, fonction contient) introuvables"]
    haut, club = x
    a = ADVERSAIRES
    # toute la place libre entre la Mentalité et l'Intensité, contenu centré ; rétrécit (coupé) si l'écran est étroit
    t.styles.style(t, haut, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "overflow": "hidden",
                             "justify-content": "center", "margin-left": a["marge"], "margin-right": a["marge"]})
    t.styles.style(t, club, {"flex-shrink": 1, "min-width": 0, "overflow": "hidden"})
    m = t.clone(pas_match, club)
    for k in list(t.children(m)):
        t.remove(k)
    no_styles(t, m)
    t.elem(m)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    sd = t.sd(m)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}-adversaires-hors-match", 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = "game.IsDuringMatch"   # InvertDirectBinding gardé (1)
    t.styles.style(t, m, {"flex-shrink": 1, "min-width": 0, "overflow": "hidden"})

    w = t.clone(liste, m, src=s)
    for k in list(t.children(w)):
        t.remove(k)
    no_styles(t, w)
    t.elem(w)["m_Classes"] = []
    wd = t.sd(w)
    wd["name"], wd["name_UxmlAttributeFlags"] = f"{PREFIXE}-adversaires-liste", 1
    # v8 (vu en jeu, console : liste vide, 0 px) : Team.FixtureListElements / NextFixtureListElement ne donnent rien
    # dans le bandeau -> fonction de la liste FM recopiée (N premiers de Team.Next5Fixtures), seul le nombre change
    f = wd["Binding"]["m_visualFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if f["m_target"]["m_guid"] != FN_N_PREMIERS or not any(x[0] == b"SI.VisualScripting.Int32VisualArg" for x in args):
        return [f"liste des prochains matchs de FM ({SOURCE_LISTE}) inattendue (le jeu a changé ?)"]
    for x in args:
        if x[0] == b"SI.VisualScripting.Int32VisualArg":
            x[1] = struct.pack("<i", a["nombre"])
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    wd["RowTemplate"]["m_AssetGUID"] = GUID_LIGNE
    wd["RowParamName"] = "row"
    wd["Direction"], wd["Direction_UxmlAttributeFlags"] = 1, 1          # horizontale (la carte FM : 1)
    wd["FixedElementSize"], wd["FixedElementSize_UxmlAttributeFlags"] = float(a["largeur"]), 1
    wd["AlternateRows"] = 0
    wd["SelectionMode"] = 0
    # liste virtualisée : sans largeur elle ne crée rien -> largeur = N lignes ; rétrécit avec la place
    t.styles.style(t, w, {"width": a["nombre"] * a["largeur"], "height": a["hauteur"], "flex-shrink": 1,
                          "min-width": 0})
    return [f"bandeau des tactiques : {a['nombre']} prochains adversaires entre la Mentalité et l'Intensité "
            "(équipes du club du joueur, hors match)"]


def ligne(t):
    """OpponentFixtureRow réécrite : paramètre row (un match de Team.Next5Fixtures), fixture = row ;
    domicile (club de l'équipe à domicile = club du joueur) : logo + nom de l'équipe à l'extérieur + (D) ;
    extérieur : logo + nom de l'équipe à domicile + (E) ; puis « Dans X jours » (Fixture.NextMatchDaysText)"""
    racine = first(t, lambda r: typ(t, r) == "BindingRoot")
    remap = racine and first(t, lambda r: typ(t, r) == "BindingRemapper" and t.parent.get(r) == racine)
    logo = remap and first(t, lambda r: typ(t, r) == "BindingRemapper" and r != remap)
    nom = first(t, lambda r: t.name(r) == "OpponentText")
    s_vis, vis = visible_model(SOURCE_COMPARE, FN_COMPARE)
    if None in (racine, remap, logo, nom, vis) or not t.sd(racine).get("Parameters"):
        return [f"{MODELE_LIGNE} : morceaux de FM introuvables"]
    p = t.sd(racine)["Parameters"][0]
    p["name"], p["type"]["id"] = "row", TYPE_MATCH
    sd = t.sd(remap)
    sd["name"], sd["name_UxmlAttributeFlags"] = NOM_LIGNE, 1
    sd["Mappings"] = [{"m_serialisedType": 0, "from": "fixture", "to": {"m_path": "row"},
                       "type": {"id": TYPE_MATCH}}]
    for r in list(t.children(remap)):
        if r not in (logo, nom):
            t.remove(r)
    t.elem(remap)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.elem(remap)["m_RuleIndex"] = -1
    t.styles.style(t, remap, {"height": ADVERSAIRES["hauteur"], "flex-shrink": 0,
                              "width": ADVERSAIRES["largeur"], "overflow": "hidden"})

    for k, (moi, autre, lettre) in enumerate((("HomeTeam", "AwayTeam", DOMICILE), ("AwayTeam", "HomeTeam", EXTERIEUR))):
        b = make_binding(s_vis.sd(vis)["Binding"], 2, [f"Fixture.{moi}.Club.UniqueId", "human.Club.UniqueId"])
        v = new_visible(t, s_vis, vis, remap, k, f"{PREFIXE}-ligne-{'domicile' if k == 0 else 'exterieur'}", b,
                        ["row-direction-normal", "align-items-center"])
        t.sd(v)["name_UxmlAttributeFlags"] = 1
        t.styles.style(t, v, {"flex-shrink": 1, "min-width": 0, "overflow": "hidden"})
        lg = t.clone(logo, v)
        t.sd(lg)["Mappings"][0]["to"]["m_path"] = f"Fixture.{autre}.Club"
        n = t.clone(nom, v)
        t.sd(n)["TextBinding"]["m_direct"]["Path"]["m_path"] = f"Fixture.{autre}.Name"
        t.sd(n)["name"], t.sd(n)["name_UxmlAttributeFlags"] = "", 0
        t.elem(n)["m_Classes"] = ["content-no-wrap", "body-md", "global-text-primary"]
        t.elem(n)["m_RuleIndex"] = -1
        t.styles.style(t, n, {"margin-left": 6, "flex-shrink": 1, "min-width": 0})
        txt = text_static(t, nom, v, lettre)
        t.sd(txt)["name"], t.sd(txt)["name_UxmlAttributeFlags"] = "", 0
        t.elem(txt)["m_Classes"] = ["content-no-wrap", "body-sm", "global-text-primary"]
        t.elem(txt)["m_RuleIndex"] = -1
        t.styles.style(t, txt, {"margin-left": 4, "flex-shrink": 0})
    t.remove(logo)
    t.remove(nom)
    modele = first(t, lambda r: typ(t, r) == "SIText")   # un nom recopié ci-dessus
    j = text_direct(t, modele, remap, "Fixture.NextMatchDaysText")
    t.sd(j)["name"], t.sd(j)["name_UxmlAttributeFlags"] = "", 0
    t.elem(j)["m_Classes"] = ["content-no-wrap", "body-sm", "global-text-secondary"]
    t.elem(j)["m_RuleIndex"] = -1
    t.styles.style(t, j, {"margin-left": 6, "flex-shrink": 0})
    return [f"{MODELE_LIGNE} : ligne adversaire (logo, nom, {DOMICILE} / {EXTERIEUR}, jours)"]


# ---------- commandes ----------
ATTENDU = {MODELE: NOM_RACINE, MODELE_LIGNE: NOM_LIGNE if ADVERSAIRES["actif"] else None}
CONSTRUIRE = {MODELE: construire, MODELE_LIGNE: ligne}


def a_jour(modele, t):
    nom = ATTENDU[modele]
    return any(t.name(r) == nom for r in marques(t)) if nom else not marques(t)


def cmd_appliquer():
    actuels = {m: ouvrir(m) for m in MODELES}
    if actuels[MODELE] is None or (ATTENDU[MODELE_LIGNE] and actuels[MODELE_LIGNE] is None):
        print(f"{MODELE} / {MODELE_LIGNE} introuvable (renommé par une mise à jour ?), ignoré")
        return
    a_faire = [m for m in MODELES if actuels[m] is not None and not a_jour(m, actuels[m][3])]
    if not a_faire:
        print("boutons des tactiques : déjà appliqué")
    else:
        prets = []
        for modele in a_faire:   # un passage par modèle ; tous construits avant d'écrire (rien à moitié)
            ancien = bool(marques(actuels[modele][3]))
            bundle, obj, tt, t = ouvrir(modele, depart_original=True)
            if marques(t):
                print("boutons des tactiques : pas de sauvegarde d'origine propre, ignoré")
                return
            msgs = (CONSTRUIRE[modele](t) if ATTENDU[modele] else [f"{modele} : remis d'origine"]) \
                + (["ancienne version remplacée"] if ancien else [])
            for m in msgs:
                print(f"boutons des tactiques : {m}")
            if any("introuvable" in m for m in msgs):
                print("boutons des tactiques : rien enregistré")
                return
            prets.append((bundle, obj, tt, t))
        for bundle, obj, tt, t in prets:
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
    for modele in MODELES:
        o = ouvrir(modele)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{modele} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{modele} : remis d'origine")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele in MODELES:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
            continue
        t = o[3]
        etat = "à jour" if a_jour(modele, t) else "ANCIENNE version"
        print(f"{modele} : " + (f"appliqué ({etat}, v{VERSION})" if marques(t) else "d'origine"))
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
            print("boutons des tactiques : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
