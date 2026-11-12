"""Attributs du STAFF en notes (1-20) au lieu des libellés de FM (« Bon », « Exceptionnel »...).

Recette staff\\notes_staff_libelles.txt (textes passés en affichage direct de la note, voir
commun\\notes_au_lieu_des_libelles.py) : profil d'un membre du staff (bloc Attributs, avec et sans icône), liste du
staff, recherche de staff. La couleur de la note ne change pas (couleurs_staff_comme_joueurs s'en occupe).

Avant le 2026-11-12, cette recette était appliquée d'office au début du choix 1, sans interrupteur.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\staff\\notes_staff.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\staff\\notes_staff.py retirer
  .venv\\Scripts\\python.exe outils\\staff\\notes_staff.py etat
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402

RECETTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes_staff_libelles.txt")
MARKER = os.path.join(backup.BACKUP_DIR, "notes_staff.actif")


def lignes():
    return [l.strip() for l in open(RECETTE, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]


# Recrutement du staff > Critères de recherche > Attributs (2026-11-12, demande du joueur) : la recherche de joueurs et
# celle du staff lisent la même liste (personsearch.AttributesItemsList) ; FM montre aux joueurs une zone à flèches qui
# affiche la note (attributesminvalue.id), au staff un menu qui affiche le libellé (Bon, Très bon...). Le staff prend
# la zone des joueurs : SIVisible « isplayersearch » -> toujours, « isstaffsearch » -> jamais (valeur min et max).
CRITERES = "PersonSearchAttributeFiltersMainBlock"
ZONE_JOUEURS, MENU_STAFF = "inputs-combobox-controls-default", "dropdown-secondary"


def criteres(t):
    faits = 0
    for r in t.walk():
        chemin = (t.binding(r) or "").lower()
        if chemin not in ("isplayersearch", "isstaffsearch", "const.true", "const.false"):
            continue
        alias = {t.elem(k).get("m_TemplateAlias") for k in t.children(r)}
        voulu = {ZONE_JOUEURS: "const.True", MENU_STAFF: "const.False"}.get(next(iter(alias), None)) \
            if len(alias) == 1 else None
        if voulu is None or chemin == voulu.lower():
            continue
        t.sd(r)["Binding"]["m_direct"]["Path"]["m_path"] = voulu
        faits += 1
    # 2026-11-12 (vu en jeu) : au repos la zone écrit le nom du niveau (« Bon »), le chiffre (12) seulement au clic :
    # son texte (surcharge) = attributesmin/maxvalue.name -> .id, comme dans les lignes de conditions (v3)
    for r in t.walk():
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            b = (t.refs[o["m_SerializedData"]["rid"]].get("data") or {}).get("TextBinding")
            if not (isinstance(b, dict) and b.get("m_kind") == 1):
                continue
            p = b["m_direct"]["Path"]
            if p["m_path"].lower() in TEXTES_NIVEAU:
                p["m_path"] = TEXTES_NIVEAU[p["m_path"].lower()]
                faits += 1
    faits += lignes_en_notes(t)
    return [f"critères Attributs du staff en notes (zone des joueurs, {faits} réglages)"] if faits else []


TEXTES_NIVEAU = {"personsearch.attributesminvalue.name": "personsearch.attributesminvalue.id",
                 "personsearch.attributesmaxvalue.name": "personsearch.attributesmaxvalue.id"}

# 2026-11-12 (le joueur : « passe ça en chiffres ») : la liste ouverte des zones écrit les niveaux (Bon, Très bon...) :
# ligne AddFilterRuleDropdownRow (row.Name), partagée par d'autres menus. Le 1 par 1 reste impossible (niveaux décidés
# par le code natif, voir etat.md). DetailLevelDropdownRow n'est cité par aucun modèle ni par le code : son contenu est
# remplacé par une copie de AddFilterRuleDropdownRow qui écrit row.id (la note), et nos zones pointent vers lui.
LIGNE_FM, LIGNE_NOTE = "AddFilterRuleDropdownRow", "DetailLevelDropdownRow"
GUID_LIGNE_FM, GUID_LIGNE_NOTE = "fe1c455c19346de48925d6b677afdcc5", "4be773a436b2e6c44951000596e942ac"
NOM_LIGNE_NOTE = "UIPickerLigneNote-v1"


def ligne_note(t):
    if any(t.name(r) == NOM_LIGNE_NOTE for r in t.walk()):
        return []
    from arbre import Tree, Styles
    sb, _, st = nb.find_vta(LIGNE_FM)
    if st is None:
        return [f"{LIGNE_FM} introuvable"]
    s = Tree(st)
    racine, src = t.tt["m_VisualTree"]["rid"], s.tt["m_VisualTree"]["rid"]
    for c in t.children(racine):
        t.remove(c)
    styles_src = Styles(sb, st)
    for c in s.children(src):
        n = t.clone(c, racine, src=s)
        t.styles.copy_from(styles_src, t, n)
    t.sd(t.children(racine)[0])["name"] = NOM_LIGNE_NOTE
    t.sd(t.children(racine)[0])["name_UxmlAttributeFlags"] = 1
    faits = 0
    for r in t.walk():
        b = t.sd(r).get("TextBinding")
        if isinstance(b, dict) and b.get("m_kind") == 1 and b["m_direct"]["Path"]["m_path"].lower() == "row.name":
            b["m_direct"]["Path"]["m_path"] = "row.id"
            faits += 1
    return [f"ligne de menu « note » (copie de {LIGNE_FM}, texte row.id, {faits})"] if faits else \
        [f"texte row.Name de {LIGNE_FM} introuvable"]


# v6 (2026-11-12, vu en jeu) : dans nos zones du staff, + / - (rule.MinValueSelection) font ±5 sans limite (23, -2) :
# le code ne sait pas avancer d'un niveau. + / - coupés (CanIncrement / CanDecrement : const.true -> const.false) ; la
# valeur se choisit dans la liste (niveaux 1, 4, 7, 10, 12, 15, 18, 20, en chiffres).
FONCTIONS_PLUS_MOINS = ("CanIncrementBoolFunc", "CanDecrementBoolFunc")
# v7 (vu en jeu : onglet Conditions = + / - utiles, gris en v6) : les deux onglets utilisent cette même ligne ;
# IsCombinedList (flèches d'ordre #change-order-visible) n'est vrai que dans Conditions -> + / - actifs là seulement
# v10 : de nouveau actifs dans les deux onglets (const.true = rien à changer), avec l'évènement rule.MinValue
CHEMIN_PLUS_MOINS = "const.true"
# v8 (vu en jeu : Conditions, + / - de 5 en 5, pas selon la liste) : ESSAI : évènements Lower / Raise (rule.MinValueSelection)
# vidés -> le combobox avance lui-même d'un élément de sa liste (comme à la molette, SetValueOnScroll) et écrit
# SelectionValueBinding (rule.minvalue, comme un choix dans la liste) ; + / - de nouveau actifs dans les deux onglets.
# Vu en jeu : + / - ne font plus rien nulle part (le combobox n'avance pas seul) -> v9 = retour à la v7.
# v10 (le joueur : « dans attributs ça marche, mets les mêmes ») : dans « Choisir attributs », les + / - du staff vont de
# niveau en niveau ; ils envoient « personsearch | MinValue » (mêmes codes d'action) et non « rule | MinValueSelection »
# (±5). Nos zones : MinValueSelection -> MinValue (MaxValue) : la propriété objet, que FM doit avancer dans sa liste.
EVENEMENTS_PLUS_MOINS = ("LowerValueEvent", "RaiseValueEvent")
# v11 vue en jeu (rule.MinValue) : + / - morts. v12 (essai) : rule.IncrementValue, comme le bouton global
# (personsearch.IncrementValue, qui marche) mais sur la ligne ; min et max (le max n'existe que pour « entre »)
# v13 : v12 morte aussi. Piste : en v4 (vu en jeu) l'ordre d'origine allait de niveau en niveau (15 -> 18) ; le ±5 est
# apparu après l'essai « boîte 1-20 » (rule.MinValue écrit en entier brut) -> lignes de la recherche enregistrée
# abîmées ? Ordre d'origine remis (aucune réécriture), à tester sur des lignes neuves.
PROPRIETES_EVENEMENT = {}


def evenement_propriete(octets, ancien, nouveau):
    """évènement [01×5][total int32][id 4][01][len int32 01 01 len cible][len int32 01 01 len propriété][4 octets] :
    propriété ancien -> nouveau (longueurs recalculées)"""
    b = bytes(octets)
    bloc = b"\x01\x01" + bytes([len(ancien)]) + ancien.encode()
    i = b.find(bloc)
    if i < 4 or int.from_bytes(b[i - 4:i], "little") != len(bloc):
        return None
    nb_ = b"\x01\x01" + bytes([len(nouveau)]) + nouveau.encode()
    n = b[:i - 4] + len(nb_).to_bytes(4, "little") + nb_ + b[i + len(bloc):]
    total = int.from_bytes(n[5:9], "little") + len(nb_) - len(bloc)
    return list(n[:5] + total.to_bytes(4, "little") + n[9:])


def plus_moins_par_niveaux(t, racine):
    faits = 0
    for r in t.walk(racine):
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            if (d.get("RowTemplate") or {}).get("m_AssetGUID") != GUID_LIGNE_NOTE:
                continue
            for k in EVENEMENTS_PLUS_MOINS:
                for ancien, nouveau in PROPRIETES_EVENEMENT.items():
                    n = evenement_propriete(d[k]["m_bytes"], ancien, nouveau)
                    if n is not None:
                        d[k]["m_bytes"] = n
                        faits += 1
    return faits


def chemin_fonction(octets, ancien, nouveau):
    """argument BindingPath (dernier argument : [longueur int32] ... 0x01 [longueur] chemin) : ancien -> nouveau"""
    b = bytes(octets)
    fin = (b"\x01" + bytes([len(ancien)]) + ancien.encode())
    if not b.endswith(fin):
        return None
    debut = len(b) - len(fin)
    # longueur int32 de l'argument : on la cherche en remontant (= taille de ce qui suit jusqu'à la fin)
    for i in range(debut - 1, 0, -1):
        if int.from_bytes(b[i - 4:i], "little") == len(b) - i:
            delta = len(nouveau) - len(ancien)
            n = b[:i - 4] + (len(b) - i + delta).to_bytes(4, "little") + b[i:debut] \
                + b"\x01" + bytes([len(nouveau)]) + nouveau.encode()
            return list(n)
    return None


# v14 (vu en jeu, v13 sur lignes neuves : + / - de niveau en niveau partout, mais 20 -> 23 et 1 -> -2) : + / - bornés
# avec la comparaison d'entiers de FM (d52cf0b2) : + si note < 20, - si note > 1 (la v1 « .id illisible » venait du
# mauvais menu, caché)
BORNES_PLUS_MOINS = {"CanIncrementBoolFunc": (0, 20), "CanDecrementBoolFunc": (4, 1)}   # (opérateur <, >), valeur


def sans_plus_moins(t, racine):
    from notes_installations import make_binding
    modele = liaison_comparer()
    faits = 0
    for r in t.walk(racine):
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            if (d.get("RowTemplate") or {}).get("m_AssetGUID") != GUID_LIGNE_NOTE or modele is None:
                continue
            note = (d.get("ValueBinding") or {}).get("m_path")
            for k, (op, valeur) in BORNES_PLUS_MOINS.items():
                d[k] = make_binding(modele, op, [note], valeur)["m_visualFunction"]
                d[k + "_UxmlAttributeFlags"] = 1
                faits += 1
    return faits


def lignes_en_notes(t, racine=None):
    """surcharges des zones (sous racine) : liste ouverte = ligne « note » au lieu de la ligne de FM"""
    faits = 0
    for r in t.walk(racine):
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            rt = d.get("RowTemplate")
            valeur = ((d.get("ValueBinding") or {}).get("m_path") or "").lower()
            if isinstance(rt, dict) and rt.get("m_AssetGUID") == GUID_LIGNE_FM \
                    and valeur.endswith(("minvalue.id", "maxvalue.id")):
                rt["m_AssetGUID"] = GUID_LIGNE_NOTE
                faits += 1
    return faits


# Recrutement du staff > Modifier recherche > Conditions / Attributs (2026-11-12, le joueur : « fais pareil que les
# joueurs pour avoir les notes, et un + - comme les attributs joueurs ») : dans une ligne de condition, la valeur d'un
# attribut du staff est un menu (#dropdown-value-visible, rule.ShowValueDropdown, texte rule.filtervalue.Name) ; celle
# d'un attribut de joueur, la zone à flèches (#attribute-combobox-value-min-visible, rule.minvalue). Essai vu en jeu :
# pour le staff, rule.minvalue.id = la note (Convenable 7, Très bon 15, Exceptionnel 18). Dans le menu, deux boîtes
# (le SIVisible du menu recopié, liaison de FM d52cf0b2 « entier OP valeur » de #intValueType) : minvalue.id >= 1 ->
# une copie de la zone des joueurs ; sinon (autres menus : Nationalité...) -> le menu de FM, déplacé tel quel.
CONDITIONS = ["PlayerSearchConditionFilterItem", "RecruitmentConditionFilterItem", "FilterRow",
              "PlayerSearchConditionFilterItemPhone"]
SOURCE_COMPARER = ("RecruitmentConditionFilterItem", "intValueType")   # SIVisible à liaison d52cf0b2 (ValueType == 4)
# v2 : v1 (rule.minvalue.id >= 1) vue en jeu : libellés partout (la comparaison d'entiers ne lit pas minvalue.id) ->
# rule.ValueType == 3 (entier que FM compare lui-même dans ce modèle ; vu 3 pour les attributs du staff)
PREFIXE = "UIPickerNotesStaff-"
# v3 : v2 vue en jeu : la zone s'affiche, + / - marchent, mais elle écrit le libellé : son texte est rule.minvalue.name
# (le chiffre chez les joueurs, « Moyen » au staff) -> rule.minvalue.id dans notre copie
# v4 : v3 vue en jeu, console du mod (une ls) : #dropdown-value-visible est CACHÉ sur ces lignes ; le menu « Très
# bon » des attributs du staff est #dropdown-value-min-visible (rule.ShowValueMinDropdown ; « entre » : aussi
# #dropdown-value-max-visible). Les v1-v3 étaient dans le mauvais menu : retirées. Paires (menu de FM, zone des joueurs,
# texte de la zone -> note)
# v5 (2026-11-12) : liste ouverte de la zone en chiffres (ligne « note », voir ligne_note)
# v6 : + / - coupés dans nos zones (voir sans_plus_moins)
# v7 : + / - actifs dans l'onglet Conditions (IsCombinedList), coupés dans Attributs
# v8 : essai, + / - sans évènement (avancent dans la liste), les deux onglets
# v9 : v8 ratée (+ / - morts partout) -> comme la v7
# v10 : + / - (Conditions) envoient rule.MinValue / MaxValue comme Choisir attributs (essai)
VERSION = "v14"   # v11 : v10 + actifs aussi dans l'onglet Attributs ; v12 : rule.IncrementValue ; v13 : ordre d'origine
#                   v14 : + / - bornés 1-20 -> CRASH de FM sur l'écran Conditions ; v15 : retour v13
VERSION = "v15"
# v16 (2026-11-12, essai, demande du joueur) : à 20 le + sort de la liste des niveaux (23), à 1 le - aussi (-2), puis
# FM avance de 5 en 5. Les + / - sont dessinés par le code de FMCombobox (pas d'élément à cacher) et CanIncrement /
# CanDecrement n'acceptent qu'un booléen de FM (6a864e59 ; une comparaison = crash, v14). Idée du joueur (« crée les
# tiens, qui ne parlent qu'au staff ») : dans NOTRE zone (staff seulement), les + / - de FM masqués
# (RaiseLowerVisibilityFunc = 6a864e59 sur const.false) et NOS boutons « - » « + » à leur place : SIButton dont
# l'évènement = celui de FM (rule | MinValueSelection, codes moins / plus), chacun dans un SIVisible « note != 1 »
# (-) / « note != 20 » (+) (comparaison de TEXTE 240779c1, qui lit un entier : settings.TextScaling ; d52cf0b2 ne
# lisait pas .id) ; une case de largeur fixe autour : la place reste quand un bouton est caché.
VERSION = "v16"
# v17 : v16 vue en jeu : + / - de FM bien masqués, nos boutons invisibles, CRASH en passant à l'onglet Attributs
# (Player.log : « Unable to cast SIVisible to ISIEnabled » dans un SIVisible : la comparaison de TEXTE 240779c1 sur
# la note) -> comparaison d'entiers d52cf0b2 (celle de nos boîtes) pour cacher nos boutons
VERSION = "v17"
# v18 : v17 vue en jeu : pas de + / - et MÊME crash dans Attributs (Player.log identique : ce n'était pas la
# comparaison, mais nos boutons / SIVisible dans la zone ou RaiseLowerVisibilityFunc). Choix du joueur : la liste des
# niveaux seule (« les ranges »), plus de 5 en 5, bloqué 1-20 -> nos boutons retirés, + / - de FM grisés (v6, vue en
# jeu sans crash)
VERSION = "v18"
# v18 finale (le joueur : « on garde les boutons de base, ça avait déjà marché ») : = v15, + / - de FM actifs et
# intacts (de niveau en niveau ; un dépassement 23 / -2 se répare en rechoisissant dans la liste)
NOS_BOUTONS = False
GRISER = False
# v19 (essai, le joueur : « fais parler les + / - comme les libellés ») : dans l'original, le menu du staff n'a PAS de
# + / - ; il envoie un CHOIX (SelectionEvents rule | rule.MinValue, liste rule.MinItems). Notre zone (copie de celle
# des joueurs) a SelectionEvents VIDE : en v8 (évènements des + / - vidés) la zone ne pouvait rien envoyer -> v19 :
# ordre de choix + liste du menu, évènements des + / - vidés
VERSION = "v19"
COMME_LE_MENU = True
# v20 : v19 vue en jeu : pas de crash mais + / - morts -> leur ordre d'origine (MinValueSelection) rendu, ordre de
# choix + liste rule.MinItems gardés (pari : le ±5 venait de la liste rule.items des joueurs)
VERSION = "v20"
VIDER_PLUS_MOINS = False
# v21 (2026-11-12, FINAL, le joueur après un test en vanilla : « les ranges de 5 c'est le mieux qu'on peut faire ») :
# v20 vue = toujours 5 en 5 ; dans le FM d'origine, ces lignes n'ont pas de + / -. Retour à la config v18 (+ / - de base)
VERSION = "v21"
COMME_LE_MENU = False
# 2026-11-11 (retour d'un joueur, Discord) : la boîte « note » s'affichait sur rule.ValueType == 3, vrai aussi pour
# Potentiel / Niveau actuel des joueurs -> zone d'attribut à la place du menu de FM, valeur ramenée à 100 (200 impossible).
# Le joueur : partie Conditions = option « staff_recherche » (fm = base : menus de FM ; chiffres = boîtes v21, casse
# Potentiel / Niveau actuel) ; le reste des chiffres du staff gardé.
import options  # noqa: E402
CONDITIONS_ACTIF = options.get("staff_recherche") == "chiffres"
BOUTON_LARGEUR = 28                    # px de chaque case + / -
BOUTONS_PM = (("moins", "1", "LowerValueEvent", "-"), ("plus", "20", "RaiseValueEvent", "+"))
SOURCE_TEXTE = "NonPlayerAttributesBlock"                      # SIVisible « texte == valeur » de FM (240779c1)
FN_TEXTE_EGAL = "240779c127ba1174a812adf0be56e006"
sm.PROPRIETES.setdefault("width", (131105, 3))
sm.PROPRIETES.setdefault("height", (131087, 3))
sm.PROPRIETES.setdefault("align-items", (131073, 7))
sm.PROPRIETES.setdefault("justify-content", (131088, 7))
PAIRES = [("dropdown-value-min-visible", "attribute-combobox-value-min-visible", "rule.minvalue.name", "rule.minvalue.id"),
          ("dropdown-value-max-visible", "attribute-combobox-value-max-visible", "rule.maxvalue.name", "rule.maxvalue.id")]
CHEMIN_TYPE, TYPE_ATTRIBUT = "rule.ValueType", 3
OP_EGAL, OP_DIFFERENT = 2, 5   # ComparisonOperator : < 0, <= 1, = 2, >= 3, > 4, != 5
_COMPARER = []


def liaison_comparer():
    if not _COMPARER:
        from arbre import Tree
        _, _, tt = nb.find_vta(SOURCE_COMPARER[0])
        s = Tree(tt) if tt is not None else None
        r = s and next((r for r in s.walk() if s.name(r) == SOURCE_COMPARER[1]), None)
        _COMPARER.append(json.loads(json.dumps(s.sd(r)["Binding"])) if r is not None else None)
    return _COMPARER[0]


_TEXTE = []


def _sources_boutons():
    """(modèle, SIVisible « texte == valeur »), (modèle, SIButton de FM) — recopiés dans nos zones"""
    if not _TEXTE:
        from notes_installations import visible_model
        from arbre import Tree
        _, _, tt = nb.find_vta(CONDITIONS[0])
        s = Tree(tt) if tt is not None else None
        btn = s and next((r for r in s.walk() if (s.elem(r).get("m_FullTypeName") or "").endswith("SIButton")), None)
        _TEXTE.append((visible_model(SOURCE_TEXTE, FN_TEXTE_EGAL), (s, btn)))
    return _TEXTE[0]


def parler_comme_le_menu(t, boite, libelle):
    """v19 : notre zone (boite) reprend l'ordre de choix (SelectionEvents rule | rule.MinValue) et la liste
    (rule.MinItems) du menu à libellés de FM (déplacé dans libelle) ; ses + / - perdent leur ordre (MinValueSelection,
    ±5) : pari = la zone avance d'un élément de SA liste et l'envoie comme un choix du menu"""
    import copy
    menu = None
    for r in t.walk(libelle):
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            if (d.get("SelectionEvents") or {}).get("m_bytes") and "BindChoicesFunction" in d:
                menu = d
    if menu is None:
        return 0
    faits = 0
    for r in t.walk(boite):
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            if "RaiseValueEvent" not in d:
                continue
            for k in ("SelectionEvents", "BindChoicesFunction"):
                d[k] = copy.deepcopy(menu[k])
                d[k + "_UxmlAttributeFlags"] = 1
            if VIDER_PLUS_MOINS:
                for k in EVENEMENTS_PLUS_MOINS:
                    d[k] = {"m_bytes": []}
                    d[k + "_UxmlAttributeFlags"] = 1
            faits += 1
    return faits


def griser_plus_moins(t, boite):
    """v18 : + / - de FM grisés dans notre zone (CanIncrement / CanDecrement sur const.false, comme la v6 vue en jeu)"""
    faits = 0
    for r in t.walk(boite):
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            if "RaiseValueEvent" not in d:
                continue
            for k in FONCTIONS_PLUS_MOINS:
                octets = chemin_fonction(d[k]["m_inputs"]["m_variable"]["m_argumentBytes"], CHEMIN_PLUS_MOINS,
                                         "const.false")
                if octets is None:
                    return 0
                d[k]["m_inputs"]["m_variable"]["m_argumentBytes"] = octets
                faits += 1
    return faits


def boutons_plus_moins(t, boite, chemin, nom):
    """v16 : + / - de FM masqués dans notre zone, nos boutons à leur place (- caché à 1, + caché à 20)"""
    import copy
    from notes_installations import make_binding
    _, (sb, btn) = _sources_boutons()
    zone = next((r for r in t.walk(boite) if t.elem(r).get("m_TemplateAlias") == "inputs-combobox-controls-default"),
                None)
    if None in (btn, zone, liaison_comparer()):
        return 0
    donnees = None
    for o in t.elem(zone).get("m_SerializedDataOverride") or []:
        d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
        if "RaiseValueEvent" in d and "CanIncrementBoolFunc" in d:
            donnees = d
    if donnees is None:
        return 0
    # les + / - de FM masqués : même fonction booléenne que CanIncrement (6a864e59), sur const.false (vu en jeu v16 :
    # masqués, pas de souci)
    f = copy.deepcopy(donnees["CanIncrementBoolFunc"])
    octets = chemin_fonction(f["m_inputs"]["m_variable"]["m_argumentBytes"], CHEMIN_PLUS_MOINS, "const.false")
    if octets is None:
        return 0
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = octets
    donnees["RaiseLowerVisibilityFunc"], donnees["RaiseLowerVisibilityFunc_UxmlAttributeFlags"] = f, 1
    cadre = t.parent[zone]
    for fin, note, evenement, texte in BOUTONS_PM:
        case = t.clone_shallow(cadre, cadre)
        t.sd(case)["name"], t.sd(case)["name_UxmlAttributeFlags"] = f"{nom}-{fin}", 1
        t.elem(case)["m_Classes"] = []
        t.elem(case)["m_RuleIndex"] = -1
        t.styles.style(t, case, {"width": BOUTON_LARGEUR, "flex-shrink": 0, "align-items": "center",
                                 "justify-content": "center"})
        # v17 : comparaison d'ENTIERS de FM (d52cf0b2, note != 1 / != 20), sur une copie de notre boîte (SIVisible).
        # v16 (texte 240779c1 sur la note) : CRASH au changement d'onglet (journal : SIVisible -> ISIEnabled)
        v = t.clone_shallow(boite, case)
        t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = f"{nom}-{fin}-visible", 1
        t.sd(v)["Binding"] = make_binding(liaison_comparer(), OP_DIFFERENT, [chemin], int(note))
        t.elem(v)["m_Classes"] = []
        t.elem(v)["m_RuleIndex"] = -1
        bouton = t.clone(btn, v, src=sb)
        for k in list(t.children(bouton)):
            t.remove(k)
        sm.no_styles(t, bouton)
        bd = t.sd(bouton)
        bd["name"], bd["name_UxmlAttributeFlags"] = f"{nom}-{fin}-bouton", 1
        bd["Events"] = {"m_bytes": list(donnees[evenement]["m_bytes"])}
        fonction_vide = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                         "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
        bd["BindTextFunction"], bd["BindTextFunction_UxmlAttributeFlags"] = fonction_vide, 0
        bd["StaticText"], bd["StaticText_UxmlAttributeFlags"] = texte, 1
        t.elem(bouton)["m_Classes"] = ["body-large-16px-regular", "white", "sitext-hover-cursor"]
        t.styles.style(t, bouton, {"width": BOUTON_LARGEUR, "height": BOUTON_LARGEUR, "align-items": "center",
                                   "justify-content": "center", **sm.SANS_CADRE})
    return len(BOUTONS_PM)


def conditions(t):
    from notes_installations import make_binding
    from elements import move
    nos = [r for r in t.walk() if t.name(r).startswith(PREFIXE)]
    if CONDITIONS_ACTIF and nos and all(f"-{VERSION}-" in t.name(r) for r in nos):
        return []
    # v16 : nos caches sont DANS nos boîtes : seules les boîtes du haut sont à défaire
    hauts = []
    for r in nos:
        p, dedans = t.parent.get(r), False
        while p is not None:
            if t.name(p).startswith(PREFIXE):
                dedans = True
                break
            p = t.parent.get(p)
        if not dedans:
            hauts.append(r)
    nos = hauts
    for r in nos:   # ancienne version : le menu de FM remis à sa place
        if r in t.parent and t.name(r).endswith("-libelle"):
            for c in t.children(r):
                move(t, c, t.parent[r])
        t.remove(r)
    if not CONDITIONS_ACTIF:
        return ["lignes de conditions : menus de FM remis (Potentiel / Niveau actuel jusqu'à 200)"] if nos else []
    modele = liaison_comparer()
    faits = 0
    for menu_nom, zone_nom, texte_zone, texte_note in PAIRES:
        menu = next((r for r in t.walk() if t.name(r) == menu_nom), None)
        zone = next((r for r in t.walk() if t.name(r) == zone_nom), None)
        if None in (menu, zone, modele):
            continue
        contenu = t.children(menu)
        boites = []
        for i, (suffixe, op) in enumerate((("note", OP_EGAL), ("libelle", OP_DIFFERENT))):
            b = t.clone_shallow(menu, menu, i)
            t.sd(b)["name"] = f"{PREFIXE}{VERSION}-{menu_nom}-{suffixe}"
            t.sd(b)["name_UxmlAttributeFlags"] = 1
            t.sd(b)["Binding"] = make_binding(modele, op, [CHEMIN_TYPE], TYPE_ATTRIBUT)
            boites.append(b)
        for c in contenu:
            move(t, c, boites[1])
        for c in t.children(zone):
            t.clone(c, boites[0])
        for r in t.walk(boites[0]):   # le texte de la zone (surcharge du modèle de FM) = la note
            e = t.elem(r)
            for sd in [t.refs[e["m_SerializedData"]["rid"]]] + [t.refs[o["m_SerializedData"]["rid"]]
                                                               for o in e.get("m_SerializedDataOverride") or []]:
                b = (sd.get("data") or {}).get("TextBinding")
                if isinstance(b, dict) and b.get("m_kind") == 1 and b["m_direct"]["Path"]["m_path"] == texte_zone:
                    b["m_direct"]["Path"]["m_path"] = texte_note
        lignes_en_notes(t, boites[0])
        # v15 : sans_plus_moins (bornes v14) RETIRÉ : FM plante en arrivant sur ces lignes (vu en jeu) ;
        # plus_moins_par_niveaux ne réécrit plus rien (PROPRIETES_EVENEMENT vide) : ordre d'origine
        plus_moins_par_niveaux(t, boites[0])
        if NOS_BOUTONS:
            if not boutons_plus_moins(t, boites[0], texte_note, f"{PREFIXE}{VERSION}-{menu_nom}"):
                return [f"{menu_nom} : + / - de FM ou morceaux de nos boutons introuvables"]
        elif GRISER and not griser_plus_moins(t, boites[0]):
            return [f"{menu_nom} : + / - de FM introuvables"]
        if COMME_LE_MENU and not parler_comme_le_menu(t, boites[0], boites[1]):
            return [f"{menu_nom} : ordre de choix du menu à libellés introuvable"]
        faits += 1
    if not faits:
        return [f"menus min / max, zones des joueurs ou liaison de {SOURCE_COMPARER[0]} introuvables"]
    return [f"menus min / max : {faits} remplacé(s) ; ""attributs du staff : note en chiffre (liste des niveaux, + / -) à la place du menu Bon / Très bon",
            f"+ / - à nous (essai {VERSION}) : - caché à 1, + caché à 20" if NOS_BOUTONS else
            ("+ / - de FM grisés : valeur choisie dans la liste des niveaux seulement" if GRISER else
             "+ / - de FM (pas de 5, code du jeu)")] + (
            [f"zone : ordre de choix et liste du menu à libellés de FM, + / - "
             f"{'sans leur ordre' if VIDER_PLUS_MOINS else 'avec leur ordre de FM'} (essai {VERSION})"]
            if COMME_LE_MENU else [])


def cmd_appliquer():
    nb.cmd_apply(RECETTE)
    from elements import appliquer_jobs
    appliquer_jobs([(LIGNE_NOTE, ligne_note), (CRITERES, criteres)] + [(m, conditions) for m in CONDITIONS], MARKER)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
        print("\nNotes du staff : 1-20 au lieu des libellés.")


def cmd_retirer():
    """remet les modèles d'origine puis refait tout le reste du skin (qui touche les mêmes fichiers)"""
    import lancer
    lancer.retirer_par_restauration(MARKER)
    print("\nLibellés d'origine du staff remis (Bon, Exceptionnel...).")


def cmd_etat():
    for spec in lignes():
        modele, reste = spec.split(":", 1)
        chemin = reste.split("=", 1)[1]
        _, _, tt = nb.find_vta(modele)
        if tt is None:
            print(f"{modele} : introuvable")
        else:
            print(f"{modele} : " + ("notes 1-20" if nb.already(tt, chemin) else "libellés d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
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
            print("notes du staff : non activées, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
