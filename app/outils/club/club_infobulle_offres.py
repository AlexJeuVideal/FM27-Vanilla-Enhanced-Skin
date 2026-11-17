"""Offres de transfert / prêt (Marché des transferts) : un « i » à gauche du nom du club, comme celui des joueurs.
Au survol, une petite bulle avec les infos du club :

  [LOGO]  AC Oulu
          [drapeau] Finlande
  [ligue] 3e de Veikkausliiga         (caché si la division n'est pas chargée dans la partie)
  ───────────────────────────────
  Statut                   Semi-professionnel      (lignes alternées, fond clair une sur deux)
  Réputation               (jauge) Nationale
  Finances                 Stable
  ───────────────────────────────
  Installations
  Centre d'entraînement    10-11  ★★★
  Structures de formation  9      ★★½
  Encadrement des jeunes   8      ★★
  Recrutement des jeunes   7      ★★

Modèles touchés (seul propriétaire) : TransferActivityClubIconNameAndOfferTypeCell (cellule Club des offres, contexte
`club` = binding.Team.Club) et, depuis la v5, ClubCell (colonne Club des tableaux : vues de recrutement, recherche,
clubs intéressés..., paramètre `club`). Le « i » et la bulle sont recopiés de PlayerReportPreviewTooltip (élément
.object-preview-hover-hotspot : icône + SI.Bindable.Tooltip Preview), le contenu de FM de la bulle est remplacé par le
nôtre, fait de morceaux FM recopiés : logo du club (ClubIcon, agrandi), drapeau, logo de ligue, lignes, jauge de
réputation et trait de la tuile Infos du club (ClubInfoTile_4x4), étoiles du bandeau du club (stats-star ratings).
Notes des installations : comme le bandeau du club (Entraînement : note exacte de l'objet éditeur, fourchette en
repli ; note exacte « Stars » pour les jeunes). Même cellule dans tous les modes d'affichage.

Usage : .venv\\Scripts\\python.exe outils\\club\\club_infobulle_offres.py appliquer|retirer|etat|si-actif [--dry-run]
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
from notes_installations import (first, src_tree, text_static, text_direct, paliers, exacte, rating_values,  # noqa: E402
                                 visible_model, new_visible, equal_binding)
from notes_installations import (note_editeur, NOM_PALIER, decode_args, encode_args, _varint, _enc_varint,  # noqa: E402
                                 _texte_visible, SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)
from club_bandeau_installations import original, fourchette, CONSTANTES, LISTE_EDITEUR  # noqa: E402
from elements import move, copy_usings, bulle_du_i  # noqa: E402
import options  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
# lignes de la bulle : (nom affiché, type, donnée) ; "texte" = texte de FM tel quel, "jauge" = jauge de réputation
# de FM + texte, "fourchette" = palier d'installation (10-11...), "exacte" = objet Stars (MinValue / MaxValue)
INFOS = [
    (L("Niveau de la division", "Division level"), "niveau", "club.Division"),   # v15 (rien si division pas jouable)
    (L("Statut", "Status"), "texte", "club.ProfessionalStatus"),
    (L("Réputation", "Reputation"), "jauge", "club.ReputationScope.DisplayString"),
    (L("Finances", "Finances"), "texte", "club.FinancialStatus.DisplayValue"),
]
TITRE_INSTALLATIONS = L("Installations", "Facilities")
ETOILES = True                              # étoiles de FM après les notes des installations
LOGO = 40                                   # px, logo du club en haut (24 dans les cellules FM)
HAUTEUR_LIGNE = 24                          # px (32 dans la tuile Infos du club)
LARGEUR_MIN = 310                           # px, largeur mini de la bulle
LARGEUR_NOTE = 40                           # px, colonne des notes (étoiles alignées après)
INSTALLATIONS = [
    (L("Centre d'entraînement", "Training Facilities"), "fourchette", "club.TrainingFacilityRating.Rating"),
    (L("Structures de formation", "Youth Facilities"), "exacte", "club.MainTeam.YouthFacilitiesStars"),
    (L("Encadrement des jeunes", "Junior Coaching"), "exacte", "club.MainTeam.YouthCoachingStars"),
    (L("Recrutement des jeunes", "Youth Recruitment"), "exacte", "club.MainTeam.YouthRecruitmentStars"),
]
TITRE = "club.Name"                         # à droite du logo
CONTINENTALE = "club.ContinentalCompetition"   # en haut à droite : coupe continentale jouée ("" = rien) (v11)
CONTINENTALE_LOGO = 24                      # px
SOUS_TITRE = "club.MainTeam.Description"    # ligne de FM : « 3e de Veikkausliiga » (avec le logo de la ligue)
REPLI_DIVISION = "club.DomesticDivision"    # si club.Division est vide (tableaux) : division nationale ("" = rien)
LARGEUR_NOMS = 165                          # px, colonne des noms
LARGEUR_VALEURS = 150                       # px, au plus (texte coupé « ... » au-delà)
DIVISION_APRES_NOM = True                  # offres : division du club juste après son nom (« Legnago  Serie D »)
DIVISION_OBJET = "club.Division"
DIVISION = "club.Division.shortname"        # nom court (comme les suspensions) ; v6 : club.Division.Name
DIVISION_LOGO = 20                          # px, logo de la ligue (16 chez FM ; v8 : « un poil plus gros »)
DIVISION_DECALAGE = 12                      # px, écart après le bloc nom / type d'offre (v8 : 8 après le nom)
# lignes de la mini-bulle de la division (v10) : (nom affiché, "jauge" | "texte", donnée sous la division)
DIVISION_INFOS = [
    (L("Réputation", "Reputation"), "jauge", "ReputationScope"),
    (L("Niveau dans le pays", "Level in the country"), "niveau", ""),   # v15 : par les divisions supérieures
    (L("Tenant du titre", "Title holder"), "tenant", "Holder.Club.Name"),   # v22 ; v26 : « Non jouable » si aucun
    ("", "mercato", ""),   # v22 : ouvert / fermé + jours ; v24 : sans nom à gauche (le texte de FM dit « Mercato… »)
]
SOURCE_MERCATO = "TransferWindowHeaderBlock"   # bloc de FM : mercato fermé / ouvert / restreint + jours restants
NIVEAU_VARIABLE = "uipickerdivision"        # nom de la division redéclarée pour le calcul du niveau (v18)
JOUABLE_TRANSFERTS = SOUS_TITRE             # Transferts : CurrentStage pas donné (essai v20) -> « 14e en ... » pas vide
JOUABLE = ".CurrentStage"                 # existe seulement pour une division jouée dans la partie (v17)
NON_JOUABLE = L("Non jouable", "Not playable")
NIVEAUX = [L("1re division", "Top tier"), L("2e division", "2nd tier"), L("3e division", "3rd tier"),
           L("4e division", "4th tier"), L("5e division ou moins", "5th tier or lower")]
DIVISION_BULLE_MIN = 240                    # px, largeur mini de la mini-bulle
DIVISION_BULLE_LOGO = 32                    # px, logo en haut de la mini-bulle
DIVISION_LARGEUR_NOMS = 130                 # px, colonne des noms de la mini-bulle
DIVISION_LARGEUR_VALEURS = 280              # px, au plus (v23 : 150 coupait « Mercato estival ouvert  22 jours... »)
NOM_DIVISION = "UIPickerDivision"           # zone de survol de la division (pas le préfixe des blocs)
SOURCE_DIVISION = "CompCellShort"         # BindingRemapper « comp » de la colonne des suspensions
SOURCE_LOGO_LIGUE = "comp-cell-medium"      # logo de la compétition (modèle CompetitionLogo)
# =====================================================================================================

MODELE = "TransferActivityClubIconNameAndOfferTypeCell"
MODELE_TABLEAUX = "ClubCell"                # colonne Club des tableaux (vues de recrutement, recherche...)
MODELE_DIVISIONS = "CompCell"               # colonne Division des tableaux (comp.Name)
# autres cellules Club des tableaux, même structure que ClubCell (v15) : colonne « club-player-search » (base de
# données des joueurs) et « club-icon-name-small » (3 lettres)
MODELES_TABLEAUX_AUTRES = ["ClubCellTightBorder", "ClubCellThreeLetterName"]
SOURCE_INFO = "PlayerReportPreviewTooltip"
SOURCE_TUILE = "ClubInfoTile_4x4"           # lignes, jauge, drapeau, logo de ligue, trait
SOURCE_LOGO = "ClubIcon"
SOURCE_ETOILES = "stats-star ratings"
VERSION = f"31{SUFFIXE}"    # v31 : FM du 2026-11-17, bulle du « i » prise dans PlayerReportPreviewTooltipContent
   # v30 : option etoiles_installations « sans » = pas de section Installations
   # v29 : option « sans étoiles » (remplacée)
   # v28 : installations seulement avec notes_installations (comme le bandeau v14)
   # v27 : note Entraînement en fourchette aussi sans éditeur (garde de note_editeur)
   # v26 : tenant « Non jouable » si aucun
   # v25 : mercato dans la grille (statut à gauche, jours à droite)
   # v23 : mini-bulle plus large, mercato pas coupé ; v24 : sans le nom « Mercato »
   # v22 : tenant du titre + mercato dans la mini-bulle de la division
   # v20 : essai Transferts ; v21 : « jouée » par le classement dans Transferts
   # v19 : niveau sur la division nationale si pas de division de la saison
   # v17 : « Non jouable » ; v18 : division redéclarée avec son type (Transferts)
   # v15 : niveau de la division, cellules Club de la base de données ; v16 : niveau
                            # par SIVisible directs
   # v13 : repli caché quand club.Division existe ; v14 : conditions sur le texte    # v9 : division à droite, centrée ; v10 : mini-bulle de la division au survol
                            # v11 : nom court réparé, sans « Niveau », colonne Division, coupe continentale
                            # v12 : repli club.DomesticDivision (club.Division vide dans les tableaux)     # à augmenter quand on change la bulle (langue : suffixe -en)
                            # v5 : Centre d'entraînement = note exacte (objet éditeur), étoiles aussi, fourchette en repli
                            # v6 : offres, division après le nom du club ; v7 : logo de la ligue + nom court, en petit
PREFIXE = "UIPickerInfoClub"
MARKER = os.path.join(backup.BACKUP_DIR, "club_infobulle_offres.actif")
MARKER_NOTES = os.path.join(backup.BACKUP_DIR, "notes_installations.actif")   # notes_installations.MARKER
INSTALLATIONS_SI_NOTES = True   # section Installations (notes + étoiles) seulement si notes_installations est active
AVEC_INSTALLATIONS = options.get("etoiles_installations") == "avec" \
    and (not INSTALLATIONS_SI_NOTES or os.path.exists(MARKER_NOTES))   # option de l'app (v30) et notes /20
NOM = f"{PREFIXE}-v{VERSION}" + ("" if AVEC_INSTALLATIONS else "-sans-installations")   # nom change = bulle refaite
for _nom, _id in (("height", 131087), ("width", 131105), ("max-height", 131094), ("margin-left", 131091),
                  ("margin-bottom", 131090), ("margin-top", 131093)):   # StylePropertyId
    sm.PROPRIETES.setdefault(_nom, (_id, 3))
CLS_NOM = ["body-sm-regular", "global-text-secondary", "content-no-wrap"]
CLS_VALEUR = ["body-sm-strong", "global-text-primary", "content-no-wrap", "content-ellipsis"]


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]



def plain(t, model, parent, cls, index=None, name=""):
    """conteneur vide copié de model (sans enfants, sans style intégré)"""
    r = t.clone_shallow(model, parent, index)
    t.elem(r)["m_Classes"] = list(cls)
    t.elem(r)["m_RuleIndex"] = -1
    t.sd(r)["name"] = name
    t.sd(r)["name_UxmlAttributeFlags"] = 1 if name else 0
    return r


def rebind(t, root, ancien, nouveau):
    """chemins de liaison du sous-arbre root (liaisons directes, composants, arguments des fonctions visuelles) qui
    commencent par ancien (sans tenir compte de la casse) réécrits avec nouveau"""
    a = ancien.lower()

    def chemin(p):
        q = p.lower()
        return nouveau + p[len(a):] if q == a or q.startswith(a + ".") else p

    def octets(val):
        """chaînes (longueur sur 1 octet + texte) d'un argument qui sont des chemins à réécrire (ex. liste de
        TranslationArg du bloc mercato de FM, v22)"""
        out, i = bytearray(), 0
        while i < len(val):
            n = val[i]
            bout = val[i + 1:i + 1 + n]
            if 0 < n < 128 and len(bout) == n and all(0x20 < c < 0x7f for c in bout):
                p = bout.decode()
                q = chemin(p)
                if q != p:
                    out += _enc_varint(len(q)) + q.encode()
                    i += 1 + n
                    continue
            out.append(n)
            i += 1
        return bytes(out)

    def args(ab):
        out = decode_args(ab)
        for arg in out:
            if arg[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") and arg[1][:1] == b"\x01":
                n, j = _varint(arg[1], 1)
                p = arg[1][j:j + n].decode()
                q = chemin(p).encode()
                arg[1] = b"\x01" + _enc_varint(len(q)) + q + arg[1][j + n:]
            elif arg[0].startswith(b"SI.VisualScripting.StructListVisualArg"):
                arg[1] = octets(arg[1])
        return encode_args(out)

    def scan(x):
        if isinstance(x, dict):
            if x.get("name") == "mappings" and isinstance(x.get("value"), str):   # objet UXML d'un composant
                x["value"] = ",".join(":".join([m[0], chemin(m[1])] + m[2:]) if len(m) > 1 else ":".join(m)
                                      for m in (e.split(":") for e in x["value"].split(",")))
            for k, v in x.items():
                if k == "m_path" and isinstance(v, str):
                    x[k] = chemin(v)
                elif k == "m_argumentBytes" and v:
                    x[k] = args(v)
                else:
                    scan(v)
        elif isinstance(x, list):
            for v in x:
                scan(v)
    for rid in t.closure(root):
        scan(t.refs[rid].get("data") or {})


def visible_direct(t, parent, chemin, inverse):
    """SIVisible direct sur l'objet chemin (existe, ou n'existe pas si inverse), copié de CompCellShort (drapeaux
    UXML posés) ; None si le modèle manque"""
    s, _ = src_tree(SOURCE_DIVISION)
    src = s and next((r for r in s.walk() if typ(s, r) == "SIVisible"
                      and bool(s.sd(r).get("InvertDirectBinding")) == inverse), None)
    if src is None:
        return None
    v = t.clone(src, parent, None, src=s)
    for c in t.children(v):
        t.remove(c)
    no_styles(t, v)
    t.sd(v)["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    t.elem(v)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    return v


def niveau_division(t, parent, base, texte):
    """niveau de la division base dans son pays (v15) : on remonte les divisions supérieures (PromotionDivision) ;
    la 1re n'en a pas. v16 : SIVisible directs sur l'objet (existe / n'existe pas, ceux de CompCellShort) : en v15 la
    condition « nom vide » ne répondait rien quand la division du dessus n'existe pas"""
    s, _ = src_tree(SOURCE_DIVISION)
    if s is None or visible_direct(t, parent, base, False) is None:
        return
    t.remove(t.children(parent)[-1])   # essai de visible_direct ci-dessus

    def direct(parent_, chemin, inverse):
        return visible_direct(t, parent_, chemin, inverse)

    # v18 : division redéclarée avec son type (BindingRemapper « comp » de CompCellShort) : dans Transferts (club
    # donné par un renvoi sans type), les SIVisible directs ne répondaient rien ; dans les tableaux ça marchait
    rmp = first(s, lambda r: typ(s, r) == "BindingRemapper")
    if rmp is not None:
        r = t.clone(rmp, parent, None, src=s)
        for c in t.children(r):
            t.remove(c)
        no_styles(t, r)
        t.elem(r)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        mp = copy.deepcopy(next(m for m in t.sd(r)["Mappings"] if m["from"] == "comp"))
        mp["from"], mp["to"]["m_path"] = NIVEAU_VARIABLE, base
        t.sd(r)["Mappings"] = [mp]
        parent, base = r, NIVEAU_VARIABLE
    cur = direct(parent, base, False)
    # v17 : division pas jouable (pas de phase en cours) : pas de division au-dessus, « 1re » à tort en v16
    if _jouable_texte:   # v21, Transferts : CurrentStage pas donné là (essai v20) -> classement du club pas vide
        st, vt = visible_model(SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)
        classer(t, text_static(t, texte, _texte_visible(t, st, vt, cur, _jouable_texte, True, ""), NON_JOUABLE),
                CLS_VALEUR)
        cur = _texte_visible(t, st, vt, cur, _jouable_texte, False, "")
    else:
        classer(t, text_static(t, texte, direct(cur, base + JOUABLE, True), NON_JOUABLE), CLS_VALEUR)
        cur = direct(cur, base + JOUABLE, False)
    p = base
    for k, nom in enumerate(NIVEAUX):
        if k == len(NIVEAUX) - 1:   # dernier : « ou moins »
            classer(t, text_static(t, texte, cur, nom), CLS_VALEUR)
            break
        haut = p + ".PromotionDivision"
        classer(t, text_static(t, texte, direct(cur, haut, True), nom), CLS_VALEUR)
        cur = direct(cur, haut, False)
        p = haut


def classer(t, r, cls):
    """classes de texte voulues, sans le style intégré ni les marges de la cellule d'origine"""
    t.elem(r)["m_Classes"] = list(cls)
    t.elem(r)["m_RuleIndex"] = -1
    return r


_jouable_texte = None   # « division jouée » par un texte pas vide au lieu de CurrentStage (Transferts, v21)


def construire(t):
    global _jouable_texte
    racine = first(t, lambda r: t.name(r) == "content-container")
    remap = racine and first(t, lambda r: typ(t, r) == "BindingRemapper", racine)
    texte = first(t, lambda r: typ(t, r) == "SIText")
    if None in (racine, remap, texte):
        return ["repères introuvables (cellule de FM changée ?), ignoré"]
    _jouable_texte = JOUABLE_TRANSFERTS
    try:
        return construire_offres(t, racine, remap, texte)
    finally:
        _jouable_texte = None


def construire_offres(t, racine, remap, texte):
    msgs = poser(t, remap, texte, racine)
    if DIVISION_APRES_NOM and not any("ignoré" in m for m in msgs):
        # division juste après le nom, dans la ligne « i + nom » (cachée si la division n'est pas chargée) ;
        # v7 : logo de la ligue + nom court en petit, comme la colonne des suspensions (CompCellShort)
        m = Morceaux(t)
        # v9 : à droite du bloc nom / type d'offre (dans #root, centré en hauteur), plus dans la ligne du nom
        root = first(t, lambda r: t.name(r) == "root")
        if root is not None and racine in t.children(root):
            div = m.copie(m.tuile, m.a_division, root, t.children(root).index(racine) + 1)
        else:
            div = m.copie(m.tuile, m.a_division, t.parent[remap])
        for c in t.children(div):
            t.remove(c)
        t.elem(div)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        t.styles.style(t, div, {"margin-left": DIVISION_DECALAGE, "flex-shrink": 0})
        # v10 : logo + nom court dans une zone de survol (le « i » de FM sans son icône), mini-bulle de la division
        zone, bulle = m.zone_survol(div)
        if zone is None:
            zone = div
        m.logo_division(zone, DIVISION_LOGO)
        classer(t, text_direct(t, texte, zone, DIVISION),
                ["body-sm-regular", "global-text-secondary", "content-no-wrap", "content-ellipsis"])
        if bulle is not None:
            move(t, bulle, zone)   # bulle en dernier enfant, comme dans le « i » de FM
            m.bulle_division(bulle, racine, texte)
            msgs.append("bulle de la division au survol")
        msgs.append("division après le nom du club")
    return msgs


def poser(t, nom_club, texte, racine=None):
    """« i » + bulle devant nom_club (élément du nom, contexte `club`) ; texte = SIText modèle des textes ; racine =
    conteneur modèle des boîtes (défaut : le « i » lui-même, vidé) ; aussi pour club_infobulle_tableaux"""
    s, s_bundle = src_tree(SOURCE_INFO)
    zone = s and first(s, lambda r: "object-preview-hover-hotspot" in (s.elem(r).get("m_Classes") or []))
    if zone is None:
        return ["« i » de FM introuvable, ignoré"]
    # ligne « i + nom » à la place du nom seul (dans le SIVisible « club existe » de FM)
    vis = t.parent[nom_club]
    index = t.children(vis).index(nom_club)
    i = t.clone(zone, vis, index, src=s)
    racine = i if racine is None else racine
    ligne = plain(t, racine, vis, ["row-direction-normal", "align-items-center"], index)
    move(t, i, ligne)
    move(t, nom_club, ligne)
    t.styles.copy_from(Styles(s_bundle, s.tt), t, i)
    t.sd(i)["name"], t.sd(i)["name_UxmlAttributeFlags"] = NOM, 1
    t.elem(i)["m_Classes"] = list(t.elem(i)["m_Classes"]) + ["margin-right-global-gap-small"]
    bulle = bulle_du_i(t, i)
    if bulle is None:
        return ["bulle du « i » de FM introuvable, ignoré"]
    for c in t.children(bulle):
        t.remove(c)
    m = Morceaux(t)
    if m.manque():
        return [f"morceaux FM introuvables ({', '.join(m.manque())}), ignoré"]
    p = plain(t, racine, bulle, ["padding-horizontal-global-padding-regular", "padding-vertical-global-padding-regular"])
    t.styles.style(t, p, {"min-width": LARGEUR_MIN})
    # en-tête : logo agrandi | nom / drapeau + pays
    tete = plain(t, racine, p, ["row-direction-normal", "align-items-center"])
    # logo dans une boîte fixe (v2 : la hauteur posée sur le ClubRatioFitter ne bornait rien, logo géant)
    boite = plain(t, racine, tete, ["margin-right-global-gap-regular", "align-items-center", "justify-content-center"])
    t.styles.style(t, boite, {"width": LOGO, "height": LOGO, "min-width": LOGO, "max-width": LOGO,
                              "min-height": LOGO, "max-height": LOGO, "flex-shrink": 0, "overflow": "hidden"})
    logo = m.copie(m.logo, m.icone, boite)
    fit = first(t, lambda r: t.name(r) == "ClubRatioFitter", logo)
    if fit is None and typ(t, logo) == "ComponentElement":   # depuis la MAJ du 2026-11-12 : le ratio est sur le logo
        fit = logo
    if fit is not None:
        t.styles.style(t, fit, {"height": LOGO})
    col = plain(t, racine, tete, [])
    classer(t, text_direct(t, texte, col, TITRE), ["heading-small-16px", "global-text-primary", "content-no-wrap"])
    m.copie(m.tuile, m.nation, col)
    if CONTINENTALE:   # v11 : coupe continentale jouée (logo + nom court) en haut à droite, rien sinon
        t.styles.style(t, col, {"flex-grow": 1})
        m.continentale(tete, racine, texte)
    # classement « 3e de ... » ; v14 : visible si son texte n'est pas vide (dans les tableaux, le SIVisible de FM sur
    # l'objet club.Division ne s'affiche jamais), sinon le nom de la division nationale (REPLI_DIVISION) s'il existe
    st, vt = visible_model(SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)
    cls_rang = ["body-sm-regular", "global-text-secondary", "content-no-wrap"]
    a = _texte_visible(t, st, vt, p, SOUS_TITRE, False, "")
    t.elem(a)["m_Classes"] = list(t.elem(a)["m_Classes"]) + ["margin-top-global-gap-small"]
    classer(t, text_direct(t, texte, a, SOUS_TITRE), cls_rang)
    if REPLI_DIVISION:
        b = _texte_visible(t, st, vt, p, SOUS_TITRE, True, "")
        c = _texte_visible(t, st, vt, b, REPLI_DIVISION + ".Name", False, "")
        t.elem(c)["m_Classes"] = list(t.elem(c)["m_Classes"]) + ["margin-top-global-gap-small"]
        classer(t, text_direct(t, texte, c, REPLI_DIVISION + ".Name"), cls_rang)
    m.copie(m.tuile, m.trait, p)
    for k, (nom, kind, chemin) in enumerate(INFOS):
        if kind == "niveau":   # ligne entière cachée si la division n'a pas de nom
            st, vt = visible_model(SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)
            boite = _texte_visible(t, st, vt, p, chemin + ".Name", False, "")
            t.elem(boite)["m_Classes"] = []   # colonne : la ligne garde toute la largeur
            niveau_division(t, m.ligne(boite, k, nom, texte), chemin, texte)
            if REPLI_DIVISION:   # v19 : pas de division de la saison (ex. Sandhausen) -> niveau de la nationale
                sans = visible_direct(t, p, chemin, True)
                if sans is not None:
                    t.elem(sans)["m_Classes"] = []
                    boite = _texte_visible(t, st, vt, sans, REPLI_DIVISION + ".Name", False, "")
                    t.elem(boite)["m_Classes"] = []
                    niveau_division(t, m.ligne(boite, k, nom, texte), REPLI_DIVISION, texte)
            continue
        case = m.ligne(p, k, nom, texte)
        if kind == "jauge":
            j = m.copie(m.tuile, m.jauge, case)   # styles gardés (taille de la jauge, 14 px)
            for r in t.walk(j):
                if typ(t, r) == "SIText":
                    t.elem(r)["m_Classes"] = CLS_VALEUR + ["margin-left-global-gap-small"]
        else:
            classer(t, text_direct(t, texte, case, chemin), CLS_VALEUR)
    if not AVEC_INSTALLATIONS:   # option « sans » ou notes /20 coupées : ni notes ni étoiles (v28, v30)
        return [f"« i » + bulle du club (logo, drapeau, classement, {len(INFOS)} infos, sans installations)"]
    m.copie(m.tuile, m.trait, p)
    titre = classer(t, text_static(t, texte, p, TITRE_INSTALLATIONS), ["body-sm-strong", "global-text-secondary"])
    t.styles.style(t, titre, {"margin-left": 4, "margin-bottom": 2})   # aligné sur le texte des lignes (marge 4 px)
    for k, (nom, kind, chemin) in enumerate(INSTALLATIONS):
        case = m.ligne(p, k, nom, texte)
        note = plain(t, racine, case, ["row-direction-normal", "align-items-center"])
        t.styles.style(t, note, {"min-width": LARGEUR_NOTE, "flex-shrink": 0})
        v = classer(t, text_direct(t, texte, note, chemin), CLS_VALEUR)
        etoiles = plain(t, racine, case, ["row-direction-normal", "align-items-center"]) if ETOILES else None
        if kind == "fourchette":
            if not paliers(t, v, chemin, rating_values()):
                return [f"{nom} : modèle de visibilité introuvable, ignoré"]
            # v5 : note exacte (objet éditeur du club, comme le bandeau v12), fourchette en repli
            note_editeur(t, [r for r in t.children(note) if t.name(r) == NOM_PALIER], LISTE_EDITEUR)
            fourchettes = []
            for code, txt in rating_values() if etoiles is not None else []:
                if code < 0:
                    continue
                a, b = fourchette(txt)
                pal = new_visible(t, m.vs, m.vis, etoiles, None, "",
                                  equal_binding(m.vs.sd(m.vis)["Binding"], chemin, code),
                                  ["row-direction-normal", "align-items-center"])
                m.etoile(pal, "const." + CONSTANTES[a], "const." + CONSTANTES[b])
                fourchettes.append(pal)
            if fourchettes:
                note_editeur(t, fourchettes, LISTE_EDITEUR, lambda parent, n: m.etoile(parent, n, n))
        elif kind == "exacte":
            if not exacte(t, note, chemin):
                return [f"{nom} : modèles de la note exacte introuvables, ignoré"]
            if etoiles is not None:
                m.etoile(etoiles, chemin + ".MinValue", chemin + ".MaxValue")
    return [f"« i » + bulle du club (logo, drapeau, classement, {len(INFOS)} infos, {len(INSTALLATIONS)} "
            f"installations" + (" avec étoiles" if ETOILES else "") + ")"]


class Morceaux:
    """morceaux FM recopiés dans la bulle (modèles sources, leurs styles intégrés)"""

    def __init__(self, t):
        self.t = t
        self.tuile = self._ouvrir(SOURCE_TUILE)
        self.logo = self._ouvrir(SOURCE_LOGO)
        self.star = self._ouvrir(SOURCE_ETOILES)
        s = self.tuile[0]
        if s is not None:
            def dbg(d):
                return first(s, lambda r: s.sd(r).get("DebugDisplay") == d)
            pro, rep = dbg("Professional status"), dbg("Reputation")
            self.fond = pro and s.parent[s.parent[pro]]          # ligne au fond clair
            self.sans = rep and s.parent[s.parent[rep]]          # ligne sans fond
            g = first(s, lambda r: typ(s, r) == "SIRadialGauge")   # jauge > SIStyleSetter > case (jauge + texte)
            self.jauge = g and s.parent[s.parent[g]]
            n = first(s, lambda r: s.elem(r).get("m_TemplateAlias") == "nation-cell-medium")
            self.nation = n and s.parent[n]
            self.a_division = first(s, lambda r: s.name(r) == "HasDivision")
            self.ligue = first(s, lambda r: s.name(r) == "ui concepts-placeholder")
            self.trait = first(s, lambda r: s.elem(r).get("m_TemplateAlias") == "layout-divider-solid-horizontal")
        s = self.logo[0]
        self.icone = s and first(s, lambda r: typ(s, r) == "BindingSetter" or (       # MAJ FM du 2026-11-12 : un
            typ(s, r) == "ComponentElement" and any(                                   # ComponentElement porte le
                "BindingSetterComponent" in s.refs[c["rid"]]["type"]["class"]          # BindingSetter et le ratio
                for c in s.sd(r).get("m_components") or [])))
        s = self.star[0]
        self.etoile_src = s and first(s, lambda r: typ(s, r) == "FMStarRatingTemp")
        self.vs, self.vis = visible_model()

    def _ouvrir(self, nom):
        s, bundle = src_tree(nom)
        return s, (Styles(bundle, s.tt) if s is not None else None)

    def manque(self):
        noms = ["fond", "sans", "jauge", "nation", "a_division", "ligue", "trait", "icone", "vis"]
        if ETOILES:
            noms.append("etoile_src")
        return [n for n in noms if getattr(self, n, None) is None]

    def copie(self, source, rid, parent, index=None):
        """sous-arbre rid du modèle source (arbre, styles) recopié sous parent, avec ses styles et modèles inclus"""
        s, st = source
        r = self.t.clone(rid, parent, index, src=s)
        copy_usings(self.t, s, rid)
        self.t.styles.copy_from(st, self.t, r)
        return r

    def ligne(self, parent, k, nom, texte, largeur=LARGEUR_NOMS, valeurs=LARGEUR_VALEURS):
        """ligne de la tuile Infos du club (fond clair une sur deux), plus basse : nom | case des valeurs (renvoyée)"""
        t = self.t
        row = self.copie(self.tuile, self.fond if k % 2 == 0 else self.sans, parent)
        for c in t.children(row):
            t.remove(c)
        t.styles.style(t, row, {"height": HAUTEUR_LIGNE})
        if nom:   # v24 : nom vide = pas de colonne des noms (ligne du mercato : le texte de FM le dit déjà)
            n = classer(t, text_static(t, texte, row, nom), CLS_NOM)
            t.styles.style(t, n, {"min-width": largeur, "max-width": largeur, "flex-shrink": 0})
        case = plain(t, row, row, ["row-direction-normal", "align-items-center"])
        t.styles.style(t, case, {"max-width": valeurs, "overflow": "hidden"})
        return case

    def zone_survol(self, parent):
        """« i » de FM (zone + bulle) recopié sous parent, sans son icône, bulle vidée ; renvoie (zone, bulle)"""
        t = self.t
        s, st = self._ouvrir(SOURCE_INFO)
        src = s and first(s, lambda r: "object-preview-hover-hotspot" in (s.elem(r).get("m_Classes") or []))
        if src is None:
            return None, None
        z = self.copie((s, st), src, parent)
        t.sd(z)["name"], t.sd(z)["name_UxmlAttributeFlags"] = NOM_DIVISION, 1
        # v11 : sans la classe ni le style de la zone du « i » (taille d'icône fixe : nom court coupé en v10)
        no_styles(t, z)
        t.elem(z)["m_Classes"] = ["sitext-hover-cursor", "row-direction-normal", "align-items-center"]
        bulle = bulle_du_i(t, z)
        if bulle is None:
            return None, None
        for c in t.children(z):
            if c != bulle:
                t.remove(c)
        for c in t.children(bulle):
            t.remove(c)
        return z, bulle

    def logo_division(self, parent, taille, base=DIVISION_OBJET):
        """logo de la division (CompetitionLogo de comp-cell-medium, contexte comp = base, la division du club)"""
        t = self.t
        court, cellule = self._ouvrir(SOURCE_DIVISION), self._ouvrir(SOURCE_LOGO_LIGUE)
        rmp = court[0] and first(court[0], lambda r: typ(court[0], r) == "BindingRemapper")
        logo = cellule[0] and first(cellule[0], lambda r: cellule[0].elem(r).get("m_TemplateAlias") == "CompetitionLogo")
        if None in (rmp, logo):
            return None
        r = self.copie(court, rmp, parent)
        for c in t.children(r):
            t.remove(c)
        lg = self.copie(cellule, logo, r)
        t.elem(lg)["m_Classes"] = [c for c in t.elem(lg)["m_Classes"] if c != "width-height-16px"]
        t.styles.style(t, lg, {"width": taille, "height": taille, "min-width": taille, "min-height": taille,
                               "flex-shrink": 0})
        t.sd(r)["Mappings"] = [mp for mp in t.sd(r)["Mappings"] if mp["from"] == "comp"]
        for mp in t.sd(r)["Mappings"]:
            mp["to"]["m_path"] = base
        t.elem(r)["m_Classes"] = []   # le logo de FM a déjà sa marge droite
        return r

    def continentale(self, parent, racine, texte):
        """SIVisible « le club joue une coupe continentale » (v14 : nom pas vide, une condition sur l'objet ne marche
        pas dans les tableaux) : logo + nom court"""
        t = self.t
        st, vt = visible_model(SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)
        if vt is None:
            return None
        v = _texte_visible(t, st, vt, parent, CONTINENTALE + ".Name", False, "")
        t.elem(v)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-left-global-gap-regular"]
        self.logo_division(v, CONTINENTALE_LOGO, CONTINENTALE)
        classer(t, text_direct(t, texte, v, CONTINENTALE + ".shortname"),
                ["body-sm-regular", "global-text-secondary", "content-no-wrap"])
        return v

    def mercato(self, parent, base):
        """état du mercato de la division : BindableSwitchElement de TransferWindowHeaderBlock recopié (sans icônes),
        liaisons comp. -> base, textes en petit"""
        t = self.t
        src = self._ouvrir(SOURCE_MERCATO)
        s = src[0]
        sw = s and first(s, lambda r: typ(s, r) == "BindableSwitchElement")
        if sw is None:
            return None
        v = self.copie(src, sw, parent)
        rebind(t, v, "comp", base)
        for r in [r for r in t.walk(v) if t.name(r) == "Icon"]:
            t.remove(r)
        for etat in t.children(v):   # #WindowClosed / #WindowOpen / #WindowRestrict : statut | jours restants
            no_styles(t, etat)
            t.elem(etat)["m_Classes"] = ["row-direction-normal", "align-items-center"]
            # v25 : dans la grille des autres lignes : statut (« Mercato en cours ») = colonne des noms (gris),
            # jours restants = colonne des valeurs (blanc gras)
            for k, r in enumerate(c for c in t.children(etat) if typ(t, c) == "SIText"):
                classer(t, r, CLS_NOM if k == 0 else CLS_VALEUR)
                if k == 0:
                    t.styles.style(t, r, {"min-width": DIVISION_LARGEUR_NOMS, "max-width": DIVISION_LARGEUR_NOMS,
                                          "flex-shrink": 0})
        return v

    def bulle_division(self, bulle, racine, texte, base=DIVISION_OBJET):
        """mini-bulle de la division base : logo + nom / drapeau + pays ; trait ; lignes DIVISION_INFOS
        (v11 : « Niveau dans le pays » retiré, DivisionLevel vide en jeu)"""
        t = self.t
        p = plain(t, racine, bulle, ["padding-horizontal-global-padding-regular", "padding-vertical-global-padding-regular"])
        t.styles.style(t, p, {"min-width": DIVISION_BULLE_MIN})
        tete = plain(t, racine, p, ["row-direction-normal", "align-items-center"])
        self.logo_division(tete, DIVISION_BULLE_LOGO, base)
        col = plain(t, racine, tete, ["margin-left-global-gap-small"])
        classer(t, text_direct(t, texte, col, base + ".Name"), ["heading-small-16px", "global-text-primary",
                                                                 "content-no-wrap"])
        rebind(t, self.copie(self.tuile, self.nation, col), "club.displaynation", base + ".Nation")
        self.copie(self.tuile, self.trait, p)
        for k, (nom, kind, donnee) in enumerate(DIVISION_INFOS):
            case = self.ligne(p, k, nom, texte, DIVISION_LARGEUR_NOMS, DIVISION_LARGEUR_VALEURS)
            if kind == "jauge":
                j = self.copie(self.tuile, self.jauge, case)
                rebind(t, j, "club.reputationscope", base + ".ReputationScope")
                for r in t.walk(j):
                    if typ(t, r) == "SIText":
                        t.elem(r)["m_Classes"] = CLS_VALEUR + ["margin-left-global-gap-small"]
            elif kind == "niveau":
                niveau_division(t, case, base, texte)
            elif kind == "mercato":   # v22 : bloc de FM (fermé / ouvert / restreint + jours restants)
                self.mercato(case, base)
            elif kind == "tenant":   # v26 : pas de tenant (division pas jouable) -> « Non jouable »
                oui, non = visible_direct(t, case, base + ".Holder", False), visible_direct(t, case, base + ".Holder", True)
                if oui is None:
                    continue
                classer(t, text_direct(t, texte, oui, f"{base}.{donnee}"), CLS_VALEUR)
                classer(t, text_static(t, texte, non, NON_JOUABLE), CLS_VALEUR)
            else:
                classer(t, text_direct(t, texte, case, f"{base}.{donnee}"), CLS_VALEUR)

    def etoile(self, parent, mini, maxi):
        t = self.t
        e = t.clone(self.etoile_src, parent, None, src=self.star[0])
        no_styles(t, e)
        t.elem(e)["m_Classes"] = ["margin-left-global-gap-small"]
        t.sd(e)["MinBinding"] = {"m_path": mini}
        t.sd(e)["MaxBinding"] = {"m_path": maxi}


def construire_tableaux(t):
    """ClubCell (colonne Club des tableaux, contexte `club`) : BindableSwitchElement = nom du club (BindingRemapper
    + club-cell-medium) si le club existe, sinon « [-] » (SIText) ; le « i » va devant le BindingRemapper"""
    sw = first(t, lambda r: typ(t, r) == "BindableSwitchElement")
    remap = sw and next((r for r in t.children(sw) if typ(t, r) == "BindingRemapper"), None)
    texte = sw and next((r for r in t.children(sw) if typ(t, r) == "SIText"), None)
    if None in (remap, texte):
        return ["repères introuvables (cellule de FM changée ?), ignoré"]
    return poser(t, remap, texte)


def construire_divisions(t):
    """CompCell (colonne Division / compétition des tableaux, paramètre `comp`) : 1er SIVisible (comp existe) >
    BindingRemapper (comp-cell-medium) ; « i » devant, mini-bulle de la division (v11)"""
    remap = first(t, lambda r: typ(t, r) == "BindingRemapper")
    texte = first(t, lambda r: typ(t, r) == "SIText")
    if None in (remap, texte):
        return ["repères introuvables (cellule de FM changée ?), ignoré"]
    s, s_bundle = src_tree(SOURCE_INFO)
    zone = s and first(s, lambda r: "object-preview-hover-hotspot" in (s.elem(r).get("m_Classes") or []))
    if zone is None:
        return ["« i » de FM introuvable, ignoré"]
    vis = t.parent[remap]
    index = t.children(vis).index(remap)
    i = t.clone(zone, vis, index, src=s)
    ligne = plain(t, i, vis, ["row-direction-normal", "align-items-center"], index)
    move(t, i, ligne)
    move(t, remap, ligne)
    t.styles.copy_from(Styles(s_bundle, s.tt), t, i)
    t.sd(i)["name"], t.sd(i)["name_UxmlAttributeFlags"] = NOM, 1
    t.elem(i)["m_Classes"] = list(t.elem(i)["m_Classes"]) + ["margin-right-global-gap-small"]
    bulle = bulle_du_i(t, i)
    if bulle is None:
        return ["bulle du « i » de FM introuvable, ignoré"]
    for c in t.children(bulle):
        t.remove(c)
    m = Morceaux(t)
    if m.manque():
        return [f"morceaux FM introuvables ({', '.join(m.manque())}), ignoré"]
    m.bulle_division(bulle, i, texte, "comp")
    return ["« i » + bulle de la division"]


# modèles touchés (seul propriétaire de chacun) : (nom, construction) ; v5 : + colonne Club des tableaux ;
# v11 : + colonne Division (CompCell) ; v15 : + cellules Club de la base de données / recherche (même structure)
MODELES = [(MODELE, construire), (MODELE_TABLEAUX, construire_tableaux), (MODELE_DIVISIONS, construire_divisions)] + \
          [(nom, construire_tableaux) for nom in MODELES_TABLEAUX_AUTRES]


def ouvrir(depart_original=False, modele=MODELE):
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None, None, None, None
    if depart_original:
        tt = original(bundle, obj) or tt
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    return bundle, obj, tt, t


def blocs(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def enregistrer(bundle, obj, tt, t, sauver=True):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    if sauver:
        nb.save_all()


def cmd_appliquer():
    for modele, fabrique in MODELES:
        bundle, obj, tt, t = ouvrir(modele=modele)
        if tt is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        old = [t.name(r) for r in blocs(t)]
        if old == [NOM]:
            print(f"{modele} : déjà appliqué")
            continue
        bundle, obj, tt, t = ouvrir(depart_original=True, modele=modele)
        if blocs(t):   # pas de sauvegarde d'origine : on part du modèle tel quel, sans relancer par-dessus
            print(f"{modele} : ancienne version présente et pas d'original, retirer d'abord")
            continue
        msgs = fabrique(t)
        for m in msgs + (["ancienne version remplacée"] if old else []):
            print(f"{modele} : {m}")
        if not any("ignoré" in m for m in msgs):
            enregistrer(bundle, obj, tt, t, sauver=False)
    nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    rien = True
    for modele, _ in MODELES:
        bundle, obj, tt, t = ouvrir(modele=modele)
        if t is None or not blocs(t):
            continue
        rien = False
        orig = original(bundle, obj)
        if orig is not None:
            obj.save_typetree(orig)
            nb._dirty.add(bundle)
            print(f"{modele} : remis d'origine")
            continue
        for i in blocs(t):   # sans original : le nom ressort de notre ligne
            ligne = t.parent[i]
            vis = t.parent[ligne]
            for c in [c for c in t.children(ligne) if c != i]:
                move(t, c, vis, t.children(vis).index(ligne))
            t.remove(ligne)
        enregistrer(bundle, obj, tt, t, sauver=False)
        print(f"{modele} : « i » du club retiré")
    if rien:
        print("rien à retirer")
    nb.save_all()


def cmd_etat():
    for modele, _ in MODELES:
        _, _, tt, t = ouvrir(modele=modele)
        if tt is None:
            print(f"{modele} : introuvable")
            continue
        old = [t.name(r) for r in blocs(t)]
        print(f"{modele} : " + (f"appliqué ({', '.join(old)} ; version actuelle v{VERSION})" if old else "d'origine"))
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
            print("bulle du club (offres) : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
