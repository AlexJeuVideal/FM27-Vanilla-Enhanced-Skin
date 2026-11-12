"""Recrutement > Joueurs recommandés > Rapports : rapport du recruteur façon FM24, avec les attributs (tous les modes).

  [ attributs (Technique / Mental / Physique)     ] | [ recommandation, niveau / potentiel     ]
  [ Pour / Contre                                 ] | [ infos transferts (sans efficacité, v19)  ]
                                                    | [ matchs observés, rôle, comparaison     ]

Modèle PlayerRecommendationsMainBlock (#combined-info-block, sous l'en-tête du recruteur) :
- une copie réorganisée (SIVisible mode >= 0, tous les modes) : à gauche (2/3) le tableau d'attributs de la
  fiche (AttributesTableTemplate, comme l'infobulle du joueur : person = le joueur du rapport, rolemask vide) puis les
  Pour / Contre ; à droite (1/3) le contenu des colonnes gauche et droite de FM, l'une sous l'autre. Trop haut : la zone
  du rapport défile (SIScrollView de FM). À droite (club), les infos transferts passent avant l'efficacité tactique.
- le bloc de FM gardé, affiché seulement dans un message (paramètre isMessage : message « Mise à jour des
  recherches », trop bas pour la copie) ; les copies dans un SIVisible hors message (v18).
Idée du joueur (2026-11-12, capture FM24) ; v1 en Large seulement (validé en jeu : « très bien »), v2 : tous les modes.

Rapport du recruteur dans un message (ScoutingReportBlock_Large / _Small, demande du joueur : « jamais la place pour
Pour / Contre ») : le tableau d'attributs à la place de Pour / Contre (gardés, cachés), Infos du joueur en haut de la
colonne de droite ; la recommandation, le niveau et les infos transferts restent à gauche.

Le modèle est aussi réécrit par Kinito (kinito_rapports_vues, 26.5 : tableau et menu des vues, depuis l'original) :
ce script travaille sur le modèle tel qu'il est, passe après lui (catalogue : ORDRE_SKIN, SUIVANTS) et ne touche pas
à ses morceaux. Retirer = défaire ses deux SIVisible (pas de retour à l'original, qui effacerait Kinito).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\recrutement\\rapport_recrutement_fm24.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\recrutement\\rapport_recrutement_fm24.py retirer [--dry-run]
  .venv\\Scripts\\python.exe outils\\recrutement\\rapport_recrutement_fm24.py etat
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
from elements import move, copy_usings, src_tree, plain, TYPE_PERSONNE  # noqa: E402
from notes_installations import visible_model, new_visible, make_binding  # noqa: E402
import arbre  # noqa: E402
import style_mediatique as sm  # noqa: E402  (titre traduit « Style médiatique »)
from attributs_tout_cocher import ouvrir  # noqa: E402  (fiche d'origine sauvegardée : bouton et polygone)
import fiche_fmguru as guru  # noqa: E402  (réglages du polygone de la vue Guru, validés en jeu)
import fiche_joueur_plus as fjp  # noqa: E402  (conteneur -> élément BindingVariables)

for _k, _v in {"max-height": (131094, 3), "position": (131102, 7), "left": (131089, 3), "top": (131104, 3),
               "right": (131103, 3), "bottom": (131080, 3), "max-width": (131095, 3),
               "white-space": (65552, 7)}.items():
    arbre.PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
PART_GAUCHE, PART_DROITE = 2, 1    # largeurs relatives : attributs + Pour / Contre | infos du recruteur
PART_INFOS, PART_RECO = 2, 3       # en haut à droite : Infos du joueur | recommandation, niveau, transferts (v21 /
#   message v9, le joueur : Infos allait jusqu'à droite et écrasait la note, le niveau et les infos transferts)
# =====================================================================================================

VERSION = 22                                        # v19 : sans l'efficacité tactique (plantage, voir copie()) ;
#   v20 (2026-11-05, le joueur) : notre rapport aussi dans le message « Mise à jour des recherches » (hauteur naturelle)
#   v21 : Infos limité en largeur (PART_INFOS), textes à la ligne
#   v22 (2026-11-11, le joueur : « Mise à jour des recherches » lent) : copies hors message / dans le message dans un
#   aiguillage isMessage (BindableSwitchElement, AlwaysInstantiate 0 : seul l'enfant choisi est construit ; avec les
#   SIVisible, les 3 copies étaient construites partout)
SWITCH_MESSAGE = "IsMessageSwitch"                  # aiguillage de FM sur isMessage (enfant 0 : hors message, 1 : message)
NOM_SWITCH = f"UIPickerRapportSwitch-v{VERSION}"
ECART_INFOS = "margin-bottom-global-gap-large"      # entre les lignes d'Infos (demande du joueur : plus aéré)
HAUTEUR_LIGNE_FM, HAUTEUR_LIGNE_LARGE = 28.0, 21.0  # lignes d'attributs (FixedElementSize) : FM | copie Large
#   (v12 : 24, pieds du gardien encore sous l'écran)
POLYGONE = "polygonselected"                        # variable du bouton polygone (comme la fiche) ; coché : le
#   polygone de la fiche à la place de Pour / Contre
VARIABLE_POLYGONE = {"m_name": POLYGONE, "m_scopeValue": {"m_serializedData": "Bool|0|"}}
COLONNE_POLYGONE = "AttributeSpiderChart"           # colonne du polygone dans la fiche (aiguillage polygonselected)
ACTIONS = "ScoutingCentreActionsButtons"            # boutons Actions / Ignorer / Conserver (bandeau du recruteur)
HAUTEUR_POLYGONE_LARGE = 380                        # Large : colonne qui défile, le polygone a une hauteur fixe
#   (v15 : 330 ; v16 : 440, coupé en bas en jeu)
RAYON_POLYGONE = 40.0                               # % de sa boîte (FM : 34,8 ; v15 : 24 de la vue Guru, trop petit
#   à la place du tableau : « augmente la taille du polygone partout »)
RESTE = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0}   # prend la hauteur qui reste
SERRE = {"flex-grow": 1, "flex-shrink": 1, "min-height": 0}   # hauteur du contenu, serrée si pas la place (base auto)
MODELE = "PlayerRecommendationsMainBlock"
BLOC = "combined-info-block"
COLONNES_FM = ["LeftColumn", "RightColumn"]          # empilées à droite, dans cet ordre
POUR_CONTRE = "ScoutedProsAndCons"                   # dans #MiddleColumn ; aussi le nom de son modèle
PC_RANGEE, PC_COLONNES = "middle-column", ("pros", "cons")   # dans le modèle : Pour | Contre côte à côte
PIEDS, PIEDS_MOITIES = "PlayerReportFootednessBlock", ("LeftFootTextFrame", "RightFootFrame")   # centrés
INFOS, INFOS_TITRE, INFOS_RANGEE = "InfoBlockFrame", "InfoBlockHeaderFrame", "Frame"   # dans ATTRIBUTS[0]
MATCHS = "MatchesWatched"                            # retiré (demande du joueur : la page tient sans défiler)
RECO, SWITCH_CLUB = "ScoutRecommendationBlock", "BindableSwitchElement-IsClub"   # haut de la colonne de droite
MEDIAS = "mediahandling"                             # person.MediaHandling (style médiatique)
DEFILEMENT = "SIScrollView"                          # SIScrollView de FM (zone du rapport), copié pour Pour / Contre
CLUB, EFFICACITE = "VisualElement-ClubTeam", "SIVisible-ShowTacticalEffectiveness2"   # club : trait + infos
#   transferts remontés au-dessus de l'efficacité tactique (demande du joueur)
TRAIT_VERTICAL, TRAIT_HORIZONTAL ="VerticalDivider1", "HorizontalDivider1"
JOUEUR = "player"                                    # paramètre du bloc (une personne)
ATTRIBUTS = ("PlayerAttributesLargeBlock", "AttributesTableTemplate")    # modèle inclus recopié de la fiche
VARIABLES_SOURCE = ("PlayerAttributesTooltipBlock", "rolemask")          # « rolemask » vide, comme l'infobulle
VARIABLES_MODELE = "BindingVariables_FM"             # élément BindingVariables de FM, dans ce modèle
REMAPPER_MODELE = "BindingRemapper-WhoScouted"       # élément BindingRemapper de FM, dans ce modèle
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Large, 1 Medium, 2 Small
MODE_LARGE, MODE_MEDIUM = 0, 1
OP_FM24, OP_LARGE, OP_FM = 3, 2, 0                   # mode >= Medium (Medium / Small) / = Large / < 0 (aucun)
PREFIXE = "UIPickerRapport"
NOM_FM24 = f"{PREFIXE}FM24-v{VERSION}"               # SIVisible : la copie réorganisée (Medium / Small)
NOM_LARGE = f"{PREFIXE}FM24Large-v{VERSION}"         # SIVisible : la copie réorganisée (Large, colonnes qui défilent)
NOM_FM = f"{PREFIXE}FM-v{VERSION}"                   # SIVisible : le bloc de FM, affiché seulement dans un message
NOM_HORS_MSG = f"{PREFIXE}HorsMessage-v{VERSION}"    # SIVisible : les 2 copies, hors message (v18)
NOM_DANS_MSG = f"{PREFIXE}DansMessage-v{VERSION}"    # SIVisible : copie à hauteur naturelle, dans le message (v20)
MESSAGE = "isMessage"                                # paramètre du bloc : vrai dans le message « Mise à jour des
#   recherches » (PlayerRecommendationsOverviewBlock), trop bas pour la copie (écrasée, v17 vue en jeu 2026-10-30)
ENVELOPPES = (f"{PREFIXE}FM", f"{PREFIXE}HorsLarge")    # SIVisible autour du bloc de FM (v2, v1)
MARKER = os.path.join(backup.BACKUP_DIR, "rapport_recrutement_fm24.actif")
# rapport du recruteur dans un message (onglet Recruteur-superviseur ; aussi l'onglet Rapport de la fiche ?) :
# [ recommandation, niveau, efficacité, transferts | attributs (à la place de Pour / Contre) | Infos, matchs, comparaison ]
MAX_INFOS_MSG = 40.0                                 # message v11 : Infos à la largeur de son contenu, au plus 40 %
#   (2026-11-12, le joueur, Medium / Small : vide entre Infos et le trait, la note serrée à droite)
VERSION_MESSAGE = 11                                 # v7 : sans l'efficacité tactique (plantage) ; v8 : colonne
#   de gauche qui défile (fiche > Rapports en Large : Pour / Contre sortaient de la tuile) ; v9 : Infos limité en
#   largeur (PART_INFOS), textes à la ligne ; v10 (2026-11-11, le joueur : messages qui mettent du temps à
#   s'afficher) : le rapport de FM n'est plus gardé caché (un SIVisible caché construit et lie quand même tout son
#   contenu = 2 rapports par message) -> retiré ; refait depuis l'original à chaque fois, retirer = original remis
MESSAGE_MODELES = ("ScoutingReportBlock_Large", "ScoutingReportBlock_Small")
MESSAGE_RAPPORT = "ScoutReport"                       # rangée des 3 colonnes de FM
MESSAGE_COLONNES = ("LeftColumn", "RightColumn")      # reco / niveau / efficacité / transferts | matchs, comparaison
MESSAGE_TRAITS = ("VerticalDivider1", "HorizontalDivider2")   # trait vertical, trait horizontal (modèles de FM)
MESSAGE_TRANSFERTS = "TransferInformation"
EFFICACITE_MSG = "config.ShowTacticalEffectiveness"   # SIVisible de l'efficacité tactique (son trait dedans)
MESSAGE_ONGLETS_DROITE = "ScoutingReport-TopRightPart"   # date + recruteur, à droite des onglets
NOM_MSG_FM = f"{PREFIXE}MsgFM-v{VERSION_MESSAGE}"          # SIVisible : le rapport de FM, caché
NOM_MSG_COPIE = f"{PREFIXE}MsgFM24-v{VERSION_MESSAGE}"     # SIVisible : la copie façon écran Rapports
NOM_MSG_INFOS = f"{PREFIXE}MsgInfos-v{VERSION_MESSAGE}"    # SIVisible : Infos à gauche du rapport (Medium / Small)
NOM_MSG_INFOS_LARGE = f"{PREFIXE}MsgInfosLarge-v{VERSION_MESSAGE}"   # SIVisible : Infos en ligne dans la barre des
#   onglets, entre « Analyste » et la date (Large, demande du joueur : place pour le rapport et les infos transferts)
PREFIXE_MSG_FM = f"{PREFIXE}MsgFM"


def nomme(t, nom):
    return next((r for r in t.walk() if t.name(r) == nom), None)


def sous_arbre(t, r):
    yield r
    for c in t.children(r):
        yield from sous_arbre(t, c)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def a_jour(t):
    noms = {t.name(r) for r in marques(t)}
    return noms == {NOM_FM24, NOM_LARGE, NOM_FM, NOM_HORS_MSG, NOM_DANS_MSG, NOM_SWITCH}


def message_a_jour(t):
    return {t.name(r) for r in marques(t)} == {NOM_MSG_COPIE, NOM_MSG_INFOS, NOM_MSG_INFOS_LARGE}


def ouvrir_original(nom):
    """(bundle, obj, typetree, arbre) d'un modèle de message repris de l'original (feuille de style d'origine aussi),
    ou None sans sauvegarde d'origine"""
    from club_page_bas import original
    bundle, obj, tt = nb.find_vta(nom)
    if tt is None:
        return None
    orig = original(bundle, obj)
    if orig is None:
        return None
    sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    t = Tree(orig)
    t.styles = Styles(bundle, orig)
    if sheet is not None:   # les règles des versions précédentes ne s'empilent pas
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, orig, t


def defaire(t):
    """retire nos SIVisible (toutes versions) : la copie part, le bloc de FM revient à sa place ; nombre défait"""
    n = 0
    for r in marques(t):
        if r not in t.refs:
            continue
        if t.name(r).rsplit("-v", 1)[0] in ENVELOPPES + (PREFIXE_MSG_FM,):
            p = t.parent[r]
            rang = t.children(p).index(r)
            for k, c in enumerate(t.children(r)):
                move(t, c, p, rang + k)
        t.remove(r)
        n += 1
    return n


def modele(nom):
    """(arbre, feuille de style intégrée, BindingExpect racine) d'un modèle de FM, ou (None, None, None)"""
    bundle, _, tt = nb.find_vta(nom)
    if tt is None:
        return None, None, None
    s = Tree(tt)
    racine = next((r for r in s.walk() if (s.elem(r).get("m_FullTypeName") or "").endswith("BindingExpect")), None)
    return s, Styles(bundle, tt), racine


class Sources:
    def __init__(self):
        self.vs, self.vis = visible_model()
        # fiche et tableau d'attributs pris à l'ORIGINE : sans ce que le skin y ajoute (bloc d'entraînement sous les
        # pieds, icônes de forme dans Infos…), posé avant ce script par le choix 1
        o = ouvrir(ATTRIBUTS[0], depart_original=True)
        self.fo = o and o[3]
        self.sa, self.sa_st = self.fo, self.fo and self.fo.styles
        self.info = self.sa and next((r for r in self.sa.walk() if self.sa.name(r) == INFOS), None)
        o = ouvrir(ATTRIBUTS[1], depart_original=True)
        self.at, self.at_st = (o[3], o[3].styles) if o else (None, None)
        self.at_be = self.at and next((r for r in self.at.walk()
                                       if typ(self.at, r).endswith("BindingExpect")), None)
        self.pi, self.pi_st, self.pi_be = modele(PIEDS)
        self.sp, self.sp_st, self.pc = modele(POUR_CONTRE)
        sv = src_tree(VARIABLES_SOURCE[0])
        self.var = sv and next((copy.deepcopy(v) for r in sv.refs.values()
                                for v in ((r or {}).get("data") or {}).get("ValueVariables") or []
                                if v.get("m_name") == VARIABLES_SOURCE[1]), None)
        # bouton et polygone aussi (le skin remplace le polygone de la fiche par Pour / Contre)
        self.case = self.fo and next((r for r in self.fo.walk() if typ(self.fo, r).endswith("SICheckBox")
                                      and (self.fo.sd(r).get("SelectionBinding") or {}).get("m_path") == POLYGONE),
                                     None)
        self.poly = self.fo and next((r for r in self.fo.walk() if self.fo.name(r) == COLONNE_POLYGONE), None)
        # un SIScrollView de FM pour le rapport du message (son modèle n'en a pas) : celui de l'écran Rapports
        self.ds = src_tree(MODELE)
        self.sv = self.ds and next((r for r in self.ds.walk() if typ(self.ds, r).endswith("SIScrollView")), None)

    def manque(self):
        return [n for n in ("vis", "info", "at_be", "pi_be", "var", "pc", "case", "poly", "sv")
                if getattr(self, n) is None]


def typ(t, r):
    return t.elem(r).get("m_FullTypeName") or ""


def recopie(t, s, st, racine, parent, index=None):
    """sous-arbre racine du modèle s recopié sous parent, avec ses styles intégrés et ses modèles inclus"""
    r = t.clone(racine, parent, index, src=s)
    t.styles.copy_from(st, t, r)
    copy_usings(t, s, racine)
    return r


def remapper_joueur(t, parent, index=None):
    """BindingRemapper (copie de celui de FM, ou du 1er du modèle) : person = le joueur du rapport"""
    patron = nomme(t, REMAPPER_MODELE) or next(r for r in t.walk() if typ(t, r).endswith(".BindingRemapper"))
    rm = t.clone_shallow(patron, parent, index)
    sd = t.sd(rm)
    sd["name"], sd["name_UxmlAttributeFlags"] = "", 0
    sd["Mappings"] = [{"m_serialisedType": 0, "from": "person", "to": {"m_path": JOUEUR}, "type": {"id": TYPE_PERSONNE}}]
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = ["align-self-stretch"], -1
    return rm


def mode_visible(t, src, parent, index, nom, op, cls, val=0):
    v = new_visible(t, src.vs, src.vis, parent, index, nom,
                    make_binding(src.vs.sd(src.vis)["Binding"], op, [MODE_AFFICHAGE], val), cls)
    t.elem(v)["m_RuleIndex"] = -1
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    return v


def sur_message(t, v, inverse):
    """SIVisible v lié directement au paramètre isMessage (inverse : visible hors message)"""
    b = t.sd(v)["Binding"]
    b["m_kind"] = 1
    b["m_direct"]["Path"]["m_path"] = MESSAGE
    t.sd(v)["InvertDirectBinding"] = 1 if inverse else 0


def colonne(t, parent, part):
    c = plain(t, parent, None, [])
    t.elem(c)["m_RuleIndex"] = -1
    t.styles.style(t, c, {"flex-grow": part, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    return c


def attributs(t, src, parent, large=False):
    """tableau d'attributs de la fiche pour le joueur du rapport : BindingVariables (rolemask vide) > BindingRemapper
    (person = player) > contenu d'AttributesTableTemplate recopié (le modèle, partagé avec la fiche, reste intact),
    avec les pieds (PlayerReportFootednessBlock, recopié aussi) centrés chacun dans sa moitié"""
    if nomme(t, VARIABLES_MODELE) is not None:
        var = t.clone_shallow(nomme(t, VARIABLES_MODELE), parent)
        sd = t.sd(var)
        sd["name"], sd["name_UxmlAttributeFlags"] = "", 0
        sd["ValueVariables"], sd["ReferenceVariables"] = [copy.deepcopy(src.var)], []
        sd["ValueVariables_UxmlAttributeFlags"] = 1
    else:        # modèle sans élément BindingVariables (bloc du message) : conteneur transformé, comme la fiche
        var = plain(t, parent, None, [])
        fjp.en_variables(t, var, src.var)
    t.elem(var)["m_Classes"], t.elem(var)["m_RuleIndex"] = ["align-self-stretch"], -1
    rm = remapper_joueur(t, var)
    be = recopie(t, src.at, src.at_st, src.at_be, rm)
    t.elem(be)["m_Classes"] = ["flex-grow-class", "align-self-stretch"]
    if large:    # lignes un peu moins hautes : tout le tableau tient dans la tuile
        for r in sous_arbre(t, be):
            sd = t.sd(r)
            if sd.get("FixedElementSize") == HAUTEUR_LIGNE_FM:
                sd["FixedElementSize"] = HAUTEUR_LIGNE_LARGE
    for inst in [r for r in sous_arbre(t, be) if t.elem(r).get("m_TemplateAlias") == PIEDS]:
        p = t.parent[inst]
        pb = recopie(t, src.pi, src.pi_st, src.pi_be, p, t.children(p).index(inst))
        t.elem(pb)["m_Classes"] = list(t.elem(inst).get("m_Classes") or [])
        t.remove(inst)
        for r in sous_arbre(t, pb):
            if t.name(r) in PIEDS_MOITIES:
                t.elem(r)["m_Classes"] = list(t.elem(r).get("m_Classes") or []) + ["align-items-center"]


def chemin_texte(t, r):
    b = t.sd(r).get("TextBinding")
    return b["m_direct"]["Path"]["m_path"] if isinstance(b, dict) and b.get("m_kind") == 1 else ""


def style_mediatique(t, f):
    """ligne « Style médiatique » sous « Personnalité » dans la copie f (si la fiche du jeu ne l'a pas déjà, cf.
    joueur_fiche\\style_mediatique.py) : copie de la ligne Personnalité, valeur person.MediaHandling, titre traduit
    pris à FM"""
    if any(chemin_texte(t, r).split(".")[-1].lower() == MEDIAS for r in sous_arbre(t, f)):
        return
    valeur = next((r for r in sous_arbre(t, f) if chemin_texte(t, r).split(".")[-1].lower() == "personality"), None)
    if valeur is None:
        return
    titre = sm.find_title_binding()
    ligne = t.parent[valeur]
    p = t.parent[ligne]
    new = t.clone(ligne, p, t.children(p).index(ligne) + 1)
    for r in sous_arbre(t, new):
        d = t.sd(r)
        if d.get("name"):
            d["name"] = d["name"].replace("Personality", "MediaHandling")
        if chemin_texte(t, r).split(".")[-1].lower() == "personality":
            tb = d["TextBinding"]["m_direct"]["Path"]
            tb["m_path"] = tb["m_path"][: -len("Personality")] + "MediaHandling"
        elif d.get("TextBinding"):
            d["TextBinding"] = copy.deepcopy(titre)


def ordre_et_ecart(t, f):
    """lignes d'Infos dans l'ordre du skin (Taille, Personnalité, Style médiatique, Réputation, cf.
    style_mediatique.reputation_last) et espacées de ECART_INFOS (sauf la dernière)"""
    val = next((r for r in sous_arbre(t, f) if chemin_texte(t, r).split(".")[-1].lower() == "personality"), None)
    rep = next((r for r in sous_arbre(t, f) if sm.text_path_ends(t, r, "Reputation")), None)
    if val is None or rep is None:
        return
    pa, ra = sm.ancestors(t, val), sm.ancestors(t, rep)
    common = next(a for a in pa if a in ra)                  # conteneur des lignes
    rep_row = ra[ra.index(common) - 1]
    kids = t.elem(common)["m_Children"]
    kids[:] = [k for k in kids if k["rid"] != rep_row] + [{"rid": rep_row}]
    # lignes du conteneur, puis Personnalité / Style médiatique (regroupées sous le même SIVisible)
    for rows in (t.children(common), t.children(t.parent[t.parent[val]])):
        for r in rows:
            cls = [c for c in t.elem(r).get("m_Classes") or [] if not c.startswith("margin-bottom")]
            t.elem(r)["m_Classes"] = cls + ([ECART_INFOS] if r != rows[-1] else [])


def infos(t, src, parent, index):
    """bloc Infos de la fiche pour le joueur du rapport : titre, taille, réputation, personnalité, style médiatique
    (sans le bouton d'analyse des attributs, les caractéristiques ni les suspensions)"""
    rm = remapper_joueur(t, parent, index)
    t.elem(rm)["m_Classes"] = []
    f = recopie(t, src.sa, src.sa_st, src.info, rm)
    t.elem(f)["m_RuleIndex"] = -1    # largeur max 312 px de la fiche
    t.elem(f)["m_Classes"] = ["column-direction-normal", "align-items-start"]
    garde = True
    for k in list(t.children(f)):
        if not garde:
            t.remove(k)
        elif t.name(k) == INFOS_TITRE:
            for b in [c for c in t.children(k) if (t.elem(c).get("m_FullTypeName") or "").endswith("SIVisible")]:
                t.remove(b)
        elif t.name(k) == INFOS_RANGEE:
            style_mediatique(t, k)
            ordre_et_ecart(t, k)
            garde = False            # tout ce qui suit (caractéristiques, suspensions et leurs traits) part
    return rm


def limiter_infos(t, conteneur, rm, serre=False):
    """case Infos (rm : remapper de infos(), dans conteneur) limitée à PART_INFOS de la rangée : plus large que son
    contenu, elle allait jusqu'à droite (largeur max de la fiche retirée) ; textes à la ligne dans leur case.
    serre (message v11) : largeur de son contenu, au plus MAX_INFOS_MSG % de la rangée (le reste à la note)"""
    if serre:
        t.styles.style(t, conteneur, {"flex-grow": 0, "flex-shrink": 1, "min-width": 0,
                                      "max-width": {"unit": 2, "value": MAX_INFOS_MSG}})
    else:
        t.styles.style(t, conteneur, {"flex-grow": PART_INFOS, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    for r in sous_arbre(t, rm):
        if r == conteneur:
            continue
        if typ(t, r).endswith("SIText"):
            t.elem(r)["m_Classes"] = [c for c in t.elem(r).get("m_Classes") or []
                                      if "ellipsis" not in c and "no-wrap" not in c]
            t.styles.style(t, r, {"white-space": "normal", "max-width": {"unit": 2, "value": 100.0},
                                  "flex-shrink": 1, "min-width": 0})
        else:
            t.styles.style(t, r, {"max-width": {"unit": 2, "value": 100.0}, "flex-shrink": 1, "min-width": 0})


def pour_contre(t, src, parent, large):
    """le contenu du modèle ScoutedProsAndCons recopié (pas le modèle lui-même, qui sert ailleurs), Pour à gauche,
    Contre à droite ; Large : listes entières (la colonne défile d'un bloc) ; renvoie un message d'erreur ou None"""
    pc = t.clone(src.pc, parent, src=src.sp)
    no_styles(t, pc)
    copy_usings(t, src.sp, src.pc)
    noms = {t.name(r): r for r in sous_arbre(t, pc)}
    if any(n not in noms for n in (PC_RANGEE, *PC_COLONNES)):
        return f"#{PC_RANGEE} / #{' #'.join(PC_COLONNES)} introuvables dans {POUR_CONTRE}"
    t.elem(noms[PC_RANGEE])["m_Classes"] = ["row-direction-normal", "align-self-stretch"]
    if large:
        for k, n in enumerate(PC_COLONNES):
            t.elem(noms[n])["m_Classes"] = ["margin-right-global-gap-large"] if k == 0 else []
            t.styles.style(t, noms[n], {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
        return None
    # Pour / Contre prennent la hauteur qui reste sous les attributs (rapport calé sur la tuile)
    t.styles.style(t, pc, RESTE)
    t.styles.style(t, noms[PC_RANGEE], RESTE)
    for k, n in enumerate(PC_COLONNES):
        e = t.elem(noms[n])
        e["m_Classes"] = ["margin-right-global-gap-large"] if k == 0 else []
        t.styles.style(t, noms[n], {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                    "min-height": 0})
        # la liste défile seule (molette dessus) dans la place qui reste ; le titre garde sa taille
        liste = next((c for c in t.children(noms[n])
                      if (t.elem(c).get("m_FullTypeName") or "").endswith("StreamedObjectList")), None)
        for c in t.children(noms[n]):
            if c != liste:
                t.styles.style(t, c, {"flex-shrink": 0})
        if liste is not None:
            sv = defilement(t, noms[n])
            move(t, sv, noms[n], t.children(noms[n]).index(liste))
            move(t, liste, sv)
    return None


def bouton_polygone(t, src, parent, index):
    """case du polygone de la fiche (icône + infobulle « Analyse des attributs »), qui écrit POLYGONE"""
    b = recopie(t, src.fo, src.fo.styles, src.case, parent, index)
    t.elem(b)["m_Classes"] = list(t.elem(b).get("m_Classes") or []) + ["margin-right-global-gap-regular"]
    t.styles.style(t, b, {"flex-shrink": 0})
    return b


def bascule(t, src, vis, parent, tableau, large):
    """tableau d'attributs affiché tant que le bouton polygone n'est pas coché ; coché, le polygone de la fiche
    (colonne recopiée, réglages de la vue Guru) à sa place, comme sur la fiche. vis : un SIVisible du modèle (patron)"""
    i = t.children(parent).index(tableau)
    sans = plain(t, parent, i, ["align-self-stretch"])
    move(t, tableau, sans)
    t.to_visible(sans, vis, POLYGONE, True, "")
    avec = plain(t, parent, i + 1, ["align-self-stretch"])
    t.to_visible(avec, vis, POLYGONE, False, "")
    col = recopie(t, src.fo, src.fo.styles, src.poly, avec)
    t.sd(col)["name"] = ""
    t.elem(col)["m_Classes"] = [c for c in t.elem(col).get("m_Classes") or [] if c != "margin-right-global-gap-large"]
    for r in sous_arbre(t, col):
        if typ(t, r).endswith("FMSpiderChart"):
            sd = t.sd(r)
            sd["SpiderChartRadiusPercentage"] = float(RAYON_POLYGONE)   # étiquettes de FM (place du tableau)
            sd["NumberOfInnerRings"] = guru.ANNEAUX_POLYGONE
    for x in (sans, avec):
        t.elem(x)["m_RuleIndex"] = -1
    t.styles.style(t, sans, {"flex-shrink": 0})            # le tableau : sa taille, comme avant
    if large:      # la colonne défile : hauteur fixe pour le polygone
        t.styles.style(t, avec, {"flex-shrink": 0, "min-height": HAUTEUR_POLYGONE_LARGE})
    else:          # 2/3 de la hauteur, Pour / Contre (RESTE) le 1/3 restant
        t.styles.style(t, avec, {"flex-grow": 2, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
        t.styles.style(t, col, {"min-height": 0})


def defilement(t, parent):
    """copie (sans nom ni style) du SIScrollView de FM, qui prend la hauteur qui reste dans parent"""
    sv = t.clone_shallow(nomme(t, DEFILEMENT), parent, None)
    t.sd(sv)["name"], t.sd(sv)["name_UxmlAttributeFlags"] = "", 0
    t.elem(sv)["m_Classes"], t.elem(sv)["m_RuleIndex"] = ["align-self-stretch"], -1
    t.styles.style(t, sv, RESTE)
    return sv


def copie(t, src, ext, p, bloc, cols, tv, th, large, message=False):
    """la copie réorganisée dans le SIVisible ext, calée sur la hauteur de la tuile (la page ne défile plus) :
    en-tête du recruteur (copié de la zone p de FM) puis la rangée réorganisée, qui prend la hauteur qui reste.
    Large : chaque colonne défile d'un bloc ; sinon Pour / Contre (et le bas de droite) défilent seuls.
    message (v20) : dans le message « Mise à jour des recherches » (hauteur pas fixée) : tout à sa hauteur naturelle,
    rien ne défile, listes Pour / Contre entières. Renvoie un message d'erreur ou None"""
    naturel = {"flex-grow": 0, "flex-shrink": 0}
    t.styles.style(t, ext, naturel if message else RESTE)
    # variable du bouton polygone (comme la fiche) : bouton et polygone en dessous
    vp = t.clone_shallow(nomme(t, VARIABLES_MODELE), ext)
    sd = t.sd(vp)
    sd["name"], sd["name_UxmlAttributeFlags"] = "", 0
    sd["ValueVariables"], sd["ReferenceVariables"] = [copy.deepcopy(VARIABLE_POLYGONE)], []
    sd["ValueVariables_UxmlAttributeFlags"] = 1
    t.elem(vp)["m_Classes"], t.elem(vp)["m_RuleIndex"] = ["align-self-stretch"], -1
    t.styles.style(t, vp, naturel if message else RESTE)
    for c in t.children(p):
        if c != bloc:
            t.styles.style(t, t.clone(c, vp), {"flex-shrink": 0})
    # bouton polygone collé à gauche d'Actions, dans le bandeau du recruteur : [vide qui pousse | bouton | Actions]
    act = next((r for r in sous_arbre(t, vp) if t.name(r) == ACTIONS), None)
    if act is None:
        return f"#{ACTIONS} introuvable"
    pa = t.parent[act]
    ligne = plain(t, pa, t.children(pa).index(act), ["row-direction-normal", "align-items-center", "flex-grow-class"])
    t.elem(ligne)["m_RuleIndex"] = -1
    vide = plain(t, ligne, None, [])
    t.elem(vide)["m_RuleIndex"] = -1
    t.styles.style(t, vide, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    bouton_polygone(t, src, ligne, None)
    move(t, act, ligne)
    t.elem(act)["m_Classes"] = [c for c in t.elem(act).get("m_Classes") or [] if c != "flex-grow-class"]
    copie = plain(t, vp, None, ["row-direction-normal", "flex-grow-class"])
    t.elem(copie)["m_RuleIndex"] = -1
    t.styles.style(t, copie, naturel if message else RESTE)
    gauche = colonne(t, copie, PART_GAUCHE)
    g = defilement(t, gauche) if large and not message else gauche
    attributs(t, src, g, large and not message)
    t.clone(th, g)
    for c in t.children(g):
        t.styles.style(t, c, {"flex-shrink": 0})        # attributs et trait : leur taille ; Pour / Contre : le reste
    err = pour_contre(t, src, g, large or message)
    if err:
        return err
    bascule(t, src, ext, g, t.children(g)[0], large or message)        # enfant 0 : le tableau d'attributs
    t.clone(tv, copie)
    droite = colonne(t, copie, PART_DROITE)
    for k, c in enumerate(cols):
        if k:
            t.clone(th, droite)
        for e in t.children(c):
            t.clone(e, droite)
    # v19 : sans l'efficacité tactique (avec son trait) : sa copie faisait planter FM à la 1re tactique d'une partie
    # (Recrutement ouvert sans tactique, puis tactique créée avec les suggestions du jeu)
    club = next((r for r in sous_arbre(t, droite) if t.name(r) == CLUB), None)
    eff = club and next((c for c in t.children(club) if t.name(c) == EFFICACITE), None)
    if eff:
        t.remove(eff)
    # sans « Matchs observés » (son SIVisible, avec son trait), pour que la page tienne sans défiler
    m = next((r for r in sous_arbre(t, droite) if t.name(r) == MATCHS), None)
    if m:
        t.remove(t.parent[m])
    # en haut à droite : [ Infos du joueur | recommandation, niveau / potentiel, infos transferts ], l'efficacité
    # tactique (club) sortie dessous sur toute la largeur, dans un switch club / sélection comme celui de FM
    reco, sw = (next((r for r in t.children(droite) if t.name(r) == n), None) for n in (RECO, SWITCH_CLUB))
    if reco is None or sw is None:
        return f"#{RECO} / #{SWITCH_CLUB} introuvables"
    rangee = plain(t, droite, t.children(droite).index(reco), ["row-direction-normal", "align-self-stretch"])
    t.elem(rangee)["m_RuleIndex"] = -1
    rm = infos(t, src, rangee, None)
    limiter_infos(t, rm, rm)
    t.clone(tv, rangee)
    col = colonne(t, rangee, PART_RECO)
    for r in [r for r in t.children(droite) if r != rangee][:t.children(droite).index(sw)]:
        move(t, r, col)
    # la page tient sans défiler : la colonne de droite prend la hauteur de celle de gauche (son contenu, en
    # position absolute, ne compte plus dans la hauteur de la rangée) ; sous [Infos | reco], le reste (efficacité
    # tactique, comparaison effectif…) défile seul dans la place qui reste
    if message:   # rien en position absolute ni qui défile : la colonne garde la hauteur de son contenu
        t.styles.style(t, rangee, {"flex-shrink": 0})
        return None
    reste = t.children(droite)[t.children(droite).index(rangee) + 1:]
    cadre = plain(t, droite, None, [])
    t.elem(cadre)["m_RuleIndex"] = -1
    t.styles.style(t, cadre, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0})
    move(t, rangee, cadre)
    t.styles.style(t, rangee, {"flex-shrink": 0})
    sv = defilement(t, cadre)
    # Large : toute la colonne défile d'un bloc (demande du joueur) ; sinon, seulement ce qui suit [Infos | reco]
    for r in ([rangee] if large else []) + reste:
        move(t, r, sv)
    return None


def construire(t, src):
    """renvoie un message, ou une erreur contenant « introuvable »"""
    bloc = nomme(t, BLOC)
    cols = [nomme(t, n) for n in COLONNES_FM]
    pc, tv, th = (nomme(t, n) for n in (POUR_CONTRE, TRAIT_VERTICAL, TRAIT_HORIZONTAL))
    if None in [bloc, pc, tv, th, *cols] or None in (nomme(t, VARIABLES_MODELE), nomme(t, REMAPPER_MODELE)):
        return f"#{BLOC} ou ses colonnes introuvables (changés par une mise à jour ?)"
    patron_sw = nomme(t, SWITCH_MESSAGE)
    if patron_sw is None or len(t.children(patron_sw)) != 2 or t.binding(patron_sw, "Binding") != MESSAGE:
        return f"aiguillage #{SWITCH_MESSAGE} (isMessage) introuvable"
    p = t.parent[bloc]
    if t.name(p) != DEFILEMENT:
        return f"#{DEFILEMENT} autour de #{BLOC} introuvable"
    wi = t.parent[p]
    rang = t.children(wi).index(p)
    # la zone qui défile de FM (en-tête du recruteur + bloc), gardée, affichée seulement dans un message
    # v20 : le bloc de FM n'est plus affiché nulle part (mode < 0) ; dans le message, notre copie à hauteur naturelle
    fm = mode_visible(t, src, wi, rang, NOM_FM, OP_FM, ["flex-grow-class"])
    move(t, p, fm)
    dm = mode_visible(t, src, wi, rang, NOM_DANS_MSG, OP_FM24, ["flex-grow-class"], 0)
    sur_message(t, dm, False)
    err = copie(t, src, dm, p, bloc, cols, tv, th, False, message=True)
    if err:
        return err
    # les copies, juste avant (hors message) : une pour Medium / Small, une pour Large
    hors = mode_visible(t, src, wi, rang, NOM_HORS_MSG, OP_FM, ["flex-grow-class"])
    sur_message(t, hors, True)
    t.styles.style(t, hors, RESTE)
    for nom, op, val, large in ((NOM_FM24, OP_FM24, MODE_MEDIUM, False), (NOM_LARGE, OP_LARGE, MODE_LARGE, True)):
        ext = mode_visible(t, src, hors, None, nom, op, ["flex-grow-class"], val)
        err = copie(t, src, ext, p, bloc, cols, tv, th, large)
        if err:
            return err
    # v22 : les deux dans un aiguillage isMessage (seul l'enfant choisi est construit) : [hors message, message]
    sw = t.clone_shallow(patron_sw, wi, t.children(wi).index(hors))
    t.sd(sw)["name"], t.sd(sw)["name_UxmlAttributeFlags"] = NOM_SWITCH, 1
    t.sd(sw)["AlwaysInstantiate"] = 0
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
    t.styles.style(t, sw, SERRE)
    move(t, hors, sw, 0)
    move(t, dm, sw, 1)
    return (f"hors message / message dans un aiguillage (une seule copie construite) ; Medium / Small : attributs (pieds centrés) + Pour | Contre à gauche, à droite Infos du joueur | "
            f"recommandation + transferts, puis comparaison dans son propre défilement (sans efficacité tactique) ; "
            f"Large : pareil, lignes d'attributs plus basses, chaque colonne défile d'un bloc ; sans Matchs observés ; "
            f"bouton polygone collé à Actions, coché : polygone à la place du tableau d'attributs (v{VERSION})")


def infos_en_ligne(t, rm):
    """Infos (rm : remapper de infos()) sans son titre, les lignes côte à côte : Taille, Personnalité, Style médiatique,
    Réputation (chaque ligne : titre au-dessus, valeur dessous, comme avant)"""
    f = t.children(rm)[0]
    for k in list(t.children(f)):
        if t.name(k) != INFOS_RANGEE:
            t.remove(k)                       # titre « Infos » et son trait
    t.elem(f)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    for r in list(sous_arbre(t, f))[1:]:
        if typ(t, r).endswith("SIText"):
            continue
        cls = [c for c in t.elem(r).get("m_Classes") or [] if c not in ("column-direction-normal", ECART_INFOS)]
        ligne = any(typ(t, c).endswith("SIText") for c in t.children(r))
        if not ligne:                         # conteneur de lignes : en rangée
            cls = ["row-direction-normal"] + cls
        if ECART_INFOS in (t.elem(r).get("m_Classes") or []):
            cls.append("margin-right-global-gap-extra-large")
        t.elem(r)["m_Classes"] = cls
    return rm


def construire_message(t, src):
    """bloc du rapport d'un message, disposé comme l'écran Rapports (v2, demande du joueur : le bloc prend la
    hauteur de son contenu, rien ne défile) : à gauche (2/3) attributs puis Pour | Contre entiers ; à droite (1/3)
    [Infos | recommandation, niveau, transferts], efficacité tactique, matchs observés, comparaison. Le rapport de
    FM est gardé, caché (mode < 0). Renvoie un message, ou une erreur contenant « introuvable »"""
    rapport, tv, th = (nomme(t, n) for n in (MESSAGE_RAPPORT, *MESSAGE_TRAITS))
    cols = [nomme(t, n) for n in MESSAGE_COLONNES]
    date = next((r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == MESSAGE_ONGLETS_DROITE), None)
    if None in (rapport, tv, th, date, *cols):
        return f"#{MESSAGE_RAPPORT}, ses colonnes, ses traits ou {MESSAGE_ONGLETS_DROITE} introuvables"
    # Large : Infos en ligne dans la barre des onglets, juste avant la date
    pd = t.parent[date]
    v = mode_visible(t, src, pd, t.children(pd).index(date), NOM_MSG_INFOS_LARGE, OP_LARGE,
                     ["row-direction-normal", "align-items-center", "margin-left-global-gap-extra-large"],
                     MODE_LARGE)   # v6 : collé à gauche, contre « Analyste » (v5 centré : touchait la date)
    t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    infos_en_ligne(t, infos(t, src, v, None))
    # v2 en jeu : rien d'affiché, #ScoutReport est un enfant d'un aiguillage (BindableSwitchElement : enfant n° 1
    # = rapport) -> il reste à sa place, son contenu de FM caché dedans, la copie à côté de lui (dedans aussi)
    fm = mode_visible(t, src, rapport, 0, NOM_MSG_FM, OP_FM, [])
    for c in t.children(rapport)[1:]:
        move(t, c, fm)
    # v3 en jeu : tout écrasé en largeur (copie en rangée : la rangée dedans gardait la largeur de son contenu, ~0) ;
    # v4 : copie en colonne, rangée étirée sur toute la largeur
    copie = mode_visible(t, src, rapport, 1, NOM_MSG_COPIE, OP_FM24, ["flex-grow-class"], 0)
    t.styles.style(t, copie, {"min-width": 0, "flex-shrink": 1, "min-height": 0})
    # v8 (capture d'un joueur, fiche > Rapports en Large : 5 Pour, la liste sortait de la tuile) : colonnes étirées sur
    # la hauteur de la rangée, qui se serre dans la tuile ; la colonne de gauche (attributs + Pour / Contre, titres
    # compris) défile d'un bloc. Hauteur naturelle gardée quand il y a la place (message : rien ne défile)
    rangee = plain(t, copie, None, ["row-direction-normal", "align-self-stretch"])
    t.elem(rangee)["m_RuleIndex"] = -1
    t.styles.style(t, rangee, SERRE)
    gauche = colonne(t, rangee, PART_GAUCHE)
    t.styles.style(t, gauche, {"min-height": 0})
    sv = t.clone(src.sv, gauche, src=src.ds)
    for c in list(t.children(sv)):
        t.remove(c)
    t.sd(sv)["name"], t.sd(sv)["name_UxmlAttributeFlags"] = "", 0
    t.elem(sv)["m_Classes"], t.elem(sv)["m_RuleIndex"] = ["align-self-stretch"], -1
    t.styles.style(t, sv, SERRE)
    gauche = sv
    attributs(t, src, gauche)
    t.clone(th, gauche)
    err = pour_contre(t, src, gauche, True)          # listes entières, Pour | Contre côte à côte
    if err:
        return err
    trait = t.clone(tv, rangee)
    t.elem(trait)["m_Classes"] = list(t.elem(trait).get("m_Classes") or []) + ["align-self-stretch"]
    droite = colonne(t, rangee, PART_DROITE)
    # en haut : [ Infos | recommandation, niveau / potentiel, infos transferts ]
    haut = plain(t, droite, None, ["row-direction-normal", "align-self-stretch"])
    t.elem(haut)["m_RuleIndex"] = -1
    v = mode_visible(t, src, haut, 0, NOM_MSG_INFOS, OP_FM24, ["row-direction-normal"], MODE_MEDIUM)
    limiter_infos(t, v, infos(t, src, v, None), serre=True)   # v11 : plus de vide entre Infos et le trait
    t.clone(tv, v)
    reco = t.clone(cols[0], haut)
    t.sd(reco)["name"] = ""
    t.styles.style(t, reco, {"flex-grow": PART_RECO, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    # v7 : sans l'efficacité tactique (avec son trait), comme le rapport (v19) : sa copie faisait planter FM
    eff = next((r for r in sous_arbre(t, reco) if typ(t, r).endswith("SIVisible")
                and (t.binding(r, "Binding") or "") == EFFICACITE_MSG), None)
    if eff:
        t.remove(eff)
    # puis la comparaison de l'effectif (colonne de droite de FM), sans Matchs observés ni son trait, comme
    # l'écran Rapports (« le même écran que celui où on a travaillé »)
    t.clone(th, droite)
    kids = t.children(cols[1])
    for k, e in enumerate(kids):
        if t.name(e) != MATCHS and not (k and t.name(kids[k - 1]) == MATCHS):
            t.clone(e, droite)
    # v10 : le rapport de FM, caché, était quand même construit et lié (2 rapports par message, affichage lent) :
    # retiré une fois la copie faite (retirer = original remis, pas de retour en arrière depuis cet arbre)
    t.remove(fm)
    return (f"comme l'écran Rapports : attributs + Pour | Contre à gauche, à droite Infos | recommandation + "
            f"transferts, puis comparaison, sans efficacité ni Matchs observés ; rapport de FM caché retiré "
            f"(un seul rapport construit, v{VERSION_MESSAGE})")


def appliquer_message(src):
    """les deux blocs du rapport d'un message ; src : Sources (ou None, chargé au besoin) ; renvoie src"""
    for nom in MESSAGE_MODELES:
        bundle, obj, tt = nb.find_vta(nom)
        if tt is None:
            print(f"{nom} : introuvable (renommé par une mise à jour ?), rien fait")
            continue
        t = Tree(tt)
        if message_a_jour(t):
            print(f"{nom} : déjà appliqué")
            continue
        src = src or Sources()
        if src.manque():
            print(f"{nom} : morceaux de FM introuvables ({', '.join(src.manque())}), rien fait")
            continue
        n = len(marques(t))
        o = ouvrir_original(nom)   # v10 : toujours depuis l'original (le rapport de FM n'est plus dans le modèle)
        if o is None:
            print(f"{nom} : pas de sauvegarde d'origine, rien fait")
            continue
        bundle, obj, tt, t = o
        if marques(t):
            print(f"{nom} : sauvegarde d'origine pas propre, rien fait")
            continue
        m = construire_message(t, src)
        if "introuvable" in m:
            print(f"{nom} : {m}, rien fait")
            continue
        print(f"{nom} : " + ("version précédente retirée ; " if n else "") + m)
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt   # relu par rapport_diminutif
        nb._dirty.add(bundle)
    return src


def cmd_appliquer():
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        print(f"{MODELE} : introuvable (renommé par une mise à jour ?), rien fait")
        return
    t = Tree(tt)
    src = None
    if a_jour(t):
        print(f"{MODELE} : déjà appliqué")
    else:
        src = Sources()
        if src.manque():
            print(f"morceaux de FM introuvables ({', '.join(src.manque())}), rien fait")
            return
        t.styles = Styles(bundle, tt)
        n = defaire(t)
        m = construire(t, src)
        if "introuvable" in m:
            print(f"{MODELE} : {m}, rien fait")
            return
        print(f"{MODELE} : " + ("version précédente retirée ; " if n else "") + m)
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt   # relu par rapport_diminutif
        nb._dirty.add(bundle)
    appliquer_message(src)
    # 2026-11-07 (le joueur : « partout juste les diminutifs ») : note + libellé court, jamais la phrase (aussi le
    # bloc de Kinito, réécrit depuis l'original avant ce script)
    import rapport_diminutif
    rapport_diminutif.appliquer_recrutement()
    if nb._dirty:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def rapport_diminutif_actif(tt):
    """le modèle porte déjà le libellé court de rapport_diminutif (à garder en remettant l'original)"""
    import rapport_diminutif
    return not rapport_diminutif.a_des_phrases(tt)   # plus aucune phrase à raccourcir


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for nom in (MODELE,) + MESSAGE_MODELES:
        bundle, obj, tt = nb.find_vta(nom)
        t = tt and Tree(tt)
        if t is None or not marques(t):
            continue
        o = ouvrir_original(nom) if nom in MESSAGE_MODELES else None
        if o is not None:   # v10 : le rapport de FM n'est plus dans le modèle -> original remis (+ libellé court)
            court = rapport_diminutif_actif(tt)
            bundle, obj, tt, t = o
            if court:
                import rapport_diminutif
                rapport_diminutif.diminutif(t)
            t.styles.save()
        else:
            defaire(t)
        t.finish()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        fait = True
        print(f"{nom} : bloc de FM remis (tous les modes)")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    _, _, tt = nb.find_vta(MODELE)
    if tt is None:
        print(f"{MODELE} : introuvable")
    else:
        t = Tree(tt)
        print(f"{MODELE} : " + (f"rapport façon FM24, tous les modes (à jour, v{VERSION})" if a_jour(t)
                                else "version précédente (à refaire : choix 1)" if marques(t) else "d'origine"))
    for nom in MESSAGE_MODELES:
        _, _, tt = nb.find_vta(nom)
        t = tt and Tree(tt)
        print(f"{nom} : " + ("introuvable" if t is None else f"attributs (à jour, v{VERSION_MESSAGE})"
                             if message_a_jour(t) else "version précédente" if marques(t) else "d'origine"))
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
            print("non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
