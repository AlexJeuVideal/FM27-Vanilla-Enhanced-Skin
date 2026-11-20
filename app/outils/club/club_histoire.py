"""Club > Histoire du club > Vue d'ensemble (maquette A, v2) : TOUT sur un seul écran, dans une grande tuile :

  [ trophées, en bandeau sur toute la largeur (défilement horizontal)                                  ]
  [ logo, nom, nation + infos du club | meilleur onze de tous les temps | repères historiques         ]
  [ records                           |                                 | entraîneurs du club        ]

- Tuile = ClubSiteFacilitiesCard (modèle FM cité par rien) réécrit : racine = BindingExpect de la tuile Honneurs de FM
  (teamcontainer, isonmainscreen). Trophées : cartes de salle_trophees (image + nombre, CareerMilestoneYearRow) si
  salle_trophees est actif, sinon lignes FM (ClubHistoryHonours_4x4_Row) ; WrappedObjectList (TeamMeetingBlock)
  sur teamcontainer.HistoryHonours.HistoryHonoursList. En-tête / infos = morceaux de ClubProfileBlock dans un
  BindingRemapper club = teamcontainer.MainTeam.Club. Records, onze (team = teamcontainer.MainTeam), repères,
  entraîneurs = tuiles FM incluses telles quelles.
- Grille ClubHistoryCardGridComposition (ui-tileslayouts, refaite depuis l'original) : la tuile Honneurs seule, sur
  toute la grille ; ClubHistoryHonoursTileDescription + une taille (toute la grille) -> notre modèle (FM prend le
  modèle dans la DESCRIPTION, pas dans m_gridElementConfigs : la v1 n'a jamais été vue pour ça).
Après club_page_bas et salle_trophees (catalogue). Une disposition perso de FM (CustomGridCompositions) passe avant.
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first  # noqa: E402
from elements import move  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
ECART = 12                  # px entre les blocs
# v6 : bandeau du haut = photo du stade voilée en fond, club (logo, nom, nation, 3 infos) | palmarès ; dessous 3
# colonnes égales. v8 : Records | VRAI meilleur onze (terrain de la page Meilleur onze, sans le tableau) |
# Événements marquants + Entraîneurs (joueurs notables retirés : doublon du onze)
PARTS = (1.0, 1.0, 1.0)     # largeurs des 3 colonnes du bas
PART_EVENEMENTS, PART_ENTRAINEURS = 1.2, 1.0   # colonne de droite
PART_CLUB, PART_TROPHEES = 1.0, 2.2          # bandeau du haut
VOILE_BANDEAU = (0.0, 0.0, 0.0, 0.70)        # voile sombre sur la photo du stade (lisibilité)
PADDING_BANDEAU = 16
INFOS_GARDEES = ("year-founded-frame", "division-frame", "region-frame")   # lignes de ClubInfoDetailsFrame
LARGEUR_INFO = 150          # px par info (libellé au-dessus de la valeur)
# bandeau des trophées par mode d'affichage (0 Défaut « Large », 1 Détaillé, 2 Condensé) : hauteur du défilement
# (cartes de salle_trophees : leurs tailles + barre) ; lignes FM (sans salle_trophees) : hauteur de la zone
BANDEAU_CARTES = {0: 124, 1: 174, 2: 174}
BANDEAU_LIGNES = {0: 56, 1: 64, 2: 64}
TITRE_TROPHEES = L("Palmarès", "Honours")
TITRE_EVENEMENTS = L("Événements marquants", "Club landmarks")
TITRE_RECORDS = L("Records", "Records")
TITRE_ENTRAINEURS = L("Entraîneurs", "Managers")
TITRE_ONZE = L("Meilleur onze", "Best XI")
TUILES = {   # (modèle FM, GUID)
    # v4 : les vrais blocs des pages Records (menu de catégorie + tableau) et Événements marquants (filtre + liste)
    "records": ("ClubHistoryRecordsAllTimeRecordsCompactBlock", "8ff879af6d8b5674992a1f577d3feecc"),   # club
    "onze": ("ClubHistoryBestXICardBody", ""),   # v8 : corps de la page Meilleur onze (menu des saisons + terrain)
    "reperes": ("ClubHistoryLandmarksCardBlock", "30fa87d81cb493c49b00cc70817def0b"),                    # teamcontainer
    "entraineurs": ("ClubManagerHistoryTile_4x4", "36ae757685d1dda4aa3ef196af4080aa"),                   # teamcontainer
}
# =====================================================================================================

VERSION = f"8{SUFFIXE}"   # v8 : vrai meilleur onze (terrain) au milieu ; v7 : trophées centrés, division alignée ; v3 : grille étirée (maximum 100 x 100) ; v4 : club | palmarès en haut, stade + vrais
                          # Records, vrais Événements marquants ; v5 : maillots (hors Large) ; v6 : refonte (bandeau
                          # sur le stade, 3 colonnes égales, blocs recopiés sans cadre en double, même titre partout)
TYPE_TEAMCONTAINER = 1380935244
STADE_PAGE = "UIPickerClubBasStade"     # stade photo de club_page_bas (dans ClubSiteBlock)
MODELE = "ClubSiteFacilitiesCard"
GUID_MODELE = "8abb87e65f464794fb030e923a75e5f8"
HONNEURS = "ClubHistoryHonours_4x4"
PROFIL = "ClubProfileBlock"
PAGE_CLUB = "ClubSiteBlock"          # SIScrollView (défilement horizontal du bandeau)
SOURCE_LISTE = ("TeamMeetingBlock", "Players")   # WrappedObjectList de FM
GUID_LIGNE = "b9a4503ca8b908444bcf342a3ad4af44"  # ClubHistoryHonours_4x4_Row (icône + nombre + compétition)
CHEMIN_HONNEURS = "teamcontainer.HistoryHonours.HistoryHonoursList"
TYPE_CLUB, CHEMIN_CLUB = 1145176067, "teamcontainer.MainTeam.Club"
TYPE_EQUIPE, CHEMIN_EQUIPE = 1145176088, "teamcontainer.MainTeam"
COMPOSITION = "ClubHistoryCardGridComposition"
GRANDE = "ClubHistoryHonours"
DESCRIPTION = "ClubHistoryHonoursTileDescription"
CONFIGS = "<Configurations>k__BackingField"
TUILES_BUNDLE = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
PREFIXE = "UIPickerHistoire"
NOM = f"{PREFIXE}-v{VERSION}"
# 2026-11-20 : marqueur renommé (catalogue : marqueur), fonction de nouveau de base, donné par la MAJ auto à tous
MARKER = os.path.join(backup.BACKUP_DIR, "club_histoire_v8.actif")
for _k, _v in {"width": (131105, 3), "height": (131087, 3), "min-height": (131096, 3), "flex-direction": (131083, 7),
               "justify-content": (131088, 7), "align-items": (131073, 7), "margin-top": (131093, 3),
               "margin-right": (131092, 3), "margin-bottom": (131090, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "padding-top": (131101, 3), "padding-bottom": (131098, 3),
               "flex-grow": (131084, 2), "flex-shrink": (131085, 2), "overflow": (458768, 7),
               "flex-basis": (131082, 3), "min-width": (131097, 3), "max-height": (131094, 3),
               "flex-wrap": (131086, 7), "margin-left": (131091, 3), "align-self": (131074, 7),
               "position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "right": (131103, 3),
               "bottom": (131080, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
CENT = {"unit": 2, "value": 100.0}


class Source:
    def __init__(self, modele):
        bundle, _, tt = nb.find_vta(modele)
        self.t = sm.Tree(tt) if tt is not None else None
        if self.t is not None:
            self.t.styles = sm.Styles(bundle, tt)

    def nom(self, n):
        return self.t and first(self.t, lambda r: self.t.name(r) == n)


class Originale(Source):
    """modèle FM repris de l'ORIGINAL (le jeu peut porter un essai sur ce modèle)"""
    def __init__(self, modele):
        o = ouvrir(modele, depart_original=True)
        self.t = o[3] if o else None


def copier(t, s, racine, parent, index=None):
    """sous-arbre racine de la source s recopié sous parent (styles intégrés et modèles inclus compris)"""
    r = t.clone(racine, parent, index, src=s.t)
    t.styles.copy_from(s.t.styles, t, r)
    utilises = {s.t.elem(x).get("m_TemplateAlias") for x in s.t.walk(racine)} - {None, ""}
    us = t.tt.setdefault("m_Usings", [])
    for u in s.t.tt.get("m_Usings") or []:
        if u.get("alias") in utilises and not any(v.get("alias") == u["alias"] for v in us):
            us.append(dict(u))
    return r


class Tuile:
    def __init__(self, t):
        self.t, self.st = t, t.styles

    def boite(self, parent, css, nom="", classes=()):
        t = self.t
        r = t.clone_shallow(self.modele_boite, parent)
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = list(classes), -1
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1 if nom else 0
        self.st.style(self.t, r, css)
        return r

    def instance(self, parent, alias, guid):
        t = self.t
        r = t.clone_shallow(self.modele_instance, parent)
        t.elem(r)["m_TemplateAlias"] = alias
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = ["height-100-percent"], -1
        t.sd(r)["templateId"] = alias
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        self.st.style(t, r, {"flex-grow": 1})
        us = t.tt.setdefault("m_Usings", [])
        if not any(u.get("alias") == alias for u in us):
            us.append({"alias": alias, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return r

    def remapper(self, parent, de, chemin, type_id, css):
        t = self.t
        r = t.clone_shallow(self.modele_remap, parent)
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        t.sd(r)["Mappings"] = [{"m_serialisedType": 0, "from": de, "to": {"m_path": chemin}, "type": {"id": type_id}}]
        self.st.style(t, r, css)
        return r


def salle_trophees_active():
    try:
        import salle_trophees
        return os.path.exists(salle_trophees.MARKER), salle_trophees
    except Exception:
        return False, None


def construire(t):
    hon, profil, page = Originale(HONNEURS), Originale(PROFIL), Source(PAGE_CLUB)
    reunion = Source(SOURCE_LISTE[0])
    srcs = {k: Originale(m) for k, (m, _) in TUILES.items()}
    if None in (hon.t, profil.t, page.t, reunion.t) or any(s.t is None for s in srcs.values()):
        return None, "modèles FM introuvables (tuile Honneurs, profil du club, page club, réunion d'équipe, tuiles)"
    be = first(hon.t, lambda r: typ(hon.t, r) == "BindingExpect")
    inst = first(hon.t, lambda r: hon.t.elem(r).get("m_TemplateAlias") == "tile-square-4x4")
    boite = hon.nom("body-area-frame")
    remap = first(profil.t, lambda r: typ(profil.t, r) == "BindingRemapper")
    morceaux = {n: profil.nom(n) for n in ("ClubInfoHeaderFrame", "ClubInfoDetailsFrame")}
    defile_src = first(page.t, lambda r: typ(page.t, r) == "SIScrollView")
    liste_src = first(reunion.t, lambda r: reunion.t.name(r) == SOURCE_LISTE[1]
                      and typ(reunion.t, r) == "WrappedObjectList")
    rec, lm, onze, ent = (srcs[k].t for k in ("records", "reperes", "onze", "entraineurs"))
    rec_racine = first(rec, lambda r: typ(rec, r) == "ComponentElement")
    rec_titre = first(rec, lambda r: rec.name(r) == "text" and rec.name(rec.parent[r]) == "Header")
    lm_racine = first(lm, lambda r: typ(lm, r) == "ComponentElement")
    onze_racine = first(onze, lambda r: typ(onze, r) == "ComponentElement")
    ent_contenu = first(ent, lambda r: typ(ent, r) == "BindableSwitchElement")
    if None in (be, inst, boite, remap, defile_src, liste_src, rec_racine, rec_titre, lm_racine, onze_racine,
                ent_contenu, *morceaux.values()):
        return None, "morceaux FM introuvables (profil, Honneurs, défilement, liste, Records, Événements, onze, entraîneurs)"
    racine_vt = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine_vt)):
        t.remove(k)
    tu = Tuile(t)
    st = t.styles
    # racine : BindingExpect de la tuile Honneurs (mêmes paramètres que les tuiles de l'écran), vidé
    racine = t.clone(be, racine_vt, src=hon.t)
    for k in list(t.children(racine)):
        t.remove(k)
    t.elem(racine)["m_Classes"], t.elem(racine)["m_RuleIndex"] = ["height-100-percent"], -1
    tu.modele_boite = t.clone(boite, racine, src=hon.t)
    for k in list(t.children(tu.modele_boite)):
        t.remove(k)
    tu.modele_instance = t.clone(inst, racine, src=hon.t)
    tu.modele_remap = t.clone(remap, racine, src=profil.t)
    for k in list(t.children(tu.modele_remap)):
        t.remove(k)
    modeles = [tu.modele_boite, tu.modele_instance, tu.modele_remap]
    recs = srcs["records"]

    tout = tu.boite(racine, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "overflow": "hidden"}, NOM)

    def titre(parent, texte, index=None):
        """même titre partout : celui du bloc Records de FM (heading-md), texte fixe"""
        txt = t.clone(rec_titre, parent, index, src=rec)
        st.copy_from(rec.styles, t, txt)
        d = t.sd(txt)
        d["text"], d["text_UxmlAttributeFlags"], d["DebugDisplay"] = texte, 1, texte
        if isinstance(d.get("TextBinding"), dict):
            d["TextBinding"] = copy.deepcopy(d["TextBinding"])
            d["TextBinding"]["m_kind"] = 0
            d["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        d["name"], d["name_UxmlAttributeFlags"] = "", 0
        st.style(t, txt, {"flex-shrink": 0, "margin-bottom": 8})
        return txt

    def cadre(parent, css):
        return tu.boite(parent, {"flex-shrink": 1, "min-height": 0, "min-width": 0, "overflow": "hidden", **css},
                        classes=["siblock-padding", "siblock-border"])

    plein = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}

    # 1. bandeau du haut : photo du stade voilée en fond ; club | palmarès
    cartes, stro = salle_trophees_active()
    if stro is None:
        return None, "salle_trophees introuvable (comparaisons du mode d'affichage)"
    haut = tu.boite(tout, {"flex-direction": "row", "flex-shrink": 0, "flex-grow": 0, "align-items": "center",
                           "overflow": "hidden", "padding-left": PADDING_BANDEAU, "padding-right": PADDING_BANDEAU,
                           "padding-top": PADDING_BANDEAU, "padding-bottom": PADDING_BANDEAU},
                    classes=["siblock-border"])
    stade = page.nom(STADE_PAGE)
    images = [k for k in page.t.children(stade) if typ(page.t, k) == "SIImage"] if stade is not None else []
    if images:
        fond = tu.remapper(haut, "club", "teamcontainer", TYPE_TEAMCONTAINER, plein)
        for k in images:
            copier(t, page, k, fond)
        tu.boite(haut, {**plein, "background-color": VOILE_BANDEAU})
        quel_stade = "photo du stade en fond"
    else:
        quel_stade = "sans photo (club_page_bas pas actif)"
    rm = tu.remapper(haut, "club", CHEMIN_CLUB, TYPE_CLUB, {"flex-grow": PART_CLUB, "flex-shrink": 1, "flex-basis": 0,
                                                            "min-width": 0, "overflow": "hidden"})
    copier(t, profil, morceaux["ClubInfoHeaderFrame"], rm)
    d = copier(t, profil, morceaux["ClubInfoDetailsFrame"], rm)
    st.style(t, d, {"flex-direction": "row", "margin-top": 12, "align-items": "flex-start"})
    for k in list(t.children(d)):
        if t.name(k) not in INFOS_GARDEES:
            t.remove(k)
            continue
        st.style(t, k, {**sm.SANS_CADRE, "width": LARGEUR_INFO, "min-width": 0, "flex-shrink": 1,
                        "padding-left": 0, "padding-right": 0, "padding-top": 0, "padding-bottom": 0,
                        "margin-right": ECART})
        paire = k if len(t.children(k)) >= 2 else t.children(k)[0]   # #YearFounded : un niveau de plus
        st.style(t, paire, {"flex-direction": "column", "align-items": "flex-start", **sm.SANS_CADRE})
        for c in t.children(paire):
            st.style(t, c, {"margin-right": 0, "margin-bottom": 2})
        # v7 : division = le nom seul (la cellule de FM avec son icône vide était plus haute : infos décalées)
        nom_div = first(t, lambda r: t.name(r) == "DivisionNameText", k)
        case_div = first(t, lambda r: t.name(r) == "DivisionNameTextFrame", k)
        switch_div = first(t, lambda r: t.name(r) == "HasDivision", k)
        if None not in (nom_div, case_div, switch_div):
            move(t, nom_div, case_div)
            t.remove(switch_div)
            st.style(t, nom_div, {"margin-right": 0})
    tu.boite(haut, {"width": 1, "align-self": "stretch", "margin-left": PADDING_BANDEAU,
                    "margin-right": PADDING_BANDEAU, "background-color": (1.0, 1.0, 1.0, 0.15), "flex-shrink": 0})
    bande = tu.boite(haut, {"flex-grow": PART_TROPHEES, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                            "overflow": "hidden"})
    for k in (0, 1, 2):
        vk = stro.visible(t, bande, stro.MODE_AFFICHAGE, stro.OP_EGAL, k, f"{PREFIXE}Trophees-mode{k}")
        if vk is None:
            return None, "modèle de comparaison FM introuvable (mode d'affichage)"
        st.style(t, vk, {"width": CENT})
        h = (BANDEAU_CARTES if cartes else BANDEAU_LIGNES)[k]
        defile = t.clone(defile_src, vk, src=page.t)
        for c in list(t.children(defile)):
            t.remove(c)
        sd = t.sd(defile)
        sd["name"] = ""
        t.elem(defile)["m_Classes"], t.elem(defile)["m_RuleIndex"] = [], -1
        sd["mode"], sd["mode_UxmlAttributeFlags"] = stro.SCROLL_HORIZONTAL, 1
        sd["horizontalScrollerVisibility"], sd["horizontalScrollerVisibility_UxmlAttributeFlags"] = stro.BARRE_AUTO, 1
        sd["verticalScrollerVisibility"], sd["verticalScrollerVisibility_UxmlAttributeFlags"] = stro.BARRE_CACHEE, 1
        st.style(t, defile, {"width": CENT, "height": h, "flex-shrink": 0})
        w = t.clone(liste_src, defile, 0, src=reunion.t)
        sm.no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": stro.GUID_CARTE if cartes else GUID_LIGNE, "m_SubObjectName": "",
                              "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = stro.path_arg(sd["VisualFuncBinding"], CHEMIN_HONNEURS)
        sd["ItemParamName"] = "row"
        t.elem(w)["m_Classes"] = []
        st.style(t, w, {"flex-direction": "row", "flex-wrap": "nowrap", "flex-shrink": 0, "flex-grow": 1,
                        "justify-content": "center", **({} if cartes else {"align-items": "center"})})
        # v7 : centré, écart fixe de la carte (space-around donnait une part de vide aux trophées à 0, cachés mais
        # présents : écarts irréguliers) ; trop de trophées = la liste dépasse -> défilement horizontal vers la droite

    # 2. trois colonnes égales
    rang = tu.boite(tout, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "min-height": 0,
                           "margin-top": ECART})

    def colonne(part, gauche):
        return tu.boite(rang, {"flex-grow": part, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "min-height": 0,
                               **({} if gauche else {"margin-left": ECART})})

    # 2a. Records : le bloc de FM recopié ; son cadre sert de cadre, titre fixe « Records », menu de catégorie
    #     remonté dans l'en-tête (avant : bouton seul au-dessus du cadre + titre = même mot)
    g = colonne(PARTS[0], True)
    rr = tu.remapper(g, "club", "teamcontainer", TYPE_TEAMCONTAINER, {"flex-grow": 1, "min-height": 0})
    r0 = copier(t, recs, rec_racine, rr)
    st.style(t, r0, {"flex-grow": 1, "min-height": 0})
    menu = first(t, lambda r: typ(t, r) == "ComponentElement" and any(typ(t, c) == "SIDropdown"
                                                                       for c in t.children(r)), r0)
    tete = first(t, lambda r: t.name(r) == "Header", r0)
    if menu is None or tete is None:
        return None, "Records : menu ou en-tête introuvable"
    for x in t.walk(tete):
        if t.name(x) == "text" and typ(t, x) == "SIText":
            d = t.sd(x)
            d["text"], d["text_UxmlAttributeFlags"], d["DebugDisplay"] = TITRE_RECORDS, 1, TITRE_RECORDS
            if isinstance(d.get("TextBinding"), dict):
                d["TextBinding"]["m_kind"] = 0
                d["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            break
    move(t, menu, tete, 1)
    st.style(t, menu, {"margin-bottom": 0, "margin-right": ECART, "flex-shrink": 1, "min-width": 0})
    st.style(t, tete, {"align-items": "center", "margin-bottom": 8, "flex-shrink": 0})

    # 2b. v8 : VRAI meilleur onze = corps de la page Meilleur onze (teamcontainer), sans le tableau : menu des
    #     saisons + terrain ; notre titre à la place de « De tous les temps »
    mo = cadre(colonne(PARTS[1], False), {"flex-grow": 1})
    o0 = copier(t, srcs["onze"], onze_racine, mo)
    st.style(t, o0, {"flex-grow": 1, "min-height": 0, "min-width": 0})
    trouve = lambda n: first(t, lambda r: t.name(r) == n, o0)  # noqa: E731
    tableau, ligne_titre, ancien_titre = trouve("table"), trouve("Frame"), trouve("all-time-text")
    terrain = first(t, lambda r: typ(t, r) == "FMTacticsPanel", o0)
    if None in (tableau, ligne_titre, ancien_titre, terrain):
        return None, "meilleur onze : tableau, titre ou terrain introuvable"
    t.remove(tableau)
    t.remove(ancien_titre)
    tt_onze = titre(ligne_titre, TITRE_ONZE, 0)
    st.style(t, tt_onze, {"margin-bottom": 0})
    for n in ("main-content-frame", "main-frame"):
        x = trouve(n)
        if x is not None:
            st.style(t, x, {**sm.SANS_CADRE, "flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0})
    st.style(t, t.parent[terrain], {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0,
                                    "align-self": "stretch"})
    st.style(t, terrain, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0})

    # 2c. Événements marquants (notre cadre + titre, le bloc FM sans son cadre intérieur) + entraîneurs (contenu de
    #     la tuile FM sans la tuile)
    dr = colonne(PARTS[2], False)
    ev = cadre(dr, {"flex-grow": PART_EVENEMENTS, "flex-basis": 0})
    titre(ev, TITRE_EVENEMENTS)
    e0 = copier(t, srcs["reperes"], lm_racine, ev)
    st.style(t, e0, {"flex-grow": 1, "min-height": 0})
    for x in t.walk(e0):
        if "border-color-layout-modules-block-border-colour" in (t.elem(x).get("m_Classes") or []):
            st.style(t, x, {**sm.SANS_CADRE, "padding-left": 0, "padding-right": 0, "padding-top": 0,
                            "padding-bottom": 0})
    ce = cadre(dr, {"flex-grow": PART_ENTRAINEURS, "flex-basis": 0, "margin-top": ECART})
    titre(ce, TITRE_ENTRAINEURS)
    c0 = copier(t, srcs["entraineurs"], ent_contenu, ce)
    st.style(t, c0, {"flex-grow": 1, "min-height": 0})

    for x in modeles:
        t.remove(x)
    return (f"{MODELE} : bandeau club | palmarès ({'cartes de salle_trophees' if cartes else 'lignes FM'}, "
            f"{quel_stade}) ; Records | meilleur onze (terrain) | Événements + entraîneurs"), None


# ---------- grille + description de la tuile Honneurs ----------
def _objets(env):
    out = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in (COMPOSITION, DESCRIPTION):
            tt = o.read_typetree()
            if ("m_gridComponents" in tt) if n == COMPOSITION else (CONFIGS in tt):
                out[n] = (o, tt)
    return out


def voulu(orig):
    """{nom: typetree voulu} depuis les originaux, ou None"""
    comp, desc = orig[COMPOSITION], orig[DESCRIPTION]
    comps = {c["m_elementID"]: c for c in comp["m_gridComponents"]}
    if GRANDE not in comps or not desc[CONFIGS]:
        return None
    w = max(c["m_location"]["x"] + c["m_location"]["width"] for c in comp["m_gridComponents"])
    h = max(c["m_location"]["y"] + c["m_location"]["height"] for c in comp["m_gridComponents"])
    cfg = copy.deepcopy(desc[CONFIGS][0])
    cfg["Size"] = {"x": w, "y": h}
    cfg["AssetRef"]["m_AssetGUID"] = GUID_MODELE
    d = copy.deepcopy(desc)
    d[CONFIGS].append(cfg)
    c = copy.deepcopy(comps[GRANDE])
    c["m_location"].update(x=0, y=0, width=w, height=h)
    c["m_minSize"] = {"x": w, "y": h}
    c["m_maxSize"] = {"x": 100, "y": 100}   # v3 : s'étire sur tout l'écran (v2 : w x h = case minuscule au centre)
    g = copy.deepcopy(c["m_gridElementConfigs"][0])
    g["Size"] = {"x": w, "y": h}
    g["AssetRef"]["m_AssetGUID"] = GUID_MODELE
    c["m_gridElementConfigs"] = [g]
    k = copy.deepcopy(comp)
    k["m_gridComponents"] = [c]
    return {COMPOSITION: k, DESCRIPTION: d}


def grille(retirer):
    env = UnityPy.load(TUILES_BUNDLE)
    actuels = _objets(env)
    src = backup.backup_path(TUILES_BUNDLE)
    orig = {n: tt for n, (o, tt) in _objets(UnityPy.load(src if os.path.exists(src) else TUILES_BUNDLE)).items()}
    if set(actuels) != {COMPOSITION, DESCRIPTION} or set(orig) != {COMPOSITION, DESCRIPTION}:
        return [f"{COMPOSITION} / {DESCRIPTION} introuvables (renommés par une mise à jour ?), ignorés"]
    cible = orig if retirer else voulu(orig)
    if cible is None:
        return [f"{COMPOSITION} : tuiles FM inattendues, ignorée"]
    champs = {COMPOSITION: ("m_gridComponents",), DESCRIPTION: (CONFIGS,)}
    change = False
    for n, (o, tt) in actuels.items():
        if all(tt[c] == cible[n][c] for c in champs[n]):
            continue
        for c in champs[n]:
            tt[c] = copy.deepcopy(cible[n][c])
        o.save_typetree(tt)
        change = True
    if not change:
        return [f"{COMPOSITION} : " + ("déjà d'origine" if retirer else "déjà appliquée")]
    msgs = [f"{COMPOSITION} : " + ("d'origine" if retirer else "la tuile Honneurs seule, sur toute la grille "
                                                            "(description : + une taille -> notre modèle)")]
    data = env.file.save(packer="original")
    if nb.DRY_RUN:
        msgs.append(f"(essai à blanc : rien écrit, {os.path.basename(TUILES_BUNDLE)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(TUILES_BUNDLE, data)
    return msgs


# ---------- commandes ----------
def marque(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def cmd_appliquer():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} introuvable (renommé par une mise à jour ?), rien fait")
        return
    if any(o[3].name(r) == NOM for r in marque(o[3])):
        print(f"{MODELE} : déjà appliqué")
    else:
        bundle, obj, tt, t = ouvrir(MODELE, depart_original=True)
        if marque(t):
            print(f"{MODELE} : pas de sauvegarde d'origine propre, rien fait")
            return
        msg, err = construire(t)
        if err:
            print(f"{MODELE} : {err}, rien enregistré")
            return
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        nb.save_all()
        print(msg)
    for m in grille(False):
        print(m)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    for m in grille(True):   # la grille d'abord : plus rien ne pointe vers le modèle
        print(m)
    o = ouvrir(MODELE)
    if o is None or not marque(o[3]):
        return
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{MODELE} : pas de sauvegarde d'origine")
        return
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{MODELE} : remis d'origine")


def cmd_etat():
    o = ouvrir(MODELE)
    m = o and marque(o[3])
    print(f"{MODELE} :", ("à jour" if any(o[3].name(r) == NOM for r in m) else "ANCIENNE version") if m else "d'origine")
    obj = _objets(UnityPy.load(TUILES_BUNDLE))
    if COMPOSITION in obj:
        print(f"{COMPOSITION} :", ", ".join(f"{c['m_elementID']} {c['m_location']['width']}x{c['m_location']['height']}"
                                             for c in obj[COMPOSITION][1]["m_gridComponents"]))
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
            print("histoire du club : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    sys.modules.setdefault("club_histoire", sys.modules[__name__])
    main(sys.argv[1:])
