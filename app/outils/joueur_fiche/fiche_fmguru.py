"""Fiche joueur FM Guru (option « fiche_fmguru » = guru, section FM Guru de la page Features additionnelles).

Demande d'un ami du joueur (2026-11-12) ; isolée le 2026-11-12 (le joueur) : la vue Guru prend le dessus sur le skin
pour la fiche joueur. Tant qu'elle est choisie, fiche_joueur_plus (Pour / Contre à la place du polygone, Féliciter /
Critiquer, logos) est désactivée (catalogue.BLOQUES_GURU) ; gardés : en-tête de la fiche, style médiatique, options
d'entraînement sous les attributs (hors_defaut), pastilles Pour / Contre.

Mode Large (FM y cache la colonne du polygone) : colonne Infos coupée en deux, Infos à gauche, polygone à droite (le
polygone est obligatoire, le joueur) ; Suspensions seulement quand la colonne du polygone de FM est là (Medium /
Small) ; attributs plus serrés. Medium / Small : fiche de FM (polygone dans sa colonne).

Toujours posée sur une fiche sans fiche_joueur_plus : s'il en reste (ancienne version, option changée hors de l'app),
les modèles d'origine sont remis et tout le skin refait. Changer l'option dans l'app refait tout le skin aussi
(options.py, « refaire_tout »).

Usage (jeu fermé) : fiche_fmguru.py appliquer [--dry-run] | si-actif | etat
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
from arbre import Tree, named, polygon_visible, polygon_button, Styles  # noqa: E402
from attributs_tout_cocher import ouvrir  # noqa: E402
from elements import first, typ, move, plain, appliquer_jobs  # noqa: E402
import options  # noqa: E402
import langue  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
LARGEUR_POSTES = 360         # colonne des postes (FM : 380, vrai largeur : le trait des attributs vient plus à gauche)
LARGEUR_ATTRIBUTS = 585      # largeur de base des attributs (FM : 860) ; décide seulement quelles colonnes FM affiche
LARGEUR_INFOS = 590          # ... et de la colonne Infos (FM : 295) ; somme gardée (mêmes colonnes dans chaque mode)
LARGEUR_INFOS_MAX = 150      # largeur max des Infos dans la ligne Infos | polygone (FM : 312) ; v18 : 170 → 150
LARGEUR_LIGNE = 485          # largeur fixe de la ligne Infos | polygone (1 px FM = 1,25 px écran) ; v14 : 640 → 540
                             # (attributs du gardien trop serrés) ; v15 : 495 ; v17 : 505 (« un poil » au polygone) ;
                             # v18 : 485, pris sur les Infos (polygone inchangé) : « Dégagement au poing » touchait
RAYON_POLYGONE = 24          # rayon du polygone, en % de sa boîte (FM : 34,8) ; la taille CSS n'y fait rien (v8 à v11)
                             # v19 : 26 → 21 (« 14 Vitesse » coupé) ; v20 : 24 (étiquettes 10 px, plus de place)
ANNEAUX_POLYGONE = 4         # anneaux intérieurs (FM : 1), comme le polygone de FM Guru (le joueur, 2026-11-12)
# étiquettes du polygone : modèle FM SpiderChartColourGradedLabel_10px (catalogue Addressables) au lieu du 18px.
# (v17 / v18 : police réduite par règle à sélecteur, puis par la variable --heading-lg-size : sans effet en jeu)
GUID_ETIQUETTES = "a5645e1771c2b1549b0dfcd072c95560"
FM_LARGEUR_POSTES, FM_LARGEUR_ATTRIBUTS, FM_LARGEUR_INFOS = 380, 860, 295   # largeurs de FM (remises en défaisant)
FM_INFOS_MAX = 312           # largeur max d'InfoBlockFrame chez FM
LARGEUR_INFOS_MEDIUM = 245   # largeur d'Infos en Medium / Small (v24 : mini 240 ; v26 : fixe 300, la même pour tous
                             # les joueurs ; v29 : 270, place donnée au polygone ; v30 : 245, « Jeu aérien » collé au
                             # trait)
LARGEUR_POLYGONE_MEDIUM = 385   # largeur fixe de la colonne du polygone de FM (Medium / Small ; v23 : ~430 ; v24 / v28 :
                                # 320 ; v29 : 360, étiquettes qui débordaient sur le trait et le bord ; v30 : 385)
RAYON_POLYGONE_MEDIUM = 23.4   # rayon (%) du polygone de la colonne de FM (FM : 34,8, réduit en jeu = flash ; v27 : 28 sur
                               # 320 px, flash encore ; v29 : 25 sur 360 ; v30 : 23,4 sur 385 = même taille en px)
# v31 (flash encore en v30) : solution de l'en-tête (entete_tuile v23, technique.md) : boîte fixe qui coupe, graphique
# INTERIEUR fois plus grand dedans (centré) : les étiquettes y tiennent toujours, FM ne réduit plus le rayon
HAUTEUR_POLYGONE_MEDIUM = 330   # hauteur de la boîte visible du polygone (largeur = LARGEUR_POLYGONE_MEDIUM)
RAYON_PX_MEDIUM = 95            # rayon voulu en px (v32 : ~95 px mesurés sur la capture v30, taille validée)
INTERIEUR = 2.0
NOM_BOITE_POLYGONE = "UIPickerGuruBoitePolygone"
HAUTEUR_MIN_CARAC = 66                     # v36 : bloc Caractéristiques = titre + 2 lignes au moins
NOM_ESPACE_CLE = "UIPickerGuruEspaceCle"   # v35 : espace avant la légende Clé / Préférables (légende en bas)
import arbre as _arbre  # noqa: E402
_arbre.PROPRIETES.setdefault("width", (131105, 3))
_arbre.PROPRIETES.setdefault("height", (131087, 3))
_arbre.PROPRIETES.setdefault("max-height", (131094, 3))
CLASSE_MIN_ATTRIBUTS = "player-attributes-block-min-width"   # classe FM (min-width) de la colonne des attributs
CLASSE_SANS_MIN = "uipicker-guru-sans-min-attributs"         # colonne à qui on l'a retirée (defaire la remet)
# =====================================================================================================

OPTION = "fiche_fmguru"
MARKER = os.path.join(backup.BACKUP_DIR, "fiche_fmguru.actif")   # jamais écrit : l'option décide (si-actif)
GROS_BLOC = "PlayerAttributesLargeBlock"
VERSION = "uipicker-guru-v37" # v13 : script à part (avant : v1 à v12 dans fiche_joueur_plus) ; v14 :
                                        # polygone plus petit, attributs plus larges, sans le bouton du polygone ;
                                        # v15 : attributs encore un peu plus larges ; v16 : bouton caché, pas
                                        # retiré (v15 sur v14 : conditions d'affichage perdues, tout en double) ;
                                        # v17 : police du polygone, colonne des postes 360 ; v18 : police par
                                        # variable --heading-lg-size, attributs +20 (Infos 150) ; v21 : bouton
                                        # attributs ↔ polygone affiché dans tous les modes ; v22 : recaché (le
                                        # joueur le voulait dans l'infobulle, pas sur la fiche) ; v23 : ligne
                                        # sans largeur fixe (Medium : plus de vide à droite d'Infos), polygone
                                        # de la colonne de FM réglé comme Guru ; v24 : Infos 240 mini en Medium,
                                        # colonne du polygone 320 max, attributs qui rétrécissent partout ;
                                        # v25 : Infos remplit sa ligne (trait vertical collé) ; v26 : Infos
                                        # de largeur fixe en Medium (300), ligne sans flex-grow ; v27 : rayon
                                        # du polygone de FM 28 % (flash) ; v28 : cale d'Infos sans liaison,
                                        # colonne du polygone fixe 320 (recrutement, chargement) ; v29 : Infos
                                        # 270 (largeur explicite), colonne 360, rayon 25 % ; v30 : Infos 245,
                                        # colonne 385, rayon 23,4 % ; v31 : boîte fixe + graphique 2× (flash) ;
                                        # v32 : sur le BON polygone (colonne), aspect de FM gardé ; v33 : Infos
                                        # dans la ligne (flex-basis 245), tableau de FM en Medium ; v34 : ligne
                                        # de largeur fixe 245, polygone caché tant que player.Age n'est pas lu ;
                                        # v35 : légende Clé / Préférables toujours en bas
NOM_LIGNE = "UIPickerGuruLigne"
NOM_POLYGONE = "UIPickerGuruPolygone"
CLASSE_TABLEAU = "uipicker-guru-tableau"         # tableau d'attributs recopié (mode Large)
CLASSE_TABLEAU_FM = "uipicker-guru-tableau-fm"   # conteneur du modèle inclus de FM (Medium / Small)
CLASSE_CACHE_BOUTON = "uipicker-guru-cache-bouton"   # conteneur qui cache le bouton du polygone (jamais affiché)
NOM_BOUTON_V21 = "UIPickerBoutonPolygone"            # v21 : copie du bouton montrée partout (defaire la retire)
# ajouts de fiche_joueur_plus (incompatibles : la vue Guru part de la fiche de FM)
NOMS_FICHE_PLUS = {"UIPickerPourContre", "UIPickerEntrainementRapide", "UIPickerLogosDynamique",
                   "UIPickerColonnePostes", "UIPickerTraitEntrainement", "UIPickerTraitPourContre"}
GARDE_RECURSION = "UIPICKER_GURU_REFAIT"


def choisie():
    return options.get(OPTION) == "guru"


def propre(t):
    """vrai si la fiche n'a rien de fiche_joueur_plus (ni d'une ancienne vue Guru) : la vue Guru peut s'y poser"""
    if any(t.name(r) in NOMS_FICHE_PLUS for r in t.walk()):
        return False
    col = first(t, lambda r: t.name(r) == "AttributeSpiderChartExpanded")
    if col is not None and not t.find(lambda r: typ(t, r) == "FM.UI.FMSpiderChart", col):
        return False   # polygone retiré par fiche_joueur_plus
    lignes = named(t, NOM_LIGNE)   # ancienne vue Guru (v1 à v12, dans fiche_joueur_plus) : pas défaite ici ; v13 et
    return all(any(c.startswith("uipicker-guru-v") and c[15:].isdigit() and int(c[15:]) >= 13   # plus : defaire()
                   for c in (t.elem(r).get("m_Classes") or [])) for r in lignes)


def defaire(t):
    """vue Guru retirée sur place (tableau recopié retiré et modèle de FM sorti de son conteneur, Infos remise,
    Suspensions sorties de leur conteneur, largeurs de FM) ; ce qu'une autre fonction a posé dans nos conteneurs
    ressort avec, à sa place. True si quelque chose était posé"""
    fait = False
    for x in [x for x in t.walk() if CLASSE_TABLEAU in (t.elem(x).get("m_Classes") or [])]:
        t.remove(x)
        fait = True
    for g in [x for x in t.walk() if CLASSE_TABLEAU_FM in (t.elem(x).get("m_Classes") or [])]:   # v24 : 2 imbriqués
        for k in list(t.children(g)):
            move(t, k, t.parent[g], t.children(t.parent[g]).index(g))
        t.remove(g)
        fait = True
    for x in [x for x in t.walk() if CLASSE_SANS_MIN in (t.elem(x).get("m_Classes") or [])]:
        t.elem(x)["m_Classes"] = [k for k in t.elem(x)["m_Classes"] if k != CLASSE_SANS_MIN] + [CLASSE_MIN_ATTRIBUTS]
        fait = True
    for row in named(t, NOM_LIGNE):
        info = next((k for k in t.walk(row) if t.name(k) == "InfoBlockFrame"), None)   # v24 : dans une colonne
        if info is not None:
            move(t, info, t.parent[row], t.children(t.parent[row]).index(row))
            t.styles.style(t, info, {"max-width": FM_INFOS_MAX, "min-width": 0})   # largeurs de FM
        t.remove(row)
        fait = True
    for g in [x for x in t.walk() if CLASSE_CACHE_BOUTON in (t.elem(x).get("m_Classes") or [])]:
        for k in t.children(g):
            move(t, k, t.parent[g], t.children(t.parent[g]).index(g))
        t.remove(g)
        fait = True
    for b in named(t, NOM_BOITE_POLYGONE):   # v31 : graphique de FM ressorti de sa boîte (v34 : et de son SIVisible)
        for k in [x for x in t.walk(b) if typ(t, x) == "FM.UI.FMSpiderChart"]:
            move(t, k, t.parent[b], t.children(t.parent[b]).index(b))
        t.remove(b)
        fait = True
    for x in named(t, NOM_ESPACE_CLE):   # v35
        t.remove(x)
        fait = True
    for x in named(t, NOM_BOUTON_V21):
        t.remove(x)
        fait = True
    bans = first(t, lambda r: t.name(r) == "PlayerReportBansBlock")
    g = t.parent.get(bans) if bans is not None else None
    # conteneur des Suspensions (v15 en jeu : resté sans condition, le bouton manquait) : FM les met dans InfoBlockFrame
    if g is not None and t.name(g) != "InfoBlockFrame" and t.children(g) == [bans]:
        for k in t.children(g):
            move(t, k, t.parent[g], t.children(t.parent[g]).index(g))
        t.remove(g)
        fait = True
    exp = first(t, lambda r: isinstance((t.sd(r).get("Settings") or {}).get("m_settings"), list))
    if fait and exp is not None and len(t.sd(exp)["Settings"]["m_settings"]) == 7:
        sets = t.sd(exp)["Settings"]["m_settings"]
        sets[0]["PredefinedSize"] = FM_LARGEUR_POSTES
        sets[2]["PredefinedSize"], sets[4]["PredefinedSize"] = FM_LARGEUR_ATTRIBUTS, FM_LARGEUR_INFOS
    return fait


def remettre_bouton(t):
    """bouton du polygone retiré par la v14 : recopié de la fiche d'origine sauvegardée, à sa place dans l'en-tête
    des Infos (ses éléments n'ont pas de règle de style). True si remis"""
    o = ouvrir(GROS_BLOC, depart_original=True)
    if o is None:
        return False
    src = o[3]
    btn = polygon_button(src)
    tete = first(t, lambda r: t.name(r) == "InfoBlockHeaderFrame")
    if btn is None or tete is None or src.name(src.parent[btn]) != "InfoBlockHeaderFrame":
        return False
    t.clone(btn, tete, src.children(src.parent[btn]).index(btn), src=src)
    return True


def guru(t):
    """défaite puis refaite à chaque passage : posée par-dessus ce que les autres fonctions de la fiche ont mis"""
    defaire(t)
    if polygon_button(t) is None and not remettre_bouton(t):
        return ["bouton du polygone introuvable, même dans l'original (le jeu a changé ?), ignoré"]
    info = first(t, lambda r: t.name(r) == "InfoBlockFrame")
    bans = first(t, lambda r: t.name(r) == "PlayerReportBansBlock")
    exp = first(t, lambda r: isinstance((t.sd(r).get("Settings") or {}).get("m_settings"), list))
    chart = first(t, lambda r: typ(t, r) == "FM.UI.FMSpiderChart")
    vdiv = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-vertical")
    if None in (info, bans, exp, chart, vdiv) or len(t.sd(exp)["Settings"]["m_settings"]) != 7:
        return ["colonne Infos, Suspensions, polygone ou éléments introuvables (le jeu a changé ?), ignoré"]

    # Suspensions : seulement quand la colonne du polygone de FM est là (Medium / Small), rien en Large
    frame = t.parent[bans]
    garde = plain(t, frame, t.children(frame).index(bans), ["align-self-stretch"])
    t.elem(garde)["m_RuleIndex"] = -1
    move(t, bans, garde)
    polygon_visible(t, garde)

    # Infos + (mode Large) polygone côte à côte, dans la même colonne du bloc (même nombre de colonnes)
    parent = t.parent[info]
    # v23 (2026-11-07, Medium + texte Grand chez l'ami du joueur) : la ligne n'a plus de largeur fixe (en Medium la
    # partie polygone est cachée : 485 px fixes = ~335 px vides à droite d'Infos, le polygone de FM sortait de
    # l'écran). Partie polygone fixe (LARGEUR_LIGNE - LARGEUR_INFOS_MAX), Infos au moins LARGEUR_INFOS_MAX, ligne au
    # plus LARGEUR_LIGNE : en Large = 485 et Infos 150 comme avant ; en Medium / Small la ligne = Infos seule (150 à
    # 312 selon la place, comme InfoBlockFrame de FM : flex 1 1 0, max 312)
    # v24 (v23 en jeu : Infos écrasée ~110 px en Medium, ligne en flex-basis 0 sans largeur mini ; colonne du polygone
    # trop large) : ligne à la taille de son contenu ; Infos dans une colonne avec une cale invisible (hauteur 0)
    # affichée seulement en Medium / Small (colonne du polygone de FM là) : Infos au moins LARGEUR_INFOS_MEDIUM
    row = plain(t, parent, t.children(parent).index(info), ["row-direction-normal", "align-self-stretch", VERSION],
                NOM_LIGNE)
    t.elem(row)["m_RuleIndex"] = -1
    # v26 (v24 / v25 en jeu : largeurs différentes d'un joueur à l'autre, Infos à la taille de ses textes ; trait
    # vertical loin d'Infos) : Infos de largeur FIXE en Medium / Small = la cale (min = max = LARGEUR_INFOS_MEDIUM),
    # ligne à la taille de son contenu (pas de flex-grow : trait collé à Infos). Large : Infos rétrécit à 150 (ligne
    # max 485 avec la partie polygone 335) comme avant
    # v34 (Caractéristiques encore écrasées en v33) : la ligne doit avoir une largeur FIXE (v22 : 485 fixe, v24 : grow
    # = OK ; v26-v33 : à la taille de son contenu = texte mesuré sans largeur, sur une ligne). Ligne = Infos =
    # LARGEUR_INFOS_MEDIUM (min = max = basis). Mode Guru fait pour le Medium (le joueur) : en Large, la partie
    # polygone à droite d'Infos est coupée (plus de polygone en Large)
    w_i = LARGEUR_INFOS_MEDIUM
    t.styles.style(t, row, {"flex-grow": 0, "flex-shrink": 0, "flex-basis": w_i, "min-width": w_i, "max-width": w_i,
                            "overflow": "hidden"})
    move(t, info, row)
    t.styles.style(t, info, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "max-width": w_i})
    # v28 (le joueur : tailles fixes aussi au recrutement / pendant le chargement) : cale SANS liaison (rien de lié ne
    # tient pendant le chargement d'une fiche, cale_largeur de fiche_joueur_plus) ; en Large elle est coupée par la
    # ligne (max 485 avec la partie polygone 335 : Infos 150)
    # colonne du polygone de FM (Medium / Small) de largeur FIXE : même place et même polygone pour tous les joueurs
    colpoly = first(t, lambda r: t.name(r) == "AttributeSpiderChartExpanded")
    if colpoly is not None:
        t.styles.style(t, colpoly, {"min-width": LARGEUR_POLYGONE_MEDIUM, "max-width": LARGEUR_POLYGONE_MEDIUM,
                                    "flex-grow": 0, "flex-shrink": 0})
    droite = plain(t, row, None, ["row-direction-normal", "align-self-stretch"])
    t.elem(droite)["m_RuleIndex"] = -1
    w = LARGEUR_LIGNE - LARGEUR_INFOS_MAX
    t.styles.style(t, droite, {"flex-grow": 0, "flex-shrink": 0, "min-width": w, "max-width": w})
    polygon_visible(t, droite, inverse=True)
    d = t.clone(vdiv, droite)
    t.sd(d)["name"] = ""
    t.elem(d)["m_Classes"] = ["margin-horizontal-global-gap-large"]
    col = plain(t, droite, None, ["column-direction-normal", "align-items-center", "justify-content-center",
                                  "flex-grow-class"], NOM_POLYGONE)
    t.elem(col)["m_RuleIndex"] = -1
    t.styles.style(t, col, {"min-width": 0})
    poly = t.clone(chart, col)   # polygone de FM recopié (celui de sa colonne reste pour Medium / Small)
    sd = t.sd(poly)
    sd["SpiderChartRadiusPercentage"] = float(RAYON_POLYGONE)
    sd["NumberOfInnerRings"] = ANNEAUX_POLYGONE
    sd["LabelsTemplate"]["m_AssetGUID"] = GUID_ETIQUETTES
    # v23 : polygone de la colonne de FM (Medium / Small) réglé comme celui de Guru (anneaux, étiquettes 10 px ; rayon
    # de FM gardé : sa colonne est faite pour) — en Medium texte Grand, les étiquettes 18 px de FM débordaient
    # v32 : le BON polygone = celui de la colonne AttributeSpiderChartExpanded (Medium / Small). v23 à v31 réglaient
    # le 1er FMSpiderChart trouvé = celui du switch tableau <-> polygone des attributs (caché en Guru) : aucun effet
    # Aspect de FM gardé (étiquettes, anneaux : vus en jeu et validés tels quels). Seul le flash est traité :
    # boîte fixe (sans liaison) LARGEUR_POLYGONE_MEDIUM × HAUTEUR_POLYGONE_MEDIUM qui coupe, graphique INTERIEUR fois
    # plus grand centré dedans, rayon en px converti en % du graphique (entete_tuile v23, technique.md)
    cm = t.find(lambda r: typ(t, r) == "FM.UI.FMSpiderChart", colpoly) if colpoly is not None else None
    cm = cm[0] if isinstance(cm, list) and cm else (cm or None)
    # v37 (le joueur : « enlève ce que tu as testé ») : boîte v32 + SIVisible v34 sans effet sur le flash -> plus
    # posés ; polygone de la colonne remis comme dans la fiche d'origine (classes, style, rayon de FM)
    if cm is not None:
        o = ouvrir(GROS_BLOC, depart_original=True)
        src = o and o[3]
        sc = src and src.find(lambda r: typ(src, r) == "FM.UI.FMSpiderChart",
                              first(src, lambda r: src.name(r) == "AttributeSpiderChartExpanded"))
        sc = sc[0] if isinstance(sc, list) and sc else None
        if sc is not None:
            t.elem(cm)["m_Classes"] = list(src.elem(sc).get("m_Classes") or [])
            t.elem(cm)["m_RuleIndex"] = src.elem(sc).get("m_RuleIndex", -1)
            t.sd(cm)["SpiderChartRadiusPercentage"] = src.sd(sc)["SpiderChartRadiusPercentage"]
    if cm is not None and False:
        pc = t.parent[cm]
        w, h = LARGEUR_POLYGONE_MEDIUM, HAUTEUR_POLYGONE_MEDIUM
        boite = plain(t, pc, t.children(pc).index(cm), ["column-direction-normal", "align-items-center",
                                                         "justify-content-center"], NOM_BOITE_POLYGONE)
        t.elem(boite)["m_RuleIndex"] = -1
        t.styles.style(t, boite, {"width": w, "min-width": w, "max-width": w, "height": h, "min-height": h,
                                  "max-height": h, "flex-grow": 0, "flex-shrink": 0, "overflow": "hidden"})
        # v34 (flash encore au recrutement, flèche suivant / précédent) : graphique dans un SIVisible lié aux données
        # du joueur (player.Age > 0) : caché tant que la fiche n'a pas ses données (entete_tuile v11) ; la boîte
        # autour, sans liaison, garde la place
        import notes_installations as ni
        s_vis, vis = ni.visible_model()
        dedans = boite
        if vis is not None:
            dedans = ni.new_visible(t, s_vis, vis, boite, None, "",
                                    ni.make_binding(s_vis.sd(vis)["Binding"], 4, ["player.Age"], 0),
                                    ["column-direction-normal", "align-items-center", "justify-content-center"])
            t.styles.style(t, dedans, {"flex-shrink": 0})
        move(t, cm, dedans)
        gw, gh = round(w * INTERIEUR), round(h * INTERIEUR)
        t.elem(cm)["m_Classes"] = [c for c in t.elem(cm).get("m_Classes") or []
                                   if c not in ("justify-content-end", "flex-grow-class", "align-self-stretch")]
        t.styles.style(t, cm, {"width": gw, "min-width": gw, "max-width": gw, "height": gh, "min-height": gh,
                               "max-height": gh, "flex-grow": 0, "flex-shrink": 0})
        t.sd(cm)["SpiderChartRadiusPercentage"] = round(RAYON_PX_MEDIUM * 100.0 / min(gw, gh), 2)

    # v35 (le joueur : au recrutement, légende Clé / Préférables collée sous les attributs, pas en bas) : sur les
    # joueurs des autres clubs il n'y a pas la barre d'entraînement (hors_defaut) ; espace qui grandit juste avant
    # la légende (sans liaison) = légende toujours en bas du bloc
    cle = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "AttributesKey")
    if cle is not None:
        esp = plain(t, t.parent[cle], t.children(t.parent[cle]).index(cle), [], NOM_ESPACE_CLE)
        t.elem(esp)["m_RuleIndex"] = -1
        t.styles.style(t, esp, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})

    # v36 (le joueur : une SEULE caractéristique sur 2 lignes = texte écrasé ; plusieurs = OK) : la liste de FM
    # calcule sa hauteur avant le retour à la ligne quand elle n'a qu'un élément -> hauteur mini du bloc = titre +
    # 2 lignes (HAUTEUR_MIN_CARAC)
    # v37 (le joueur : « enlève ce que tu as testé », sans effet en jeu) : hauteur mini retirée (0 = celle de FM)
    carac = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "PlayerTraitsFrameList")
    if carac is not None and False:
        t.styles.style(t, carac, {"min-height": HAUTEUR_MIN_CARAC})
    if carac is not None:
        t.styles.style(t, carac, {"min-height": 0})

    # colonne des postes jamais réduite ; tableau d'attributs recopié en ligne (mode Large) sans « flex-no-shrink » :
    # il rétrécit (le modèle inclus gardait sa largeur et débordait). Medium / Small : modèle inclus de FM.
    roles = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "role_selector-large")
    if roles is not None:
        t.styles.style(t, roles, {"flex-shrink": 0})
    tc = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "AttributesTableTemplate")
    bundle, _, stt = nb.find_vta("AttributesTableTemplate")
    if tc is not None and stt is not None:
        src, sst = Tree(stt), Styles(bundle, stt)
        holder = t.parent[tc]
        i = t.children(holder).index(tc)
        # v24 (« serrer un poil les attributs » en Medium) : la copie qui rétrécit sert dans TOUS les modes ; le modèle
        # de FM reste (defaire le remet) dans deux conteneurs aux conditions contraires = jamais affiché ; classe
        # min-width de FM retirée de la colonne des attributs
        # v33 (le joueur : sur les joueurs d'AUTRES clubs la fiche disparaît une seconde, même sans la tuile
        # Efficacité) : retour au modèle inclus de FM en Medium / Small (la copie en ligne y perd sans doute les
        # paramètres du modèle inclus, cf. visibilityMask, technique.md) ; copie qui rétrécit en Large seulement
        # (comme v7 à v23). Classe min-width de FM laissée en place.
        g = plain(t, holder, i, ["align-self-stretch", CLASSE_TABLEAU_FM])
        t.elem(g)["m_RuleIndex"] = -1
        move(t, tc, g)
        polygon_visible(t, g)
        large = plain(t, holder, i + 1, ["align-self-stretch", CLASSE_TABLEAU])
        t.elem(large)["m_RuleIndex"] = -1
        t.styles.style(t, large, {"min-width": 0, "overflow": "hidden"})
        polygon_visible(t, large, inverse=True)
        root = src.children(src.tt["m_VisualTree"]["rid"])[0]
        copie = t.clone(root, large, src=src)
        t.styles.copy_from(sst, t, copie)
        used = {src.elem(x).get("m_TemplateAlias") for x in src.walk(root)} - {None, ""}
        for u in src.tt.get("m_Usings") or []:
            if u.get("alias") in used and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
                t.tt["m_Usings"].append(dict(u))
        for x in t.walk(copie):
            cls = t.elem(x).get("m_Classes") or []
            if "flex-no-shrink-class" in cls or x == copie or t.name(x) in ("Outfielder", "Goalkeeper"):
                t.elem(x)["m_Classes"] = [c for c in cls if c != "flex-no-shrink-class"]
                t.styles.style(t, x, {"min-width": 0, "flex-shrink": 1, "overflow": "hidden"})

    # bouton au-dessus des Infos qui ouvre le polygone de FM : caché sur cette fiche (le joueur, 2026-11-12 ; v21 le
    # montrait partout, le joueur le voulait dans l'infobulle : v22 le recache). PAS retiré : les conditions d'affichage
    # (polygon_visible, ici et dans hors_defaut) copient sa liaison (v14 le retirait : v15 posée par-dessus sans
    # conditions, tout en double en jeu). Il est mis dans un conteneur affiché seulement quand la colonne du polygone
    # est là, lui seulement quand elle n'y est pas.
    tete = first(t, lambda r: t.name(r) == "InfoBlockHeaderFrame")
    for k in (list(t.children(tete)) if tete is not None else []):
        if t.find(lambda r: typ(t, r) == "SI.Bindable.SICheckBox", k):
            cache = plain(t, tete, t.children(tete).index(k), [CLASSE_CACHE_BOUTON])
            t.elem(cache)["m_RuleIndex"] = -1
            move(t, k, cache)
            polygon_visible(t, cache)

    sets = t.sd(exp)["Settings"]["m_settings"]
    sets[0]["PredefinedSize"] = LARGEUR_POSTES
    sets[2]["PredefinedSize"], sets[4]["PredefinedSize"] = LARGEUR_ATTRIBUTS, LARGEUR_INFOS
    return ["fiche FM Guru (mode Large) : Infos | polygone, sans Suspensions, "
            f"postes {LARGEUR_POSTES} px, attributs {LARGEUR_ATTRIBUTS} px, Infos {LARGEUR_INFOS} px, "
            f"polygone : étiquettes 10 px, {ANNEAUX_POLYGONE} anneaux, rayon {RAYON_POLYGONE} %"]


def refaire_tout():
    """modèles d'origine remis puis tout le skin refait (la vue Guru se pose à la fin, sur une fiche propre)"""
    print(langue.texte("fiche joueur : restes de la version du skin, tout le skin est refait à partir des originaux",
                       "player profile: skin version leftovers, the whole skin is redone from the originals"))
    nb.cmd_restore()
    env = dict(os.environ, **{GARDE_RECURSION: "1"})
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                 "commun", "lancer.py"), "skin", langue.LANGUE], env=env)


def cmd_appliquer():
    _, _, tt = nb.find_vta(GROS_BLOC)
    if tt is None:
        print(f"{GROS_BLOC} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    if not propre(Tree(tt)):
        if nb.DRY_RUN:
            print("(essai à blanc) fiche pas propre : l'application refera tout le skin à partir des originaux")
            return
        if os.environ.get(GARDE_RECURSION):
            print(f"{GROS_BLOC} : restes de fiche_joueur_plus même après remise d'origine, vue Guru ignorée")
            return
        refaire_tout()
        return
    # 2026-11-10 (le joueur) : fix des caractéristiques sur 2 lignes de fiche_joueur_plus (liste-traits, validé en jeu)
    # aussi en vue Guru (fiche_joueur_plus y est bloquée) ; import ici : fiche_joueur_plus importe ce module
    import fiche_joueur_plus as fjp
    appliquer_jobs([(GROS_BLOC, guru_si_change), (fjp.LISTE_TRAITS, fjp.liste_traits)], os.devnull)


def guru_si_change(t):
    """vue déjà posée (ligne Guru de cette version) : rien. Défaite puis refaite, elle ajoutait à chaque passage de
    nouvelles règles de style (feuille qui grossit) et Vérifier la disait toujours « pas à jour » (2026-11-12)"""
    if any(VERSION in (t.elem(r).get("m_Classes") or []) for r in named(t, NOM_LIGNE)):
        return []
    return guru(t)


def cmd_etat():
    _, _, tt = nb.find_vta(GROS_BLOC)
    t = Tree(tt) if tt is not None else None
    pose = t is not None and any(VERSION in (t.elem(r).get("m_Classes") or []) for r in named(t, NOM_LIGNE))
    print(f"option : {options.get(OPTION)} ; vue Guru posée : {'oui' if pose else 'non'}")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "si-actif":
        if choisie():
            cmd_appliquer()
        else:
            print("fiche FM Guru : pas choisie, rien à faire")
    elif op == "etat":
        cmd_etat()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
