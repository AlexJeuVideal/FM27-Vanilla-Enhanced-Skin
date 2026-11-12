"""Club > Finances (Vue d'ensemble) en UNE seule tuile (maquette du joueur, 2026-11-12), tous les modes d'affichage.

  Solde général    Dette restante | Dette initiale | Budgets pour les recrutements
  (courbe)                            |   Transfert  [Modifier le budget transferts]
  Projections (courbe)                |   Salaire    [Modifier le budget transferts]
  Revenus | Dépenses (courbes + listes)|   Recrutement [Modifier le budget recherche]
    ... [Demande aux dirigeants]      | Solde (projection, bloc FM)
                                      | Chiffre d'affaires (projection, bloc FM ; pas en mode Large)
                                      | [Clauses] [Sponsors]

Deux morceaux :
- grille (ui-tileslayouts) : dans chaque composition de ClubFinancesCardGridCompositionSet, la tuile des graphiques
  (FinancesOverviewGraphs) seule, sur toute la place ; les autres tuiles (budgets, FFP, salaires, dettes,
  sponsors...) retirées. La composition « défaut » de FM n'a pas la tuile des graphiques : elle y est ajoutée.
  ⚠ Une disposition perso du joueur (AppData\\LocalLow\\...\\CustomGridCompositions) passe avant : la réinitialiser.
- modèle FinanceOverviewGraphsBlock : cadre en ligne, contenu FM à gauche, colonne à droite (cachée dans les
  messages, comme les boutons du bas de FM). Morceaux de FM : sections de RecruitmentBudgetsTile_4x4 (recopiées),
  FinancesProjectionsBalanceBlock_4x4 / FinancesProjectionsTurnoverBlock_4x4 (inclus tels quels : les points de
  graphes_finances suivent), #DebtDataFrame de FinancesDebtsAndLoansTile_4x2 (recopié). Boutons « Modifier le
  budget » : ceux du bas de FM (#TransferAction, #ScoutingAction) déplacés sous Transfert / Recrutement, une copie
  de #TransferAction sous Salaire (le même dialogue de FM règle transferts et salaires). Clauses / Sponsors : bouton
  FM (#CancelButton d'InterfaceColoursPreferencesCard) avec le clic et le titre (traduction FM) des tuiles
  ClausesTile_4x2 / FinancesSponsorshipsTile_4x2.
Textes : tous des traductions de FM (suivent la langue du jeu).
Appliquer repart toujours des originaux sauvegardés ; retirer les remet.

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
import arbre as sm  # noqa: E402
from arbre import Tree, Styles  # noqa: E402
import notes_installations as ni  # noqa: E402
from notes_installations import first  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
LARGEUR_DROITE = 24       # % de la largeur de la tuile pour la colonne de droite
CA_HORS_LARGE = True      # v2 (demande du joueur) : Chiffre d'affaires caché en mode Large (Solde seul)
ECART_SMALL = 29          # v10 : px ajoutés en Small au-dessus du trait sous les budgets (0 = rien) ; v15 : 24 -> 27
#                           (vu en jeu v14 : un poil trop haut) ; v16 : 27 -> 31 (vu v15 : encore ~4 px trop haut) ;
#                           v17 : 31 -> 29 (vu v16 : trait de droite 2 px d'écran trop bas, capture du 2026-11-12 ;
#                           vu v18 : aligné)
DECALER_TRAIT_CA = -1     # v19 : px (+ = plus bas) du trait entre Solde et Chiffre d'affaires (vu v18 : 1 px trop bas)
# =====================================================================================================

VERSION = 19  # v1 : vue en jeu (colonne OK) ; v2 : Chiffre d'affaires caché en Large, dettes sous les Revenus ;
#               v3 : clic sur les dettes -> page Dettes (vue en jeu) ; v4 : dettes sur la ligne de « Demande aux
#               dirigeants » ; v5 : dettes en haut à droite, sur la ligne du titre des budgets (bas de FM d'origine,
#               vue en jeu) ; v6 : dettes en haut à droite de Solde général, 2 rangées (traits du haut alignés), plus
#               de trait entre Solde et Chiffre d'affaires (vue : Solde général figé) ; v7 : rangées + courbes retouchées (vue : pire) ; v8 :
#               rangées qui grandissent à parts égales, courbes de FM d'origine (vue : déborde en Large) ; v9 :
#               forme v5 (une ligne gauche | droite), dettes à droite de Solde général, sans trait Solde / CA
#               (vue, OK) ; v10 : en Small, écart fixe au-dessus du trait sous les budgets (ECART_SMALL) ;
#               v11 : en-têtes cliquables -> page de leur section (ENTETES) (vue : 4 lettres cliquables à gauche) ;
#               v12 : bouton posé par-dessus l'en-tête (toute sa surface) ; v13 : écart Small sur « mode == 1 » (vu :
#               rien) ; v14 : « mode > 1 », hauteur portée par un enfant du SIVisible (vu : marche,
#               presque aligné) ; v15 : écart 27 px ; v16 : 31 px ; v17 : 29 px ; v18 : Solde / Chiffre
#               d'affaires recopiés sans aspect de tuile, trait entre les deux (hors Large) ; v19 : ce trait -1 px
MOT_CLE_AUTO = 2          # StyleValueKeyword.Auto
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Large (vu en jeu), 1 Medium, 2 Small (supposé)
OP_SUPERIEUR = 4          # opérateur de comparaison FM « > »
MODELE = "FinanceOverviewGraphsBlock"
PREFIXE = "UIPickerFinances"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"       # ligne gauche | droite : repère « déjà appliqué »
CLASSE = f"uipicker-finances-tuile-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "finances_tuile_unique.actif")
TUILES = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
ENSEMBLE = "ClubFinancesCardGridCompositionSet"
TUILE = "FinancesOverviewGraphs"
BUDGETS_SOURCE = "RecruitmentBudgetsTile_4x4"
# v18 : classes de l'aspect « tuile » du cadre de ces blocs (retirées de nos copies)
TUILE_CLASSES = ("border-tile-radius-12px", "padding-global-padding-large", "border-color-layout-modules-block-border-colour")
SOLDE_GUID = ("FinancesProjectionsBalanceBlock_4x4", "db657dc1d5d29e74e8864f4d1ad834f5")
CA_GUID = ("FinancesProjectionsTurnoverBlock_4x4", "ee1c3cd8e964d484289073a7c60646fe")
DETTES_SOURCE, DETTES = "FinancesDebtsAndLoansTile_4x2", "DebtDataFrame"
BOUTON_SOURCE, BOUTON = "InterfaceColoursPreferencesCard", "CancelButton"
LIENS = ["ClausesTile_4x2", "FinancesSponsorshipsTile_4x2"]   # tuiles FM : clic du titre + titre
OV_EVENTS, OV_TITRE = 130628061, -1311125049    # surcharges du cadre de tuile FM : clic du titre / texte du titre
# v11 (demande du joueur) : un clic sur chaque en-tête ouvre la page de sa section (clic du titre de la tuile FM)
ENTETES = {"solde_general": "ClubFinancesSummaryTile_4x2", "projections": "FinancesProjectionsTile_4x4",
           "revenus": "FinancesIncomeTile_4x4", "depenses": "FinancesExpenditureTile_4x4",
           "budgets": "RecruitmentBudgetsTile_4x4", "transfert": "TransferBudgetTile_4x4",
           "salaire": "WageBudgetTile_4x4", "recrutement": "ScoutingBudget_Tile_4x4"}
TITRE_BLOC = 40           # px : hauteur de la zone cliquable posée sur le titre des blocs Solde / Chiffre d'affaires
sm.PROPRIETES.setdefault("width", (131105, 3))
sm.PROPRIETES.setdefault("height", (131087, 3))
for _k, _v in {"position": (131102, 7), "top": (131104, 3), "left": (131089, 3), "right": (131103, 3),
               "bottom": (131080, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
SANS_MARGE = {"padding-top": 0, "padding-bottom": 0, "padding-left": 0, "padding-right": 0, "margin-left": 0,
              "margin-right": 0, "margin-top": 0, "margin-bottom": 0}
sm.PROPRIETES.setdefault("flex-direction", (131083, 7))
sm.PROPRIETES.setdefault("margin-top", (131093, 3))
sm.PROPRIETES.setdefault("margin-bottom", (131090, 3))
sm.PROPRIETES.setdefault("margin-left", (131091, 3))
for _k, _v in {"margin-right": (131092, 3), "padding-bottom": (131098, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "padding-top": (131101, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
POURCENT = lambda v: {"unit": 2, "value": float(v)}  # noqa: E731
GRANDIR = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "min-width": 0}
FIXE = {"flex-grow": 0, "flex-shrink": 0}


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def nomme(t, n, root=None):
    return first(t, lambda r: t.name(r) == n, root)


def surcharge(t, element_id):
    """données d'une surcharge (m_SerializedDataOverride) posée sur un modèle inclus, ou None"""
    for r in t.walk():
        for ov in t.elem(r).get("m_SerializedDataOverride") or []:
            if ov.get("m_ElementId") == element_id:
                return t.refs[ov["m_SerializedData"]["rid"]]["data"]
    return None


def source(model):
    bundle, _, stt = nb.find_vta(model)
    return (Tree(stt), Styles(bundle, stt)) if stt is not None else (None, None)


class Tuile:
    def __init__(self, t):
        self.t = t
        self.cadre = nomme(t, "frames-transfer-budget-graphs")
        self.bas = nomme(t, "MessagesVisibleCheck")
        self.transfert = nomme(t, "TransferAction")
        self.recrutement = nomme(t, "ScoutingAction")
        self.texte = nomme(t, "ProjectionsText")
        self.vide = nomme(t, "ExpendituresTextFrame")   # VisualElement de FM : modèle des conteneurs ajoutés
        self.trait = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-horizontal")
        self.trait_vertical = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical")

    def manque(self):
        return [n for n in ("cadre", "bas", "transfert", "recrutement", "texte", "vide", "trait", "trait_vertical")
                if getattr(self, n) is None]

    def boite(self, parent, name="", model=None, index=None):
        t = self.t
        r = t.clone_shallow(model or self.vide, parent, index)
        t.elem(r)["m_Classes"] = []
        t.elem(r)["m_RuleIndex"] = -1
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = name, 1 if name else 0
        return r

    def copie(self, parent, s, ss, root):
        """sous-arbre root du modèle s recopié ici (styles intégrés et modèles inclus compris)"""
        t = self.t
        r = t.clone(root, parent, src=s)
        t.styles.copy_from(ss, t, r)
        used = {s.elem(x).get("m_TemplateAlias") for x in s.walk(root)} - {None, ""}
        for u in s.tt.get("m_Usings") or []:
            if u.get("alias") in used and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
                t.tt["m_Usings"].append(dict(u))
        return r

    def modele(self, parent, alias, guid):
        """instance d'un modèle FM (copie d'un trait de FM avec un autre alias)"""
        t = self.t
        r = t.clone_shallow(self.trait, parent)
        t.elem(r)["m_TemplateAlias"] = alias
        t.elem(r)["m_Classes"] = []
        t.elem(r)["m_RuleIndex"] = -1
        t.sd(r)["templateId"] = alias
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        if not any(u.get("alias") == alias for u in t.tt.setdefault("m_Usings", [])):
            t.tt["m_Usings"].append({"alias": alias, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return r

    def titre(self, parent, binding):
        """texte comme « Projections » de FM, avec la liaison (traduction FM) du titre d'une tuile"""
        t = self.t
        r = t.clone(self.texte, parent)
        t.sd(r)["TextBinding"] = copy.deepcopy(binding)
        t.sd(r)["name"] = ""
        t.elem(r)["m_Classes"] = [c for c in t.elem(r).get("m_Classes") or [] if not c.startswith("margin-right")] \
            + ["margin-bottom-global-gap-regular"]
        return r

    def sous(self, rid, parent):
        """bouton (ou son SIVisible) déplacé à la fin de parent, aligné à droite"""
        t = self.t
        old = t.parent[rid]
        t.elem(old)["m_Children"] = [k for k in t.elem(old)["m_Children"] if k["rid"] != rid]
        t.elem(parent)["m_Children"].append({"rid": rid})
        t.elem(rid)["m_Parent"] = {"rid": parent}
        t.parent[rid] = parent
        t.elem(rid)["m_Classes"] = [c for c in t.elem(rid).get("m_Classes") or [] if not c.startswith("align-self")] \
            + ["align-self-end", "margin-top-8"]

    def bouton_vide(self, parent, clic, nom, index=None):
        """bouton FM sans aspect ni enfant (copie de #CancelButton) qui fait le clic d'un titre de tuile FM"""
        t, st = self.t, self.t.styles
        b = self.copie(parent, *self.modele_bouton)
        for k in list(t.children(b)):
            t.remove(k)
        if index is not None:
            t.elem(parent)["m_Children"] = [k for k in t.elem(parent)["m_Children"] if k["rid"] != b]
            t.elem(parent)["m_Children"].insert(index, {"rid": b})
        sd = t.sd(b)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}{nom}", 1
        sd["Events"] = copy.deepcopy(clic["Events"])
        sd["Events_UxmlAttributeFlags"] = 1   # sans ce drapeau FM ignore l'événement
        t.elem(b)["m_Classes"] = []
        t.elem(b)["m_RuleIndex"] = -1
        st.style(t, b, {**sm.SANS_CADRE, **FIXE, **SANS_MARGE})
        return b

    def lien_autour(self, rid, clic, nom):
        """v11 : l'élément rid (en-tête) rendu cliquable. v12 : rid dans un conteneur simple à sa place, bouton sans
        aspect posé dessus (position absolue, toute la surface) : un bouton FM se mesure sur son propre texte (vide)
        et pas sur ses enfants -> en v11 seules les 4 premières lettres des textes seuls étaient cliquables"""
        t = self.t
        parent = t.parent[rid]
        cont = self.boite(parent, f"{PREFIXE}{nom}Zone", index=t.children(parent).index(rid))
        t.styles.style(t, cont, FIXE)
        t.elem(parent)["m_Children"] = [k for k in t.elem(parent)["m_Children"] if k["rid"] != rid]
        t.elem(cont)["m_Children"].append({"rid": rid})
        t.elem(rid)["m_Parent"] = {"rid": cont}
        t.parent[rid] = cont
        b = self.bouton_vide(cont, clic, nom)
        t.styles.style(t, b, {**sm.SANS_CADRE, **FIXE, **SANS_MARGE, "position": "absolute", "top": 0, "left": 0,
                              "right": 0, "bottom": 0})
        return b

    def lien_titre_bloc(self, bloc, clic, nom):
        """v11 : zone cliquable posée sur le titre d'un bloc FM inclus (on ne peut pas toucher à son intérieur)"""
        z = self.bouton_vide(bloc, clic, nom)
        self.t.styles.style(self.t, z, {**sm.SANS_CADRE, **FIXE, **SANS_MARGE, "position": "absolute", "top": 0,
                                        "left": 0, "right": 0, "height": TITRE_BLOC})
        return z

    def dettes(self, parent, sbt, sbts, bouton, sd_, sds, dettes, clic_dettes):
        """Dette restante | Dette initiale (#DebtDataFrame de FM) : v5, chaque dette en une ligne (montant puis
        libellé) pour tenir dans la ligne du titre sans la grandir ; v3 : un clic ouvre la page Dettes (clic du titre
        de la tuile FM des dettes), bouton FM sans aspect (comme le nom du stade de club_page_bas)"""
        t, st = self.t, self.t.styles
        lien = self.copie(parent, sbt, sbts, bouton)
        for k in list(t.children(lien)):
            t.remove(k)
        sd = t.sd(lien)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}LienDettes", 1
        sd["Events"] = copy.deepcopy(clic_dettes["Events"])
        sd["Events_UxmlAttributeFlags"] = 1
        t.elem(lien)["m_Classes"] = []
        t.elem(lien)["m_RuleIndex"] = -1
        st.style(t, lien, {**sm.SANS_CADRE, "flex-grow": 0, "flex-shrink": 1, "min-width": 0, "overflow": "hidden",
                           "padding-top": 0, "padding-bottom": 0, "padding-left": 0, "padding-right": 0,
                           "margin-left": 0, "margin-right": 0, "margin-top": 0, "margin-bottom": 0})
        d = self.copie(lien, sd_, sds, dettes)
        t.elem(d)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        st.style(t, d, {"flex-shrink": 1, "min-width": 0})
        cadres = t.children(d)
        for i, c in enumerate(cadres):
            # règle FM : colonne, largeur 140 px, marge du bas 8 px -> ligne, largeur auto, sans marge du bas
            regle = st.values(t.elem(c)["m_RuleIndex"]) if t.elem(c).get("m_RuleIndex", -1) >= 0 else []
            enleve = {131083, 131074, 131090, 131105}   # flex-direction, align-items, margin-bottom, width
            t.elem(c)["m_RuleIndex"] = st.add_rule([p for p in regle if p[0] not in enleve] + [
                (131083, "", [(7, "row")]), (131074, "", [(7, "center")]), (131090, "", [(3, 0)]),
                (131105, "", [(1, MOT_CLE_AUTO)])])
            t.elem(c)["m_Classes"] = ["margin-right-global-gap-large"] if i < len(cadres) - 1 else []
            textes = [k for k in t.children(c) if typ(t, k) == "SIText"]
            for j, k in enumerate(textes):
                t.elem(k)["m_Classes"] = (["body-md-strong", "global-text-primary"] if j == 0 else
                                          ["body-sm", "global-text-secondary", "margin-left-global-gap-regular"]) \
                    + ["sitext-hover-cursor"]
        return lien

    def construire(self):
        t, st = self.t, self.t.styles
        sb, sbs = source(BUDGETS_SOURCE)
        sd_, sds = source(DETTES_SOURCE)
        sbt, sbts = source(BOUTON_SOURCE)
        liens = [source(m)[0] for m in LIENS]
        budgets = sb and nomme(sb, "Frame")
        dettes = sd_ and nomme(sd_, DETTES)
        bouton = sbt and nomme(sbt, BOUTON)
        titre_budgets = sb and surcharge(sb, OV_TITRE)
        clics = [s and surcharge(s, OV_EVENTS) for s in liens]
        clic_dettes = sd_ and surcharge(sd_, OV_EVENTS)   # page Dettes et emprunts
        noms_liens = [s and surcharge(s, OV_TITRE) for s in liens]
        if None in (budgets, dettes, bouton, titre_budgets, clic_dettes, *clics, *noms_liens):
            return "morceaux FM introuvables (budgets / dettes / bouton / tuiles Clauses, Sponsors)"
        recrutement_vis = t.parent[self.recrutement]
        if typ(t, recrutement_vis) != "SIVisible":
            return "bouton du budget de recrutement : forme inattendue (introuvable)"
        self.modele_bouton = (sbt, sbts, bouton)
        clic = {k: (lambda s: s and surcharge(s, OV_EVENTS))(source(m)[0]) for k, m in ENTETES.items()}
        if None in clic.values():
            return "clic des tuiles FM introuvable (" + ", ".join(ENTETES[k] for k, v in clic.items() if v is None) + ")"

        # cadre en ligne : gauche = contenu de FM (tailles de FM intactes), trait vertical, droite = colonne ajoutée.
        # v9 : retour à cette forme (v6-v8 coupaient en 2 rangées pour caler les traits : Solde général devait être
        # au moins aussi haut que les budgets -> proportions faussées, débordement en Large ; calage abandonné)
        anciens = t.children(self.cadre)
        ligne = self.boite(self.cadre, NOM_RACINE)
        t.elem(ligne)["m_Classes"] = [CLASSE, "row-direction-normal"]
        st.style(t, ligne, {"width": POURCENT(100), **GRANDIR})
        gauche = self.boite(ligne, f"{PREFIXE}Gauche")
        st.style(t, gauche, GRANDIR)
        t.elem(self.cadre)["m_Children"] = [{"rid": ligne}]
        for k in anciens:
            t.elem(gauche)["m_Children"].append({"rid": k})
            t.elem(k)["m_Parent"] = {"rid": gauche}
            t.parent[k] = gauche
        tv = t.clone(self.trait_vertical, ligne)
        t.elem(tv)["m_Classes"] = ["margin-horizontal-global-gap-large"]
        # droite : copie vide du SIVisible des boutons du bas (cachée dans les messages, isMessage)
        droite = self.boite(ligne, f"{PREFIXE}Droite", model=self.bas)
        st.style(t, droite, {"width": POURCENT(LARGEUR_DROITE), "flex-direction": "column", **FIXE,
                             "min-height": 0, "overflow": "hidden"})

        # v6 : dettes en haut à droite de Solde général (ligne = cadre du titre FM | vide | dettes)
        titre_solde = anciens[0]
        ligne_solde = self.boite(gauche, f"{PREFIXE}LigneSolde", index=0)
        t.elem(ligne_solde)["m_Classes"] = ["row-direction-normal", "align-items-start"]
        st.style(t, ligne_solde, {"width": POURCENT(100), **FIXE})
        t.elem(gauche)["m_Children"] = [k for k in t.elem(gauche)["m_Children"] if k["rid"] != titre_solde]
        t.elem(ligne_solde)["m_Children"].append({"rid": titre_solde})
        t.elem(titre_solde)["m_Parent"] = {"rid": ligne_solde}
        t.parent[titre_solde] = ligne_solde
        vide = self.boite(ligne_solde)
        st.style(t, vide, GRANDIR)
        self.dettes(ligne_solde, sbt, sbts, bouton, sd_, sds, dettes, clic_dettes)
        # v11 : en-têtes de gauche cliquables
        for n, k in (("OveralBalanceText", "solde_general"), ("ProjectionsText", "projections"),
                     ("IncomeText", "revenus"), ("ExpenditureText", "depenses")):
            r = nomme(t, n)
            if r is None:
                return f"en-tête {n} introuvable"
            self.lien_autour(r, clic[k], f"Entete{n}")

        # 1. budgets (sections de la tuile FM) + boutons « Modifier » de FM ; v11 : titres cliquables
        tb = self.titre(droite, titre_budgets["TextBinding"])
        self.lien_autour(tb, clic["budgets"], "EnteteBudgets")
        b = self.copie(droite, sb, sbs, budgets)
        st.style(t, b, FIXE)
        transfert, salaire, recrut = (nomme(t, n, b) for n in ("TransferBudget-Frame", "Wage-Frame", "ScoutingFrame"))
        if None in (transfert, salaire, recrut):
            return "sections des budgets introuvables"
        for section, k in ((transfert, "transfert"), (salaire, "salaire"), (recrut, "recrutement")):
            r = nomme(t, "SectionTitleFrame", section)
            if r is None:
                return "titre d'une section des budgets introuvable"
            self.lien_autour(r, clic[k], f"Entete{k.capitalize()}")
        self.sous(self.transfert, transfert)
        copie_transfert = t.clone(self.transfert, salaire)
        self.sous(copie_transfert, salaire)
        self.sous(recrutement_vis, recrut)

        # 2-3. Solde et Chiffre d'affaires (blocs de projection de FM, inclus tels quels), se partagent la hauteur ;
        # v2 : Chiffre d'affaires caché en mode Large (comparaison FM « mode > 0 », comme club_page_bas)
        s_vis, vis = ni.visible_model()
        if vis is None:
            return "modèle de comparaison FM introuvable"
        # v10 (demande du joueur) : en Small seulement, un espace fixe avant le trait sous les budgets pour qu'il
        # tombe à la hauteur du trait sous Solde général (comparaison FM « mode > 1 »). Vu en jeu : rien avec
        # « > 1 » (v10-v12) ni « == 1 » (v13) -> c'est le SIVisible vide qui ne prend pas de hauteur ; v14 : la
        # hauteur est portée par un enfant (comme le bloc Chiffre d'affaires, qui a du contenu et marche)
        if ECART_SMALL:
            esp = ni.new_visible(t, s_vis, vis, droite, None, f"{PREFIXE}EcartSmall",
                                 ni.make_binding(s_vis.sd(vis)["Binding"], OP_SUPERIEUR, [MODE_AFFICHAGE], 1))
            t.sd(esp)["name_UxmlAttributeFlags"] = 1
            t.elem(esp)["m_RuleIndex"] = -1
            st.style(t, esp, FIXE)
            cale = self.boite(esp, f"{PREFIXE}EcartSmallCale")
            st.style(t, cale, {"height": ECART_SMALL, "min-height": ECART_SMALL, **FIXE})
        trait = t.clone(self.trait, droite)   # trait sous les budgets (comme en v5)
        t.elem(trait)["m_Classes"] = list(t.elem(trait).get("m_Classes") or []) + ["margin-vertical-global-gap-regular"]
        for alias, guid in (SOLDE_GUID, CA_GUID):
            if not (alias == CA_GUID[0] and CA_HORS_LARGE):
                bloc = self.boite(droite)   # v11 : conteneur du bloc + zone cliquable sur son titre
                st.style(t, bloc, {"flex-direction": "column", **GRANDIR, "overflow": "hidden"})
            else:
                bloc = ni.new_visible(t, s_vis, vis, droite, None, f"{PREFIXE}ChiffreAffairesHorsLarge",
                                      ni.make_binding(s_vis.sd(vis)["Binding"], OP_SUPERIEUR, [MODE_AFFICHAGE], 0))
                t.sd(bloc)["name_UxmlAttributeFlags"] = 1
                t.elem(bloc)["m_RuleIndex"] = -1
                st.style(t, bloc, {"flex-direction": "column", **GRANDIR, "overflow": "hidden"})
                # v18 (demande du joueur) : trait de FM entre Solde et Chiffre d'affaires (v6 l'avait retiré), comme
                # celui sous les budgets
                tr = t.clone(self.trait, bloc)
                t.elem(tr)["m_Classes"] = list(t.elem(tr).get("m_Classes") or []) + ["margin-vertical-global-gap-regular"]
                # v19 : vu en jeu (Small) 1 px sous le trait de gauche : remonté (top, la mise en page ne bouge pas)
                if DECALER_TRAIT_CA:
                    st.style(t, tr, {"top": DECALER_TRAIT_CA})
            # v18 : bloc de FM RECOPIÉ (plus inclus) pour lui retirer son aspect de tuile (bord, coins, marge
            # intérieure) ; ses modèles servent aussi aux tuiles de Finances > Projections, qu'on ne touche pas.
            # Les points des courbes : graphes_finances (relancé après, SUIVANTS) les pose aussi sur ces copies.
            s_bloc, ss_bloc = source(alias)
            if s_bloc is None:
                return f"{alias} introuvable"
            m = self.copie(bloc, s_bloc, ss_bloc, s_bloc.children(s_bloc.tt["m_VisualTree"]["rid"])[0])
            cadres = [r for r in t.walk(m) if TUILE_CLASSES[0] in (t.elem(r).get("m_Classes") or [])]
            if len(cadres) != 1:
                return f"{alias} : cadre de tuile introuvable"
            t.elem(cadres[0])["m_Classes"] = [c for c in t.elem(cadres[0])["m_Classes"] if c not in TUILE_CLASSES]
            st.style(t, m, {**GRANDIR, "overflow": "hidden"})
            self.lien_titre_bloc(bloc, clic["projections"], f"Entete{alias.split('_')[0]}")

        # 4. Clauses / Sponsors : bouton FM, clic et titre des tuiles FM
        rang = self.boite(droite)
        t.elem(rang)["m_Classes"] = ["row-direction-normal", "margin-top-8"]
        st.style(t, rang, FIXE)
        for i, (clic, nom) in enumerate(zip(clics, noms_liens)):
            r = self.copie(rang, sbt, sbts, bouton)
            sd = t.sd(r)
            sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}Lien{i}", 1
            sd["Events"] = copy.deepcopy(clic["Events"])
            sd["Events_UxmlAttributeFlags"] = 1   # sans ce drapeau FM ignore l'événement
            t.elem(r)["m_Classes"] = [c for c in t.elem(r)["m_Classes"] if not c.startswith("margin-")] \
                + ([] if i == 0 else ["margin-left-global-gap-regular"])
            st.style(t, r, GRANDIR)
            for k in t.walk(r):
                if typ(t, k) == "SIText":
                    t.sd(k)["TextBinding"] = copy.deepcopy(nom["TextBinding"])
        return None


# ---------- modèle ----------
def original(bundle, obj, path_id=None):
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    pid = obj.path_id if path_id is None else path_id
    o = next((o for o in UnityPy.load(backup.backup_path(bundle)).objects if o.path_id == pid), None)
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
    if sheet is not None:   # feuille d'origine aussi : les règles des versions précédentes ne s'empilent pas
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, tt, t


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def modele_appliquer():
    bundle, obj, tt, t = ouvrir()
    if tt is None:
        return f"{MODELE} : introuvable (renommé par une mise à jour ?), ignoré"
    old = marques(t)
    if any(t.name(r) == NOM_RACINE for r in old):
        return f"{MODELE} : déjà appliqué"
    bundle, obj, tt, t = ouvrir(depart_original=True)
    if marques(t):
        return f"{MODELE} : pas de sauvegarde d'origine propre, ignoré"
    p = Tuile(t)
    if p.manque():
        return f"{MODELE} : repères FM introuvables ({', '.join(p.manque())}), ignoré"
    err = p.construire()
    if err:
        return f"{MODELE} : {err}, ignoré"
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    return (f"{MODELE} : colonne de droite ({LARGEUR_DROITE} %) budgets modifiables, solde, chiffre d'affaires, "
            "dettes, clauses / sponsors" + (" ; ancienne version remplacée" if old else ""))


def modele_retirer():
    bundle, obj, tt, t = ouvrir()
    if not t or not marques(t):
        return None
    orig = original(bundle, obj)
    if orig is None:
        return f"{MODELE} : pas de sauvegarde d'origine, rien fait"
    obj.save_typetree(orig)
    sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    return f"{MODELE} : remis d'origine"


# ---------- grille (ui-tileslayouts) ----------
def compositions(env):
    """[(objet, typetree)] des compositions de l'ensemble Finances (même fichier)"""
    objs = {o.path_id: o for o in env.objects}
    ens = None
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                if o.peek_name() == ENSEMBLE:
                    ens = o.read_typetree()
                    break
            except Exception:
                continue
    if ens is None:
        return []
    out = []
    for entry in ens["m_gridBreakpointCompositionData"]["m_values"]:
        for ref in entry["m_value"]:
            if ref["m_FileID"] == 0 and ref["m_PathID"] in objs:
                o = objs[ref["m_PathID"]]
                out.append((o, o.read_typetree()))
    return out


def voulu(orig, modele_tuile):
    """(composants, coins optionnels) : la tuile des graphiques seule, sur toute la place de la composition"""
    comps = orig["m_gridComponents"]
    w = max(c["m_location"]["x"] + c["m_location"]["width"] for c in comps)
    h = max(c["m_location"]["y"] + c["m_location"]["height"] for c in comps)
    c = copy.deepcopy(next((c for c in comps if c["m_elementID"] == TUILE), modele_tuile))
    c["m_location"].update(x=0, y=0, width=w, height=h)
    c["m_minSize"]["x"], c["m_minSize"]["y"] = min(c["m_minSize"]["x"], w), min(c["m_minSize"]["y"], h)
    c["m_maxSize"]["x"], c["m_maxSize"]["y"] = 100, 100
    c["m_isOptional"] = 0
    coins = copy.deepcopy(orig["m_optionalSlices"])
    for k, v in coins.items():
        if isinstance(v, list) and k != "m_instantiationOrder":
            coins[k] = []
    return [c], coins


def grille(retirer):
    env = UnityPy.load(TUILES)
    src = backup.backup_path(TUILES)
    origine = {o.path_id: tt for o, tt in compositions(UnityPy.load(src if os.path.exists(src) else TUILES))}
    actuelles = compositions(env)
    if not actuelles:
        return [f"{ENSEMBLE} : introuvable (renommé par une mise à jour ?), ignoré"]
    modele_tuile = next((c for tt in origine.values() for c in tt["m_gridComponents"] if c["m_elementID"] == TUILE),
                        None)
    if modele_tuile is None:
        return [f"{ENSEMBLE} : tuile {TUILE} introuvable, ignoré"]
    msgs, change = [], False
    for o, tt in actuelles:
        orig = origine.get(o.path_id)
        if orig is None:
            msgs.append(f"{tt['m_Name']} : pas d'origine, ignorée")
            continue
        comps, coins = ((orig["m_gridComponents"], orig["m_optionalSlices"]) if retirer
                        else voulu(orig, modele_tuile))
        if (tt["m_gridComponents"], tt["m_optionalSlices"]) == (comps, coins):
            continue
        tt["m_gridComponents"], tt["m_optionalSlices"] = copy.deepcopy(comps), copy.deepcopy(coins)
        o.save_typetree(tt)
        change = True
        l = comps[0]["m_location"]
        msgs.append(f"{tt['m_Name']} : " + ("d'origine" if retirer else f"{TUILE} seule {l['width']}x{l['height']}"))
    if change:
        data = env.file.save(packer="original")
        if nb.DRY_RUN:
            msgs.append(f"(essai à blanc : rien écrit, {os.path.basename(TUILES)} ferait {len(data) / 1e6:.2f} Mo)")
        else:
            backup.write_bundle(TUILES, data)
    else:
        msgs.append(f"{ENSEMBLE} : " + ("déjà d'origine" if retirer else "déjà appliqué"))
    return msgs


# ---------- commandes ----------
def cmd_appliquer():
    print(modele_appliquer())
    nb.save_all()
    for m in grille(retirer=False):
        print(m)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
    print("Si la page garde l'ancienne disposition : la réinitialiser en jeu (tuiles perso de FM). / "
          "If the page keeps the old layout: reset it in game (FM custom tiles).")


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    m = modele_retirer()
    print(m or f"{MODELE} : rien à retirer")
    if m:
        nb.save_all()
    for m in grille(retirer=True):
        print(m)


def cmd_etat():
    _, _, tt, t = ouvrir()
    old = [t.name(r) for r in marques(t)] if t else []
    print(f"{MODELE} : " + (f"appliqué ({', '.join(old[:3])} ; version actuelle v{VERSION})" if old else "d'origine"))
    for o, ct in compositions(UnityPy.load(TUILES)):
        print(f"  {ct['m_Name']} : " + ", ".join(c["m_elementID"] for c in ct["m_gridComponents"]))
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
            print("finances en une tuile : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
