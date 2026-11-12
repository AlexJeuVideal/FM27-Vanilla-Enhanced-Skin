"""Dynamique > État d'esprit façon FM24 : colonnes de satisfaction à droite de la Hiérarchie, en cases colorées.

FM27 n'affiche que Statut / joueur / Hiérarchie / État d'esprit (vue ClubSquadHappinessTable, fabrique
PlayerTableFactory, tableau du bloc SquadHappinessPlayerTableBlock). Après la Hiérarchie :
  Promesses | Points positifs | Points négatifs                       (chiffres, sans case)
  Moral | Entraînement | Traitement | Club | Gestion | Temps de jeu | État d'esprit   (cases colorées FM24)
Case = fond coloré selon le niveau, logo au milieu, libellé dessous (comme FM24).

Données : Moral = binding.Morale (0..20) + MoraleString ; État d'esprit = HierarchyOverallHappinessLevel ;
Temps de jeu = PlayingTimeHappinessLevel (logos / libellés des collections FM) ; Traitement / Club / Gestion /
Entraînement = HappinessTreatment / Club / Management / Training (affichés nulle part chez FM) : .Severity (vu en jeu :
négatif = content, positif = mécontent ; Entraînement : autre échelle, -111 = pas d'info) et .Description (phrase,
mise en infobulle ; Entraînement : « Satisfait »… affiché).

Modèles (ce script est leur seul propriétaire : appliquer repart des originaux, retirer les remet) : 5 cellules FM
inutilisées (catalogue Addressables, citées par aucun bundle), réécrites en cases (CELLULES).

Bundles des tableaux :
- ui-tableviews : seule la vue ClubSquadHappinessTable change (refaite depuis sa liste d'origine ; retirer la remet).
- ui-tablefactories : nos colonnes « uipicker-… » ; moral_icone_seule (propriétaire, repart de l'original) rappelle
  fabrique_appliquer() quand ce script est actif (marqueur).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\etat_esprit_fm24.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\etat_esprit_fm24.py retirer
  .venv\\Scripts\\python.exe outils\\etat_esprit_fm24.py etat
"""
import copy
import json
import os
import struct
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (correctif UnityPy, chemins du jeu)
import sauvegarde_originaux as backup  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (cases : changer un réglage -> augmenter VERSION)
# =====================================================================================================
APRES = "hierarchy-icon"   # les colonnes sont placées juste après la Hiérarchie (logo)
CASE_LARGEUR, CASE_MIN = 92, 70   # px
# (id de colonne, largeur, largeur min)
COLONNES = [
    ("promises-count", 80, 60),
    ("uipicker-happiness-positives", 80, 60),
    ("uipicker-happiness-negatives", 80, 60),
    ("uipicker-case-morale", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-training", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-treatment", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-club", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-management", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-playingtime", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-overall", CASE_LARGEUR, CASE_MIN),
]
ENLEVER = ["happiness", "happiness-align-right"]   # colonnes FM retirées de la vue (remplacées par la case)
# couleurs des cases, du pire (0) au meilleur (6) ; 3 = neutre (presque pas de fond, comme « Assez content » FM24)
COULEURS = ["#9E2430",   # 0 très mécontent — rouge
            "#C4442D",   # 1 mécontent — rouge orangé
            "#C9813A",   # 2 moyen (« Correct » FM24) — orange
            None,        # 3 neutre — fond discret
            "#8FA22C",   # 4 bon — vert olive
            "#2E9A48",   # 5 satisfait — vert
            "#17705A"]   # 6 ravi — vert-bleu (« Satisfait » de l'État d'esprit FM24)
NEUTRE = (1, 1, 1, 0.06)
MARGE_CASE = 1        # px autour du fond coloré
LOGO = 16             # px
TEXTE = 11            # px ; un texte trop long passe sur deux lignes (« Extrêmement / bon »)
# colonne du nom (FM : 908 px, min 592 / 596, min 264) : moins large -> plus de place pour les cases et leurs titres
NOM_LARGEUR = {"portrait-name-description-large": (520, 320), "portrait-name-description": (420, 260)}
# =====================================================================================================

VERSION = 2   # v2 : libellés accordés au joueur (f97abdf5), texte de l'Entraînement dans chaque bande, textes sur
#               deux lignes, titres Entraînement / Gestion / Temps de jeu, colonne du nom réduite
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
VUE = "ClubSquadHappinessTable"
FABRIQUE = "PlayerTableFactory"
MARKER = os.path.join(backup.BACKUP_DIR, "etat_esprit_fm24.actif")
DRY_RUN = "--dry-run" in sys.argv
NOM_CASE = f"UIPickerCase-v{VERSION}"

# cellules FM inutilisées -> cases (nom, GUID Addressables)
CELLULES = {
    # RatedDebugStringCell (a068b4fc…) supprimée par la MAJ du 2026-11-12 -> autre cellule inutilisée (vérifié)
    "morale": ("LiveTablePldCell", "eb2a8fd4fb4271943ad77f62946e8a0f"),
    "overall": ("StandardDataDisplayCellValueRange", "518f7f0ba435600488f7903468885b9c"),
    "playingtime": ("StandardLabelCellColouredTextNegativePositive", "217262d10587ed2448aa86d052e34656"),
    "categorie": ("PlayerPositionAbilityCell", "bb758309c8bfa2b47913cc32f7be602b"),
    "training": ("NonPlayerContractExpiryCell", "998ac81db1a95154f8dc8992a98632a1"),
}
SOURCES = {"morale": "PlayerMoraleCell", "overall": "PlayerHappinessCell", "playingtime": "PlayerPlayingTimeHappinessCell",
           "categorie": "PlayerHappinessCell", "training": "PlayerHappinessCell"}
TEXTE_TRADUIT_SOURCE = "PlayerHappinessTile_4x4"   # SIText « ([%number#1]) » : traduction + arguments (f97abdf5)
FN_TRADUCTION = "f97abdf5"   # les libellés FM « Ravi[%male#1…] » attendent le joueur en argument (accord)


def icone(k):
    return f"scaling-icons-morale-happiness-{k}-size-small-16px-filled-false"


# bandes : (au-dessus de, jusqu'à (inclus), couleur, logo ou None, texte traduit ou None) ; None = pas de limite
BANDES = {
    "morale": ("binding.Morale", [(None, -1, 3, None, None), (-1, 4, 0, None, None), (4, 7, 1, None, None),
                                  (7, 11, 2, None, None), (11, 14, 4, None, None), (14, 17, 5, None, None),
                                  (17, None, 6, None, None)]),
    # clés d'OverallHappinessDataCollection (≤ -81 -61 -41 -21 19 39 59 79 100)
    "overall": ("level", [(None, -61, 0, None, None), (-61, -21, 1, None, None), (-21, 19, 3, None, None),
                          (19, 59, 4, None, None), (59, 79, 5, None, None), (79, None, 6, None, None)]),
    # clés de PlayingTimeHappinessDataCollection (≤ -101 -40 -30 -20 20 49 74 100)
    "playingtime": ("level", [(None, -30, 0, None, None), (-30, -20, 1, None, None), (-20, 20, 3, None, None),
                              (20, 49, 4, None, None), (49, 74, 5, None, None), (74, None, 6, None, None)]),
    # Severity : négatif = content ; libellés = ceux du temps de jeu (Ravi 26948, Heureux 26950, Satisfait 31043,
    # Préoccupé 31042) et de l'État d'esprit (31053, 31051 : mécontent ?)
    "categorie": ("level", [(None, -4, 6, icone(5), 26948), (-4, -1, 5, icone(4), 26950),
                            (-1, 0, 5, icone(4), 31043), (0, 2, 2, icone(2), 31042),
                            (2, 4, 1, icone(1), 31053), (4, None, 0, icone(1), 31051)]),
    # Entraînement : -111 = pas d'info ; vu 0..19 avec « Satisfait »
    "training": ("level", [(None, -100, 3, None, None), (-100, -1, 1, icone(2), None), (-1, None, 5, icone(4), None)]),
}

MODELE_COLONNE = "promises-count"   # colonne nombre (cellule texte 275b9570, paramètre binding)
G = {k: v[1] for k, v in CELLULES.items()}
# id : réglages de la colonne créée dans la fabrique (copie de « modele »)
NOUVELLES = {
    "uipicker-happiness-positives": dict(modele=MODELE_COLONNE, titre=4324, chemin="binding.HappinessPositivesCount"),
    "uipicker-happiness-negatives": dict(modele=MODELE_COLONNE, titre=4325, chemin="binding.HappinessNegativesCount"),
    "uipicker-case-morale": dict(modele="morale", guid=G["morale"]),
    "uipicker-case-overall": dict(modele="hierarchy-overall-happiness", guid=G["overall"], titre=3245),
    "uipicker-case-playingtime": dict(modele="playing-time-happiness", guid=G["playingtime"], titre=5960),  # Playing Time
}
# titres : « Training » 1378, « Treatment » 3153, « Club » 3193, « Managerial » 13319 (série de « Playing Time » 13320)
for _cat, _titre, _cell in (("Training", 1378, "training"), ("Treatment", 3153, "categorie"),
                            ("Club", 3193, "categorie"), ("Management", 13319, "categorie")):
    NOUVELLES[f"uipicker-case-{_cat.lower()}"] = dict(
        modele="playing-time-happiness", guid=G[_cell], titre=_titre,
        level=f"binding.Happiness{_cat}.Severity", texte=f"binding.Happiness{_cat}.Description")


def monos(env, nom):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if tt.get("m_Name") == nom:
            yield o, tt


def colonnes():
    return list(COLONNES)


def a_creer():
    voulues = {c[0] for c in colonnes()}
    return {k: v for k, v in NOUVELLES.items() if k in voulues}


# ----------------------------------------------------------------------------------- fabrique

def _liaison(r, nom):
    return next((b for b in r.get("m_valueBindings") or [] if b.get("from") == nom), None)


def nouvelle_colonne(rows, cid, cfg):
    modele = next((r for r in rows if r["m_id"] == cfg["modele"]), None)
    if modele is None:
        sys.exit(f"{FABRIQUE} : colonne modèle {cfg['modele']} introuvable")
    r = copy.deepcopy(modele)
    r["m_id"] = cid
    if "titre" in cfg:
        r["m_translationID"] = {"GameID": cfg["titre"]}
        r["m_hintID"] = {"GameID": -1}
    if "chemin" in cfg:
        r["m_sortBinding"]["m_path"] = cfg["chemin"]
        r["m_valueBindings"][0]["to"]["m_path"] = cfg["chemin"]
    if "level" in cfg:
        _liaison(r, "level")["to"]["m_path"] = cfg["level"]
        r["m_sortBinding"]["m_path"] = cfg["level"]
    if "texte" in cfg:
        b = copy.deepcopy(_liaison(r, "level"))
        b["from"], b["to"]["m_path"] = "texte", cfg["texte"]
        r["m_valueBindings"].append(b)
        f = copy.deepcopy(next(x for x in r["m_footerValueBindings"] if x["from"] == "level"))
        f["from"] = "texte"
        r["m_footerValueBindings"].append(f)
    if "guid" in cfg:
        r["m_uxmlRef"]["m_AssetGUID"] = cfg["guid"]
        r["m_defaultWidth"], r["m_minimumWidth"] = float(CASE_LARGEUR), float(CASE_MIN)
    else:
        r["m_defaultWidth"] = r["m_minimumWidth"] = 80.0
    return r


def fabrique_appliquer(env):
    """crée nos colonnes dans PlayerTableFactory (env déjà chargé), enlève les « uipicker-… » plus voulues ou
    d'une autre version ; True si changé"""
    change = False
    for o, tt in monos(env, FABRIQUE):
        rows = tt["m_rowData"]
        creer = a_creer()
        voulu = {cid: nouvelle_colonne(rows, cid, cfg) for cid, cfg in creer.items()}
        garde = [r for r in rows if not r["m_id"].startswith("uipicker-")
                 or (r["m_id"] in voulu and json.dumps(r) == json.dumps(voulu[r["m_id"]]))]
        if len(garde) != len(rows):
            rows[:] = garde
            change = True
        ids = {r["m_id"] for r in rows}
        for cid, r in voulu.items():
            if cid not in ids:
                rows.append(r)
                change = True
                print(f"{FABRIQUE} : colonne {cid} créée")
        if change:
            o.save_typetree(tt)
    return change


def fabrique_retirer(env):
    change = False
    for o, tt in monos(env, FABRIQUE):
        avant = len(tt["m_rowData"])
        tt["m_rowData"] = [r for r in tt["m_rowData"] if not r["m_id"].startswith("uipicker-")]
        if len(tt["m_rowData"]) != avant:
            o.save_typetree(tt)
            change = True
    return change


def ecrire(path, env):
    data = env.file.save(packer="original")
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(path)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(path, data)


# ----------------------------------------------------------------------------------- vue

def config_origine():
    orig = backup.backup_path(VUES)
    if not os.path.exists(orig):
        return None
    for _, tt in monos(UnityPy.load(orig), VUE):
        return tt["m_tableView"]["m_tableConfig"]


def vue_voulue(cfg_actuel):
    """liste de colonnes voulue : celle d'origine de FM (ou l'actuelle sans nos ajouts) + nos colonnes après APRES"""
    origine = config_origine()
    cfg = copy.deepcopy(origine if origine is not None else
                        [c for c in cfg_actuel if not c["m_columnID"].startswith("uipicker-")])
    ids = [c["m_columnID"] for c in cfg]
    if APRES not in ids:
        sys.exit(f"{VUE} : colonne {APRES} introuvable")
    modele = cfg[ids.index(APRES)]
    cfg = [c for c in cfg if c["m_columnID"] not in ENLEVER and c["m_columnID"] not in {k for k, _, _ in colonnes()}]
    pos = [c["m_columnID"] for c in cfg].index(APRES) + 1
    for c in cfg:
        if c["m_columnID"] in NOM_LARGEUR:
            w, wmin = NOM_LARGEUR[c["m_columnID"]]
            c["m_columnMetadata"]["m_widthOverride"], c["m_columnMetadata"]["m_minWidthOverride"] = float(w), float(wmin)
    for cid, w, wmin in colonnes():
        c = copy.deepcopy(modele)
        c["m_columnID"] = cid
        m = c["m_columnMetadata"]
        m["m_widthOverride"], m["m_minWidthOverride"] = float(w), float(wmin)
        m["m_applicableBreakpoints"] = -1
        m["m_titleTranslationIdOverride"] = {"GameID": 0}
        cfg.insert(pos, c)
        pos += 1
    return cfg


# ----------------------------------------------------------------------------------- cases (modèles)

def _modules():
    """outils des autres scripts (chargés seulement pour les cases)"""
    import pastilles_pour_contre as ipc
    import notes_installations as ni
    import arbre as sm
    from attributs_tout_cocher import ouvrir, original
    for k, v in {"color": (65536, 4), "font-size": (65537, 3), "-unity-text-align": (65546, 7),
                 "white-space": (65552, 7)}.items():
        sm.PROPRIETES.setdefault(k, v)
    return ipc, ni, sm, ouvrir, original


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith("UIPickerCase")]


def construire_case(t, sorte, outils):
    ipc, ni, sm, s_vis, vis, txt_trad, tip = outils
    typ = ipc.typ
    s = ipc.src_tree(SOURCES[sorte])
    racine = t.tt["m_VisualTree"]["rid"]
    s_expect = next(r for r in s.children(s.tt["m_VisualTree"]["rid"]) if typ(s, r) == "BindingExpect")
    vieux = list(t.children(racine))
    expect = t.clone(s_expect, racine, src=s)
    for k in vieux:
        t.remove(k)
    sm.no_styles(t, expect)
    img = ipc.first(t, lambda r: typ(t, r) == "SIImage", expect)
    txt = ipc.first(t, lambda r: typ(t, r) == "SIText", expect)
    if img is None or txt is None:
        return [f"{sorte} : logo / texte de {SOURCES[sorte]} introuvables"]
    classes_texte = [c for c in t.elem(txt).get("m_Classes") or [] if "ellipsis" not in c and "no-wrap" not in c]
    t.elem(txt)["m_Classes"] = classes_texte
    style_texte = {"color": (1, 1, 1, 1), "font-size": TEXTE, "-unity-text-align": "middle-center",
                   "white-space": "normal", "max-width": {"unit": 2, "value": 100.0},
                   "margin-top": 1, "margin-left": 0, "margin-right": 0, "margin-bottom": 0}
    # argument « joueur » des libellés FM (accord), pris dans le texte de la cellule FM (PlayerHappinessCell)
    arg_joueur = None
    tb0 = t.sd(txt).get("TextBinding") or {}
    if tb0.get("m_kind") == 2:
        for a in ni.decode_args(tb0["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]):
            if a[0].startswith(b"SI.VisualScripting.StructListVisualArg"):
                arg_joueur = a[1]
    if sorte == "categorie" and arg_joueur is None:
        return [f"{sorte} : argument joueur des libellés introuvable"]
    if sorte == "training":   # texte FM de la catégorie (« Satisfait »…) ; recopié dans chaque bande plus bas
        t.remove(img)
        tb = copy.deepcopy(t.sd(txt)["TextBinding"])
        tb["m_kind"] = 1
        tb["m_direct"]["Path"]["m_path"] = "texte"
        t.sd(txt)["TextBinding"] = tb
        t.styles.style(t, txt, style_texte)
        t.sd(txt)["pickingMode"], t.sd(txt)["pickingMode_UxmlAttributeFlags"] = 1, 1
    cadre = t.parent[img]
    t.sd(cadre)["name"], t.sd(cadre)["name_UxmlAttributeFlags"] = NOM_CASE, 1
    t.elem(cadre)["m_Classes"] = []
    t.styles.style(t, cadre, {"flex-grow": 1, "flex-direction": "column", "justify-content": "center",
                              "align-items": "center", "align-self": "stretch", **ipc.MARGES(MARGE_CASE)})
    r = t.parent[cadre]
    while r != racine:   # BindingExpect / BindingSetter : toute la case
        t.styles.style(t, r, {"flex-grow": 1, "align-self": "stretch"})
        r = t.parent[r]
    if sorte in ("categorie", "training"):   # paramètre « texte » (phrase / libellé FM de la catégorie)
        params = t.sd(expect)["Parameters"]
        p = copy.deepcopy(next(x for x in params if x["name"] == "level"))
        p["name"] = "texte"
        params.append(p)
    # bandes de couleur (sous le contenu)
    chemin, bandes = BANDES[sorte]
    for k, (bas, haut, coul, logo, libelle) in enumerate(bandes):
        parent, idx = cadre, k
        if bas is not None:
            parent = ni.new_visible(t, s_vis, vis, parent, idx, "", ni.make_binding(s_vis.sd(vis)["Binding"], 4, [chemin], bas))
            t.styles.style(t, parent, ipc.PLEIN)
            idx = None
        if haut is not None:
            parent = ni.new_visible(t, s_vis, vis, parent, idx, "", ni.make_binding(s_vis.sd(vis)["Binding"], 1, [chemin], haut))
            t.styles.style(t, parent, ipc.PLEIN)
            idx = None
        fond = ipc.nouveau(t, parent, idx, [], {**ipc.PLEIN, "flex-direction": "column", "justify-content": "center",
                                                "align-items": "center", "overflow": "hidden", "padding": 2,
                                                "background-color": ipc._rgba(COULEURS[coul]) if COULEURS[coul] else NEUTRE})
        t.sd(fond)["pickingMode"], t.sd(fond)["pickingMode_UxmlAttributeFlags"] = 1, 1
        if logo:
            ipc.nouveau(t, fond, None, [logo], {**ipc.CARRE(LOGO), "flex-shrink": 0})
        if libelle:
            s_tr, r_tr = txt_trad
            x = t.clone(r_tr, fond, src=s_tr)
            sm.no_styles(t, x)
            t.sd(x)["name"] = ""
            t.elem(x)["m_Classes"] = classes_texte
            vf = copy.deepcopy(t.sd(x)["TextBinding"])
            args = ni.decode_args(vf["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
            for a in args:
                if a[0].endswith(b"TranslationID]"):
                    dbg = b"UIPicker"
                    a[1] = struct.pack("<i", libelle) + b"\x01" + ni._enc_varint(len(dbg)) + dbg
                elif a[0].startswith(b"SI.VisualScripting.StructListVisualArg"):
                    a[1] = arg_joueur
            vf["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = ni.encode_args(args)
            t.sd(x)["TextBinding"] = vf
            t.styles.style(t, x, style_texte)
        if sorte == "training":   # texte FM dans la bande, sous le logo (plus par-dessus)
            t.clone(txt, fond)
    # contenu FM par-dessus (logo + texte), ou rien
    if sorte in ("categorie", "training"):
        if sorte == "categorie":
            t.remove(img)
        t.remove(txt)
    else:
        t.styles.style(t, img, {**ipc.CARRE(LOGO), **ipc.MARGES(0), "flex-shrink": 0})
        t.styles.style(t, txt, style_texte)
        t.sd(txt)["pickingMode"], t.sd(txt)["pickingMode_UxmlAttributeFlags"] = 1, 1
    if sorte in ("categorie", "training"):   # survol = phrase FM de la catégorie
        s_tip, r_tip = tip
        b = t.clone(r_tip, cadre, src=s_tip)
        sm.no_styles(t, b)
        texte = t.children(b)[0]
        t.sd(texte)["name"] = ""
        tb = copy.deepcopy(t.sd(texte)["TextBinding"])
        tb["m_kind"] = 1
        tb["m_direct"]["Path"]["m_path"] = "texte"
        t.sd(texte)["TextBinding"] = tb
    return [f"{sorte} : case colorée ({len(bandes)} niveaux) dans {CELLULES[sorte][0]}"]


def cases_appliquer():
    ipc, ni, sm, ouvrir, _ = _modules()
    actuels = {k: ouvrir(v[0]) for k, v in CELLULES.items()}
    if None in actuels.values():
        print("cases : cellules FM introuvables (renommées par une mise à jour ?), ignoré")
        return False
    if all(any(o[3].name(r) == NOM_CASE for r in marques(o[3])) for o in actuels.values()):
        print("cases colorées : déjà appliqué")
        return True
    travail = {k: ouvrir(v[0], depart_original=True) for k, v in CELLULES.items()}
    if any(marques(o[3]) for o in travail.values()):
        print("cases : pas de sauvegarde d'origine propre, rien fait")
        return False
    s_vis, vis = ni.visible_model()
    s_tr = ipc.src_tree(TEXTE_TRADUIT_SOURCE)
    r_tr = s_tr and ipc.first(s_tr, lambda r: (s_tr.sd(r).get("TextBinding") or {}).get("m_kind") == 2 and
                              s_tr.sd(r)["TextBinding"]["m_visualFunction"]["m_target"]["m_guid"].startswith(FN_TRADUCTION))
    tip = ipc.sources()[1]
    if vis is None or r_tr is None or tip is None:
        print("cases : morceaux de FM (SIVisible, texte traduit, infobulle) introuvables, rien fait")
        return False
    outils = (ipc, ni, sm, s_vis, vis, (s_tr, r_tr), tip)
    msgs = []
    for k, o in travail.items():
        msgs += construire_case(o[3], k, outils)
    for m in msgs:
        print(f"cases : {m}")
    if any("introuvable" in m for m in msgs):
        print("cases : rien enregistré")
        return False
    for bundle, obj, tt, t in travail.values():
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    nb.save_all()
    return True


def cases_retirer():
    _, _, _, ouvrir, original = _modules()
    fait = False
    for nom, _ in CELLULES.values():
        o = ouvrir(nom)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = original(bundle, obj)
        if orig is None:
            print(f"{nom} : pas de sauvegarde d'origine")
            continue
        obj.save_typetree(orig)
        sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{nom} : remis d'origine")
    if fait:
        nb.save_all()


# ----------------------------------------------------------------------------------- commandes

def cmd_appliquer():
    # 1. cases (modèles) d'abord : si elles échouent, rien d'autre n'est posé
    if not cases_appliquer():
        return
    # 2. fabrique, avant la vue qui cite ses colonnes
    env = UnityPy.load(FABRIQUES)
    if fabrique_appliquer(env):
        ecrire(FABRIQUES, env)
    else:
        print(f"{FABRIQUE} : colonnes déjà là")
    # 3. vue
    env = UnityPy.load(VUES)
    change = False
    for o, tt in monos(env, VUE):
        voulu = vue_voulue(tt["m_tableView"]["m_tableConfig"])
        if json.dumps(voulu) != json.dumps(tt["m_tableView"]["m_tableConfig"]):
            tt["m_tableView"]["m_tableConfig"] = voulu
            o.save_typetree(tt)
            change = True
            print(f"{VUE} :", " | ".join(c["m_columnID"] for c in voulu))
    if change:
        ecrire(VUES, env)
    else:
        print(f"{VUE} : déjà appliqué")
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
        print("\nÉtat d'esprit façon FM24 en place.")


def cmd_retirer():
    if os.path.exists(MARKER):
        os.remove(MARKER)   # avant : moral_icone_seule ne doit plus recréer nos colonnes
    origine = config_origine()
    env = UnityPy.load(VUES)
    for o, tt in monos(env, VUE):
        cfg = tt["m_tableView"]["m_tableConfig"]
        tt["m_tableView"]["m_tableConfig"] = origine if origine is not None else \
            [c for c in cfg if not c["m_columnID"].startswith("uipicker-")]
        o.save_typetree(tt)
    ecrire(VUES, env)
    env = UnityPy.load(FABRIQUES)
    if fabrique_retirer(env):
        ecrire(FABRIQUES, env)
    cases_retirer()
    print("Vue État d'esprit d'origine remise, nos colonnes et cases retirées.")


def cmd_etat():
    for _, tt in monos(UnityPy.load(VUES), VUE):
        print(f"{VUE} :", " | ".join(c["m_columnID"] for c in tt["m_tableView"]["m_tableConfig"]))
    for _, tt in monos(UnityPy.load(FABRIQUES), FABRIQUE):
        nos = [r["m_id"] for r in tt["m_rowData"] if r["m_id"].startswith("uipicker-")]
        print(f"{FABRIQUE} : colonnes créées :", ", ".join(nos) or "aucune")
    _, _, _, ouvrir, _ = _modules()
    for k, (nom, _) in CELLULES.items():
        o = ouvrir(nom)
        m = o and marques(o[3])
        print(f"case {k} ({nom}) :", ("à jour" if any(o[3].name(r) == NOM_CASE for r in m) else "ANCIENNE version")
              if m else "d'origine")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def actif():
    return os.path.exists(MARKER)


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
        if actif():
            cmd_appliquer()
        else:
            print("état d'esprit FM24 : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
