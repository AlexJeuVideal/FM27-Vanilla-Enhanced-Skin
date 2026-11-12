"""Bandeau du haut de la page club (tous les clubs) : installations, stade et finances.

  Centre d'entraînement 14-15 ★★★½ | Encadrement des jeunes 10 ★★½ | Forme | ... | Stade      | Capacité 25 586     | Finances
  Structures de formation  11 ★★½  | Recrutement des jeunes 10 ★★½ |      |     | MKM Stadium| Construit en 2002   | (pièces) Prospère
                                                                                  (+ Prix des places / Prix abonnement)

Tout est ajouté au modèle ClubSiteHeaderTemplate (contexte `club` : n'importe quel club).
- Installations, à gauche de « Forme » : mêmes notes que notes_installations.py (exactes pour Structures / Encadrement
  / Recrutement, fourchette pour l'Entraînement). Étoiles : dessin d'étoiles de FM (FMStarRatingTemp) alimenté par
  les « Stars » sur 20 ; pour l'Entraînement, une valeur fixe par palier (constantes FM const.Ten...).
- Stade, juste après « Stade » : capacité, année de construction, prix moyens (textes FM recopiés de la fiche
  Profil du club, ClubProfileBlock : mêmes formats, € compris).
- Finances, après le stade : section comme « Surnom » (titre, petite icône pièces, état : Prospère...).

Menu Outils FM.bat : 16 (catégorie), puis la fonction ; réappliqué par le choix 1.
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
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
from notes_installations import (first, src_tree, visible_model, new_visible, equal_binding, text_static,  # noqa: E402
                                 paliers, exacte, rating_values, make_binding, note_editeur, NOM_PALIER)
from elements import move  # noqa: E402
import options  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
# Chaque bloc = colonnes, chacune lue de haut en bas : (nom affiché, type, donnée)
#   "fourchette" : palier d'installation (Rating) -> 10-11... ; "exacte" : objet Stars (MinValue/MaxValue) ;
#   "fm"         : texte de FM recopié tel quel (nom de l'élément dans ClubProfileBlock)
INSTALLATIONS = [
    # noms fixes : français ou anglais selon langue.py (choix 106)
    [(L("Centre d'entraînement", "Training Facilities"), "fourchette", "club.TrainingFacilityRating.Rating"),
     (L("Structures de formation", "Youth Facilities"), "exacte", "club.MainTeam.YouthFacilitiesStars")],
    [(L("Encadrement des jeunes", "Junior Coaching"), "exacte", "club.MainTeam.YouthCoachingStars"),
     (L("Recrutement des jeunes", "Youth Recruitment"), "exacte", "club.MainTeam.YouthRecruitmentStars")],
]
STADE = [   # [] = pas de bloc prix ; possibles : [("Prix des places", "fm", "MatchTicketPriceText"),
            # ("Prix abonnement", "fm", "SeasonTicketPriceText")], ("Capacité", "fm", "TotalCapacityText"),
            # ("Construit en", "fm", "YearBuiltText") (prix retirés en v7, capacité / année en v3)
]
STADE_FM = False               # False : la section « Stade » de FM (nom du stade) est retirée du bandeau
FINANCES = True                # section « Finances » (icône pièces + Prospère, Stable...)
FINANCES_HORS_LARGE = True     # Finances cachée en mode d'affichage Large (place), gardée en Medium / Small
SURNOM_HORS_LARGE = True       # section « Surnom » de FM cachée en mode Large aussi (v10)
TEXTE_REDUIT = {               # classes de texte du bandeau remplacées (une taille en dessous, suit la taille du texte FM)
    "body-md-regular": "body-sm-regular", "body-regular-14px-regular": "body-sm-regular"}   # 14 -> 12 px
TEXTE_REDUIT_LARGE_SEUL = True  # texte réduit en mode Large seulement (2 copies de chaque texte, une par mode)
PERSONNALITE = True            # section « Personnalité de l'effectif » (titre traduit par FM, ex. Équilibrée)
# ordre des sections du bandeau, de gauche à droite (une section absente de la liste reste à la fin, dans l'ordre FM)
ORDRE = ["installations", "etabli", "reputation", "professionnalisme", "personnalite", "surnom", "forme", "stade",
         "prix", "finances", "feminine"]
# ordre d'origine de FM : forme, professionnalisme, etabli, stade, surnom, reputation, feminine
ETOILES = True                 # étoiles de FM à droite des notes d'installations
INSTALLATIONS_SI_NOTES = True  # installations (notes + étoiles) seulement si la fonction notes_installations est
                               # active (v14, retour d'un joueur : la couper laissait notes et étoiles en haut)
INSTALLATIONS_OPTION = options.get("etoiles_installations") == "avec"   # option de l'app (v16) : « sans » = section
                               # installations retirée (ni notes ni étoiles)
SEULEMENT_SI_LARGE = True      # comme « Niveau de professionnalisme » : caché quand la fenêtre est trop étroite
HAUTEUR_LIGNE = 24             # px ; le bandeau de FM fait 66 px de haut
MAILLOTS_EN_HAUT = False       # False : les 3 maillots à côté du nom du club sont retirés (ils sont dans le panneau
                               # du bas, voir club_page_bas.py)
# =====================================================================================================

MODELE = "ClubSiteHeaderTemplate"
VERSION = f"16{SUFFIXE}"   # à augmenter quand on change les réglages : refait les blocs (langue : suffixe -en)
                           # v11 : Centre d'entraînement = note exacte (objet éditeur du club), fourchette en repli ;
                           # v12 : ses étoiles aussi ; v13 : fourchette aussi sans éditeur (garde de note_editeur) ;
                           # v14 : installations seulement avec notes_installations (INSTALLATIONS_SI_NOTES) ;
                           # v15 : option « sans étoiles » (remplacée) ; v16 : option etoiles_installations
                           # « sans » = pas de section installations
ENTRAINEMENT = "club.TrainingFacilityRating.Rating"
LISTE_EDITEUR = "club.Editor.GenericSections"
PREFIXE = "UIPickerBandeau"
NOMS = {"installations": f"{PREFIXE}Installations-v{VERSION}", "stade": f"{PREFIXE}Stade-v{VERSION}",
        "finances": f"{PREFIXE}Finances-v{VERSION}", "personnalite": f"{PREFIXE}Personnalite-v{VERSION}",
        "surnom": f"{PREFIXE}Surnom-v{VERSION}"}   # surnom : SIVisible « hors mode Large » autour de #Nickname
NOM_TRAIT = f"{PREFIXE}Trait-v{VERSION}"   # trait ajouté par le réordonnancement (ex. après Réputation)
SECTIONS_FM = {"Form": "forme", "ProfessionalStatus": "professionnalisme", "Founded": "etabli", "Stadium": "stade",
               "Nickname": "surnom", "Rep": "reputation"}
LIAISON_FEMININE = "teamcontainer.OppositeGenderTeamContainer"
NOM_ETOILES = "UIPickerEtoiles"
NOM_TEXTE_MODE = "UIPickerTexteMode"          # SIVisible des 2 copies d'un texte (pas le préfixe : pas un bloc)
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Large, 1 Medium, 2 Small
OP_EGAL, OP_SUPERIEUR = 2, 4                  # opérateurs de comparaison FM
ETOILES_SOURCE = "stats-star ratings"
TEXTES_SOURCE = "ClubProfileBlock"
TITRE_FINANCES = L("Finances", "Finances")
ICONE_FINANCES = "game-concepts-coins_small"
DONNEE_FINANCES = "club.FinancialStatus.DisplayValue"
PERSO_SOURCE = "ClubInfoTile_4x4"            # tuile Infos du club : titre traduit « Squad Personnality »
PERSO_TITRE_FM = "Squad Personnality"        # (texte d'aperçu anglais de FM, faute de frappe comprise)
ICONE_PERSO = "game-concepts-team-dynamics_small"
DONNEE_PERSO = "club.SquadPersonality"
MARKER = os.path.join(backup.BACKUP_DIR, "club_bandeau_installations.actif")
MARKER_NOTES = os.path.join(backup.BACKUP_DIR, "notes_installations.actif")   # notes_installations.MARKER
CONSTANTES = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven",
              "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]
sm.PROPRIETES.setdefault("height", (131087, 3))   # StylePropertyId Height (66 px du bandeau dans ClubSiteHeader)


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def classes(t, r):
    return t.elem(r).get("m_Classes") or []


def plain(t, model, parent, cls, index=None, name=""):
    """conteneur vide copié de model (sans enfants, sans style intégré)"""
    r = t.clone_shallow(model, parent, index)
    t.elem(r)["m_Classes"] = list(cls)
    t.elem(r)["m_RuleIndex"] = -1
    t.sd(r)["name"] = name
    t.sd(r)["name_UxmlAttributeFlags"] = 1 if name else 0
    return r


def cellule(t, model, parent, cls=()):
    c = plain(t, model, parent, ["row-direction-normal", "align-items-center"] + list(cls))
    t.styles.style(t, c, {"height": HAUTEUR_LIGNE, "min-height": HAUTEUR_LIGNE, "flex-shrink": 0})
    return c


def fourchette(texte):
    a, _, b = texte.partition("-")
    return int(a), int(b or a)


class Bandeau:
    """repères et modèles du bandeau de FM, et sources des copies"""

    def __init__(self, t):
        self.t = t
        self.founded = first(t, lambda r: t.name(r) == "Founded")
        self.pro = first(t, lambda r: t.name(r) == "ProfessionalStatus")
        self.stadium = first(t, lambda r: t.name(r) == "Stadium")
        self.nickname = first(t, lambda r: t.name(r) == "Nickname")
        self.bande = t.parent.get(self.founded)
        f = self.founded
        self.label = f and first(t, lambda r: typ(t, r) == "SIText" and "global-text-secondary" in classes(t, r), f)
        self.valeur = f and first(t, lambda r: (t.binding(r, "TextBinding") or "") == "club.YearFounded", f)
        self.ligne = t.parent.get(self.valeur)
        self.trait = next((r for r in t.children(self.bande) if t.elem(r).get("m_TemplateAlias")
                           == "layout-divider-solid-vertical"), None) if self.bande else None
        self.vs, self.vis = visible_model()
        self.ss, self.star = src_tree(ETOILES_SOURCE)
        self.star = self.ss and first(self.ss, lambda r: typ(self.ss, r) == "FMStarRatingTemp")
        self.ts, _ = src_tree(TEXTES_SOURCE)

    def manque(self):
        # « Stadium » facultatif : retiré du bandeau par FM (MAJ du 2026-11-12)
        noms = ["founded", "pro", "nickname", "bande", "label", "valeur", "ligne", "trait", "vis"]
        if ETOILES:
            noms.append("star")
        if STADE:
            noms.append("ts")
        return [n for n in noms if getattr(self, n) is None]

    def bloc(self, index, nom, parent=None):
        """section ajoutée dans la bande : SIVisible « fenêtre large » comme #ProfessionalStatus, ou conteneur"""
        t = self.t
        parent = self.bande if parent is None else parent
        if SEULEMENT_SI_LARGE:
            b = t.clone_shallow(self.pro, parent, index)
            t.elem(b)["m_RuleIndex"] = -1
            t.sd(b)["name"], t.sd(b)["name_UxmlAttributeFlags"] = nom, 1 if nom else 0
            return b
        return plain(t, self.founded, parent, classes(t, self.pro), index, nom)

    def mode_visible(self, parent, index, nom, op, cls):
        """SIVisible « mode d'affichage <op> 0 » (OP_EGAL : Large seulement, OP_SUPERIEUR : Medium / Small)"""
        t = self.t
        v = new_visible(t, self.vs, self.vis, parent, index, nom,
                        make_binding(self.vs.sd(self.vis)["Binding"], op, [MODE_AFFICHAGE], 0), cls)
        t.elem(v)["m_RuleIndex"] = -1
        t.sd(v)["name_UxmlAttributeFlags"] = 1
        return v

    def bloc_hors_large(self, index, nom):
        """section cachée en mode Large : SIVisible (mode > 0) nommé nom, section dedans (renvoyée) ; son trait est
        posé dedans par reordonner()"""
        v = self.mode_visible(self.bande, index, nom, OP_SUPERIEUR, classes(self.t, self.pro))
        return self.bloc(None, "", v)

    def etoiles(self, parent, mini, maxi):
        t = self.t
        e = t.clone(self.star, parent, None, src=self.ss)
        no_styles(t, e)
        t.elem(e)["m_Classes"] = ["margin-left-global-gap-small"]
        sd = t.sd(e)
        sd["name"] = NOM_ETOILES
        sd["MinBinding"] = {"m_path": mini}
        sd["MaxBinding"] = {"m_path": maxi}

    def grille(self, bloc, colonnes, avec_etoiles):
        """colonnes de lignes « nom  valeur  (étoiles) », séparées par un trait ; renvoie une erreur ou None"""
        t = self.t
        g = plain(t, self.ligne, bloc, ["row-direction-normal", "align-items-center"])
        for k, colonne in enumerate(colonnes):
            if k:
                t.clone(self.trait, g)
            col = plain(t, self.ligne, g, ["row-direction-normal"])
            noms = plain(t, self.ligne, col, ["margin-right-global-gap-large"])
            notes = plain(t, self.ligne, col, [])
            stars = plain(t, self.ligne, col, []) if avec_etoiles else None
            for nom, kind, chemin in colonne:
                c = cellule(t, self.ligne, noms)
                txt = text_static(t, self.label, c, nom)
                t.elem(txt)["m_Classes"] = [x for x in classes(t, txt) if not x.startswith("margin-")]
                c = cellule(t, self.ligne, notes, ["justify-content-end"] if kind != "fm" else [])
                if kind == "fm":
                    src = first(self.ts, lambda r: self.ts.name(r) == chemin)
                    if src is None:
                        return f"{nom} : texte {chemin} introuvable dans {TEXTES_SOURCE}"
                    v = t.clone(src, c, None, src=self.ts)
                    no_styles(t, v)
                    t.elem(v)["m_Classes"] = list(classes(t, self.valeur))
                    continue
                v = t.clone(self.valeur, c)
                if kind == "exacte":
                    if not exacte(t, c, chemin):
                        return f"{nom} : modèles de la note exacte introuvables"
                elif not paliers(t, v, chemin, rating_values()):
                    return f"{nom} : modèle de visibilité introuvable"
                elif chemin == ENTRAINEMENT:   # v11 : note exacte (objet éditeur du club), fourchette en repli
                    note_editeur(t, [r for r in t.children(c) if t.name(r) == NOM_PALIER], LISTE_EDITEUR)
                if not stars:
                    continue
                c = cellule(t, self.ligne, stars)
                if kind == "exacte":
                    self.etoiles(c, chemin + ".MinValue", chemin + ".MaxValue")
                    continue
                fourchettes = []
                for code, texte in rating_values():
                    if code < 0:
                        continue
                    a, b = fourchette(texte)
                    p = new_visible(t, self.vs, self.vis, c, None, "",
                                    equal_binding(self.vs.sd(self.vis)["Binding"], chemin, code),
                                    ["row-direction-normal", "align-items-center"])
                    self.etoiles(p, "const." + CONSTANTES[a], "const." + CONSTANTES[b])
                    fourchettes.append(p)
                if chemin == ENTRAINEMENT:   # v12 (le joueur) : étoiles de la note exacte, celles de la fourchette en repli
                    note_editeur(t, fourchettes, LISTE_EDITEUR, lambda parent, note: self.etoiles(parent, note, note))
        return None

    def section(self, bloc, titre, icone, donnee, apercu):
        """copie de la section « Surnom » : titre (texte fixe, ou liaison de titre traduit de FM), icône, valeur"""
        t = self.t
        s = t.clone(self.nickname, bloc, 0)
        t.sd(s)["name"] = ""
        lab = first(t, lambda r: typ(t, r) == "SIText" and "global-text-secondary" in classes(t, r), s)
        val = first(t, lambda r: (t.binding(r, "TextBinding") or "").lower() == "club.mainteam.nickname", s)
        ico = first(t, lambda r: any(c.startswith("game-concepts-fans") for c in classes(t, r)), s)
        if None in (lab, val, ico):
            return "section Surnom : éléments introuvables"
        if isinstance(titre, str):
            new = text_static(t, lab, t.parent[lab], titre, t.children(t.parent[lab]).index(lab))
            t.remove(lab)
            if not new:
                return "titre introuvable"
        else:   # liaison de texte d'un titre FM (traduit dans la langue du jeu)
            t.sd(lab)["TextBinding"] = copy.deepcopy(titre)
            t.sd(lab)["text"], t.sd(lab)["text_UxmlAttributeFlags"] = "", 0
            t.sd(lab)["DebugDisplay"] = "Personnalité de l'effectif"
        t.elem(ico)["m_Classes"] = [icone if c.startswith("game-concepts-fans") else c for c in classes(t, ico)]
        t.sd(ico)["name"] = icone
        t.sd(val)["TextBinding"]["m_direct"]["Path"]["m_path"] = donnee
        t.sd(val)["DebugDisplay"] = apercu
        return None

    def finances(self, bloc):
        """titre Finances, icône pièces, état des finances"""
        return self.section(bloc, TITRE_FINANCES, ICONE_FINANCES, DONNEE_FINANCES, "Prospère")

    def personnalite(self, bloc):
        """titre traduit « Personnalité de l'effectif » (repris de la tuile Infos du club), icône dynamique d'équipe"""
        s, _ = src_tree(PERSO_SOURCE)
        titre = s and first(s, lambda r: s.sd(r).get("DebugDisplay") == PERSO_TITRE_FM)
        if titre is None:
            return f"titre « {PERSO_TITRE_FM} » introuvable dans {PERSO_SOURCE}"
        return self.section(bloc, s.sd(titre)["TextBinding"], ICONE_PERSO, DONNEE_PERSO, "Équilibrée")


def est_trait(t, r):
    return t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical"


def cle(t, r):
    n = t.name(r)
    noms = {NOMS["installations"]: "installations", NOMS["stade"]: "prix", NOMS["finances"]: "finances",
            NOMS["personnalite"]: "personnalite", NOMS["surnom"]: "surnom"}
    if n in SECTIONS_FM or n in noms:
        return SECTIONS_FM.get(n) or noms[n]
    if t.binding(r) == LIAISON_FEMININE:
        return "feminine"
    return None


def reordonner(t, b):
    """sections de la bande dans l'ordre ORDRE ; un trait entre chaque section visible côte à côte.
    Traits de FM : dans la section (Forme, Niveau pro, nos blocs : après ; Équipe féminine : avant) ou juste après
    elle (Établi en, Stade, Surnom ; Réputation, dernière chez FM, n'en a pas)."""
    unites = []   # [clé, élément, trait voisin]
    for c in t.children(b.bande):
        if est_trait(t, c):
            if unites and unites[-1][2] is None:
                unites[-1][2] = c
            else:
                t.remove(c)
            continue
        unites.append([cle(t, c), c, None])
    rang = {k: i for i, k in enumerate(ORDRE)}
    unites.sort(key=lambda u: (u[0] == "feminine", rang.get(u[0], len(ORDRE))))
    # sections qui peuvent être cachées (SIVisible) : Forme (FM la cache sans matchs joués), Finances en mode Large.
    # En fin de bande (seulement des cachables jusqu'à l'équipe féminine), leur trait est mis devant elles, dedans :
    # il disparaît avec elles (sinon deux traits côte à côte avant l'équipe féminine).
    caches = {"forme"} | ({"finances"} if FINANCES and FINANCES_HORS_LARGE else set()) \
        | ({"surnom"} if SURNOM_HORS_LARGE else set())

    def fin_cachable(j):
        return j < len(unites) and all(u[0] in caches for u in unites[j:] if u[0] != "feminine")

    seq = []
    for i, (k, r, voisin) in enumerate(unites):
        interne = k != "feminine" and t.children(r) and est_trait(t, t.children(r)[-1])
        suite = i + 1 < len(unites) and unites[i + 1][0] != "feminine" and not fin_cachable(i + 1)
        seq.append(r)
        if k in caches:
            if voisin is not None:
                t.remove(voisin)
            if fin_cachable(i):
                if interne:
                    move(t, t.children(r)[-1], r, 0)
                else:
                    t.clone(b.trait, r, 0)
            elif suite and not interne:
                t.clone(b.trait, r)
            elif interne and not suite:
                t.remove(t.children(r)[-1])
            continue
        if k == "feminine":
            continue
        if suite:
            if voisin is None and not interne:
                voisin = t.clone(b.trait, b.bande)
                t.sd(voisin)["name"], t.sd(voisin)["name_UxmlAttributeFlags"] = NOM_TRAIT, 1
            if voisin is not None:
                seq.append(voisin)
        else:   # dernière avant l'équipe féminine (qui a son trait) : pas de trait en double
            if voisin is not None:
                t.remove(voisin)
            if interne:
                t.remove(t.children(r)[-1])
    t.elem(b.bande)["m_Children"] = [{"rid": r} for r in seq]
    for r in seq:
        t.parent[r] = b.bande
    return [u[0] or "?" for u in unites]


def construire(t):
    b = Bandeau(t)
    if b.manque():
        return [f"bandeau : repères ou modèles FM introuvables ({', '.join(b.manque())}), ignoré"]
    msgs = []
    # installations : 1re section de la bande (à gauche de « Forme »), trait après
    if avec_installations():
        bloc = b.bloc(0, NOMS["installations"])
        err = b.grille(bloc, INSTALLATIONS, ETOILES)
        if err:
            return [err + ", ignoré"]
        t.clone(b.trait, bloc)
        msgs.append("installations" + (" avec étoiles" if ETOILES else ""))
    else:
        msgs.append("sans installations (option de l'app ou notes /20 coupées)")
    # stade puis finances : juste après « Stade » et son trait
    # (sans section Stade chez FM : à la fin, l'ordre final est fait par reordonner())
    index = t.children(b.bande).index(b.stadium) + 2 if b.stadium is not None else len(t.children(b.bande))
    if STADE:
        bloc = b.bloc(index, NOMS["stade"])
        err = b.grille(bloc, STADE, False)
        if err:
            return [err + ", ignoré"]
        t.clone(b.trait, bloc)
        index += 1
        msgs.append("stade (" + ", ".join(nom for col in STADE for nom, _, _ in col) + ")")
    if FINANCES:
        bloc = b.bloc_hors_large(index, NOMS["finances"]) if FINANCES_HORS_LARGE else b.bloc(index, NOMS["finances"])
        err = b.finances(bloc)
        if err:
            return [err + ", ignoré"]
        if not FINANCES_HORS_LARGE:
            t.clone(b.trait, bloc)
        msgs.append("finances" + (" (hors mode Large)" if FINANCES_HORS_LARGE else ""))
    if PERSONNALITE:   # placée par reordonner() (ORDRE)
        bloc = b.bloc(len(t.children(b.bande)), NOMS["personnalite"])
        err = b.personnalite(bloc)
        if err:
            return [err + ", ignoré"]
        t.clone(b.trait, bloc)
        msgs.append("personnalité de l'effectif")
    if not STADE_FM and b.stadium is not None:   # son trait voisin est rattaché / retiré par reordonner()
        t.remove(b.stadium)
        msgs.append("section Stade de FM retirée")
    if SURNOM_HORS_LARGE:   # après Finances / Personnalité (copiées de #Nickname) ; son trait : reordonner()
        i = t.children(b.bande).index(b.nickname)
        move(t, b.nickname, b.mode_visible(b.bande, i, NOMS["surnom"], OP_SUPERIEUR, classes(t, b.pro)))
        msgs.append("surnom hors mode Large")
    ordre = reordonner(t, b)
    if TEXTE_REDUIT:
        n = reduire_texte(t, b)
        msgs.append(f"texte réduit ({n})" + (" en mode Large" if TEXTE_REDUIT_LARGE_SEUL else ""))
    if not MAILLOTS_EN_HAUT:
        msgs.append(retirer_maillots(t))
    return ["bandeau du club : " + ", ".join(msgs) + (" (fenêtre large)" if SEULEMENT_SI_LARGE else ""),
            "ordre : " + " | ".join(ordre)]


def reduire_texte(t, b):
    """classes de texte de la bande (sections FM et nos ajouts) remplacées selon TEXTE_REDUIT ; un SIText sans classe
    de texte (valeur de « Niveau de professionnalisme ») reçoit la plus petite. TEXTE_REDUIT_LARGE_SEUL : le texte
    d'origine reste dans un SIVisible « mode > 0 », sa copie réduite dans un SIVisible « mode == 0 » juste après.
    Les sections cachées en mode Large (Finances) ne sont pas touchées."""
    caches = {r for r in t.children(b.bande) if t.name(r) in (NOMS["finances"], NOMS["surnom"])}
    cibles = []
    for sec in t.children(b.bande):
        if sec in caches:
            continue
        for r in t.walk(sec):
            cls = classes(t, r)
            if typ(t, r) == "SIText" and not any(c.startswith("body-") for c in cls):
                cibles.append((r, cls + ["body-sm-regular"]))
            elif typ(t, r) == "SIText" and any(c in TEXTE_REDUIT for c in cls):
                cibles.append((r, [TEXTE_REDUIT.get(c, c) for c in cls]))
    for r, petit in cibles:
        if not TEXTE_REDUIT_LARGE_SEUL:
            t.elem(r)["m_Classes"] = petit
            continue
        p = t.parent[r]
        i = t.children(p).index(r)
        cls = ["row-direction-normal", "align-items-center"]
        autres = b.mode_visible(p, i, NOM_TEXTE_MODE, OP_SUPERIEUR, cls)
        large = b.mode_visible(p, i + 1, NOM_TEXTE_MODE, OP_EGAL, cls)
        move(t, r, autres)
        t.elem(t.clone(r, large))["m_Classes"] = petit
    return len(cibles)


def retirer_maillots(t):
    """les 3 maillots à côté du nom : images liées à club.mainteam.Kit*, dans deux SIVisible (pas petit, pas téléphone)"""
    img = first(t, lambda r: typ(t, r) == "SIImage" and b"KitHome" in bytes(
        ((t.sd(r).get("Binding") or {}).get("m_visualFunction") or {}).get("m_inputs", {}).get("m_variable", {})
        .get("m_argumentBytes") or []))
    if img is None:
        return "maillots introuvables (déjà retirés ?)"
    r = t.parent[img]
    while typ(t, t.parent[r]) == "SIVisible":
        r = t.parent[r]
    t.remove(r)
    return "maillots retirés"


def avec_installations():
    return INSTALLATIONS_OPTION and (not INSTALLATIONS_SI_NOTES or os.path.exists(MARKER_NOTES))


def attendus():
    return ({NOMS["installations"]} if avec_installations() else set()) | ({NOMS["stade"]} if STADE else set()) | ({NOMS["finances"]} if FINANCES else set()) \
        | ({NOMS["personnalite"]} if PERSONNALITE else set()) | ({NOMS["surnom"]} if SURNOM_HORS_LARGE else set())


def blocs(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def original(bundle, obj):
    """modèle tel qu'à l'origine (sauvegarde des originaux), ou None"""
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    env = UnityPy.load(backup.backup_path(bundle))
    o = next((o for o in env.objects if o.path_id == obj.path_id), None)
    return o.read_typetree() if o is not None else None


def ouvrir(depart_original=False):
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        return None, None, None, None
    if depart_original:   # on refait tout à partir du modèle d'origine (ordre et traits de FM compris)
        tt = original(bundle, obj) or tt
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    return bundle, obj, tt, t


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    nb.save_all()


def cmd_appliquer():
    bundle, obj, tt, t = ouvrir()
    if tt is None:
        print(f"{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    old = blocs(t)
    msgs = []
    if {t.name(r) for r in old if not t.name(r).startswith(PREFIXE + "Trait")} != attendus():
        bundle, obj, tt, t = ouvrir(depart_original=True)
        for r in blocs(t):   # pas de sauvegarde d'origine : on retire au moins nos blocs
            t.remove(r)
        msgs = construire(t) + (["ancienne version remplacée"] if old else [])
    for m in msgs or ["déjà appliqué"]:
        print(f"{MODELE} : {m}")
    if [m for m in msgs if "introuvable" not in m]:
        enregistrer(bundle, obj, tt, t)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    bundle, obj, tt, t = ouvrir()
    old = blocs(t) if t else []
    if not old:
        print("rien à retirer")
        return
    orig = original(bundle, obj)
    if orig is not None:   # remet aussi l'ordre et les traits de FM
        obj.save_typetree(orig)
        nb._dirty.add(bundle)
        nb.save_all()
        print(f"{MODELE} : remis d'origine (ajouts retirés, ordre de FM)")
        return
    for r in old:
        if t.name(r).startswith(f"{PREFIXE}Surnom"):   # #Nickname de FM ressorti de notre SIVisible
            for c in list(t.children(r)):
                if t.name(c) == "Nickname":
                    move(t, c, t.parent[r], t.children(t.parent[r]).index(r))
        t.remove(r)
    enregistrer(bundle, obj, tt, t)
    print(f"{MODELE} : ajouts du bandeau retirés (pas de sauvegarde d'origine : ordre laissé tel quel)")


def cmd_etat():
    _, _, tt, t = ouvrir()
    if tt is None:
        print(f"{MODELE} : introuvable")
        return
    old = [t.name(r) for r in blocs(t)]
    print(f"{MODELE} : " + (f"appliqué ({', '.join(old)} ; version actuelle v{VERSION})" if old else "d'origine"))
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
            print("bandeau du club : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
