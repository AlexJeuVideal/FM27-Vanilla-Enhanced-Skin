"""Pastilles Pour / Contre comme FM24 (rond coloré selon la note, logo blanc dedans, texte au survol) : moteur et
réglages communs (tailles, couleurs NUANCES) des fonctions qui les affichent :
- joueur_infobulle\\infobulle_pour_contre.py : infobulle joueur, le bloc « Rapport du préparateur / du recruteur »
  remplacé par Niveau + Potentiel en étoiles et les Pour / Contre en pastilles (CoachScoutReportTooltipBlock +
  PlayerAbilityCellWithBorder, cellule FM inutilisée remplacée par la pastille construite depuis StrengthWeaknessCell
  d'origine ; v15 : StrengthWeaknessCell elle-même n'est plus touchée, FM27 s'en sert dans les rapports d'équipe) ;
- joueur_fiche\\listes_pour_contre.py : listes Pour / Contre FM27 de la fiche (data_display-string-list-item-pro-con) ;
- joueur_entete\\entete_fiche.py : ProConRow (cellule FM inutilisée) = la même pastille en plus grand pour l'en-tête.
Chaque fonction est seule propriétaire de ses modèles : appliquer repart des originaux sauvegardés, retirer les remet.
Listes = WrappedObjectList (recopiée de TeamMeetingBlock, à la ligne) sur report.ScoutedProConsList.ProsList / ConsList.
(Avant le rangement du 2026-11-12 : tout dans infobulle_pour_contre.py.)
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, no_styles, MOITIE  # noqa: E402
from elements import move, plain, set_text_binding  # noqa: E402
from attributs_tout_cocher import original, ouvrir  # noqa: E402
from hierarchie_pyramide import path_arg  # noqa: E402
from notes_installations import (decode_args, encode_args, _enc_varint, visible_model, new_visible,  # noqa: E402
                                 equal_binding)

# ============================== RÉGLAGES (en changer un -> augmenter VERSION) ==============================
PASTILLE = 22                   # diamètre de la pastille (px) ; FM : 24 (v1 : 26, 4 par ligne, débordait)
LOGO = 14                       # taille du logo dans la pastille (px) ; FM : 16
ECART = 1                       # marge autour de chaque pastille (px)
COULEURS = "nuances"            # "nuances" = NUANCES ci-dessous selon la note ; "pour_contre" = vert / rouge FM27 ;
                                # "note" = 7 couleurs FM27 selon la note (vert -> jaune -> rouge)
# couleur par note ProConRating (0..6), comme les rapports FM24 (ex. régularité : 18-20, 15-17, 12-14, rien, 7-9, 4-6, 1-3)
# v6 (plus clair : #4CE65C #86D93B #C2DC45 #B0B5BE #FFA04D #FF6F4F #FF4058) refusé : « trop exposé »
# v7 = couleurs v5, sauf le meilleur Pour (0) en vert foncé pour bien le distinguer du 1 (v5 : #3FB54A)
NUANCES = ["#0A5A26",   # 0 très (régulier) — vert foncé (v11 : #16823A, v12 : #0F6E30)
           "#56A626",   # 1 (régulier) — vert (v4-v12 : #4E9A22)
           "#86A31E",   # 2 assez (régulier) — vert olive
           "#8A8F98",   # 3 neutre (FM24 : aucune information) — gris
           "#E0692C",   # 4 assez (irrégulier) — orange
           "#D8452B",   # 5 (irrégulier) — rouge orangé
           "#B81F2E"]   # 6 très (irrégulier) — rouge foncé
VOILE = 0.25                    # voile noir sur le rond (0 = couleurs FM27 vives, 0.5 = très sombre) ; logo non voilé
LIGNES_MAX = 2                  # lignes de pastilles visibles par cadre (5 par ligne -> 10 max), le reste est caché
ECART_HAUT = 3                  # px entre Niveau / Potentiel et les cadres (v10 : 6)
TITRE_AU_DESSUS = True          # Niveau / Potentiel : titre centré au-dessus des étoiles (False = à gauche, tronqué)
TITRES_PETITS = ["body-sm-strong", "content-ellipsis"]   # classes FM des titres Niveau actuel / Potentiel
CADRE_FOND = (1, 1, 1, 0.06)    # fond des cadres POUR / CONTRE (rouge, vert, bleu, opacité)
CADRE_ARRONDI = 6               # px
TITRE_DU_BLOC = False           # garder le titre FM « Rapport du préparateur » au-dessus (FM24 : non)
INFOBULLE_PASTILLE = True       # survol d'une pastille : texte long du Pour / Contre
LISTES_FM27_EN_NUANCES = True   # listes FM27 (fiche joueur…) : couleurs NUANCES selon la note au lieu de vert / rouge
PASTILLE_LISTE, LOGO_LISTE = 32, 20   # taille pastille / logo dans les listes de la fiche (v8 : 22 / 14 ; v9-v11 : 28 / 18)
PASTILLE_BANDEAU, LOGO_BANDEAU = 28, 18   # en-tête de la fiche (fiches_plus) ; 0 = pas de cellule à part
LISTES_STYLE = "pastille"       # "pastille" = rond coloré + logo blanc (comme l'infobulle) ; "logo" = logo teinté
# ==========================================================================================================
VERSION = 15  # v2 : titres petits, pastilles 22 px, voile ; v3 : vert / rouge FM27 ; v4 : nuances FM24 par note ;
#               v5 : mêmes nuances dans les listes FM27 (fiche joueur) ; v6 : nuances plus claires (refusé) ;
#               v7 : retour v5, meilleur Pour en vert foncé ; v8 : pastilles aussi dans les listes de la fiche ; v9 : 28 / 18 px ;
#               v10 : infobulle, titres Niveau / Potentiel au-dessus des étoiles ; v11 : 2 lignes max, resserré ; v12 : top vert plus foncé, fiche 32 / 20 ; v13 : top encore plus foncé, note 1 un poil plus claire ; v14 : pastille de l'en-tête (ProConRow)
#               v15 : pastille de l'infobulle dans PlayerAbilityCellWithBorder, StrengthWeaknessCell remise d'origine
GUID_COULEURS = "08392e5c3d207f64685c8d63d6f5c9ac"   # ProConColourDataCollection (clé IsPro -> Colour)
PREFIXE = "UIPickerPourContre"
NOM = f"{PREFIXE}-v{VERSION}"
NOM_PASTILLE = f"UIPickerPastille-v{VERSION}"
NOM_PASTILLE_BANDEAU = f"UIPickerPastilleBandeau-v{VERSION}"
BLOC, CELLULE = "CoachScoutReportTooltipBlock", "StrengthWeaknessCell"   # CELLULE : source de la pastille, gardée
# d'origine (FM27 : Analyse de formation > Tactique probable, rapport d'équipe ; v1-v14 la réécrivaient -> textes perdus)
CELLULE_LIBRE = "PlayerAbilityCellWithBorder"   # cellule FM inutilisée (index GUID FM27, 2026-10-30) -> pastille
LISTE_FM = "data_display-string-list-item-pro-con"   # ligne des listes Pour / Contre FM27 (fiche joueur, rapports)
# lignes Avantages / Inconvénients du rapport de l'adjoint (onglet Prestation, CoachReportBlock_*) : même logo FM,
# paramètre « row » (2026-11-12, le joueur : « pas les pastilles comme partout »)
LIGNES_RAPPORT = {"CoachReportProsRow": "row.ProConRating", "CoachReportConsRow": "row.ProConRating"}
CELLULE_BANDEAU = "ProConRow"   # cellule FM inutilisée (catalogue Addressables) -> pastille de l'en-tête (fiches_plus)
MODELES = [BLOC, CELLULE_LIBRE, CELLULE] + ([LISTE_FM] if LISTES_FM27_EN_NUANCES else []) + \
    ([CELLULE_BANDEAU] if PASTILLE_BANDEAU else [])
GUID_CELLULE = "550f84322fd82eb4e91ed42c0c7af3f0"   # PlayerAbilityCellWithBorder (v1-v14 : 1fcf53e2… StrengthWeaknessCell)
LISTE_SOURCE, LISTE = "TeamMeetingBlock", "Players"   # WrappedObjectList
TITRES_SOURCE = "ScoutedProsAndCons"                  # titres traduits « Pour » / « Contre »
INFOBULLE_SOURCE = "PlayerAttributesLargeBlock"       # SI.Bindable.Tooltip + SIText (bouton du polygone)
LISTES = [("pros-heading", "report.ScoutedProConsList.ProsList"),
          ("cons-heading", "report.ScoutedProConsList.ConsList")]
for k, v in {"width": (131105, 3), "height": (131087, 3), "flex-direction": (131083, 7), "flex-wrap": (131086, 7),
             "justify-content": (131088, 7), "align-self": (131074, 7), "align-items": (131073, 7),
             "padding": (262151, 3), "border-radius": (262147, 3), "margin-left": (131091, 3),
             "margin-right": (131092, 3), "margin-top": (131093, 3), "margin-bottom": (131090, 3),
             "min-width": (131097, 3), "max-width": (131095, 3), "min-height": (131096, 3),
             "max-height": (131094, 3), "position": (131102, 7), "top": (131104, 3), "left": (131089, 3),
             "-unity-background-image-tint-color": (196610, 4)}.items():
    sm.PROPRIETES.setdefault(k, v)
MARGES = lambda v: {f"margin-{c}": v for c in ("left", "right", "top", "bottom")}  # noqa: E731
PLEIN = {"position": "absolute", "top": 0, "left": 0, "width": {"unit": 2, "value": 100.0},
         "height": {"unit": 2, "value": 100.0}}


def _rgba(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


CARRE = lambda v: {k: v for k in ("width", "height", "min-width", "min-height", "max-width", "max-height")}  # noqa: E731


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def src_tree(model):
    _, _, tt = nb.find_vta(model)
    return Tree(tt) if tt is not None else None


def first(t, pred, root=None):
    return next((r for r in t.walk(root) if pred(r)), None) if root is not None else \
        next((r for r in t.walk() if pred(r)), None)


def nouveau(t, parent, index, classes, css, name=""):
    v = plain(t, parent, index, classes, name)
    t.elem(v)["m_RuleIndex"] = -1
    if name:
        t.sd(v)["name_UxmlAttributeFlags"] = 1
    if css:
        t.styles.style(t, v, css)
    return v


# ---------- la pastille (StrengthWeaknessCell réécrite) ----------
def construire_pastille(t, tip_src):
    racine = first(t, lambda r: t.name(r) == "StrengthWeaknessCell")
    setter = racine is not None and first(t, lambda r: typ(t, r) == "SIStyleSetter", racine)
    frame = racine is not None and first(t, lambda r: t.name(r) == "Frame", racine)
    if not (racine and setter and frame):
        return ["StrengthWeaknessCell : pastille introuvable (le jeu a changé ?)"]
    t.remove(frame)   # textes court / long
    t.sd(racine)["name"], t.sd(racine)["name_UxmlAttributeFlags"] = NOM_PASTILLE, 1
    t.elem(racine)["m_Classes"] = ["align-items-center", "justify-content-center"]
    t.styles.style(t, racine, {**MARGES(ECART), "align-self": "auto", "flex-shrink": 0})
    rond = t.children(setter)[0]   # ui-concepts-placeholder_medium : le rond (teinté par la note)
    t.elem(rond)["m_Classes"] = [c for c in t.elem(rond).get("m_Classes") or [] if not c.startswith("margin-")]
    t.styles.style(t, rond, CARRE(PASTILLE))
    logo = first(t, lambda r: typ(t, r) == "SIImage", rond)
    t.styles.style(t, logo, CARRE(LOGO))
    msgs = [f"pastille {PASTILLE} px (logo {LOGO} px), textes retirés"]
    if COULEURS == "pour_contre":   # comme la liste FM27 : ProConColourDataCollection sur IsPro -> pro-item / con-item
        bf = t.sd(setter)["BindFunction"]["m_inputs"]["m_variable"]
        args = decode_args(bf["m_argumentBytes"])
        for a in args:
            if a[0] == b"SI.VisualScripting.AssetReferenceVisualArg":
                a[1] = a[1].replace(b"a7083723296b79d42b0f53ab7f24d5af", GUID_COULEURS.encode())
            elif a[0] == b"SI.VisualScripting.StringVisualArg":
                a[1] = b"\x01" + _enc_varint(len(b"Colour")) + b"Colour"
            elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                a[1] = b"\x01" + _enc_varint(len(b"procon.IsPro")) + b"procon.IsPro"
        bf["m_argumentBytes"] = encode_args(args)
        msgs.append("couleurs vert / rouge (Pour / Contre) comme la liste FM27")
    if COULEURS == "nuances":   # nos couleurs : un disque par note, chacun dans un SIVisible « ProConRating == k »
        s, vis = visible_model()
        if vis is None:
            return msgs + ["modèle de SIVisible introuvable : nuances non posées"]
        t.styles.style(t, rond, {"-unity-background-image-tint-color": (0, 0, 0, 0)})   # rond FM effacé
        for k, couleur in enumerate(NUANCES):
            v = new_visible(t, s, vis, rond, t.children(rond).index(logo), f"UIPickerNuance{k}",
                            equal_binding(s.sd(vis)["Binding"], "procon.ProConRating", k))
            t.sd(v)["name_UxmlAttributeFlags"] = 1
            t.styles.style(t, v, PLEIN)
            disque = nouveau(t, v, None, [], {**PLEIN, "border-radius": {"unit": 2, "value": 50.0},
                                               "background-color": _rgba(couleur)})
            t.sd(disque)["pickingMode"], t.sd(disque)["pickingMode_UxmlAttributeFlags"] = 1, 1
        msgs.append("couleurs = 7 nuances par note (comme les rapports FM24)")
    if VOILE > 0 and COULEURS != "nuances":   # rond noir transparent par-dessus la couleur, sous le logo (une opacité voilerait aussi le logo)
        voile = nouveau(t, rond, t.children(rond).index(logo), [],
                        {"position": "absolute", "top": 0, "left": 0, "width": {"unit": 2, "value": 100.0},
                         "height": {"unit": 2, "value": 100.0}, "border-radius": {"unit": 2, "value": 50.0},
                         "background-color": (0, 0, 0, VOILE)})
        t.sd(voile)["pickingMode"], t.sd(voile)["pickingMode_UxmlAttributeFlags"] = 1, 1   # Ignore : survol inchangé
        msgs.append(f"couleurs voilées à {VOILE}")
    if INFOBULLE_PASTILLE:
        s, tip = tip_src
        b = t.clone(tip, racine, src=s)
        no_styles(t, b)
        texte = t.children(b)[0]
        t.sd(texte)["name"] = ""
        set_text_binding(t, texte, {"m_kind": 1, "m_direct": {"Path": {"m_path": "procon.ProConsLongString"},
                                                              "Nullable": 0},
                                    "m_visualFunction": {"m_target": {"m_guid": ""},
                                                         "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                                         "m_outputs": {"m_variable": {"m_argumentBytes": []}}}})
        msgs.append("survol = texte du Pour / Contre")
    return msgs


# ---------- recopie de la pastille dans une cellule FM inutilisée ----------
def recopier_pastille(t, c, modele):
    """contenu de t (cellule FM inutilisée) remplacé par une copie de la pastille déjà construite dans c"""
    racine_uxml = t.tt["m_VisualTree"]["rid"] if "m_VisualTree" in t.tt else None
    expect_c = c.children(c.tt["m_VisualTree"]["rid"])[0] if "m_VisualTree" in c.tt else None
    if racine_uxml is None or expect_c is None:
        return None, [f"{modele} : racine introuvable"]
    for k in list(t.children(racine_uxml)):
        t.remove(k)
    copie = t.clone(expect_c, racine_uxml, src=c)
    t.styles.copy_from(c.styles, t, copie)
    return copie, []


# ---------- la même pastille en plus grand pour l'en-tête de la fiche (fiches_plus) ----------
def construire_pastille_bandeau(t, c):
    """ProConRow (cellule FM inutilisée) remplacée par une copie de la pastille déjà construite dans c, agrandie"""
    copie, msgs = recopier_pastille(t, c, CELLULE_BANDEAU)
    if copie is None:
        return msgs
    for r in t.walk(copie):
        if t.name(r) == NOM_PASTILLE:
            t.sd(r)["name"] = NOM_PASTILLE_BANDEAU
        elif t.name(r) == "ui-concepts-placeholder_medium":
            t.styles.style(t, r, CARRE(PASTILLE_BANDEAU))
        elif typ(t, r) == "SIImage":
            t.styles.style(t, r, CARRE(LOGO_BANDEAU))
    return [f"pastille de l'en-tête de la fiche {PASTILLE_BANDEAU} px (logo {LOGO_BANDEAU} px)"]


# ---------- les listes FM27 (fiche joueur, rapports) : logo teinté selon la note ----------
def construire_liste_fm(t, modele=LISTE_FM, note="binding.ProConRating", marges=None):
    """logo FM (0043cf8d, vert / rouge) gardé transparent pour la place ; dedans, une copie par note teintée NUANCES[k]
    (modele / note : aussi les lignes du rapport de l'adjoint, LIGNES_RAPPORT ; marges None = celles du logo FM)"""
    img = first(t, lambda r: typ(t, r) == "SIImage"
                and "0043cf8d" in str((t.sd(r).get("Binding") or {}).get("m_visualFunction", {}).get("m_target")))
    if img is None:
        return [f"{modele} : logo introuvable"]
    s, vis = visible_model()
    if vis is None:
        return ["modèle de SIVisible introuvable : listes non teintées"]
    if LISTES_STYLE == "pastille":   # comme l'infobulle : rond coloré selon la note + logo blanc
        parent = t.parent[img]
        if marges is None:
            marges = [x for x in t.elem(img).get("m_Classes") or [] if x.startswith("margin-")]
        rond = nouveau(t, parent, t.children(parent).index(img),
                       ["align-items-center", "justify-content-center"] + marges,
                       {**CARRE(PASTILLE_LISTE), "flex-shrink": 0}, f"{PREFIXE}Liste-v{VERSION}")
        for k, couleur in enumerate(NUANCES):
            v = new_visible(t, s, vis, rond, None, f"{PREFIXE}Liste{k}-v{VERSION}",
                            equal_binding(s.sd(vis)["Binding"], note, k))
            t.sd(v)["name_UxmlAttributeFlags"] = 1
            t.styles.style(t, v, PLEIN)
            disque = nouveau(t, v, None, [], {**PLEIN, "border-radius": {"unit": 2, "value": 50.0},
                                               "background-color": _rgba(couleur)})
            t.sd(disque)["pickingMode"], t.sd(disque)["pickingMode_UxmlAttributeFlags"] = 1, 1
        move(t, img, rond)   # logo FM par-dessus, en blanc (le style inline passe avant la classe pro-item / con-item)
        t.elem(img)["m_Classes"] = [x for x in t.elem(img).get("m_Classes") or [] if not x.startswith("margin-")]
        t.styles.style(t, img, {**CARRE(LOGO_LISTE), "-unity-background-image-tint-color": (1, 1, 1, 1)})
        return ["listes FM27 (fiche joueur…) : pastilles colorées selon la note" if modele == LISTE_FM else
                f"{modele} (rapport de l'adjoint) : pastilles colorées selon la note"]
    modele = t.clone(img, t.parent[img])   # copie faite avant d'ajouter des enfants au logo
    t.elem(modele)["m_Classes"] = [x for x in t.elem(modele).get("m_Classes") or [] if not x.startswith("margin-")]
    for k, couleur in enumerate(NUANCES):
        v = new_visible(t, s, vis, img, None, f"{PREFIXE}Liste{k}-v{VERSION}",
                        equal_binding(s.sd(vis)["Binding"], note, k))
        t.sd(v)["name_UxmlAttributeFlags"] = 1
        t.sd(v)["pickingMode"], t.sd(v)["pickingMode_UxmlAttributeFlags"] = 1, 1
        t.styles.style(t, v, PLEIN)
        t.styles.style(t, t.clone(modele, v), {"-unity-background-image-tint-color": _rgba(couleur)})
    t.remove(modele)
    t.styles.style(t, img, {"-unity-background-image-tint-color": (0, 0, 0, 0)})
    return ["listes FM27 (fiche joueur…) : logo teinté selon la note"]


# ---------- le bloc de l'infobulle ----------
def contenu(t, parent, coach_col, sources):
    """colonne : [Niveau ★ | Potentiel ★] puis [POUR | CONTRE] ; coach_col = colonne FM Niveau / Potentiel (déplacée)"""
    lst, liste, ttr = sources
    col = nouveau(t, parent, None, [], {"flex-grow": 1, "flex-direction": "column"}, NOM)
    # Niveau / Potentiel sur une ligne : titre puis étoiles (le texte « Leader de Premier League » est retiré)
    ligne = nouveau(t, col, None, ["row-direction-normal", "align-items-center"], {"margin-bottom": ECART_HAUT})
    for nom_bloc, nom_info in (("Cur-Ability", "CurAbilityInfo"), ("Pot-Ability", "PotInfo")):
        bloc = first(t, lambda r: t.name(r) == nom_bloc, coach_col)
        move(t, bloc, ligne)
        info = first(t, lambda r: t.name(r) == nom_info, bloc)
        if info is not None:
            t.remove(info)
        titre = t.children(bloc)[0]
        t.elem(titre)["m_Classes"] = list(TITRES_PETITS)
        if TITRE_AU_DESSUS:   # v10 : titre centré au-dessus des étoiles (place prise sur le vide sous les logos)
            t.elem(bloc)["m_Classes"] = ["align-items-center"]
            t.styles.style(t, bloc, {"flex-direction": "column"})
            t.styles.style(t, titre, {"margin-bottom": -2, "margin-right": 0, "max-width": {"unit": 2, "value": 100.0},
                                      "overflow": "hidden"})
        else:   # le titre rétrécit (« … ») plutôt que les étoiles (v1 : il chevauchait le Potentiel)
            t.elem(bloc)["m_Classes"] = ["row-direction-normal", "align-items-center"]
            t.styles.style(t, titre, {"margin-bottom": 0, "margin-right": 4, "flex-shrink": 1, "min-width": 0,
                                      "overflow": "hidden"})
        etoiles = t.children(bloc)[1]
        t.elem(etoiles)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        t.styles.style(t, etoiles, {"flex-shrink": 0})
        if nom_bloc == "Pot-Ability":
            t.styles.style(t, bloc, {**MOITIE, "overflow": "hidden", "margin-left": 6})
        else:
            t.styles.style(t, bloc, {**MOITIE, "overflow": "hidden"})
    # POUR | CONTRE
    rang = nouveau(t, col, None, ["row-direction-normal"], {"flex-grow": 1, "align-items": "stretch"})
    for i, (titre_nom, chemin) in enumerate(LISTES):
        cadre = nouveau(t, rang, None, ["align-items-center"],
                        {**MOITIE, "flex-direction": "column", "background-color": CADRE_FOND,
                         "border-radius": CADRE_ARRONDI, "padding": 3, **({"margin-left": 6} if i else {})})
        titre_src = first(ttr, lambda r: ttr.name(r) == titre_nom)
        titre = t.clone(titre_src, cadre, src=ttr)
        no_styles(t, titre)
        t.sd(titre)["name"] = ""
        t.elem(titre)["m_Classes"] = ["body-sm-strong", "global-text-primary"]
        t.styles.style(t, titre, {"margin-bottom": 2})
        w = t.clone(liste, cadre, src=lst)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": GUID_CELLULE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], chemin)
        sd["ItemParamName"] = "procon"
        sd["ItemUssClassName"] = ""
        t.elem(w)["m_Classes"] = []
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "wrap", "justify-content": "center",
                              "align-self": "stretch",
                              "max-height": LIGNES_MAX * (PASTILLE + 2 * ECART), "overflow": "hidden"})
    return col


def construire_bloc(t, sources):
    coach = first(t, lambda r: t.name(r) == "CoachBlock")
    scout = first(t, lambda r: t.name(r) == "ScoutBlock")
    a_rapport = coach is not None and first(t, lambda r: t.name(r) == "BindableSwitchElement_HasReport", coach)
    infos = scout is not None and first(t, lambda r: t.name(r) == "HasScoutedInfo", scout)
    coach_col = a_rapport and t.children(a_rapport)[0]
    if not (a_rapport and infos and coach_col and first(t, lambda r: t.name(r) == "Cur-Ability", coach_col)):
        return ["CoachScoutReportTooltipBlock : blocs préparateur / recruteur introuvables (le jeu a changé ?)"]
    # préparateur : la colonne FM Niveau / Potentiel est remplacée par la nôtre (même place dans le switch)
    col = contenu(t, a_rapport, coach_col, sources)
    move(t, col, a_rapport, 0)
    t.remove(coach_col)
    # recruteur : même contenu à la place de la description du joueur + recommandation
    for k in list(t.children(infos)):
        t.remove(k)
    t.clone(col, infos)
    t.styles.style(t, infos, {"flex-grow": 1})
    msgs = ["Niveau / Potentiel en étoiles + POUR / CONTRE en logos (préparateur et recruteur)"]
    if not TITRE_DU_BLOC:
        for nom in ("CoachTitle", "ScoutTitle"):
            r = first(t, lambda x: t.name(x) == nom)
            if r is not None:
                t.remove(r)
        msgs.append("titre du bloc retiré")
    return msgs


# ---------- commandes ----------
def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE) or t.name(r).startswith("UIPickerPastille")]


def sources():
    lst = src_tree(LISTE_SOURCE)
    liste = lst and first(lst, lambda r: lst.name(r) == LISTE and typ(lst, r) == "WrappedObjectList")
    ttr = src_tree(TITRES_SOURCE)
    ok_titres = ttr and all(first(ttr, lambda r, n=n: ttr.name(r) == n) for n, _ in LISTES)
    s = ouvrir(INFOBULLE_SOURCE, depart_original=True)   # d'origine : la vue FM Guru (v14) retire ce bouton
    s = s and s[3]
    tip = s and first(s, lambda r: typ(s, r) == "Tooltip" and len(s.children(r)) == 1
                      and typ(s, s.children(r)[0]) == "SIText")
    if not (liste and ok_titres and tip):
        return None, None
    return (lst, liste, ttr), (s, tip)

# ---------- commandes (communes aux 3 fonctions : modeles = leurs modèles) ----------
def a_jour(m, t):
    if m == BLOC:
        return any(t.name(r) == NOM for r in marques(t))
    if m == CELLULE:   # FM27 s'en sert (rapports d'équipe) : doit rester d'origine
        return not marques(t)
    if m == CELLULE_LIBRE:
        return any(t.name(r) == NOM_PASTILLE for r in marques(t))
    return any(t.name(r).endswith(f"-v{VERSION}") for r in marques(t))


def appliquer(modeles, marker):
    actuels = {m: ouvrir(m) for m in modeles}
    if None in actuels.values():
        print("infobulle Pour / Contre : modèles introuvables (renommés par une mise à jour ?), ignoré")
        return
    if all(a_jour(m, actuels[m][3]) for m in modeles):
        print("infobulle Pour / Contre : déjà appliqué")
    else:
        ancien = any(marques(v[3]) for v in actuels.values())
        travail = {m: ouvrir(m, depart_original=True) for m in modeles
                   if not (m == CELLULE and a_jour(m, actuels[m][3]))}   # CELLULE : réécrite seulement pour la remettre
        if any(marques(v[3]) for v in travail.values()):
            print("infobulle Pour / Contre : pas de sauvegarde d'origine propre, rien fait")
            return
        src_bloc, src_tip = sources()
        if src_bloc is None:
            print("infobulle Pour / Contre : morceaux de FM (liste, titres, infobulle) introuvables, rien enregistré")
            return
        msgs = []
        c = None   # pastille construite (sans l'enregistrer) depuis StrengthWeaknessCell d'origine, puis recopiée
        if CELLULE_LIBRE in travail or CELLULE_BANDEAU in travail:
            c = ouvrir(CELLULE, depart_original=True)
            m_pastille = construire_pastille(c[3], src_tip)
            msgs += m_pastille if CELLULE_LIBRE in travail else [m for m in m_pastille if "introuvable" in m]
        if CELLULE_LIBRE in travail:
            msgs += recopier_pastille(travail[CELLULE_LIBRE][3], c[3], CELLULE_LIBRE)[1]
        if CELLULE in travail:   # anciennes versions (v1-v14) : la cellule de FM est remise telle quelle
            msgs.append(f"{CELLULE} remise d'origine (rapports d'équipe : points forts / faibles)")
        if BLOC in travail:
            msgs += construire_bloc(travail[BLOC][3], src_bloc)
        if LISTE_FM in travail:
            msgs += construire_liste_fm(travail[LISTE_FM][3], marges=["margin-right-global-gap-small"])
        for m, note in LIGNES_RAPPORT.items():
            if m in travail:
                msgs += construire_liste_fm(travail[m][3], m, note)
        if CELLULE_BANDEAU in travail:   # la même, en plus grand
            msgs += construire_pastille_bandeau(travail[CELLULE_BANDEAU][3], c[3])
        msgs += ["ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"infobulle Pour / Contre : {m}")
        if any("introuvable" in m for m in msgs):
            print("infobulle Pour / Contre : rien enregistré")
            return
        for bundle, obj, tt, t in travail.values():
            t.finish()
            t.styles.save()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(marker, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def retirer(modeles, marker):
    if os.path.exists(marker) and not nb.DRY_RUN:
        os.remove(marker)
    fait = False
    for m in modeles:
        o = ouvrir(m)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = original(bundle, obj)
        if orig is None:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
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


def etat(modeles, marker):
    for m in modeles:
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        noms = sorted({o[3].name(r) for r in marques(o[3])})
        print(f"{m} : " + (f"appliqué ({', '.join(noms)} ; version actuelle v{VERSION})" if noms else "d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(marker) else "non")


def main(argv, modeles, marker, libelle):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        appliquer(modeles, marker)
    elif op == "retirer":
        retirer(modeles, marker)
    elif op == "etat":
        etat(modeles, marker)
    elif op == "si-actif":
        if os.path.exists(marker):
            appliquer(modeles, marker)
        else:
            print(f"{libelle} : non activé, rien à faire")
    else:
        sys.exit(sys.modules["__main__"].__doc__)
