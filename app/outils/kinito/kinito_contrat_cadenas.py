"""[AJOUT KINITO] Négociation de contrat : le menu du cadenas devient des icônes visibles à droite de la ligne.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Chaque ligne a un cadenas : un SIDropdown dont les choix sont component.BaseComponentData.PossibleLockStatuses et
dont le choix est écrit dans une donnée de la ligne (SelectionValueBinding, ex. component.addonlockstatus), sans
événement. Valeurs (NegotiationLocksDataCollection, ui-datacollections) : 0 Négociable (cadenas ouvert), 1
Semi-négociable (jaune), 2 Non négociable (rouge), 3 Retirer et exclure (poubelle). Le menu ne propose que ce que la
ligne permet (3 options pour le salaire, 2 pour les promesses, 4 pour les primes et clauses).

Historique des versions (demandes, relevés en jeu, essais) : résumé dans « AJOUTS KINITO - DETAILS.md »,
§ 4 ; texte complet gardé par Kinito.

Modèles touchés (ce script est leur seul propriétaire, appliquer repart toujours des originaux sauvegardés ; aucun
script d'AlexJeuVideal n'y touche) : ContractNegotiationAddOnItem, ContractNegotiationPromisesAddOnItem,
ContractNegotiationFuturePlayingTimeItem, (v22) ContractNegotiationPromisesAddOnItem_FMC, TeamGeneralPerformanceLabel, (v19) ContractNegotiationCashItem,
ContractNegotiationItem, ContractNegotiationPromisesItem, et (classe des listes, place des lignes, surcharges des lignes
fixes) ContractTermsBlock, ContractTermsCombinedBlock, ContractPromisesBlock, ContractPromisesCombinedBlock,
ContractTermsBlock_FMC, ContractPromisesBlock_FMC ; (v23) TransferOfferClauseItem, TransferOfferClauseItemSimple,
TransferOfferClauseItemSecondaryProperty, TransferOfferClauseItemValueProperty, TeamGeneralPerformanceEnhancedLabel,
et (classe des listes) TransferOfferTermsBlock, TransferOfferTermsDropdownBlock, TransferOfferClausesArea,
TransferOfferBonusClauseContent.
Utilise, sans les modifier : entrainement_equipes (construire_bouton, Morceaux, _chemins).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_contrat_cadenas.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_contrat_cadenas.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_contrat_cadenas.py etat
"""
import copy
import json
import os
import struct
import sys

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir, path_arg  # noqa: E402
from notes_installations import first, decode_args, encode_args, _enc_varint  # noqa: E402
import notes_installations as ni  # noqa: E402  (SIVisible de comparaison d'Alex : visible_model, make_binding, new_visible)
import arbre as sm  # noqa: E402  (v1.04 d'Alex : l'ancien style_mediatique_et_meilleur_pied)
import entrainement_equipes as ee  # noqa: E402  (bouton segmenté et morceaux d'Alex, sans les modifier)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
ICONE = 16              # px, l'icône : la taille des icônes « _small » de FM, celle de la poubelle (FMImages_1x) ; la ligne du menu FM les gonfle à 20
SEGMENT = ICONE + 4     # px, côté d'un bouton-icône carré : 2 px autour de l'icône (v10 : 24 avec une icône de 20 ; v8 : 32 = le bouton de la poubelle ; v5 : ~62)
# largeur de la rangée : nombre d'options de la ligne x SEGMENT (une rangée par nombre d'options, v12), collée à la poubelle
HAUTEUR = SEGMENT       # px
ECART = 8               # px, écart avec ce qui précède (le « + » ou le menu de la valeur)
ECART_POUBELLE = 0      # px, écart avec la poubelle de la ligne : collée (v9 : 8, « un espace entre la poubelle et la deuxième poubelle »)
NOM_LARGEUR_MIN = 260   # px, largeur minimale du bloc du nom (sinon il s'écrase quand la ligne est pleine)
OBJECTIF_LARGEUR_MAX = 260   # px, largeur maximale du menu du type d'objectif (temps de jeu futur ; FM : toute la ligne)
MENU_TEMPS_LARGEUR = (150, 260)   # px, largeur min / max du menu du temps de jeu d'une saison future (FM : rien ; promesses : 150 / 165)
OBJECTIF_MENU = "inputs-combobox-default-default-base-2"   # ce menu, sous #target-visible (ContractNegotiationFuturePlayingTimeItem)
OBJECTIF_BLOC = "target-visible"
FLEX_GROW, FLEX = 131084, 262149   # StylePropertyId : flex-grow, flex (raccourci) — relevés sur le #Frame des lignes de primes
DATE_LARGEUR_MAX = 220  # px, largeur maximale du sélecteur de date d'échéance d'une clause
LIGNE_HAUTEUR = 32      # px, hauteur d'une ligne de prime / clause (FM : 38) = celle des boutons de FM (32) ; v14 : 34
LIGNE_ECART = 1         # px, marge au-dessus et au-dessous de chaque ligne (FM : 6 et 6) ; v14 : 2 dessous
LIGNE_PAS = LIGNE_HAUTEUR + 2 * LIGNE_ECART   # px, place réservée à une ligne par la liste des primes (FM : 50, fixe)
MOLETTE = False         # pourcentages et années dans le champ des montants : ESSAI RATÉ (v14, v15 : la molette et les -/+ ne font rien sur ces lignes), menu d'origine gardé
# =====================================================================================================

VERSION = 25  # v25 : temps de jeu futur : son menu borné (150 à 260 px) — vide, il s'étirait sur toute la ligne
# v24 : temps de jeu futur : le nom prend la place libre (menu et icônes à droite), menu d'objectif plafonné
# v23 : les offres de transfert comme les contrats (icônes, rond barré, poubelle, lignes serrées)
# v22 : la variante _FMC des lignes de promesse en icônes aussi
# v21 : primes en hauteur libre (32 px au moins) et liste des primes qui mesure ses lignes : plus de noms qui se chevauchent
# v20 : les lignes fixes resserrées comme les primes (32 px au moins + 1 + 1)
# v19 : les lignes fixes (salaire, prime de fidélité, commission, durée, temps de jeu, date de début…) en icônes
# v18 : menu d'origine remis sur les pourcentages et les années (la molette n'y marche pas en skin)
# v17 : « Retirer et exclure » avec le rond barré de FM au lieu de la poubelle
# v16 : lignes de 32 px + 1 + 1 ; la liste des primes réserve 34 px par ligne au lieu de 50 (place fixe)
# v15 : la valeur calculée du clic (interrupteur) est déclarée dans le bouton ; molette des pourcentages : actions -/+ de la ligne gardées
# v14 : lignes plus serrées (34 px + 2) ; pourcentages et années dans le champ des montants (molette)
# v13 : recliquer sur l'option en cours la retire (retour à Négociable) ; le bouton Négociable est caché
# v12 : une rangée par nombre d'options (2, 3, 4), chacune à sa largeur : collée à la poubelle même quand il manque une option
# v11 : icônes de 16 px (comme la poubelle ; la ligne du menu les mettait à 20), boutons de 20 px
# v10 : rangée collée à la poubelle de la ligne (ECART_POUBELLE 0, LARGEUR sans réserve)
# v9 : boutons de SEGMENT = 24 px (demande de Kinito : « encore trop gros, la marge sur le côté des cadenas est trop grande »)
# v8 : boutons au style « contrôle » de FM (celui de la poubelle : sans fond ni contour ; l'option en cours avec le léger cadre de --active-true) ; listes du contrat en classe « agentoffer » (la ligne choisie garde le fond du tableau au lieu du violet)
# v7 : boutons carrés de SEGMENT px (taille de la poubelle, demande de Kinito), icône sans marges
# v6 : boutons de SEGMENT px (les 4 tiennent), icônes AVANT la poubelle (elle passe tout à droite), infobulle d'une ligne FM (RoleLabelwIcon) au lieu du modèle StandardTextTooltip (que FM remplit lui-même : la bulle restait vide)
# v5 : la valeur d'une option est row.RowData (relevé en jeu par la sonde, 2026-11-12) : row.PropertyValue n'existe pas, les boutons étaient vides, tous surlignés, et l'écran se bloquait
# v4 : l'icône et la bulle lisent aussi row.PropertyValue (le menu FM leur donne la valeur, la liste donne la paire : le jeu plantait encore en ajoutant une promesse) ; la forme des segments compte les options de la ligne (uipickercadenaschoix) au lieu des équipes d'un club
# v3 : une option du menu est une paire (DisplayValuePair) : on lit et on écrit row.PropertyValue (v2 comparait la paire entière à un nombre : le jeu plantait en affichant la ligne)
LIGNES = ["ContractNegotiationAddOnItem", "ContractNegotiationPromisesAddOnItem",
          "ContractNegotiationFuturePlayingTimeItem",
          "ContractNegotiationPromisesAddOnItem_FMC"]   # v22 : variante des promesses (ContractPromisesBlock_FMC, ContractNegotiationPromiseCategorySection)
# lignes fixes (v19) : un modèle commun, et c'est l'écran qui dit à chaque ligne où ranger son cadenas (surcharge de
# son menu, ligne par ligne) ; ces modèles ne servent que dans les blocs du contrat (vérifié le 2026-11-12)
LIGNES_FIXES = ["ContractNegotiationCashItem",        # salaire, prime de fidélité, commission de l'agent
                "ContractNegotiationItem",            # (alias « frames-contract-terms ») date de début, durée, statut, postes
                "ContractNegotiationPromisesItem"]    # promesses : temps de jeu, date de début
CIBLE_MODELE = "component.BaseComponentData.UIPickerKinitoSansCadenas"   # rien : chaque écran donne le vrai chemin
# offres de transfert (v23) : les lignes de clause (indemnité, date, primes, clauses…) ; leur cadenas lit lock = clause.LockProps
# (LockStatus, PossibleLockStatuses : de simples nombres 0..3, relevé en jeu) et son clic appelle l'action 121 du jeu sur
# handler = clause avec la nouvelle valeur (octets relevés sur TransferOfferClauseItem)
LIGNES_TRANSFERT = ["TransferOfferClauseItem", "TransferOfferClauseItemSimple", "TransferOfferClauseItemSecondaryProperty",
                    "TransferOfferClauseItemValueProperty"]
BLOCS_TRANSFERT = ["TransferOfferTermsBlock", "TransferOfferTermsDropdownBlock", "TransferOfferClausesArea",
                   "TransferOfferBonusClauseContent"]   # leurs listes de lignes de clause : classe agentoffer
CELLULE_T = "TeamGeneralPerformanceEnhancedLabel"     # 2e cellule FM inutilisée (citée par aucun bundle ni par le code, nom unique ; vérifié le 2026-11-12)
GUID_CELLULE_T = "3c675d5c0f21b2146b55295cddf9ac50"
PARAM_HANDLER = "uipickerhandler"                    # l'objet sur lequel le clic appelle l'action du jeu
ACTION_CADENAS = 121                                 # action du jeu « changer le cadenas » d'une clause de transfert
VALEUR_T = "row"                                     # une option du cadenas d'un transfert = le nombre lui-même
CHOIX_FIXES = "component.BaseComponentData.PossibleLockStatuses"         # les choix (les mêmes pour toutes ces lignes)
CELLULE = "TeamGeneralPerformanceLabel"
# blocs du contrat dont les listes portent nos lignes : on n'y ajoute qu'une classe (FM a deux variantes de chaque écran)
BLOCS = ["ContractTermsBlock", "ContractTermsCombinedBlock", "ContractPromisesBlock", "ContractPromisesCombinedBlock",
         "ContractTermsBlock_FMC", "ContractPromisesBlock_FMC"]
LISTES = ("add-on-list", "future-playing-times-list")
CLASSE_LISTE = "agentoffer"   # seule règle de FM : .agentoffer .virtualised-list__item--selected / :hover -> --data-tables-background
BOUTON_ACTIF = "buttons-controls-pc-default--active-true"     # contrôle FM avec son cadre (l'option en cours)
BOUTON_INACTIF = "buttons-controls-pc-default--active-false"  # contrôle FM nu : celui de la poubelle
GUID_CELLULE = "2f722db51ed885c49bfc9768908f42d4"   # TeamGeneralPerformanceLabel (catalogue Addressables)
SOURCE_ICONE = "NegotiationLockDropdownRow"          # ligne du menu FM : #lock-icon (SIImage) et #lock-text (texte)
SOURCE_BULLE = "RoleLabelwIcon"                      # infobulle posée dans une ligne FM, qui lit la ligne : Tooltip > SIText
SOURCE_NOMBRE = ("ContinentCompetitionsBlock", "MoreItems")   # SIVisible FM « la liste a plus de N éléments »
NOMBRES = (2, 3, 4)                                  # nombres d'options d'une ligne (relevés en jeu : 2, 3 ou 4)
PARAM = "uipickercadenas"                            # la donnée du cadenas de la ligne, vue depuis le bouton
PARAM_CHOIX = "uipickercadenaschoix"                 # les options possibles de la ligne, vues depuis le bouton
CIBLE = "uipickercadenascible"                       # ce que le clic écrit : 0 (négociable) si l'option est déjà en cours, elle sinon
NEGOCIABLE = "const.Zero"                            # valeur 0 = Négociable (cadenas ouvert)
OP_EGAL, OP_DIFFERENT = 2, 5                         # ComparisonOperator de FM (relevés sur isSelected du bouton d'Alex)
CACHER_NEGOCIABLE = True                             # le bouton « Négociable » est caché : recliquer sur l'option en cours y revient
EXCLURE = "const.Three"                              # valeur 3 = Retirer et exclure
ICONE_EXCLURE = "ui-concepts-remove-from-list_small"  # rond barré de FM (16 px), à la place de la poubelle de la table
COULEUR_EXCLURE = "transfer-comment-neutral-icon-colour"  # la couleur que la table donne à l'option 3
SOURCE_ICONE_SIMPLE = ("ContractNegotiationAddOnItem", "ui-concepts-delete_small")   # icône FM sans liaison (la poubelle)
VALEUR = "row.RowData"                               # une option de la liste = DynamicReference { RowData = 0..3 } (relevé en jeu)
LISTE_EQUIPES = "row.teamcontainer.Teams"            # ce que compte le bouton d'Alex pour savoir s'il est le dernier
PREFIXE = "UIPickerKinito"
NOM_GROUPE = f"{PREFIXE}-cadenas-v{VERSION}"
NOM_CELLULE = f"{PREFIXE}BoutonCadenas-v{VERSION}"
NOM_CELLULE_T = f"{PREFIXE}BoutonCadenasTransfert-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_contrat_cadenas.actif")

for k, v in {"width": (131105, 3), "height": (131087, 3), "margin-left": (131091, 3), "min-width": (131097, 3),
             "max-width": (131095, 3), "flex-shrink": (131085, 2), "margin-right": (131092, 3), "padding": (262151, 3),
             "justify-content": (131088, 7), "min-height": (131096, 3), "align-items": (131073, 7),
             "margin-bottom": (131090, 3), "margin-top": (131093, 3), "height-auto": (131087, 1)}.items():
    sm.PROPRIETES.setdefault(k, v)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def listes_du_bloc(t):
    return [r for r in t.walk() if t.name(r) in LISTES]


def nos_surcharges(t):
    """surcharges de nos rangées posées par un bloc sur ses lignes fixes (v19)"""
    out = []
    for r in t.walk():
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = (t.refs.get(o["m_SerializedData"]["rid"]) or {}).get("data") or {}
            if (d.get("name") or "").startswith(PREFIXE):
                out.append((r, o))
    return out


def modifie(m, t):
    if m in BLOCS_TRANSFERT:
        return any(CLASSE_LISTE in (t.elem(r).get("m_Classes") or []) for r in t.walk()
                   if (t.sd(r) if r in t.refs else {}).get("RowTemplate"))
    if m in BLOCS:
        return any(CLASSE_LISTE in (t.elem(r).get("m_Classes") or []) for r in listes_du_bloc(t)) or bool(nos_surcharges(t))
    return bool(marques(t))


def a_jour_modele(m, t):
    if m in BLOCS or m in BLOCS_TRANSFERT:
        return modifie(m, t)
    cible = NOM_CELLULE if m == CELLULE else NOM_CELLULE_T if m == CELLULE_T else NOM_GROUPE
    return any(t.name(r) == cible for r in marques(t))


def construire_bloc(t):
    listes = listes_du_bloc(t)
    if not listes:
        return []
    fixes = []
    for r in listes:
        cl = t.elem(r).setdefault("m_Classes", [])
        if CLASSE_LISTE not in cl:
            cl.append(CLASSE_LISTE)
        d = t.sd(r)
        if d.get("FixedElementSize_UxmlAttributeFlags"):   # place réservée par ligne (50 px chez FM)
            d["FixedElementSize"] = float(LIGNE_PAS)        # sert d'estimation quand la liste mesure ses lignes
            if not d.get("DynamicElements"):                # place fixe : une ligne sur deux lignes de texte débordait
                d["DynamicElements"], d["DynamicElements_UxmlAttributeFlags"] = 1, 1   # comme la liste des promesses de FM
            fixes.append(t.name(r))
    return [f"classe {CLASSE_LISTE} sur {', '.join(t.name(r) for r in listes)}"
            + (f", lignes mesurées ({LIGNE_PAS} px estimés) sur {', '.join(fixes)}" if fixes else "")]


# ---------- événement « copier une valeur » de FM (217,15,225,87) ----------
def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def _bloc(b):
    return struct.pack("<i", len(b)) + b


def evenement_copier(source, destination):
    """événement de bouton qui copie la valeur de <source> dans <destination> (format de FM, vérifié en refaisant à
    l'identique celui de ClubNationInfoTabButton)"""
    corps = bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([1, 0])
    return list(bytes([1, 1, 1, 1, 1]) + struct.pack("<i", len(corps)) + corps)


def evenement_action(objet, argument, action):
    """événement de bouton qui appelle l'action <action> du jeu sur <objet> avec la valeur de <argument> (format de FM,
    vérifié en refaisant à l'identique celui du menu du cadenas de TransferOfferClauseItem)"""
    corps = bytes([27, 222, 7, 0, 1]) + _bloc(_texte(objet)) + _bloc(_texte(argument)) + struct.pack("<i", action)
    return list(bytes([1, 1, 1, 1, 1]) + struct.pack("<i", len(corps)) + corps)


def _verifier_action():
    attendu = [1, 1, 1, 1, 1, 45, 0, 0, 0, 27, 222, 7, 0, 1, 10, 0, 0, 0, 1, 1, 7, 104, 97, 110, 100, 108, 101, 114, 18, 0,
               0, 0, 1, 1, 15, 108, 111, 99, 107, 46, 76, 111, 99, 107, 83, 116, 97, 116, 117, 115, 121, 0, 0, 0]
    return evenement_action("handler", "lock.LockStatus", 121) == attendu


def _verifier_evenement():
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    return evenement_copier("rowindex", "selected-tab") == attendu


# ---------- le bouton : TeamGeneralPerformanceLabel réécrite ----------
class Sources:
    def __init__(self):
        b = ouvrir(ee.BOUTON_SOURCE)
        self.bouton = b and b[3]
        i = ouvrir(SOURCE_ICONE)
        self.ic = i and i[3]
        self.icone = self.ic and first(self.ic, lambda r: self.ic.name(r) == "lock-icon")
        texte = self.ic and first(self.ic, lambda r: self.ic.name(r) == "lock-text")
        self.texte_binding = texte and copy.deepcopy(self.ic.sd(texte).get("TextBinding"))
        u = ouvrir(SOURCE_BULLE)
        self.bu = u and u[3]
        self.bulle = self.bu and first(self.bu, lambda r: typ(self.bu, r) == "Tooltip"
                                       and len(self.bu.children(r)) == 1
                                       and typ(self.bu, self.bu.children(r)[0]) == "SIText")
        self.mx = ee.Morceaux()
        n = ouvrir(SOURCE_NOMBRE[0])
        self.vn = n and n[3]
        self.nombre = self.vn and first(self.vn, lambda r: self.vn.name(r) == SOURCE_NOMBRE[1] and typ(self.vn, r) == "SIVisible")

    def ok(self):
        return None not in (self.bouton, self.icone, self.texte_binding, self.bulle, self.nombre) and self.mx.ok()


def construire_cellule(t, src, nom=None, valeur=None, evenement=None, extra=(), cellule=None):
    """nom / valeur / evenement / extra (paramètres de plus) / cellule : pour la 2e cellule (transferts, v23) ; par
    défaut ceux des contrats"""
    nom = nom or NOM_CELLULE
    VALEUR = valeur or globals()["VALEUR"]
    cellule = cellule or CELLULE
    msgs = ee.construire_bouton(t, src.bouton)   # boutons segmentés d'Alex ; paramètres, surbrillance et clic changés
    if any("introuvable" in m for m in msgs):
        return msgs
    racine = t.tt["m_VisualTree"]["rid"]
    c = t.children(racine)[0]
    t.sd(c)["name"] = nom
    composants = [x["rid"] for x in t.sd(c).get("m_components") or []]
    attente = next((x for x in composants if "BindingExpect" in t.refs[x]["type"]["class"]), None)
    reglage = next((x for x in composants if "BindingSetter" in t.refs[x]["type"]["class"]), None)
    if attente is None or reglage is None:
        return ["composants du bouton introuvables"]
    # paramètres : row = une option du cadenas (sans type, comme la ligne du menu FM), uipickercadenas = la donnée,
    # uipickercadenaschoix = les options de la ligne
    params = t.refs[attente]["data"]["Parameters"]
    for p in params:
        if p["name"] == "row":
            p["type"]["id"] = 0
        elif p["name"] == ee.PARAM_EQUIPE:
            p["name"], p["type"]["id"] = PARAM, 0
            choix = copy.deepcopy(p)
            choix["name"] = PARAM_CHOIX
    if not any(p["name"] == PARAM for p in params):
        return ["paramètres du bouton introuvables"]
    params.append(choix)
    for x in extra:
        q = copy.deepcopy(choix)
        q["name"] = x
        params.append(q)
    for e in (t.elem(r) for r in t.walk(c)):
        for prop in e.get("m_Properties") or []:
            if prop["name"] == "params":
                prop["value"] = prop["value"].replace("row:team:False", "row:invalid:False") \
                    .replace(f"{ee.PARAM_EQUIPE}:team:True", f"{PARAM}:invalid:True")
    # surbrillance : l'option affichée par le bouton est celle de la ligne ; forme (début / milieu / fin de la
    # rangée) : le dernier bouton est celui de la dernière option de la ligne
    compte = 0
    for f in t.refs[reglage]["data"]["BindFunction"]:
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        if any(b"isSelected" in a[1] for a in args):
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(
                ee._chemins(args, {"row.UniqueId": VALEUR, f"{ee.PARAM_EQUIPE}.UniqueId": PARAM}))
        elif any(a[1].endswith(LISTE_EQUIPES.encode()) for a in args):
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(ee._chemins(args, {LISTE_EQUIPES: PARAM_CHOIX}))
            compte += 1
    if compte != 1:
        return [f"forme des boutons ({LISTE_EQUIPES}) introuvable"]
    # style : le contrôle de FM (celui de la poubelle) au lieu des boutons segmentés d'Alex
    styles = 0
    for r in t.walk(c):
        if typ(t, r) != "SIStyleSetter":
            continue
        f = t.sd(r).get("BindFunction") or {}
        entrees = (f.get("m_inputs") or {}).get("m_variable") or {}
        args = decode_args(entrees.get("m_argumentBytes") or [])
        if not any(b"isSelected" in a[1] for a in args):
            continue
        for a in args:
            if a[0] == b"SI.VisualScripting.StringVisualArg":
                texte = a[1][2:].decode(errors="replace")
                if texte.startswith("buttons-segmented-button-row-active"):
                    nouveau = BOUTON_ACTIF
                elif texte.startswith("buttons-segmented-button-row-inactive"):
                    nouveau = BOUTON_INACTIF
                else:
                    continue
                a[1] = b"\x01" + _enc_varint(len(nouveau)) + nouveau.encode()
                styles += 1
        entrees["m_argumentBytes"] = encode_args(args)
    # 6 (début / milieu / fin de rangée, actif et inactif) ; 8 depuis la v1.04 d'Alex (entrainement_equipes v6+ : 4e cas,
    # « bouton seul / boutons séparés », copie du début de rangée arrondie des deux côtés) : tous deviennent le contrôle
    if styles not in (6, 8):
        return [f"styles des boutons d'Alex introuvables ({styles} sur 6 ou 8)"]
    # interrupteur : CIBLE = 0 (négociable) si l'option est déjà en cours, l'option sinon ; copie des deux fonctions
    # isSelected (égal / différent), même destination, autre valeur
    nouvelles = []
    for f in t.refs[reglage]["data"]["BindFunction"]:
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        if not any(a[1].endswith(b"isSelected") for a in args):
            continue
        f2 = copy.deepcopy(f)
        f2["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(
            ee._chemins(args, {"isSelected": CIBLE, "const.True": NEGOCIABLE, "const.False": VALEUR}))
        nouvelles.append(f2)
    if len(nouvelles) != 2:
        return [f"fonctions isSelected du bouton introuvables ({len(nouvelles)} sur 2)"]
    t.refs[reglage]["data"]["BindFunction"].extend(nouvelles)
    variables = next((x for x in composants if "BindingVariables" in t.refs[x]["type"]["class"]), None)
    if variables is None:
        return ["variables du bouton (BindingVariablesComponent) introuvables"]
    vv = t.refs[variables]["data"].setdefault("ValueVariables", [])
    if not vv:
        return ["variables du bouton : aucun modèle de déclaration"]
    if not any(v["m_name"] == CIBLE for v in vv):
        v = copy.deepcopy(vv[0])
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = CIBLE, "Int|0|"
        vv.append(v)
    # chaque segment : l'icône de l'option + l'infobulle de son nom, clic = CIBLE devient la valeur de la ligne
    ev = evenement or evenement_copier(CIBLE, PARAM)
    boutons = [r for r in t.walk(c) if typ(t, r) == "SIButton"]
    if not boutons:
        return ["boutons du modèle FM introuvables"]
    # « Retirer et exclure » : la table des cadenas lui donne la poubelle, celle de la ligne juste à côté ; on affiche un
    # rond barré à la place (une icône FM sans liaison, sous SIVisible == 3 ; l'icône de la table sous != 3)
    s_cmp, vis = ni.visible_model(ni.SOURCE_COMPARE, ni.FN_COMPARE)
    o_simple = ouvrir(SOURCE_ICONE_SIMPLE[0], depart_original=True)
    t_simple = o_simple and o_simple[3]
    simple = t_simple and first(t_simple, lambda r: t_simple.name(r) == SOURCE_ICONE_SIMPLE[1])
    if vis is None or simple is None:
        return ["SIVisible de comparaison ou icône simple de FM introuvable"]
    for b in boutons:
        t.sd(b)["Events"]["m_bytes"] = list(ev)
        for k in [k for k in t.children(b) if typ(t, k) == "SIText"]:
            t.remove(k)
        # un bouton à la taille d'une icône (les boutons d'équipes d'Alex sont faits pour un nom)
        t.styles.style(t, b, {"width": SEGMENT, "min-width": SEGMENT, "height": SEGMENT, "min-height": SEGMENT,
                              "padding": 0, "justify-content": "center", "align-items": "center"})
        icone = t.clone(src.icone, b, src=src.ic)
        t.styles.copy_from(src.ic.styles, t, icone)
        t.sd(icone)["name"] = f"{PREFIXE}-cadenas-icone"
        # la ligne du menu lui donne des marges et 20 x 20 px : on revient aux 16 px des icônes de FM (celle de la poubelle)
        t.styles.style(t, icone, {"margin-left": 0, "margin-right": 0, "width": ICONE, "height": ICONE})
        place = t.children(b).index(icone)
        sauf3 = ni.new_visible(t, s_cmp, vis, b, place, f"{PREFIXE}-cadenas-icone-table",
                               ni.make_binding(s_cmp.sd(vis)["Binding"], OP_DIFFERENT, [VALEUR, EXCLURE]))
        deplacer(t, icone, sauf3)
        si3 = ni.new_visible(t, s_cmp, vis, b, place + 1, f"{PREFIXE}-cadenas-icone-exclure",
                             ni.make_binding(s_cmp.sd(vis)["Binding"], OP_EGAL, [VALEUR, EXCLURE]))
        for v in (sauf3, si3):
            if "m_ParentId" in t.elem(v):
                t.elem(v)["m_ParentId"] = t.elem(b).get("m_Id", t.elem(v)["m_ParentId"])
        stop = t.clone(simple, si3, src=t_simple)
        t.styles.copy_from(t_simple.styles, t, stop)
        t.sd(stop)["name"], t.sd(stop)["name_UxmlAttributeFlags"] = f"{PREFIXE}-cadenas-exclure", 1
        t.elem(stop)["m_Classes"] = [ICONE_EXCLURE, COULEUR_EXCLURE]
        if "m_ParentId" in t.elem(stop):
            t.elem(stop)["m_ParentId"] = t.elem(si3).get("m_Id", t.elem(stop)["m_ParentId"])
        bulle = t.clone(src.bulle, b, src=src.bu)   # sur le bouton entier : survol de tout le segment
        t.styles.copy_from(src.bu.styles, t, bulle)
        t.sd(bulle)["name"], t.sd(bulle)["name_UxmlAttributeFlags"] = f"{PREFIXE}-cadenas-bulle", 1
        texte = t.children(bulle)[0]
        t.sd(texte)["name"], t.sd(texte)["name_UxmlAttributeFlags"] = f"{PREFIXE}-cadenas-bulle-texte", 1
        t.sd(texte)["TextBinding"] = copy.deepcopy(src.texte_binding)
        # la table des cadenas de FM attend la valeur : le menu FM la lui donne dans row, notre liste y met la paire
        for liaison in (t.sd(icone)["Binding"], t.sd(texte)["TextBinding"]):
            entrees = liaison["m_visualFunction"]["m_inputs"]["m_variable"]
            args = decode_args(entrees["m_argumentBytes"])
            if not any(a[1] == b"\x01\x03row" for a in args):
                return ["icône ou texte du menu FM : donnée « row » introuvable"]
            entrees["m_argumentBytes"] = encode_args(ee._chemins(args, {"row": VALEUR}))
    if CACHER_NEGOCIABLE:
        # tout le bouton sous un SIVisible « row.RowData différent de 0 » (comparaison d'Alex) : plus de bouton Négociable
        s_cmp, vis = ni.visible_model(ni.SOURCE_COMPARE, ni.FN_COMPARE)
        if vis is None:
            return ["SIVisible de comparaison de FM introuvable"]
        liaison = ni.make_binding(s_cmp.sd(vis)["Binding"], OP_DIFFERENT, [VALEUR, NEGOCIABLE])
        # seulement l'affichage : les composants de liaison (BindingExpect / Variables / Setter) restent sur le bouton
        enfants = [k for k in t.children(c) if not typ(t, k).endswith("Component")]
        v = ni.new_visible(t, s_cmp, vis, c, 0, f"{PREFIXE}-cadenas-sauf-negociable", liaison)
        if "m_ParentId" in t.elem(v):
            t.elem(v)["m_ParentId"] = t.elem(c).get("m_Id", t.elem(v)["m_ParentId"])
        for k in enfants:
            deplacer(t, k, v)
    return [f"bouton : {cellule}, icône + infobulle du menu FM (d'après {VALEUR}), clic = "
            + ("action du jeu" if evenement else f"{CIBLE} -> {PARAM}") + " (0 si déjà en cours)"
            + (", Négociable caché" if CACHER_NEGOCIABLE else "") + f", Retirer et exclure en {ICONE_EXCLURE}"]


def deplacer(t, rid, parent):
    """déplace un élément (et son sous-arbre) à la fin des enfants de parent"""
    ancien = t.parent.get(rid)
    if ancien is not None:
        t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != rid]
    t.elem(parent).setdefault("m_Children", []).append({"rid": rid})
    t.elem(rid)["m_Parent"] = {"rid": parent}
    if "m_ParentId" in t.elem(rid):
        t.elem(rid)["m_ParentId"] = t.elem(parent).get("m_Id", t.elem(rid)["m_ParentId"])
    t.parent[rid] = parent


# ---------- une ligne de liste ----------
def visible_nombre(t, src, parent, liste, seuil, inverse, nom):
    """SIVisible de FM « liste a plus de <seuil> éléments » (inverse : « pas plus de »), vide, sous parent"""
    v = t.clone(src.nombre, parent, src=src.vn)
    for k in list(t.children(v)):
        t.remove(k)
    t.styles.copy_from(src.vn.styles, t, v)
    t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = f"{PREFIXE}-cadenas-{nom}", 1
    if "m_ParentId" in t.elem(v):
        t.elem(v)["m_ParentId"] = t.elem(parent).get("m_Id", t.elem(v)["m_ParentId"])
    entrees = t.sd(v)["Binding"]["m_visualFunction"]["m_inputs"]["m_variable"]
    args = ee._chemins(decode_args(entrees["m_argumentBytes"]), {"divisionlist": liste, "MinItems": seuil})
    for a in args:
        if a[0] == b"SI.VisualScripting.BooleanVisualArg":
            a[1] = b"\x01" if inverse else b"\x00"
    entrees["m_argumentBytes"] = encode_args(args)
    return v


def rangee(t, src, parent, liste, n, guid=None):
    """liste horizontale d'Alex sur les options de la ligne, à la largeur de n boutons"""
    mx = src.mx
    lst = t.clone(mx.liste, parent, src=mx.lst)
    ee._vide(t, lst)
    wd = t.sd(lst)
    wd["RowTemplate"] = {"m_AssetGUID": guid or GUID_CELLULE, "m_SubObjectName": "", "m_SubObjectType": ""}
    wd["Binding"]["m_visualFunction"] = path_arg(wd["Binding"]["m_visualFunction"], liste)
    visibles = n - (1 if CACHER_NEGOCIABLE else 0)   # le bouton Négociable (0) est caché
    t.styles.style(t, lst, {"width": visibles * SEGMENT, "height": HAUTEUR, "flex-shrink": 0})
    return lst


def construire_ligne(t, src, fixe=False, sortie=None):
    """fixe : ligne d'un modèle commun (salaire…), sans chemin de cadenas dans le modèle (l'écran le donne ligne par
    ligne, voir surcharges_fixes) ; pas de poubelle forcément ; ni resserrement ni molette"""
    cadenas = first(t, lambda r: t.name(r) == "lock-button-enabled")
    if cadenas is None:
        return ["cadenas de la ligne (#lock-button-enabled) introuvable"]
    menus = [r for r in t.walk(cadenas) if t.elem(r).get("m_TemplateAlias") == "buttons-dropdown-icon-base-default"]
    if len(menus) != 1:
        return ["menu du cadenas introuvable"]
    # la donnée écrite et les choix : ceux du menu (surcharge du modèle inclus)
    cible = choix = None
    for o in t.elem(menus[0]).get("m_SerializedDataOverride") or []:
        d = (t.refs.get(o["m_SerializedData"]["rid"]) or {}).get("data") or {}
        if d.get("SelectionValueBinding", {}).get("m_path"):
            cible = d["SelectionValueBinding"]["m_path"]
            args = decode_args(d["BindChoicesFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
            for a in args:
                if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                    choix = a[1][2:].decode()
    if fixe:
        cible, choix = cible or CIBLE_MODELE, choix or CHOIX_FIXES
    if not cible or not choix:
        return ["donnée ou choix du cadenas introuvables"]
    ligne = first(t, lambda r: any(c.startswith("frames-contract-terms-fill") for c in t.elem(r).get("m_Classes") or []))
    if ligne is None:
        return ["cadre de la ligne introuvable"]
    # juste avant la poubelle (elle reste tout à droite) : copie du SIEnabled du cadenas (même grisé), vidée
    poubelle = next((i for i, k in enumerate(t.children(ligne))
                     if any(t.name(r) == "ui-concepts-delete_small" for r in t.walk(k))), None)
    if poubelle is None and not fixe:
        return ["poubelle de la ligne introuvable"]
    g = t.clone(cadenas, ligne, poubelle)
    for k in list(t.children(g)):
        t.remove(k)
    t.sd(g)["name"], t.sd(g)["name_UxmlAttributeFlags"] = NOM_GROUPE, 1
    if "m_ParentId" in t.elem(g):
        t.elem(g)["m_ParentId"] = t.elem(ligne).get("m_Id", t.elem(g)["m_ParentId"])
    t.styles.style(t, g, {"margin-left": ECART, "margin-right": ECART_POUBELLE, "flex-shrink": 0})
    mx = src.mx
    rm = t.clone(mx.remap, g, src=mx.ent)
    ee._vide(t, rm)
    sd = t.sd(rm)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}-cadenas-donnee", 1
    m = copy.deepcopy(sd["Mappings"][0])
    m["from"], m["to"]["m_path"], m["type"]["id"] = PARAM, cible, 0
    m2 = copy.deepcopy(m)
    m2["from"], m2["to"]["m_path"] = PARAM_CHOIX, choix
    sd["Mappings"] = [m, m2]
    t.styles.style(t, rm, {"height": HAUTEUR, "flex-shrink": 0})
    if sortie is not None:
        sortie["rm"] = rm
        sortie["menu"] = t.elem(menus[0])["m_Id"]   # l'instance du menu du cadenas dans le modèle
    # une rangée par nombre d'options, à sa largeur exacte, une seule visible : collée à la poubelle même à 2 ou 3 options
    plus3 = visible_nombre(t, src, rm, choix, "const.Three", False, "4")         # plus de 3 options
    rangee(t, src, plus3, choix, 4)
    pas3 = visible_nombre(t, src, rm, choix, "const.Three", True, "3-ou-moins")  # 3 ou moins
    plus2 = visible_nombre(t, src, pas3, choix, "const.Two", False, "3")
    rangee(t, src, plus2, choix, 3)
    pas2 = visible_nombre(t, src, pas3, choix, "const.Two", True, "2")
    rangee(t, src, pas2, choix, 2)
    # le cadenas de gauche disparaît
    t.remove(cadenas)
    # le nom ne s'écrase plus ; le sélecteur de date (clauses à échéance) ne prend plus toute la place
    nom = first(t, lambda r: t.name(r) == "Frame" and t.parent.get(r) is not None)
    nom_etire = False
    if nom is not None:
        t.styles.style(t, nom, {"min-width": NOM_LARGEUR_MIN})
        # v24 : le nom prend la place libre, comme dans les lignes de primes et de promesses de FM (flex 1 0 0 +
        # flex-grow 1 sur leur #Frame) ; la ligne du temps de jeu futur ne l'a pas : son menu restait au milieu (FM le
        # met entre le nom et la poubelle) et nos icônes le décalaient encore (vu en jeu par Kinito)
        regle = t.elem(nom).get("m_RuleIndex", -1)
        if not fixe and not (regle >= 0 and any(p[0] in (FLEX_GROW, FLEX) for p in t.styles.values(regle))):
            t.styles.style(t, nom, {"flex-grow": 1})
            nom_etire = True
    # v24 : le menu du type d'objectif de temps de jeu (temps de jeu futur) ne prend plus toute la largeur, calé à droite
    def sous_objectif(r):
        p = t.parent.get(r)
        while p is not None:
            if t.name(p) == OBJECTIF_BLOC:
                return True
            p = t.parent.get(p)
        return False
    objectif = first(t, lambda r: t.name(r) == OBJECTIF_MENU and sous_objectif(r))
    menu_temps = None
    if objectif is not None and not fixe:
        t.styles.style(t, objectif, {"max-width": OBJECTIF_LARGEUR_MAX})
        # v25 : le menu du temps de jeu de la saison (#button-1-frame), sans largeur chez FM : vide (aucun temps de jeu
        # choisi), il s'étirait sur toute la ligne (vu en jeu par Kinito) ; borné comme FM borne celui des promesses
        # (150 / 165 px), un peu plus large pour « Joueur de rotation (Recommandé) »
        cadre = first(t, lambda r: t.name(r) == "button-1-frame")
        menu_temps = cadre is not None and next((k for k in t.children(cadre)
                                                 if t.elem(k).get("m_TemplateAlias") == "inputs-combobox-default-default-base"), None)
        if menu_temps:
            t.styles.style(t, menu_temps, {"min-width": MENU_TEMPS_LARGEUR[0], "max-width": MENU_TEMPS_LARGEUR[1]})
    date = first(t, lambda r: t.name(r) == "end-date-selector")
    if date is not None:
        t.styles.style(t, date, {"max-width": DATE_LARGEUR_MAX, "flex-shrink": 1})
    if fixe:
        # v20 : resserrées aussi (FM : 38 px + 12 de marge, classe du cadre) ; hauteur libre, 32 px au moins : une ligne
        # fixe peut avoir une 2e ligne de texte
        t.styles.style(t, ligne, {"height-auto": 2, "min-height": LIGNE_HAUTEUR, "margin-top": LIGNE_ECART,
                                  "margin-bottom": LIGNE_ECART})
        return [f"cadenas -> icônes à droite (ligne fixe : chemin donné par chaque écran, choix {choix}), "
                f"ligne {LIGNE_HAUTEUR} px au moins + {LIGNE_ECART} + {LIGNE_ECART}"]
    # lignes plus serrées : plus de primes à l'écran, la liste défile moins. Hauteur libre, LIGNE_HAUTEUR au moins : un
    # nom de prime ou une note de promesse sur deux lignes agrandit la ligne au lieu de déborder sur la suivante (v21 :
    # vu en jeu par Kinito en grande taille d'interface, la hauteur fixe de 32 px faisait se chevaucher les noms)
    t.styles.style(t, ligne, {"height-auto": 2, "min-height": LIGNE_HAUTEUR, "margin-top": LIGNE_ECART,
                              "margin-bottom": LIGNE_ECART})
    msgs = [f"cadenas -> icônes à droite, avant la poubelle ({cible}, choix {choix})"
            + (", date plafonnée" if date is not None else "") + f", ligne {LIGNE_HAUTEUR} px au moins + {LIGNE_ECART} + {LIGNE_ECART}"
            + (", nom étiré (menu et icônes à droite)" if nom_etire else "")
            + (f", menu d'objectif {OBJECTIF_LARGEUR_MAX} px au plus" if objectif is not None and not fixe else "")
            + (f", menu du temps de jeu {MENU_TEMPS_LARGEUR[0]} à {MENU_TEMPS_LARGEUR[1]} px" if menu_temps else "")]
    if MOLETTE and first(t, lambda r: t.name(r) == "button-2-remapper") is not None:
        msgs += molette_numerique(t)
    return msgs


def deplacer_a(t, rid, parent, index):
    """déplace un élément (et son sous-arbre) sous parent, à la place index"""
    deplacer(t, rid, parent)
    kids = t.elem(parent)["m_Children"]
    k = kids.pop()
    kids.insert(index, k)


def construire_ligne_transfert(t, src):
    """ligne de clause d'une offre de transfert : son cadenas (#lock-button-remapper : lock = clause.LockProps,
    handler = clause, puis #lock-button-enabled > menu de FM) passe à droite, juste avant le bouton qui retire la clause ;
    le menu est remplacé par nos rangées d'icônes (2e cellule : valeur = le nombre, clic = action 121 sur handler) ; le
    bouton qui retire la clause prend la poubelle (le rond barré est pour « Retirer et exclure », comme aux contrats) ;
    la ligne est resserrée comme celles des contrats"""
    rml = first(t, lambda r: t.name(r) == "lock-button-remapper")
    en = rml is not None and first(t, lambda r: t.name(r) == "lock-button-enabled" and t.parent.get(r) == rml)
    ligne = first(t, lambda r: any(c.startswith("frames-contract-terms-fill") for c in t.elem(r).get("m_Classes") or []))
    if rml is None or not en or ligne is None:
        return ["cadenas ou cadre de la ligne de clause introuvable"]
    retrait = next((i for i, k in enumerate(t.children(ligne))
                    if any(t.name(r) == "ui-concepts-delete_small" for r in t.walk(k))), None)
    if retrait is None:
        return ["bouton qui retire la clause introuvable"]
    deplacer_a(t, rml, ligne, retrait)
    for k in list(t.children(en)):          # le menu de FM
        t.remove(k)
    t.sd(en)["name"], t.sd(en)["name_UxmlAttributeFlags"] = NOM_GROUPE, 1
    t.styles.style(t, en, {"margin-left": ECART, "margin-right": ECART_POUBELLE, "flex-shrink": 0})
    t.styles.style(t, rml, {"flex-shrink": 0})
    mx = src.mx
    rm = t.clone(mx.remap, en, src=mx.ent)
    ee._vide(t, rm)
    sd = t.sd(rm)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}-cadenas-donnee", 1
    m = copy.deepcopy(sd["Mappings"][0])
    m["type"]["id"] = 0
    alias = []
    for de, vers in ((PARAM, "lock.LockStatus"), (PARAM_CHOIX, "lock.PossibleLockStatuses"), (PARAM_HANDLER, "handler")):
        x = copy.deepcopy(m)
        x["from"], x["to"]["m_path"] = de, vers
        alias.append(x)
    sd["Mappings"] = alias
    t.styles.style(t, rm, {"height": HAUTEUR, "flex-shrink": 0})
    choix = "lock.PossibleLockStatuses"
    plus3 = visible_nombre(t, src, rm, choix, "const.Three", False, "4")
    rangee(t, src, plus3, choix, 4, GUID_CELLULE_T)
    pas3 = visible_nombre(t, src, rm, choix, "const.Three", True, "3-ou-moins")
    plus2 = visible_nombre(t, src, pas3, choix, "const.Two", False, "3")
    rangee(t, src, plus2, choix, 3, GUID_CELLULE_T)
    pas2 = visible_nombre(t, src, pas3, choix, "const.Two", True, "2")
    rangee(t, src, pas2, choix, 2, GUID_CELLULE_T)
    # le bouton qui retire la clause : la poubelle de FM (il avait le rond barré)
    for r in t.walk(ligne):
        if t.name(r) == "ui-concepts-delete_small":
            t.elem(r)["m_Classes"] = ["ui-concepts-delete_small"]
    t.styles.style(t, ligne, {"height-auto": 2, "min-height": LIGNE_HAUTEUR, "margin-top": LIGNE_ECART,
                              "margin-bottom": LIGNE_ECART})
    return [f"cadenas -> icônes à droite, avant le bouton qui retire la clause (devenu poubelle), ligne "
            f"{LIGNE_HAUTEUR} px au moins + {LIGNE_ECART} + {LIGNE_ECART}"]


def construire_bloc_transfert(t, guids):
    """listes d'un écran de transfert dont les lignes sont des lignes de clause : classe agentoffer (la ligne cliquée
    ne passe pas en violet). Elles mesurent déjà leurs lignes (DynamicElements 1)."""
    faites = []
    for r in t.walk():
        d = t.sd(r) if r in t.refs else {}
        if (d.get("RowTemplate") or {}).get("m_AssetGUID") in guids:
            cl = t.elem(r).setdefault("m_Classes", [])
            if CLASSE_LISTE not in cl:
                cl.append(CLASSE_LISTE)
            faites.append(t.name(r))
    return [f"classe {CLASSE_LISTE} sur {', '.join(faites)}"] if faites else []


def _drapeaux(d, *cles):
    for k in cles:
        if k + "_UxmlAttributeFlags" in d:
            d[k + "_UxmlAttributeFlags"] = 1


def molette_numerique(t):
    """primes en pourcentage / en années (button-1 : menu simple de FM, sans molette) : on y met une copie du champ des
    montants de la même ligne (button-2 : BindingRemapper > FMCombobox, molette et -/+), branchée sur les choix et la
    valeur du pourcentage (component.AddOnPossibleNumericValues / AddOnNumericValue : paires {PropertyValue, DisplayValue},
    relevées en jeu). v15 : les -/+ gardent les actions de la ligne (51 / 52 sur component) : la molette passe par eux."""
    cadre = first(t, lambda r: t.name(r) == "button-1-frame")
    rm_montant = first(t, lambda r: t.name(r) == "button-2-remapper")
    menu = None
    if cadre is not None:
        menu = next((k for k in t.children(cadre)
                     if t.elem(k).get("m_TemplateAlias") == "inputs-combobox-default-default"), None)
    if cadre is None or rm_montant is None or menu is None:
        return ["molette : champ du pourcentage ou des montants introuvable"]
    choix = sel = None
    for o in t.elem(menu).get("m_SerializedDataOverride") or []:
        d = (t.refs.get(o["m_SerializedData"]["rid"]) or {}).get("data") or {}
        if d.get("SelectionValueBinding", {}).get("m_path"):
            choix, sel = copy.deepcopy(d["BindChoicesFunction"]), d["SelectionValueBinding"]["m_path"]
    if not choix or not sel:
        return ["molette : choix du pourcentage introuvables"]
    index = t.children(cadre).index(menu)
    rm = t.clone(rm_montant, cadre, index)
    t.sd(rm)["name"], t.sd(rm)["name_UxmlAttributeFlags"] = f"{PREFIXE}-molette", 1
    if "m_ParentId" in t.elem(rm):
        t.elem(rm)["m_ParentId"] = t.elem(cadre).get("m_Id", t.elem(rm)["m_ParentId"])
    # les données entrent dans le modèle par ses deux entrées, comme pour les montants : « value » -> la valeur du
    # pourcentage, « cashselection » -> ses choix (le modèle ne voit peut-être que ses entrées)
    liste = next((a[1][2:].decode() for a in decode_args(choix["m_inputs"]["m_variable"]["m_argumentBytes"])
                  if b"BindingPath" in a[0]), None)
    sd = t.sd(rm)
    m = next((x for x in sd["Mappings"] if x["from"] == "value"), None)
    m2 = next((x for x in sd["Mappings"] if x["from"] == "cashselection"), None)
    if m is None or m2 is None or not liste:
        return ["molette : entrées du champ des montants introuvables"]
    m["to"]["m_path"] = sel
    m2["to"]["m_path"], m2["type"]["id"] = liste, 0
    sd["Mappings"] = [m2, m]
    choix["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(
        ee._chemins(decode_args(choix["m_inputs"]["m_variable"]["m_argumentBytes"]), {liste: "cashselection"}))
    champ = next((k for k in t.walk(rm) if t.elem(k).get("m_TemplateAlias") == "inputs-combobox-controls-default"), None)
    if champ is None:
        return ["molette : champ des montants (modèle) introuvable"]
    fait = set()
    for o in t.elem(champ).get("m_SerializedDataOverride") or []:
        r = t.refs.get(o["m_SerializedData"]["rid"]) or {}
        d = r.get("data") or {}
        classe = r.get("type", {}).get("class", "")
        if classe.startswith("BindingExpect"):
            for prm in d.get("Parameters") or []:
                prm["isOptional"] = 1          # pas de valeur au départ : facultatif
                if prm["name"] == "cashselection":
                    prm["type"]["id"] = 0      # une liste de choix, plus la donnée des montants
            fait.add("attente")
        elif classe.startswith("FMCombobox"):
            d["BindChoicesFunction"] = copy.deepcopy(choix)
            d["SelectionValueBinding"] = {"m_path": "value"}
            d["ValueBinding"] = {"m_path": "value.propertyvalue"}
            tb = d["TextBinding"]
            tb["m_kind"], tb["m_direct"]["Path"]["m_path"] = 1, "value.displayvalue"
            # v15 : la molette du champ passe par ses -/+ (relevé en jeu par Kinito : sans eux, rien) ; on garde les
            # actions « monter / descendre » de la ligne (51 / 52 sur component, celles des montants) ; la validation
            # d'une saisie au clavier, propre aux montants, est retirée
            d["ValidateValueEvents"]["m_bytes"] = []
            for k in ("CanIncrementBoolFunc", "CanDecrementBoolFunc"):
                f = d[k]["m_inputs"]["m_variable"]
                f["m_argumentBytes"] = encode_args(ee._chemins(decode_args(f["m_argumentBytes"]), {
                    "cashselection.canincrementvalue": "const.True", "cashselection.candecrementvalue": "const.True"}))
            _drapeaux(d, "BindChoicesFunction", "SelectionValueBinding", "ValueBinding", "TextBinding", "RaiseValueEvent",
                      "LowerValueEvent", "ValidateValueEvents", "CanIncrementBoolFunc", "CanDecrementBoolFunc")
            fait.add("champ")
    if fait != {"attente", "champ"}:
        return [f"molette : réglages du champ des montants introuvables ({sorted(fait)})"]
    t.remove(menu)
    return [f"molette : pourcentage / années dans le champ des montants ({sel})"]


# ---------- lignes fixes : surcharges dans les blocs (v19) ----------
_catalogue = {}


def catalogue():
    """GUID (catalogue Addressables) -> nom des modèles des deux bundles d'écrans"""
    if not _catalogue:
        for b in nb.BUNDLES:
            env = nb.env_of(b)
            mb = {o.path_id: o for o in env.objects if o.type.name == "MonoBehaviour"}
            for o in env.objects:
                if o.type.name != "AssetBundle":
                    continue
                for k, v in o.read_typetree()["m_Container"]:
                    x = mb.get(v["asset"]["m_PathID"])
                    if x is None:
                        continue
                    try:
                        n = x.peek_name()
                    except Exception:
                        continue
                    if n != "inlineStyle":
                        _catalogue[k] = n
    return _catalogue


def surcharges_fixes(t, tt, rangees):
    """rangees : {modèle de ligne fixe : (id de notre BindingRemapper dans le modèle, sa référence, id de l'instance du
    menu du cadenas dans le modèle)}. Pour chaque ligne fixe du bloc : le chemin et les choix du cadenas, lus dans LA
    surcharge que le bloc pose sur le menu du cadenas (m_ElementIdsPath [instance du menu, SIDropdown]) — pas dans celle
    d'un autre menu de la ligne (la valeur) —, puis une surcharge de notre BindingRemapper (alias uipickercadenas -> ce
    chemin) sur la même ligne"""
    alias = {u["alias"]: catalogue().get(u["path"]) for u in tt.get("m_Usings") or []}
    faites = []
    for r in t.walk():
        e = t.elem(r)
        modele = alias.get(e.get("m_TemplateAlias"))
        if modele not in rangees:
            continue
        ident, ref, menu = rangees[modele]
        cible = choix = None
        for o in e.get("m_SerializedDataOverride") or []:
            if (o.get("m_ElementIdsPath") or [None])[0] != menu:
                continue
            d = (t.refs.get(o["m_SerializedData"]["rid"]) or {}).get("data") or {}
            if (d.get("SelectionValueBinding") or {}).get("m_path"):
                cible = d["SelectionValueBinding"]["m_path"]
                choix = next((a[1][2:].decode() for a in decode_args(d["BindChoicesFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
                              if b"BindingPath" in a[0]), None)
        if not cible:
            continue
        nouveau = copy.deepcopy(ref)
        nouveau["rid"] = t.new_rid()
        for mp in nouveau["data"]["Mappings"]:
            if mp["from"] == PARAM:
                mp["to"]["m_path"] = cible
            elif mp["from"] == PARAM_CHOIX and choix:
                mp["to"]["m_path"] = choix
        t.refs[nouveau["rid"]] = nouveau
        t.tt["references"]["RefIds"].append(nouveau)
        e.setdefault("m_SerializedDataOverride", []).append(
            {"m_ElementId": ident, "m_ElementIdsPath": [ident], "m_SerializedData": {"rid": nouveau["rid"]}})
        faites.append(f"{t.name(r)} -> {cible}")
    return [f"lignes fixes : {', '.join(faites)}"] if faites else []


# ---------- commandes ----------
def cmd_appliquer():
    if not ee._verifier_evenement() or not _verifier_evenement() or not _verifier_action():
        print("[Kinito] Contrat : format d'événement inattendu, rien enregistré")
        return
    tous = LIGNES + LIGNES_FIXES + [CELLULE] + BLOCS + LIGNES_TRANSFERT + [CELLULE_T] + BLOCS_TRANSFERT
    actuels = {m: ouvrir(m) for m in tous}
    if None in actuels.values():
        print("[Kinito] Contrat : modèles du contrat introuvables (renommés par une mise à jour ?), ignoré")
        return
    a_jour = all(a_jour_modele(m, actuels[m][3]) for m in tous)
    if a_jour:
        print("[Kinito] Contrat : déjà appliqué")
    else:
        ancien = any(modifie(m, v[3]) for m, v in actuels.items())
        travail = {m: ouvrir(m, depart_original=True) for m in tous}
        if any(modifie(m, v[3]) for m, v in travail.items()):
            print("[Kinito] Contrat : pas de sauvegarde d'origine propre, ignoré")
            return
        src = Sources()
        if not src.ok():
            print("[Kinito] Contrat : morceaux de FM (bouton, icône, infobulle, liste) introuvables, rien enregistré")
            return
        msgs = construire_cellule(travail[CELLULE][3], src)
        for m in LIGNES:
            msgs += [f"{m} : {x}" for x in construire_ligne(travail[m][3], src)]
        rangees = {}
        for m in LIGNES_FIXES:
            sortie = {}
            msgs += [f"{m} : {x}" for x in construire_ligne(travail[m][3], src, fixe=True, sortie=sortie)]
            if "rm" in sortie:
                tm = travail[m][3]
                rangees[m] = (tm.elem(sortie["rm"])["m_Id"], tm.refs[tm.elem(sortie["rm"])["m_SerializedData"]["rid"]],
                              sortie["menu"])
        for m in BLOCS:
            msgs += [f"{m} : {x}" for x in construire_bloc(travail[m][3]) + surcharges_fixes(travail[m][3], travail[m][2], rangees)]
        # offres de transfert (v23)
        msgs += [f"{CELLULE_T} : {x}" for x in construire_cellule(
            travail[CELLULE_T][3], src, nom=NOM_CELLULE_T, valeur=VALEUR_T, cellule=CELLULE_T,
            evenement=evenement_action(PARAM_HANDLER, CIBLE, ACTION_CADENAS), extra=(PARAM_HANDLER,))]
        for m in LIGNES_TRANSFERT:
            msgs += [f"{m} : {x}" for x in construire_ligne_transfert(travail[m][3], src)]
        nom_vers_guid = {n: g for g, n in catalogue().items()}
        guids_t = {nom_vers_guid.get(m) for m in LIGNES_TRANSFERT} - {None}
        for m in BLOCS_TRANSFERT:
            msgs += [f"{m} : {x}" for x in construire_bloc_transfert(travail[m][3], guids_t)]
        msgs += ["ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"[Kinito] Contrat : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Contrat : rien enregistré")
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
    for m in LIGNES + LIGNES_FIXES + [CELLULE] + BLOCS + LIGNES_TRANSFERT + [CELLULE_T] + BLOCS_TRANSFERT:
        o = ouvrir(m)
        if o is None or not modifie(m, o[3]):
            continue
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
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
    for m in LIGNES + LIGNES_FIXES + [CELLULE] + BLOCS + LIGNES_TRANSFERT + [CELLULE_T] + BLOCS_TRANSFERT:
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        etat = "à jour" if a_jour_modele(m, t) else "ANCIENNE version"
        print(f"{m} : " + (f"appliqué ({etat}, v{VERSION})" if modifie(m, t) else "d'origine"))
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
            print("[Kinito] Contrat : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
