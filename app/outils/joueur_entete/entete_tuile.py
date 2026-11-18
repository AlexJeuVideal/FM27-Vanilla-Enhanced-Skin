"""En-tête de la fiche joueur en « grande tuile » (2026-11-05, concept du joueur) : vue au choix (option
`entete_vue`), appelée par entete_fiche (seul écrivain du bundle des en-têtes).

Une seule tuile (fond, bord, coins ronds), largeurs FIXES (rien ne s'adapte, rien ne bave), de gauche à droite :
photo | identité (nom + n°, poste, taille, drapeaux de statut, Actions) | grille 2 colonnes (Nation + sélections /
Âge / Valeur | Club + temps de jeu / Salaire + contrat) | polygone (pas en Small) | Statut de transfert +
Éligibilité (tuiles 2x1 de FM, sans leur cadre) | Progression (tuile 2x1 de FM ; pas dans la plus petite largeur) |
Niveau actuel / Potentiel (bloc de FM : étoiles chez nous, rapport du recruteur sinon).

Dans PlayerReportHeader (modèle touché par ce seul script) : chaque bannière de FM (max / mid / min, choisies par
FM selon la largeur de la fenêtre ; pas celle du téléphone) est cachée et notre tuile, aux largeurs de cette
taille (TAILLES), prend sa place ; la photo de FM est cachée (recopiée dans la tuile). Chaque passage repart du
modèle d'origine (sauvegarde) : option « fm » = modèle d'origine remis.
Éléments repris par contenu (chemins de données, noms FM) dans la bannière max (déjà retouchée par entete_fiche :
2e nationalité comprise).
"""
import copy

from arbre import Tree, Styles, named, PROPRIETES, no_styles  # noqa: F401
from elements import first, typ, plain, copy_usings, move
import notes_au_lieu_des_libelles as nb
from langue import texte as L
import options

OPTION = "entete_vue"
MODELE = "PlayerReportHeader"
PREFIXE = "UIPickerEnteteTuile"
# v2 : v1 vue en jeu = rien d'affiché : les aiguillages de FM (UseStandard / UseSmall) choisissent leur enfant PAR
# POSITION ; bannière cachée + tuile côte à côte décalaient les enfants -> les deux dans un seul conteneur (Place),
# à la place exacte de la bannière
# v3 (le joueur, v2 vue en jeu : « j'aime beaucoup ») : Progression retirée ; tuile sur toute la largeur (dépassait
# en Large, trop courte en Medium / Small) : blocs en parts fixes (POIDS) ; grille en 2 rangées (traits alignés,
# trait du milieu à la hauteur de celui Statut / Éligibilité) ; bords alignés sur la fiche ; dégradé du club
# v4 (le joueur, v3 vue en Large : « rend bien mieux ») : statut étroit, Statut de prêt au lieu d'Éligibilité,
# grille Âge | Nation / Salaire | Valeur, marge avant chaque trait
# v5 : polygone dans une cale fixe sans liaison (il s'affichait en très grand pendant le chargement)
# v6 : une seule ligne de sélections (A, ou jeunes avant AGE_JEUNE ans), le détail au survol (infobulle de FM)
# v7 : la ligne unique de sélections en Large seulement (Medium / Small : les deux côte à côte)
# v8 : nationalités en 3 lettres en Large
# v9 : bannière / photo de FM cachées sans liaison (le grand polygone Medium flashait au chargement) ; nom court du
# club en Large
# v10 : colonne âge / salaire plus large, nation / valeur plus étroite
# v11 : polygone affiché seulement une fois les données du joueur lues (flash à l'ouverture)
# v12 : rayon du polygone 44 -> 17 % (flash au changement de joueur : image sans étiquettes, rayon entier)
# v13 : paire Âge | Nation en 2 versions (Large / Medium + Small) : plus de place pour la nation en Medium
# v14 (le joueur : « augmente la taille du polygone » Large et Medium, « égalise quelques tailles entre les cases »
# en Large) : cale du polygone et tuile plus grandes, rayon par bannière ; âge / nation / club à peu près égaux en
# Large, statut un peu plus étroit
# v15 (le joueur, v14 vue : « medium tu peux largement grossir encore, large un peu ») : rayon 20 -> 24 % (max),
# 18,3 -> 27 % (mid) ; la cale avait encore beaucoup de place autour des étiquettes
# v16 (le joueur : étoiles du niveau un peu coupées en Large) : cale max 250 -> 224 px de large (étiquettes ~190 px,
# rayon inchangé : % du petit côté = la hauteur)
# v17 (le joueur, Small : « pourquoi c'est en 3 lettres ? ») : la bannière de FM27 a sa propre nation en 3 lettres
# (primarytext nation.threelettername), trouvée en premier quand UIPickerNationalites manque -> Medium / Small
# prennent la nation en nom complet (nation.Name)
# v18 (le joueur, Large + Medium : polygone encore plus grand, étiquettes à ~3-4 mm du bord de la tuile ; Large :
# niveau / potentiel un peu à gauche, pris sur Dispo. transfert / prêt) : mesuré sur sa capture Large (×1,17 écran) :
# étiquettes à ~29 px du bord haut / bas -> rayon + ~16 px (Large) / + ~10 px (Medium), cale + 2 × ce gain (même
# marge autour des étiquettes qu'en v15 : pas de flash) ; la cale dépasse la zone en hauteur (coupée par la zone,
# les étiquettes restent dedans) ; parts statut / niveau propres au Large (`poids` de TAILLES)
# v19 (le joueur, v18 vue : polygone parfait mais le flash revient) : 32 % de la cale agrandie = rayon trop grand pour
# la marge des étiquettes (~33-36 px au lieu de ~37 : FM le réduit -> saut). Rayon = celui que FM garde avec les
# étiquettes (moitié de la hauteur - ~38 px) : max 31 % (62,6 px), mid 29 % (53,4 px) ; même taille à l'écran
# v20 (le joueur, v19 vue : flash plus petit mais encore léger) : marge ~38 px pas assez ; v15 (pas de flash) avait
# ~44 px en Large -> max 28 % (56,6 px, marge 44), mid 27 % (49,7 px, marge 42)
# v21 (le joueur, v20 vue : léger flash encore, Large + Medium ; « tu avais réussi parfaitement avant ») : le rayon
# n'était pas seul en cause -> cale + rayon du polygone remis comme en v16 (validée sans flash) : max 224 × 170 à 24 %,
# mid 226 × 164 à 27 % ; le reste de v17 / v18 gardé (nations, parts statut / niveau du Large)
# v22 (le joueur : « la taille actuelle, sans flash ») : cale visible de v18 gardée (elle coupe), mais le graphique
# y est INTERIEUR fois plus grand, centré (déborde des 4 côtés, coupé) : les étiquettes y tiennent toujours, FM ne
# réduit plus le rayon -> même taille au chargement et à l'affichage. Rayon donné en px (`rayon_px`), converti en %
# du petit côté du graphique ; px = taille finale de v20, mesurée sur les vidéos du joueur (10 im/s, 1re image après
# le changement de joueur = flash : polygone +2 % en Large, +5 % en Medium, étiquettes +7 % / +4 %) : 55,5 / 47,5 px
# v23 : px mesurés sur les vidéos (v22 : px estimés)
# v24 (2026-11-07, le joueur, maquette « B » choisie) : chaque info dans sa carte (fond, bord, coins ronds, écart
# entre les cartes) au lieu des traits : [Âge / Contrat] [Nation / Valeur (bord vert)] [Club] [Dispo. transfert /
# Dispo. prêt] [Niveau / Potentiel] [polygone] ; polygone TOUT À DROITE, et aussi en Small (vide à droite)
# v25 (le joueur, v24 vue : « j'adore ») : nom du club coupé net -> « … » + nom complet au survol (bloc club de FM
# déplié dans tous les modes, chaîne rétrécissable, DisplayTooltipWhenElided sur le texte de la cellule) ; plus de bord
# vert autour de la valeur ; contenu des cartes centré ; cartes un peu plus discrètes ; plus de cadre autour de
# l'en-tête (seul le trait du bas reste) ; polygone un peu plus petit (rayon -10 %, plus d'air)
# v26 (le joueur : salaire et temps de jeu pas centrés) : leur bloc de FM sans largeur 100 % ni calage à gauche
# v27 (le joueur : « tu mets la progression en haut à droite ») : tuile Progression de FM (sans son cadre) à la place
# du polygone, dans sa carte tout à droite, tous les modes (le polygone reste dans le code : PROGRESSION = False)
# v28 : Progression en Small seulement (mode > 1), polygone en Large / Medium
# v30 : carte Progression habillée (titre, tendance, courbe dans un bandeau sombre)
# v31 (2026-11-09, le joueur : « brancher l'en-tête sur la couleur des tuiles ») : fond des cartes plus en style
# intégré (il passait devant tout) mais par la classe CL_CARTE (règle de la feuille du modèle, même couleur) ;
# couleurs_interface (tuiles) pose une règle plus forte sur cette classe
# v32 (2026-11-09, le joueur, Large : « fais de la place pour le nom ») : Dispo. transfert | Dispo. prêt côte à côte
# au-dessus de Niveau / Potentiel, dans une seule colonne ; la place gagnée va à l'identité
# v33 : rapport de supervision trop haut pour la carte Niveau (Large) : Niveau 1.15 / Dispo. 0.85 de la hauteur,
# marges réduites ; titre du rapport caché en Large (etoiles_rapport v2)
# v34 (le joueur : « Indisponible » sur 2 lignes) : valeurs Dispo. sur une ligne, « … » + infobulle (Large)
# v35 (Heyti, 2026-11-12 : sélections U20 affichées pour un jeune déjà sélectionné en A) : Large, ligne unique = A
# aussi avant AGE_JEUNE ans dès que InternationalDebutNationalTeamContainer n'est pas nul
# v36 (2026-11-15, le joueur) : Dispo. transfert / prêt centrés dans leur carte (cadre de FM en align-items-start)
# v37 : Large, titres Dispo. sur une ligne (body-xs) : les deux cartes à la même hauteur
# v38 (2026-11-18, le joueur : bas de l'en-tête mangé depuis FM du 2026-11-17) : FM fixe la hauteur du conteneur
# (.report-player-full-header-max-type-player, height 180 px) < notre tuile (Large 188 + 2 x 6) : hauteur du conteneur
# en auto (style intégré) -> il suit la tuile et pousse la fiche
# v39 (le joueur, v38 vue : Medium OK ; Large poussé = bas de la fiche qui défile) : tuile Large ramenée à 180 px
# (haut 172, marges 4) -> ne pousse plus rien en Large ; hauteur auto gardée (Medium 192)
VERSION = 39
CONTENEUR = "report-player-full-header-max"   # élément de FM qui porte la classe à hauteur fixe
AUTO = (1, 2)                                  # mot-clé Auto (style intégré)
CL_CARTE = "uipicker-entete-carte"     # classe fixe (sans version) : couleurs_interface.ENTETE_CARTE la vise
COURBE_FOND = (0.0, 0.0, 0.0, 0.22)
PROGRESSION = True
# v29 (le joueur : la 2x1 « écrit juste une phrase ») : la 2x2 a la courbe (FMLineChart) + la tendance
MODELE_PROGRESSION = "TrainingProgressReportTile_2x2"
INTERIEUR = 2.0                             # graphique = cale × INTERIEUR (v22)
# 2026-11-14 (option fiche_medium_colonne, demande de hunfair) : en Medium, carte Pour / Contre en pastilles (comme
# l'infobulle : cadres POUR | CONTRE) à la place du polygone, qui passe à droite d'Infos (fiche_joueur_plus)
MEDIUM_PC = options.get("fiche_medium_colonne") == "polygone"
# 2026-11-15 (option fiche_large_tuile) : en Large, entete = polygone (base) ; pastilles = carte Pour / Contre comme
# Medium ; dessous = rien (polygone + Pour / Contre à droite d'Infos, fiche_joueur_plus)
LARGE_TUILE = options.get("fiche_large_tuile")
# carte de droite par mode (0 Large, 1 Medium) : "pc", "poly" ou None
DROITE = {0: {"pastilles": "pc", "dessous": None}.get(LARGE_TUILE, "poly"), 1: "pc" if MEDIUM_PC else "poly"}
PC_RAPPORT = "Person.PlayerReportForContextTeam"     # comme le bandeau de l'en-tête de FM (entete_fiche)
PC_GUID_PASTILLE = "1d9ea6f83e853594c9a3339ba036281b"   # ProConRow = pastille de l'en-tête (entete_fiche, 28 px)
PC_RANGEES = 3                                       # rangées de pastilles max par cadre (le reste est caché)
PC_PAR_RANGEE = 4                                    # v2 (le joueur, v1 vue en jeu : « limite à 12 ») : 4 × 3 = 12 max
NOM = f"{PREFIXE}-v{VERSION}" + ("-mpc5" if MEDIUM_PC else "") \
    + {"pastilles": "-lpc1", "dessous": "-lrien1"}.get(LARGE_TUILE, "")
# mpc v3 : titres calés en haut ; v4 : pastilles centrées ; v5 : bouton Observer sans rapport
NOM_CACHE = PREFIXE + "Cache"          # SIVisible jamais vrai : bannière / photo de FM gardées, cachées
NOM_PLACE = PREFIXE + "Place"          # conteneur [bannière cachée, tuile] = un seul enfant de l'aiguillage
SOURCE = "report-player-banner-max"
MODE = "settings.AdaptiveScalingLevelIndex"
JOUEUR, EQUIPE = 1145176065, 1145176088

# par bannière de FM remplacée (taille de fenêtre) : polygone (largeur, hauteur en px ; None = pas), hauteur de la
# tuile, écart de part et d'autre des traits
TAILLES = {
    # v25 : rayons -10 % (le joueur : « que ça respire un poil plus » ; plus petit = plus de marge, pas de flash)
    # v39 (le joueur : en Large, v38 poussait la fiche = bas qui défile) : 172 + 2 x 4 = 180 = hauteur de FM
    "report-player-banner-max": dict(poly=(256, 202), haut=172, marge_haut=4, ecart=12, rayon_px=50.0,
                                     # v32 : statut + niveau en une colonne, le reste à l'identité (nom)
                                     poids=dict(statut_niveau=1.75, ident=2.65)),
    "report-player-banner-mid": dict(poly=(246, 184), haut=180, ecart=10, rayon_px=43.0),
    # v24 : polygone aussi ici (le joueur) ; rayon à la même marge d'étiquettes que le Large (~28 px haut / bas)
    "report-player-banner-min": dict(poly=(224, 150), haut=152, ecart=8, rayon_px=35.0),
}
# v24 : cartes (maquette B) : fond / bord d'une carte, coins ; v25 : un peu plus discrètes, plus de bord vert
CARTE_FOND, CARTE_BORD = (1.0, 1.0, 1.0, 0.03), (1.0, 1.0, 1.0, 0.07)
CARTE_RAYON = 8
CARTE_BORD_VALEUR = CARTE_BORD
CELLULE_CLUB = "text-cell-medium-strong"   # cellule du nom du club (texte #primary-text, « … » déjà là)
# v14 : rayon (% du petit côté de la cale) par bannière ; mesuré en jeu (v13, 210 × 150 à 17 %) : FM garde ~37 px de
# marge en largeur et en hauteur autour des étiquettes -> cale agrandie de 2 × le gain de rayon dans les deux sens,
# pour que FM ne réduise pas le rayon (sinon le flash revient)
# parts de la largeur de la tuile (flex-basis 0 : la même pour tous les joueurs, rien ne dépend du contenu ;
# en Small le polygone n'est pas là, les autres se partagent sa part)
# v4 : statut bien plus étroit, la place va à la nation (sélections jeunes coupées en v3)
# v10 (le joueur : salaire / fin de contrat coupés en Large) : âge / salaire 1.3 -> 1.75, nation / valeur 1.9 -> 1.45
# v13 : la paire Âge | Nation a sa part (paire), partagée selon le mode (POIDS_PAIRE : Large / Medium + Small) ;
# un peu plus large qu'avant (3.2 -> 3.5) pour les noms complets du Medium
# v14 (le joueur : égaliser les cases en Large) : âge ≈ nation ≈ club ; statut 1.1 -> 0.9 (la place du polygone)
POIDS = dict(ident=2.0, paire=3.6, club=1.75, poly=2.0, statut=0.9, niveau=1.5)
POIDS_PAIRE = {"large": (1.85, 1.75), "autres": (1.4, 2.1)}   # (âge / salaire, nation / valeur)
MARGE_HAUT = 6                              # px au-dessus / au-dessous de la tuile
MARGE_COTES = 28                            # px à gauche / à droite (bords de la fiche dessous)
# dégradé de l'en-tête de FM recopié en fond de la tuile : False (v3) = le dégradé d'origine de l'en-tête (autour de
# tout) teinte déjà la tuile (vu en jeu, club rouge) ; True le doublerait
DEGRADE_CLUB = False
DIRECTION_DEGRADE = 11                      # TopToBottomWithAlphaTweak (celle de l'en-tête de FM)
AGE_JEUNE = 21                              # moins de ... ans : sélections jeunes au lieu des sélections A (v6)
POLYGONE_MARGE = 10                        # px de part et d'autre de la cale du polygone (v5)
# v12 (vidéo du joueur, flash à chaque changement de joueur) : une image sans étiquettes, où FM prend le rayon demandé
# en entier (44 % : gros polygone), puis les étiquettes reviennent et FM le réduit ~2,7 fois pour qu'elles tiennent ;
# rayon demandé = celui que FM garde avec les étiquettes -> même taille sur les deux images
POLYGONE_RAYON = 17.0                     # % (FM : 34,8 ; étiquettes 10 px de la vue Guru)
FOND, BORD = (1.0, 1.0, 1.0, 0.045), (1.0, 1.0, 1.0, 0.12)
TRAIT = (1.0, 1.0, 1.0, 0.10)               # traits fins de la grille et entre les blocs
RAYON, MARGE = 12, (10, 14)                 # coins ; marges intérieures (haut / bas, gauche / droite)
CELLULE = (6, 10)                           # marges intérieures d'une case de la grille (haut / bas, côtés)
# v4 : Statut de transfert / Statut de prêt = les 2 cadres (repérés par leur titre) de cette tuile de FM
CLUB = "PlayerReportHeaderMaxTeamSection"   # bloc club de FM (recopié en Large avec le nom court, v9)
STATUT = "PlayerTransferStatusTile_2x2"
STATUT_CADRES = ["transfer-status-text", "loan-status-text"]

for _k, _v in {"width": (131105, 3), "height": (131087, 3), "max-height": (131094, 3),
               "padding-top": (131101, 3), "padding-bottom": (131098, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "margin-left": (131091, 3), "margin-right": (131092, 3),
               "margin-top": (131093, 3), "align-self": (131074, 7), "align-items": (131073, 7),
               "justify-content": (131088, 7), "flex-direction": (131083, 7),
               "border-top-color": (458763, 4), "border-bottom-color": (458758, 4),
               "border-left-color": (458761, 4), "border-right-color": (458762, 4),
               "border-top-left-radius": (458764, 3), "border-top-right-radius": (458765, 3),
               "border-bottom-left-radius": (458759, 3), "border-bottom-right-radius": (458760, 3),
               "position": (131102, 7), "left": (131089, 3), "top": (131104, 3),
               "font-size": (65537, 3), "text-overflow": (196609, 7), "white-space": (65552, 7)}.items():
    PROPRIETES.setdefault(_k, _v)


def vue():
    # 2026-11-07 (le joueur) : mode FM Guru = en-tête de FM (retouché), jamais la grande tuile
    if options.get("fiche_fmguru") == "guru":
        return "fm"
    return options.get(OPTION)


# ---------- recherche dans la bannière source ----------
def _surcharges(s, r):
    """texte des données surchargées d'un modèle inclus (chemins des liaisons par fonction décodés)"""
    out = []
    for o in s.elem(r).get("m_SerializedDataOverride") or []:
        d = (s.refs.get(o["m_SerializedData"]["rid"]) or {}).get("data") or {}
        out.append(str(d))
        tb = d.get("TextBinding")
        if isinstance(tb, dict) and tb.get("m_kind") == 2:
            out.append(nb.describe(tb))
    return " ".join(out)


def _alias(s, r):
    return s.elem(r).get("m_TemplateAlias") or ""


def pieces(s):
    """éléments de la bannière max à recopier (dict nom -> rid), ou None si l'un manque"""
    nom_txt = first(s, lambda r: "person.Name" in str(s.sd(r).get("TextBinding") or ""))
    poste = first(s, lambda r: "PositionCombinedStringLong" in _surcharges(s, r))
    flags = first(s, lambda r: s.name(r) == "PlayerStatusFlagsForTeamVisible")
    def _nation(r, court):
        if not typ(s, r).endswith("BindingRemapper"):
            return False
        maps = s.sd(r).get("Mappings") or []
        if not any(m.get("to", {}).get("m_path", "").lower() == "person.nation" for m in maps):
            return False
        trois = any(m.get("from") == "primarytext" and "threelettername" in m.get("to", {}).get("m_path", "").lower()
                    for m in maps)
        return trois == court
    # v17 : nom complet d'abord (la bannière de FM27 a aussi une nation en 3 lettres)
    nat3 = first(s, lambda r: _nation(r, True))   # Large, si la ligne d'entete_fiche manque
    nat = first(s, lambda r: s.name(r) == "UIPickerNationalites") or first(s, lambda r: _nation(r, False)) or nat3
    caps = first(s, lambda r: {"StandardTextTooltip", "text-cell-button-medium"}
                 <= {_alias(s, k) for k in s.children(r)})
    age = first(s, lambda r: _alias(s, r) == "data_display-cell-standard-regular" and "Person.Age" in _surcharges(s, r))
    club = first(s, lambda r: _alias(s, r) == "PlayerReportHeaderMaxTeamSection")
    valeur = first(s, lambda r: typ(s, r).endswith("BindingRemapper")
                   and any(m.get("from") == "TransferValueRange" for m in s.sd(r).get("Mappings") or []))
    contrat = first(s, lambda r: typ(s, r).endswith("BindableSwitchElement")
                    and "person.fullcontract.IsValid" in str(s.sd(r).get("Binding") or ""))
    scout = first(s, lambda r: _alias(s, r) == "PlayerReportHeaderScoutSection")
    actions = first(s, lambda r: s.name(r) == "FrameActions")
    setter = first(s, lambda r: typ(s, r).endswith("BindingSetter"))
    p = dict(nom=nom_txt is not None and s.parent[nom_txt], poste=poste is not None and s.parent[poste],
             flags=flags is not None and s.parent[flags], nat=nat, caps=caps, age=age, club=club, valeur=valeur,
             contrat=contrat, scout=scout is not None and s.parent[scout], actions=actions, setter=setter)
    manque = [k for k, v in p.items() if v is None or v is False]
    p["nat3"] = nat3
    return p, manque


# ---------- petits outils ----------
def boite(t, parent, css, classes=(), nom=""):
    classes = list(classes)
    if css and css.pop("_carte", False):   # v31 : carte (habille) -> fond par la classe CL_CARTE
        classes.append(CL_CARTE)
    b = plain(t, parent, None, classes, nom)
    t.elem(b)["m_RuleIndex"] = -1
    if nom:
        t.sd(b)["name_UxmlAttributeFlags"] = 1
    if css:
        t.styles.style(t, b, css)
    return b


def trait_vertical(t, parent):
    boite(t, parent, {"width": 1, "min-width": 1, "flex-shrink": 0, "align-self": "stretch",
                      "background-color": TRAIT})


def bloc(t, parent, largeur, classes=("column-direction-normal",), css=None):
    """bloc de largeur fixe (ne grandit pas, ne rétrécit pas, coupe ce qui dépasse)"""
    return boite(t, parent, {"width": largeur, "min-width": largeur, "max-width": largeur, "flex-shrink": 0,
                             "flex-grow": 0, "overflow": "hidden", **(css or {})}, classes)


class Src:
    """sous-arbre d'un autre modèle, recopié avec ses styles et ses modèles inclus"""
    def __init__(self, modele):
        bundle, _, tt = nb.find_vta(modele)
        self.s = Tree(tt) if tt is not None else None
        self.styles = Styles(bundle, tt) if tt is not None else None

    def clone(self, t, r, parent, index=None):
        c = t.clone(r, parent, index, src=self.s)
        copy_usings(t, self.s, r)
        t.styles.copy_from(self.styles, t, c)
        return c


def titre(t, txt_src, txt_rid, parent, fr, en):
    """petit titre fixe (style du titre « Rapport de supervision » de FM : body-xs-strong, gris)"""
    c = t.clone(txt_rid, parent, src=txt_src.s)
    no_styles(t, c)
    sd = t.sd(c)
    sd["name"] = ""
    sd["text"], sd["text_UxmlAttributeFlags"] = L(fr, en), 1
    sd["DebugDisplay"] = sd["text"]
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    t.elem(c)["m_Classes"] = ["body-xs-strong", "global-text-secondary", "content-ellipsis",
                              "margin-bottom-global-gap-small"]
    return c


def remapper(t, modele_rm, parent, liens, classes=()):
    rm = t.clone_shallow(modele_rm, parent)
    t.sd(rm)["name"] = ""
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": k, "to": {"m_path": p}, "type": {"id": ty}}
                            for k, (p, ty) in liens.items()]
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = list(classes), -1
    return rm


def tuile_fm(t, parent, modele_rm, modele, liens):
    """contenu d'une tuile de FM (son cadre retiré), paramètres -> données de l'en-tête ; message ou None"""
    src = Src(modele)
    if src.s is None:
        return f"{modele} introuvable"
    s = src.s
    racine = s.children(s.tt["m_VisualTree"]["rid"])[0]
    noms = [p.get("name") for p in s.sd(racine).get("Parameters") or []]
    rm = remapper(t, modele_rm, parent, {k: v for k, v in liens.items() if k in noms}, ["align-self-stretch"])
    c = src.clone(t, racine, rm)
    for r in list(t.walk(c)):
        e = t.elem(r)
        e["m_Classes"] = [k for k in e.get("m_Classes") or [] if k not in ("height-100-percent", "tile-content")]
    for r in [r for r in t.walk(c) if (t.elem(r).get("m_TemplateAlias") or "").startswith(("tile-", "micro-tile-"))]:
        p = t.parent[r]
        box = plain(t, p, t.children(p).index(r), ["align-self-stretch"])
        t.elem(box)["m_RuleIndex"] = -1
        for k in list(t.children(r)):
            move(t, k, box)
        t.remove(r)
    t.elem(c)["m_Classes"] = ["align-self-stretch"]
    return None


def habiller_progression(t, carte_p, txt):
    """v30 (le joueur : « la mini courbe, mais plus belle, pas juste dans le vide ») : titre « Progression » en haut
    de la carte, tendance (icône + phrase de FM) dessous, courbe dans un bandeau sombre aux coins ronds qui prend le
    reste de la hauteur"""
    ts, tr = txt
    if tr is not None:
        c = titre(t, ts, tr, carte_p, "Progression", "Progression")
        move(t, c, carte_p, 0)
    courbe = first(t, lambda r: t.name(r) == "data_display-graphs-tile-line_chart"
                   and r in set(t.walk(carte_p)))
    if courbe is None:
        return "Progression : courbe introuvable (pas de bandeau)"
    t.styles.style(t, courbe, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "margin-top": 6,
                               "background-color": COURBE_FOND, "padding-top": 4, "padding-bottom": 4,
                               "padding-left": 6, "padding-right": 6,
                               **{f"border-{c}-radius": 6 for c in ("top-left", "top-right", "bottom-left",
                                                                    "bottom-right")}})
    # les conteneurs entre la carte et la courbe prennent toute la hauteur (la courbe s'étire)
    r = t.parent[courbe]
    while r is not None and r != carte_p:
        t.styles.style(t, r, {"flex-grow": 1, "min-height": 0})
        r = t.parent.get(r)


def centrer(t, top):
    """v26 : contenu de FM centré dans sa carte : plus de largeur 100 % ni de calage à gauche, conteneurs centrés"""
    retire = {"width-100-percent", "align-items-start", "align-self-start", "content-left-align"}
    for r in t.walk(top):
        e = t.elem(r)
        if e.get("m_Classes") is None or typ(t, r).endswith(("Component", "SIText")):
            if e.get("m_Classes"):
                e["m_Classes"] = [k for k in e["m_Classes"] if k not in retire]
            continue
        e["m_Classes"] = [k for k in e["m_Classes"] if k not in retire]
        if "align-items-center" not in e["m_Classes"]:
            e["m_Classes"].append("align-items-center")
    return top


def club_retrecissable(t, top):
    """v25 : bloc club déplié sous top : chaque niveau rétrécit (max 100 %, min 0, sans flex-no-shrink) sauf le
    logo, pour que la cellule du nom (max 100 %, « … » de FM) soit bornée par la carte ; infobulle du nom complet
    quand il est coupé (DisplayTooltipWhenElided du texte de la cellule, par surcharge du modèle inclus) ;
    message ou None"""
    cent = {"unit": 2, "value": 100.0}
    for r in list(t.walk(top)):
        alias = t.elem(r).get("m_TemplateAlias") or ""
        if "Icon" in alias:
            continue
        e = t.elem(r)
        if e.get("m_Classes") is not None:
            e["m_Classes"] = [k for k in e["m_Classes"] if k != "flex-no-shrink-class"]
        if typ(t, r).endswith(("BindingRemapperComponent", "BindingSetterComponent")):
            continue
        t.styles.style(t, r, {"max-width": cent, "min-width": 0, "flex-shrink": 1})
    cell = Src(CELLULE_CLUB)
    txt = cell.s and first(cell.s, lambda r: cell.s.name(r) == "primary-text")
    if txt is None:
        return f"{CELLULE_CLUB} : texte introuvable (pas d'infobulle du nom du club)"
    ident = cell.s.sd(txt)["uxmlAssetId"]
    for inst in [r for r in t.walk(top) if t.elem(r).get("m_TemplateAlias") == CELLULE_CLUB]:
        ovs = t.elem(inst).setdefault("m_SerializedDataOverride", [])
        o = next((o for o in ovs if o["m_ElementId"] == ident), None)
        if o is None:
            ref = copy.deepcopy(cell.s.refs[cell.s.elem(txt)["m_SerializedData"]["rid"]])
            ref["rid"] = t.new_rid()
            t.refs[ref["rid"]] = ref
            t.tt["references"]["RefIds"].append(ref)
            ovs.append({"m_ElementId": ident, "m_ElementIdsPath": [ident], "m_SerializedData": {"rid": ref["rid"]}})
            d = ref["data"]
        else:
            d = t.refs[o["m_SerializedData"]["rid"]]["data"]
        for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
            d[k], d[k + "_UxmlAttributeFlags"] = 1, 1
    return None


def regle_cartes(t, racine):
    """v31 : « .CL_CARTE { background-color: CARTE_FOND } » dans la feuille intégrée du modèle (une fois), feuille
    rattachée à la racine de la tuile (comme salle_trophees.barre_au_survol) ; spécificité d'une classe (10) :
    la règle de couleurs_interface (tuiles) passe devant"""
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(racine).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)
    sh = t.styles.sh
    if any(p.get("m_Value") == CL_CARTE for r in sh["m_Rules"] for cs in r.get("m_ComplexSelectors") or []
           for s in cs["m_Selectors"] for p in s["m_Parts"]):
        return
    idx = t.styles.add_rule([(PROPRIETES["background-color"][0], "", [(4, CARTE_FOND)])])
    sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": 10, "ruleIndex": idx, "m_Selectors": [
        {"m_Parts": [{"m_Value": CL_CARTE, "m_Type": 3}], "m_PreviousRelationship": 0}]}]


# ---------- la tuile ----------
def construire(t, parent, index, dims, src, p, txt, photo, haut_src, poly_src, rm_model, s_vis, vis, degrade):
    """v3 : la tuile prend toute la largeur ; blocs en parts fixes de la largeur (POIDS : même place pour tous les
    joueurs, rien ne dépend du contenu) ; grille en 2 rangées (traits alignés) ; barre aux couleurs du club"""
    import notes_installations as ni
    v, h = MARGE
    # le setter de la bannière (variables hasContract / teamtodisplay lues par le bloc du club)
    # (élément d'un autre modèle : recopié avec ses enfants, puis vidé ; clone_shallow ne lit que t)
    racine = t.clone(p["setter"], parent, index, src=src.s)
    for k in list(t.children(racine)):
        t.remove(k)
    t.sd(racine)["name"], t.sd(racine)["name_UxmlAttributeFlags"] = NOM, 1
    t.elem(racine)["m_Classes"], t.elem(racine)["m_RuleIndex"] = ["align-self-stretch"], -1
    regle_cartes(t, racine)
    # v25 (le joueur) : plus de cadre (fond, bords, coins) : seul le trait du bas sépare l'en-tête de la fiche
    carte = boite(t, racine, {
        "flex-direction": "row", "align-items": "stretch", "height": dims["haut"], "min-height": dims["haut"],
        "max-height": dims["haut"], "flex-shrink": 0, "flex-grow": 1, "overflow": "hidden",
        "border-bottom-width": 1, "border-bottom-color": BORD,
        "padding-top": v, "padding-bottom": v, "padding-left": h, "padding-right": h,
        "margin-top": dims.get("marge_haut", MARGE_HAUT), "margin-bottom": dims.get("marge_haut", MARGE_HAUT),
        "margin-left": MARGE_COTES,
        "margin-right": MARGE_COTES},
        ["align-self-stretch"])
    # touche de couleur du club (le joueur : « pas une couleur entière », « du haut vers le bas, comme la tuile de
    # base du jeu ») : le dégradé de l'en-tête d'origine recopié (même fonction de couleurs, GradientDirection 11 =
    # TopToBottomWithAlphaTweak, ordre de l'énumération lu dans global-metadata), en fond de toute la tuile,
    # derrière le contenu (1er enfant, position absolue)
    if degrade is not None and DEGRADE_CLUB:
        g = t.clone_shallow(degrade, carte, 0)
        t.sd(g)["name"] = ""
        t.sd(g)["GradientDirection"] = DIRECTION_DEGRADE
        t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = [], -1
        t.styles.style(t, g, {"position": "absolute", "left": 0, "top": 0, "width": {"unit": 2, "value": 100.0},
                              "height": {"unit": 2, "value": 100.0},
                              **{f"border-{c}-radius": RAYON for c in ("top-left", "top-right", "bottom-left",
                                                                        "bottom-right")}})
    e = dims["ecart"]
    msgs = []
    POIDS = {**globals()["POIDS"], **dims.get("poids", {})}   # v18 : parts propres à une bannière

    def sep(dans=None):
        """v24 : écart entre deux cartes (plus de trait)"""
        dans = carte if dans is None else dans
        boite(t, dans, {"width": e, "min-width": e, "max-width": e, "flex-shrink": 0})

    def habille(css, bord=CARTE_BORD, padding=True):
        """v24 : style d'une carte (fond, bord, coins ronds, marges intérieures)"""
        cv_, ch_ = CELLULE
        css.update({"_carte": True,   # v31 : fond CARTE_FOND par la classe (regle_cartes)
                    **{f"border-{c}-width": 1 for c in ("top", "bottom", "left", "right")},
                    **{f"border-{c}-color": bord for c in ("top", "bottom", "left", "right")},
                    **{f"border-{c}-radius": CARTE_RAYON for c in ("top-left", "top-right", "bottom-left",
                                                                    "bottom-right")}})
        if padding:
            css.update({"padding-top": cv_, "padding-bottom": cv_, "padding-left": ch_, "padding-right": ch_})
        return css

    def part(dans, poids, classes, css=None):
        """bloc qui prend poids parts de la largeur (flex-basis 0 : ne dépend pas du contenu, coupe le surplus)"""
        return boite(t, dans, {"flex-grow": poids, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                               "overflow": "hidden", **(css or {})}, classes)

    # photo
    ph = t.clone(photo, carte)
    t.sd(ph)["name"] = ""
    t.elem(ph)["m_Classes"] = ["row-direction-normal", "align-items-center", "justify-content-center"]
    t.styles.style(t, ph, {"flex-shrink": 0, "align-self": "center", "margin-right": e})
    # identité
    ident = part(carte, POIDS["ident"], ["column-direction-normal", "justify-content-center"])
    for k in ("nom", "poste"):
        c = src.clone(t, p[k], ident)
        t.styles.style(t, c, {"flex-shrink": 0, "margin-bottom": 4})
    if haut_src:
        hs, hr = haut_src
        c = t.clone(hr, ident, src=hs)
        t.styles.copy_from(hs.styles, t, c)
        copy_usings(t, hs, hr)
        t.sd(c)["name"] = ""
        t.elem(c)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-bottom-global-gap-small"]
        kids = t.children(c)
        if kids:
            t.elem(kids[0])["m_Classes"] = ["global-text-secondary", "body-sm", "margin-right-global-gap-small"]
    ligne = boite(t, ident, {"flex-shrink": 0}, ["row-direction-normal", "align-items-center"])
    a = src.clone(t, p["actions"], ligne)
    t.sd(a)["name"] = ""
    f = src.clone(t, p["flags"], ligne)
    t.elem(f)["m_Classes"] = ["margin-left-global-gap-regular"]
    sep()
    # grille (v3, le joueur) : 3 carrés côte à côte, séparés par des traits : [Nation + sélections / Âge],
    # [Contrat + temps de jeu / Valeur], [Club seul, toute la hauteur : un joueur prêté a 2 clubs (parent + prêt)] ;
    # trait du milieu des 2 premiers carrés à la même hauteur (et à celle du trait Statut / Éligibilité)
    cv, ch = CELLULE

    def carre(poids, avec_trait):
        if avec_trait:
            sep()
        return part(carte, poids, ["column-direction-normal", "align-self-stretch"])

    def moitie(c, haut_, bord=CARTE_BORD):
        # v24 : une carte (moitié haute ou basse d'une colonne), écart e entre les deux
        css = habille({"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "overflow": "hidden",
                       "justify-content": "center"}, bord)
        css["margin-bottom" if haut_ else "margin-top"] = e // 2
        return boite(t, c, css, ["column-direction-normal", "align-items-center"])   # v25 : centré

    # v4 (le joueur) : en haut Âge | Nation, en bas Salaire (contrat + temps de jeu) | Valeur
    # v13 (le joueur : en Medium, sélections jeunes et 3e pays coupés) : 2 versions de la paire Âge | Nation, chacune
    # avec ses parts (POIDS_PAIRE) : Large (mode == 0 : 3 lettres, une ligne de sélections) et Medium / Small
    # (mode > 0 : noms complets, sélections A et jeunes côte à côte) ; la paire garde la même part de la tuile
    b = s_vis.sd(vis)["Binding"]
    court = None   # v8 : nationalités en 3 lettres (ligne posée par entete_fiche, nations_courtes_large)
    for r in src.s.walk():
        if src.s.name(r) == "UIPickerNationsCourtesLarge-v1" and src.s.children(r):
            court = src.s.children(r)[0]
            break
    if court is None:
        court = p.get("nat3")   # v17 : nation en 3 lettres de la bannière de FM27
    paire = part(carte, POIDS["paire"], ["row-direction-normal", "align-self-stretch"])
    for large, liaison in ((True, ni.equal_binding(b, MODE, 0)), (False, ni.make_binding(b, 4, [MODE], 0))):
        p_age, p_nat = POIDS_PAIRE["large" if large else "autres"]
        zone = ni.new_visible(t, s_vis, vis, paire, None, "", liaison, ["row-direction-normal"])
        t.styles.style(t, zone, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                 "align-self": "stretch", "overflow": "hidden"})
        c1 = part(zone, p_age, ["column-direction-normal", "align-self-stretch"])
        src.clone(t, p["age"], moitie(c1, True))
        centrer(t, src.clone(t, p["contrat"], moitie(c1, False)))   # v26 : salaire / temps de jeu centrés
        sep(zone)
        c2 = part(zone, p_nat, ["column-direction-normal", "align-self-stretch"])
        h1 = moitie(c2, True)
        n = src.clone(t, court if (large and court is not None) else p["nat"], h1)
        t.sd(n)["name"] = ""
        k = src.clone(t, p["caps"], h1)
        t.elem(k)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        cellules = [x for x in t.children(k) if (t.elem(x).get("m_TemplateAlias") or "") == "text-cell-button-medium"]
        if not large:   # sélections A et jeunes côte à côte
            for x in cellules:
                t.elem(x)["m_Classes"] = ["margin-right-global-gap-regular"]
        elif len(cellules) == 2:
            # Large (v6) : une seule ligne : sélections A, ou jeunes avant AGE_JEUNE ans ; tout le détail (A +
            # jeunes) reste dans l'infobulle de FM au survol (InternationalCapsAndGoalsStringIncludingYouth)
            # v35 : A aussi avant AGE_JEUNE ans dès qu'il a joué en A
            ni.selections_une_ligne(t, s_vis, vis, k, cellules, b, AGE_JEUNE)
        src.clone(t, p["valeur"], moitie(c2, False, CARTE_BORD_VALEUR))
    c3 = carre(POIDS["club"], True)
    bc = boite(t, c3, habille({"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "overflow": "hidden",
                               "justify-content": "center"}),
               ["column-direction-normal", "align-items-center"])
    # v9 (le joueur : nom du club mordu en Large) : en Large, contenu du bloc club de FM recopié avec le nom court
    # (primarytext team.Name -> club.ShortName dans ses remappers) ; Medium / Small : nom complet
    # v25 (le joueur : nom coupé net quand il est long) : bloc de FM déplié dans TOUS les modes pour que toute la
    # chaîne rétrécisse (max 100 %, min 0) jusqu'à la cellule du nom (« … » de FM) ; nom complet au survol
    clubs = Src(CLUB)
    cr = clubs.s and clubs.s.children(clubs.s.tt["m_VisualTree"]["rid"])
    cr = cr and clubs.s.children(cr[0])
    if cr:
        for court, liaison in ((True, ni.equal_binding(b, MODE, 0)), (False, ni.make_binding(b, 4, [MODE], 0))):
            nl = ni.new_visible(t, s_vis, vis, bc, None, "", liaison)
            c = clubs.clone(t, cr[0], nl)
            if court:
                for r in t.walk(c):
                    for prop in t.elem(r).get("m_Properties") or []:
                        if prop.get("name") == "mappings" and isinstance(prop.get("value"), str):
                            prop["value"] = prop["value"].replace("primarytext:team.Name:",
                                                                  "primarytext:club.ShortName:")
            msg = club_retrecissable(t, nl)
            if msg:
                msgs.append(msg)
    else:
        src.clone(t, p["club"], bc)
    st = Src(STATUT)

    def statut_cadre(h, nom_titre):
        titre_fm = st.s and first(st.s, lambda r: st.s.name(r) == nom_titre)
        if titre_fm is None:
            msgs.append(f"{STATUT} : {nom_titre} introuvable")
            return
        rm = remapper(t, rm_model, h, {"player": ("person", JOUEUR)}, ["align-self-stretch"])
        c = st.clone(t, st.s.parent[titre_fm], rm)
        t.sd(c)["name"] = ""
        # v36 (2026-11-15, le joueur : « dispo transfert mal aligné dans sa case ») : cadre de FM en align-items-start
        # -> titre et valeur centrés dans la carte
        t.elem(c)["m_Classes"] = ["column-direction-normal", "align-items-center", "justify-content-center"]
        t.styles.style(t, c, {"margin-bottom": 0})   # FM : 8 px dessous (texte remonté)
        return c

    def statut_court(c):
        """v34 (le joueur : « Indisponible » coupé en 2 lignes en Large) : valeur sur une ligne, « … » si elle ne tient
        pas (FM n'a pas de diminutif traduit), texte complet au survol (DisplayTooltipWhenElided)"""
        cent = {"unit": 2, "value": 100.0}
        for r in t.walk(c):
            if not t.name(r).endswith("-value-text") and not t.name(r).endswith("-style-setter"):
                continue
            t.styles.style(t, r, {"max-width": cent, "min-width": 0, "flex-shrink": 1, "overflow": "hidden"})
            if typ(t, r).endswith("SIText"):
                t.styles.style(t, r, {"white-space": "nowrap", "text-overflow": "ellipsis"})
                for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
                    t.sd(r)[k], t.sd(r)[k + "_UxmlAttributeFlags"] = 1, 1

    if "statut_niveau" in POIDS:
        # v32 (le joueur, Large : « fais de la place pour le nom ») : une colonne, en haut Dispo. transfert | Dispo.
        # prêt côte à côte, en bas Niveau / Potentiel ; la place gagnée va à l'identité
        sep()
        col = part(carte, POIDS["statut_niveau"], ["column-direction-normal", "align-self-stretch"])
        # v33 (rapport de supervision qui débordait) : Niveau un peu plus haut que les Dispo., marges du haut / bas
        # réduites dans les cartes
        haut_ = boite(t, col, {"flex-grow": 0.85, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                               "margin-bottom": e // 2}, ["row-direction-normal", "align-self-stretch"])
        for i, nom_titre in enumerate(STATUT_CADRES):
            if i:
                sep(haut_)
            hc = boite(t, haut_, {**habille({"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                             "overflow": "hidden", "justify-content": "center"}),
                                  "padding-top": 3, "padding-bottom": 3},
                       ["column-direction-normal", "align-items-center"])
            c = statut_cadre(hc, nom_titre)
            if c is not None:
                statut_court(c)
                # v37 (le joueur, Large : « Dispo. transfert » sur 2 lignes, plus haut que « Dispo. prêt ») : titre sur
                # une ligne, un cran plus petit (body-xs), « … » + texte complet au survol s'il ne tient pas
                for r in t.walk(c):
                    if t.name(r) == nom_titre and typ(t, r).endswith("SIText"):
                        t.elem(r)["m_Classes"] = ["body-xs" if k == "body-sm" else k
                                                  for k in t.elem(r).get("m_Classes") or []]
                        t.styles.style(t, r, {"white-space": "nowrap", "text-overflow": "ellipsis",
                                              "max-width": {"unit": 2, "value": 100.0}, "overflow": "hidden"})
                        for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
                            t.sd(r)[k], t.sd(r)[k + "_UxmlAttributeFlags"] = 1, 1
        nv = boite(t, col, {**habille({"flex-grow": 1.15, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                                       "overflow": "hidden", "margin-top": e // 2}),
                            "padding-top": 2, "padding-bottom": 2},
                   ["column-direction-normal", "justify-content-center", "align-items-center"])
        src.clone(t, p["scout"], nv)
    else:
        # statut de transfert / prêt l'un sous l'autre, puis niveau à côté (Medium / Small)
        # v4 (le joueur) : colonne étroite, Statut de transfert / Statut de prêt (cadres de la tuile 2x2 de FM, titres
        # traduits par FM compris) ; Éligibilité retirée
        sep()
        col = part(carte, POIDS["statut"], ["column-direction-normal", "align-self-stretch"])
        for i, nom_titre in enumerate(STATUT_CADRES):
            statut_cadre(moitie(col, i == 0), nom_titre)
        # niveau actuel / potentiel (bloc de FM)
        sep()
        nv = part(carte, POIDS["niveau"], ["column-direction-normal", "justify-content-center", "align-items-center"],
                  habille({}))
        src.clone(t, p["scout"], nv)
    # polygone : v24 tout à droite, dans sa carte, dans tous les modes (Small compris)
    if dims["poly"] and poly_src:
        w, hh = dims["poly"]
        # v5 (le joueur : polygone « en très grand une demi-seconde » à l'ouverture) : rien de lié ne tient pendant
        # le chargement d'une fiche (fonctions.md, cale de la fiche 2026-11-12) -> zone de largeur fixe et cale
        # w × hh SANS liaison, qui coupe ce qui dépasse, autour du polygone
        large = w + e + 2 * POLYGONE_MARGE
        zcss = {"width": large, "min-width": large, "max-width": large, "flex-grow": 0, "flex-shrink": 0,
                "align-self": "stretch", "overflow": "hidden"}
        bv = s_vis.sd(vis)["Binding"]
        # v28 (le joueur : « la progression fallait la mettre que sur la vue en petite ») : Progression en Small
        # (mode > 1), polygone en Large / Medium (mode < 2)
        if PROGRESSION:
            zp = ni.new_visible(t, s_vis, vis, carte, None, "", ni.make_binding(bv, 4, [MODE], 1),
                                ["row-direction-normal"])
            t.styles.style(t, zp, dict(zcss))
            sep(zp)
            cpp = boite(t, zp, habille({"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                                        "overflow": "hidden"}),
                        ["column-direction-normal", "align-items-stretch", "justify-content-center"])
            m = tuile_fm(t, cpp, rm_model, MODELE_PROGRESSION,
                         {"person": ("person", JOUEUR), "team": ("person.Team", EQUIPE)})
            if m:
                msgs.append(m)
            else:
                m = habiller_progression(t, cpp, txt)
                if m:
                    msgs.append(m)
            # options fiche_medium_colonne / fiche_large_tuile : Pour / Contre, polygone ou rien selon le mode
            def selon(quoi):
                modes = [m for m in (0, 1) if DROITE[m] == quoi]
                if not modes:
                    return None
                b = ni.make_binding(bv, 0, [MODE], 2) if len(modes) == 2 else ni.equal_binding(bv, MODE, modes[0])
                return ni.new_visible(t, s_vis, vis, carte, None, "", b, ["row-direction-normal"])
            zpc = selon("pc")
            if zpc is not None:
                t.styles.style(t, zpc, dict(zcss))
                sep(zpc)
                msgs += carte_pour_contre(t, zpc, habille)
            if DROITE != {0: "poly", 1: "poly"}:
                zone = selon("poly")
                if zone is None:
                    return msgs
            else:
                zone = ni.new_visible(t, s_vis, vis, carte, None, "", ni.make_binding(bv, 0, [MODE], 2),
                                      ["row-direction-normal"])
            t.styles.style(t, zone, zcss)
        else:
            zone = boite(t, carte, zcss, ["row-direction-normal"])
        sep(zone)
        cp = boite(t, zone, habille({"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                                     "overflow": "hidden"}, padding=False),
                   ["column-direction-normal", "align-items-center", "justify-content-center"])
        pb = boite(t, cp, {"width": w, "min-width": w, "max-width": w, "height": hh, "min-height": hh,
                           "max-height": hh, "flex-grow": 0, "flex-shrink": 0, "overflow": "hidden",
                           "align-self": "center"},
                   ["column-direction-normal", "align-items-center", "justify-content-center"])
        # v11 (le joueur : flash encore, Large et Medium) : graphique dans un SIVisible lié aux données du joueur
        # (person.Age > 0) : caché tant que la fiche n'est pas chargée (un conteneur lié reste caché tant que sa
        # liaison n'est pas lue), il n'apparaît qu'avec les vraies notes
        # v22 : graphique plus grand que la cale (gw × gh), centré dans la cale qui coupe ; rayon en px
        if "rayon_px" in dims:
            gw, gh = round(w * INTERIEUR), round(hh * INTERIEUR)
            rayon = round(dims["rayon_px"] * 100.0 / min(gw, gh), 2)
        else:
            gw, gh, rayon = w, hh, dims.get("rayon", POLYGONE_RAYON)
        fixe = lambda a, b: {"width": a, "min-width": a, "max-width": a, "height": b, "min-height": b,
                             "max-height": b, "flex-grow": 0, "flex-shrink": 0}
        attente = ni.new_visible(t, s_vis, vis, pb, None, "", ni.make_binding(s_vis.sd(vis)["Binding"], 4,
                                                                             ["person.Age"], 0))
        t.styles.style(t, attente, fixe(gw, gh))
        rm = remapper(t, rm_model, attente, {"player": ("person", JOUEUR)})
        t.styles.style(t, rm, fixe(gw, gh))
        ps, pr = poly_src
        import fiche_fmguru as guru
        poly = t.clone(pr, rm, src=ps)
        t.styles.copy_from(ps.styles, t, poly)
        copy_usings(t, ps, pr)
        sd = t.sd(poly)
        sd["SpiderChartRadiusPercentage"] = rayon
        sd["NumberOfInnerRings"] = guru.ANNEAUX_POLYGONE
        sd["LabelsTemplate"]["m_AssetGUID"] = guru.GUID_ETIQUETTES
        t.elem(poly)["m_Classes"] = [x for x in t.elem(poly)["m_Classes"]
                                     if x not in ("justify-content-end", "flex-grow-class", "align-self-stretch")]
        t.styles.style(t, poly, fixe(gw, gh))
    return msgs


def carte_pour_contre(t, parent, habille):
    """Medium (option fiche_medium_colonne = polygone) : carte à la place du polygone, comme l'infobulle du joueur
    (pastilles_pour_contre.contenu) : cadres POUR | CONTRE côte à côte, titres traduits de FM, pastilles de l'en-tête
    (ProConRow, couleur selon la note, texte au survol) ; rangées en trop cachées"""
    import pastilles_pour_contre as ppc
    from hierarchie_pyramide import path_arg
    lst = ppc.src_tree(ppc.LISTE_SOURCE)
    liste = lst and first(lst, lambda r: lst.name(r) == ppc.LISTE and typ(lst, r).endswith("WrappedObjectList"))
    ttr = ppc.src_tree(ppc.TITRES_SOURCE)
    titres = ttr and [first(ttr, lambda r, n=n: ttr.name(r) == n) for n, _ in ppc.LISTES]
    if liste is None or not titres or None in titres:
        return ["carte Pour / Contre (Medium) : liste ou titres de FM introuvables (le jeu a changé ?), ignorée"]
    # v5 (2026-11-15, le joueur : « un bouton Observer comme là où il y a tout l'espace ») : comme la colonne de la
    # fiche (fiche_joueur_plus) : rapport de l'adjoint OU rapport fait = pastilles, sinon phrase de FM + Observer joueur
    import fiche_joueur_plus as fjp
    from arbre import make_visible
    tour = boite(t, parent, habille({"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                                     "overflow": "hidden"}, padding=False),
                 ["column-direction-normal", "align-items-stretch"])
    cl = ["flex-grow-class", "align-self-stretch"]
    adj, autre = fjp.aiguillage_adjoint(t, parent, tour, cl, rapport=PC_RAPPORT)
    oui = make_visible(t, parent, autre, None, PC_RAPPORT + ".HasScoutedInfo", "", list(cl))
    t.elem(oui)["m_RuleIndex"] = -1
    msgs = fjp.sans_rapport(t, autre, parent, rapport=PC_RAPPORT)
    for cible in (adj, oui):
        pastilles_pour_contre(t, cible, liste, lst, titres, ttr, ppc, path_arg)
    return msgs + ["carte Pour / Contre en pastilles à la place du polygone, Observer sans rapport"]


def pastilles_pour_contre(t, parent, liste, lst, titres, ttr, ppc, path_arg):
    pas = ppc.PASTILLE_BANDEAU + 2   # pastille + marges 1 px
    cp = boite(t, parent, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                           "overflow": "hidden", "padding-top": 6, "padding-bottom": 6, "padding-left": 6,
                           "padding-right": 6},
               ["row-direction-normal", "align-items-stretch"])
    for i, (titre_src, (_, chemin)) in enumerate(zip(titres, ppc.LISTES)):
        cadre = boite(t, cp, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden",
                              "background-color": ppc.CADRE_FOND, "border-radius": ppc.CADRE_ARRONDI, "padding": 3,
                              # v3 (le joueur) : titres toujours en haut, à la même hauteur (pas selon le nombre)
                              "justify-content": "flex-start", "padding-top": 6, **({"margin-left": 6} if i else {})},
                      ["column-direction-normal", "align-items-center"])
        ti = t.clone(titre_src, cadre, src=ttr)
        no_styles(t, ti)
        t.sd(ti)["name"] = ""
        t.elem(ti)["m_Classes"] = ["body-sm-strong", "global-text-primary"]
        t.styles.style(t, ti, {"margin-bottom": 2, "flex-shrink": 0})
        # v4 (le joueur) : pastilles centrées en hauteur dans la place sous le titre (titre, lui, reste en haut)
        zone = boite(t, cadre, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                                "overflow": "hidden", "align-self": "stretch", "justify-content": "center"},
                     ["column-direction-normal", "align-items-center"])
        w = t.clone(liste, zone, src=lst)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": PC_GUID_PASTILLE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], PC_RAPPORT + chemin[len("report"):])
        sd["ItemParamName"] = "procon"
        sd["ItemUssClassName"] = "flex-no-shrink-class"   # sinon les pastilles rétrécissent et se chevauchent
        t.elem(w)["m_Classes"] = []
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "wrap", "justify-content": "center",
                              "align-self": "center", "max-width": PC_PAR_RANGEE * pas,
                              "min-height": pas, "max-height": PC_RANGEES * pas,
                              "overflow": "hidden", "flex-shrink": 0})


# ---------- étoiles Niveau / Potentiel sous la note du rapport (joueur hors club) ----------
# 2026-11-07 (le joueur, avant v1.66) : sur la fiche d'un joueur hors club, la carte Niveau / Potentiel ne montrait que
# la note A/B/C : dans PlayerReportHeaderScoutSection, l'aiguillage report.UseCoachReportLayout montre SOIT la note
# (#ScoutReport, recruteur) SOIT les étoiles (#AbilityStarRange, entraîneur = nos joueurs). Le bloc des étoiles de FM
# est recopié sous la note, dans la branche « rapport connu » (report.HasScoutedInfo) : rien avant supervision. Note +
# étoiles centrées. Vue « tuile » seulement (cartes de hauteur fixe : ça tient ; la bannière de FM n'est pas touchée)
MODELE_RAPPORT = "PlayerReportHeaderScoutSection"
PREFIXE_ETOILES = PREFIXE + "Etoiles"
NOM_ETOILES = f"{PREFIXE_ETOILES}-v5"   # v4 (2026-11-13, le joueur, capture Large : « Rapport de supervision » pas
                                        # centré au-dessus de la note) : titre align-self-start de FM -> centré
                                        # v5 (2026-11-15, le joueur : « Potentiel pas centré ») : aussi les titres
                                        # Niveau / Potentiel du bloc d'étoiles de FM (tes joueurs : rapport adjoint)
NOM_TITRE_RAPPORT = PREFIXE_ETOILES + "Titre"   # aiguillage du titre d'origine (Medium / Small) ; + « Large » : petit
TITRE_RAPPORT_LARGE = 10                        # px, titre du rapport en Large (v3)
ETOILES_ECART = 6   # px entre la note et les étoiles


def etoiles_rapport(t):
    """job d'entete_fiche sur PlayerReportHeaderScoutSection"""
    a_nous = [r for r in t.walk() if t.name(r).startswith(PREFIXE_ETOILES)]
    if (vue() == "tuile" and named(t, NOM_ETOILES)) or (vue() != "tuile" and not a_nous):
        return []
    for r in a_nous:   # v2 : le titre du rapport ressorti de son aiguillage
        if r in t.refs and t.name(r) == NOM_TITRE_RAPPORT:
            par = t.parent[r]
            i = t.children(par).index(r)
            for j, k in enumerate(list(t.children(r))):
                move(t, k, par, i + j)
    for r in a_nous:
        if r in t.refs:
            t.remove(r)
    frame = first(t, lambda r: t.name(r) == "Frame")
    if frame is not None:   # FM : marge à droite du cadre (décalait le centre)
        cl = t.elem(frame).get("m_Classes") or []
        if vue() == "tuile":
            t.elem(frame)["m_Classes"] = [c for c in cl if c != "margin-right-global-gap-regular"]
        elif "margin-right-global-gap-regular" not in cl:
            t.elem(frame)["m_Classes"] = cl + ["margin-right-global-gap-regular"]
    titre_fm = first(t, lambda r: t.name(r) == "ScoutReport" and typ(t, r).endswith("SIText"))
    avant, apres = ("align-self-start", "align-self-center-class") if vue() == "tuile" else \
        ("align-self-center-class", "align-self-start")
    if titre_fm is not None:   # v4 : centré en vue tuile, à gauche (FM) sinon
        t.elem(titre_fm)["m_Classes"] = [apres if c == avant else c for c in t.elem(titre_fm).get("m_Classes") or []]
    # v5 : titres Niveau / Potentiel du bloc d'étoiles de FM (rapport de l'adjoint) : centrés en vue tuile
    ab = first(t, lambda r: t.name(r) == "AbilityStarRange")
    for r in (list(t.walk(ab)) if ab is not None else []):
        if t.name(r) in ("CurrentAbilityText", "PotentialAbilityText"):
            t.elem(r)["m_Classes"] = [apres if c == avant else c for c in t.elem(r).get("m_Classes") or []]
    has = first(t, lambda r: t.name(r) == "HasReport")
    kids = has is not None and t.children(has)
    if vue() != "tuile":
        if kids and len(kids) > 1:
            t.elem(kids[1])["m_Classes"] = []   # classes d'origine (aucune)
        return ["étoiles sous la note du rapport retirées (vue de FM)"]
    etoiles = first(t, lambda r: t.name(r) == "AbilityStarRange")
    if etoiles is None or not kids or len(kids) < 2:
        return ["étoiles ou rapport connu introuvables : étoiles non posées"]
    connu = kids[1]   # aiguillage HasScoutedInfo : 0 = pas supervisé, 1 = rapport
    t.elem(connu)["m_Classes"] = ["column-direction-normal", "align-items-center"]
    boite_ = boite(t, connu, {"margin-top": ETOILES_ECART, "flex-shrink": 0},
                   ["column-direction-normal", "align-items-center"], NOM_ETOILES)
    c = t.clone(etoiles, boite_)
    t.sd(c)["name"] = ""
    dedans = set(t.closure(c))
    pot = first(t, lambda r: r in dedans and t.name(r) == "PotentialAbility")
    if pot is not None:   # dernière colonne : pas de marge à droite (centre juste)
        t.elem(pot)["m_Classes"] = [k for k in t.elem(pot).get("m_Classes") or []
                                    if k != "margin-right-global-gap-regular"]
    # v4 (le joueur : « centre le niveau et le potentiel pile au-dessus des étoiles ») : étiquettes centrées
    for r in dedans:
        if t.name(r) in ("CurrentAbilityText", "PotentialAbilityText"):
            t.elem(r)["m_Classes"] = ["align-self-center-class" if k == "align-self-start" else k
                                      for k in t.elem(r).get("m_Classes") or []]
    # v2 (le joueur, Large v32 : carte Niveau en demi-hauteur, rapport qui déborde) : titre « Rapport de supervision »
    # d'origine en Medium / Small (mode > 0) ; v3 (le joueur : « il doit apparaître, juste plus petit ») : en Large
    # (mode == 0) une copie du titre en petit
    msgs = ["rapport de supervision : étoiles Niveau / Potentiel sous la note (vue tuile)"]
    import notes_installations as ni
    titre = first(t, lambda r: t.name(r) == "ScoutReport" and typ(t, r).endswith("SIText"))
    s_vis, vis = ni.visible_model()
    if titre is not None and vis is not None:
        par = t.parent[titre]
        sv = ni.new_visible(t, s_vis, vis, par, t.children(par).index(titre), NOM_TITRE_RAPPORT,
                            ni.make_binding(s_vis.sd(vis)["Binding"], 4, [MODE], 0))
        move(t, titre, sv)
        sl = ni.new_visible(t, s_vis, vis, par, t.children(par).index(sv) + 1, NOM_TITRE_RAPPORT + "Large",
                            ni.equal_binding(s_vis.sd(vis)["Binding"], MODE, 0))
        petit = t.clone(titre, sl)
        t.sd(petit)["name"] = ""
        t.styles.style(t, petit, {"font-size": TITRE_RAPPORT_LARGE, "margin-top": 0, "margin-bottom": 1})
    else:
        msgs.append("rapport de supervision : titre introuvable, gardé en Large")
    return msgs


def hauteur_auto(t, oui):
    """v38 : hauteur du conteneur de FM en auto (oui) ou rendue à la règle de FM (non)"""
    c = first(t, lambda r: t.name(r) == CONTENEUR)
    if c is None:
        return False
    e = t.elem(c)
    old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    reste = [p for p in old if not (p[0] == 131087 and p[2] == [AUTO])]
    if oui:
        e["m_RuleIndex"] = t.styles.add_rule(reste + [(131087, "", [AUTO])])
    elif len(reste) != len(old):
        e["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
    return True


def remettre_fm(t):
    """nos tuiles retirées, bannières / photo de FM remises à leur place"""
    hauteur_auto(t, False)
    for c in [r for r in t.walk() if t.name(r) == NOM_CACHE]:
        par = t.parent[c]
        i = t.children(par).index(c)
        for j, k in enumerate(list(t.children(c))):
            move(t, k, par, i + j)
        t.remove(c)
    for c in [r for r in t.walk() if t.name(r) == NOM_PLACE]:   # v2 : contenu ressorti à la place du conteneur
        par = t.parent[c]
        i = t.children(par).index(c)
        for j, k in enumerate(list(t.children(c))):
            move(t, k, par, i + j)
        t.remove(c)
    for r in [r for r in t.walk() if t.name(r).startswith(PREFIXE)]:
        if r in t.refs:
            t.remove(r)


def job(t):
    """job d'entete_fiche sur PlayerReportHeader"""
    a_nous = [r for r in t.walk() if t.name(r).startswith(PREFIXE)]
    if vue() != "tuile":
        if not a_nous:
            return []
        remettre_fm(t)
        return ["en-tête de FM remis (vue grande tuile retirée)"]
    if named(t, NOM):
        return []
    if a_nous:   # ancienne version : FM remis, puis refait
        remettre_fm(t)
    import notes_installations as ni
    from moteur_photos import ouvrir
    src = Src(SOURCE)
    if src.s is None:
        return [f"{SOURCE} introuvable : grande tuile non posée"]
    p, manque = pieces(src.s)
    if manque:
        return [f"en-tête grande tuile : {', '.join(manque)} introuvable(s) dans la bannière, ignoré"]
    txt = Src("PlayerReportHeaderScoutSection")
    txt_rid = txt.s and first(txt.s, lambda r: typ(txt.s, r).endswith("SIText") and txt.s.name(r) == "ScoutReport")
    photo = first(t, lambda r: t.name(r) == "PersonPictureFrame")
    rm_model = first(t, lambda r: typ(t, r).endswith("BindingRemapper"))
    degrade = first(t, lambda r: typ(t, r).endswith("SIGradient"))   # dégradé du club de l'en-tête d'origine
    o = ouvrir("PlayerAttributesLargeBlock", depart_original=True)
    fa = o and o[3]
    haut = fa and first(fa, lambda r: fa.name(r) == "PersonHeightTextFrame")
    chart = fa and first(fa, lambda r: typ(fa, r).endswith("FMSpiderChart"))
    s_vis, vis = ni.visible_model()
    if None in (txt_rid, photo, rm_model, vis):
        return ["en-tête grande tuile : titre, photo ou modèles introuvables, ignoré"]
    def cacher(r):
        """v9 : élément SANS liaison (taille 0, hors du flux, coupe tout) : v1-v8 = SIVisible « mode == 99 », qui
        laissait voir la bannière de FM pendant le chargement de la fiche (liaison pas encore lue), avec le grand
        polygone de l'en-tête Medium (le joueur : « le polygone flashe trop gros avant »)"""
        par = t.parent[r]
        c = boite(t, par, {"position": "absolute", "left": 0, "top": 0, "width": 0, "height": 0,
                           "max-width": 0, "max-height": 0, "overflow": "hidden"}, [], NOM_CACHE)
        move(t, c, par, t.children(par).index(r))
        move(t, r, c)
        return c

    msgs = []
    bannieres = [r for r in t.walk() if t.elem(r).get("m_TemplateAlias") in TAILLES
                 and t.name(t.parent[r]) != "PhoneSwitch"]
    for r in bannieres:
        dims = TAILLES[t.elem(r)["m_TemplateAlias"]]
        haut_ = t.parent[r]
        place = plain(t, haut_, t.children(haut_).index(r), ["align-self-stretch"], NOM_PLACE)
        t.sd(place)["name_UxmlAttributeFlags"] = 1
        t.elem(place)["m_RuleIndex"] = -1
        move(t, r, place)
        cacher(r)
        msgs += construire(t, place, None, dims, src, p, (txt, txt_rid), photo,
                           (fa, haut) if haut is not None else None, (fa, chart) if chart is not None else None,
                           rm_model, s_vis, vis, degrade)
    cacher(photo)
    if not hauteur_auto(t, True):
        msgs.append(f"en-tête grande tuile : {CONTENEUR} introuvable, hauteur de FM gardée (bas coupé)")
    # pas de photo de FM recopiée en double : les tuiles ont la leur
    return list(dict.fromkeys(msgs)) + [f"en-tête en grande tuile ({len(bannieres)} tailles de fenêtre)"]
