"""ESSAI (2026-11-12, demande du joueur, méthode B) : rangée du bas de la fiche joueur (Vue d'ensemble : État d'esprit,
Condition physique, Forme, Entraînement, Stats saison, Stats carrière) vue comme UN seul bloc, séparé par des traits,
chaque tuile gardant son sélecteur (le ⌄ est posé par la grille de FM, pas par la tuile).

Deux morceaux :
- écran PlayerReport (grille ScalableBindableGridLayoutElement de la Vue d'ensemble) : un repère « uipickerfiche »
  (const.One) transmis à chaque tuile de la grille (m_nameBindings + m_gridElementBindingData), sauf le gros bloc du
  haut. Les autres pages ne le transmettent pas. Chaque modèle de tuile de la fiche (et le cadre) l'ajoute à ses
  Parameters (facultatif, comme isonmainscreen) : un modèle inclus ne lit une donnée du parent que si elle y est.
- cadre commun des tuiles (tile-figma-base-template, TOUTES les tuiles du jeu) : dans le bouton de la tuile, juste
  après son bord, un SIVisible « uipickerfiche == 1 » (BindIntToVisible de FM : repère absent = caché) qui contient
  un fond + bord de tuile sans coins arrondis, élargi de la moitié de l'écart de la grille de chaque côté : les fonds
  voisins se touchent, les bords gauche / droit des voisins tombent sur la même colonne = un trait entre les tuiles.
À voir en jeu : le repère arrive-t-il jusqu'au cadre ? le fond élargi est-il coupé au bord de la tuile ? l'écart
(ECART) est-il le bon ? le ⌄ reste-t-il au-dessus ? les autres pages restent-elles d'origine ?

Repart toujours des modèles d'origine (sauvegarde). Retiré par le choix 1 et le 105 (zone d'essai).
Usage (jeu fermé) : essai_fiche_bas_bloc.py appliquer [--dry-run] | retirer | etat
"""
import copy
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
import notes_installations as ni  # noqa: E402
from notes_installations import first  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
ECART = 16                # px d'écart entre deux tuiles de la grille (supposé, capture du joueur) : à ajuster en jeu
TEST_ROUGE = False        # v2 : fond teinté + bord rouges, pour VOIR s'il s'affiche (v1 vue en jeu : rien de changé ;
#                           repère absent, ou fond coupé au bord de la tuile et identique à elle ?)
# =====================================================================================================

VERSION = 8   # v1 : vue en jeu (2026-11-12), aucun changement visible ; v2 : fond en rouge (diagnostic) : vu, les
#               6 tuiles rouges (repère OK) mais coupées au bord de la tuile ; v3 : overflow visible sur le bouton et
#               ses parents du cadre (TOUTES les tuiles du jeu : à surveiller ailleurs) : vu, une bande rouge
#               continue avec les traits (2026-11-12) ; v4 : vraie couleur, grille de la fiche coupée à ses bords
#               (le fond élargi des tuiles du bout ne dépasse plus) : vu, un seul bloc avec le haut ; v5 : grille =
#               ordre État d'esprit, Condition, Stats saison, Carrière, Forme, Entraînement, tailles fixes, Stats
#               saison élargie jusqu'au bord du bloc du haut ; v6 : ni fond ni survol de tuile (SIStyleSetter de FM
#               sur le repère), traits seuls, repère vrai / faux : vu, fond de FM resté (17,19,23 dans la tuile,
#               9,16,18 dans les écarts) ; v7 : classes de fond / bord posées d'office retirées (le setter seul) : vu,
#               ordre OK, mais rangée moins large que le haut et qui dépasse à gauche d'un demi-écart ; v8 : Stats
#               saison s'étire (maxi du bloc du haut), traits des tuiles du bout calés sur leur bord (DEBUT / FIN),
#               Entraînement au bout dans toutes les dispositions (Small / Large-FMC : à la place de Forme)
SANS_COUPE = True         # v3 : overflow visible du bouton jusqu'à la racine du cadre
ECRAN = "PlayerReport"
CADRE = "tile-figma-base-template"
REPERE = "uipickerfiche"
DEBUT, FIN = REPERE + "debut", REPERE + "fin"   # v8 : 1re / dernière tuile de la rangée du bas
PREMIERE, DERNIERE = "Happiness", "PlayerTrainingOverview"
REPERES = [REPERE, DEBUT, FIN]
CONSTANTE = "const.True"   # v6 : vrai / faux (le SIStyleSetter de FM lit un booléen ; v1-v5 : const.One)
HORS_BLOC = ["PlayerAttributesBlock"]       # gros bloc du haut : garde son aspect de tuile
PREFIXE = "UIPickerFicheBloc"
NOM = f"{PREFIXE}-v{VERSION}"
OP_EGAL = 2
CLASSES_FOND = ["layout-tile-interaction-button-background", "surfaces-card-tile-border",
                "border-color-layout-modules-block-border-colour"]
CLASSES_TRAITS = ["border-color-layout-modules-block-border-colour"]   # v6 : traits et tour seulement, pas de fond
SANS_FOND_TUILE = True    # v6 (le joueur : « on veut que ça fasse partie de l'écran ») : ni fond ni survol de tuile
SANS_FOND = "uipicker-fiche-sans-fond"    # classes vides (aucune règle) posées à la place du fond / du bord de FM
SANS_BORD = "uipicker-fiche-sans-bord"
CLASSE_BORD = "surfaces-card-tile-border"
CLASSE_FOND = "layout-tile-interaction-button-background"
for _k, _v in {"position": (131102, 7), "top": (131104, 3), "left": (131089, 3), "right": (131103, 3),
               "bottom": (131080, 3), "border-top-left-radius": (458764, 3), "border-top-right-radius": (458765, 3),
               "border-bottom-left-radius": (458759, 3), "border-bottom-right-radius": (458760, 3),
               "border-color": (262146, 4)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
SANS_COINS = {"border-top-left-radius": 0, "border-top-right-radius": 0, "border-bottom-left-radius": 0,
              "border-bottom-right-radius": 0}
BORDS = {"border-top-width": 1, "border-bottom-width": 1, "border-left-width": 1, "border-right-width": 1}


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


CLASSE_GRILLE = f"uipicker-fiche-bloc-v{VERSION}"   # repère « déjà appliqué » posé sur la grille


def element_grille(t):
    """grille de la Vue d'ensemble (celle qui a des liaisons de tuiles)"""
    return first(t, lambda r: typ(t, r) == "ScalableBindableGridLayoutElement"
                 and ((t.sd(r).get("Bindings") or {}).get("m_gridElementBindingData")))


def grille(t):
    r = element_grille(t)
    return t.sd(r)["Bindings"] if r is not None else None


def ecran_fait(t):
    r = element_grille(t)
    return r is not None and CLASSE_GRILLE in (t.elem(r).get("m_Classes") or [])


def construire_ecran(t):
    b = grille(t)
    if b is None:
        return ["grille de la Vue d'ensemble introuvable, ignoré"]
    g = element_grille(t)
    # v4 : la grille coupe à ses bords le fond élargi des tuiles du bout (fiche seulement)
    t.elem(g)["m_Classes"] = list(t.elem(g).get("m_Classes") or []) + [CLASSE_GRILLE]
    t.styles.style(t, g, {"overflow": "hidden"})
    noms = b["m_nameBindings"]
    if not noms:
        return ["liaisons de noms vides, ignoré"]
    for r in REPERES:
        n = copy.deepcopy(noms[0])
        n["name"], n["path"]["m_path"] = r, CONSTANTE
        noms.append(n)
    data = b["m_gridElementBindingData"]
    tuiles = []
    for d in list(data):
        desc = d["DescriptionAndMapping"]["DescriptionName"]
        if desc in HORS_BLOC or desc in tuiles:
            continue
        tuiles.append(desc)
        # v8 : DEBUT / FIN seulement aux tuiles du bout de la rangée (celles de la disposition du skin)
        for r in [REPERE] + [r for r, t_ in ((DEBUT, PREMIERE), (FIN, DERNIERE)) if t_ == desc]:
            x = copy.deepcopy(d)
            x["DescriptionAndMapping"]["MappingName"] = r
            data.append(x)
    return [f"repère « {REPERE} » transmis à {len(tuiles)} tuiles ({', '.join(tuiles)}), "
            f"« {DEBUT} » à {PREMIERE}, « {FIN} » à {DERNIERE}"]


def cadre_fait(t):
    return any(t.name(r) == NOM for r in t.walk())


def construire_cadre(t):
    bouton = first(t, lambda r: t.name(r) == "layout-tile-interaction-button")
    bord = first(t, lambda r: t.name(r) == "Border_TIle")
    if bouton is None or bord is None or t.parent.get(bord) != bouton:
        return ["bouton / bord du cadre de tuile introuvables, ignoré"]
    setter = first(t, lambda r: t.name(r) == "BackgroundStyleSetter")
    if setter is None or t.parent.get(bouton) != setter:
        return ["sélecteur de fond du cadre introuvable, ignoré"]
    s_vis, vis = ni.visible_model()
    if vis is None:
        return ["modèle de comparaison FM introuvable, ignoré"]
    # v6 (le joueur : pas de couleur de tuile ni de survol, mais le clic garde) : le SIStyleSetter de FM remplace sur
    # son enfant (le bouton) la classe de fond par celle en surbrillance si sa donnée est vraie (FM : const.False).
    # Branché sur le repère, avec une classe vide : fond ET survol retirés sur la fiche, le bouton (clic) reste.
    arguments_setter(t, setter, REPERE, SANS_FOND)
    # v7 (vu v6 : fond de FM resté, mesuré sur la capture) : le setter ne retire pas la classe posée d'office sur
    # l'enfant -> retirée ; le setter seul la pose (classe « faux » ailleurs, classe vide sur la fiche)
    t.elem(bouton)["m_Classes"] = [c for c in t.elem(bouton)["m_Classes"] if c != CLASSE_FOND]
    t.elem(bord)["m_Classes"] = [c for c in t.elem(bord)["m_Classes"] if c != CLASSE_BORD]
    # même chose pour le bord de FM : un SIStyleSetter (copie) autour de #Border_TIle
    cadre_bord = t.clone_shallow(setter, bouton, t.children(bouton).index(bord))
    t.sd(cadre_bord)["name"], t.sd(cadre_bord)["name_UxmlAttributeFlags"] = PREFIXE + "Bord", 1
    t.elem(cadre_bord)["m_Classes"], t.elem(cadre_bord)["m_RuleIndex"] = [], -1
    t.styles.style(t, cadre_bord, {"position": "absolute", "top": 0, "bottom": 0, "left": 0, "right": 0})
    arguments_setter(t, cadre_bord, REPERE, SANS_BORD, CLASSE_BORD)
    deplacer(t, bord, cadre_bord)
    index = t.children(bouton).index(cadre_bord) + 1   # au-dessus du bord de FM, sous le titre et le contenu
    def visible(parent, idx, nom, chemin, inverse=False, css=None):
        v = ni.new_visible(t, s_vis, vis, parent, idx, nom, {
            "m_kind": 1, "m_direct": {"Path": {"m_path": chemin}, "Nullable": 0},
            "m_visualFunction": {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                 "m_outputs": {"m_variable": {"m_argumentBytes": []}}}})   # vrai / faux direct
        sd = t.sd(v)
        sd["name_UxmlAttributeFlags"] = 1
        sd["InvertDirectBinding"] = 1 if inverse else 0
        if "pickingMode" in sd:   # ne prend pas les clics (la tuile garde son survol / clic)
            sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1
        t.elem(v)["m_RuleIndex"] = -1
        t.styles.style(t, v, css or {"position": "absolute", "top": 0, "bottom": 0, "left": 0, "right": 0})
        return v

    v = visible(bouton, index, NOM, REPERE)
    moitie = ECART / 2
    # v4 (le joueur : « TOUT l'écran en 1 tuile », bloc du haut compris) : le fond monte aussi de tout l'écart (+1 px :
    # son bord haut passe sous le bord bas du bloc du haut = un seul trait) ; la grille coupe à ses bords
    t.styles.style(t, v, {"position": "absolute", "top": -(ECART + 1), "bottom": 0, "left": 0, "right": 0})
    # v8 (vu v7 : la rangée dépasse du bloc du haut d'un demi-écart à gauche) : la 1re tuile (repère DEBUT) a son trait
    # gauche sur son bord, la dernière (FIN) son trait droit ; les autres au milieu de l'écart (trait partagé)
    for debut in (True, False):
        vd = visible(v, len(t.children(v)), f"{PREFIXE}Debut{int(debut)}", DEBUT, inverse=not debut)
        for fin in (True, False):
            vf = visible(vd, len(t.children(vd)), f"{PREFIXE}Fin{int(fin)}", FIN, inverse=not fin)
            fond = t.clone_shallow(bord, vf)
            t.elem(fond)["m_Classes"] = list(CLASSES_TRAITS if SANS_FOND_TUILE else CLASSES_FOND)
            t.elem(fond)["m_RuleIndex"] = -1
            t.sd(fond)["name"], t.sd(fond)["name_UxmlAttributeFlags"] = PREFIXE + "Fond", 1
            if "pickingMode" in t.sd(fond):
                t.sd(fond)["pickingMode"], t.sd(fond)["pickingMode_UxmlAttributeFlags"] = 1, 1
            t.styles.style(t, fond, {"position": "absolute", "top": 0, "bottom": 0,
                                     "left": 0 if debut else -moitie, "right": 0 if fin else -(moitie + 1),
                                     **SANS_COINS, **BORDS,
                                     **({"border-color": (1, 0, 0, 1), "background-color": (0.6, 0, 0, 1)}
                                        if TEST_ROUGE else {})})
    coupes = 0
    if SANS_COUPE:   # le fond élargi ne doit pas être coupé au bord de la tuile (vu en v2)
        r = bouton
        while r is not None and r != t.tt["m_VisualTree"]["rid"]:
            t.styles.style(t, r, {"overflow": "visible"})
            coupes += 1
            r = t.parent.get(r)
    msgs = ajouter_param(t)   # le cadre (modèle inclus) doit attendre le repère pour le lire
    msgs += [f"rien coupé sur {coupes} éléments du cadre"] if coupes else []
    return msgs + [f"fond commun posé (si repère), élargi de {moitie:g} px de chaque côté"]


def attend(t):
    """Parameters du BindingExpect racine (un modèle inclus ne voit une donnée du parent que si elle y est)"""
    r = first(t, lambda r: typ(t, r) == "BindingExpect")
    return t.sd(r).get("Parameters") if r is not None else None


def param_fait(t):
    noms = {p.get("name") for p in attend(t) or []}
    return all(r in noms for r in REPERES)


def param_present(t):
    return any(p.get("name") in REPERES for p in attend(t) or [])


def ajouter_param(t):
    ps = attend(t)
    if not ps:
        return ["paramètres de la tuile introuvables, ignoré"]
    manquants = [r for r in REPERES if r not in {p.get("name") for p in ps}]
    for r in manquants:
        p = copy.deepcopy(next((p for p in ps if p.get("name") == "isonmainscreen"), ps[0]))
        p.update(name=r, isOptional=1, type={"id": 0})   # comme isonmainscreen : facultatif, sans type
        ps.append(p)
    return [f"paramètre « {', '.join(manquants)} » (facultatif) ajouté"]


def retirer_param(t):
    ps = attend(t)
    ps[:] = [p for p in ps if p.get("name") not in REPERES]
    return ["paramètre retiré"]


def arguments_setter(t, r, chemin, si_vrai, si_faux=None):
    """fonction FM d47d9f6b du SIStyleSetter r : (donnée vrai / faux, classe si vrai, classe si faux, ...)"""
    vf = t.sd(r)["BindFunction"]
    args = ni.decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    textes = [a for a in args if a[0] == b"SI.VisualScripting.StringVisualArg"]
    for a in args:
        if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            p = chemin.encode()
            a[1] = b"\x01" + ni._enc_varint(len(p)) + p
    for a, valeur in zip(textes, (si_vrai, si_faux)):
        if valeur is not None:
            v = valeur.encode()
            a[1] = b"\x01" + ni._enc_varint(len(v)) + v
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = ni.encode_args(args)


def deplacer(t, r, parent):
    ancien = t.parent[r]
    t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != r]
    t.elem(parent)["m_Children"].append({"rid": r})
    t.elem(r)["m_Parent"] = {"rid": parent}
    t.parent[r] = parent


PARTIES = [(ECRAN, ecran_fait, construire_ecran), (CADRE, cadre_fait, construire_cadre)]
# tuiles de la grille de la fiche (tailles comprises) : le repère y est ajouté PAR-DESSUS (d'autres fonctions du skin
# retouchent certaines de ces tuiles : pas de départ de l'original)
TUILES = [f"{m}_{s}" for m, tailles in {
    "PlayerFitnessTile": "2x1 2x2 4x2 4x4 8x4", "PlayerHappinessTile": "2x2 4x2 4x4",
    "PlayerFormTile": "2x2 4x2 4x4 8x4", "PlayerSeasonStatsTile": "2x1 2x2 4x2 4x4 8x2 8x4",
    "TrainingOverviewTile": "2x1 2x2 4x2 4x4 8x4", "CareerStatsTile": "2x2 4x2 4x4 8x4",
    "PlayerLoanReportTile": "2x2 4x2 4x4 8x4", "PlayerHomegrownStatusTile": "2x1 2x2 4x2 4x4"}.items()
    for s in tailles.split()]


# ---------- grille (ui-tileslayouts) : ordre de la rangée du bas, Stats saison élargie (v5, demande du joueur) ----------
TUILES_GRILLE = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
ENSEMBLE = "PlayerReportOverviewCompositionSet"
HAUT = "PlayerAttributesBlock"
ORDRE = ["Happiness", "FItness", "PlayerSeasonStats", "CareerStats", "PlayerForm", "PlayerTrainingOverview"]
REMPLACEE = "PlayerForm"   # v8 : cède sa place à Entraînement là où FM n'en met pas (Small / Large-FMC)
ELARGIE = "PlayerSeasonStats"   # seule tuile qui change de taille : prend la place pour finir au bord du bloc du haut
# largeurs imposées (le reste : celle de FM). Standard : Stats carrière vue en 2 de large chez le joueur (capture du
# 2026-11-12), gardée telle quelle
LARGEURS = {"PlayerReportOverviewComposition-Standard": {"CareerStats": 2}}


def compositions(env):
    objs = {o.path_id: o for o in env.objects}
    ens = None
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                if o.peek_name() == ENSEMBLE:
                    ens = o.read_typetree()
                    break
            except Exception:
                continue
    if ens is None:
        return []
    return [(objs[r["m_PathID"]], objs[r["m_PathID"]].read_typetree())
            for e in ens["m_gridBreakpointCompositionData"]["m_values"] for r in e["m_value"]
            if r["m_FileID"] == 0 and r["m_PathID"] in objs]


def rangee_voulue(orig, modele_derniere=None):
    """composants : bloc du haut tel quel ; dessous, dans l'ORDRE, chaque tuile à sa taille fixe (mini = maxi : FM
    ne répartit plus de place en trop), Stats saison jusqu'au bord ; None si la composition n'a pas cette forme"""
    comps = copy.deepcopy(orig["m_gridComponents"])
    # v8 : la dernière tuile porte le repère FIN -> au bout partout ; sans place pour elle (Small / Large-FMC), elle
    # remplace Forme (même largeur)
    ids = [c["m_elementID"] for c in comps]
    if DERNIERE not in ids and REMPLACEE in ids and modele_derniere is not None:
        i = ids.index(REMPLACEE)
        c = copy.deepcopy(modele_derniere)
        for k in ("m_location", "m_minSize", "m_maxSize"):
            c[k] = copy.deepcopy(comps[i][k])
        comps[i] = c
    haut = next((c for c in comps if c["m_elementID"] == HAUT), None)
    par_nom = {c["m_elementID"]: c for c in comps}
    if haut is None or ELARGIE not in par_nom or set(par_nom) - set(ORDRE) - {HAUT}:
        return None
    total, y = haut["m_location"]["width"], haut["m_location"]["height"]
    imposees = LARGEURS.get(orig["m_Name"], {})
    rangee = [par_nom[n] for n in ORDRE if n in par_nom]
    for c in rangee:
        if c["m_elementID"] in imposees:
            c["m_location"]["width"] = imposees[c["m_elementID"]]
    reste = total - sum(c["m_location"]["width"] for c in rangee if c["m_elementID"] != ELARGIE)
    if reste < par_nom[ELARGIE]["m_location"]["width"]:
        return None
    par_nom[ELARGIE]["m_location"]["width"] = reste
    x = 0
    for c in rangee:
        l = c["m_location"]
        l.update(x=x, y=y)
        c["m_minSize"]["x"], c["m_minSize"]["y"] = l["width"], l["height"]
        c["m_maxSize"]["x"], c["m_maxSize"]["y"] = l["width"], l["height"]
        if c["m_elementID"] == ELARGIE:   # FM étire le bloc du haut (maxi 100) : Stats saison prend le reste
            c["m_maxSize"]["x"] = haut["m_maxSize"]["x"]
        x += l["width"]
    return [haut] + rangee


def grille_tuiles(retirer):
    env = UnityPy.load(TUILES_GRILLE)
    src = backup.backup_path(TUILES_GRILLE)
    origine = {o.path_id: tt for o, tt in compositions(UnityPy.load(src if os.path.exists(src) else TUILES_GRILLE))}
    actuelles = compositions(env)
    if not actuelles:
        return [f"{ENSEMBLE} : introuvable, ignoré"]
    msgs, change = [], False
    modele_derniere = next((c for tt in origine.values() for c in tt["m_gridComponents"]
                            if c["m_elementID"] == DERNIERE), None)
    for o, tt in actuelles:
        orig = origine.get(o.path_id)
        if orig is None or len(orig["m_gridComponents"]) < 2:   # Phone_Landscape : bloc du haut seul
            continue
        comps = orig["m_gridComponents"] if retirer else rangee_voulue(orig, modele_derniere)
        if comps is None:
            msgs.append(f"{tt['m_Name']} : autre forme, laissée")
            continue
        if tt["m_gridComponents"] == comps:
            continue
        tt["m_gridComponents"] = copy.deepcopy(comps)
        o.save_typetree(tt)
        change = True
        msgs.append(f"{tt['m_Name']} : " + ("d'origine" if retirer else " | ".join(
            f"{c['m_elementID']} {c['m_location']['width']}" for c in comps[1:])))
    if change:
        data = env.file.save(packer="original")
        if nb.DRY_RUN:
            msgs.append(f"(essai à blanc : rien écrit, {os.path.basename(TUILES_GRILLE)} ferait {len(data) / 1e6:.2f} Mo)")
        else:
            backup.write_bundle(TUILES_GRILLE, data)
    else:
        msgs.append(f"{ENSEMBLE} : " + ("déjà d'origine" if retirer else "déjà appliqué"))
    return msgs


def par_dessus(fait, fn, voulu):
    """fn sur chaque tuile telle qu'elle est, si fait(t) != voulu ; True si une a changé"""
    change = False
    for modele in TUILES:
        o = hp.ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable, ignoré")
            continue
        bundle, obj, tt, t = o
        if fait(t) == voulu:
            continue
        msgs = fn(t)
        print(f"{modele} : {msgs[0]}")
        if not any("ignoré" in m for m in msgs):
            enregistrer(bundle, obj, tt, t)
            change = True
    return change


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def cmd_appliquer():
    change = False
    for modele, fait, construire in PARTIES:
        o = hp.ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        if fait(o[3]):
            print(f"{modele} : déjà appliqué")
            continue
        bundle, obj, tt, t = hp.ouvrir(modele, depart_original=True)
        if fait(t):
            print(f"{modele} : ancienne version présente et pas d'original, retirer d'abord")
            continue
        msgs = construire(t)
        for m in msgs:
            print(f"{modele} : {m}")
        if not any("ignoré" in m for m in msgs):
            enregistrer(bundle, obj, tt, t)
            change = True
    if par_dessus(param_fait, ajouter_param, True) or change:
        nb.save_all()
    else:
        print(f"tuiles : repère déjà attendu par les {len(TUILES)} tuiles")
    for m in grille_tuiles(retirer=False):
        print(m)


def cmd_retirer():
    change = False
    for modele, fait, _ in PARTIES:
        o = hp.ouvrir(modele)
        if o is None or not fait(o[3]):
            continue
        bundle, obj, tt, t = hp.ouvrir(modele, depart_original=True)
        if fait(t):
            print(f"{modele} : pas de sauvegarde d'origine, rien retiré")
            continue
        enregistrer(bundle, obj, tt, t)
        change = True
        print(f"{modele} : remis d'origine")
    change = par_dessus(param_present, retirer_param, False) or change
    if change:
        nb.save_all()
    else:
        print("essai fiche (bas en un bloc) : rien à retirer")
    for m in grille_tuiles(retirer=True):
        print(m)


def cmd_etat():
    for modele, fait, _ in PARTIES:
        o = hp.ouvrir(modele)
        print(f"{modele} : " + ("introuvable" if o is None else "essai posé" if fait(o[3]) else "d'origine"))
    n = sum(1 for m in TUILES if (o := hp.ouvrir(m)) is not None and param_fait(o[3]))
    print(f"tuiles : repère attendu par {n} / {len(TUILES)}")


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
