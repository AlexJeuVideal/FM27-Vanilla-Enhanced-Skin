"""Panneau du bas de la page club (Vue d'ensemble, tous les clubs, fenêtre large) réorganisé en 3 colonnes.

  Équipe première       | Maillots (toute la largeur)        | Actualités (pas en mode Défaut)
  ---------------       | Stade : photo en fond, nom + ville | ----------
  Budgets               | en haut, 4 cases en bas            | Historique des transferts
  Finances (pas Défaut) | Légendes / Grands noms / Préférés  |
                        | Affiliations                       |

Modèle touché : ClubSiteBlock (le panneau en fenêtre large ; les versions MidRes / LowRes ne sont pas touchées).
- gauche / droite : même largeur (LARGEUR_COTES) ; le milieu prend le reste et défile de haut en bas si besoin ;
- blocs du milieu = modèles FM inclus tels quels ou recopiés (ceux de la page Infos / Installations du club) :
  KitsBlock, ClubAffiliatesBlockCompact, ClubFacilitiesStadiumBlock, ClubInfoLegendsBlock.
- v14 (2026-11-12, validée en jeu comme essai_image_stade v9) : Stade avec photo (dossier graphics, commun\\
  stades_photos.py) ; Budgets + Finances en bas à gauche à la place d'« À propos du club ».
  (Option club_stade photo / classique supprimée en v18 : la photo du stade est toujours là.)
- v15 (2026-11-12, essai_stade_defaut v3 validé en jeu) : club SANS photo -> stade générique, sièges à la couleur
  du bandeau du club. Sous la photo du club (qui le cache quand elle existe) : aplat couleur du club (échantillon de
  couleur de FM) puis image fixe du jeu (texture posée par commun\\fonds_jeu.py, seul écrivain du bundle des fonds).
- v16 (2026-11-12) : en bas à gauche, onglets Budgets | Finances | À propos (TabGroup de FM recopié de
  ClubBoardCompactBlock : le contenu change sur place) ; l'option club_gauche est supprimée.
- v17 (2026-11-12, v16 validée en jeu) : Budgets plus serré en mode Large (2e copie, LARGE_*).
- v18 (2026-11-12) : option club_stade supprimée (stade photo obligatoire) ; mode Large : maillots réduits
  (MAILLOTS_ECHELLE_LARGE, 2e copie du bloc) et stade plus haut (STADE_HAUTEUR_DEFAUT).
- v19 (2026-11-12) : Affiliations retirées du milieu.
- v22 (2026-11-12) : nom du stade cliquable -> écran Infrastructures du club (STADE_ECRAN).
- v23 (2026-11-12) : le bouton du nom sans fond ni bordure (cadre clair vu en jeu en v22).
- v24 (2026-11-12) : fondu en couches empilées (retiré en v25 : marches visibles en jeu).
- v25 (2026-11-12) : bandes du haut / bas d'origine, moins sombres (STADE_VOILE 0.30 au lieu de 0.55).
- v26 (2026-11-12) : STADE_VOILE 0.10.
- v27 (2026-11-12) : STADE_VOILE 0.20 (demande du joueur, après la v26 vue en jeu).
- v28 (2026-11-12) : STADE_VOILE 0.25 (demande du joueur, après la v27 vue en jeu).
- v29 (2026-11-12) : onglets du bas à gauche dans l'ordre À propos | Budgets | Finances (À propos ouvert d'office).
- v30 (2026-11-12) : l'actu à la une revient (partait avec la liste des articles) ; milieu sans barre de défilement.
- v31 (2026-11-05, essai) : 4e onglet en bas à gauche, Direction = avis de la direction sur notre travail (page de
  notre club seulement).
Appliquer repart toujours du modèle d'origine sauvegardé ; retirer le remet.
(Les maillots du bandeau du haut sont retirés par club_bandeau_installations.py, MAILLOTS_EN_HAUT.)

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
from arbre import Tree, Styles  # noqa: E402
import notes_installations as ni  # noqa: E402
from notes_installations import first, decode_args, encode_args, _enc_varint  # noqa: E402
import stades_photos  # noqa: E402
import fonds_jeu  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
LARGEUR_COTES = 25        # % de la largeur pour la colonne de gauche ET celle de droite (le milieu prend le reste)
PART_EFFECTIF = 1.0       # gauche : hauteur Équipe première / hauteur du bas (1.0 = moitié-moitié)
PART_ACTUALITES = 1.0     # droite : hauteur Actualités / hauteur Transferts (1.0 = moitié-moitié)
ACTUALITES_EN_DEFAUT = False   # False : en mode d'affichage Défaut, pas d'Actualités, les Transferts prennent la colonne
# v13 (demande du 2026-11-12) : Actualités = seulement l'actu à la une (tuile FM) ; « More Stories » + liste des autres
# articles retirés, le bloc prend sa hauteur naturelle et les Transferts dessous prennent tout le reste
ACTUALITES_UNE_SEULE = True
# milieu, de haut en bas : lignes ; une ligne = colonnes côte à côte (part de largeur, blocs l'un sous l'autre) ;
# part 0 = largeur naturelle du bloc (maillots : jamais coupés), sinon le reste est partagé selon les parts.
# Blocs : "KitsBlock", "ClubAffiliatesBlockCompact" (modèles FM tels quels), "ClubFacilitiesStadiumBlock",
#         "ClubInfoLegendsBlock" (recopiés pour s'étirer en largeur), "ClubInfoFinancesBlock", "Budgets" (solde +
#         budget transferts + budget salaires : morceaux des tuiles FM Finances / Budgets ; v14 : à gauche)
MILIEU = [
    [(1, ["KitsBlock"])],
    [(1, ["ClubFacilitiesStadiumBlock"])],
    [(1, ["ClubInfoLegendsBlock"])],
]   # v19 : Affiliations (ClubAffiliatesBlockCompact) retirées à la demande du joueur
TITRE_BUDGETS = L("Budgets", "Budgets")   # texte fixe (langue.py, choix 106)
# --- Stade avec photo ---
STADE_HAUTEUR = 500           # px, Détaillé / Condensé (photo 16:9 recadrée : 1280 x 720)
STADE_HAUTEUR_DEFAUT = 320    # px, mode d'affichage Large (v18 : 280 + la place gagnée sur les maillots)
# mode Large : maillots plus petits (bloc FM de 228 px de haut, maillots 137 x 169 px) pour laisser la place au stade
MAILLOTS_ECHELLE_LARGE = 0.75  # None = taille de FM ; garder STADE_HAUTEUR_DEFAUT - 280 <= place gagnée (bas du stade
                               # visible sans faire défiler)
STADE_CASES = ["capacity", "surface", "pitch-condition", "year-built"]   # lignes FM du bloc Stade, de gauche à droite
# club sans photo : stade générique (images_sources\fabriquer_stade_defaut.py), sièges à cette couleur. Essai v2 :
# Team.Club.PrimaryColor = parfois la couleur du texte (Chelsea jaune, Arsenal blanc) -> couleur du bandeau
STADE_COULEUR = "Team.Club.TitlebarBackgroundColour"
STADE_VOILE = (0, 0, 0, 0.25)  # fond sombre sous les textes (v26 : 0.55 -> 0.10 ; v27 : 0.20 ; v28 : 0.25, demandes du joueur)
STADE_TAILLE_NOM, STADE_TAILLE_VALEUR = 26, 18   # px
# clic sur le nom du stade : écran Infrastructures du club (ClubFacilitiesCard, comme le titre de la tuile FM
# Installations, ClubFacilitiesTile_4x4)
STADE_ECRAN = "6ac245609970052488a498460d16d4f7"
STADE_ECRAN_PARAMS = [("club", "club")]
# --- en bas à gauche : onglets (texte fixe, langue.py), le 1er est ouvert à l'arrivée sur la page ---
ONGLETS = [("APropos", L("À propos", "About")), ("Budgets", L("Budgets", "Budgets")),
           ("Finances", L("Finances", "Finances")),
           ("Direction", L("Direction", "Board"))]   # le 1er est ouvert d'office
# v31 : onglet Direction = avis de la direction (bloc FM de l'écran Retours), page de notre club seulement
DIRECTION_SOURCE = "FeedbackPerformanceClubBoardBlock"
DIRECTION_PARAMS = {"team": "human.team", "teamconfidence": "human.team.TeamConfidence"}
ONGLETS_SOURCE = "ClubBoardCompactBlock"   # tuile FM avec onglets (TabGroup + #TabButtons + SwitchElement #TabsContent)
SERRE_TRAIT, SERRE_MARGE, SERRE_LIGNE = 6, 2, 24   # px : marges des traits, sous les titres, hauteur ligne Finances
SERRE_SOLDE = 20              # px, montant du solde
# mode d'affichage Large (interface plus grosse, la rangée d'onglets prend de la place) : Budgets encore plus serré
LARGE_SOLDE, LARGE_TRAIT = 16, 3   # px : montant du solde, marges des traits
LARGE_TEXTES = {"body-md": "body-sm", "body-md-strong": None, "body-large-16px-bold": "body-md-strong"}   # None = retirée
SANS_BULLES = True        # blocs du milieu sans leur cadre FM (bordure arrondie + fond) : séparés par des traits
# maillots qui suivent la place : largeur = % de leur emplacement (1/3 ou 1/2 s'il n'y a pas de 3e maillot), hauteur
# selon les proportions du maillot. None = taille fixe de FM (137 x 169 px)
MAILLOTS_LARGEUR = None   # % de l'emplacement (essai v7 à 70 : images invisibles, bloc immense -> désactivé)
MAILLOTS_MAX = 280        # px, largeur maximale d'un maillot (grands écrans)
# =====================================================================================================

MODELE = "ClubSiteBlock"
BARRE_CACHEE = 2          # ScrollerVisibility de Unity : 0 auto, 1 toujours, 2 cachée
OP_EGAL_CLUB, OP_DIFFERENT_CLUB = 2, 5   # ComparisonOperator de FM (=, ≠) : onglets de notre club / des autres (v32)
VERSION = f"35{SUFFIXE}"   # -en : langue ; v20 / v21 = essais retirés (peut-être encore dans le jeu) : sautés
PREFIXE = "UIPickerClubBas"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"       # colonne du milieu : repère « déjà appliqué »
MARKER = os.path.join(backup.BACKUP_DIR, "club_page_bas.actif")
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Défaut, 1 Détaillé, 2 Condensé (lisible sur la page club)
OP_SUPERIEUR = 4   # opérateur de comparaison FM « > » (déjà utilisé par notes_installations.exacte)
DESCRIPTIONS = {   # modèle FM inclus tel quel -> description de tuile qui donne son identifiant (GUID Addressables)
    "ClubAffiliatesBlockCompact": "ClubAffiliatesCompactBlockDescription",
}
CLASSES_CADRE = {"border-color-layout-modules-block-border-colour", "siblock-border"}   # cadres des blocs FM
LEGENDES_COLONNES = ["legends-frame", "icons-frame", "favoured-personel-frame"]
SOLDE_SOURCE, SOLDE = "ClubFinancesTile_4x4", "OveralFrame"                 # solde (titre FM traduit + montant)
BUDGETS_SOURCE, BUDGETS = "RecruitmentBudgetsTile_4x4", ["TransferBudget-Frame", "Wage-Frame"]
TUILES = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")   # lu seulement
sm.PROPRIETES.setdefault("height", (131087, 3))
sm.PROPRIETES.setdefault("width", (131105, 3))   # StylePropertyId Width (27 % / 25 % / 20 % chez FM)
sm.PROPRIETES.setdefault("height-auto", (131087, 1))       # Height en mot-clé (StyleValueKeyword Auto = 2)
sm.PROPRIETES.setdefault("max-height-none", (131094, 1))   # MaxHeight en mot-clé (None = 6)
sm.PROPRIETES.setdefault("max-height", (131094, 3))
sm.PROPRIETES.setdefault("flex-basis-auto", (131082, 1))   # FlexBasis en mot-clé (Auto = 2)
for _k, _v in {"margin-top": (131093, 3), "margin-bottom": (131090, 3), "position": (131102, 7),
               "left": (131089, 3), "top": (131104, 3), "right": (131103, 3), "bottom": (131080, 3),
               "flex-direction": (131083, 7), "justify-content": (131088, 7), "align-items": (131073, 7),
               "font-size": (65537, 3), "-unity-text-align": (65546, 7), "display": (131081, 1),
               "margin-left": (131091, 3), "margin-right": (131092, 3), "padding-bottom": (131098, 3),
               "padding-left": (131099, 3), "padding-right": (131100, 3), "padding-top": (131101, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
MOT_AUTO, MOT_AUCUN = 2, 6
FLEX_GROW = 131084            # StylePropertyId FlexGrow
OP_EGAL = 2                   # opérateur de comparaison FM « == » (notes_installations.equal_binding)
STADE_NOM = f"{PREFIXE}Stade"
BUDGETS_NOM = f"{PREFIXE}Budgets"
STADE_PLACES = L(" places", " seats")
# capacité : nombre seul, liaison directe (selectedstadium.Capacity = long texte de FM ; le texte traduit
# « [%number#1-long] » de FM ne recevait rien ici)
STADE_CAPACITE = "selectedstadium.TotalCapacity"
STADE_EN_TETE = ["container-header", "layout-divider-solid-horizontal-1"]   # titre Stade + pastille : cachés
STADE_IMAGE_SOURCE = "AboutClubTile_4x8"    # SIImage du logo du club (chargeur d'images FM, fonction 7a35874b)
STADE_TYPE_IMAGE = 1          # ResourceType Compétition : graphics/pictures/comp/<id du club>/logo (stades_photos.py)
# v33 ESSAI (2026-11-10) : photo par id de STADE, format des packs d'internet (sortitoutsi : pictures/stadium/<id>/
# background). Couche au-dessus de la photo du club : chargeur de FM, type 12 (Unsupported : jamais essayé),
# texte « background », chemin selectedstadium.ObjectLookupData. None = pas de couche.
STADE_ESSAI_ID = None   # v34 (12, "background", "selectedstadium.ObjectLookupData") : ÉCHEC en jeu (générique)
STADE_DEFAUT_GUID ="1f813cf5a178ab443a2caf65727d79aa"   # texture « caraboa-cup-skin-test-min » (fonds_jeu.py)
COULEUR_SOURCE = ("ColourSwatch", "d5d001b1")   # échantillon de couleur de FM : SIImage, fond = couleur liée
KIT_RATIO = 137.545 / 168.964   # largeur / hauteur du maillot (.kits-t-shirt de FM)
FITTER_SOURCE = "KitShirt"      # modèle FM où un maillot est dans un SIAspectRatioFitter (#RatioFitter)
POURCENT = lambda v: {"unit": 2, "value": float(v)}  # noqa: E731
GRANDIR = lambda g: {"flex-grow": g, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "min-width": 0}  # noqa: E731


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def guids():
    """{modèle: GUID} lus dans les descriptions de tuiles de FM"""
    wanted = {d: m for m, d in DESCRIPTIONS.items()}
    out = {}
    env = UnityPy.load(TUILES)
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in wanted:
            for c in o.read_typetree().get("<Configurations>k__BackingField") or []:
                out[wanted[n]] = c["AssetRef"]["m_AssetGUID"]
                break
    return out


def _arguments(sd, motif=b"GraphicsUtils+ResourceType"):
    """dictionnaires d'arguments de fonctions FM (m_argumentBytes) qui contiennent motif (défaut : chargeur d'images)"""
    trouves = []

    def fouille(x):
        if isinstance(x, dict):
            ab = x.get("m_argumentBytes")
            if ab and motif in bytes(ab):
                trouves.append(x)
            for v in x.values():
                fouille(v)
        elif isinstance(x, list):
            for v in x:
                fouille(v)
    fouille(sd)
    return trouves


def classes(t, r):
    return t.elem(r).get("m_Classes") or []


def centrer(t, r, cls):
    """remplace la classe align-items-* de FM par cls"""
    t.elem(r)["m_Classes"] = [c for c in classes(t, r) if not c.startswith("align-items-")] + [cls]


def move(t, rid, new_parent, index=None):
    old = t.parent[rid]
    t.elem(old)["m_Children"] = [k for k in t.elem(old)["m_Children"] if k["rid"] != rid]
    kids = t.elem(new_parent)["m_Children"]
    kids.insert(len(kids) if index is None else index, {"rid": rid})
    t.elem(rid)["m_Parent"] = {"rid": new_parent}
    t.parent[rid] = new_parent


class Panneau:
    def __init__(self, t):
        self.t = t
        nom = lambda n: first(t, lambda r: t.name(r) == n)  # noqa: E731
        self.team, self.about, self.transfers, self.news = (nom(n) for n in ("FirstTeam", "About", "TransferHistory",
                                                                              "News"))
        self.d1, self.d2, self.d3 = (nom(n) for n in ("Divider1", "Divider2", "Divider3"))
        self.dh = nom("Divider5")   # trait horizontal de FM (dans les transferts) : modèle des traits ajoutés
        self.row = self.team and t.parent.get(self.team)
        self.scroll = self.about and first(t, lambda r: typ(t, r) == "SIScrollView", self.about)

    def manque(self):
        return [n for n in ("team", "about", "transfers", "news", "d1", "d2", "d3", "dh", "row", "scroll")
                if getattr(self, n) is None]

    def boite(self, parent, cls, name="", index=None, model=None):
        """conteneur vide (copie sans enfants ni style de #FirstTeam, ou de model)"""
        t = self.t
        r = t.clone_shallow(model or self.team, parent, index)
        t.elem(r)["m_Classes"] = list(cls)
        t.elem(r)["m_RuleIndex"] = -1
        t.sd(r)["name"] = name
        t.sd(r)["name_UxmlAttributeFlags"] = 1 if name else 0
        return r

    def trait_h(self, parent, marge="margin-vertical-global-gap-large"):
        r = self.t.clone(self.dh, parent)
        self.t.sd(r)["name"] = ""
        self.t.elem(r)["m_Classes"] = ["layout-divider-solid-horizontal", marge]
        return r

    def trait_v(self, parent):
        r = self.t.clone(self.d1, parent)
        self.t.sd(r)["name"] = ""
        self.t.elem(r)["m_Classes"] = ["margin-horizontal-global-gap-large"]
        return r

    def modele(self, parent, alias, guid, cls=()):
        """instance d'un modèle FM (comme les traits de FM : copie de #Divider1 avec un autre alias)"""
        t = self.t
        r = t.clone_shallow(self.d1, parent)
        t.elem(r)["m_TemplateAlias"] = alias
        t.elem(r)["m_Classes"] = list(cls)
        t.elem(r)["m_RuleIndex"] = -1
        t.sd(r)["templateId"] = alias
        t.sd(r)["name"] = ""
        t.sd(r)["name_UxmlAttributeFlags"] = 0
        if not any(u.get("alias") == alias for u in t.tt.setdefault("m_Usings", [])):
            t.tt["m_Usings"].append({"alias": alias, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return r

    def source(self, model):
        """(arbre, feuille de styles) d'un autre modèle FM, ou (None, None)"""
        bundle, _, stt = nb.find_vta(model)
        return (Tree(stt), Styles(bundle, stt)) if stt is not None else (None, None)

    def copie(self, parent, s, ss, root, index=None):
        """recopie le sous-arbre root du modèle s ici (styles intégrés et modèles inclus compris)"""
        t = self.t
        r = t.clone(root, parent, index, src=s)
        t.styles.copy_from(ss, t, r)
        used = {s.elem(x).get("m_TemplateAlias") for x in s.walk(root)} - {None, ""}
        for u in s.tt.get("m_Usings") or []:
            if u.get("alias") in used and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
                t.tt["m_Usings"].append(dict(u))
        return r

    def recopie(self, parent, model):
        """tout le bloc model recopié (au lieu d'être inclus) : on peut alors changer sa mise en page ;
        SANS_BULLES : son cadre (bordure, fond) est retiré"""
        s, ss = self.source(model)
        if s is None:
            return None
        r = self.copie(parent, s, ss, s.children(s.tt["m_VisualTree"]["rid"])[0])
        if SANS_BULLES:
            t = self.t
            for x in t.walk(r):
                if CLASSES_CADRE & set(classes(t, x)):
                    t.styles.style(t, x, sm.SANS_CADRE)
        return r

    def stade(self, parent):
        """bloc Stade de FM (détaillé, avec la pastille d'état), recopié pour pouvoir retirer son cadre"""
        r = self.recopie(parent, "ClubFacilitiesStadiumBlock")
        if r is None:
            return "ClubFacilitiesStadiumBlock : introuvable"
        self.t.elem(r)["m_Classes"] = list(classes(self.t, r)) + ["flex-grow-class"]
        return None

    def finances(self, parent):
        """bloc Finances de FM ; colonne des titres plus étroite (308 px fixes chez FM)"""
        t = self.t
        r = self.recopie(parent, "ClubInfoFinancesBlock")
        vue = r and first(t, lambda x: t.name(x) == "finances-view", r)
        if vue is None:
            return "ClubInfoFinancesBlock : introuvable"
        for ligne in t.children(vue):   # titres à largeur fixe : valeurs alignées (décalées chez FM selon le texte)
            if t.children(ligne):
                t.styles.style(t, t.children(ligne)[0], {"width": POURCENT(50), "min-width": POURCENT(50),
                                                         "max-width": POURCENT(50), "flex-grow": 0, "flex-shrink": 0})
        return None

    def legendes(self, parent):
        """Légendes / Grands noms / Personnes préférées : les 3 colonnes se partagent toute la largeur"""
        t = self.t
        r = self.recopie(parent, "ClubInfoLegendsBlock")
        cols = [first(t, lambda x, n=n: t.name(x) == n, r) for n in LEGENDES_COLONNES] if r else [None]
        if None in cols:
            return "ClubInfoLegendsBlock : introuvable"
        for c in cols:
            t.styles.style(t, c, GRANDIR(1))
            centrer(t, c, "align-items-stretch")   # sinon la liste garde la largeur de son texte (noms coupés)
        return None

    def maillots(self, parent):
        """bloc Maillots de FM (640 px, maillots 180 px) étiré sur toute la largeur, chaque maillot centré"""
        t = self.t
        r = self.recopie(parent, "KitsBlock")
        cadre = r and (t.children(r) or [None])[0]
        ligne = cadre and next((x for x in t.children(cadre) if "row-direction-normal" in classes(t, x)), None)
        if ligne is None:
            return "KitsBlock : introuvable"
        t.styles.style(t, cadre, {"width": POURCENT(100), "max-width": POURCENT(100)})
        for x in t.children(ligne):
            if not t.elem(x).get("m_TemplateAlias"):   # pas les traits
                t.styles.style(t, x, {"max-width": POURCENT(100)})
                centrer(t, x, "align-items-center")
        # pas de 3e maillot : FM ne cache que le maillot (son tiers et le trait restent). L'emplacement devient
        # lui-même un SIVisible avec la condition de FM (#ThirdKitVisible) : même place et mêmes réglages que les
        # 2 autres (sinon décalé en hauteur) ; le trait d'avant est mis dans le #ThirdKitVisible vidé.
        vis = first(t, lambda x: t.name(x) == "ThirdKitVisible", ligne)
        if vis is not None:
            place = t.parent[vis]
            i = t.children(ligne).index(place)
            trait = t.children(ligne)[i - 1] if i and t.elem(t.children(ligne)[i - 1]).get("m_TemplateAlias") else None
            for k in list(t.children(vis)):
                move(t, k, place)
            # l'emplacement prend le type et les données de #ThirdKitVisible (condition comprise)
            e = t.elem(place)
            ancien = e["m_SerializedData"]["rid"]
            d = copy.deepcopy(t.refs[t.elem(vis)["m_SerializedData"]["rid"]])
            d["rid"] = t.new_rid()
            d["data"]["uxmlAssetId"] = e["m_Id"]
            d["data"]["name"], d["data"]["name_UxmlAttributeFlags"] = "", 0
            t.refs[d["rid"]] = d
            t.tt["references"]["RefIds"].append(d)
            e["m_FullTypeName"] = t.elem(vis)["m_FullTypeName"]
            e["m_SerializedData"] = {"rid": d["rid"]}
            t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r and r["rid"] != ancien]
            t.refs.pop(ancien, None)
            # #ThirdKitVisible (vide) : enveloppe du trait, à sa place dans la rangée
            if trait:
                move(t, vis, ligne, i - 1)
                move(t, trait, vis)
                t.elem(vis)["m_Classes"] = ["row-direction-normal", "align-items-start"]
            else:
                t.remove(vis)
        if MAILLOTS_LARGEUR:
            err = self.maillots_adaptes(cadre)
            if err:
                return err
        if MAILLOTS_ECHELLE_LARGE:
            return self.maillots_large(r, cadre)
        return None

    def maillots_large(self, r, cadre):
        """2 copies dans des SIVisible sur le mode d'affichage : mode Large = maillots, bloc et traits réduits"""
        t, st = self.t, self.t.styles
        s, vis = ni.visible_model()
        if vis is None:
            return "modèle de comparaison FM introuvable"
        col = t.parent[r]
        cls = classes(t, r)
        k = MAILLOTS_ECHELLE_LARGE
        for op in (OP_EGAL, OP_SUPERIEUR):
            v = ni.new_visible(t, s, vis, col, t.children(col).index(r),
                               f"{PREFIXE}MaillotsMode{op}", ni.make_binding(s.sd(vis)["Binding"], op, [MODE_AFFICHAGE], 0))
            t.elem(v)["m_RuleIndex"] = -1
            t.elem(v)["m_Classes"] = list(cls)
            st.style(t, v, {"width": POURCENT(100)})
            if op == OP_SUPERIEUR:
                move(t, r, v)
                continue
            c = t.clone(r, v)
            bloc = t.children(c)[0]   # copie de cadre
            h = round(228 - 169 * (1 - k))
            st.style(t, bloc, {"height": h, "max-height": h})
            for x in t.walk(c):
                if "kits-t-shirt" in classes(t, x):
                    st.style(t, x, {"width": round(137.545 * k), "height": round(168.964 * k)})
                    if "ScaleMode" in t.sd(x):
                        t.sd(x)["ScaleMode"] = 2   # image ajustée à sa boîte
                elif "layout-divider-solid-vertical" in classes(t, x):
                    st.style(t, x, {"height": round(170 - 169 * (1 - k))})
        return None

    def maillots_adaptes(self, cadre):
        """chaque image de maillot dans un SIAspectRatioFitter (copié de KitShirt) : largeur en % de l'emplacement,
        hauteur selon les proportions ; bandeau de couleur (Domicile...) à la même largeur ; bloc sans hauteur fixe"""
        t = self.t
        s, _ = self.source(FITTER_SOURCE)
        modele = s and first(s, lambda x: (s.elem(x).get("m_FullTypeName") or "").endswith("SIAspectRatioFitter"))
        imgs = [x for x in t.walk(cadre) if "kits-t-shirt" in classes(t, x)]
        if modele is None or not imgs:
            return "maillots : SIAspectRatioFitter ou images introuvables"
        t.styles.style(t, cadre, {"height-auto": MOT_AUTO, "max-height-none": MOT_AUCUN})
        largeur = {"width": POURCENT(MAILLOTS_LARGEUR), "max-width": MAILLOTS_MAX, "min-width": 0}
        for img in imgs:
            boite = t.parent[img]            # 180 px chez FM, marges intérieures 26 px
            place = t.parent[boite]          # emplacement du maillot (colonne : image puis bandeau)
            t.styles.style(t, boite, {**largeur, "flex-grow": 0, "flex-shrink": 0})
            f = t.clone(modele, boite, t.children(boite).index(img), src=s)
            for k in list(t.children(f)):
                t.remove(k)
            t.elem(f)["m_Classes"] = []
            t.elem(f)["m_RuleIndex"] = -1
            t.sd(f)["name"], t.sd(f)["name_UxmlAttributeFlags"] = "", 0
            t.sd(f)["AspectMode"], t.sd(f)["AspectRatio"] = 1, KIT_RATIO   # la largeur commande la hauteur
            t.styles.style(t, f, {"width": POURCENT(100)})
            move(t, img, f)
            t.sd(img)["ScaleMode"] = 2      # image ajustée à sa boîte (comme dans KitShirt)
            t.styles.style(t, img, {"width": POURCENT(100), "height": POURCENT(100), "flex-grow": 1})
            for k in t.children(place):      # bandeau Domicile / Extérieur : 180 px chez FM
                if k != boite:
                    t.styles.style(t, k, largeur)
                    for x in t.walk(k):
                        if x != k and t.elem(x).get("m_RuleIndex", -1) >= 0:
                            t.styles.style(t, x, {"width": POURCENT(100)})
        return None

    # ---------- Stade avec photo ----------
    def _boite(self, modele, parent, index=None):
        t = self.t
        r = t.clone_shallow(modele, parent, index)
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        t.elem(r)["m_Classes"] = []
        t.elem(r)["m_RuleIndex"] = -1
        return r

    def _bouton_ecran(self, parent, ecran, params):
        """bouton FM sans aspect (copie vide de #ShowTilesButton du panneau) : un clic ouvre l'écran (ui-panelids)"""
        import entrainement_equipes as ee   # ici : il importe hierarchie_pyramide, qui importe ce script
        t = self.t
        src = first(t, lambda r: t.name(r) == "ShowTilesButton" and typ(t, r) == "SIButton")
        if src is None:
            return None
        b = t.clone_shallow(src, parent)
        t.elem(b)["m_Classes"] = []
        t.elem(b)["m_RuleIndex"] = -1
        sd = t.sd(b)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{STADE_NOM}Lien", 1
        sd["Events"]["m_bytes"] = ee.evenement_ecran(ecran, params)
        sd["Events_UxmlAttributeFlags"] = 1   # sans ce drapeau FM ignore l'événement
        # v23 : sans l'aspect de bouton de Unity (fond clair + bordure autour du nom, vu en jeu en v22)
        t.styles.style(t, b, {**sm.SANS_CADRE, "padding-top": 0, "padding-bottom": 0, "padding-left": 0,
                              "padding-right": 0, "margin-left": 0, "margin-right": 0, "margin-bottom": 0})
        return b

    def _photo(self, parent, index):
        """SIImage du logo du club (AboutClubTile_4x8) recopié : id du club en type Comp (dossier graphics, voir
        stades_photos.py), en fond du bloc ; club sans photo : image transparente"""
        t = self.t
        s, _ = self.source(STADE_IMAGE_SOURCE)
        img = s and first(s, lambda r: typ(s, r) == "SIImage" and any(
            b"Club.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in _arguments(s.sd(r))))
        if not img:
            return None
        im = t.clone(img, parent, index, src=s)
        for k in list(t.children(im)):
            t.remove(k)
        t.elem(im)["m_RuleIndex"] = -1
        t.elem(im)["m_Classes"] = []
        t.sd(im)["name"], t.sd(im)["name_UxmlAttributeFlags"] = "", 0
        if "ScaleMode" in t.sd(im):
            t.sd(im)["ScaleMode"] = 1   # ScaleAndCrop : remplit le bloc, recadrée
        for x in _arguments(t.sd(im)):
            args = decode_args(x["m_argumentBytes"])
            for a in args:
                if a[0].endswith(b"GraphicsUtils+ResourceType]"):
                    a[1] = STADE_TYPE_IMAGE.to_bytes(4, "little")
                elif a[0] == b"SI.VisualScripting.StringVisualArg":
                    a[1] = b"\x00"
                elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                    chemin = a[1][2:].decode().replace("Club.", "Team.Club.", 1).encode()
                    a[1] = b"\x01" + _enc_varint(len(chemin)) + chemin
            x["m_argumentBytes"] = encode_args(args)
        t.styles.style(t, im, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0,
                               "width": POURCENT(100), "height": POURCENT(100)})
        return im

    def _photo_stade(self, parent, index):
        """v33 ESSAI : copie de _photo, chargée par l'id du stade affiché (STADE_ESSAI_ID : type, texte, chemin)"""
        typ_img, texte, chemin = STADE_ESSAI_ID
        im = self._photo(parent, index)
        if im is None:
            return None
        t = self.t
        for x in _arguments(t.sd(im)):
            args = decode_args(x["m_argumentBytes"])
            for a in args:
                if a[0].endswith(b"GraphicsUtils+ResourceType]"):
                    a[1] = typ_img.to_bytes(4, "little")
                elif a[0] == b"SI.VisualScripting.StringVisualArg":
                    a[1] = b"\x01" + _enc_varint(len(texte)) + texte.encode()
                elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                    a[1] = b"\x01" + _enc_varint(len(chemin)) + chemin.encode()
            x["m_argumentBytes"] = encode_args(args)
        t.sd(im)["name"], t.sd(im)["name_UxmlAttributeFlags"] = f"{STADE_NOM}EssaiId", 1
        return im

    def stade_defaut(self, cadre, photo):
        """sous la photo du club : aplat couleur du club (SIImage de l'échantillon de couleur de FM, fonction
        d5d001b1) puis image fixe du jeu (stade générique aux sièges ajourés, texture de fonds_jeu.py)"""
        t, st = self.t, self.t.styles
        i = t.children(cadre).index(photo)
        s, _ = self.source(COULEUR_SOURCE[0])
        src = s and first(s, lambda r: ((s.sd(r).get("Binding") or {}).get("m_visualFunction") or {})
                          .get("m_target", {}).get("m_guid", "").startswith(COULEUR_SOURCE[1]))
        if not src:
            return f"{COULEUR_SOURCE[0]} : échantillon de couleur introuvable"
        aplat = t.clone(src, cadre, i, src=s)
        for k in list(t.children(aplat)):
            t.remove(k)
        t.elem(aplat)["m_RuleIndex"] = -1
        t.elem(aplat)["m_Classes"] = []
        t.sd(aplat)["name"], t.sd(aplat)["name_UxmlAttributeFlags"] = "", 0
        vf = t.sd(aplat)["Binding"]["m_visualFunction"]
        args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                a[1] = b"\x01" + _enc_varint(len(STADE_COULEUR)) + STADE_COULEUR.encode()
        vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        plein = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0,
                 "width": POURCENT(100), "height": POURCENT(100)}
        st.style(t, aplat, plein)
        fixe = t.clone(photo, cadre, i + 1)   # copie de la photo du club devenue image fixe du jeu
        sd = t.sd(fixe)
        sd["ImageKind"] = 0
        sd["StaticImage"]["m_AssetGUID"] = STADE_DEFAUT_GUID
        sd["StaticImage_UxmlAttributeFlags"] = 1
        bd = sd["Binding"]
        bd["m_kind"] = 0
        bd["m_direct"]["Path"]["m_path"] = ""
        bd["m_visualFunction"]["m_target"]["m_guid"] = ""
        bd["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
        bd["m_visualFunction"]["m_outputs"]["m_variable"]["m_argumentBytes"] = []
        sd["Binding_UxmlAttributeFlags"] = 0
        st.style(t, fixe, plein)
        return None

    def _capacite(self, rang):
        """« 61276 places » : le long texte de FM (selectedstadium.Capacity) remplacé par le nombre seul + places ;
        hors du BindableSwitchElement de FM (retiré)"""
        t = self.t
        vieux = first(t, lambda r: t.binding(r, "TextBinding") == "selectedstadium.Capacity", rang)
        if vieux is None:
            return "Stade : capacité introuvable"
        r = t.clone_shallow(vieux, rang)
        t.sd(r)["name"] = ""
        t.sd(r)["TextBinding"]["m_direct"]["Path"]["m_path"] = STADE_CAPACITE
        f = t.clone_shallow(vieux, rang)
        t.sd(f)["name"] = ""
        t.sd(f)["text"], t.sd(f)["text_UxmlAttributeFlags"] = STADE_PLACES, 1
        t.sd(f)["TextBinding"]["m_kind"] = 0
        t.sd(f)["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        t.remove(t.parent[vieux])
        return None

    def stade_photo(self):
        """bloc Stade recopié (déjà dans le milieu) : photo en fond, nom + ville centrés en haut, 4 cases en bas ;
        2 copies (mode Défaut moins haut / autres modes) dans des SIVisible sur le mode d'affichage"""
        t, st = self.t, self.t.styles
        nom_val = first(t, lambda r: t.binding(r, "TextBinding") == "selectedstadium.Name")
        main = nom_val
        while main is not None and t.name(main) != "container-main":
            main = t.parent.get(main)
        if main is None:
            return "Stade : #container-main introuvable"
        ligne = {n: first(t, lambda r, n=n: t.name(r) == n, main) for n in ["name", "city"] + STADE_CASES}
        cotes = {n: (r and first(t, lambda x: t.name(x) == "left-side", r),
                     r and first(t, lambda x: t.name(x) == "right-side", r)) for n, r in ligne.items()}
        if any(None in c for c in cotes.values()):
            return "Stade : lignes du bloc introuvables"
        anciens = list(t.children(main))

        cadre = self._boite(main, main, 0)
        t.sd(cadre)["name"], t.sd(cadre)["name_UxmlAttributeFlags"] = STADE_NOM, 1
        st.style(t, cadre, {"width": POURCENT(100), "flex-direction": "column", "justify-content": "space-between",
                            "overflow": "hidden"})
        # de bas en haut : aplat couleur du club, stade générique (sièges ajourés), photo du club (transparente sans
        # photo : le stade générique se voit seulement pour les clubs sans photo)
        photo = self._photo(cadre, 0)
        if photo is None:
            return f"{STADE_IMAGE_SOURCE} : image du logo introuvable"
        err = self.stade_defaut(cadre, photo)
        if err:
            return err
        if STADE_ESSAI_ID:
            self._photo_stade(cadre, t.children(cadre).index(photo) + 1)
            t.remove(photo)   # v34 ESSAI : sans notre photo par id de club, seulement la couche par id de stade

        haut = self._boite(main, cadre)   # nom du stade, puis ville
        st.style(t, haut, {"align-items": "center", "background-color": STADE_VOILE, "width": POURCENT(100)})
        for n in ("name", "city"):
            if n == "name":   # v22 : nom cliquable (bouton FM sans aspect) -> écran Infrastructures du club
                rang = self._bouton_ecran(haut, STADE_ECRAN, STADE_ECRAN_PARAMS)
                if rang is None:
                    return "Stade : bouton FM (#ShowTilesButton) introuvable"
            else:
                rang = self._boite(main, haut)
            st.style(t, rang, {"flex-direction": "row", "justify-content": "center", "align-items": "center",
                               "margin-top": 6 if n == "name" else 0, "margin-bottom": 6 if n == "city" else 0})
            for k in list(t.children(cotes[n][1])):
                move(t, k, rang)
        for x in t.walk(haut):
            if typ(t, x) == "SIText":
                st.style(t, x, {"-unity-text-align": "middle-center",
                                **({"font-size": STADE_TAILLE_NOM} if x == nom_val else {})})
                if x == nom_val and "sitext-hover-cursor" not in classes(t, x):   # main au survol (titres FM cliquables)
                    t.elem(x)["m_Classes"] = list(classes(t, x)) + ["sitext-hover-cursor"]

        bas = self._boite(main, cadre)    # 4 cases séparées par des traits
        st.style(t, bas, {"flex-direction": "row", "align-items": "stretch", "background-color": STADE_VOILE,
                          "width": POURCENT(100)})
        for i, n in enumerate(STADE_CASES):
            if i:
                self.trait_v(bas)
            case = self._boite(main, bas)
            st.style(t, case, {**GRANDIR(1), "align-items": "center", "justify-content": "center",
                               "margin-top": 8, "margin-bottom": 8})
            titre, valeur = cotes[n]
            for k in list(t.children(titre)):
                move(t, k, case)
                if typ(t, k) == "SIText":
                    t.elem(k)["m_Classes"] = ["body-sm", "global-text-secondary"]
                    st.style(t, k, {"-unity-text-align": "middle-center"})
            rang = self._boite(main, case)
            st.style(t, rang, {"flex-direction": "row", "justify-content": "center", "align-items": "center",
                               "margin-top": 4})
            for k in list(t.children(valeur)):
                move(t, k, rang)
            if n == "capacity":
                err = self._capacite(rang)
                if err:
                    return err
            for x in t.walk(rang):
                if typ(t, x) == "SIText":
                    st.style(t, x, {"-unity-text-align": "middle-center", "font-size": STADE_TAILLE_VALEUR})

        for r in anciens:   # anciennes lignes FM : vidées plus haut ou inutiles ici
            t.remove(r)
        s, vis = ni.visible_model()
        if vis is None:
            return "modèle de comparaison FM introuvable"
        for op, h in ((OP_EGAL, STADE_HAUTEUR_DEFAUT), (OP_SUPERIEUR, STADE_HAUTEUR)):
            v = ni.new_visible(t, s, vis, main, t.children(main).index(cadre),
                               f"{STADE_NOM}Mode{op}", ni.make_binding(s.sd(vis)["Binding"], op, [MODE_AFFICHAGE], 0))
            t.elem(v)["m_RuleIndex"] = -1
            st.style(t, v, {"width": POURCENT(100)})
            c = t.clone(cadre, v) if op == OP_EGAL else cadre
            if c == cadre:
                move(t, cadre, v)
            st.style(t, c, {"height": h, "min-height": h})
        for n in STADE_EN_TETE:
            r = first(t, lambda x, n=n: t.name(x) == n, t.parent[main])
            if r is None:
                return f"Stade : en-tête (#{n}) introuvable"
            st.style(t, r, {"display": MOT_AUCUN})
        return None

    # ---------- bas de la colonne de gauche : onglets À propos | Budgets | Finances ----------
    def onglets_gauche(self):
        """à la place d'« À propos du club » : les onglets d'une tuile FM (ClubBoardCompactBlock), un clic change le
        contenu sur place ; Budgets et Finances dans une zone qui défile (comme l'À propos de FM), sans leur titre
        (l'onglet le donne), resserrés (marges, lignes, solde)"""
        t, st = self.t, self.t.styles
        s, ss = self.source(ONGLETS_SOURCE)
        groupe = s and first(s, lambda x: typ(s, x) == "TabGroup")
        if groupe is None:
            return f"{ONGLETS_SOURCE} : onglets introuvables"
        gauche = t.parent[self.about]
        zone = self.boite(gauche, [], BUDGETS_NOM, t.children(gauche).index(self.about))
        st.style(t, zone, {"width": POURCENT(100), **GRANDIR(1), "overflow": "hidden"})
        # v32 (le joueur : Direction « actif que pour notre club », pas d'onglet vide ailleurs) : deux groupes
        # d'onglets, un par cas (cacher un seul bouton d'un TabGroup FM n'est pas sûr) ; le À propos est recopié
        sc, vis = ni.visible_model(ni.SOURCE_COMPARE, ni.FN_COMPARE)
        if vis is None:
            return "modèle de comparaison FM introuvable"
        about = self.about
        for op, onglets, suffixe in ((OP_EGAL_CLUB, ONGLETS, ""),
                                     (OP_DIFFERENT_CLUB, [o for o in ONGLETS if o[0] != "Direction"], "Autres")):
            v = ni.new_visible(t, sc, vis, zone, None, f"{BUDGETS_NOM}Club{suffixe or 'Notre'}",
                               ni.make_binding(sc.sd(vis)["Binding"], op, ["club.UniqueId", "human.Club.UniqueId"]))
            t.elem(v)["m_RuleIndex"] = -1
            st.style(t, v, {"width": POURCENT(100), **GRANDIR(1), "overflow": "hidden"})
            scroll = self.scroll
            if suffixe:   # copie du À propos ; sa zone qui défile = même place que dans l'original
                kids = t.children(about)
                if scroll not in kids:
                    return "À propos : zone qui défile introuvable (copie pour les autres clubs)"
                self.about = t.clone(about, gauche)
                self.scroll = t.children(self.about)[kids.index(scroll)]
            err = self._groupe_onglets(v, s, ss, groupe, onglets, suffixe)
            self.scroll = scroll
            if err:
                return err
        return None

    def _groupe_onglets(self, zone, s, ss, groupe, onglets, suffixe):
        t, st = self.t, self.t.styles
        tg = self.copie(zone, s, ss, groupe)
        boutons = first(t, lambda x: t.name(x) == "TabButtons", tg)
        contenu = first(t, lambda x: t.name(x) == "TabsContent", tg)
        if boutons is None or contenu is None or not t.children(boutons):
            return f"{ONGLETS_SOURCE} : onglets introuvables"
        st.style(t, tg, {"width": POURCENT(100), **GRANDIR(1)})
        st.style(t, contenu, {"width": POURCENT(100), **GRANDIR(1)})
        while len(t.children(boutons)) < len(onglets):
            t.clone(t.children(boutons)[-1], boutons)
        for b in t.children(boutons)[len(onglets):]:
            t.remove(b)
        for b, (_, texte) in zip(t.children(boutons), onglets):
            for o in t.elem(b).get("m_SerializedDataOverride") or []:
                sd = t.refs[o["m_SerializedData"]["rid"]]["data"]
                if "TextBinding" not in sd:
                    continue
                sd["text"], sd["text_UxmlAttributeFlags"], sd["DebugDisplay"] = texte, 1, texte
                sd["TextBinding"]["m_kind"] = 0
                sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        for x in t.children(contenu):
            t.remove(x)
        pages = {}
        for nom, _ in onglets:   # une page par onglet, dans l'ordre des onglets
            pages[nom] = self.boite(contenu, [], f"{BUDGETS_NOM}{nom}{suffixe}")
            st.style(t, pages[nom], {"width": POURCENT(100), **GRANDIR(1), "overflow": "hidden"})
        s, vis = ni.visible_model()
        if vis is None:
            return "modèle de comparaison FM introuvable"
        # Budgets : 2 copies, une plus serrée pour le mode Large (op ==) et une pour les autres modes (op >)
        endroits = [("Budgets", self.budgets, None), ("Finances", self.finances, None),
                    ("Direction", self.direction, None)]
        endroits[0:1] = [("Budgets", self.budgets, op) for op in (OP_EGAL, OP_SUPERIEUR)]
        endroits = [e for e in endroits if e[0] in pages]
        for nom, faire, op in endroits:
            parent = pages[nom]
            if op is not None:
                parent = ni.new_visible(t, s, vis, pages[nom], None, f"{BUDGETS_NOM}{nom}{suffixe}Mode{op}",
                                        ni.make_binding(s.sd(vis)["Binding"], op, [MODE_AFFICHAGE], 0))
                t.elem(parent)["m_RuleIndex"] = -1
                st.style(t, parent, {"width": POURCENT(100), **GRANDIR(1), "overflow": "hidden"})
            large = op == OP_EGAL
            defile = t.clone_shallow(self.scroll, parent)
            t.sd(defile)["name"], t.sd(defile)["name_UxmlAttributeFlags"] = "", 0
            t.elem(defile)["m_Classes"] = ["flex-grow-class", "align-self-stretch"] + ([] if large else ["margin-top-8"])
            t.elem(defile)["m_RuleIndex"] = -1
            err = faire(defile)
            if err:
                return err
            titre = first(t, lambda x: t.name(x) == "Title", defile)
            if titre is not None:
                st.style(t, titre, {"display": MOT_AUCUN})
            self.resserrer(defile, large)
        move(t, self.about, pages["APropos"])
        st.style(t, self.about, {"width": POURCENT(100), **GRANDIR(1)})
        lien = t.children(self.about)[0]   # titre « À propos » (lien FM) : l'onglet le donne
        if lien != self.scroll:
            st.style(t, lien, {"display": MOT_AUCUN})
            t.elem(self.scroll)["m_Classes"] = list(classes(t, self.scroll)) + ["margin-top-8"]
        return None

    def resserrer(self, defile, large=False):
        """marges, lignes et solde plus serrés (colonne étroite) ; large : encore plus (mode d'affichage Large)"""
        t, st = self.t, self.t.styles
        trait = LARGE_TRAIT if large else SERRE_TRAIT
        for x in t.walk(defile):
            cls = classes(t, x)
            if x != defile and t.elem(x).get("m_RuleIndex", -1) >= 0 and any(
                    p[0] == FLEX_GROW for p in st.values(t.elem(x)["m_RuleIndex"])):
                st.style(t, x, {"flex-grow": 0})   # cadres FM en flex-grow 1 : grand vide en bas
            if large and typ(t, x) == "SIText":
                t.elem(x)["m_Classes"] = [LARGE_TEXTES.get(c, c) for c in cls if LARGE_TEXTES.get(c, c)]
                cls = classes(t, x)
            if large and t.name(x) == "LeftFrame":
                t.elem(x)["m_Classes"] = ["margin-left-global-gap-regular" if c == "margin-left-global-gap-extra-large"
                                          else c for c in cls]
            if "layout-divider-solid-horizontal" in cls:
                st.style(t, x, {"margin-top": trait, "margin-bottom": trait})
            elif t.name(x) in ("TransferBudget-Frame", "Wage-Frame", "SectionTitleFrame"):
                st.style(t, x, {"margin-bottom": 0 if large else SERRE_MARGE})
            elif large and t.name(x) == "OveralFrame":
                st.style(t, x, {"margin-bottom": 0})
            elif t.name(x) == "finances-view":
                for ligne in t.children(x):
                    st.style(t, ligne, {"height": SERRE_LIGNE, "min-height": SERRE_LIGNE})
                    for k in t.walk(ligne):
                        if typ(t, k) == "SIText":
                            t.elem(k)["m_Classes"] = ["body-sm" if c == "body-md" else c for c in classes(t, k)]
            elif t.name(x) == "OveralValue":   # montant du solde
                st.style(t, x, {"font-size": LARGE_SOLDE if large else SERRE_SOLDE})

    def direction(self, parent):
        """v31 : avis de la direction sur notre travail (bloc FM de l'écran Retours, FeedbackPerformanceClubBoardBlock :
        note globale + match / recrutement / tactique / effectif), seulement sur la page de notre club (SIVisible
        club == club du joueur) ; ses paramètres team / teamconfidence donnés par un BindingRemapper (human.team)"""
        t, st = self.t, self.t.styles
        s, ss = self.source(DIRECTION_SOURCE)
        if s is None:
            return f"{DIRECTION_SOURCE} : introuvable"
        racine = s.children(s.tt["m_VisualTree"]["rid"])[0]
        remap = first(s, lambda x: typ(s, x) == "BindingRemapper")
        params = {p["name"]: p["type"]["id"] for p in s.sd(racine).get("Parameters") or []}
        sc, vis = ni.visible_model(ni.SOURCE_COMPARE, ni.FN_COMPARE)
        if remap is None or vis is None or set(params) != set(DIRECTION_PARAMS):
            return f"{DIRECTION_SOURCE} : structure FM inattendue"
        v = ni.new_visible(t, sc, vis, parent, None, f"{BUDGETS_NOM}DirectionNotreClub",
                           ni.make_binding(sc.sd(vis)["Binding"], 2, ["club.UniqueId", "human.Club.UniqueId"]))
        t.elem(v)["m_RuleIndex"] = -1
        st.style(t, v, {"width": POURCENT(100)})
        r = t.clone(remap, v, src=s)
        for k in list(t.children(r)):
            t.remove(k)
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
        st.style(t, r, {"width": POURCENT(100)})
        sd = t.sd(r)
        sd["name"], sd["name_UxmlAttributeFlags"] = "", 0
        sd["Mappings"] = [{"m_serialisedType": 0, "from": n, "to": {"m_path": c}, "type": {"id": params[n]}}
                          for n, c in DIRECTION_PARAMS.items()]
        b = self.copie(r, s, ss, racine)
        for x in t.walk(b):   # colonne étroite : détail puis points forts / critiques l'un sous l'autre
            if t.name(x) == "Container" and "row-direction-normal" in classes(t, x):
                t.elem(x)["m_Classes"] = [c for c in classes(t, x) if c != "row-direction-normal"]
                st.style(t, x, {"flex-direction": "column"})
        return None

    def budgets(self, parent):
        """cadre et titre du bloc Finances, puis solde (tuile Finances) et budgets transferts / salaires (tuile
        Budgets du recrutement), séparés par des traits"""
        t = self.t
        r = self.recopie(parent, "ClubInfoFinancesBlock")
        vue = r and first(t, lambda x: t.name(x) == "finances-view", r)
        titre = r and first(t, lambda x: t.name(x) == "Title", r)
        sf, sfs = self.source(SOLDE_SOURCE)
        sb, sbs = self.source(BUDGETS_SOURCE)
        solde = sf and first(sf, lambda x: sf.name(x) == SOLDE)
        parts = [sb and first(sb, lambda x, n=n: sb.name(x) == n) for n in BUDGETS]
        if None in (vue, titre, solde, *parts):
            return "Budgets : morceaux FM introuvables"
        cadre = t.parent[vue]
        t.remove(vue)
        sd = t.sd(titre)
        sd["text"], sd["text_UxmlAttributeFlags"], sd["DebugDisplay"] = TITRE_BUDGETS, 1, TITRE_BUDGETS
        sd["TextBinding"]["m_kind"] = 0
        sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        t.elem(titre)["m_Classes"] = list(t.elem(titre).get("m_Classes") or []) + ["margin-bottom-global-gap-regular"]
        s = self.copie(cadre, sf, sfs, solde)
        for x in t.walk(s):   # montant du solde un cran plus petit (gagne de la hauteur)
            if "heading-xl" in classes(t, x):
                t.elem(x)["m_Classes"] = ["heading-lg" if c == "heading-xl" else c for c in classes(t, x)]
        for x in parts:
            self.trait_h(cadre)
            self.copie(cadre, sb, sbs, x)
        return None


def construire(t):
    p = Panneau(t)
    if p.manque():
        return [f"repères FM introuvables ({', '.join(p.manque())}), ignoré"]
    g = guids()
    speciaux = {"Budgets": p.budgets, "ClubInfoFinancesBlock": p.finances, "ClubInfoLegendsBlock": p.legendes,
                "KitsBlock": p.maillots, "ClubFacilitiesStadiumBlock": p.stade}
    absents = sorted({m for ligne in MILIEU for _, col in ligne for m in col} - set(g) - set(speciaux))
    if absents:
        return [f"modèles FM introuvables ({', '.join(absents)}), ignoré"]
    st = t.styles

    # gauche : Équipe première puis À propos
    gauche = p.boite(p.row, [], f"{PREFIXE}Gauche", t.children(p.row).index(p.team))
    st.style(t, gauche, {"width": POURCENT(LARGEUR_COTES), "flex-shrink": 0, "min-height": 0})
    move(t, p.team, gauche)
    p.trait_h(gauche)
    move(t, p.about, gauche)
    st.style(t, p.team, {"width": POURCENT(100), **GRANDIR(PART_EFFECTIF)})
    st.style(t, p.about, {"width": POURCENT(100), **GRANDIR(1)})

    # milieu : défile de haut en bas si trop haut
    milieu = p.boite(p.row, [], NOM_RACINE, t.children(p.row).index(p.d1) + 1)
    st.style(t, milieu, {**GRANDIR(1), "overflow": "hidden"})
    defile = t.clone_shallow(p.scroll, milieu)
    t.sd(defile)["name"] = ""
    t.elem(defile)["m_Classes"] = ["flex-grow-class", "align-self-stretch"]
    t.elem(defile)["m_RuleIndex"] = -1
    if "verticalScrollerVisibility" not in t.sd(defile):
        return ["défilement du milieu : réglage de la barre introuvable, ignoré"]
    t.sd(defile)["verticalScrollerVisibility"] = BARRE_CACHEE   # défile toujours (molette), sans barre
    t.sd(defile)["verticalScrollerVisibility_UxmlAttributeFlags"] = 1   # 0 : valeur ignorée par Unity
    noms = []
    for i, ligne in enumerate(MILIEU):
        if i:
            p.trait_h(defile, "margin-vertical-global-gap-regular")
        rang = p.boite(defile, ["row-direction-normal", "align-items-stretch"])
        for j, (part, colonne) in enumerate(ligne):
            if j:
                p.trait_v(rang)
            col = p.boite(rang, ["align-items-stretch"])
            st.style(t, col, GRANDIR(part) if part else {"flex-grow": 0, "flex-shrink": 0})
            for k, m in enumerate(colonne):
                if k:   # blocs empilés : un trait, ou un petit espace s'ils gardent leur cadre
                    if SANS_BULLES:
                        p.trait_h(col, "margin-vertical-global-gap-regular")
                    else:
                        p.boite(col, ["margin-top-8"])
                if m in speciaux:
                    err = speciaux[m](col)
                    if err:
                        return [err + ", ignoré"]
                else:   # seul dans sa colonne : s'étire jusqu'en bas de la ligne (pas de vide sous le stade)
                    p.modele(col, m, g[m], ["flex-grow-class" if len(colonne) == 1 else "flex-no-shrink-class"])
                noms.append(m)

    # droite : Actualités puis Historique des transferts ; plus de 3e trait vertical
    t.remove(p.d3)
    droite = p.boite(p.row, [], f"{PREFIXE}Droite")
    st.style(t, droite, {"width": POURCENT(LARGEUR_COTES), "flex-shrink": 0, "min-height": 0})
    haut = droite
    if not ACTUALITES_EN_DEFAUT:   # Actualités + trait dans un SIVisible « mode d'affichage > 0 (pas Défaut) »
        # comparaison FM (BindIntToVisible, op 4 = « > ») : la liaison directe sur l'entier restait visible en Défaut (v11)
        s, vis = ni.visible_model()
        if vis is None:
            return ["modèle de comparaison FM introuvable, ignoré"]
        haut = ni.new_visible(t, s, vis, droite, None, f"{PREFIXE}ActualitesHorsDefaut",
                              ni.make_binding(s.sd(vis)["Binding"], OP_SUPERIEUR, [MODE_AFFICHAGE], 0))
        t.sd(haut)["name_UxmlAttributeFlags"] = 1
        t.elem(haut)["m_RuleIndex"] = -1
        st.style(t, haut, {"width": POURCENT(100), **GRANDIR(PART_ACTUALITES), "overflow": "hidden"})
    move(t, p.news, haut)
    p.trait_h(haut)
    move(t, p.transfers, droite)
    st.style(t, p.news, {"width": POURCENT(100), **GRANDIR(1 if haut != droite else PART_ACTUALITES)})
    st.style(t, p.transfers, {"width": POURCENT(100), **GRANDIR(1)})
    if ACTUALITES_UNE_SEULE:
        autres = first(t, lambda x: t.name(x) == "TransferNewsMoreStoriesText", p.news)
        liste = first(t, lambda x: t.name(x) == "StoriesList", p.news)
        # bloc de la liste = son ancêtre voisin de « More Stories » (v30 : remonter jusqu'à #News emportait la
        # tuile à la une, rangée par FM avec la liste dans le même BindingRemapper / #HasNews)
        bloc_liste = liste
        cadre = autres is not None and t.parent.get(autres)
        while bloc_liste is not None and t.parent.get(bloc_liste) != cadre:
            bloc_liste = t.parent.get(bloc_liste)
        if autres is None or bloc_liste is None:
            return ["Actualités : « More Stories » / liste des articles introuvables, ignoré"]
        t.remove(autres)
        t.remove(bloc_liste)
        # hauteur naturelle : base « auto » (GRANDIR plus haut avait mis flex-basis 0 : le bloc tomberait à 0)
        fixe = {"flex-grow": 0, "flex-shrink": 0, "flex-basis-auto": MOT_AUTO}
        st.style(t, p.news, {"width": POURCENT(100), **fixe})
        if haut != droite:
            st.style(t, haut, {"width": POURCENT(100), **fixe})
    if "ClubFacilitiesStadiumBlock" in noms:
        err = p.stade_photo()
        if err:
            return [err + ", ignoré"]
    err = p.onglets_gauche()
    if err:
        return [err + ", ignoré"]
    return [f"3 colonnes (côtés {LARGEUR_COTES} %) ; milieu : " + ", ".join(noms)
            + ("" if ACTUALITES_EN_DEFAUT else " ; actualités cachées en mode Défaut")
            + " ; stade avec photo"
            + " ; gauche : onglets " + " | ".join(n for n, _ in ONGLETS)]


def original(bundle, obj, path_id=None):
    """typetree d'origine (sauvegarde des originaux) de obj (ou de l'objet path_id), ou None"""
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    env = UnityPy.load(backup.backup_path(bundle))
    pid = obj.path_id if path_id is None else path_id
    o = next((o for o in env.objects if o.path_id == pid), None)
    return o.read_typetree() if o is not None else None


def ouvrir(depart_original=False):
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        return None, None, None, None
    sheet = None
    if depart_original:
        orig = original(bundle, obj)
        if orig is not None:
            tt = orig
            sheet = original(bundle, obj, tt["inlineSheet"]["m_PathID"])
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    if sheet is not None:   # feuille de style d'origine aussi : les règles des versions précédentes ne s'empilent pas
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, tt, t


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    nb.save_all()


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def photos_stades():
    """dossier des photos de stade + son config.xml refait d'après les images présentes (stades_photos.py)"""
    d, n = stades_photos.ecrire(a_blanc=nb.DRY_RUN)
    if d is None:
        print(L("photos des stades : dossier Documents de FM 27 introuvable (lancer FM une fois)",
                "stadium photos: FM 27 Documents folder not found (start FM once)"))
    else:
        print(L(f"photos des stades : {n} dans {d}", f"stadium photos: {n} in {d}"))


def cmd_appliquer():
    photos_stades()
    bundle, obj, tt, t = ouvrir()
    if tt is None:
        print(f"{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    old = marques(t)
    if any(t.name(r) == NOM_RACINE for r in old):
        print(f"{MODELE} : déjà appliqué")
    else:
        bundle, obj, tt, t = ouvrir(depart_original=True)
        if marques(t):
            print(f"{MODELE} : pas de sauvegarde d'origine propre, ignoré")
            return
        msgs = construire(t) + (["ancienne version remplacée"] if old else [])
        for m in msgs:
            print(f"{MODELE} : {m}")
        if any("introuvable" in m for m in msgs):
            return
        enregistrer(bundle, obj, tt, t)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
    # stade générique (clubs sans photo) dans le bundle des fonds
    fonds_jeu.ecrire(stade=True, a_blanc=nb.DRY_RUN)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fonds_jeu.ecrire(stade=False, a_blanc=nb.DRY_RUN)   # le fond des pages (theme_fond) reste s'il est actif
    bundle, obj, tt, t = ouvrir()
    if not t or not marques(t):
        print("rien à retirer")
        return
    orig = original(bundle, obj)
    if orig is None:
        print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return
    obj.save_typetree(orig)
    sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{MODELE} : remis d'origine")


def cmd_etat():
    _, _, tt, t = ouvrir()
    if tt is None:
        print(f"{MODELE} : introuvable")
        return
    old = [t.name(r) for r in marques(t)]
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
            print("panneau du bas du club : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
