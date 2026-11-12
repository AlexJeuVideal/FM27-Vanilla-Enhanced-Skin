"""[AJOUT KINITO] Effectif : dans la Vue d'ensemble, les boutons d'Alex en icônes et des liens vers les autres équipes
du club ; sur l'écran Effectif de chaque équipe, les boutons des équipes à côté de « Avec le ballon / Sans le ballon » ;
et les boutons d'Alex en icônes partout où il les pose (écran Effectif, Tactiques).

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demandes de Kinito (2026-11-12) :
- Effectif > Vue d'ensemble : les trois boutons qu'Alex met sur l'écran Équipe première (« au même endroit » : juste
  après le menu « Infos effectif ») ; v3 : en ICÔNES (celles du panneau Favoris de FM), leur nom au survol — en taille
  de texte maximale, les trois boutons écrits mangeaient le « Dans X jours » du prochain match ;
- v4 : « les mêmes icônes partout où sont utilisés ces boutons » : les boutons d'Alex de l'écran Effectif de chaque
  équipe (Entraînement, Entraîn. individuel, Programme des rencontres : effectif_boutons_entrainement) et de l'écran
  Tactiques (Effectif, Programme des rencontres : tactiques_boutons ; « les deux en icônes ») ;
- les équipes du club : un clic ouvre l'écran Effectif de l'équipe (« le bouton Équipe 2 envoie ici »), sur la Vue
  d'ensemble et sur l'écran Effectif de chaque équipe (« pour toutes mes équipes ») :
  - écran Effectif : la rangée de boutons d'Alex (Rodez AF | Équipe 2 | U19), juste à droite de « Avec le ballon /
    Sans le ballon » (validée en jeu, v2) ;
  - Vue d'ensemble (v3) : des LIENS comme « Équipe première » (lien souligné en haut à gauche du bloc), à sa suite
    (« Équipe première  Équipe 2  U19 »). v2 y mettait la rangée de boutons : en taille de texte maximale, elle
    faisait passer les postes (GB… R9) sur deux lignes — l'écran est plus étroit (colonne de droite).
  v1 posait les flèches ^ v de FM (QuickFlick) : elles vont à l'équipe « suivante » de FM (Reims…), retirées en v2.
- « qu'on puisse switch les boutons entre texte et icône » (choix de Kinito : dans Outils FM) : le réglage est la
  fonction 26.11 (kinito_effectif_texte) — activée, les boutons modifiés restent ÉCRITS (ceux d'Alex intacts, ceux de
  la Vue d'ensemble écrits comme les siens) ; retirée, ils sont en icônes. Lu par icones() (son marqueur, ou la
  variable KINITO_BOUTONS qu'elle passe en relançant cet ajout).

Comment (outils d'Alex, SANS les modifier ; morceaux de FM recopiés) :
- UN BOUTON EN ICÔNE (iconifier) : le bouton perd son texte (sa fonction de texte vidée, ou son SIText enfant vidé pour
  ceux des Tactiques) et reçoit l'icône de FM (élément icône du bouton Tactiques de TeamSquadBlock, classe changée) et
  l'infobulle de FM (Tooltip > SIText de RoleLabelwIcon, comme 26.3 / 26.4), dont le texte est la traduction FM du
  bouton (n° des réglages d'Alex), avec la fonction de texte traduit du lien « Équipe première ». Icônes : celles du
  panneau Favoris de FM (Entraînement = cône, Programme des rencontres = calendrier, Équipe première = joueur pour
  « Effectif ») et celle de l'entraînement individuel de FM.
- Vue d'ensemble, BOUTONS : ee.construire_effectif (avec les réglages de son effectif_boutons_entrainement), renommés,
  puis iconifiés.
- Boutons d'ALEX (écran Effectif, Tactiques) : iconifiés SUR PLACE, ses noms gardés (ses scripts les voient « à
  jour »). Nos éléments (icône, infobulle) sont nommés UIPickerKinito… ; « retirer » les enlève et rend aux boutons
  leurs données exactes, recalculées par SES fonctions (ee.construire_effectif / tactiques_boutons.construire) sur
  l'original, en mémoire. Quand son script réécrit un modèle, ses boutons reviennent écrits : le choix 1 relance cet
  ajout après lui. Sa fonction désactivée : rien à iconifier, rien n'est ajouté.
- Vue d'ensemble, LIENS : une rangée remplace le lien « Équipe première » à sa place (le lien y est déplacé, ses
  classes passent à la rangée), puis la liste d'Alex (ee.rangee, liste FM non virtualisée sur human.Club.Teams), dans
  un SIVisible « équipe du club du joueur ». Chaque lien est une cellule de FM que RIEN ne cite (CompNationCell,
  vérifiée sur les données décompressées le 2026-11-12 ; sa racine perd le fond noir et la hauteur de FM), réécrite :
  le modèle inclus « title-link » de FM (celui d'« Équipe première »), texte = row.TeamTypeStringTypeOnly (le texte des
  boutons d'équipe : « Équipe 2 », « U19 »), clic = écran Effectif de l'équipe ; caché pour l'équipe affichée
  (row.UniqueId ≠ équipe affichée : opérateur NotEqual = 5 de ComparisonOperator, lu dans le code du jeu, utilisé 43
  fois par FM avec cette fonction).
- RANGÉE (écran Effectif) : ee.rangee (liste FM horizontale, boutons segmentés, équipe affichée surlignée), qui prend
  la place libre de la ligne (flex-grow 1000 ; le groupe FM « Avec / Sans le ballon » a flex-grow-class = 1) ; son
  bouton est une cellule de FM que RIEN ne cite (ClubBigIconAndTextAndLeagueCell), réécrite par ee.construire_bouton.
- Clic des liens et des boutons d'équipe : TeamSquadReport, team = l'équipe (l'événement des tuiles FM Équipe
  première / Équipes de jeunes). La Vue d'ensemble (panneau SquadScreen) n'a aucun paramètre : elle ne s'ouvre que
  pour l'équipe première.

Touché :
- SquadOverviewTableBlock (Vue d'ensemble) : seul propriétaire, repart de l'original, retirer le remet. Ce bloc sert
  aussi à la Vue d'ensemble d'un sélectionneur : les ajouts y sont sous la condition « équipe du club du joueur ».
- TeamSquadBlock (écran Effectif ; propriétaire effectif_boutons_entrainement d'Alex) et TacticalPlannerHeader (écran
  Tactiques ; propriétaire tactiques_boutons d'Alex) : modèles PARTAGÉS. On part du modèle tel qu'il est ; nos
  éléments (rangée, icônes, infobulles) sont retirés par leur nom, avec les règles de style qu'ils étaient seuls à
  utiliser (et les valeurs devenues inutiles en fin de table) ; les données des boutons d'Alex sont rendues.
- ClubBigIconAndTextAndLeagueCell (bouton d'équipe) et CompNationCell (lien d'équipe) : cellules FM inutilisées,
  réécrites ; seul propriétaire de chacune.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_effectif_vue.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_effectif_vue.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_effectif_vue.py etat
"""
import bisect
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
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, make_binding, new_visible, decode_args, encode_args, _enc_varint  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import no_styles  # noqa: E402
import elements as el  # noqa: E402
import entrainement_equipes as ee  # noqa: E402  (outil d'AlexJeuVideal : boutons et rangée, non modifiés)
import effectif_boutons_entrainement as eb  # noqa: E402  (ses réglages des boutons de l'Effectif, lus seulement)
import tactiques_boutons as tb  # noqa: E402  (ses boutons des Tactiques : réglages et construction, lus seulement)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter la version de la pièce concernée)
# =====================================================================================================
BOUTONS = True       # Vue d'ensemble : les trois boutons d'Alex (en icônes ou écrits, voir icones())
ICONES_ALEX = True   # les boutons d'Alex en icônes là où il les pose (écran Effectif, Tactiques), si icones()
ICONES = {           # icône de chaque bouton, par la fin de son nom (icônes de FM, panneau Favoris surtout)
    "bouton": "game-concepts-training-general_small",        # Entraînement (Favoris : Entraînement, cône)
    "individuel": "game-concepts-individual-training_small",  # Entraînement individuel
    "programme": "ui-concepts-calendar_small",                # Programme des rencontres (Favoris : calendrier)
    "effectif": "game-concepts-player_small",                 # Tactiques : Effectif (Favoris : Équipe première)
}
LIENS = True         # Vue d'ensemble : liens des autres équipes du club à la suite d'« Équipe première »
ECART_LIENS = 16     # px avant chaque lien
#  écran Effectif : rangée des équipes juste après « Avec le ballon / Sans le ballon » (liste FM, hauteur, écart)
EQUIPES = {"actif": True, "liste": "human.Club.Teams", "hauteur": 32, "marge": 8}
POUSSER = 1000       # flex-grow de la rangée (le groupe FM « Avec / Sans le ballon » a 1)
DECALER_EQUIPES = -1   # px, + = plus bas : rangée de l'écran Effectif calée sur « Avec / Sans le ballon » (v3, UI PICKER,
                       # 2026-11-12 : 1 px trop bas en jeu, relevé par Alex ; propriété top, la ligne ne bouge pas)
# =====================================================================================================

VERSION = 4   # Vue d'ensemble. v1 : boutons + flèches ^ v de FM ; v2 : flèches retirées, rangée de boutons d'équipes ;
              # v3 : boutons en icônes, liens d'équipes à la suite d'« Équipe première » au lieu de la rangée ;
              # v4 : boutons en icônes OU écrits, selon le réglage 26.11 (nom du SIVisible selon le mode)
VERSION_RANGEE = 3   # écran Effectif (v2 : première version de la rangée, validée en jeu ; v3 : DECALER_EQUIPES)
VERSION_ICONES = 1   # boutons d'Alex en icônes (v4 de l'ajout)
VERSION_CELLULE = 1  # bouton d'équipe
VERSION_LIEN = 1     # lien d'équipe
VUE = "SquadOverviewTableBlock"      # Effectif > Vue d'ensemble (seul propriétaire)
EFFECTIF = "TeamSquadBlock"          # écran Effectif d'une équipe (partagé : propriétaire effectif_boutons_entrainement)
TACTIQUES = "TacticalPlannerHeader"  # écran Tactiques (partagé : propriétaire tactiques_boutons)
PARTAGES = (EFFECTIF, TACTIQUES)
CELLULE = "ClubBigIconAndTextAndLeagueCell"
GUID_CELLULE = "83d5df0914b2d05419b989661d23aa0a"   # ClubBigIconAndTextAndLeagueCell (catalogue Addressables)
LIEN = "CompNationCell"
GUID_LIEN = "60b8f5bf1c1c48440932ca2bb2079aa8"      # CompNationCell (catalogue Addressables)
ECRAN_EFFECTIF = "7957386accba7b44d81ac248d04efbac"  # TeamSquadReport (écran Effectif d'une équipe, paramètre team)
ALIAS_TITRE = "title-link"                          # modèle inclus FM du lien « Équipe première »
SOURCE_BULLE = "RoleLabelwIcon"                     # infobulle FM : Tooltip > SIText (comme 26.3 / 26.4)
NON_EGAL = 5                                        # ComparisonOperator.NotEqual (code du jeu)
TEXTE_EQUIPE = "row.TeamTypeStringTypeOnly"         # texte des boutons d'équipe de FM (« Équipe 2 », « U19 »)
PREFIXE = "UIPickerKinito-effectif-vue"
NOM_BOUTONS = f"{PREFIXE}-v{VERSION}"               # SIVisible des trois boutons (celui d'Alex, renommé) + -icones / -texte
NOM_TITRE = f"{PREFIXE}-titre-v{VERSION}"           # rangée du titre : « Équipe première » + nos liens
NOM_LIENS = f"{PREFIXE}-liens"                      # SIVisible « équipe du club du joueur » des liens
NOM_LIENS_LISTE = f"{PREFIXE}-liens-liste"
NOM_EQUIPES = f"{PREFIXE}-equipes-v{VERSION_RANGEE}"   # écran Effectif : SIVisible « équipe du club du joueur »
NOM_LISTE = f"{PREFIXE}-equipes-liste"
NOM_CELLULE = f"{PREFIXE}-bouton-equipe-v{VERSION_CELLULE}"
NOM_LIEN = f"{PREFIXE}-lien-equipe-v{VERSION_LIEN}"
ALEX = f"{PREFIXE}-alex-v{VERSION_ICONES}"          # nos éléments dans les boutons d'Alex : <ALEX>-icone-<fin>, -bulle-
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_effectif_vue.actif")
# réglage 26.11 (kinito_effectif_texte) : son marqueur présent = boutons ÉCRITS au lieu des icônes. Elle relance cet
# ajout avec KINITO_BOUTONS = texte / icones (le mode voulu, même pour un essai à blanc, avant d'écrire son marqueur)
MARKER_TEXTE = os.path.join(backup.BACKUP_DIR, "kinito_effectif_texte.actif")


def icones():
    """vrai : les boutons modifiés sont en icônes (par défaut) ; faux : écrits (réglage 26.11)"""
    force = os.environ.get("KINITO_BOUTONS")
    if force in ("texte", "icones"):
        return force == "icones"
    return not os.path.exists(MARKER_TEXTE)


def nom_boutons():
    return f"{NOM_BOUTONS}-{'icones' if icones() else 'texte'}"


# le texte de chaque bouton (n° de traduction FM, repère), par la fin de son nom, selon le modèle (réglages d'Alex)
TEXTES = {
    EFFECTIF: {"bouton": (eb.EFFECTIF["texte"], b"UIPicker Training"),
               "individuel": (eb.EFFECTIF_INDIVIDUEL["texte"], b"UIPicker Individual Training"),
               "programme": (eb.EFFECTIF_PROGRAMME["texte"], b"UIPicker Fixture Schedule")},
    TACTIQUES: {nom: (numero, repere) for nom, numero, repere, _, _ in tb.BOUTONS},
}
PREFIXES_ALEX = {EFFECTIF: ee.PREFIXE, TACTIQUES: tb.PREFIXE}


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def racines(t):
    """nos éléments du plus haut niveau (leurs enfants partent avec eux)"""
    def dans_un_des_notres(r):
        p = t.parent.get(r)
        while p is not None:
            if t.name(p).startswith(PREFIXE):
                return True
            p = t.parent.get(p)
        return False
    return [r for r in marques(t) if not dans_un_des_notres(r)]


def a_nous(t, nom):
    return any(t.name(r) == nom for r in marques(t))


def vue_a_jour(t):
    attendus = ({nom_boutons()} if BOUTONS else set()) | ({NOM_TITRE} if LIENS else set())
    # modif d'Alex (2026-10-30) : liens encore sur l'ancienne condition « même club » (cachés sur la U23) -> refaits
    return {t.name(r) for r in racines(t)} == attendus and not ee.ancienne_condition(t)


def boutons_alex(t, modele):
    """{fin du nom : rid} des boutons d'Alex de ce modèle (repérés par ses noms)"""
    pref = PREFIXES_ALEX[modele] + "-"
    out = {}
    for r in t.walk():
        n = t.name(r)
        if typ(t, r) == "SIButton" and n.startswith(pref) and n[len(pref):] in TEXTES[modele]:
            out[n[len(pref):]] = r
    return out


def attendus_partage(t, modele):
    noms = {NOM_EQUIPES} if modele == EFFECTIF and EQUIPES["actif"] else set()
    if ICONES_ALEX and icones():
        for fin in boutons_alex(t, modele):
            noms |= {f"{ALEX}-icone-{fin}", f"{ALEX}-bulle-{fin}"}
    return noms


def partage_a_jour(t, modele):
    return {t.name(r) for r in racines(t)} == attendus_partage(t, modele)


def cellule_a_jour(t, nom, actif):
    return a_nous(t, nom) if actif else not marques(t)


def nommer(t, r, nom):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    """clone() ne refait que m_Parent : l'identifiant du parent aussi, s'il existe (modèles du bundle global)"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def reecrire_regle(t, r, css):
    """la règle de style que vient de poser une fonction (à cet élément seul) est réécrite à sa place : aucune règle
    orpheline"""
    idx = t.elem(r).get("m_RuleIndex", -1)
    if idx < 0 or sum(1 for x in t.walk() if t.elem(x).get("m_RuleIndex", -1) == idx) != 1:
        return False
    t.styles.add_rule([(sm.PROPRIETES[k][0], "", [(sm.PROPRIETES[k][1], v)]) for k, v in css.items()])
    t.styles.sh["m_Rules"][idx] = t.styles.sh["m_Rules"].pop()
    return True


def declarer_modele(t, s, alias):
    """déclare le modèle inclus <alias> (m_Usings de s), à sa place dans l'ordre des noms (comme FM)"""
    u = next((u for u in s.tt.get("m_Usings") or [] if u.get("alias") == alias), None)
    if u is None:
        return False
    usings = t.tt.setdefault("m_Usings", [])
    if not any(x.get("alias") == alias for x in usings):
        cles = [x.get("alias") or "" for x in usings]
        usings.insert(bisect.bisect_left(cles, alias) if cles == sorted(cles) else len(usings), copy.deepcopy(u))
    return True


def surcharges(t, r):
    return [t.refs[ov["m_SerializedData"]["rid"]]["data"] for ov in t.elem(r).get("m_SerializedDataOverride") or []]


def fonction_vide(f):
    f["m_target"] = {"m_guid": ""}
    f["m_inputs"] = {"m_variable": {"m_argumentBytes": []}}
    f["m_outputs"] = {"m_variable": {"m_argumentBytes": []}}


def reglages_effectif():
    """les réglages d'Alex de l'écran Équipe première (effectif_boutons_entrainement), posés dans entrainement_equipes
    le temps d'un appel : renvoie ceux à remettre"""
    avant = (ee.EMPLACEMENTS["effectif"], ee.EFFECTIF_INDIVIDUEL, ee.EFFECTIF_PROGRAMME)
    ee.EMPLACEMENTS["effectif"], ee.EFFECTIF_INDIVIDUEL, ee.EFFECTIF_PROGRAMME = (
        eb.EFFECTIF, eb.EFFECTIF_INDIVIDUEL, eb.EFFECTIF_PROGRAMME)
    return avant


def remettre_reglages(avant):
    ee.EMPLACEMENTS["effectif"], ee.EFFECTIF_INDIVIDUEL, ee.EFFECTIF_PROGRAMME = avant


# ---------- morceaux de FM recopiés ----------
class Sources:
    def __init__(self):
        e = ouvrir(EFFECTIF, depart_original=True)
        self.te = e[3] if e else None
        self.icone = None
        if self.te is not None:
            tac = first(self.te, lambda r: self.te.name(r) == "TacticsButton" and typ(self.te, r) == "SIButton")
            if tac is not None:   # l'icône du bouton Tactiques (VisualElement qui ne prend pas le clic)
                self.icone = next((k for k in self.te.children(tac) if typ(self.te, k) == "VisualElement"
                                   and any(c.endswith("_small") for c in self.te.elem(k)["m_Classes"])), None)
        u = ouvrir(SOURCE_BULLE, depart_original=True)
        self.tu = u[3] if u else None
        self.bulle = None if self.tu is None else first(
            self.tu, lambda r: typ(self.tu, r) == "Tooltip" and len(self.tu.children(r)) == 1
            and typ(self.tu, self.tu.children(r)[0]) == "SIText")
        v = ouvrir(VUE, depart_original=True)
        self.tv = v[3] if v else None
        self.titre = None if self.tv is None else first(
            self.tv, lambda r: self.tv.elem(r).get("m_TemplateAlias") == ALIAS_TITRE)
        self.texte_titre = None   # la liaison du texte traduit du lien « Équipe première »
        if self.titre is not None:
            self.texte_titre = next((d["TextBinding"] for d in surcharges(self.tv, self.titre) if "TextBinding" in d
                                     and (d["TextBinding"]["m_visualFunction"]["m_target"] or {}).get("m_guid")), None)

    def ok(self):
        return None not in (self.icone, self.bulle, self.titre, self.texte_titre)

    def texte_traduit(self, numero, repere):
        """liaison de texte d'un SIText : le texte FM n° <numero> (la fonction du lien « Équipe première »)"""
        b = copy.deepcopy(self.texte_titre)
        args = decode_args(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"TranslationID]"):
                a[1] = struct.pack("<i", numero) + b"\x01" + _enc_varint(len(repere)) + repere
        b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        return b


# ---------- un bouton en icône ----------
def iconifier(t, b, icone, numero, repere, src, nom_icone, nom_bulle):
    """le bouton b perd son texte, reçoit l'icône de FM <icone> et, au survol, le texte FM n° <numero>"""
    sd = t.sd(b)
    fonction_vide(sd["BindTextFunction"])   # texte du bouton lui-même (boutons de l'Effectif)
    sd["BindTextFunction_UxmlAttributeFlags"] = 0
    sd["StaticText"], sd["StaticText_UxmlAttributeFlags"] = "", 0
    for k in t.children(b):                  # texte posé en enfant (boutons des Tactiques)
        if typ(t, k) == "SIText":
            ks = t.sd(k)
            ks["TextBinding"]["m_kind"] = 0
            ks["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            fonction_vide(ks["TextBinding"]["m_visualFunction"])
            ks["text"], ks["text_UxmlAttributeFlags"] = "", 1
    ic = t.clone(src.icone, b, 0, src=src.te)
    no_styles(t, ic)
    recaler_parent(t, ic)
    t.elem(ic)["m_Classes"] = [icone]
    nommer(t, ic, nom_icone)
    bulle = t.clone(src.bulle, b, src=src.tu)   # sur le bouton entier
    t.styles.copy_from(src.tu.styles, t, bulle)
    recaler_parent(t, bulle)
    nommer(t, bulle, nom_bulle)
    texte = t.children(bulle)[0]
    recaler_parent(t, texte)
    nommer(t, texte, nom_bulle + "-texte")
    t.sd(texte)["TextBinding"] = src.texte_traduit(numero, repere)
    t.sd(texte)["TextBinding_UxmlAttributeFlags"] = 1


# ---------- Vue d'ensemble : les trois boutons d'Alex, en icônes ----------
def ajouter_boutons(t, mx, src):
    avant = reglages_effectif()
    try:
        msgs = ee.construire_effectif(t, mx)
    finally:
        remettre_reglages(avant)
    if any("introuvable" in m for m in msgs):
        return msgs
    racine = [r for r in t.walk() if t.name(r) == ee.NOM_RACINE]
    if len(racine) != 1:
        return ["boutons d'Alex : ajout inattendu (introuvable)"]
    boutons = boutons_alex(t, EFFECTIF)   # encore sous ses noms
    t.sd(racine[0])["name"] = nom_boutons()
    for fin, b in boutons.items():
        cle = {"bouton": "entrainement"}.get(fin, fin)
        t.sd(b)["name"] = f"{PREFIXE}-bouton-{cle}"
        if icones():
            numero, repere = TEXTES[EFFECTIF][fin]
            iconifier(t, b, ICONES[fin], numero, repere, src, f"{PREFIXE}-icone-{cle}", f"{PREFIXE}-bulle-{cle}")
    if any(t.name(r).startswith(ee.PREFIXE) for r in t.walk(racine[0])):
        return ["boutons d'Alex : nom inattendu (introuvable)"]
    return [m.replace("effectif : ", "Vue d'ensemble : ", 1) for m in msgs] + [
        f"Vue d'ensemble : les {len(boutons)} boutons en icônes, leur nom FM au survol" if icones() else
        f"Vue d'ensemble : les {len(boutons)} boutons écrits (réglage 26.11)"]


# ---------- boutons d'Alex (écran Effectif, Tactiques) : en icônes, sur place ----------
def boutons_alex_origine(modele, mx):
    """les données des boutons d'Alex tels que SA fonction les construit (sur l'original, en mémoire, rien n'est
    enregistré) : {fin : (données du bouton, [données de ses SIText enfants])}"""
    o = ouvrir(modele, depart_original=True)
    if o is None:
        return None
    s = o[3]
    if modele == EFFECTIF:
        avant = reglages_effectif()
        try:
            msgs = ee.construire_effectif(s, mx)
        finally:
            remettre_reglages(avant)
    else:
        msgs = tb.construire(s)
    if any("introuvable" in m for m in msgs):
        return None
    return {fin: (copy.deepcopy(s.sd(b)), [copy.deepcopy(s.sd(k)) for k in s.children(b) if typ(s, k) == "SIText"])
            for fin, b in boutons_alex(s, modele).items()}


def copier_donnees(dst, src):
    garde = dst.get("uxmlAssetId")
    dst.clear()
    dst.update(copy.deepcopy(src))
    if garde is not None:
        dst["uxmlAssetId"] = garde


def rendre_boutons_alex(t, modele, origine):
    """rend aux boutons d'Alex leurs données (texte compris), celles de sa fonction"""
    rendus = 0
    for fin, b in boutons_alex(t, modele).items():
        if fin not in origine:
            continue
        donnees, textes = origine[fin]
        copier_donnees(t.sd(b), donnees)
        enfants = [k for k in t.children(b) if typ(t, k) == "SIText"]
        if len(enfants) != len(textes):
            return None
        for k, d in zip(enfants, textes):
            copier_donnees(t.sd(k), d)
        rendus += 1
    return rendus


def iconifier_alex(t, modele, src):
    boutons = boutons_alex(t, modele)
    for fin, b in boutons.items():
        numero, repere = TEXTES[modele][fin]
        iconifier(t, b, ICONES[fin], numero, repere, src, f"{ALEX}-icone-{fin}", f"{ALEX}-bulle-{fin}")
    nom = {EFFECTIF: "écran Effectif", TACTIQUES: "écran Tactiques"}[modele]
    return [f"{nom} : boutons d'Alex en icônes ({', '.join(boutons)}), leur nom FM au survol" if boutons else
            f"{nom} : pas de boutons d'Alex (sa fonction n'est pas appliquée), rien à changer"]


# ---------- Vue d'ensemble : liens des équipes à la suite d'« Équipe première » ----------
def ajouter_liens(t, mx):
    titre = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == ALIAS_TITRE)
    parent = None if titre is None else t.parent.get(titre)
    if parent is None:
        return ["lien « Équipe première » (title-link) introuvable"]
    # une rangée à sa place, qui reprend ses classes (marge du bas) ; le lien y est déplacé
    rangee = el.plain(t, parent, t.children(parent).index(titre),
                      ["row-direction-normal"] + list(t.elem(titre)["m_Classes"]), NOM_TITRE)
    t.elem(rangee)["m_RuleIndex"] = -1   # plain() recopie un élément du bloc : pas son style
    t.sd(rangee)["name_UxmlAttributeFlags"] = 1
    el.move(t, titre, rangee)
    t.elem(titre)["m_Classes"] = []
    # la liste d'Alex (non virtualisée : largeur de son contenu), équipes du club du joueur seulement
    ee.rangee(t, mx, rangee, None, {"liste": EQUIPES["liste"], "largeur": None, "hauteur": 1, "marge": 0,
                                    "descendre": 0}, meme_club=True)
    nouveaux = [r for r in t.children(rangee) if r != titre]
    if len(nouveaux) != 1:
        return ["liens des équipes : ajout inattendu (introuvable)"]
    club = nouveaux[0]
    for r in t.walk(club):
        if t.name(r).startswith(ee.PREFIXE):
            t.sd(r)["name"] = NOM_LIENS if r == club else NOM_LIENS_LISTE
    listes = [r for r in t.walk(club) if t.sd(r).get("ItemTemplate")]
    if t.name(club) != NOM_LIENS or len(listes) != 1 or not reecrire_regle(t, club, {"flex-shrink": 0}):
        return ["liens des équipes : nom, liste ou style inattendus (introuvable)"]
    t.sd(listes[0])["ItemTemplate"]["m_AssetGUID"] = GUID_LIEN
    return [f"Vue d'ensemble : liens des équipes du club ({EQUIPES['liste']}) à la suite d'« Équipe première », "
            "l'équipe affichée cachée, équipes du club du joueur seulement"]


def construire_lien(t, mx, src):
    racine = t.tt["m_VisualTree"]["rid"]
    attente = next((k for k in t.children(racine) if typ(t, k) == "BindingExpect"), None)
    if attente is None or not t.sd(attente).get("Parameters") or not declarer_modele(t, src.tv, ALIAS_TITRE):
        return [f"{LIEN} (BindingExpect) ou modèle inclus {ALIAS_TITRE} introuvable"]
    # paramètres : l'équipe de la ligne, et l'équipe affichée (facultative, donnée par la liste d'Alex)
    params = t.sd(attente)["Parameters"]
    ligne = copy.deepcopy(params[0])
    ligne["name"], ligne["type"]["id"], ligne["isOptional"] = "row", ee.TYPE_EQUIPE, 0
    affichee = copy.deepcopy(params[0])
    affichee["name"], affichee["type"]["id"], affichee["isOptional"] = ee.PARAM_EQUIPE, ee.TYPE_EQUIPE, 1
    params[:] = [ligne, affichee]
    for k in list(t.children(attente)):
        t.remove(k)
    # le style de la racine de la cellule FM (fond noir à 39 %, hauteur 40 px) : remplacé, le lien n'a ni fond ni
    # hauteur imposée (comme « Équipe première »)
    if not reecrire_regle(t, attente, {"flex-shrink": 0}):
        return [f"{LIEN} : style de la racine inattendu (introuvable)"]
    # caché pour l'équipe affichée (« Équipe première » est déjà écrit à gauche)
    b = make_binding(mx.s_vis.sd(mx.vis)["Binding"], NON_EGAL, ["row.UniqueId", f"{ee.PARAM_EQUIPE}.UniqueId"])
    v = new_visible(t, mx.s_vis, mx.vis, attente, None, NOM_LIEN, b, ["row-direction-normal"])
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, v, {"margin-left": ECART_LIENS})
    # le lien de FM d'« Équipe première », pour cette équipe
    lien = t.clone(src.titre, v, src=src.tv)
    no_styles(t, lien)
    t.elem(lien)["m_Classes"] = []
    evenement = texte = 0
    for d in surcharges(t, lien):
        if "Events" in d:
            d["Events"]["m_bytes"] = list(ee.evenement_ecran(ECRAN_EFFECTIF, [("team", "row")]))
            evenement += 1
        if "TextBinding" in d:
            tb_ = d["TextBinding"]
            tb_["m_kind"] = 1
            tb_["m_direct"]["Path"]["m_path"] = TEXTE_EQUIPE
            fonction_vide(tb_["m_visualFunction"])
            d["DebugDisplay"] = "UIPicker team link"
            texte += 1
    if (evenement, texte) != (1, 1):
        return [f"lien d'équipe : surcharges du {ALIAS_TITRE} inattendues (introuvable)"]
    return [f"lien d'équipe : {ALIAS_TITRE} de FM dans {LIEN}, texte = {TEXTE_EQUIPE}, clic = écran Effectif de "
            "l'équipe (TeamSquadReport), caché pour l'équipe affichée"]


# ---------- écran Effectif : la rangée des équipes ----------
def ajouter_equipes(t, mx, ecran):
    onglets = first(t, lambda r: t.name(r) == "TabButtons")   # « Avec le ballon / Sans le ballon »
    groupe = None if onglets is None else t.parent.get(onglets)
    ligne = None if groupe is None else t.parent.get(groupe)
    if ligne is None or t.name(ligne) != "possessionToggle" or not typ(t, groupe).endswith("ContextShortcutsElement"):
        return [f"{ecran} : boutons « Avec le ballon / Sans le ballon » (#possessionToggle > #TabButtons) introuvables"]
    avant = set(t.children(ligne))
    ee.rangee(t, mx, ligne, t.children(ligne).index(groupe) + 1, dict(EQUIPES, largeur=1, descendre=0),
              meme_club=True)
    nouveaux = [r for r in t.children(ligne) if r not in avant]
    if len(nouveaux) != 1:
        return [f"{ecran} : rangée des équipes, ajout inattendu (introuvable)"]
    club = nouveaux[0]
    # ee.rangee donne ses noms (UIPickerEquipesEntrainement…) : les nôtres à la place. Repérée par sa position (pas par
    # son nom) : sur l'écran Effectif, le SIVisible des boutons d'Alex porte le même nom que celui de sa rangée.
    for r in t.walk(club):
        if t.name(r).startswith(ee.PREFIXE):
            t.sd(r)["name"] = NOM_EQUIPES if r == club else NOM_LISTE
    listes = [r for r in t.walk(club) if t.sd(r).get("RowTemplate")]
    if t.name(club) != NOM_EQUIPES or len(listes) != 1:
        return [f"{ecran} : rangée des équipes, nom ou liste inattendus (introuvable)"]
    t.sd(listes[0])["RowTemplate"]["m_AssetGUID"] = GUID_CELLULE
    # place : toute la largeur libre de la ligne, juste après les deux boutons (au lieu de la largeur fixe d'ee.rangee)
    if not reecrire_regle(t, club, {"height": EQUIPES["hauteur"], "margin-left": EQUIPES["marge"], "flex-grow": POUSSER,
                                    "flex-shrink": 1, "min-width": 0, "align-self": "center",
                                    "top": DECALER_EQUIPES}):
        return [f"{ecran} : style de la rangée d'Alex inattendu (introuvable)"]
    return [f"{ecran} : boutons des équipes du club ({EQUIPES['liste']}) après « Avec le ballon / Sans le ballon », "
            "équipes du club du joueur seulement"]


def retirer_racines(t):
    """retire nos éléments, puis les règles de style qu'ils étaient seuls à utiliser (celles des autres restent)"""
    racs = racines(t)
    nos_regles = {t.elem(r).get("m_RuleIndex", -1) for x in racs for r in t.walk(x)} - {-1}
    for r in racs:
        t.remove(r)
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = nos_regles - utilisees
    if not enlever:
        return bool(racs)
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    # les valeurs que nos règles avaient ajoutées en fin de table (1000, 32 px…) : enlevées si plus rien ne s'en sert
    # (seulement en fin de table, les numéros des autres valeurs ne bougent pas ; mesuré le 11/10 : la feuille d'Alex
    # n'a aucune valeur inutilisée, le retrait la rend donc à l'identique)
    tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
    servies = {}
    for regle in t.styles.sh["m_Rules"]:
        for p in regle["m_Properties"]:
            for v in p["m_Values"]:
                if v["m_ValueType"] in tables:
                    servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
    for nom in set(tables.values()):
        valeurs = t.styles.sh.get(nom) or []
        while valeurs and len(valeurs) - 1 not in servies.get(nom, set()):
            valeurs.pop()
    t.styles.changed = True
    return True


def remettre_partage(t, modele, mx):
    """modèle partagé avec Alex : nos éléments retirés, ses boutons rendus tels que sa fonction les fait"""
    origine = boutons_alex_origine(modele, mx) if boutons_alex(t, modele) else {}
    if origine is None:
        return None
    ancien = retirer_racines(t)
    if rendre_boutons_alex(t, modele, origine) is None:
        return None
    return ancien


# ---------- la cellule du bouton d'équipe (écran Effectif) ----------
def construire_cellule(t, src):
    msgs = ee.construire_bouton(t, src)   # le bouton de la rangée d'Alex : nom et clic remplacés ci-dessous
    if any("introuvable" in m for m in msgs):
        return msgs
    racine = t.tt["m_VisualTree"]["rid"]
    c = t.children(racine)[0]
    t.sd(c)["name"] = NOM_CELLULE
    ev = ee.evenement_ecran(ECRAN_EFFECTIF, [("team", "row")])
    boutons = [r for r in t.walk(c) if typ(t, r) == "SIButton"]
    for r in boutons:
        t.sd(r)["Events"]["m_bytes"] = list(ev)
    if not boutons:
        return ["boutons du modèle FM introuvables"]
    # comme 26.2 v4 : le texte du bouton (SIText de FM) ne prend pas le clic, sinon une petite fenêtre vide s'ouvre
    textes = [r for r in t.walk(c) if typ(t, r) == "SIText"]
    for r in textes:
        t.sd(r)["pickingMode"], t.sd(r)["pickingMode_UxmlAttributeFlags"] = 1, 1
    return [f"bouton d'équipe : copie de {ee.BOUTON_SOURCE} dans {CELLULE}, clic = écran Effectif de l'équipe "
            f"(TeamSquadReport), texte non cliquable ({len(textes)})"]


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre_original(o, nom):
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{nom} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return False
    obj.save_typetree(orig)
    feuille = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if feuille is not None:
        t.styles.sh, t.styles.changed = feuille, True
        t.styles.save()
    nb._dirty.add(bundle)
    print(f"{nom} : remis d'origine")
    return True


# ---------- commandes ----------
def cmd_appliquer():
    if not ee._verifier_evenement():
        print("[Kinito] Effectif : format d'événement d'Alex inattendu, rien enregistré")
        return
    vue, cel, lie = ouvrir(VUE), ouvrir(CELLULE), ouvrir(LIEN)
    partages = {m: ouvrir(m) for m in PARTAGES}
    if None in (vue, cel, lie) or None in partages.values():
        print("[Kinito] Effectif : modèles de l'Effectif / des Tactiques introuvables (renommés par une mise à jour ?), "
              "ignoré")
        return
    vue_ok = vue_a_jour(vue[3])
    cel_ok = cellule_a_jour(cel[3], NOM_CELLULE, EQUIPES["actif"])
    lie_ok = cellule_a_jour(lie[3], NOM_LIEN, LIENS)
    partages_ok = {m: partage_a_jour(o[3], m) for m, o in partages.items()}
    if vue_ok and cel_ok and lie_ok and all(partages_ok.values()):
        print("[Kinito] Effectif : déjà appliqué")
    else:
        mx, src = ee.Morceaux(), Sources()
        src_b = ouvrir(ee.BOUTON_SOURCE)
        if src_b is None or not mx.ok() or mx.aujourdhui is None or not src.ok():
            print("[Kinito] Effectif : morceaux d'Alex / de FM introuvables, rien enregistré")
            return
        msgs = []
        # Vue d'ensemble et cellules (à nous) : depuis l'original, seulement celles qui ne sont pas à jour
        travail_v = ouvrir(VUE, depart_original=True) if not vue_ok else None
        travail_c = ouvrir(CELLULE, depart_original=True) if not cel_ok else None
        travail_l = ouvrir(LIEN, depart_original=True) if not lie_ok else None
        if any(o is not None and marques(o[3]) for o in (travail_v, travail_c, travail_l)):
            print("[Kinito] Effectif : pas de sauvegarde d'origine propre de la Vue d'ensemble ou d'une cellule, ignoré")
            return
        if travail_v is not None:
            if BOUTONS:
                msgs += ajouter_boutons(travail_v[3], mx, src)
            if LIENS:
                msgs += ajouter_liens(travail_v[3], mx)
            msgs += ["Vue d'ensemble : ancienne version remplacée"] if marques(vue[3]) else []
        if travail_c is not None and EQUIPES["actif"]:
            msgs += construire_cellule(travail_c[3], src_b[3])
        if travail_l is not None and LIENS:
            msgs += construire_lien(travail_l[3], mx, src)
        # modèles partagés avec Alex : nos éléments retirés et ses boutons rendus, puis tout remis
        for m, o in partages.items():
            if partages_ok[m]:
                continue
            ancien = remettre_partage(o[3], m, mx)
            if ancien is None:
                msgs.append(f"{m} : boutons d'Alex à rendre introuvables (sa fonction a changé ?)")
                continue
            if m == EFFECTIF and EQUIPES["actif"]:
                msgs += ajouter_equipes(o[3], mx, "écran Effectif")
            if ICONES_ALEX and icones():
                msgs += iconifier_alex(o[3], m, src)
            elif boutons_alex(o[3], m):
                msgs.append(f"{m} : boutons d'Alex écrits, comme sa fonction les fait (réglage 26.11)")
            msgs += [f"{m} : ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"[Kinito] Effectif : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Effectif : rien enregistré")
            return
        for o in (travail_v, travail_c, travail_l):
            if o is not None:
                enregistrer(*o)
        for m, o in partages.items():
            if not partages_ok[m]:
                enregistrer(*o)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    mx = None
    for m in PARTAGES:
        o = ouvrir(m)
        if o is None or not racines(o[3]):
            continue
        mx = mx or ee.Morceaux()
        if remettre_partage(o[3], m, mx) is None:
            print(f"{m} : boutons d'Alex à rendre introuvables (sa fonction a changé ?) : rien fait sur ce modèle ; "
                  "réappliquer sa fonction les remettra")
            continue
        enregistrer(*o)
        fait = True
        print(f"{m} : éléments Kinito retirés, boutons d'Alex rendus tels que sa fonction les fait (le reste du modèle "
              "n'est pas touché)")
    for nom in (VUE, CELLULE, LIEN):
        o = ouvrir(nom)
        if o is not None and marques(o[3]):
            fait = remettre_original(o, nom) or fait
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    vue, cel, lie = ouvrir(VUE), ouvrir(CELLULE), ouvrir(LIEN)
    partages = {m: ouvrir(m) for m in PARTAGES}
    if None in (vue, cel, lie) or None in partages.values():
        print("modèles de l'Effectif / des Tactiques introuvables")
        return
    def etat(t, ok, v):
        return f"à jour (v{v})" if ok and marques(t) else ("ANCIENNE version" if marques(t) else "d'origine")
    print("boutons modifiés : " + ("en ICÔNES (26.11 pas activée)" if icones() else "ÉCRITS (réglage 26.11 activé)"))
    print(f"{VUE} (Vue d'ensemble) : {etat(vue[3], vue_a_jour(vue[3]), VERSION)}")
    for m, o in partages.items():
        t = o[3]
        ok = partage_a_jour(t, m)
        print(f"{m} : " + ("à jour" if ok and marques(t) else
                           "à refaire (nouvelle version de cet ajout, ou le script d'Alex a réécrit le modèle)"
                           if not ok and os.path.exists(MARKER) else "d'origine" if not marques(t) else "ANCIENNE")
              + f" — boutons d'Alex : {', '.join(boutons_alex(t, m)) or 'aucun'}")
    print(f"{CELLULE} (bouton d'équipe) : "
          f"{etat(cel[3], cellule_a_jour(cel[3], NOM_CELLULE, EQUIPES['actif']), VERSION_CELLULE)}")
    print(f"{LIEN} (lien d'équipe) : {etat(lie[3], cellule_a_jour(lie[3], NOM_LIEN, LIENS), VERSION_LIEN)}")
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
            print("[Kinito] Effectif : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
