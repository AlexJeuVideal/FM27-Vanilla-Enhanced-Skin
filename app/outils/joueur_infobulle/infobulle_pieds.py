"""Infobulle du joueur (survol d'un joueur) : style médiatique sous la personnalité, Réputation en bas, et pieds.

- ligne "Style médiatique" sous "Personnalité" + Réputation en bas (fonctions de joueur_fiche\\style_mediatique.py) ;
- joueurs de champ : pied gauche + pied droit (ou le meilleur pied) sous la colonne Physique ; les caractéristiques
  restent dans Infos ;
- gardiens : le "Meilleur pied" reste dans Infos ; les caractéristiques sont retirées
  (le trait de séparation entre meilleur pied et caractéristiques est retiré pour ne pas laisser de double trait).
⚠ À appliquer AVANT style_mediatique.py (fiche) : le bloc des pieds est recopié du tableau d'attributs d'origine.

Usage (jeu fermé) : infobulle_pieds.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)
import sauvegarde_originaux as backup  # noqa: E402
from arbre import Tree, named, PROPRIETES  # noqa: E402
PROPRIETES.update({"height": (131087, 3), "max-height": (131094, 3), "width": (131105, 3)})   # comme fiche_joueur_plus
for _k, _v in {"margin-top": (131093, 3), "align-self": (131074, 7), "margin-right": (131092, 3),
               "text-overflow": (196609, 7), "white-space": (65552, 7),
               "padding-left": (131099, 3)}.items():   # v17 (comme entete_tuile)
    PROPRIETES.setdefault(_k, _v)
from elements import typ, move, plain  # noqa: E402
from attributs_tout_cocher import ouvrir  # noqa: E402  (fiche d'origine sauvegardée)
import style_mediatique as sm_fiche  # noqa: E402  (ligne Style médiatique, Réputation en bas)
from style_mediatique import has_media  # noqa: E402
import lancer  # noqa: E402  (retirer : tout le skin refait après la restauration)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (True = activé, False = désactivé)
# =====================================================================================================
STYLE_MEDIATIQUE = True                      # ligne "Style médiatique" sous "Personnalité" (+ Réputation en bas,
                                             # réglage REPUTATION_EN_BAS de style_mediatique.py)
INFOBULLE_PIED_SOUS_PHYSIQUE = True          # joueurs de champ : pied(s) sous la colonne Physique
INFOBULLE_PIEDS = "les_deux"                 # "les_deux" : pied gauche + pied droit (comme le Rapport joueur)
                                             # "meilleur" : seulement le meilleur pied
INFOBULLE_PIEDS_CENTRES = True               # pied gauche + pied droit centrés sous Physique (sinon calés à gauche)
INFOBULLE_GARDIEN_SANS_CARACTERISTIQUES = True   # gardiens : meilleur pied gardé dans Infos, caractéristiques retirées
INFOBULLE_BOUTON_POLYGONE = True             # v10 : réglage lisible (voir REGLAGE_POLYGONE) ; v8 en jeu : même un texte clignote, la bascule elle-même casse l'infobulle ; bouton en haut à droite d'Infos : polygone à la place des attributs
                                             # (le joueur, 2026-11-12) ; False le retire. v1 à v3 (variables de
                                             # BindingVariablesComponent) : aiguillage SANS enfant en jeu (console du
                                             # mod) ; v4 : réglage global REGLAGE_POLYGONE. Le clic ferme l'infobulle :
                                             # le changement se voit au survol suivant
# =====================================================================================================

INFOBULLE = "PlayerAttributesTooltipBlock"
MARKER = os.path.join(backup.BACKUP_DIR, "infobulle_pieds.actif")
NOM_PIED_PHYSIQUE = "UIPickerMeilleurPiedPhysique"
NOM_DEUX_PIEDS = "UIPickerDeuxPiedsPhysique"
NOM_TRAIT_PIEDS = "UIPickerTraitPieds"
PIEDS_SOURCE = "AttributesTableTemplate"     # tableau d'attributs du Rapport joueur : contient le bloc des deux pieds
PIEDS_MODELE = "PlayerReportFootednessBlock"
NOM_GARDIEN_SEUL = "UIPickerGardienSeulement"
NOM_CHAMP_SEUL = "UIPickerChampSeulement"
NOM_POLYGONE_INFOBULLE = "UIPickerPolygoneInfobulle"
FICHE = "PlayerAttributesLargeBlock"         # fiche joueur d'origine : aiguillage attributs / polygone + bouton
# variable de l'aiguillage, simple (comme {positionmask}{Int|0|} de l'infobulle) : remise à faux à chaque ouverture.
# v1 la gardait pour la session : en jeu zone vide au départ, et une fois cliqué l'infobulle ne s'ouvrait plus
VARIABLE_POLYGONE = ",{polygonselected}{Bool|0|}"
VERSION_POLYGONE = "uipicker-infobulle-polygone-v22"   # +1 à chaque modif : refaite au prochain passage
NOM_PIEDS_POLYGONE = "UIPickerPiedsPolygone"           # v13 : pieds sous le polygone (joueurs de champ)
RAYON_POLYGONE_INFOBULLE = 31                          # v16 : rayon du polygone en % de sa boîte (FM : 34,8)
# v17 (le joueur, 2026-11-11) : vue polygone = colonne gauche (Dispo. transfert | prêt, caractéristiques, pieds) |
# trait | polygone calé à droite
LARGEUR_POLYGONE = 58                                  # % de la zone pour la boîte du polygone (le reste : colonne gauche)
POLYGONE_DROITE = 0                                    # px : écart de la boîte du polygone au trait d'Infos (v17 : 4)
POLYGONE_DECALAGE = 12                                 # v18 (le joueur : « légèrement plus à droite ») : marge
                                                       # intérieure gauche de la boîte (polygone centré décalé de 6 px)
PIEDS_BAS = 12                                         # v18 : pieds un peu surélevés (v17 : 6 px)
STATUT = "PlayerTransferStatusTile_2x2"                # cadres Dispo. transfert / prêt (comme entete_tuile)
STATUT_CADRES = ["transfer-status-text", "loan-status-text"]
TRAITS = "PlayerTraitsFrameList"                       # cadre Caractéristiques de la fiche (titre + liste)
# v21 : ligne de FM SANS infobulle (PlayerTraitsRow12px de la fiche a la description en infobulle : au survol, elle
# fermait la nôtre). PlayerTraitRow (gameworld) : icône + nom, paramètre « trait ». Vérifiée dans m_Container
LIGNE_SANS_INFOBULLE = ("d0b8b323e750dd24faab0ba8074c6ef0", "trait")   # (GUID Addressables, paramètre de ligne)
LIGNE = "PlayerTraitRow"
# v23 (le joueur, 2026-11-11 : logos trop gros, image sans taille dans le modèle) : puce de la fiche au lieu du logo.
# ⚠ PlayerTraitRow sert aussi à TrainingOverviewTile_8x4 (vanilla) : puce là aussi (accepté par le joueur)
VERSION_LIGNE = "uipicker-ligne-puce-v1"
PUCE_SOURCE = "PlayerTraitsRow12px"                    # #IconFrame / #Icon (.bullet-point) de la fiche
ESSAI_TEXTE_AU_LIEU_DU_POLYGONE = False# essai : texte « Infos » à la place du polygone (bascule seule)
# état du bouton : booléen global de FM, gardé hors de l'infobulle. v4-v9 : case de débogage
# `settings.MatchEnablePlaybackModeChangeOutput` → console v9 : une infobulle ne lit pas `settings.` (attributs ET
# polygone masqués). Racines lues dans les infobulles de FM : game. / human. / config. → v10 : option du manager
# « garder l'historique après la retraite » (seul booléen sous ces racines écrit par une case ; choix du joueur)
REGLAGE_POLYGONE = "game.gamecurrentmanager.keephistoryafterretirement"
REGLAGES_POLYGONE_ANCIENS = ("settings.MatchEnablePlaybackModeChangeOutput",)   # retirés au nettoyage
VARIABLE_POLYGONE_V1 =",{polygonselected}{Bool|0|(Session&#44;Implicit&#44;{}&#44;{uipicker-infobulle-polygone})}"


# ---------- 2. infobulle : meilleur pied / caractéristiques ----------
def tooltip_parts(t):
    switch = next((r for r in t.walk() if t.binding(r) and t.binding(r).lower() == "player.isgoalkeeper"), None)
    outfielder = next((c for c in t.children(switch) if t.name(c) == "Outfielder"), None) if switch else None
    physical = None
    if outfielder:
        lst = next((r for r in t.walk(outfielder) if (t.binding(r) or "").lower() == "player.attributesphysical"), None)
        physical = t.parent.get(t.parent.get(lst)) if lst else None   # colonne qui contient la section Physique
    def in_copy(r):   # la copie sous Physique contient aussi le composant "pied" : on ne veut que l'original
        while r in t.parent:
            if t.name(r) == NOM_PIED_PHYSIQUE:
                return True
            r = t.parent[r]
        return False

    foot_comp = next((r for r in t.walk() if not in_copy(r) and any("Footedness.PreferredFoot" in (p.get("value") or "")
                                                                     for p in t.elem(r).get("m_Properties") or [])), None)
    foot_block = t.parent.get(t.parent.get(foot_comp)) if foot_comp else None   # titre + valeur
    foot_container = t.parent.get(foot_block) if foot_block else None          # conteneur dans Infos
    traits = next((r for r in t.walk() if t.name(r) == "Traits"), None)
    traits_container = t.parent.get(traits) if traits else None
    visible_model = next((r for r in t.walk() if t.name(r) == "PersonalityVisibleForActualPlayer"), None)
    return switch, physical, foot_block, foot_container, traits_container, visible_model




def feet_under_physical(t, physical, foot_block):
    """joueurs de champ : pied(s) en bas de la colonne Physique, selon INFOBULLE_PIEDS"""
    msgs = []
    want_two = INFOBULLE_PIEDS == "les_deux"
    # on retire la version qui ne correspond plus au réglage
    for r in named(t, NOM_DEUX_PIEDS if not want_two else NOM_PIED_PHYSIQUE) + (named(t, NOM_TRAIT_PIEDS) if not want_two else []):
        t.remove(r)
        msgs.append("ancienne version des pieds sous Physique retirée")

    if want_two and not named(t, NOM_DEUX_PIEDS):
        # même rendu que le Rapport joueur : un trait puis le bloc "Pied gauche / Pied droit" avec leurs barres
        _, _, stt = nb.find_vta(PIEDS_SOURCE)
        if stt is None:
            return msgs + [f"{PIEDS_SOURCE} introuvable (le jeu a changé ?), pieds non ajoutés"]
        s = Tree(stt)
        feet = next((r for r in s.walk() if s.elem(r).get("m_TemplateAlias") == PIEDS_MODELE), None)
        using = next((u for u in stt.get("m_Usings") or [] if u.get("alias") == PIEDS_MODELE), None)
        if feet is None or using is None:
            return msgs + [f"bloc {PIEDS_MODELE} introuvable dans {PIEDS_SOURCE}, pieds non ajoutés"]
        kids = s.children(s.parent[feet])
        i = kids.index(feet)
        divider = kids[i - 1] if i > 0 and s.elem(kids[i - 1]).get("m_TemplateAlias", "").startswith("layout-divider") else None
        if divider is not None:
            new_div = t.clone(divider, physical, src=s)
            t.sd(new_div)["name"] = NOM_TRAIT_PIEDS
        new_feet = t.clone(feet, physical, src=s)
        t.sd(new_feet)["name"] = NOM_DEUX_PIEDS
        if not any(u.get("alias") == PIEDS_MODELE for u in t.tt.get("m_Usings") or []):
            t.tt["m_Usings"].append(copy.deepcopy(using))   # déclare le modèle inclus (par son identifiant)
        msgs.append("joueurs de champ : pied gauche + pied droit ajoutés sous Physique")

    # centrage : le conteneur du bloc occupe toute la largeur, son contenu (les deux pieds) se centre en groupe
    for r in named(t, NOM_DEUX_PIEDS):
        cls = t.elem(r).setdefault("m_Classes", [])
        if INFOBULLE_PIEDS_CENTRES and "align-items-center" not in cls:
            cls.append("align-items-center")
            msgs.append("pieds centrés sous Physique")
        elif not INFOBULLE_PIEDS_CENTRES and "align-items-center" in cls:
            cls.remove("align-items-center")
            msgs.append("pieds recalés à gauche")

    if not want_two and not named(t, NOM_PIED_PHYSIQUE):
        new = t.clone(foot_block, physical)
        t.sd(new)["name"] = NOM_PIED_PHYSIQUE
        cls = t.elem(new).setdefault("m_Classes", [])
        for c in ("align-self-stretch", "margin-top-global-gap-regular"):
            if c not in cls:
                cls.append(c)
        title = t.children(new)[0]   # titre "Meilleur pied" au style des titres de colonne (comme "Physique")
        if t.sd(title).get("TextBinding"):
            t.elem(title)["m_Classes"] = ["secondary-text-colour", "condensed-xs-regular", "margin-bottom-4"]
        msgs.append("joueurs de champ : meilleur pied ajouté sous Physique")
    return msgs


def tooltip_foot(t):
    msgs = []
    switch, physical, foot_block, foot_cont, traits_cont, vis = tooltip_parts(t)
    if None in (switch, physical, foot_block, foot_cont, traits_cont, vis):
        return ["éléments de l'infobulle introuvables (le jeu a changé ?), ignoré"]

    if INFOBULLE_PIED_SOUS_PHYSIQUE:
        msgs += feet_under_physical(t, physical, foot_block)

    if INFOBULLE_PIED_SOUS_PHYSIQUE and t.name(foot_cont) != NOM_GARDIEN_SEUL:
        t.to_visible(foot_cont, vis, "player.IsGoalkeeper", invert=False, name=NOM_GARDIEN_SEUL)
        msgs.append("Infos : meilleur pied affiché pour les gardiens seulement")

    if INFOBULLE_GARDIEN_SANS_CARACTERISTIQUES and t.name(traits_cont) != NOM_CHAMP_SEUL:
        t.to_visible(traits_cont, vis, "player.IsGoalkeeper", invert=True, name=NOM_CHAMP_SEUL)
        msgs.append("Infos : caractéristiques retirées pour les gardiens")

    # trait de séparation entre meilleur pied et caractéristiques : ferait un double trait / un trait orphelin
    if INFOBULLE_PIED_SOUS_PHYSIQUE or INFOBULLE_GARDIEN_SANS_CARACTERISTIQUES:
        parent = t.parent.get(traits_cont)
        kids = t.children(parent)
        i = kids.index(traits_cont)
        if i > 0 and kids[i - 1] != foot_cont and t.elem(kids[i - 1]).get("m_TemplateAlias", "").startswith("layout-divider"):
            t.remove(kids[i - 1])
            msgs.append("Infos : trait de séparation en trop retiré")
    return msgs

# ---------- 3. infobulle : bouton polygone (à la place des attributs) ----------
def tooltip_polygon(t):
    """bouton du polygone de la fiche (case + icône + infobulle) en haut à droite d'Infos ; coché, le polygone de FM
    prend la place des attributs. État = réglage global REGLAGE_POLYGONE (gardé d'une infobulle à l'autre ; le clic
    ferme l'infobulle, le changement se voit au survol suivant). Éléments recopiés de la fiche d'origine."""
    if any(VERSION_POLYGONE in (t.elem(r).get("m_Classes") or []) for r in named(t, NOM_POLYGONE_INFOBULLE)):
        return []
    tooltip_sans_polygon(t)   # version précédente : refaite
    o = ouvrir(FICHE, depart_original=True)
    src = o and o[3]
    sw_src = src and next((r for r in src.walk() if typ(src, r) == "SI.Bindable.BindableSwitchElement"
                           and src.binding(r) == "polygonselected"), None)
    case = src and next((r for r in src.walk() if typ(src, r) == "SI.Bindable.SICheckBox"
                         and (src.sd(r).get("SelectionBinding") or {}).get("m_path") == "polygonselected"), None)
    attrs = next((r for r in t.walk() if t.binding(r) == "player.IsGoalkeeper"
                  and typ(t, r) == "SI.Bindable.BindableSwitchElement"), None)
    infos = next((k for k in t.children(t.parent[attrs]) if t.name(k) == "Frame"), None) if attrs else None
    tete = infos and next((r for r in t.walk(infos)
                           if "justify-content-space-between" in (t.elem(r).get("m_Classes") or [])), None)
    if None in (sw_src, case, attrs, tete) or len(src.children(sw_src)) != 2:
        return ["infobulle : aiguillage / bouton du polygone ou en-tête Infos introuvable (le jeu a changé ?), ignoré"]

    # attributs et polygone tous les deux construits à l'ouverture, un seul affiché (SIVisible sur le réglage global
    # REGLAGE_POLYGONE, comme les lignes gardien / joueur de champ de l'infobulle). v4 / v5 : aiguillage de FM
    # (BindableSwitchElement) : rien au départ, puis polygone 1 s et infobulle qui clignote (il construit son enfant
    # après coup : l'infobulle change de taille sous la souris). Variables de l'infobulle : jamais lues (console du mod)
    vis = next((r for r in t.walk() if t.name(r) == "PersonalityVisibleForActualPlayer"), None)
    col_src = src.children(sw_src)[1]
    if vis is None:
        return ["infobulle : modèle d'affichage conditionnel introuvable (le jeu a changé ?), ignoré"]
    p = t.parent[attrs]
    sw = plain(t, p, t.children(p).index(attrs), list(t.elem(attrs).get("m_Classes") or []) + [VERSION_POLYGONE],
               NOM_POLYGONE_INFOBULLE)
    t.elem(sw)["m_RuleIndex"] = -1
    boite = plain(t, sw, None, ["flex-grow-class", "height-100-percent"])
    t.elem(boite)["m_RuleIndex"] = -1
    move(t, attrs, boite)
    t.to_visible(boite, vis, REGLAGE_POLYGONE, invert=True, name="")
    col = t.clone(col_src, sw, None, src=src)
    t.styles.copy_from(src.styles, t, col)
    t.to_visible(col, vis, REGLAGE_POLYGONE, invert=False, name="")
    for x in (boite, col):   # construits dès l'ouverture, même cachés (pas après coup, sous la souris)
        if "AlwaysInstantiate" in t.sd(x):
            t.sd(x)["AlwaysInstantiate"] = 1
    # colonne du polygone : mise en page de la fiche (flex-grow, contenu centré) sans sa marge droite. v5-v11 : taille
    # fixe 440 x 230 + overflow hidden (contre le clignotement, dû en fait au réglage illisible) → textes mordus, polygone
    # en haut (le joueur, 2026-11-12 : « bien centré, tous les textes comme il faut »)
    t.elem(col)["m_Classes"] = [c for c in t.elem(col).get("m_Classes") or [] if c != "margin-right-global-gap-large"]
    # v16 (le joueur : textes trop proches) : polygone un peu plus petit (rayon en % de sa boîte, FM 34,8)
    for r in [r for r in t.walk(col) if typ(t, r) == "FM.UI.FMSpiderChart"]:
        t.sd(r)["SpiderChartRadiusPercentage"] = float(RAYON_POLYGONE_INFOBULLE)
    if ESSAI_TEXTE_AU_LIEU_DU_POLYGONE:   # essai : la bascule seule, sans le polygone (v2 en jeu : il plantait)
        for k in list(t.children(col)):
            t.remove(k)
        titre = next(r for r in t.walk(tete) if typ(t, r) == "SI.Bindable.SIText")
        t.clone(titre, col)
    msgs = colonne_gauche(t, col, vis, src)
    if isinstance(msgs, str):
        return [msgs]
    # bouton en haut à droite d'Infos (ligne du titre, déjà « space-between »)
    b = t.clone(case, tete, None, src=src)
    t.styles.copy_from(src.styles, t, b)
    t.sd(b)["SelectionBinding"]["m_path"] = REGLAGE_POLYGONE   # le clic ferme l'infobulle : effet au prochain survol
    # v11 : sans l'infobulle « Analyse des attributs » de la case (infobulle dans l'infobulle ; v10 en jeu : le joueur
    # cliqué ne rouvrait plus la sienne avant un changement d'écran)
    for k in [r for r in t.walk(b) if typ(t, r) == "SI.Bindable.Tooltip"]:
        t.remove(k)
    used = {src.elem(x).get("m_TemplateAlias") for x in list(src.walk(sw_src)) + list(src.walk(case))} - {None, ""}
    for u in src.tt.get("m_Usings") or []:
        if u.get("alias") in used and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
            t.tt["m_Usings"].append(dict(u))
    return ["bouton du polygone en haut à droite d'Infos : polygone à la place des attributs"] + msgs


def guid_present(guid):
    """le modèle de GUID Addressables guid est-il dans un des bundles de modèles (m_Container) ?"""
    for bundle in nb.BUNDLES:
        env = nb.env_of(bundle)
        ab = next((o for o in env.objects if o.type.name == "AssetBundle"), None)
        if ab is not None and any(g == guid for g, _ in ab.read_typetree()["m_Container"]):
            return True
    return False


def ajouter_usings(t, s, racine):
    """modèles inclus dans le sous-arbre racine de s : déclarés dans t (par leur identifiant)"""
    used = {s.elem(x).get("m_TemplateAlias") for x in s.walk(racine)} - {None, ""}
    for u in s.tt.get("m_Usings") or []:
        if u.get("alias") in used and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
            t.tt["m_Usings"].append(dict(u))


def colonne_gauche(t, col, vis, src):
    """v17 (le joueur, 2026-11-11) : dans la vue polygone, rangée colonne gauche | trait | polygone à droite.
    Colonne gauche : en haut Dispo. transfert | Dispo. prêt côte à côte (cadres de PlayerTransferStatusTile_2x2, comme
    l'en-tête de la fiche), au milieu la liste des caractéristiques (PlayerTraitsFrameList de la fiche), en bas les
    2 pieds (joueurs de champ). Sources vérifiées AVANT de toucher à l'arbre ; renvoie les messages ou une erreur (str)"""
    chart = next((r for r in t.walk(col) if typ(t, r) == "FM.UI.FMSpiderChart"), None)
    trait_src = next((r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical"
                      and t.name(r) == "layout-divider-solid-vertical-1"), None)
    o = ouvrir(STATUT, depart_original=True) or ouvrir(STATUT, depart_original=False)
    s = o and o[3]
    cadres = [s and next((r for r in s.walk() if s.name(r) == n), None) for n in STATUT_CADRES]
    # v19 : modèle des caractéristiques recopié EN LIGNE (pas inclus) : sa liste est « flex-no-shrink » (ne se coupe
    # jamais : 4 longues caractéristiques débordaient, titre mordu) → rendue rétrécissable, FM la coupe en « +N »
    ol = ouvrir(TRAITS, depart_original=False)
    tl = ol and ol[3]
    traits = tl and next((r for r in tl.walk() if typ(tl, r).endswith("BindingExpect")), None)
    if not guid_present(LIGNE_SANS_INFOBULLE[0]):
        traits = None
    if None in (chart, trait_src, traits) or None in cadres:
        return "infobulle : polygone, trait, Dispo. transfert / prêt ou caractéristiques introuvables (le jeu a " \
               "changé ?), vue polygone ignorée"

    def boite(parent, classes, css):
        b = plain(t, parent, None, classes)
        t.elem(b)["m_RuleIndex"] = -1
        t.styles.style(t, b, css)
        return b

    def trait(parent):
        k = t.clone(trait_src, parent)
        t.sd(k)["name"] = ""
        return k

    rangee = boite(col, ["row-direction-normal"], {"flex-grow": 1, "flex-shrink": 1, "align-self": "stretch",
                                                   "min-height": 0})
    gauche = boite(rangee, ["column-direction-normal"], {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                                                         "min-width": 0, "overflow": "hidden"})
    trait(rangee)
    poly = boite(rangee, ["column-direction-normal", "align-items-center", "justify-content-center"],
                 {"width": {"unit": 2, "value": float(LARGEUR_POLYGONE)}, "flex-shrink": 0, "align-self": "stretch",
                  "margin-right": POLYGONE_DROITE, "padding-left": POLYGONE_DECALAGE})
    move(t, chart, poly)

    # haut : Dispo. transfert | Dispo. prêt, valeur sur une ligne (« … » + texte complet au survol)
    haut = boite(gauche, ["row-direction-normal"], {"flex-shrink": 0, "align-self": "stretch", "margin-bottom": 8})
    cent = {"unit": 2, "value": 100.0}
    for i, titre in enumerate(cadres):
        if i:
            trait(haut)
        hc = boite(haut, ["column-direction-normal", "align-items-start"],
                   {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden"})
        c = t.clone(s.parent[titre], hc, src=s)
        t.styles.copy_from(s.styles, t, c)
        t.sd(c)["name"] = ""
        ajouter_usings(t, s, s.parent[titre])
        for r in t.walk(c):
            if t.name(r).endswith("-value-text") or t.name(r).endswith("-style-setter"):
                t.styles.style(t, r, {"max-width": cent, "min-width": 0, "flex-shrink": 1, "overflow": "hidden"})
                if typ(t, r).endswith("SIText"):
                    t.styles.style(t, r, {"white-space": "nowrap", "text-overflow": "ellipsis"})
                    for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
                        t.sd(r)[k], t.sd(r)[k + "_UxmlAttributeFlags"] = 1, 1

    # milieu : caractéristiques (gardiens : retirées, comme dans Infos, si INFOBULLE_GARDIEN_SANS_CARACTERISTIQUES)
    milieu = boite(gauche, ["column-direction-normal"], {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                                                         "min-height": 0, "overflow": "hidden"})
    # v22 (le joueur) : gardiens aussi (colonne gauche = Dispo. + caractéristiques, sans pieds), même si Infos les
    # retire (INFOBULLE_GARDIEN_SANS_CARACTERISTIQUES ne vaut que pour Infos)
    k = t.clone(traits, milieu, src=tl)
    t.styles.copy_from(tl.styles, t, k)
    ajouter_usings(t, tl, traits)
    # v18 (le joueur : jamais par-dessus les pieds) : cadre limité à la place du milieu, le milieu coupe le reste
    # (overflow hidden) ; pieds en flex-shrink 0, dessinés après. v19 : toute la chaîne jusqu'à la liste rétrécit
    # (titre gardé entier, liste = la place restante : coupée par FM en « +N » s'il y a trop de caractéristiques)
    for r in set([k] + list(t.walk(k))):
        n = t.name(r)
        if r == k or n in ("PlayerTraitsFrame", "PlayerTraitsSwitch", "PlayerTraitsList"):
            t.elem(r)["m_Classes"] = [c for c in t.elem(r).get("m_Classes") or [] if c != "flex-no-shrink-class"]
            css = {"flex-grow": 1, "flex-shrink": 1, "min-height": 0}
            if n == "PlayerTraitsSwitch":
                css["flex-basis"] = 0
            t.styles.style(t, r, css)
        if n == "PlayerTraitsList":
            # v20 (le joueur) : liste qui défile (barre seulement si ça dépasse) au lieu d'être coupée (Truncate ne
            # mettait pas de « +N », dernière ligne mordue). Lignes ignorées par la souris (SetIgnorePickingMode,
            # comme les clubs intéressés de FM) : l'infobulle de chaque caractéristique fermait la nôtre
            # v21 : SetIgnorePickingMode 1 n'a pas suffi (en jeu) → ligne de FM sans infobulle, souris normale
            # (la molette doit atteindre la liste)
            for champ, v in (("Truncate", 0), ("VerticalScrollerVisibility", 0), ("SetIgnorePickingMode", 0)):
                t.sd(r)[champ], t.sd(r)[champ + "_UxmlAttributeFlags"] = v, 1
            t.sd(r)["RowTemplate"]["m_AssetGUID"] = LIGNE_SANS_INFOBULLE[0]
            t.sd(r)["RowParamName"] = LIGNE_SANS_INFOBULLE[1]
            t.sd(r)["RowTemplate_UxmlAttributeFlags"] = t.sd(r)["RowParamName_UxmlAttributeFlags"] = 1

    # bas : les 2 pieds (joueurs de champ ; gardien : meilleur pied déjà dans Infos). v18 (le joueur) : centrés dans
    # la colonne (align-items-center du bloc sous Physique gardé), un peu surélevés
    a_copier = named(t, NOM_DEUX_PIEDS) + named(t, NOM_PIED_PHYSIQUE)
    if a_copier:
        pieds = boite(gauche, ["column-direction-normal", "align-items-center"],
                      {"flex-shrink": 0, "margin-top": 6, "margin-bottom": PIEDS_BAS})
        for r in a_copier:
            k = t.clone(r, pieds)
            t.sd(k)["name"] = ""
        t.to_visible(pieds, vis, "player.IsGoalkeeper", invert=True, name=NOM_PIEDS_POLYGONE)
    return ["vue polygone : Dispo. transfert | prêt, caractéristiques et pieds à gauche, polygone à droite"]


def tooltip_sans_polygon(t):
    """bouton du polygone retiré (en jeu 2026-11-12 : icône invisible, et une fois cliqué l'infobulle ne s'ouvrait
    plus) : attributs sortis de l'aiguillage, case et variable retirées"""
    fait = False
    for sw in named(t, NOM_POLYGONE_INFOBULLE):
        attrs = next(r for r in t.walk(sw) if t.binding(r) == "player.IsGoalkeeper"
                     and typ(t, r) == "SI.Bindable.BindableSwitchElement")
        move(t, attrs, t.parent[sw], t.children(t.parent[sw]).index(sw))
        t.remove(sw)
        fait = True
    for c in [r for r in t.walk() if typ(t, r) == "SI.Bindable.SICheckBox"
              and (t.sd(r).get("SelectionBinding") or {}).get("m_path") in ("polygonselected", REGLAGE_POLYGONE) + REGLAGES_POLYGONE_ANCIENS]:
        t.remove(c)
        fait = True
    for r in t.walk():
        for p in t.elem(r).get("m_Properties") or []:
            for v in (VARIABLE_POLYGONE_V1, VARIABLE_POLYGONE):
                if p["name"] == "value-vars" and v in p["value"]:
                    p["value"] = p["value"].replace(v, "")
                    fait = True
    var = next((r for r in t.walk() if typ(t, r) == "SI.Bindable.BindingVariablesComponent"), None)
    comp = t.parent.get(var) if var is not None else None
    remap = next((k for k in t.children(comp) if typ(t, k) == "SI.Bindable.BindingRemapperComponent"), None) \
        if comp is not None else None
    if remap is not None and t.children(comp).index(var) != t.children(comp).index(remap) + 1:   # ordre de FM (v3)
        kids = [k for k in t.children(comp) if k != var]
        move(t, var, comp, kids.index(remap) + 1)   # move retire d'abord var : index compté sans lui
        fait = True
    return ["bouton du polygone retiré de l'infobulle"] if fait else []


def ligne_puce(t):
    """ligne de caractéristique de la vue polygone : logo (image à sa taille native, énorme) remplacé par la puce de
    la fiche (#IconFrame de PlayerTraitsRow12px), centrée sur le texte"""
    racine = next((r for r in t.walk() if typ(t, r).endswith("BindingExpect")), None)
    if racine is None or VERSION_LIGNE in (t.elem(racine).get("m_Classes") or []):
        return []
    icone = next((r for r in t.walk() if t.name(r) == "TraitIcon"), None)
    o = ouvrir(PUCE_SOURCE, depart_original=True) or ouvrir(PUCE_SOURCE, depart_original=False)
    s = o and o[3]
    cadre = s and next((r for r in s.walk() if s.name(r) == "IconFrame"), None)
    if icone is None or cadre is None:
        return [f"{LIGNE} : logo ou puce introuvable (le jeu a changé ?), inchangé"]
    i = t.children(racine).index(icone)
    t.remove(icone)
    k = t.clone(cadre, racine, i, src=s)
    t.styles.copy_from(s.styles, t, k)
    cl = t.elem(racine).setdefault("m_Classes", [])
    cl += [c for c in ("align-items-center", VERSION_LIGNE) if c not in cl]
    return ["caractéristiques : puce au lieu du logo"]


# ---------- commandes ----------
def cmd_appliquer():
    title = sm_fiche.find_title_binding() if STYLE_MEDIATIQUE else None

    def travail(model, t):
        if model == LIGNE:
            return ligne_puce(t)
        msgs = []
        if STYLE_MEDIATIQUE:
            msgs += sm_fiche.add_media(t, title)
        if sm_fiche.REPUTATION_EN_BAS:
            msgs += sm_fiche.reputation_last(t)
        return msgs + tooltip_foot(t) + (tooltip_polygon(t) if INFOBULLE_BOUTON_POLYGONE else tooltip_sans_polygon(t))
    sm_fiche.appliquer_modeles([INFOBULLE] + ([LIGNE] if INFOBULLE_BOUTON_POLYGONE else []), travail, MARKER)


def cmd_etat():
    _, _, tt = nb.find_vta(INFOBULLE)
    if tt is None:
        print(f"{INFOBULLE} : introuvable")
    else:
        t = Tree(tt)
        bits = ["style médiatique : " + ("oui" if has_media(t) else "non"),
                "sous Physique : " + ("pied gauche + pied droit" if named(t, NOM_DEUX_PIEDS)
                                      else "meilleur pied" if named(t, NOM_PIED_PHYSIQUE) else "rien"),
                "gardiens sans caractéristiques : " + ("oui" if named(t, NOM_CHAMP_SEUL) else "non")]
        print(f"{INFOBULLE} : " + ", ".join(bits))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        lancer.retirer_par_restauration(MARKER)
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("pieds de l'infobulle : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
