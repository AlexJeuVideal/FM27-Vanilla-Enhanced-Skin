"""Hiérarchie de l'effectif (Effectif > Dynamique de groupe > Hiérarchie) en pyramide, comme dans les anciens FM.

  [ Entraîneur ]              bandeau étroit, sa carte dessous
  [  Leaders d'équipe  ]      bandeau + cartes centrées, qui passent à la ligne dans la largeur du bandeau
  [ Joueurs très influents ]
  [    Joueurs influents     ]
  [        Autres joueurs       ]   (chaque étage plus large que le précédent : forme de pyramide)

Carte = photo + nom + personnalité ; clic sur le nom = fiche (joueur, ou staff pour l'entraîneur) ; clic ailleurs sur
la carte = sélection (« selected-person » de FM, comme la ligne du tableau d'origine : le panneau de droite suit), et
les cartes se colorent comme dans les anciens FM :
- entraîneur choisi : vert = le joueur t'apprécie, rouge = il ne t'aime pas, normal = pas d'avis (seuils des pouces de FM) ;
- joueur choisi : son groupe social en vert (noyau ou groupe secondaire ; « autres » = aucun groupe, rien en vert).
Les titres, nombres de joueurs et flèches de changement de FM sont gardés dans les bandeaux.

Modèles touchés (ce script est leur seul propriétaire, appliquer repart toujours des originaux sauvegardés) :
- SquadHierarchyTableBlock : la liste de gauche de l'écran ; chaque tableau devient une liste à la ligne de FM
  (WrappedObjectList, recopiée de la réunion d'équipe, TeamMeetingBlock).
- PlayerHierarchyCell : petite cellule FM inutilisée (aucune référence dans les bundles), réécrite en carte joueur
  (bouton + photo de PlayerPortraitNameHierarchyCell, textes de PlayerInMeetingCell). Une liste FM ne peut afficher
  que des modèles déjà connus du catalogue du jeu : d'où cette réutilisation.

Menu Outils FM.bat : 18 (catégorie), puis la fonction ; réappliqué par le choix 1.
"""
import copy
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
import notes_installations as ni  # noqa: E402
from notes_installations import first, decode_args, encode_args, _enc_varint  # noqa: E402
from elements import copy_usings, add_using  # noqa: E402
from club_page_bas import original, move  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
# étages : liste FM, largeur du bandeau et de ses cartes (% de la zone), couleur du bandeau (rouge, vert, bleu, opacité)
ETAGES = [
    ("Team.HierarchyTeamLeaders", 40, (0.80, 0.64, 0.16, 0.85)),         # or
    ("Team.HierarchyHighlyInfluential", 60, (0.62, 0.64, 0.68, 0.85)),   # argent
    ("Team.HierarchyInfluential", 80, (0.78, 0.45, 0.16, 0.85)),         # bronze
    ("Team.HierarchyOther", 100, (0.16, 0.38, 0.72, 0.85)),              # bleu
]
ENTRAINEUR = (25, (0.40, 0.42, 0.47, 0.85))   # bandeau de l'entraîneur
# taille des cartes selon le mode d'affichage FM (settings.AdaptiveScalingLevelIndex), pour que la pyramide garde à peu
# près la même place à l'écran : FM agrandit tout en Défaut et rapetisse tout en Condensé.
#   mode : (largeur de la carte px, photo px, textes, écart px)
#   textes : "sm" = classes FM body-sm, "md" = body-md, ou un nombre = taille forcée en px (ignore la taille de texte FM)
MODES = {
    # textes en px forcés : la taille du texte FM (Petit / Normal…) ne fait plus grossir les cartes
    0: (98, 36, 10, 2),    # Défaut (v4 en 114 / 46 / sm : encore trop gros)
    1: (136, 56, 12, 4),   # Détaillé (validé en 136 / 56 avec le texte FM « Petit »)
    2: (164, 68, 14, 4),   # Condensé
}
# taille du texte FM (settings.TextScaling : 0 Petit, 1 Normal, 2 Grand, 3 Plus grand) : elle agrandit tout l'écran.
# Pour les modes listés ici : une carte par taille de texte (MODES = celle du texte Petit). Défaut / Condensé : validés.
TAILLE_TEXTE = "settings.TextScaling"   # valeur texte : Small / Normal / Large / Larger (v6 : pas comparable en entier)
TEXTE_PLUS_GRAND = {
    1: {"Normal": (122, 50, 11, 3),    # Détaillé, texte Normal
        "Large": (110, 44, 10, 2),     # Grand
        "Larger": (98, 36, 10, 2)},    # Plus grand
}
VICE_CAPITAINE = True      # brassard aussi pour le vice-capitaine (icône FM différente)
ENTRAINEUR_PERSONNALITE = False
CARTE_FOND = (0.04, 0.06, 0.12, 0.85)
CARTE_ARRONDI = 6          # px
NOM = "InitialSurname"     # "InitialSurname" (P. Chirivella) ou "Name" (nom complet, peut être coupé)
# couleurs de la sélection (rouge, vert, bleu, opacité), posées sur le fond de la carte
COULEUR_POUR = (0.16, 0.62, 0.30, 0.60)      # t'apprécie / même groupe
COULEUR_CONTRE = (0.78, 0.18, 0.18, 0.60)    # ne t'aime pas
COULEUR_CHOISI = (0.85, 0.87, 0.92, 0.22)    # carte de l'entraîneur quand il est choisi
SEUIL_POUR, SEUIL_CONTRE = 10, -50   # RelationshipValue (-100…100) : pouce levé de FM > 10, pouce baissé <= -50
# =====================================================================================================

VERSION = 11 # v2 : titres des bandeaux sur une ligne ; v3 : vide sous l'entraîneur, i, brassards ; v4 : taille par mode ;
              # v5 : Défaut compact ; v6 : Détaillé selon la taille du texte FM
              # (comparé en entier : aucune carte) ; v7 : comparé en texte, carte Petit par défaut ;
              # v8 : clic sur l'entraîneur = sa fiche staff (avant : fiche joueur, le jeu plantait) ;
              # v9 : nom = fiche, reste de la carte = sélection + couleurs (avis sur toi / groupe social) ;
              # v10 : carte entière = un bouton, design de v8 (v9 : cadres de bouton FM autour du nom / personnalité)
              # v11 (le joueur : fiche ouverte depuis la pyramide = infos manquantes, comme un joueur pas observé) :
              # reportcontextteam = team donné aux cartes (les tableaux FM le donnent à leurs lignes, pas la liste)
SELECTION = "selected-person"   # paramètre du bloc (SquadHierarchyTool), lu par le panneau de droite
CONTEXTE = "reportcontextteam"  # équipe du point de vue de la fiche (FM : TeamHierarchyTableFactory, = team)
TYPE_EQUIPE = 1145176088
RELATION = "binding.RelationshipWithHuman.RelationshipValue"
GROUPE = "SocialGroupCategory"   # 0 noyau, 1 / 2 groupes secondaires, 3 autres (pas un groupe)
GROUPES = (0, 1, 2)
OP_INF_EGAL, OP_SUP = 1, 4
COPIE = (217, 15, 225, 87)   # action FM « copier une valeur » (EditSessionClubRow : Team -> SelectedClub)
CLIC_PERSONNE_SOURCE = "PersonPortraitNameCellWithSecondaryText"   # bouton FM : fiche joueur ou staff selon la personne
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Défaut, 1 Détaillé, 2 Condensé
OP_EGAL = 2
FN_TEXTE_EGAL = "240779c127ba1174a812adf0be56e006"   # SIVisible : texte égal (Boolean 0) / différent (1) d'une valeur
VISIBLE_TEXTE_SOURCE = "NonPlayerAttributesBlock"   # #tactical-style-visible
MODELE = "SquadHierarchyTableBlock"
CARTE = "PlayerHierarchyCell"
GUID_CARTE = "1a2ffd95bb45287429f32f46df9b6982"   # PlayerHierarchyCell (catalogue Addressables)
BOUTON_SOURCE, BOUTON = "PlayerPortraitNameHierarchyCell", "CellButton"   # bouton -> profil, avec la photo
TEXTES_SOURCE = "PlayerInMeetingCell"           # textes nom / personnalité d'une carte de réunion
NOM_INFO_SOURCE = "PlayerNameCell14px"          # cellule nom FM avec le « i » (PlayerReportPreviewTooltip)
BRASSARD_SOURCE = "PlayerRoleIconNameDescriptionCell"   # icônes #CaptainIcon / #ViceCaptainIcon
LISTE_SOURCE, LISTE = "TeamMeetingBlock", "Players"   # liste à la ligne centrée (WrappedObjectList)
PREFIXE = "UIPickerPyramide"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
NOM_CARTE = f"UIPickerCarte-v{VERSION}"
ALIAS_CARTE = "UIPickerCarte"
TYPE_PERSONNE = 1145176065
MARKER = os.path.join(backup.BACKUP_DIR, "hierarchie_pyramide.actif")
CLASSES_CADRE = {"border-color-layout-modules-block-border-colour", "siblock-border"}

for k, v in {"width": (131105, 3), "height": (131087, 3), "flex-direction": (131083, 7), "flex-wrap": (131086, 7),
             "justify-content": (131088, 7), "align-self": (131074, 7), "padding": (262151, 3),
             "border-radius": (262147, 3), "border-color": (262146, 4), "margin-left": (131091, 3),
             "margin-right": (131092, 3), "margin-top": (131093, 3), "margin-bottom": (131090, 3),
             "text-align": (65546, 7), "white-space": (65552, 7), "flex-basis-auto": (131082, 1),
             "position": (131102, 7), "top": (131104, 3), "right": (131103, 3), "font-size": (65537, 3),
             "left": (131089, 3), "bottom": (131080, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)
POURCENT = lambda v: {"unit": 2, "value": float(v)}  # noqa: E731
MOT_AUTO = 2   # StyleValueKeyword.Auto
SANS_CADRE = {**sm.SANS_CADRE, "border-color": (0, 0, 0, 0), "padding": 0}
PLEIN = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def src_tree(model):
    _, _, tt = nb.find_vta(model)
    return Tree(tt) if tt is not None else None


def path_arg(binding, path):
    """liaison de fonction FM (36a81e80 : clé + chemin) avec un autre chemin"""
    b = copy.deepcopy(binding)
    args = decode_args(b["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            p = path.encode()
            a[1] = b"\x01" + _enc_varint(len(p)) + p
    b["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return b


# ---------- la carte joueur (PlayerHierarchyCell réécrit ; copiée telle quelle pour l'entraîneur) ----------
class Sources:
    """morceaux de FM recopiés dans la carte"""

    def __init__(self):
        self.s, self.m = src_tree(BOUTON_SOURCE), src_tree(TEXTES_SOURCE)
        self.n, self.b = src_tree(NOM_INFO_SOURCE), src_tree(BRASSARD_SOURCE)
        s, m, n, b = self.s, self.m, self.n, self.b
        self.btn = s and first(s, lambda r: s.name(r) == BOUTON)
        self.vide = s and first(s, lambda r: s.elem(r).get("m_FullTypeName") == "UnityEngine.UIElements.VisualElement"
                                and not s.elem(r).get("m_TemplateAlias"))   # VisualElement simple (cadre de la cellule)
        self.textes = m and {p: first(m, lambda r, p=p: typ(m, r) == "SIText"
                                      and (m.binding(r, "TextBinding") or "").lower() == p)
                             for p in ("player.person.initialsurname", "player.person.personality")}
        # ligne « i + nom » de FM : VisualElement [SIVisible config.ShowPlayerReportTooltip > PlayerReportPreviewTooltip, nom]
        self.info = n and first(n, lambda r: n.elem(r).get("m_TemplateAlias") == "PlayerReportPreviewTooltip")
        self.ligne = self.info and n.parent[n.parent[self.info]]
        self.icones = b and {nm: first(b, lambda r, nm=nm: b.name(r) == nm) for nm in ("CaptainIcon", "ViceCaptainIcon")}
        self.v, self.vis = ni.visible_model()   # SIVisible FM « entier OP valeur » (BindIntToVisible)
        self.sb, self.svis = ni.visible_model(VISIBLE_TEXTE_SOURCE, FN_TEXTE_EGAL)   # « texte == / != valeur »

    def ok(self):
        return all([self.btn, self.vide, self.textes and None not in self.textes.values(), self.ligne,
                    self.icones and None not in self.icones.values(), self.vis, self.svis])


def texte(t, src, parent, chemin, cls, sources, taille, marge=2):
    """taille : "sm" / "md" (classes FM body-*) ou un nombre (px, forcé)"""
    x = t.clone(src, parent, src=sources.m)
    no_styles(t, x)
    t.sd(x)["TextBinding"] = copy.deepcopy(t.sd(x)["TextBinding"])
    t.sd(x)["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
    t.elem(x)["m_Classes"] = [c.replace("{t}", taille if isinstance(taille, str) else "sm") for c in cls]
    t.styles.style(t, x, {"max-width": POURCENT(100), "min-width": 0, "flex-shrink": 1,
                          "text-align": "middle-center", "margin-top": marge,
                          **({} if isinstance(taille, str) else {"font-size": taille})})
    return x


def visible_entier(t, src, parent, chemin, op, valeur, nom_v):
    """SIVisible « entier OP valeur » (BindIntToVisible de FM)"""
    v = ni.new_visible(t, src.v, src.vis, parent, None, nom_v,
                       ni.make_binding(src.v.sd(src.vis)["Binding"], op, [chemin], valeur))
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.elem(v)["m_RuleIndex"] = -1
    return v


def visible_direct(t, src, parent, chemin, inverse, nom_v):
    """SIVisible sur une donnée directe (objet non vide / booléen), inversé ou non"""
    b = copy.deepcopy(src.v.sd(src.vis)["Binding"])
    b["m_kind"] = 1
    b["m_direct"]["Path"]["m_path"] = chemin
    b["m_visualFunction"]["m_target"]["m_guid"] = ""
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    v = ni.new_visible(t, src.v, src.vis, parent, None, nom_v, b)
    sd = t.sd(v)
    sd["name_UxmlAttributeFlags"] = 1
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = (1 if inverse else 0), 1
    t.elem(v)["m_RuleIndex"] = -1
    return v


def vide(t, src, parent, nom):
    """VisualElement vide (copié du cadre de la cellule FM)"""
    v = t.clone(src.vide, parent, src=src.s)
    for k in list(t.children(v)):
        t.remove(k)
    no_styles(t, v)
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = nom, 1
    return v


def sans_clic(t, r):
    t.sd(r)["pickingMode"], t.sd(r)["pickingMode_UxmlAttributeFlags"] = 1, 1   # PickingMode.Ignore


def evenement_copie(modele, source, cible):
    """événement FM « copier source dans cible » (même forme que les onglets / EditSessionClubRow)"""
    def texte_ev(s):
        b = s.encode()
        return struct.pack("<i", len(b) + 3) + bytes([1, 1, len(b)]) + b
    corps = bytes(COPIE) + b"\x01" + texte_ev(source) + texte_ev(cible) + b"\x00\x00"
    ev = copy.deepcopy(modele)
    ev["m_bytes"] = list(b"\x01\x01\x01\x01\x01" + struct.pack("<i", len(corps)) + corps)
    return ev


def bouton(t, src, parent, nom, events, pleine_largeur=True):
    """bouton vide (celui de la cellule FM) avec les événements voulus, en colonne (sur toute la largeur de la carte,
    ou juste la largeur de son contenu)"""
    b = t.clone(src.btn, parent, src=src.s)
    for k in list(t.children(b)):
        t.remove(k)
    no_styles(t, b)
    t.elem(b)["m_Classes"] = ["align-items-center"]
    t.sd(b)["name"], t.sd(b)["name_UxmlAttributeFlags"] = nom, 1
    t.sd(b)["Events"], t.sd(b)["Events_UxmlAttributeFlags"] = events, 1
    t.styles.style(t, b, {**({"width": POURCENT(100)} if pleine_largeur else
                             {"max-width": POURCENT(100), "align-self": "center"}),
                          "flex-direction": "column", "flex-shrink": 0})
    return b


def calque(t, src, parent, nom, couleur=None):
    """calque plein cadre derrière la carte (sans clic) ; avec couleur : fond coloré arrondi"""
    sans_clic(t, parent)
    t.styles.style(t, parent, PLEIN)
    if couleur:
        f = vide(t, src, parent, nom)
        sans_clic(t, f)
        t.styles.style(t, f, {**PLEIN, "background-color": couleur, "border-radius": CARTE_ARRONDI})


def couleurs_selection(t, src, carte, nom, entraineur=False):
    """couleurs de la carte selon la personne choisie (selected-person)"""
    choix = visible_direct(t, src, carte, SELECTION, False, f"{nom}-Choix")
    calque(t, src, choix, nom)
    choix_entraineur = visible_direct(t, src, choix, f"{SELECTION}.IsPlayer", True, f"{nom}-ChoixEntraineur")
    calque(t, src, choix_entraineur, nom)
    if entraineur:   # la carte de l'entraîneur : juste « choisi »
        calque(t, src, choix_entraineur, f"{nom}-Choisi", COULEUR_CHOISI)
        return
    for op, seuil, couleur, suffixe in ((OP_SUP, SEUIL_POUR, COULEUR_POUR, "Pour"),
                                        (OP_INF_EGAL, SEUIL_CONTRE, COULEUR_CONTRE, "Contre")):
        v = visible_entier(t, src, choix_entraineur, RELATION, op, seuil, f"{nom}-{suffixe}")
        calque(t, src, v, f"{nom}-{suffixe}Fond", couleur)
    choix_joueur = visible_direct(t, src, choix, f"{SELECTION}.IsPlayer", False, f"{nom}-ChoixJoueur")
    calque(t, src, choix_joueur, nom)
    for k in GROUPES:   # même groupe que le joueur choisi (FM ne compare pas deux chemins : un étage par groupe)
        g = visible_entier(t, src, choix_joueur, f"{SELECTION}.{GROUPE}", OP_EGAL, k, f"{nom}-Groupe{k}")
        calque(t, src, g, nom)
        h = visible_entier(t, src, g, f"binding.{GROUPE}", OP_EGAL, k, f"{nom}-MemeGroupe{k}")
        calque(t, src, h, f"{nom}-Groupe{k}Fond", COULEUR_POUR)


def cartes_par_mode(t, parent, src, nom, **kw):
    """une carte par mode d'affichage, chacune dans un SIVisible « mode == k » (les autres ne prennent pas de place)"""
    def visible(sous, chemin, valeur, nom_v):
        return visible_entier(t, src, sous, chemin, OP_EGAL, valeur, nom_v)

    for k, tailles in MODES.items():
        v = visible(parent, MODE_AFFICHAGE, k, f"{nom}-mode{k}")
        nom_k = nom if k == min(MODES) else f"{nom}-{k}"
        if k not in TEXTE_PLUS_GRAND:
            remplir_carte(t, v, src, nom_k, *tailles, **kw)
            continue
        # une carte par taille du texte FM ; celle du texte Petit = « aucune des autres » (s'affiche si la valeur
        # n'est pas lisible : jamais d'étage vide)
        petit = v
        for j in TEXTE_PLUS_GRAND[k]:
            petit = texte_visible(t, src, petit, j, False, f"{nom}-mode{k}-pas{j}")
        remplir_carte(t, petit, src, nom_k, *tailles, **kw)
        for j, tj in TEXTE_PLUS_GRAND[k].items():
            vj = texte_visible(t, src, v, j, True, f"{nom}-mode{k}-texte{j}")
            remplir_carte(t, vj, src, f"{nom_k}-{j}", *tj, **kw)


def texte_visible(t, src, parent, valeur, egal, nom_v):
    """SIVisible « settings.TextScaling == valeur » (egal) ou « != valeur » (fonction FM 240779c1 : texte égal / différent)"""
    b = copy.deepcopy(src.sb.sd(src.svis)["Binding"])
    args = decode_args(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0] == b"SI.VisualScripting.StringVisualArg":
            a[1] = b"\x01" + _enc_varint(len(valeur)) + valeur.encode()
        elif a[0] == b"SI.VisualScripting.BooleanVisualArg":
            a[1] = b"\x00" if egal else b"\x01"   # FM : 1 = visible si différent (« pas vide »)
        elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            a[1] = b"\x01" + _enc_varint(len(TAILLE_TEXTE)) + TAILLE_TEXTE.encode()
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    v = ni.new_visible(t, src.sb, src.svis, parent, None, nom_v, b)
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.elem(v)["m_RuleIndex"] = -1
    return v


def remplir_carte(t, parent, src, nom, largeur, photo, taille, ecart, perso=True, info=True, brassard=True,
                  selection=False, entraineur=False):
    """carte sous parent, pour la personne « binding » ; selection : nom -> fiche, photo / personnalité -> sélection
    + couleurs (la pyramide) ; sinon tout -> fiche (cercles_amis_cartes)"""
    st, s, n = t.styles, src.s, src.n
    fiche = s.sd(src.btn)["Events"]   # bouton de la cellule FM : fiche du joueur (l'entraîneur : remplacé ensuite)
    choisir = evenement_copie(fiche, "binding", SELECTION) if selection else fiche
    # la carte entière = un bouton (sélection ; sans sélection : fiche), comme en v8
    c = bouton(t, src, parent, nom, choisir)
    st.style(t, c, {"width": largeur, "flex-direction": "column", "flex-shrink": 0, "padding": ecart + 2,
                    "border-radius": CARTE_ARRONDI, "background-color": CARTE_FOND,
                    **{f"margin-{c_}": ecart for c_ in ("left", "right", "top", "bottom")}})
    if selection:
        couleurs_selection(t, src, c, nom, entraineur)   # en premier : derrière le reste

    # photo (BindingRemapper person -> binding de la cellule FM)
    photo_rm = t.clone(first(s, lambda r: typ(s, r) == "BindingRemapper", src.btn), c, src=s)
    copy_usings(t, s, first(s, lambda r: typ(s, r) == "BindingRemapper", src.btn))
    t.elem(photo_rm)["m_Classes"] = []
    st.style(t, photo_rm, {"margin-bottom": min(4, ecart)})
    for p in t.children(photo_rm):
        st.style(t, p, {"width": photo, "height": photo})

    # ligne du nom : « i » (infobulle du joueur, comme dans les tableaux FM) + nom ; avec sélection : le nom seul est
    # un bouton -> fiche, sans cadre ni fond (dans le bouton de la carte)
    if selection:
        bn = bouton(t, src, c, f"{nom}-Nom", copy.deepcopy(fiche), pleine_largeur=False)
        st.style(t, bn, {**SANS_CADRE, "background-color": (0, 0, 0, 0), "max-width": POURCENT(100),
                         "align-self": "center", **{f"margin-{c_}": 0 for c_ in ("left", "right", "top", "bottom")}})
    ligne = t.clone(src.ligne, bn if selection else c, src=n)
    no_styles(t, ligne)
    for k in list(t.children(ligne)):
        if typ(t, k) != "SIVisible" or not info:
            t.remove(k)
    if info:
        copy_usings(t, n, src.ligne)
    t.elem(ligne)["m_Classes"] = ["row-direction-normal", "align-items-center", "justify-content-center"]
    marge = 2 if isinstance(taille, str) or ecart >= 4 else 0
    st.style(t, ligne, {"max-width": POURCENT(100), "margin-top": marge})
    texte(t, src.textes["player.person.initialsurname"], ligne, f"binding.{NOM}",
          ["body-{t}-strong", "global-text-primary", "content-ellipsis", "sitext-hover-cursor"], src, taille, marge)
    if perso:
        texte(t, src.textes["player.person.personality"], c, "binding.personality",
              ["body-{t}", "global-text-secondary", "content-ellipsis"], src, taille, marge)

    # brassard en haut à droite (capitaine, vice-capitaine)
    if brassard:
        vis_modele = next(k for k in t.walk(ligne) if typ(t, k) == "SIVisible") if info else None
        for chemin, icone in [("binding.IsCaptain", "CaptainIcon")] + \
                ([("binding.IsViceCaptain", "ViceCaptainIcon")] if VICE_CAPITAINE else []):
            v = t.clone(vis_modele, c, src=t) if vis_modele else t.clone(n.parent[src.info], c, src=n)
            for k in list(t.children(v)):
                t.remove(k)
            no_styles(t, v)
            t.elem(v)["m_Classes"] = []
            t.sd(v)["name"] = f"UIPickerBrassard-{icone}"
            t.sd(v)["Binding"] = copy.deepcopy(t.sd(v)["Binding"])
            t.sd(v)["Binding"]["m_direct"]["Path"]["m_path"] = chemin
            t.sd(v)["InvertDirectBinding"] = 0
            st.style(t, v, {"position": "absolute", "top": ecart + 2, "right": ecart + 2})
            ic = t.clone(src.icones[icone], v, src=src.b)
            no_styles(t, ic)
            t.elem(ic)["m_Classes"] = [cl for cl in t.elem(ic).get("m_Classes") or [] if cl.startswith("game-concepts-")]
    return c


def construire_carte(t, src):
    root = t.children(t.tt["m_VisualTree"]["rid"])
    expect = next((r for r in root if typ(t, r) == "BindingExpect"), None)
    if expect is None:
        return ["modèle de carte introuvable"]
    t.elem(expect)["m_Classes"] = []
    for k in list(t.children(expect)):
        t.remove(k)
    # la personne choisie, lue (couleurs) et écrite (clic) depuis le bloc parent
    params = t.sd(expect).setdefault("Parameters", [])
    for nom, type_id in ((SELECTION, TYPE_PERSONNE), (CONTEXTE, TYPE_EQUIPE)):
        if not any(p["name"] == nom for p in params):
            p = copy.deepcopy(params[0])
            p.update({"name": nom, "type": {"id": type_id}, "isOptional": 1})
            params.append(p)
    cartes_par_mode(t, expect, src, NOM_CARTE, selection=True)
    tailles = ", ".join(f"{m[0]}/{m[1]} px" for m in MODES.values())
    return [f"carte joueur : photo + i + nom ({NOM}) + personnalité + brassard, clic sur le nom = profil, ailleurs = "
            f"sélection (vert / rouge : avis sur l'entraîneur ; vert : groupe social du joueur choisi) ; "
            f"largeur/photo par mode (Défaut, Détaillé, Condensé) : {tailles}"]


# ---------- la pyramide (SquadHierarchyTableBlock) ----------
def bandeau(t, tier, frame, header, largeur, couleur):
    st = t.styles
    t.elem(tier)["m_Classes"] = [c for c in t.elem(tier).get("m_Classes") or [] if c not in CLASSES_CADRE]
    st.style(t, tier, {**SANS_CADRE, "flex-grow": 0})   # FM : l'entraîneur grandissait (grand vide dessous)
    t.elem(frame)["m_Classes"] = [c for c in t.elem(frame).get("m_Classes") or []
                                  if not c.startswith("align-items-")] + ["align-items-center"]
    st.style(t, frame, {"padding": 0, "flex-grow": 0})
    st.style(t, header, {"width": POURCENT(largeur), "align-self": "center", "justify-content": "center",
                         "background-color": couleur, "border-radius": 4, "padding": 4, "margin-bottom": 4})
    kids = t.children(header)
    if kids:   # titre : largeur de son texte (FM : flex 1 0 0 -> largeur nulle une fois centré)
        st.style(t, kids[0], {"flex-grow": 0, "flex-shrink": 0, "flex-basis-auto": MOT_AUTO})
    for k in kids[1:]:
        st.style(t, k, {"margin-left": 16, "flex-grow": 0, "flex-shrink": 0})
    for r in t.walk(header):
        if typ(t, r) == "SIText":
            st.style(t, r, {"white-space": "nowrap"})


def contexte_equipe():
    return {"m_serialisedType": 0, "from": CONTEXTE, "to": {"m_path": "team"}, "type": {"id": TYPE_EQUIPE}}


def construire_bloc(t, src):
    lst = src_tree(LISTE_SOURCE)
    modele_liste = lst and first(lst, lambda r: lst.name(r) == LISTE and typ(lst, r) == "WrappedObjectList")
    s = src.s
    rm_modele = s and first(s, lambda r: typ(s, r) == "BindingRemapper")
    if modele_liste is None or rm_modele is None:
        return ["liste à la ligne ou modèles de FM introuvables"]
    tables = [r for r in t.walk() if typ(t, r) == "StreamedTable"]
    msgs = []
    for k, (chemin, largeur, couleur) in enumerate(ETAGES):
        tbl = next((r for r in tables if r in t.refs and (t.binding(r) or "").lower() == chemin.lower()), None)
        if tbl is None:
            msgs.append(f"tableau {chemin} introuvable")
            continue
        frame = t.parent[tbl]
        tier = t.parent[frame]
        header = t.children(frame)[0]
        bandeau(t, tier, frame, header, largeur, couleur)
        idx = t.children(frame).index(tbl)
        # v11 : liste dans un BindingRemapper reportcontextteam -> team (contexte de la fiche ouverte par une carte)
        rc = t.clone(rm_modele, frame, idx, src=s)
        for kk in list(t.children(rc)):
            t.remove(kk)
        no_styles(t, rc)
        t.elem(rc)["m_Classes"] = []
        t.sd(rc)["name"] = f"{PREFIXE}-Contexte-{k}"
        t.sd(rc)["Mappings"] = [contexte_equipe()]
        t.styles.style(t, rc, {"width": POURCENT(100)})
        w = t.clone(modele_liste, rc, 0, src=lst)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = NOM_RACINE if k == 0 else f"{PREFIXE}-{k}"
        sd["ItemTemplate"] = {"m_AssetGUID": GUID_CARTE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], chemin)
        sd["ItemParamName"] = "binding"
        t.elem(w)["m_Classes"] = ["justify-content-center"]
        t.styles.style(t, w, {"width": POURCENT(largeur), "align-self": "center", "flex-wrap": "wrap",
                              "justify-content": "center", "margin-top": 4})
        t.remove(tbl)
        msgs.append(f"{chemin.split('.')[-1]} : bandeau {largeur} % + cartes")

    # entraîneur : sa carte recopiée en ligne (sans personnalité, sans i ni brassard), BindingRemapper binding -> Team.Manager
    def manager(r):
        b = t.sd(r).get("Binding") or {}
        return b.get("m_kind") == 2 and "Team.Manager" in nb.paths_in(
            b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    mgr = next((r for r in tables if r in t.refs and manager(r)), None)
    if mgr is None:
        msgs.append("tableau de l'entraîneur introuvable")
        return msgs
    switch = t.parent[mgr]
    frame = t.parent[switch]
    tier = t.parent[frame]
    bandeau(t, tier, frame, t.children(frame)[0], *ENTRAINEUR)
    t.styles.style(t, switch, {"align-self": "center", "flex-grow": 0})
    rm = t.clone(rm_modele, switch, t.children(switch).index(mgr), src=s)
    for k in list(t.children(rm)):
        t.remove(k)
    no_styles(t, rm)
    t.elem(rm)["m_Classes"] = []
    t.sd(rm)["name"] = f"{PREFIXE}-Entraineur"
    # v8 (le joueur : clic sur soi = crash, fiche joueur ouverte pour un entraîneur) : « person » aussi, pour le clic
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": nom, "to": {"m_path": "Team.Manager"},
                             "type": {"id": TYPE_PERSONNE}} for nom in ("binding", "person")] + [contexte_equipe()]
    cartes_par_mode(t, rm, src, f"{PREFIXE}-CarteEntraineur", perso=ENTRAINEUR_PERSONNALITE, info=False,
                    brassard=False, selection=True, entraineur=True)
    # clic sur le nom de l'entraîneur = celui de FM qui choisit fiche joueur (person.IsPlayer) ou fiche staff
    p = src_tree(CLIC_PERSONNE_SOURCE)
    bouton = p and first(p, lambda r: typ(p, r) == "SIButton" and (p.sd(r).get("Events") or {}).get("m_bytes"))
    if bouton is None:
        msgs.append(f"clic de l'entraîneur : {CLIC_PERSONNE_SOURCE} introuvable, carte de l'entraîneur sans clic")
    events = copy.deepcopy(p.sd(bouton)["Events"]) if bouton is not None else {"m_bytes": []}
    for r in t.walk(rm):
        if typ(t, r) == "SIButton" and t.name(r).endswith("-Nom"):
            t.sd(r)["Events"] = copy.deepcopy(events)
            t.sd(r)["Events_UxmlAttributeFlags"] = 1 if events["m_bytes"] else 0
    t.remove(mgr)
    msgs.append(f"entraîneur : bandeau {ENTRAINEUR[0]} % + carte, clic sur le nom = sa fiche (staff), ailleurs = "
                f"le choisir (cartes des joueurs selon leur avis sur toi)")
    return msgs


# ---------- ouverture / enregistrement ----------
def ouvrir(modele, depart_original=False):
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
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


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE) or t.name(r).startswith("UIPickerCarte")]


def cmd_appliquer():
    actuels = {m: ouvrir(m) for m in (MODELE, CARTE)}
    if None in actuels.values():
        print("modèles de la hiérarchie introuvables (renommés par une mise à jour ?), ignoré")
        return
    t_bloc, t_carte = actuels[MODELE][3], actuels[CARTE][3]
    if any(t_bloc.name(r) == NOM_RACINE for r in marques(t_bloc)) and \
            any(t_carte.name(r) == NOM_CARTE for r in marques(t_carte)):
        print("hiérarchie en pyramide : déjà appliqué")
    else:
        ancien = bool(marques(t_bloc) or marques(t_carte))
        travail = {m: ouvrir(m, depart_original=True) for m in (MODELE, CARTE)}
        if any(marques(v[3]) for v in travail.values()):
            print("hiérarchie : pas de sauvegarde d'origine propre, ignoré")
            return
        src = Sources()
        if not src.ok():
            print("hiérarchie : morceaux de FM (bouton, textes, i, brassards) introuvables, rien enregistré")
            return
        msgs = construire_carte(travail[CARTE][3], src) + construire_bloc(travail[MODELE][3], src)
        msgs += ["ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"hiérarchie : {m}")
        if any("introuvable" in m for m in msgs):
            print("hiérarchie : rien enregistré")
            return
        for bundle, obj, tt, t in travail.values():
            t.finish()
            t.styles.save()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for m in (MODELE, CARTE):
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


def cmd_etat():
    for m in (MODELE, CARTE):
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        noms = sorted({t.name(r) for r in marques(t)})
        print(f"{m} : " + (f"appliqué ({', '.join(noms)} ; version actuelle v{VERSION})" if noms else "d'origine"))
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
            print("hiérarchie en pyramide : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
