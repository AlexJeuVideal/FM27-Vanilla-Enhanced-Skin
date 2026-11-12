"""Fiche joueur COMPLÈTE au clic sur un de tes joueurs, partout dans le jeu.

FM ouvre la fiche « du point de vue » d'une équipe (reportcontextteam) : les tableaux (Effectif, Tactiques…) la donnent
à leurs lignes, les listes et blocs simples (Stats joueurs du Portail, raccourcis…) non. Sans elle, FM affiche la
fiche comme pour un joueur d'un autre club (État d'esprit, Entraînement, Pour / Contre absents).

Ce script donne aux cases joueur de FM (nom, photo, bouton du nom) une VALEUR PAR DÉFAUT pour reportcontextteam :
ton équipe (human.team), utilisée seulement quand rien ne la donne. Là où FM la donne déjà, rien ne change ; les
joueurs des autres clubs restent vus comme dans la recherche de joueurs de FM (contexte = ton équipe).
v4 : là où l'écran donne une autre équipe (messages, compétitions…), le lien du nom d'un joueur de ton club passe par
un aiguillage qui lui donne SON équipe (voir VERSION_AIGUILLAGE).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\fiche_contexte_equipe.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\fiche_contexte_equipe.py retirer
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\fiche_contexte_equipe.py etat
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)
import sauvegarde_originaux as backup  # noqa: E402

CONTEXTE = "reportcontextteam"
DEFAUT = "human.team"          # équipe par défaut (FM : recherche de joueurs, GlobalSearchResultsPeopleTabTableFactory)
TYPE_EQUIPE = 1145176088
# cases joueur qui ont déjà le paramètre (facultatif, sans défaut ou défaut null) : on lui donne DEFAUT
AVEC_PARAMETRE = [
    "PersonImageDescriptionCell", "PersonNameButton", "PersonNameCell14px", "PersonNameWNationalityCell",
    "PersonPortraitNameCell", "PersonPortraitShortNameCell", "PlayerImageDescriptionCell",
    "PlayerInjuryRecentlyReturnedCell", "PlayerMatchNameCell", "PlayerNameCell", "PlayerNameCell14pxBold",
    "PlayerNameCell16pxBold", "PlayerNameNationShortlistedCheckCell", "PlayerNamePlayingTimeCell",
    "PlayerNamePositionCell", "PlayerNamePositionCellWithBorders", "PlayerNameWClubCell", "PlayerNameWNationalityCell",
    "PlayerPortaitNameAndBuyinLevelCell", "PlayerPortaitNameAndBuyinLevelCompactCell",
    "PlayerPortaitNameAndMindsetCell", "PlayerPortraitCell", "PlayerPortraitCell_14px", "PlayerPortraitCell_32px",
    "PlayerPortraitNameCell", "PlayerPortraitNameCell-no-border", "PlayerPortraitNameCell-no-border_16px",
    "PlayerPortraitNameCellCompact", "PlayerPortraitNameNationalityCell", "PlayerPortraitNamePlayingTimeCell",
    "PlayerPortraitNamePositionCell", "PlayerPortraitNamePositionClubNationCell", "PlayerPortraitShortNameCell",
    "PlayerShortNamePositionCell", "PlayerSurnameCell",
    "PlayerNameButton", "PlayerNameNationShortlistedButton", "PlayerPortraitNameClub",
]
# cases joueur cliquables (fiche, 77188c7b) sans ce paramètre : on l'ajoute (facultatif, DEFAUT)
SANS_PARAMETRE = [
    "PlayerPortraitNameRolesCell", "PlayerPortraitNameHierarchyCell", "PlayerShirtNamePositionCell",
    "PlayerPortraitNameAndBanCell", "PlayerPortraitNameAndPotentialBanCell", "PlayerPortraitNameMediumCellAsterisk",
    "PlayerPortraitNamePositionCellWithBorders", "PersonPortraitNameCellWithSecondaryText",
    "PersonPortraitNameCellWithSecondaryText-Compact", "PlayerRoleAbilityCell", "PlayerRoleAbilityCellInMatch",
    "PlayerTacticAbilityCell", "PlayerTacticAbilityCellInMatch",
]
MARKER = os.path.join(backup.BACKUP_DIR, "fiche_contexte_equipe.actif")

# v2 (2026-11-09) : BindingRemapper reportcontextteam -> <personne>.Team en RACINE de chaque case : vu en jeu, sans
# effet (la case reçoit l'équipe à son entrée, avant ce relais) -> retiré en v3 (defaire_relais).
VERSION_RELAIS = "uipicker-contexte-v2"
# v3 (2026-11-09, Kastrati / Caputcho, page du club) : l'équipe du joueur posée dans le BLOC PARENT, sur le
# BindingRemapper qui donne déjà la personne à la case incluse (comme la pyramide de la hiérarchie, validée) :
# (modèle, nom du BindingRemapper, chemin de la personne dans ce remapper)
PORTEURS = [
    ("ClubKeyPeopleCell", "person-found", "person"),   # en-tête de la page club : meilleur joueur, capitaine...
]
# v4 (2026-11-12, le joueur : fiche « pas chez toi » depuis un message, les compétitions… « sur tous les noms
# interactifs ») : le clic du nom = NavigableLink de text-cell-medium / -large, il lit reportcontextteam là où il est.
# Dans chaque case joueur, le lien est mis dans un aiguillage sur <personne>.Team.IsHuman (seul l'enfant choisi est
# construit) : faux = le lien tel quel (contexte donné par l'écran, inchangé pour les autres clubs) ; vrai = le lien
# dans un BindingRemapper reportcontextteam -> <personne>.Team (comme FM dans PlayerKitNamePlayingTimeCell : remapper
# SOUS le paramètre de la case, pas au-dessus comme v2).
# v5 (2026-11-12) : v4 vidait le nom des joueurs SANS CLUB (Team nul -> aiguillage sans branche, vu en jeu : rapports
# des recruteurs). Condition = variable Bool (BindingSetter de FM, défaut faux) « human.Club.Teams contient
# <personne>.Team » (comme entrainement_equipes v12) : sans club = faux = lien d'origine ; U19 / U23 de ton club = vrai.
VERSION_AIGUILLAGE = 5
NOM_AIGUILLAGE_V4 = "UIPickerContexteAiguillage-v4"
NOM_CALCUL = f"UIPickerContexteCalcul-v{VERSION_AIGUILLAGE}"
VAR_MON_CLUB = "uipickerjoueurduclub"
LIENS =("text-cell-medium", "text-cell-large", "PlayerNameButton")   # aiguillés là où une case les inclut
# PlayerNameButton jamais modifié lui-même : les cartes jeunes de Kinito (26.x v19) visent son chemin exact
# (.kinito-nom-bouton > .row-direction-normal > TemplateContainer) ; il est aiguillé depuis les cases qui l'incluent
PAS_DEDANS = ("PlayerNameButton",)
# autres cases qui incluent PlayerNameButton directement (aiguillage seul ; BestXIPosition = club_vue_ensemble)
AIGUILLER_AUSSI = ["PlayerShirtAndInitialSurnameCell", "TrainingIntensityAtRiskPlayerRow", "PortalPlayerHeader",
                   "PortalLoanReportBlock", "PortalDomesticRoundupBlock"]
# (2026-11-12, le joueur : fiche « pas chez toi » depuis la carte d'un message de transfert) : nom = SIText lié
# directement à <personne>.Name (lien riche, pas un modèle de LIENS) -> aiguillé aussi.
# modèle : (chemin du texte, personne ; None = paramètre personne du modèle). Tour d'horizon : la personne vient d'un
# BindingRemapper (keyplayer.Player -> person) au-dessus du texte, pas des paramètres.
TEXTES_NOM = {"PortalPlayerHeader": ("person.name", None), "PortalLoanReportBlock": ("player.name", None),
              "PortalDomesticRoundupBlock": ("person.name", "person")}
NOM_AIGUILLAGE = f"UIPickerContexteAiguillage-v{VERSION_AIGUILLAGE}"
NOM_RELAIS_V4 = f"UIPickerContexteRelais-v{VERSION_AIGUILLAGE}"
TYPE_PERSONNE = 1145176065
SOURCE_AIGUILLAGE = ("PlayerRecommendationsMainBlock", "IsMessageSwitch")   # BindableSwitchElement booléen de FM
SOURCE_RELAIS = "PlayerKitNamePlayingTimeCell"     # son BindingRemapper (player -> Person) : élément remapper de FM
SOUPLE = {"flex-shrink": 1, "min-width": 0}         # les deux enveloppes laissent le nom se rogner (« … »)


def defaire_relais(tt):
    """retire le relais v2 (contenu remis à la racine) ; True si retiré"""
    from arbre import Tree
    from elements import move
    t = Tree(tt)
    racine = tt["m_VisualTree"]["rid"]
    w = next((k for k in t.children(racine) if VERSION_RELAIS in (t.elem(k).get("m_Classes") or [])), None)
    if w is None:
        return False
    i = t.children(racine).index(w)
    for n, k in enumerate(t.children(w)):
        move(t, k, racine, i + n)
    t.remove(w)
    t.finish()
    return True


def equipe_porteur(tt, nom, chemin):
    """ajoute reportcontextteam -> <chemin>.Team au BindingRemapper nommé ; True si ajouté"""
    from arbre import Tree
    t = Tree(tt)
    rm = next((r for r in t.walk() if t.name(r) == nom and isinstance(t.sd(r).get("Mappings"), list)), None)
    if rm is None:
        return None
    maps = t.sd(rm)["Mappings"]
    if any(m.get("from") == CONTEXTE for m in maps):
        return False
    maps.append({"m_serialisedType": 0, "from": CONTEXTE, "to": {"m_path": f"{chemin}.Team"}, "type": {"id": TYPE_EQUIPE}})
    return True


def var_personne(tt):
    """nom du paramètre « personne » de la case (binding, person…), ou None"""
    for params in listes(tt):
        for p in params:
            if p.get("type", {}).get("id") == TYPE_PERSONNE and p["name"] != "human":
                return p["name"]
    return None


_sources = {}


def sources():
    """(arbre, rid) de l'aiguillage et du remapper modèles de FM, ou None"""
    if not _sources:
        from elements import src_tree, first
        s = src_tree(SOURCE_AIGUILLAGE[0])
        sw = s and first(s, lambda r: s.name(r) == SOURCE_AIGUILLAGE[1] and len(s.children(r)) == 2)
        m = src_tree(SOURCE_RELAIS)
        rm = m and first(m, lambda r: (m.elem(r).get("m_FullTypeName") or "").endswith("BindingRemapper")
                         and isinstance(m.sd(r).get("Mappings"), list))
        _sources["v"] = (s, sw, m, rm) if None not in (s, sw, m, rm) else None
    return _sources["v"]


def classes_flex(t, r):
    return [c for c in t.elem(r).get("m_Classes") or [] if "flex-grow" in c or c.startswith("align-self")]


def defaire_v4(tt):
    """retire l'aiguillage v4 (lien d'origine remis à sa place) ; nombre retiré"""
    from arbre import Tree
    from elements import move
    t = Tree(tt)
    vieux = [r for r in t.walk() if t.name(r) == NOM_AIGUILLAGE_V4]
    for sw in vieux:
        par = t.parent[sw]
        i = t.children(par).index(sw)
        ta = t.children(sw)[0]          # enfant 0 = le lien d'origine (branche « faux »)
        move(t, ta, par, i)
        t.remove(sw)
    if vieux:
        t.finish()
    return len(vieux)


def calcul_mon_club(t, par, i, p):
    """BindingSetter de FM (VAR_MON_CLUB = human.Club.Teams contient <p>.Team, défaut faux) sous par ; rid ou None"""
    import entrainement_equipes as ee
    s = ee._sources_club()
    if s is None:
        return None
    sc, calc, fn, _, _ = s
    f = copy.deepcopy(fn)
    args = ee.decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    attendu = ["BooleanVisualArg", "BindingPath]", "BindingPath]", "BooleanVisualArg", "BindingPath]"]
    if len(args) != len(attendu) or any(not bytes(a[0]).endswith(x.encode()) for a, x in zip(args, attendu)):
        return None
    for a, v in zip(args, [b"\x00", ee._chemin_arg("human.Club.Teams"), ee._chemin_arg(f"{p}.Team"), None,
                           ee._chemin_arg(VAR_MON_CLUB)]):
        if v is not None:
            a[1] = v
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = ee.encode_args(args)
    haut = t.clone(calc, par, i, src=sc)
    ee._vide(t, haut)
    sd = t.sd(haut)
    sd["name"], sd["name_UxmlAttributeFlags"] = NOM_CALCUL, 1
    sd["ValueVariables"] = [{"m_name": VAR_MON_CLUB, "m_scopeValue": {"m_serializedData": "Bool|0|"}}]
    sd["ReferenceVariables"] = []
    sd["ValueVariables_UxmlAttributeFlags"] = sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    sd["BindFunction"], sd["BindFunction_UxmlAttributeFlags"] = [f], 1
    return haut


def aiguiller(bundle, tt):
    """liens de nom de la case dans l'aiguillage « joueur de ton club » ; nombre de liens posés (0 : déjà fait / rien)"""
    from arbre import Tree, Styles
    from elements import move
    src = sources()
    texte, p = TEXTES_NOM.get(tt.get("m_Name"), (None, None))
    p = p or var_personne(tt)
    if src is None or p is None or tt.get("m_Name") in PAS_DEDANS:
        return 0
    s, sw0, m, rm0 = src
    t = Tree(tt)
    if any(t.name(r) == NOM_AIGUILLAGE for r in t.walk()):
        return 0
    if texte:   # seulement le nom de la personne (pas les liens de club du même bloc)
        liens = [r for r in t.walk() if (((t.sd(r) or {}).get("TextBinding") or {}).get("m_direct") or {})
                 .get("Path", {}).get("m_path", "").lower() == texte]
    else:
        liens = [r for r in t.walk() if t.elem(r).get("m_TemplateAlias") in LIENS]
    if not liens:
        return 0
    try:
        t.styles = Styles(bundle, tt)
    except (KeyError, StopIteration):   # case sans feuille intégrée : enveloppes sans style
        t.styles = None
    for ta in liens:
        par = t.parent[ta]
        i = t.children(par).index(ta)
        flex = classes_flex(t, ta)
        haut = calcul_mon_club(t, par, i, p)
        if haut is None:
            return 0      # morceaux de FM introuvables : rien d'écrit (t non sauvé)
        sw = t.clone(sw0, haut, 0, src=s)
        for k in list(t.children(sw)):
            t.remove(k)
        d = t.sd(sw)
        d["name"], d["name_UxmlAttributeFlags"] = NOM_AIGUILLAGE, 1
        d["Binding"]["m_direct"]["Path"]["m_path"] = VAR_MON_CLUB
        d["AlwaysInstantiate"] = 0
        rm = t.clone(rm0, sw, 0, src=m)
        for k in list(t.children(rm)):
            t.remove(k)
        t.sd(rm)["name"], t.sd(rm)["name_UxmlAttributeFlags"] = NOM_RELAIS_V4, 1
        t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": CONTEXTE, "to": {"m_path": f"{p}.Team"},
                                 "type": {"id": TYPE_EQUIPE}}]
        for r in (haut, sw, rm):
            t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = list(flex), -1
            if t.styles:
                t.styles.style(t, r, SOUPLE)
        t.clone(ta, rm)          # vrai (enfant 1) : le lien sous le remapper
        move(t, ta, sw, 0)       # faux (enfant 0) : le lien d'origine
    t.finish()
    if t.styles:
        t.styles.save()
    return len(liens)


def defaut():
    return {"m_kind": 1, "Path": {"m_path": DEFAUT}, "m_scopeValue": {"m_serializedData": ""}}


def listes(tt):
    """listes Parameters (BindingExpect / BindingExpectComponent) du modèle"""
    return [d["Parameters"] for d in (r.get("data") or {} for r in tt["references"]["RefIds"])
            if isinstance(d.get("Parameters"), list) and d["Parameters"]]


def regler(tt, ajouter):
    """nombre de paramètres posés ; ajouter : paramètre ajouté aux listes qui ne l'ont pas"""
    n = 0
    for params in listes(tt):
        p = next((x for x in params if x["name"] == CONTEXTE), None)
        if p is None:
            if not ajouter:
                continue
            p = copy.deepcopy(params[0])
            p.update({"m_serialisedType": 0, "name": CONTEXTE, "type": {"id": TYPE_EQUIPE}, "isOptional": 1})
            params.append(p)
        elif not p.get("isOptional") or (p.get("defaultValue") or {}).get("Path", {}).get("m_path") == DEFAUT:
            continue   # obligatoire (donné par FM) ou déjà réglé
        p["defaultValue"] = defaut()
        n += 1
    return n


def fait(tt):
    return any(x["name"] == CONTEXTE and (x.get("defaultValue") or {}).get("Path", {}).get("m_path") == DEFAUT
               for params in listes(tt) for x in params)


def modeles(name):
    """[(bundle, objet, typetree)] : toutes les copies du modèle (certains noms existent dans les deux bundles)"""
    res = []
    for bundle in nb.BUNDLES:
        for o in nb.env_of(bundle).objects:
            if o.type.name != "MonoBehaviour":
                continue
            try:
                if o.peek_name() != name:
                    continue
            except Exception:
                continue
            tt = o.read_typetree()
            if "m_VisualTree" in tt:
                res.append((bundle, o, tt))
    return res


def cmd_appliquer():
    total = defaits = porteurs = aiguilles = 0
    if sources() is None:
        print("aiguillage « joueur de ton club » : modèles de FM introuvables (le jeu a changé ?), liens inchangés")
    for model in AVEC_PARAMETRE + SANS_PARAMETRE:
        copies = modeles(model)
        if not copies:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        posees = 0
        for bundle, obj, tt in copies:
            n = regler(tt, model in SANS_PARAMETRE)
            d = defaire_relais(tt) + defaire_v4(tt)
            a = aiguiller(bundle, tt)
            aiguilles += a
            if n or d or a:
                obj.save_typetree(tt)
                nb._ecrits[(bundle, obj.path_id)] = tt
                nb._dirty.add(bundle)
                posees += n
                defaits += d
        total += posees
        if not posees and not any(fait(tt) for _, _, tt in copies):
            print(f"{model} : paramètre {CONTEXTE} introuvable, ignoré")
    for model, nom, chemin in PORTEURS:
        copies = modeles(model)
        for bundle, obj, tt in copies:
            r = equipe_porteur(tt, nom, chemin)
            if r is None:
                print(f"{model} : bloc {nom} introuvable (le jeu a changé ?), ignoré")
            elif r:
                obj.save_typetree(tt)
                nb._ecrits[(bundle, obj.path_id)] = tt
                nb._dirty.add(bundle)
                porteurs += 1
                print(f"{model} : fiche vue depuis l'équipe du joueur")
        if not copies:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
    if total:
        print(f"{total} case(s) joueur : équipe de la fiche par défaut = {DEFAUT}")
    if defaits:
        print(f"{defaits} case(s) joueur : ancien relais d'équipe retiré")
    for model in AIGUILLER_AUSSI:
        for bundle, obj, tt in modeles(model):
            d = defaire_v4(tt)
            a = aiguiller(bundle, tt)
            if a or d:
                obj.save_typetree(tt)
                nb._ecrits[(bundle, obj.path_id)] = tt
                nb._dirty.add(bundle)
                aiguilles += a
    if aiguilles:
        print(f"{aiguilles} lien(s) de nom : fiche vue depuis l'équipe du joueur quand il est dans ton club")
    if total or defaits or porteurs or aiguilles:
        nb.save_all()
    else:
        print("fiche complète de tes joueurs : déjà appliqué")
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    """remet les modèles d'origine puis refait tout le reste du skin (qui touche les mêmes fichiers)"""
    import lancer
    lancer.retirer_par_restauration(MARKER)
    print("\nCases joueur d'origine remises.")


def cmd_etat():
    for model in AVEC_PARAMETRE + SANS_PARAMETRE:
        copies = modeles(model)
        rel = any(VERSION_RELAIS in json.dumps(tt["references"]) for _, _, tt in copies)
        aig = any(NOM_AIGUILLAGE in json.dumps(tt["references"]) for _, _, tt in copies)
        print(f"{model} : " + ("introuvable" if not copies else "réglé" if any(fait(tt) for _, _, tt in copies)
                               else "d'origine") + (", ancien relais v2" if rel else "")
              + (f", liens aiguillés v{VERSION_AIGUILLAGE}" if aig else ""))
    for model, nom, chemin in PORTEURS:
        ok = any(equipe_porteur(copy.deepcopy(tt), nom, chemin) is False for _, _, tt in modeles(model))
        print(f"{model} : " + ("fiche vue depuis l'équipe du joueur" if ok else "d'origine"))
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
    elif op == "si-actif":   # utilisé par le menu après une mise à jour
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("fiche complète de tes joueurs : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
