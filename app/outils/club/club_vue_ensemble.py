"""Club > Vue d'ensemble refaite (maquette B, essai_club_vue_ensemble v9 validé en jeu le 2026-11-09) : une seule
grande tuile. À gauche (fenêtre large seulement) une colonne « carte d'identité » du club :

  [stade (photo de la page club)]
  [logo, nom, nation]
  [fondé, surnom, région, division, statut]
  Onze de légende (meilleur 11 de l'histoire du club, terrain de FM)
  [maillots]

- Modèle touché : ClubScreenOverviewBlock (cité par aucun autre script) ; appliquer repart de l'original, retirer le
  remet. Colonne = SIVisible app.GridBreakpointIsLarge (copie du SIVisible des Finances) > SIScrollView sans barre.
- Morceaux recopiés comme club_histoire : ClubProfileBlock (en-tête, infos, maillots), stade = celui de la page club
  fait par club_page_bas (photo ; sinon le bloc Stade du profil), ClubHistoryBestXICardBody (terrain) dans un
  BindingRemapper teamcontainer = club (sans la liste des saisons ni le tableau).
- v2 : grilles ClubComposition-Large / -Standard / -Small (ui-tileslayouts, refaites depuis l'original) = barre
  d'actions + grande tuile sur toute la hauteur (tuiles du bas retirées) ; stade 140 px, places + année seulement.
- v3 : tuiles en plus des grands écrans (m_optionalSlices) retirées aussi ; à droite, Vision | Finances | Staff en
  haut (blocs FM déplacés, Vision et Finances côte à côte dans #Large), puis 2 rangées de tuiles FM incluses (TUILES).
- v4 : tuile Installations à droite des infos du club (colonne de gauche) ; stade 250 px.
- v5 : Staff un peu moins large (PART_VISION_FINANCES), Finances plus larges (PART_FINANCES) pour que la courbe ne soit plus coupée.
- v6 : onze de légende couché (FMTacticsPanel Orientation 1, ONZE_INVERSE), terrain qui remplit sa boîte.
- v7 : gardien à gauche (FlipPositions 1 ; à 0, FM le met à droite).
- v8 : noms des joueurs cliquables (fiche) : BestXIPosition (carte des onzes types, aussi onzes de saison et
  présentation du club) réécrit depuis l'original, bouton de nom FM à la place du nom (noms_cliquables).
- v9 : tuiles rangées dans l'ordre du menu Club (TUILES).
- v11 (captures Fulham en Large / Medium, « tout est décalé ») : colonne à la hauteur de la tuile (align-self stretch)
  et défilement en absolu dedans (elle sortait de la tuile, la page défilait dans le vide, maillots coupés) ; barre
  de défilement si ça dépasse (BARRE_COLONNE) ; tuile Installations sous les infos quand les deux ne rentrent pas.
- v12 (captures Aachen v11 : Installations posée sur le onze, colonne qui défile) : colonne fixe sans défilement
  (stade / onze rétrécissent, STADE_MINI / ONZE_MINI), Installations toujours sous les infos, maillots retirés (MAILLOTS).
- v13 (v12 vue : Medium / Small OK ; Large : logo sur le stade, commentaires de Vision tassés) : stade par mode
  d'affichage (Large : STADE_LARGE, 0 = caché ; hauteur fixe), défilement des onglets de Vision étiré ; carte v4 :
  cartes des onzes types remontées de CARTE_DECALAGE (noms qui dépassaient sous le terrain).
- v14 (v13 vue : stade sur les infos en Large / Medium, trou sous le stade en Small) : bloc du stade ni étiré ni
  tassé ; colonne par mode d'affichage : Small = infos | Installations + maillots, Medium = infos puis Installations,
  Large = stade STADE_LARGE + Installations (sans infos).
- v15 (v14 vue : onze trop serré, Vision dans un petit rectangle) : Medium = infos | Installations comme Small ;
  Large : Installations 140 px ; titre « Onze de légende » en Small seulement ; terrain qui prend toute la place
  restante ; onglets de Vision superposés en absolu (empilés, chacun n'avait qu'un tiers de la hauteur).
- v16 (v15 vue : Vision toujours en petit rectangle en Large, onze trop haut en Medium, Installations étroite) :
  Vision sans .height-50-percent (moitié de la rangée), infos LARGEUR_INFOS 240 rognées, terrain ONZE_MAXI ; carte v5 :
  maillot CARTE_MAILLOT, textes CARTE_TEXTE (touche aussi onzes de saison / présentation).
- Fonction du skin v1 (2026-11-09) = essai v9 : texte « Onze de légende » traduit (langue.py), marqueur, si-actif ;
  après club_page_bas (SUIVANTS : son stade photo est recopié d'ici).
Usage (jeu fermé) : appliquer [--dry-run] | retirer [--dry-run] | etat | si-actif
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import UnityPy  # noqa: E402
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first  # noqa: E402
import notes_installations as ni  # noqa: E402  (v14 : SIVisible par mode d'affichage)
import club_histoire as ch  # noqa: E402,F401  (réglages de styles)
import club_page_bas as cpb  # noqa: E402  (ordre des cases du stade)
from club_histoire import Source, copier  # noqa: E402
import arbre as sm  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
LARGEUR = 24            # % de la tuile pour la colonne de gauche
HAUTEUR_STADE = 250     # px, photo du stade (v2 : 200 -> 140 ; v4 : 250, place libre en bas de la colonne)
STADE_GARDEES = ("capacity", "year-built")   # v2 : cases du stade gardées (club_page_bas.STADE_CASES)
HAUTEUR_ONZE = 300      # px, terrain du onze de légende (v6 : 330 -> 300, couché)
ONZE_ORIENTATION = 1    # v6 : FMTacticsPanel.Orientation 1 = couché (0 = debout, FM)
ONZE_INVERSE = 1        # FlipPositions : 0 = gardien à droite (vu en jeu v6), 1 = gardien à gauche
ECART = 12              # px entre les blocs
HAUTEUR_INSTALLATIONS = 140   # v15 : px de la tuile Installations en Large (seule, sans infos ; v12 : 170)
OP_SUPERIEUR = 4        # ComparisonOperator de FM « > » (mode > Large = Medium / Small)
STADE_LARGE = 200       # v14 : px du stade en mode d'affichage Large (0 = caché) ; infos du club cachées en Large
LARGEUR_INFOS = 240     # v16 : px des infos du club (Small / Medium, Installations à droite) ; lignes FM de 280 px
                        # rognées à droite (valeurs courtes) pour élargir Installations (v14 : 280)
ONZE_MAXI = 330         # v16 : px maxi du terrain (Medium : il prenait toute la hauteur, trop haut)
CARTE_MAILLOT = 18      # v16 : px du maillot des cartes des onzes types (FM : ~24) ; 0 = taille de FM
CARTE_TEXTE = 10        # v16 : px des textes des cartes (poste, nom) ; 0 = taille de FM
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"
MODE_LARGE, MODE_MEDIUM, MODE_SMALL = 0, 1, 2
ONZE_MINI = 140         # v12 : colonne fixe (sans défilement) : le terrain du onze rétrécit jusque-là
CARTE_DECALAGE = 14     # v13 : px dont les cartes des onzes types remontent (centrées sur le terrain, pas le maillot)
TITRE_ONZE = L("Onze de légende", "Legends XI")
PART_HAUT = 1.4         # hauteur de Vision | Finances | Staff par rapport à une rangée de tuiles
PART_VISION_FINANCES = 1.3   # v5 : largeur de Vision + Finances pour 1 de Staff (avant 1 / 1 : Staff trop large)
PART_FINANCES = 1.3          # v5 : Finances pour 2 de Vision (avant 1 : courbe coupée)
TUILES = [   # rangées de tuiles FM (modèle 4x2 ou 2x2, GUID, attend teamcontainer = club)
    # v9 : dans l'ordre du menu Club (Profil du club : Profil, Infos club, Infos diverses, Infrastructures,
    # Affiliations ; puis Vision du club, Supporters, Finances, Histoire du club)
    [("ClubSiteTile_4x2", "2fda54fe74e37e44a8725d72542b8463", False),
     ("ClubInfoTile_4x2", "c6449580b48f3b54fb524599cd259663", False),
     ("RivalsTile_2x2", "1cb804f0e8e3f754c9e67946498eb601", False),
     ("YouthSetupTile_4x2", "b819857d2e7c2a74f83614e3cdbb19dc", False),
     ("ClubAffiliatesTile_4x2", "c1f71d05a885c76408a6cc5d3d71952d", False)],
    [("SquadDynamicsTile_4x2", "d8dd200c9b102754ca4dfd0974b8f900", False),
     ("ClubSupportersTile_4x2", "459461706df47e84595838425003cfd5", False),
     ("TransferHistory_4x2", "9b7ea9f15a87f7f45b6df638649d0973", False),
     ("ClubHistoryTile_4x2", "4f1200c065ff2e245bc928dc103838a0", True)],
]
# v4 : installations dans la colonne de gauche, à droite des infos du club (sous le stade)
TUILE_INFOS = ("ClubFacilitiesTile_4x2", "8c0654e9bc7f16e42bbb17646c9ef385")
# =====================================================================================================

VERSION = f"16{SUFFIXE}"   # suite des versions de l'essai (v9 validée) : l'essai posé chez le joueur est refait
VERSION_CARTE = "5"      # noms cliquables sur les cartes des onzes types (essai : v1) ; v3 : + équipe de la fiche
                         # (reportcontextteam -> équipe du joueur : fiche « pas chez toi » depuis la page club)
MARKER = os.path.join(backup.BACKUP_DIR, "club_vue_ensemble.actif")
CARTE = "BestXIPosition"
NOM_SOURCE = "PlayerNameWNationalityCell"
TYPE_PERSONNE = 1145176065
TYPE_EQUIPE = 1145176088
NOM_CARTE = f"UIPickerVueClubNom-v{VERSION_CARTE}"
COMPOSITIONS = ("ClubComposition-Large", "ClubComposition-Standard", "ClubComposition-Small")
GRANDE, BARRE = "ClubScreenOverviewBlock", "HumanActionsControlPanelBlock"
TUILES_BUNDLE = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
MODELE = "ClubScreenOverviewBlock"
PREFIXE = "UIPickerVueClub"
NOM = f"{PREFIXE}-v{VERSION}"
PROFIL, PAGE_CLUB, ONZE = "ClubProfileBlock", "ClubSiteBlock", "ClubHistoryBestXICardBody"
STADE_PAGE = "UIPickerClubBasStade"     # stade photo de club_page_bas
TYPE_TEAMCONTAINER = 1380935244
GRANDE_FENETRE = "app.GridBreakpointIsLarge"
for _k, _v in {"display": (131081, 1), "max-width": (131095, 3), "min-width": (131097, 3),
               "margin-left": (131091, 3), "flex-basis": (131082, 3), "align-self": (131074, 7),
               "flex-wrap": (131086, 7), "position": (131102, 7), "left": (131089, 3), "top": (131104, 3),
               "right": (131103, 3), "bottom": (131080, 3), "margin-right": (131092, 3),
               "margin-top": (131093, 3), "font-size": (65537, 3), "max-height": (131094, 3),
               "height": (131087, 3), "width": (131105, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
AUCUN = 6   # mot-clé None (display: none)


def cases_retirees(t, stade):
    """cases du bas du stade (club_page_bas : 4 cases séparées par des traits) dont une liaison cite STADE_CACHES :
    retirées avec le trait d'avant ; nombre de cases retirées"""
    n = 0
    cadres = [v for v in t.walk(stade) if t.name(v) == STADE_PAGE]   # 2 copies (modes d'affichage)
    for cadre in cadres:
        # rangée du bas = enfant du cadre avec des traits ; cases dans l'ordre de cpb.STADE_CASES
        rang = next((r for r in t.children(cadre) if any(t.elem(k).get("m_TemplateAlias") for k in t.children(r))),
                    None)
        if rang is None:
            continue
        cases = [k for k in t.children(rang) if not t.elem(k).get("m_TemplateAlias")]
        if len(cases) != len(cpb.STADE_CASES):
            continue
        for nom, c in zip(cpb.STADE_CASES, cases):
            if nom in STADE_GARDEES:
                continue
            i = t.children(rang).index(c)
            t.remove(c)
            voisin = t.children(rang)[i - 1] if i else (t.children(rang) or [None])[0]
            if voisin is not None and t.elem(voisin).get("m_TemplateAlias"):
                t.remove(voisin)
            n += 1
    return n


def construire(t):
    profil, page, onze = Source(PROFIL), Source(PAGE_CLUB), Source(ONZE)
    if None in (profil.t, onze.t):
        return None, "modèles FM introuvables (profil du club, meilleur 11)"
    st = t.styles
    aiguillage = first(t, lambda r: typ(t, r) == "BindableSwitchElement" and t.binding(r, "Binding") == GRANDE_FENETRE)
    vis_fm = first(t, lambda r: typ(t, r) == "SIVisible" and t.binding(r, "Binding") == "club.CanViewFinancesReport")
    trait_fm = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical")
    remap = first(profil.t, lambda r: typ(profil.t, r) == "BindingRemapper")
    morceaux = {n: profil.nom(n) for n in ("ClubInfoHeaderFrame", "ClubInfoDetailsFrame", "KitsTitleText",
                                            "MainStadiumVisible")}
    kits = first(profil.t, lambda r: profil.t.name(r) == "KitsFrame" and profil.t.name(profil.t.parent[r]) == "RHS")
    racine_onze = onze.t.children(onze.t.tt["m_VisualTree"]["rid"])
    if None in (aiguillage, vis_fm, trait_fm, remap, kits, *morceaux.values()) or not racine_onze:
        return None, "morceaux FM introuvables (tuile, profil du club ou meilleur 11)"
    rang = t.parent[aiguillage]

    # colonne : SIVisible « grande fenêtre » > défilement vertical sans barre
    col = t.clone_shallow(vis_fm, rang, 0)
    t.elem(col)["m_Classes"], t.elem(col)["m_RuleIndex"] = [], -1
    sd = t.sd(col)
    sd["name"], sd["name_UxmlAttributeFlags"] = NOM, 1
    sd["Binding"] = copy.deepcopy(sd["Binding"])
    sd["Binding"]["m_direct"]["Path"]["m_path"] = GRANDE_FENETRE
    sd["StyleClassToApplyOnVisible"] = ""
    pc = {"unit": 2, "value": float(LARGEUR)}
    # v11 : hauteur = celle de la rangée (la rangée de FM est en align-items-start : la colonne prenait la hauteur de
    # son contenu et sortait de la tuile en Large / Medium, la page défilait dans le vide)
    st.style(t, col, {"width": pc, "min-width": pc, "max-width": pc, "flex-shrink": 0, "flex-grow": 0,
                      "align-self": "stretch"})
    boite_fm = first(t, lambda r: typ(t, r) == "VisualElement" and not t.children(r) and not t.name(r))

    def boite(parent, css):
        if boite_fm is not None:
            r = t.clone_shallow(boite_fm, parent)
        else:
            r = t.clone_shallow(vis_fm, parent)   # jamais : la tuile a des VisualElement vides
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        st.style(t, r, css)
        return r

    def inst_tuile(parent, modele, guid):
        """tuile FM incluse telle quelle (copie d'une instance de modèle, autre alias + using)"""
        inst = t.clone_shallow(trait_fm, parent)
        t.elem(inst)["m_TemplateAlias"] = modele
        t.elem(inst)["m_Classes"], t.elem(inst)["m_RuleIndex"] = ["height-100-percent"], -1
        t.sd(inst)["templateId"] = modele
        t.sd(inst)["name"], t.sd(inst)["name_UxmlAttributeFlags"] = "", 0
        st.style(t, inst, {"flex-grow": 1})
        us = t.tt.setdefault("m_Usings", [])
        if not any(u.get("alias") == modele for u in us):
            us.append({"alias": modele, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return inst

    # v12 : colonne fixe (plus de défilement) : boîte en absolu à la taille de la colonne (son contenu ne compte pas
    # dans la hauteur de la tuile), rien ne dépasse ; stade et onze rétrécissent s'il manque de la place
    fixe = boite(col, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0, "overflow": "hidden"})
    # trait vertical de séparation DANS la colonne (caché avec elle en petite fenêtre)
    contenu = boite(fixe, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "min-height": 0})
    pile = boite(contenu, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "min-height": 0,
                           "overflow": "hidden", "padding-right": ECART})

    tv = t.clone(trait_fm, contenu)
    t.sd(tv)["name"], t.sd(tv)["name_UxmlAttributeFlags"] = "", 0

    # 1. stade : photo de la page club (club_page_bas), sinon bloc Stade du profil
    stade = page.t and page.nom(STADE_PAGE)
    while stade is not None and typ(page.t, stade) != "ComponentElement":
        stade = page.t.parent.get(stade)
    if stade is not None:
        s = copier(t, page, stade, pile)
        # v14 : ni étiré (trou sous la photo en Small) ni tassé (photo sur le logo en Large)
        st.style(t, s, {"flex-grow": 0, "flex-shrink": 0})
        modes_large = []
        for v in t.walk(s):
            if t.name(v) == STADE_PAGE:
                # v13 : par mode d'affichage (copies de club_page_bas : …Mode2 = Large, …Mode4 = Medium / Small),
                # hauteur fixe (v12 : le stade qui rétrécissait passait sous le logo en Large)
                h = HAUTEUR_STADE
                if t.name(t.parent[v]) == f"{STADE_PAGE}Mode{cpb.OP_EGAL}":
                    h = STADE_LARGE
                    modes_large.append(h)
                    if not h:   # sur le cadre : le SIVisible remet lui-même son display (v13)
                        st.style(t, v, {"display": AUCUN})
                        continue
                st.style(t, v, {"height": h, "min-height": h, "flex-shrink": 0})
        n_cases = cases_retirees(t, s)
        quel = (f"photo de la page club, {n_cases} cases retirées ; mode Large : "
                f"{(str(modes_large[0]) + ' px') if modes_large and modes_large[0] else 'caché' if modes_large else 'pas trouvé'}")
    else:
        copier(t, profil, morceaux["MainStadiumVisible"], pile)
        quel = "bloc Stade du profil (club_page_bas pas actif)"

    # 2. logo / nom / nation, puis par mode d'affichage (v14) :
    #    Small = infos | installations côte à côte (v10, validé) ; Medium = infos puis installations dessous (v12,
    #    validé) ; Large = installations seules (pas la place pour les infos)
    s_vis, vis_m = ni.visible_model()
    if vis_m is None:
        return None, "modèle de visibilité de FM introuvable (mode d'affichage)"

    def par_mode(mode, op=cpb.OP_EGAL):
        v = ni.new_visible(t, s_vis, vis_m, pile, None, "",
                           ni.make_binding(s_vis.sd(vis_m)["Binding"], op, [MODE_AFFICHAGE], mode), [])
        t.elem(v)["m_RuleIndex"] = -1
        st.style(t, v, {"flex-shrink": 0, "flex-grow": 0})
        return v

    def infos(parent, css):
        b = boite(parent, {"flex-shrink": 0, "overflow": "hidden", **css})   # v16 : lignes FM 280 px rognées
        copier(t, profil, morceaux["ClubInfoDetailsFrame"], b)

    copier(t, profil, morceaux["ClubInfoHeaderFrame"], boite(pile, {"flex-shrink": 0, "margin-top": ECART}))
    # v15 : Small ET Medium = infos | installations (à la hauteur des infos) ; Large = installations seules, plus basses
    rangee = boite(par_mode(MODE_LARGE, OP_SUPERIEUR), {"flex-direction": "row", "flex-shrink": 0,
                                                        "align-items": "stretch", "margin-top": ECART})
    infos(rangee, {"width": LARGEUR_INFOS, "min-width": LARGEUR_INFOS})
    inst_tuile(boite(rangee, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                              "margin-left": ECART}), *TUILE_INFOS)
    inst_tuile(boite(par_mode(MODE_LARGE), {"height": HAUTEUR_INSTALLATIONS, "min-height": HAUTEUR_INSTALLATIONS,
                                            "flex-shrink": 0, "margin-top": ECART}), *TUILE_INFOS)

    # 3. onze de légende : titre (Small seulement, v15) + terrain (BindingRemapper teamcontainer = club)
    txt = t.clone(morceaux["KitsTitleText"], boite(par_mode(MODE_SMALL), {"margin-top": ECART, "flex-shrink": 0}),
                  src=profil.t)
    st.copy_from(profil.t.styles, t, txt)
    d = t.sd(txt)
    d["text"], d["text_UxmlAttributeFlags"], d["DebugDisplay"] = TITRE_ONZE, 1, TITRE_ONZE
    d["TextBinding"] = copy.deepcopy(d["TextBinding"])
    d["TextBinding"]["m_kind"] = 0
    d["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    d["name"], d["name_UxmlAttributeFlags"] = "", 0
    rm = t.clone(remap, pile, src=profil.t)
    for k in list(t.children(rm)):
        t.remove(k)
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = [], -1
    t.sd(rm)["name"], t.sd(rm)["name_UxmlAttributeFlags"] = f"{PREFIXE}Onze", 1
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": "teamcontainer", "to": {"m_path": "club"},
                             "type": {"id": TYPE_TEAMCONTAINER}}]
    # v15 : le terrain prend toute la place qui reste (grow), rétrécit jusqu'à ONZE_MINI
    st.style(t, rm, {"height": HAUTEUR_ONZE, "min-height": ONZE_MINI, "max-height": ONZE_MAXI, "flex-grow": 1,
                     "flex-shrink": 1, "margin-top": ECART})
    corps = copier(t, onze, racine_onze[0], rm)
    st.style(t, corps, {"flex-grow": 1})
    retires = []
    for n in ("top-frame", "table"):   # liste des saisons, tableau des joueurs : seulement le terrain
        x = first(t, lambda r, n=n: t.name(r) == n, corps)
        if x is not None:
            st.style(t, x, {"display": AUCUN})
            retires.append(n)
    # v6 : terrain couché (gardien à gauche) qui remplit sa boîte
    panneau = first(t, lambda r: typ(t, r) == "FMTacticsPanel", corps)
    if panneau is None:
        return None, "onze de légende : terrain (FMTacticsPanel) introuvable"
    sdp = t.sd(panneau)
    for champ, val in (("Orientation", ONZE_ORIENTATION), ("FlipPositions", ONZE_INVERSE),
                       ("FillAllAvailableSpace", 1)):
        sdp[champ], sdp[champ + "_UxmlAttributeFlags"] = val, 1
    x = panneau
    while x != corps:   # le terrain et ses parents prennent toute la place (le tableau caché la laissait vide)
        st.style(t, x, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0,
                        "width": {"unit": 2, "value": 100.0}})
        x = t.parent[x]

    # 4. maillots (v14 : en Small seulement, la place manque en Medium / Large)
    b = boite(par_mode(MODE_SMALL), {"margin-top": ECART, "flex-shrink": 0, "margin-bottom": ECART})
    copier(t, profil, kits, b)

    # 5. droite (v3) : en haut Vision | Finances | Staff (blocs FM déplacés), puis les tuiles FM en rangées
    grande = first(t, lambda r: t.name(r) == "Large", aiguillage)
    vision = grande and next((k for k in t.children(grande) if typ(t, k) == "VisualElement"), None)
    finances = grande and next((k for k in t.children(grande) if typ(t, k) == "SIVisible"), None)
    if None in (grande, vision, finances):
        return None, "Vision / Finances (#Large) introuvables"
    droite = boite(rang, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    t.sd(droite)["name"], t.sd(droite)["name_UxmlAttributeFlags"] = f"{PREFIXE}Droite", 1
    haut = boite(droite, {"flex-direction": "row", "flex-grow": PART_HAUT, "flex-shrink": 1, "flex-basis": 0,
                          "min-height": 0})
    for k in [k for k in t.children(rang) if k not in (col, droite)]:
        cpb.move(t, k, haut)          # aiguillage Vision / Finances, trait, Staff
    st.style(t, aiguillage, {"flex-grow": PART_VISION_FINANCES, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    for k in t.children(haut):    # v5 : Staff (ni l'aiguillage ni le trait) = 1 part
        if k != aiguillage and not t.elem(k).get("m_TemplateAlias"):
            st.style(t, k, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    # grande fenêtre : Vision et Finances côte à côte (dans l'enfant #Large : l'aiguillage choisit par position)
    st.style(t, grande, {"flex-direction": "row"})
    st.style(t, vision, {"flex-grow": 2, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    # v15 : les 3 onglets de Vision (#TabsContent) restent tous dans la mise en page : empilés, chacun n'avait qu'un
    # tiers de la hauteur (petit rectangle, texte tassé). Superposés en absolu dans #TabsContent qui prend toute la
    # hauteur libre ; le défilement de chaque onglet la remplit.
    st.style(t, grande, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
    # v16 : Vision a la classe FM .height-50-percent (et son ComponentElement aussi) : en rangée = la moitié de la
    # hauteur (petit rectangle en Large) -> 100 %
    cent = {"unit": 2, "value": 100.0}
    st.style(t, vision, {"height": cent})
    for k in t.children(vision):
        if "height-50-percent" in (t.elem(k).get("m_Classes") or []):
            t.elem(k)["m_Classes"] = [c for c in t.elem(k)["m_Classes"] if c != "height-50-percent"]
    t.elem(vision)["m_Classes"] = [c for c in (t.elem(vision).get("m_Classes") or []) if c != "height-50-percent"]
    onglets = first(t, lambda r: t.name(r) == "TabsContent", vision)
    if onglets is None:
        return None, "Vision : onglets (#TabsContent) introuvables"
    x = onglets
    while x != vision:
        st.style(t, x, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        x = t.parent[x]
    for o in t.children(onglets):
        st.style(t, o, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0})
        for sv in [r for r in t.walk(o) if typ(t, r) == "SIScrollView"]:
            x = sv
            while x != o:
                st.style(t, x, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
                x = t.parent[x]
    st.style(t, finances, {"flex-grow": PART_FINANCES, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                           "margin-left": ECART})
    trait_h = next((k for k in t.children(finances) if t.elem(k).get("m_TemplateAlias")), None)
    if trait_h is not None:   # trait horizontal au-dessus des Finances : inutile côte à côte
        st.style(t, trait_h, {"display": AUCUN})
    noms = []
    for ligne in TUILES:
        r_ = boite(droite, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                            "min-height": 0, "margin-top": ECART})
        for i, (modele, guid, remap_tc) in enumerate(ligne):
            case = boite(r_, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                              **({"margin-left": ECART} if i else {})})
            if remap_tc:   # tuile qui attend teamcontainer : = club
                rmt = t.clone(remap, case, src=profil.t)
                for k in list(t.children(rmt)):
                    t.remove(k)
                t.elem(rmt)["m_Classes"], t.elem(rmt)["m_RuleIndex"] = [], -1
                t.sd(rmt)["name"], t.sd(rmt)["name_UxmlAttributeFlags"] = "", 0
                t.sd(rmt)["Mappings"] = copy.deepcopy(t.sd(rm)["Mappings"])
                st.style(t, rmt, {"flex-grow": 1})
                case = rmt
            inst_tuile(case, modele, guid)
            noms.append(modele.split("Tile")[0] or modele)
    return (f"{MODELE} : colonne de gauche {LARGEUR} % (stade {HAUTEUR_STADE} px : {quel} ; en-tête, infos | "
            f"installations, onze de légende{' sans ' + ', '.join(retires) if retires else ''}, maillots) ; droite : Vision | Finances | Staff, "
            f"tuiles {', '.join(noms)}"), None


# ---------- grilles ClubComposition-Large / -Standard / -Small (ui-tileslayouts) ----------
def _compositions(env):
    out = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in COMPOSITIONS:
            tt = o.read_typetree()
            if "m_gridComponents" in tt:
                out[n] = (o, tt)
    return out


def voulu(orig):
    """barre d'actions + grande tuile seules, la tuile sur toute la hauteur (tuiles du bas retirées)"""
    comps = {c["m_elementID"]: c for c in orig["m_gridComponents"]}
    if GRANDE not in comps or BARRE not in comps:
        return None
    bas = max(c["m_location"]["y"] + c["m_location"]["height"] for c in orig["m_gridComponents"])
    g = copy.deepcopy(comps[GRANDE])
    h = bas - g["m_location"]["y"]
    g["m_location"]["height"] = h
    g["m_minSize"]["y"] = h
    for c in g["m_gridElementConfigs"]:
        c["Size"]["y"] = h
    return [copy.deepcopy(comps[BARRE]), g]


def grilles(retirer):
    env = UnityPy.load(TUILES_BUNDLE)
    actuelles = _compositions(env)
    src = backup.backup_path(TUILES_BUNDLE)
    origines = _compositions(UnityPy.load(src if os.path.exists(src) else TUILES_BUNDLE))
    msgs, change = [], False
    for n in COMPOSITIONS:
        if n not in actuelles or n not in origines:
            msgs.append(f"{n} introuvable (renommée par une mise à jour ?), ignorée")
            continue
        o, tt = actuelles[n]
        comps = origines[n][1]["m_gridComponents"] if retirer else voulu(origines[n][1])
        if comps is None:
            msgs.append(f"{n} : tuiles FM inattendues, ignorée")
            continue
        # v3 : tuiles « en plus » des grands écrans (m_optionalSlices : Historique club, Affiliations) retirées aussi
        tranches = copy.deepcopy(origines[n][1]["m_optionalSlices"])
        if not retirer:
            for k, v in tranches.items():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    tranches[k] = []
        if tt["m_gridComponents"] == comps and tt["m_optionalSlices"] == tranches:
            continue
        tt["m_gridComponents"] = copy.deepcopy(comps)
        tt["m_optionalSlices"] = tranches
        o.save_typetree(tt)
        change = True
        msgs.append(f"{n} : " + ("d'origine" if retirer else "tuiles du bas retirées, grande tuile sur toute la hauteur"))
    if change:
        data = env.file.save(packer="original")
        if nb.DRY_RUN:
            msgs.append(f"(essai à blanc : rien écrit, {os.path.basename(TUILES_BUNDLE)} ferait {len(data) / 1e6:.2f} Mo)")
        else:
            backup.write_bundle(TUILES_BUNDLE, data)
    elif not msgs:
        msgs.append("grilles de la page club : " + ("déjà d'origine" if retirer else "déjà appliquées"))
    return msgs


def noms_cliquables(t):
    """v8 : carte d'un joueur des onzes types (BestXIPosition : onze de légende, onzes de saison, présentation du
    club) : le nom de famille (SIText #name) caché, à sa place le bouton de nom de FM (PlayerNameButton dans le
    BindingRemapper de PlayerNameWNationalityCell) : souligné au survol, clic = fiche du joueur"""
    src = Source(NOM_SOURCE)
    rm = src.t and first(src.t, lambda r: typ(src.t, r) == "BindingRemapper" and any(
        src.t.elem(k).get("m_TemplateAlias") == "PlayerNameButton" for k in src.t.children(r)))
    nom = first(t, lambda r: t.name(r) == "name" and typ(t, r) == "SIText")
    if rm is None or nom is None:
        return None, "nom du joueur ou bouton de nom FM introuvable"
    parent = t.parent[nom]
    r = copier(t, src, rm, parent, t.children(parent).index(nom))
    t.elem(r)["m_RuleIndex"] = -1
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = NOM_CARTE, 1
    t.sd(r)["Mappings"] = [
        {"m_serialisedType": 0, "from": "binding", "to": {"m_path": "Position.BestPlayer"}, "type": {"id": TYPE_PERSONNE}},
        {"m_serialisedType": 0, "from": "primarytext", "to": {"m_path": "Position.BestPlayer.Surname"}, "type": {"id": 0}},
        {"m_serialisedType": 0, "from": "reportcontextteam", "to": {"m_path": "Position.BestPlayer.Team"},
         "type": {"id": TYPE_EQUIPE}}]
    t.styles.style(t, nom, {"display": AUCUN})
    # v4 : carte remontée (FM la place par le maillot : les noms dépassaient en bas du terrain)
    racine = t.children(t.tt["m_VisualTree"]["rid"])
    corps = racine and next((k for k in t.children(racine[0]) if typ(t, k) == "VisualElement"), None)
    if corps is None:
        return None, "carte : bloc principal introuvable"
    t.styles.style(t, corps, {"margin-top": -CARTE_DECALAGE})
    # v5 : cartes plus petites (onze de légende trop serré) : maillot et textes
    fait = []
    if CARTE_MAILLOT:
        m = first(t, lambda r: t.name(r) == "Shirt")
        if m is not None:
            t.styles.style(t, m, {"width": CARTE_MAILLOT, "height": CARTE_MAILLOT, "min-width": CARTE_MAILLOT,
                                  "min-height": CARTE_MAILLOT, "max-width": CARTE_MAILLOT,
                                  "max-height": CARTE_MAILLOT})
            fait.append(f"maillot {CARTE_MAILLOT} px")
    if CARTE_TEXTE:
        n = 0
        for r in t.walk():
            if t.name(r) in ("position", "name", "LabelsContainer", "PlayerNameButton"):
                t.styles.style(t, r, {"font-size": CARTE_TEXTE})
                n += 1
        fait.append(f"textes {CARTE_TEXTE} px ({n})")
    return (f"{CARTE} : nom du joueur cliquable (fiche), remontée de {CARTE_DECALAGE} px"
            f"{', ' + ', '.join(fait) if fait else ''}"), None


MODELES = ((MODELE, NOM, construire), (CARTE, NOM_CARTE, noms_cliquables))


def marque(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def cmd_appliquer():
    for modele, nom, faire in MODELES:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} introuvable (renommé par une mise à jour ?), rien fait")
            continue
        if any(o[3].name(r) == nom for r in marque(o[3])):
            print(f"{modele} : déjà appliqué")
            continue
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marque(t):
            print(f"{modele} : pas de sauvegarde d'origine propre, rien fait")
            continue
        msg, err = faire(t)
        if err:
            print(f"{modele} : {err}, rien enregistré")
            continue
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        print(msg)
    nb.save_all()
    for m in grilles(False):
        print(m)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    msgs = grilles(True)
    if msgs != ["grilles de la page club : déjà d'origine"]:
        for m in msgs:
            print(m)
    rien = True
    for modele, _, _ in MODELES:
        o = ouvrir(modele)
        if o is None or not marque(o[3]):
            continue
        rien = False
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{modele} : pas de sauvegarde d'origine")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        print(f"{modele} : remis d'origine")
    nb.save_all()
    if rien:
        print("rien à retirer")


def cmd_etat():
    for modele, nom, _ in MODELES:
        o = ouvrir(modele)
        m = o and marque(o[3])
        print(f"{modele} :", ("à jour" if any(o[3].name(r) == nom for r in m) else "ANCIENNE version") if m else "d'origine")
    for n, (_, tt) in _compositions(UnityPy.load(TUILES_BUNDLE)).items():
        print(f"{n} :", ", ".join(f"{c['m_elementID']} {c['m_location']['width']}x{c['m_location']['height']}"
                                  for c in tt["m_gridComponents"]))


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("vue d'ensemble du club : non activée, rien à faire")
        return
    {"appliquer": cmd_appliquer, "retirer": cmd_retirer, "etat": cmd_etat}.get(op, lambda: sys.exit(__doc__))()
    if op == "etat":
        print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


if __name__ == "__main__":
    main(sys.argv[1:])
