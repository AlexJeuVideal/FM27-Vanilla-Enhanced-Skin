"""Match : tableau de score de base (modèle Scoreboard qui contient #scorebar, bundle du match) redisposé
(maquette « C » choisie par le joueur le 2026-11-10) :

  ligne du haut (bande claire) : [logo] NOM [score dom. sur la couleur du maillot][score ext. sur sa couleur] NOM [logo]
  onglet dessous (cases sombres) : [logo de la compétition] 72:43 +3 / ET  (+ cumul « 4 - 2 AGG » au match retour)

Logos = modèle FM TeamIcon24px (logo du club, drapeau pour une sélection), recopié de GoalScoredPopup. Couleurs du
score = SIStyleSetter de FM (team.KitForMatch.ForegroundColour) qui faisaient les petits traits de couleur. Outline
sombre sur les scores et le temps (lisible si le texte a la couleur du fond).
Tableaux sous licence (Premier League, Ligue des champions…) : autres modèles, pas redisposés (PL : seulement les
noms longs qui passaient sous le score, voir pl()).

Pas de script à lancer : appelé par match_haut (appliquer) et par couleurs_interface.tableau_score (qui repart du
modèle d'origine pour poser ses couleurs, puis redispose).
"""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from elements import plain, move, copy_usings, src_tree, types_ref_manquants  # noqa: E402
import notes_installations as ni  # noqa: E402  (SIVisible de comparaison d'entier : mode d'affichage)

for _k, _v in {"align-items": (131073, 7), "flex-direction": (131083, 7), "align-self": (131074, 7),
               "justify-content": (131088, 7), "top": (131104, 3), "left": (131089, 3), "bottom": (131080, 3), "height": (131087, 3),
               "width": (131105, 3), "width-mot-cle": (131105, 1), "height-mot-cle": (131087, 1),"min-height": (131096, 3),
               "margin-top": (131093, 3), "margin-left": (131091, 3), "margin-right": (131092, 3),
               "margin-bottom": (131090, 3), "padding-bottom": (131098, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "padding-top": (131101, 3),
               "font-size": (65537, 3), "text-outline-color": (65549, 4), "text-outline-width": (65550, 2),
               "position": (131102, 7), "border-bottom-left-radius": (458759, 3),
               "border-bottom-right-radius": (458760, 3), "border-top-left-radius": (458764, 3),
               "border-top-right-radius": (458765, 3), "white-space": (65552, 7), "color": (65536, 4),
               "right": (131103, 3), "overflow": (458768, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
# RÉGLAGES MODIFIABLES
ACTIF = True              # False = tableau de score de FM (match_haut ne le redispose plus)
# v3 « grossis-le » : HAUT + BAS <= 61 (marge du haut 24 + bloc = bandeau de 85 px, panneaux dessous vers 97)
# contenu de la bande = 2 × (LOGO + 12) + 2 × NOM + 2 × (CASE_SCORE + 2) = 280 ; v8 : 370 -> 320 (vide à droite
# et à gauche sur la capture du joueur, « pas trop non plus, un peu d'espace sur les bords » : ~30 px bord -> logo)
# v18 (le joueur : « Ituano », nom court 6 lettres d'un club sans sigle, débordait et poussait la bande) : bande
# 308 -> 344, case du nom fixe 60 -> 78 (6 lettres en 19 px), texte bloqué dans la case
# v19 (« Ituano » sur 2 lignes en v18) : noms 78 -> 86, bande 344 -> 360
# v20 (« Dunde / e » : lettres larges > 86 px) : noms 86 -> 94 + nowrap, bande 360 -> 376
LARGEUR = 376            # px, largeur du bloc (FM 316) ; tout est en largeurs fixes (v1 au contenu = tout tassé)
NOM = 94               # px, largeur FIXE d'un nom (3 lettres, ou 6 pour un club sans sigle) (v8-v17 : 60 mini)
TEMPS = 84                # px, largeur mini du temps
HAUT = 32                 # px, ligne logos / noms / score (v3-v6 : 36)
# v6 : carré du logo de la compétition au-dessus de la bande + onglet du temps dessous : bloc 88 px de haut ;
# match_haut remonte le score (margin-top-16) : fin vers 104 px FM, panneaux vers 117 (capture du joueur)
# v7 : v6 touchait le panneau du dessous (capture : bloc jusqu'à 112, panneau à 115) -> 78 px, fin vers 94
BAS = 24                  # px, onglet du temps (v13 : 22 -> 24, temps sous la barre de progression)
COMP_H = 24               # px, hauteur du carré de la compétition
COMP_CARRE = 42           # px, largeur du carré (plus large que haut : logos larges de certaines compétitions)
COMP_ICONE = 20           # px, hauteur du logo de la compétition
COMP_ICONE_L = 34         # px, largeur maxi du logo (logo réduit en gardant ses proportions)
# v16 (le joueur : 1080p en mise à l'échelle Large, même en plein écran, l'onglet du temps passait sur le panneau du
# dessous) : en Large seulement, tout sur UNE ligne de HAUT px : [carré de la compétition][temps][bande du score] ;
# Medium / Small : 2 lignes comme v13 (v14-v15 : carré seul à gauche, Large puis GridBreakpoint, pas suffisant)
LIGNE_LARGE = True
ECART_LIGNE = 4           # px entre carré / temps / bande (Large)
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Large, 1 Medium, 2 Small
# v18 (le joueur : « 89:52 (+4) » des arrêts de jeu dépassait) : 72 -> 104 (place pour « (+10) »)
ONGLET = 104              # px, largeur de l'onglet du temps (les 2 cases de score = 64)
GAUCHE_L = COMP_CARRE + ECART_LIGNE + ONGLET + ECART_LIGNE   # px à gauche de la bande en Large
ARRONDI = 6               # px, coins du bas de l'onglet
COULEUR_KIT = "BackgroundColour"   # couleur du maillot porté pour le fond du score (même longueur que
                                   # « ForegroundColour » : remplacée dans les octets de la fonction de FM)
BARRE_TEMPS = 3          # px, barre de progression du match (FM), en haut de l'onglet du temps
ARRONDI_BANDE = 6        # px, coins de la bande claire (logos / noms / scores) (FM 2)
LOGO = 30                 # px, case du logo (le logo lui-même reste à 24 px, centré dedans)
LOGO_FM = 24              # px, taille du modèle FM TeamIcon24px
DECALE_SCORE = 1          # px vers le bas : chiffres du score (v3 vus ~2 px trop hauts, place des jambages)
CASE_SCORE = 30           # px, largeur d'une case de score (v10 : 36 -> 30, « vraiment gros »)
CASE_SCORE_H = 26         # px, hauteur d'une case de score (v3-v9 : HAUT - 4 = 28)
TAILLE_NOM = 19           # px, sigles des équipes
TAILLE_SCORE = 17         # px, chiffres du score (v10 : 21 -> 17)
TAILLE_TEMPS = 16        # px, texte de l'onglet (temps, +3, cumul) (v2 : 13)
ROUGES = 5                # px, hauteur des cartons rouges (FM 3), posés au-dessus du tableau
ROUGES_ECART = 3          # px entre les cartons et le haut du tableau
OUTLINE = 1.0            # épaisseur du contour des scores et du temps (0 = aucun)
OUTLINE_COULEUR = (0.0, 0.0, 0.0, 0.85)
# v21 (maquette « B » choisie par le joueur le 2026-11-12) : UNE ligne dans tous les modes d'affichage
#   [logo compétition + temps, fond couleur du skin][logo NOM centré  score (couleur du skin)  NOM centré logo]
#   bande claire de FM (ou score_bande du thème), fondu de la couleur du maillot porté qui part de chaque bout
# "C" = disposition v20 (2 lignes hors Large)
MAQUETTE = "B"
# v23 : couleur FIXE (v21-v22 : var(--colours-base-purple-base) dans le style intégré = crash natif suspect)
COULEUR_SKIN_FM = "#232735"   # v27 : cases de FM (aucun thème / score_fond pas choisi) ; v23-v26 violet #B145E3


TEXTE_FONCE = (35 / 255, 39 / 255, 53 / 255, 1.0)   # #232735, sur une case claire
SEUIL_CLAIR = 0.6         # luminance au-dessus de laquelle le texte passe en foncé (= couleurs_interface)


def couleur_skin():
    """(fond, texte) du bloc temps et de la case du score, en dur : « Tableau de score : cases » de l'app
    (score_fond, v24, demande du joueur), sinon boutons / accent du thème, sinon violet FM ; reposée par
    couleurs_interface.tableau_score quand le thème change"""
    hexa, a = COULEUR_SKIN_FM, 1.0
    try:
        import couleurs_interface as ci
        cfg = CFG_THEME if CFG_THEME is not None else (ci.config() if os.path.exists(ci.MARKER) else None)
        if cfg:
            choix = cfg.get("score_fond")   # v27 : plus de repli boutons / accent (« pas violet » sans thème)
            if choix:
                hexa, a = choix, ci.alpha(choix)
    except Exception:
        pass
    h = hexa.lstrip("#")[:6]
    rgb = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return rgb + (a,), (TEXTE_FONCE if lum >= SEUIL_CLAIR else (1.0, 1.0, 1.0, 1.0))


CFG_THEME = None          # réglages du thème en cours d'application (posé par couleurs_interface.tableau_score)
LISERE = 4                # px, liseré de la couleur du maillot tout au bord gauche / droit de la bande (0 = aucun)
OUTLINE_B = False        # v25 (le joueur) : plus de contour sur le temps / score / cumul en maquette B
BLOC_G = 150              # px, bloc compétition + temps (6 + logo 34 + temps 104 + 6)
TEMPS_B = 104             # px, temps dans ce bloc (« 89:52 (+4) »)
CASE_SCORE_B = 64         # px, case unique du score « 2 - 1 »
# v28 (le joueur : sigles toujours 3 lettres, « réduit mais que ça respire ») : bande 376 -> 296, noms 114 -> 74
LARGEUR_B = 296           # px, bande de la maquette B (noms = (LARGEUR_B - 2 × (LOGO + 12) - CASE_SCORE_B) / 2)
CUMUL_B = 104             # px, case du cumul aller-retour « 1 - 5 Cmb » à droite de la bande (v29)
TAILLE_CUMUL = 12         # px, « Cmb » / « AGG » dans cette case
# v21 en jeu (2026-11-12) : crash natif à l'ouverture du match (ContinuePanel) -> v22 sans fondus pour isoler
FONDUS = False            # True = fondus du maillot (SIGradient sur KitForMatch : SUSPECT du crash v21)
FONDU = 28                # % de la bande couvert par chaque fondu
FONDU_FORCE = 0.75        # opacité du maillot au bord (0..1), 0 au bout du fondu
FONDU_SOURCE = ("NewsDynamicBackground", "CompSIGradient_LeftToRight")   # SIGradient de FM recopié (fonction 9f612110)
FN_DEGRADE = "9f6121106098fd4478470df83d3e70ee"   # couleur (chemin) + opacité début / fin
FONDU_CHEMIN ="team.KitForMatch.BackgroundColour"   # lu dans le BindingRemapper de l'équipe (team = match.HomeTeam…)
# =====================================================================================================

VERSION = "uipicker-score-dispo-v29"   # changer la disposition -> augmenter le numéro
# v29 : cumul aller-retour dans une case de largeur fixe (CUMUL_B), une ligne, fond couleur du skin
# v28 : maquette B plus étroite (bande 296, noms 74 : sigles 3 lettres partout)
# v27 : sans thème (ou cases pas choisies) = couleur des cases de FM #232735, plus le violet
# v26 : liserés de la couleur du maillot (4 px) tout au bord de la bande (traits de couleur de FM)
# v25 : sans contour (temps, score, cumul)
# v24 : bloc temps + case du score = « Tableau de score : cases » de l'app (score_fond), texte foncé si claire
# v23 : v22 crashait encore -> couleur du skin en dur (plus de var()), BindingRemapper d'équipe cachés (pas retirés)
# v22 : v21 sans les fondus (crash v21 à l'ouverture du match)
# v21 : maquette B, une ligne partout (voir MAQUETTE)
# v20 : noms 94 + white-space nowrap (jamais 2 lignes), bande 376
# v19 : noms sur une ligne (texte jamais rétréci, rogné par son aiguillage), cases des noms 86, bande 360
# v18 : bande 344, noms en case fixe de 78 px (texte bloqué dedans : un nom long ne pousse plus rien), onglet du
# temps 96 (arrêts de jeu « +3 » dépassaient)
# v17 : logo source cherché aussi dans le bundle du match (couleurs du score posées = disposition gardée)
# v16 : Large : une ligne compétition / temps / score (SIVisible sur le mode d'affichage) ; bloc 430 de large
# v15 : condition = app.GridBreakpoint Small (compact, ex. fenêtre) au lieu du réglage Large (le match ne le lit pas)
# v14 : Large : carré de la compétition à gauche de la bande (SIVisible sur le mode d'affichage) ; hauteur du bloc
# au contenu (carré du haut caché en Large = 24 px de moins)
# v13 : temps descendu sous la barre de progression (collé dessus en v12), onglet 24 px
# v12 : cases du score : contenu bloqué dans le cadre noir (trait du bas recouvert en v11)
# v11 : fond du score = couleur principale du maillot porté (KitForMatch.BackgroundColour)
# v10 : score plus petit (chiffres 17, cases 30 x 26), bloc 308 de large
# v9 : barre de progression du match en haut de l'onglet du temps (v8 en bas, rognée)
# v8 : bande moins large (320 au lieu de 370, noms 60)
# v7 : resserré de 10 px (v6 touchait le panneau du dessous)
# v6 : logo de la compétition dans un carré posé SUR la bande (au-dessus des scores), temps seul dessous
# v5 : onglet sous les scores : logo de la compétition centré au-dessus du temps (v4 « pas naturel ») ; bande
# arrondie (6 px)
# v4 : logos centrés dans leur case (v3 : ~5 px trop hauts / à gauche), chiffres descendus de 2 px
# v3 : onglet du bas plus grand (26 px, temps en 17) et temps centré sous les scores (marge droite = case de la
# compétition)
# v2 : largeurs fixes partout + flex-shrink 0 (v1 en jeu : bloc tassé à la largeur d'un logo, noms / scores / temps
# écrasés à 0)
MATCH = os.path.join(os.path.dirname(nb.BUNDLES[0]), "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle")
MARKER_MATCH_HAUT = os.path.join(backup.BACKUP_DIR, "match_haut.actif")
MODELE = "Scoreboard"
REPERE = "scorebar"
SOURCE_LOGO = "GoalScoredPopup"
LOGO_ALIAS = "TeamIcon24px"
PREFIXE = "UIPickerScore-"


def _src_logo():
    """GoalScoredPopup (source du logo) : bundles du passage, sinon le bundle du match (couleurs_interface ne cherche
    que gameworld / global : sans ça, poser les couleurs du score faisait sauter la disposition, 2026-11-11)"""
    t = src_tree(SOURCE_LOGO)
    if t is not None or not os.path.exists(MATCH):
        return t
    for o in nb.env_of(MATCH).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != SOURCE_LOGO:
                continue
        except Exception:
            continue
        deja = nb._ecrits.get((MATCH, o.path_id))
        tt = copy.deepcopy(deja) if deja is not None else o.read_typetree()
        if "m_VisualTree" in tt:
            return sm.Tree(tt)
    return None


def actif():
    return ACTIF and os.path.exists(MARKER_MATCH_HAUT)


def modele(bundle=MATCH):
    """(objet, typetree) du Scoreboard de base (celui qui contient #scorebar), état de ce passage compris"""
    for o in nb.env_of(bundle).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != MODELE:
                continue
        except Exception:
            continue
        deja = nb._ecrits.get((bundle, o.path_id))
        tt = copy.deepcopy(deja) if deja is not None else o.read_typetree()
        if "m_VisualTree" in tt and any(sm.Tree(tt).name(r) == REPERE for r in sm.Tree(tt).walk()):
            return o, tt
    return None, None


def _typ(t, r):
    return t.elem(r).get("m_FullTypeName") or ""


def _texte_lie(t, root, chemin):
    return next((r for r in t.walk(root) if _typ(t, r).endswith("SIText") and t.binding(r, "TextBinding") == chemin), None)


def _contient(t, root, pred):
    return any(pred(r) for r in t.walk(root))


def _cls(t, r, retirer=(), ajouter=()):
    e = t.elem(r)
    e["m_Classes"] = [c for c in (e.get("m_Classes") or []) if not c.startswith(tuple(retirer))] + list(ajouter)


def version_posee(t):
    """classe de version posée (« uipicker-score-dispo-vN ») ou None"""
    return next((c for r in t.walk() for c in (t.elem(r).get("m_Classes") or [])
                 if c.startswith("uipicker-score-dispo-")), None)


def deja(t):
    return version_posee(t) == VERSION


def _si_large(t, vis, parent, index, large, nom):
    """SIVisible (copie de vis, BindIntToVisible du Scoreboard) affiché seulement en Large (large) ou seulement hors
    Large (settings.AdaptiveScalingLevelIndex : Large = mode < 1, sinon mode > 0 ; comme tuile_forme.si_large)"""
    b = ni.make_binding(t.sd(vis)["Binding"], 0 if large else 4, [MODE_AFFICHAGE], 1 if large else 0)
    v = ni.new_visible(t, t, vis, parent, index, f"{PREFIXE}{nom}", b)
    t.elem(v)["m_RuleIndex"] = -1
    return v


def disposer(t):
    """t : Tree du Scoreboard de base avec t.styles, PAS encore disposé ; renvoie les messages (« introuvable » =
    rien fait)"""
    if version_posee(t):
        return []
    if MAQUETTE == "B":
        return _disposer_b(t)
    named = {}
    for r in t.walk():
        named.setdefault(t.name(r), r)
    bar = named.get(REPERE)
    rh, ra, tbar = named.get("BindingRemapper_HomeTeam"), named.get("BindingRemapper_AwayTeam"), named.get("time-bar")
    sh, sa = named.get("SIStyleSetter_HColourPrimary"), named.get("SIStyleSetter_AColourPrimary")
    if None in (bar, rh, ra, tbar, sh, sa) or t.parent.get(rh) != t.parent.get(ra):
        return ["tableau de score : morceaux introuvables (le jeu a changé ?), ignoré"]
    bande = t.parent[rh]
    kids = t.children(bar)
    comp = next((k for k in kids if _contient(t, k, lambda r: t.elem(r).get("m_TemplateAlias") == "CompIcon")), None)
    temps = next((k for k in kids if _contient(t, k, lambda r: t.name(r) == "time")), None)
    cumul = next((k for k in kids if t.binding(k) == "match.IsSecondLeg"), None)
    sc_h, sc_a = _texte_lie(t, tbar, "match.MatchHomeScore"), _texte_lie(t, tbar, "match.MatchAwayScore")
    noms = [k for k in t.children(bande) if k not in (rh, ra, tbar)]
    if None in (comp, temps, sc_h, sc_a) or len(noms) != 2 or not t.children(sh) or not t.children(sa):
        return ["tableau de score : morceaux introuvables (le jeu a changé ?), ignoré"]
    src = _src_logo()
    logo_src = src and next((r for r in src.walk() if src.elem(r).get("m_TemplateAlias") == LOGO_ALIAS), None)
    if logo_src is None:
        return [f"tableau de score : logo d'équipe ({LOGO_ALIAS}) introuvable (le jeu a changé ?), ignoré"]
    st = t.styles
    root = t.parent[bar]
    contour = {"text-outline-width": OUTLINE, "text-outline-color": OUTLINE_COULEUR} if OUTLINE else {}

    # bloc entier : 2 lignes, largeur fixe (v1 « au contenu » : tout tassé à la largeur d'un logo en jeu)
    # v16 : hauteur au contenu (2 lignes hors Large, 1 en Large) ; morceaux à hauteur fixe + shrink 0
    # (FM : height 40 dans la règle de la racine -> mot-clé auto = 2) ; largeur fixe = bande + partie gauche du Large
    # (morceaux hors Large calés par margin-left sous la bande)
    vis = None
    if LIGNE_LARGE:
        # modèle : un SIVisible BindIntToVisible du Scoreboard lui-même (#NormalTime)
        vis = next((r for r in t.walk() if _typ(t, r).endswith("SIVisible")
                    and (t.sd(r).get("Binding") or {}).get("m_kind") == 2
                    and t.sd(r)["Binding"]["m_visualFunction"]["m_target"]["m_guid"] == ni.FN_EGAL), None)
        if vis is None:
            return ["tableau de score : SIVisible de FM introuvable (le jeu a changé ?), ignoré"]
        # créés tout de suite (#NormalTime peut partir avec un morceau retiré plus bas), rangés ensuite
        haut = _si_large(t, vis, bar, None, False, "comp-haut")
        bas = _si_large(t, vis, bar, None, False, "temps-bas")
        gauche = _si_large(t, vis, bar, None, True, "gauche")
    large = LIGNE_LARGE
    total = LARGEUR + (GAUCHE_L if large else 0)
    st.style(t, root, ({"height-mot-cle": 2, "min-height": HAUT} if large else {"height": COMP_H + HAUT + BAS})
             | {"width": total, "flex-shrink": 0})
    st.style(t, bar, {"flex-direction": "column", "align-items": "flex-start" if large else "center",
                      "min-width": total, "width": total, "flex-shrink": 0})
    _cls(t, bar, retirer=["row-direction-"], ajouter=[VERSION])

    # ligne du haut = la bande claire de FM, toute la largeur
    st.style(t, bande, {"height": HAUT, "min-height": HAUT, "min-width": LARGEUR, "width": LARGEUR,
                        "align-items": "center", "justify-content": "center", "flex-shrink": 0, "flex-grow": 0,
                        "border-top-left-radius": ARRONDI_BANDE, "border-top-right-radius": ARRONDI_BANDE,
                        "border-bottom-left-radius": ARRONDI_BANDE, "border-bottom-right-radius": ARRONDI_BANDE})
    _cls(t, bande, retirer=["margin-right-"])
    for n in noms:   # blocs des noms : FM 36 px de haut mini + 8 px en haut / en bas
        st.style(t, n, {"flex-shrink": 0})
        for k in t.children(n):
            if _typ(t, k) == "UnityEngine.UIElements.VisualElement":
                st.style(t, k, {"min-height": 0, "padding-top": 0, "padding-bottom": 0, "min-width": NOM,
                                "width": NOM, "max-width": NOM, "height": HAUT, "flex-shrink": 0,
                                "align-items": "center", "justify-content": "center"})
        for k in t.walk(n):
            if _typ(t, k).endswith("SIText"):
                # v19 : texte jamais rétréci (v18 : max-width + shrink = « Ituan / o » sur 2 lignes) ; c'est son
                # aiguillage (club / sélection) qui rogne au bord de la case
                st.style(t, k, {"font-size": TAILLE_NOM, "flex-shrink": 0, "max-width": 1000,
                                "white-space": "nowrap"})
                p = t.parent.get(k)
                if p is not None and p != n and "Switch" in _typ(t, p):
                    st.style(t, p, {"max-width": NOM, "overflow": "hidden", "align-items": "center",
                                    "justify-content": "center"})
        # cartons rouges (SIStepper de FM, en absolu dans le bloc du nom, haut de la bande) : au-dessus du
        # tableau, sur leur équipe
        for k in t.walk(n):
            if _typ(t, k).endswith("SIStepper"):
                st.style(t, k, {"top": -(ROUGES + ROUGES_ECART), "height": ROUGES, "min-height": ROUGES})

    # scores sur la couleur du maillot (dans le setter de FM ; l'autre trait de couleur retiré)
    for remap, setter, score in ((rh, sh, sc_h), (ra, sa, sc_a)):
        for k in t.children(remap):
            if k != setter:
                t.remove(k)
        case = t.children(setter)[0]
        for k in t.children(setter)[1:]:
            t.remove(k)
        move(t, score, case)
        # v11 : couleur PRINCIPALE du maillot porté (FM : ForegroundColour = la 2e couleur, rayures / motif)
        fn = (t.sd(setter).get("BindFunction") or {}).get("m_inputs", {}).get("m_variable", {})
        octets = bytes(fn.get("m_argumentBytes") or [])
        ancien, nouveau = b"team.KitForMatch.ForegroundColour", f"team.KitForMatch.{COULEUR_KIT}".encode()
        if ancien in octets and len(ancien) == len(nouveau):
            fn["m_argumentBytes"] = list(octets.replace(ancien, nouveau))
        st.style(t, remap, {"height": CASE_SCORE_H, "width": CASE_SCORE + 2, "min-width": CASE_SCORE + 2,
                            "flex-grow": 0, "flex-shrink": 0})
        _cls(t, remap, retirer=["flex-grow-class"])
        # v12 : tout tient DANS le cadre noir (1 px) : v11 le chiffre (26 px avec ses marges) poussait la couleur
        # par-dessus le trait du bas
        dedans = CASE_SCORE_H - 2
        st.style(t, setter, {"width": CASE_SCORE, "min-width": CASE_SCORE, "flex-shrink": 0, "flex-grow": 0,
                             "height": dedans, "min-height": 0, "overflow": "hidden"})
        st.style(t, case, {"flex-grow": 0, "width": CASE_SCORE, "min-width": CASE_SCORE, "flex-shrink": 0,
                           "height": dedans, "min-height": 0, "overflow": "hidden",
                           "align-items": "center", "justify-content": "center"})
        st.style(t, score, dict(contour, **{"font-size": TAILLE_SCORE, "top": DECALE_SCORE, "height": dedans,
                                            "min-height": 0, "padding-top": 0, "padding-bottom": 0,
                                            "margin-top": 0, "margin-bottom": 0}))
    t.remove(tbar)   # « - » et case sombre du milieu
    kb = t.children(bande)
    i_h, i_a = kb.index(rh), kb.index(ra)
    if i_a < i_h:
        rh, ra = ra, rh

    # logos de part et d'autre (TeamIcon24px, « team » = l'équipe du côté)
    for remap, cote in ((rh, 0), (ra, None)):
        r = t.clone_shallow(remap, bande, cote)
        t.sd(r)["name"] = f"{PREFIXE}logo-{'dom' if cote == 0 else 'ext'}"
        t.sd(r)["name_UxmlAttributeFlags"] = 1
        t.elem(r)["m_Classes"] = []
        t.elem(r)["m_RuleIndex"] = -1
        st.style(t, r, {"width": LOGO + 12, "min-width": LOGO + 12, "flex-shrink": 0, "align-items": "center",
                        "justify-content": "center"})
        boite = plain(t, r, 0, [])
        t.elem(boite)["m_RuleIndex"] = -1
        st.style(t, boite, {"width": LOGO, "height": LOGO, "min-width": LOGO, "min-height": LOGO, "flex-shrink": 0,
                            "margin-left": 6, "margin-right": 6, "align-items": "center", "justify-content": "center"})
        lg = t.clone(logo_src, boite, src=src)
        sm.no_styles(t, lg)
        # v4 : à sa taille (le logo de TeamIcon24px reste à 24 px, calé en haut à gauche d'une boîte plus grande)
        st.style(t, lg, {"width": LOGO_FM, "height": LOGO_FM, "flex-shrink": 0})
    copy_usings(t, src, logo_src)

    # v6 (le joueur) : petit carré du logo de la compétition posé SUR la bande, au-dessus des scores ; onglet du
    # temps seul sous les scores (+ cumul à sa droite au match retour)
    zero = {"padding-left": 0, "padding-right": 0, "padding-top": 0, "padding-bottom": 0, "flex-grow": 0,
            "flex-shrink": 0, "min-width": 0, "min-height": 0}
    if large:
        # v16 : hors Large, carré du haut / onglet du temps dans des SIVisible « pas Large », calés sous la bande ;
        # Large : ligne = [partie gauche (SIVisible Large) | bande]
        fixe = {"flex-shrink": 0, "flex-grow": 0, "align-self": "flex-start"}
        move(t, haut, bar, 0)
        st.style(t, haut, dict(fixe, **{"width": COMP_CARRE, "height": COMP_H, "min-width": COMP_CARRE,
                                        "min-height": COMP_H, "margin-left": (LARGEUR - COMP_CARRE) // 2}))
        move(t, comp, haut, 0)
        ligne = plain(t, bar, t.children(bar).index(bande), ["row-direction-always-normal"], f"{PREFIXE}ligne")
        t.elem(ligne)["m_RuleIndex"] = -1
        st.style(t, ligne, dict(fixe, **{"flex-direction": "row", "height": HAUT, "min-height": HAUT,
                                         "width": total, "min-width": total, "align-items": "center"}))
        move(t, gauche, ligne, 0)
        move(t, bande, ligne)
        st.style(t, gauche, dict(fixe, **{"flex-direction": "row", "width": GAUCHE_L, "min-width": GAUCHE_L,
                                          "height": HAUT, "min-height": HAUT, "align-items": "center"}))
        move(t, bas, bar)
        st.style(t, bas, dict(fixe, **{"width": ONGLET, "min-width": ONGLET, "height": BAS, "min-height": BAS,
                                       "margin-left": (LARGEUR - ONGLET) // 2}))
    else:
        move(t, comp, bar, 0)
    _cls(t, comp, retirer=["margin-right-", "padding-horizontal-", "row-direction-"])
    st.style(t, comp, dict(zero, **{"height": COMP_H, "width": COMP_CARRE, "align-self": "center",
                                    "flex-direction": "column", "align-items": "center", "justify-content": "center",
                                    "border-top-left-radius": ARRONDI, "border-top-right-radius": ARRONDI,
                                    "border-bottom-left-radius": 0, "border-bottom-right-radius": 0}))
    onglet = plain(t, bas if large else bar, None, ["row-direction-always-normal"], f"{PREFIXE}onglet")
    t.elem(onglet)["m_RuleIndex"] = -1
    st.style(t, onglet, {"height": BAS, "align-self": "flex-start" if large else "center", "align-items": "stretch",
                         "flex-shrink": 0})
    for k in (temps, cumul):
        if k is not None:
            move(t, k, onglet)
            _cls(t, k, retirer=["margin-right-", "padding-horizontal-", "row-direction-"])
    icone = next((r for r in t.walk(comp) if t.elem(r).get("m_TemplateAlias") == "CompIcon"), None)
    if icone is not None:
        _cls(t, icone, retirer=["margin-global-gap-"])
        st.style(t, icone, {"width": COMP_ICONE_L, "height": COMP_ICONE, "min-width": COMP_ICONE_L,
                            "min-height": COMP_ICONE, "flex-grow": 0, "flex-shrink": 0, "margin-top": 0,
                            "margin-bottom": 0, "margin-left": 0, "margin-right": 0})
    # v13 : le haut de l'onglet est pour la barre de progression -> temps centré dans ce qui reste
    st.style(t, temps, dict(zero, **{"height": BAS, "width": ONGLET, "justify-content": "center",
                                     "align-items": "center", "padding-top": BARRE_TEMPS + 1,
                                     "border-top-left-radius": 0, "border-top-right-radius": 0,
                                     "border-bottom-left-radius": ARRONDI, "border-bottom-right-radius": ARRONDI}))
    for r in t.walk(temps):
        if _typ(t, r).endswith("SIText"):
            st.style(t, r, dict(contour, **{"font-size": TAILLE_TEMPS}))
        elif _typ(t, r).endswith("SIProgressBar"):
            # v9 : en haut de l'onglet, juste sous les scores (v8 en bas : rognée par les coins arrondis)
            st.style(t, r, {"height": BARRE_TEMPS, "top": 0})
    if cumul is not None:
        st.style(t, cumul, {"height": BAS, "flex-shrink": 0})
        for r in t.walk(cumul):
            if r == cumul:
                continue
            if _typ(t, r).endswith("SIText"):
                st.style(t, r, dict(contour, **{"font-size": TAILLE_TEMPS, "height": BAS, "margin-bottom": 0}))
            elif t.children(r) and t.parent.get(r) == cumul:
                st.style(t, r, {"flex-direction": "row", "height": BAS, "align-items": "center",
                                "padding-left": 6, "padding-right": 6, "min-width": 70, "flex-shrink": 0})
            elif t.children(r):
                st.style(t, r, {"margin-top": 0, "height": BAS, "align-items": "center"})
    if large:
        # v16 : Large : copies du carré et du temps à gauche de la bande, à sa hauteur, coins arrondis (le cumul du
        # match retour reste dans l'onglet hors Large)
        arrondi = {"border-top-left-radius": ARRONDI_BANDE, "border-top-right-radius": ARRONDI_BANDE,
                   "border-bottom-left-radius": ARRONDI_BANDE, "border-bottom-right-radius": ARRONDI_BANDE}
        comp_g = t.clone(comp, gauche)
        st.style(t, comp_g, dict(arrondi, **{"height": HAUT, "min-height": HAUT, "margin-right": ECART_LIGNE}))
        temps_g = t.clone(temps, gauche)
        st.style(t, temps_g, dict(arrondi, **{"height": HAUT, "min-height": HAUT, "margin-right": ECART_LIGNE,
                                              "overflow": "hidden"}))
    return ["tableau de score : logos, scores sur la couleur des maillots, temps dans un onglet dessous"
            + (" (contour des chiffres)" if OUTLINE_B else "")]


def _src_fondu():
    """modèle source du dégradé (NewsDynamicBackground) : bundles du passage, sinon le bundle gameworld (match_haut
    ne charge que le bundle du match)"""
    s = src_tree(FONDU_SOURCE[0])
    if s is not None:
        return s
    b = os.path.join(os.path.dirname(MATCH), "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle")
    if not os.path.exists(b):
        return None
    for o in nb.env_of(b).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != FONDU_SOURCE[0]:
                continue
            tt = o.read_typetree()
        except Exception:
            continue
        if "m_VisualTree" in tt:
            return sm.Tree(tt)
    return None


def _fondu(t, gsrc, g, remap, bande, index, cote):
    """fondu de la couleur du maillot : copie du BindingRemapper de l'équipe (team = son équipe), en absolu au bout
    de la bande, avec dedans le SIGradient de FM (gauche -> droite) qui lit FONDU_CHEMIN"""
    import struct
    from notes_installations import decode_args, encode_args, _enc_varint
    boite = t.clone_shallow(remap, bande, index)
    t.sd(boite)["name"], t.sd(boite)["name_UxmlAttributeFlags"] = f"{PREFIXE}fondu-{cote}", 1
    t.elem(boite)["m_Classes"], t.elem(boite)["m_RuleIndex"] = [], -1
    pos = {"position": "absolute", "top": 0, "height": {"unit": 2, "value": 100.0},
           "width": {"unit": 2, "value": float(FONDU)}}
    pos["left" if cote == "dom" else "right"] = 0
    t.styles.style(t, boite, pos)
    d = t.clone(g, boite, src=gsrc)
    sm.no_styles(t, d)
    for k in list(t.children(d)):
        t.remove(k)
    s = t.sd(d)
    s["name"], s["name_UxmlAttributeFlags"] = "", 0
    for x in (boite, d):
        if "pickingMode" in t.sd(x):
            t.sd(x)["pickingMode"] = 1   # clics ignorés
    s["GradientDirection"] = 1   # LeftToRight
    f = copy.deepcopy(s["BindGradientFunc"])
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    args[0][1] = b"\x01" + _enc_varint(len(FONDU_CHEMIN)) + FONDU_CHEMIN.encode()
    a0, a1 = (FONDU_FORCE, 0.0) if cote == "dom" else (0.0, FONDU_FORCE)
    args[1][1], args[2][1] = struct.pack("<f", a0), struct.pack("<f", a1)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    s["BindGradientFunc"] = f
    t.elem(d)["m_Classes"] = []
    t.styles.style(t, d, {"width": {"unit": 2, "value": 100.0}, "height": {"unit": 2, "value": 100.0}})


def _disposer_b(t):
    """v21, maquette B : une ligne [compétition + temps sur la couleur du skin][bande : logo nom score nom logo,
    fondus du maillot aux 2 bouts] dans tous les modes d'affichage"""
    named = {}
    for r in t.walk():
        named.setdefault(t.name(r), r)
    bar = named.get(REPERE)
    rh, ra, tbar = named.get("BindingRemapper_HomeTeam"), named.get("BindingRemapper_AwayTeam"), named.get("time-bar")
    if None in (bar, rh, ra, tbar) or t.parent.get(rh) != t.parent.get(ra):
        return ["tableau de score : morceaux introuvables (le jeu a changé ?), ignoré"]
    bande = t.parent[rh]
    kids = t.children(bar)
    comp = next((k for k in kids if _contient(t, k, lambda r: t.elem(r).get("m_TemplateAlias") == "CompIcon")), None)
    temps = next((k for k in kids if _contient(t, k, lambda r: t.name(r) == "time")), None)
    cumul = next((k for k in kids if t.binding(k) == "match.IsSecondLeg"), None)
    textes_score = [r for r in t.children(tbar) if _typ(t, r).endswith("SIText")]
    noms = [k for k in t.children(bande) if k not in (rh, ra, tbar)]
    if None in (comp, temps) or len(noms) != 2 or len(textes_score) != 3:
        return ["tableau de score : morceaux introuvables (le jeu a changé ?), ignoré"]
    src = _src_logo()
    logo_src = src and next((r for r in src.walk() if src.elem(r).get("m_TemplateAlias") == LOGO_ALIAS), None)
    if logo_src is None:
        return [f"tableau de score : logo d'équipe ({LOGO_ALIAS}) introuvable (le jeu a changé ?), ignoré"]
    from notes_installations import decode_args

    def _degrade_fm(r):
        f = gsrc.sd(r).get("BindGradientFunc")
        return (_typ(gsrc, r).endswith("SIGradient") and isinstance(f, dict)
                and f["m_target"]["m_guid"] == FN_DEGRADE
                and len(decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])) == 3)
    gsrc = _src_fondu() if FONDUS else None
    g = gsrc and next((r for r in gsrc.walk() if gsrc.name(r) == FONDU_SOURCE[1] and _degrade_fm(r)), None)
    st = t.styles
    root = t.parent[bar]
    contour = {"text-outline-width": OUTLINE, "text-outline-color": OUTLINE_COULEUR} if OUTLINE_B else {}
    blanc = (1.0, 1.0, 1.0, 1.0)
    skin, texte_skin = couleur_skin()
    total = BLOC_G + LARGEUR_B
    zero = {"padding-left": 0, "padding-right": 0, "padding-top": 0, "padding-bottom": 0, "flex-grow": 0,
            "flex-shrink": 0, "min-width": 0, "min-height": 0, "margin-left": 0, "margin-right": 0}
    arrondi_g = {"border-top-left-radius": ARRONDI_BANDE, "border-bottom-left-radius": ARRONDI_BANDE,
                 "border-top-right-radius": 0, "border-bottom-right-radius": 0}
    arrondi_d = {"border-top-left-radius": 0, "border-bottom-left-radius": 0,
                 "border-top-right-radius": ARRONDI_BANDE, "border-bottom-right-radius": ARRONDI_BANDE}

    # bloc entier : une ligne de HAUT px, largeur fixe (auto = tout tassé en jeu)
    st.style(t, root, {"height": HAUT, "min-height": HAUT, "width": total, "flex-shrink": 0})
    st.style(t, bar, {"flex-direction": "row", "align-items": "center", "min-width": total, "width": total,
                      "height": HAUT, "flex-shrink": 0})
    _cls(t, bar, ajouter=[VERSION])

    # bloc de gauche = la case de la compétition de FM : logo + temps, fond couleur du skin
    _cls(t, comp, retirer=["margin-right-", "padding-horizontal-"])
    st.style(t, comp, dict(zero, **arrondi_g, **{
        "width": BLOC_G, "height": HAUT, "flex-direction": "row", "align-items": "center",
        "justify-content": "center", "background-color": skin, "overflow": "hidden"}))
    icone = next((r for r in t.walk(comp) if t.elem(r).get("m_TemplateAlias") == "CompIcon"), None)
    if icone is not None:
        _cls(t, icone, retirer=["margin-global-gap-"])
        st.style(t, icone, dict(zero, **{"width": COMP_ICONE_L, "height": COMP_ICONE, "min-width": COMP_ICONE_L,
                                         "min-height": COMP_ICONE, "margin-top": 0, "margin-bottom": 0}))
    move(t, temps, comp)
    _cls(t, temps, retirer=["margin-right-", "padding-horizontal-"])
    st.style(t, temps, dict(zero, **{"width": TEMPS_B, "height": HAUT, "justify-content": "center",
                                     "align-items": "center", "background-color": (0, 0, 0, 0)}))
    for r in t.walk(temps):
        if _typ(t, r).endswith("SIText"):
            _cls(t, r, retirer=["text-colours-brand-fm-ultra-violet"])
            st.style(t, r, dict(contour, **{"font-size": TAILLE_TEMPS, "color": texte_skin}))
        elif _typ(t, r).endswith("SIProgressBar"):
            st.style(t, r, {"height": BARRE_TEMPS, "top": HAUT - BARRE_TEMPS})   # en bas du bloc

    # bande : couleur de FM (claire) ou celle du thème (score_bande, posée avant par couleurs_interface, noms en
    # blanc si foncée) ; coins à droite seulement (collée au bloc de gauche)
    sombre = False
    css = dict(arrondi_d, **{"height": HAUT, "min-height": HAUT, "min-width": LARGEUR_B, "width": LARGEUR_B,
                             "align-items": "center", "justify-content": "center", "flex-shrink": 0,
                             "flex-grow": 0, "margin-right": 0,
                             # v25 : visible (cartons rouges posés AU-DESSUS de la bande) ; hidden seulement pour
                             # rogner les fondus aux coins arrondis
                             "overflow": "hidden" if FONDUS else "visible"})
    st.style(t, bande, css)
    _cls(t, bande, retirer=["margin-right-"])
    nom_l = (LARGEUR_B - 2 * (LOGO + 12) - CASE_SCORE_B) // 2
    for n in noms:
        st.style(t, n, {"flex-shrink": 0})
        for k in t.children(n):
            if _typ(t, k) == "UnityEngine.UIElements.VisualElement":
                st.style(t, k, {"min-height": 0, "padding-top": 0, "padding-bottom": 0, "min-width": nom_l,
                                "width": nom_l, "max-width": nom_l, "height": HAUT, "flex-shrink": 0,
                                "align-items": "center", "justify-content": "center"})
        for k in t.walk(n):
            if _typ(t, k).endswith("SIText"):
                st.style(t, k, dict({"font-size": TAILLE_NOM, "flex-shrink": 0, "max-width": 1000,
                                     "white-space": "nowrap"}, **({"color": blanc} if sombre else {})))
                p = t.parent.get(k)
                if p is not None and p != n and "Switch" in _typ(t, p):
                    st.style(t, p, {"max-width": nom_l, "overflow": "hidden", "align-items": "center",
                                    "justify-content": "center"})
            elif _typ(t, k).endswith("SIStepper"):   # cartons rouges : au-dessus du tableau
                st.style(t, k, {"top": -(ROUGES + ROUGES_ECART), "height": ROUGES, "min-height": ROUGES})

    # score : la case du milieu de FM (« 2 - 1 »), fond couleur du skin
    _cls(t, tbar, retirer=["margin-horizontal-"])
    st.style(t, tbar, dict(zero, **{"width": CASE_SCORE_B, "min-width": CASE_SCORE_B, "height": CASE_SCORE_H,
                                    "min-height": 0, "align-items": "center", "justify-content": "center",
                                    "background-color": skin, "border-top-left-radius": 4,
                                    "border-top-right-radius": 4, "border-bottom-left-radius": 4,
                                    "border-bottom-right-radius": 4}))
    for k in textes_score:
        _cls(t, k, retirer=["padding-horizontal-"])
        st.style(t, k, dict(contour, **{"font-size": TAILLE_SCORE, "top": DECALE_SCORE, "color": texte_skin,
                                        "padding-left": 2, "padding-right": 2, "margin-top": 0,
                                        "margin-bottom": 0}))

    # logos (TeamIcon24px, « team » = l'équipe du côté) et fondus, dans des copies des BindingRemapper de FM
    kb = t.children(bande)
    if kb.index(ra) < kb.index(rh):
        rh, ra = ra, rh
    for remap, cote in ((rh, 0), (ra, None)):
        r = t.clone_shallow(remap, bande, cote)
        t.sd(r)["name"] = f"{PREFIXE}logo-{'dom' if cote == 0 else 'ext'}"
        t.sd(r)["name_UxmlAttributeFlags"] = 1
        t.elem(r)["m_Classes"] = []
        t.elem(r)["m_RuleIndex"] = -1
        st.style(t, r, {"width": LOGO + 12, "min-width": LOGO + 12, "flex-shrink": 0, "align-items": "center",
                        "justify-content": "center"})
        boite = plain(t, r, 0, [])
        t.elem(boite)["m_RuleIndex"] = -1
        st.style(t, boite, {"width": LOGO, "height": LOGO, "min-width": LOGO, "min-height": LOGO, "flex-shrink": 0,
                            "margin-left": 6, "margin-right": 6, "align-items": "center", "justify-content": "center"})
        lg = t.clone(logo_src, boite, src=src)
        sm.no_styles(t, lg)
        st.style(t, lg, {"width": LOGO_FM, "height": LOGO_FM, "flex-shrink": 0})
    copy_usings(t, src, logo_src)
    msgs = []
    if g is not None:   # en premier dans la bande : sous les logos / noms / score
        _fondu(t, gsrc, g, rh, bande, 0, "dom")
        _fondu(t, gsrc, g, ra, bande, 1, "ext")
    elif FONDUS:
        msgs.append(f"tableau de score : dégradé de FM ({FONDU_SOURCE[0]}) introuvable, pas de fondu des maillots")
    # v26 : petits traits de couleur de FM = liserés du maillot porté tout au bord de la bande (rien retiré : v23,
    # éléments nommés de FM) ; même liaison que le score v11-v20, vue en jeu (SIStyleSetter 76b11a74 -> fond de
    # l'enfant), chemin ForegroundColour -> BackgroundColour (couleur principale)
    for remap, cote in ((rh, "dom"), (ra, "ext")):
        if not LISERE:
            st.style(t, remap, {"display-mot-cle": 6})
            continue
        _cls(t, remap, retirer=["flex-grow-class", "border-"])
        bord = {"position": "absolute", "top": 0, "height": {"unit": 2, "value": 100.0}, "width": LISERE,
                "min-width": 0, "min-height": 0, "flex-grow": 0, "flex-shrink": 0}
        bord["left" if cote == "dom" else "right"] = 0
        st.style(t, remap, bord)
        setters = [k for k in t.children(remap) if _typ(t, k).endswith("SIStyleSetter")]
        for k in setters[1:]:   # couleur secondaire : cachée
            st.style(t, k, {"display-mot-cle": 6})
        if not setters:
            continue
        s = setters[0]
        fn = (t.sd(s).get("BindFunction") or {}).get("m_inputs", {}).get("m_variable", {})
        octets = bytes(fn.get("m_argumentBytes") or [])
        ancien, nouveau = b"team.KitForMatch.ForegroundColour", f"team.KitForMatch.{COULEUR_KIT}".encode()
        if ancien in octets and len(ancien) == len(nouveau):
            fn["m_argumentBytes"] = list(octets.replace(ancien, nouveau))
        _cls(t, s, retirer=["flex-grow-class"])
        plein = {"width": {"unit": 2, "value": 100.0}, "height": {"unit": 2, "value": 100.0}, "min-width": 0,
                 "min-height": 0, "flex-grow": 0, "flex-shrink": 0}
        st.style(t, s, plein)
        coins = ({"border-top-right-radius": ARRONDI_BANDE, "border-bottom-right-radius": ARRONDI_BANDE}
                 if cote == "ext" else {})
        for c in t.children(s):
            st.style(t, c, dict(plein, **coins))

    # cumul du match retour : case à droite de la bande (hors de la largeur fixe, déborde à droite) ; v29 : largeur
    # fixe CUMUL_B, une ligne « 1 - 5 Cmb », fond couleur du skin (v28 : sans largeur, « Cmb » passait dessous)
    if cumul is not None:
        _cls(t, cumul, retirer=["row-direction-"])
        st.style(t, cumul, dict(zero, **{
            "height": HAUT, "min-height": HAUT, "width": CUMUL_B, "min-width": CUMUL_B, "margin-left": ECART_LIGNE,
            "flex-direction": "row", "align-items": "center", "justify-content": "center", "background-color": skin,
            "overflow": "hidden", "border-top-left-radius": ARRONDI_BANDE, "border-top-right-radius": ARRONDI_BANDE,
            "border-bottom-left-radius": ARRONDI_BANDE, "border-bottom-right-radius": ARRONDI_BANDE}))
        for r in t.walk(cumul):
            if r == cumul:
                continue
            if _typ(t, r).endswith("SIText"):
                _cls(t, r, retirer=["padding-horizontal-", "margin-right-", "text-colours-brand-fm-ultra-violet"])
                agg = t.parent.get(r) != cumul and t.parent.get(t.parent.get(r)) == cumul   # « Cmb » / « AGG »
                st.style(t, r, dict(contour, **{"font-size": TAILLE_CUMUL if agg else TAILLE_TEMPS,
                                                "color": texte_skin, "white-space": "nowrap", "flex-shrink": 0,
                                                "margin-top": 0, "margin-bottom": 0, "margin-right": 0,
                                                "margin-left": 4 if agg else 0, "padding-left": 1,
                                                "padding-right": 1}))
            elif _typ(t, r) == "UnityEngine.UIElements.VisualElement":
                _cls(t, r, retirer=["row-direction-", "padding-horizontal-"])
                st.style(t, r, dict(zero, **{"flex-direction": "row", "align-items": "center",
                                             "justify-content": "center", "height": HAUT}))
    return msgs + ["tableau de score sur une ligne : compétition et temps sur la couleur du skin"
                   + (", fondus des maillots" if g is not None else "")
                   + (" (contour des chiffres)" if OUTLINE_B else "")]


# ---------- option score_licence : notre tableau aussi sur les compétitions sous licence ----------
# FM choisit le tableau par un DynamicItem (OverviewHeader pendant le match, ContinuePanel à la mi-temps / fin) :
# fonction ae0c5ec3 (match.Competition.UniqueId -> table d'assets), PreviewAsset = Scoreboard de base. « notre » :
# DynamicItem rangé dans une boîte display none (rien supprimé : retour en arrière = le remettre), et à sa place le
# Scoreboard de base inclus en dur (modèle inclus par son GUID).
OPTION = "score_licence"
OPTION_VALEURS = ("licence", "notre")
BASE_GUID = "67150a05d1cd6304a92ccda211557611"   # Scoreboard de base (clé du catalogue)
ALIAS_PARTOUT = "UIPickerScoreboard"
NOM_CACHE, NOM_PARTOUT = f"{PREFIXE}licence-cache", f"{PREFIXE}partout"
sm.PROPRIETES.setdefault("display-mot-cle", (131081, 1))


def notre_partout():
    force = os.environ.get("UIPICKER_OPTION_SCORE_LICENCE")   # bancs
    if force in OPTION_VALEURS:
        return force == "notre"
    try:
        import options
        return options.get(OPTION) == "notre"
    except Exception:
        return False


def licence(t):
    """OverviewHeader / ContinuePanel : selon l'option, tableau sous licence de FM ou le nôtre partout"""
    if not ACTIF:
        return []
    named = {t.name(r): r for r in t.walk()}
    cache, partout = named.get(NOM_CACHE), named.get(NOM_PARTOUT)
    if notre_partout():
        if partout is not None:
            return []
        dyn = next((r for r in t.walk() if _typ(t, r).endswith("DynamicItem")
                    and (t.sd(r).get("PreviewAsset") or {}).get("m_AssetGUID") == BASE_GUID), None)
        if dyn is None:
            return ["choix du tableau de score par compétition introuvable (le jeu a changé ?), ignoré"]
        par = t.parent[dyn]
        if "Switch" in _typ(t, par):
            return ["tableau de score dans un aiguillage (le jeu a changé ?), ignoré"]
        modele_inclus = next((r for r in t.walk() if t.elem(r).get("m_TemplateAlias")), None)
        if modele_inclus is None:
            return ["modèle inclus à recopier introuvable, ignoré"]
        # notre tableau à la place exacte du DynamicItem (1er enfant du SIStyleSetter qui pose fm-scoreboard), la
        # boîte cachée juste après
        i = t.children(par).index(dyn)
        boite = plain(t, par, i + 1, [], NOM_CACHE)
        t.sd(boite)["name_UxmlAttributeFlags"] = 1
        t.elem(boite)["m_RuleIndex"] = -1
        t.styles.style(t, boite, {"display-mot-cle": 6})
        move(t, dyn, boite)
        tp = t.clone_shallow(modele_inclus, par, i)
        t.elem(tp)["m_TemplateAlias"] = ALIAS_PARTOUT
        t.elem(tp)["m_Classes"] = list(t.elem(dyn).get("m_Classes") or [])
        t.elem(tp)["m_RuleIndex"] = -1
        t.sd(tp)["templateId"] = ALIAS_PARTOUT
        t.sd(tp)["name"] = NOM_PARTOUT
        t.sd(tp)["name_UxmlAttributeFlags"] = 1
        us = t.tt.setdefault("m_Usings", [])
        if not any(u.get("alias") == ALIAS_PARTOUT for u in us):
            us.append({"alias": ALIAS_PARTOUT, "path": BASE_GUID, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return ["notre tableau de score aussi sur les compétitions sous licence"]
    if cache is None:
        return []
    par = t.parent[cache]
    i = t.children(par).index(cache)
    for k in list(t.children(cache)):
        move(t, k, par, i)
    t.remove(cache)
    if partout is not None:
        t.remove(partout)
    t.tt["m_Usings"] = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") != ALIAS_PARTOUT]
    return ["compétitions sous licence : leur propre tableau de score remis"]


# ---------- tableau sous licence Premier League : nom long qui passe sous le score ----------
# Modèle « Scoreboard » de la PL (classes pl-licensed-scoreboard-team) : cases d'équipe de 120 px, bloc du score
# (120 px, en absolu, centré) posé par-dessus -> ~50 px pour le nom. Le nom = 3 lettres, sinon le nom court 6 lettres
# du club (« Man C ») qui passait sous le score. Cases élargies, nom bloqué avant le bloc du score (… si trop long).
PL_CLASSE = "pl-licensed-scoreboard-team"
PL_LARGEUR = {PL_CLASSE: 160, PL_CLASSE + "-cjk": 200}   # px, case d'une équipe (FM 120 / 180 en CJK)
PL_BLOC_SCORE = 120       # px, bloc du score de FM (ne pas changer : lu dans le modèle)
PL_MARGE = 12             # px, padding de la case + petit écart avant le score
PL_VERSION = "uipicker-score-pl-v1"


def pl_modele(bundle=MATCH):
    for o in nb.env_of(bundle).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != MODELE:
                continue
        except Exception:
            continue
        deja_ecrit = nb._ecrits.get((bundle, o.path_id))
        tt = copy.deepcopy(deja_ecrit) if deja_ecrit is not None else o.read_typetree()
        if "m_VisualTree" in tt and any(PL_CLASSE in (sm.Tree(tt).elem(r).get("m_Classes") or [])
                                        for r in sm.Tree(tt).walk()):
            return o, tt
    return None, None


def pl(t):
    """t : Tree du tableau PL avec t.styles ; renvoie les messages"""
    if any(c.startswith("uipicker-score-pl-") for r in t.walk() for c in (t.elem(r).get("m_Classes") or [])):
        return []   # une seule version pour l'instant (v1) : déjà posée
    n = 0
    for r in list(t.walk()):
        cls = t.elem(r).get("m_Classes") or []
        cle = next((c for c in cls if c in PL_LARGEUR), None)
        if cle is None or not _typ(t, r).endswith("SIText"):
            continue
        case = t.parent.get(r)
        while case is not None and not _typ(t, case).endswith("SIStyleSetter"):
            case = t.parent.get(case)
        if case is None:
            continue
        w = PL_LARGEUR[cle]
        t.styles.style(t, case, {"width": w})
        t.styles.style(t, r, sm.LARGEUR_MAX(w - PL_BLOC_SCORE // 2 - PL_MARGE))
        n += 1
    if n == 0:
        return ["noms d'équipe du tableau PL introuvables (le jeu a changé ?), ignoré"]
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    _cls(t, racine, ajouter=[PL_VERSION])
    return [f"tableau Premier League : cases d'équipe élargies, nom long bloqué avant le score ({n} noms)"]


def appliquer_pl(bundle=MATCH):
    obj, tt = pl_modele(bundle)
    if tt is None:
        print("Scoreboard Premier League : introuvable (le jeu a changé ?), ignoré")
        return
    t = sm.Tree(tt)
    t.styles = sm.Styles(bundle, tt)
    msgs = pl(t)
    for m in msgs or ["déjà appliqué"]:
        print(f"Scoreboard PL : {m}")
    if [m for m in msgs if "introuvable" not in m]:
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt
        nb._dirty.add(bundle)


def appliquer(bundle=MATCH):
    """passage autonome (match_haut) : redispose le Scoreboard de base tel qu'il est dans ce passage"""
    appliquer_pl(bundle)
    if not ACTIF:
        return
    obj, tt = modele(bundle)
    if tt is None:
        print(f"{MODELE} (tableau de score) : introuvable (le jeu a changé ?), ignoré")
        return
    t = sm.Tree(tt)
    t.styles = sm.Styles(bundle, tt)
    pre = []
    if version_posee(t) and not deja(t):   # ancienne disposition : on repart du modèle d'origine (et de sa feuille)
        from club_page_bas import original
        orig = original(bundle, obj)
        feuille = orig and original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if orig is None or feuille is None:
            print(f"{MODELE} : ancienne disposition mais pas de sauvegarde d'origine, laissée")
            return
        tt.clear()
        tt.update(orig)
        t = sm.Tree(tt)
        t.styles = sm.Styles(bundle, tt)
        t.styles.sh, t.styles.changed = feuille, True
        pre = ["ancienne disposition retirée (couleurs du tableau : reposées par couleurs_interface)"]
    msgs = pre + disposer(t)
    for m in msgs or ["déjà appliqué"]:
        print(f"{MODELE} : {m}")
    if [m for m in msgs if "introuvable" not in m]:
        t.finish()
        t.styles.save()
        for n in types_ref_manquants(obj, tt):   # v21 : SIGradient des fondus
            print(f"{MODELE} : type {n} déclaré dans le bundle (recopié)")
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt
        nb._dirty.add(bundle)
