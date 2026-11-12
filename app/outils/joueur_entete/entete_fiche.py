"""En-tête de la fiche joueur (bannière large / moyenne) : 2e nationalité, Pour / Contre en pastilles (mode Défaut),
Niveau / Potentiel serrés, bloc valeur moins large.

- nationalité(s) secondaire(s) juste à droite de la nationalité, en toutes lettres (rien s'il n'y en a pas) ;
- mode Défaut seulement : à droite du Potentiel, un trait puis les pastilles (Pour en haut, Contre en bas ; chaque
  liste sur 1 ou 2 rangées, option pour_contre_lignes) ;
  pastille = ProConRow (cellule FM inutilisée) réécrite ici par le moteur commun\\pastilles_pour_contre.py (même
  pastille que l'infobulle, en plus grand : PASTILLE_BANDEAU / LOGO_BANDEAU, couleurs NUANCES) ;
- Niveau actuel / Potentiel à la largeur de leur contenu ; bloc valeur / salaire moins large ;
- mode Large seulement : bouton Actions sous la nationalité / l'âge (à droite de la photo).

Repérage par contenu (noms FM, chemins de données) : valable après une mise à jour du jeu.
Usage (jeu fermé) : entete_fiche.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import (Tree, named, make_visible, polygon_visible,  # noqa: E402,F401
                   polygon_button, CLASSE_SI_POLYGONE, Styles, no_styles,
                   LARGEUR_MAX, MOITIE, FIXE, PROPRIETES)
from elements import (src_tree, add_using, copy_usings, first, typ, move, plain, visible_model,  # noqa: E402,F401
                      action_buttons, set_text_binding, appliquer_jobs)
import lancer  # noqa: E402  (retirer : modèles d'origine remis puis tout le skin refait)
import pastilles_pour_contre as ppc  # noqa: E402  (pastille ProConRow de l'en-tête)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (True = activé, False = désactivé)
# =====================================================================================================
DEUXIEME_NATIONALITE = True                 # en-tête de la fiche joueur
BANDEAU_POUR_CONTRE = True                   # en-tête de la fiche, mode Défaut : pastilles Pour / Contre à droite
                                             # du Potentiel (2 lignes) ; la pastille vient de infobulle_pour_contre
BANDEAU_PC_MARGE = 32                        # ... px laissés à droite (v1 : 0, collé au bord de l'écran)
# ... pastilles max par rangée et rangées max par liste (Pour, Contre ; le reste est caché), selon l'option
# pour_contre_lignes (v8) : « 2 » (de base) = 7 par rangée puis rangée suivante ; « 1 » = une rangée de 10 (comme v6)
BANDEAU_PC_DISPOSITION = {"2": (7, 2), "1": (10, 1)}
OPTION_LIGNES = "pour_contre_lignes"
NIVEAU_POTENTIEL_SERRE = True                # en-tête : Niveau actuel / Potentiel à la largeur de leur contenu
                                             # (FM : largeur fixe, grand vide à droite des étoiles ; tous modes)
VALEUR_LARGEUR_MIN = (180, 150)               # en-tête : largeur min. du bloc valeur / salaire (bandeau large,
                                             # moyen ; FM : 220, 180 ; None = FM)
ACTIONS_SOUS_L_AGE = True                    # en-tête, mode Large seulement : bouton Actions sous nationalité / âge
NATIONS_COURTES_LARGE = True                 # en-tête, mode Large seulement : nationalités en 3 lettres (ESP, FRA)
RAPPORT_LETTRE_LARGE = True                  # en-tête, mode Large seulement : rapport de supervision = la lettre
                                             # (B+) + libellé court de FM, sans la phrase (« Jeune très
                                             # prometteur… »), trop longue
MOT_CLE_AUTO = 2                             # StyleValueKeyword.Auto
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "entete_fiche.actif")
BANNIERES = ["report-player-banner-max", "report-player-banner-mid"]
NOM_NATIONALITES = "UIPickerNationalites"
RAPPORT = "Person.PlayerReportForContextTeam"
# 2e nationalité écrite comme la 1re (nom complet) : cellules FM inutilisées réécrites (vérifié : citées par aucun
# modèle), une par bannière selon le modèle de la 1re nationalité : modèle inclus -> (cellule, GUID de la cellule)
TYPE_NATION = 1145176074
NOM_CELLULE_NATION = "UIPickerCelluleNation"
CELLULES_NATION = {"nation-cell-medium-bold": ("NationalityCell", "63ed9c253547d184ea5e858f9a7cbfa9"),   # bannière large
                   "nation-cell-medium": ("NationalitiesEligibilityClubCell", "c08f851738f589c48885e875492b128d")}
USINGS_NATION = {"nation-cell-medium-bold": "7632e7e4579e2c1489980c05ee07a872",
                 "nation-cell-medium": "c73088b9c5038f94f821ad13d945a8ba"}
PREFIXE_BANDEAU_PC = "UIPickerBandeauPourContre"
import options  # noqa: E402
LIGNES_PC = options.get(OPTION_LIGNES)
# option de fiche_joueur_plus (2026-10-30, le joueur) : Pour / Contre dans la fiche en Large -> plus de pastilles ici
# 2026-11-05 (le joueur) : en-tête en grande tuile = jamais de pastilles ici (ni pour_contre_lignes ni
# fiche_large_colonne ne passent avant la tuile)
# 2026-11-07 (le joueur) : mode FM Guru = en-tête de FM avec les pastilles, toujours (ces options n'y jouent pas)
GURU = options.get("fiche_fmguru") == "guru"
SANS_PASTILLES = not GURU and (options.get("fiche_large_colonne") == "pour_contre"
                               or options.get("entete_vue") == "tuile")
# changer le numéro (ou l'option) refait le bloc ; v8 : la rangée de l'en-tête garde sa hauteur (traits pas allongés)
NOM_BANDEAU_PC = PREFIXE_BANDEAU_PC + ("-v9-sans" if SANS_PASTILLES else f"-v9-{LIGNES_PC}l") + ("-guru" if GURU else "")
GUID_PASTILLE = "1d9ea6f83e853594c9a3339ba036281b"   # ProConRow, réécrite ici (v3 : 1fcf53e2… = celle de l'infobulle, 22 px)
NOM_ACTIONS_LARGE = "UIPickerActionsLarge-v1"           # copie du bouton Actions sous l'âge (Large)
NOM_ACTIONS_AUTRES = "UIPickerActionsMediumSmall"       # l'original, gardé en Medium / Small
NOM_NATIONS_LARGE = "UIPickerNationsCourtesLarge-v1"    # nationalités en 3 lettres (Large)
NOM_NATIONS_AUTRES = "UIPickerNationsMediumSmall"       # en toutes lettres (Medium / Small)
MODELE_RAPPORT = "PlayerReportHeaderScoutSection"       # bloc « Rapport de supervision » de l'en-tête
NOM_PHRASE_RAPPORT = "UIPickerRapportPhraseMediumSmall-v1"   # la phrase, gardée en Medium / Small
NOM_RAPPORT_COURT_LARGE = "UIPickerRapportCourtLarge-v2"      # libellé court de FM (« Excellent »), Large
BANDEAU_PC_PASTILLE = 28                   # taille de cette pastille (PASTILLE_BANDEAU de pastilles_pour_contre)
# 2026-11-05 (le joueur) : carte « identité » à droite de la photo (nom, n°, poste, nationalité, âge, taille), tous
# modes ; en Medium, polygone juste après la carte (le bouton du polygone de la colonne Pour / Contre est caché en
# Medium par fiche_joueur_plus)
# 2026-11-05 (le joueur, 3e retour) : « vire la carte mais garde l'idée du polygone » -> carte défaite si présente,
# polygone gardé à droite du bloc du nom
CARTE_IDENTITE = False
NOM_CARTE = "UIPickerCarteIdentite-v1"
# v4 (le joueur : « un poil plus grand ») : 280×150 / 30 % -> 300×160 / 36 % ; v5 (« encore plus grand ») : 340×200 / 46 %
NOM_POLYGONE_ENTETE = "UIPickerPolygoneEntete-v5"
POLYGONE_ENTETE = not GURU   # mode FM Guru : le polygone est dans la fiche (pas en double dans l'en-tête)
POLYGONE_ENTETE_TAILLE = (340, 200)          # px (largeur, hauteur) de la zone du polygone dans l'en-tête (Medium)
POLYGONE_ENTETE_RAYON = 46.0               # % (FM : 34.8 ; étiquettes 10 px de la vue Guru)
CARTE_FOND, CARTE_BORD = (1.0, 1.0, 1.0, 0.045), (1.0, 1.0, 1.0, 0.12)
CARTE_RAYON, CARTE_MARGE = 10, (8, 16)      # px : coins, marges intérieures (haut / bas, gauche / droite)
for _k, _v in {"padding-top": (131101, 3), "padding-bottom": (131098, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "border-top-color": (458763, 4), "border-bottom-color": (458758, 4),
               "border-left-color": (458761, 4), "border-right-color": (458762, 4),
               "border-top-left-radius": (458764, 3), "border-top-right-radius": (458765, 3),
               "border-bottom-left-radius": (458759, 3), "border-bottom-right-radius": (458760, 3),
               "width": (131105, 3), "height": (131087, 3), "margin-left": (131091, 3), "margin-right": (131092, 3),
               "margin-top": (131093, 3), "align-self": (131074, 7)}.items():
    PROPRIETES.setdefault(_k, _v)


def appliquer():
    if BANDEAU_POUR_CONTRE and ppc.PASTILLE_BANDEAU:   # la pastille (ProConRow, repart de l'original), puis l'en-tête
        ppc.appliquer([ppc.CELLULE_BANDEAU], MARKER)
    appliquer_jobs(jobs(), MARKER)


# ---------- 2. deuxième nationalité ----------
def nation_cell(cellule, alias):
    """réécrit une cellule FM inutilisée (ComponentElement > BindingExpect + BindingRemapper + modèle inclus) en
    ligne de liste de nationalités : paramètre binding = nation, texte = nom complet, modèle FM alias (v2 : la
    nationalité secondaire s'écrit comme la 1re de la bannière, plus « ITA » de NationCellShort)"""
    def fn(t):
        if named(t, NOM_CELLULE_NATION):
            return []
        comp = first(t, lambda r: typ(t, r) == "SI.UI.ComponentElement")
        inc = first(t, lambda r: t.elem(r).get("m_TemplateAlias"))
        if comp is None or inc is None:
            return [f"{cellule} : structure inattendue (introuvable), ignoré"]
        ids = {c["rid"] for c in t.sd(comp)["m_components"]}
        refs = {r["rid"]: r for r in t.tt["references"]["RefIds"]}
        expect = next((refs[i]["data"] for i in ids if "Parameters" in refs[i]["data"]), None)
        remap = next((refs[i]["data"] for i in ids if "Mappings" in refs[i]["data"]), None)
        if expect is None or remap is None:
            return [f"{cellule} : composants introuvables, ignoré"]
        p = expect["Parameters"][0]
        p["name"], p["type"]["id"], p["isOptional"] = "binding", TYPE_NATION, 0
        del expect["Parameters"][1:]
        remap["Mappings"] = [
            {"m_serialisedType": 0, "from": "nation", "to": {"m_path": "binding"}, "type": {"id": TYPE_NATION}},
            {"m_serialisedType": 0, "from": "primarytext", "to": {"m_path": "nation.Name"}, "type": {"id": 0}}]
        for e in t.tt["references"]["RefIds"]:   # textes de débogage des composants (affichage UI Builder)
            for prop in (e.get("data") or {}).get("m_Properties") or []:
                if prop.get("name") == "params":
                    prop["value"] = "binding:nation:False"
                elif prop.get("name") == "mappings":
                    prop["value"] = "nation:binding:nation,primarytext:nation.Name:invalid"
        t.elem(inc)["m_TemplateAlias"] = alias
        t.sd(inc)["templateId"] = alias
        t.tt["m_Usings"] = [{"alias": alias, "path": USINGS_NATION[alias], "asset": {"m_FileID": 0, "m_PathID": 0}}]
        t.elem(comp)["m_Classes"] = ["margin-left-global-gap-small"]
        sd = t.sd(comp)
        sd["name"], sd["name_UxmlAttributeFlags"] = NOM_CELLULE_NATION, 1
        return [f"cellule réécrite : nationalité en toutes lettres ({alias})"]
    return fn


def second_nationality(t):
    old = named(t, NOM_NATIONALITES)
    if old:   # déjà posée : seulement mettre la liste sur la cellule « nom complet » (v2)
        lst = next((r for r in t.walk(old[0]) if typ(t, r).endswith("StreamedObjectList")), None)
        bold = any(t.elem(r).get("m_TemplateAlias") == "nation-cell-medium-bold" for r in t.walk(old[0]))
        guid = CELLULES_NATION["nation-cell-medium-bold" if bold else "nation-cell-medium"][1]
        if lst is None or t.sd(lst)["RowTemplate"]["m_AssetGUID"] == guid:
            return []
        t.sd(lst)["RowTemplate"]["m_AssetGUID"], t.sd(lst)["RowParamName"] = guid, "binding"
        t.elem(lst)["m_Classes"] = ["row-direction-normal"]
        return ["nationalité(s) secondaire(s) en toutes lettres"]
    # la nationalité de l'encadré "sélection" : la cellule nation placée dans une colonne
    nat = first(t, lambda r: typ(t, r) == "SI.Bindable.BindingRemapper"
                and any((m.get("to") or {}).get("m_path", "").lower() == "person.nation" for m in t.sd(r).get("Mappings") or [])
                and "column-direction-normal" in (t.elem(t.parent[r]).get("m_Classes") or []))
    s = src_tree("PersonPersonalBlock")
    lst = first(s, lambda r: s.name(r) == "SecondaryNationalitiesList") if s else None
    if nat is None or lst is None:
        return ["nationalité ou liste des nationalités introuvable, ignoré"]
    col = t.parent[nat]
    row = plain(t, col, t.children(col).index(nat), ["row-direction-normal", "align-items-start"], NOM_NATIONALITES)
    move(t, nat, row)
    new = t.clone(lst, row, src=s)
    t.sd(new)["name"] = ""
    t.elem(new)["m_Classes"] = ["row-direction-normal"]   # écart : marge de la cellule
    alias = t.elem(t.children(nat)[0]).get("m_TemplateAlias") if t.children(nat) else None
    guid = CELLULES_NATION["nation-cell-medium-bold" if alias == "nation-cell-medium-bold" else "nation-cell-medium"][1]
    t.sd(new)["RowTemplate"]["m_AssetGUID"], t.sd(new)["RowParamName"] = guid, "binding"
    return ["nationalité(s) secondaire(s) à droite de la nationalité, en toutes lettres"]


def banner_pros_cons(t):
    """en-tête de la fiche, mode Défaut seulement : à droite de Niveau actuel / Potentiel, un trait puis 2 lignes de
    pastilles (Pour en haut, Contre en bas) = cellule de infobulle_pour_contre (couleur selon la note, texte au survol)"""
    if named(t, NOM_BANDEAU_PC):
        return []
    old = [r for r in t.walk() if t.name(r).startswith(PREFIXE_BANDEAU_PC)]
    for r in old:
        t.remove(r)
    import notes_installations as ni
    from hierarchie_pyramide import path_arg
    scout = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "PlayerReportHeaderScoutSection")
    bloc, rangee = scout, scout is not None and t.parent[scout]
    while rangee is not None and not any(t.elem(k).get("m_TemplateAlias") == "layout-divider-solid-vertical"
                                         for k in t.children(rangee)):
        bloc, rangee = rangee, t.parent.get(rangee)
    trait = rangee and first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical")
    s, vis = ni.visible_model()
    lst = src_tree("TeamMeetingBlock")
    liste = lst and next((r for r in lst.walk() if lst.name(r) == "Players"
                          and typ(lst, r).endswith("WrappedObjectList")), None)
    if not (rangee and trait and vis is not None and liste is not None):
        return ["niveau / potentiel, trait ou liste introuvable : Pour / Contre du bandeau non posés"]
    if VALEUR_LARGEUR_MIN:   # bloc valeur / salaire : FM min-width 220 (max) / 180 (mid), vide à droite du texte
        val = first(t, lambda r: "TransferValueRangeString" in str(t.sd(r).get("TextBinding") or ""))
        while val is not None and t.parent.get(val) != rangee:
            val = t.parent.get(val)
        if val is not None:
            t.styles.style(t, val, {"min-width": VALEUR_LARGEUR_MIN[0 if "max" in t.name(first(
                t, lambda r: t.name(r).startswith("report-player-banner")) or "") else 1]})
    if NIVEAU_POTENTIEL_SERRE:   # FM : largeur fixe 260 px (max) / 200 px (mid), grand vide après les étoiles
        t.styles.style(t, bloc, {"width-mot-cle": MOT_CLE_AUTO})
    if SANS_PASTILLES:   # juste une marque vide (« déjà appliqué »), sans taille
        m = plain(t, rangee, None, [])
        t.elem(m)["m_RuleIndex"] = -1
        t.sd(m)["name"], t.sd(m)["name_UxmlAttributeFlags"] = NOM_BANDEAU_PC, 1
        t.styles.style(t, m, {"position": "absolute", "width": 0, "height": 0})
        return ["pas de pastilles Pour / Contre dans l'en-tête (elles sont dans la fiche en Large)"
                + (" (retirées)" if old else "")]
    # visible seulement en mode Défaut (settings.AdaptiveScalingLevelIndex == 0) ; mode FM Guru (2026-11-07, le
    # joueur : « comme sur mes vues ») : aussi en Medium (index < 2)
    cond = (ni.make_binding(s.sd(vis)["Binding"], 0, ["settings.AdaptiveScalingLevelIndex"], 2) if GURU else
            ni.equal_binding(s.sd(vis)["Binding"], "settings.AdaptiveScalingLevelIndex", 0))
    box = ni.new_visible(t, s, vis, rangee, t.children(rangee).index(bloc) + 1, NOM_BANDEAU_PC, cond,
                         ["row-direction-normal", "align-items-center"])
    t.sd(box)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, box, {"align-self": "stretch", "flex-shrink": 0, "margin-right": BANDEAU_PC_MARGE})
    d = t.clone(trait, box)
    t.sd(d)["name"] = ""
    t.elem(d)["m_Classes"] = ["margin-left-global-gap-regular", "margin-right-global-gap-regular",
                              "align-self-stretch-class"]
    # v9 : zone de largeur fixe (la place des pastilles), pastilles en position absolute dedans (hauteur 100 %,
    # centrées, elles débordent en haut et en bas, visibles) : elles ne comptent plus dans la taille de la rangée,
    # les traits gardent leur hauteur (v7 : 4 rangées = 143 px au lieu de 81 ; v8, boîte de hauteur 0 : en-tête
    # entier écrasé à gauche en jeu)
    par_rangee, rangees = BANDEAU_PC_DISPOSITION.get(LIGNES_PC, BANDEAU_PC_DISPOSITION["2"])
    pas = BANDEAU_PC_PASTILLE + 2   # pastille 22 px + marges 1 px (infobulle_pour_contre)
    zone = plain(t, box, None, [])
    t.elem(zone)["m_RuleIndex"] = -1
    t.styles.style(t, zone, {"width": par_rangee * pas, "min-width": par_rangee * pas, "flex-shrink": 0,
                             "align-self": "stretch"})
    col = plain(t, zone, None, ["column-direction-normal", "justify-content-center"])
    t.elem(col)["m_RuleIndex"] = -1
    t.styles.style(t, col, {"position": "absolute", "left": 0, "top": 0, "width": {"unit": 2, "value": 100.0},
                            "height": {"unit": 2, "value": 100.0}})
    for chemin in (RAPPORT + ".ScoutedProConsList.ProsList", RAPPORT + ".ScoutedProConsList.ConsList"):
        w = t.clone(liste, col, src=lst)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": GUID_PASTILLE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], chemin)
        sd["ItemParamName"] = "procon"
        sd["ItemUssClassName"] = "flex-no-shrink-class"   # v5 : sinon les pastilles rétrécissent et se chevauchent
        t.elem(w)["m_Classes"] = []
        # v7 : trop de pastilles -> rangée suivante (au lieu d'élargir le bloc et serrer le reste de l'en-tête)
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "wrap" if rangees > 1 else "nowrap",
                              "overflow": "hidden", "max-width": par_rangee * pas, "min-height": pas,
                              "max-height": rangees * pas, "flex-shrink": 0})
    return [("Pour / Contre en pastilles à droite du Potentiel (Large + Medium, mode FM Guru)" if GURU else
             "Pour / Contre en pastilles à droite du Potentiel (mode Défaut)") + (" (refait)" if old else "")]

def actions_large(t):
    """mode Large seulement : bouton Actions (FrameActions) sous la nationalité / l'âge, à droite de la photo ;
    l'original (colonne des drapeaux de statut) reste en Medium / Small"""
    if named(t, NOM_ACTIONS_LARGE):
        return []
    import notes_installations as ni
    fa =first(t, lambda r: t.name(r) == "FrameActions")
    nom = first(t, lambda r: "person.Name" in str(t.sd(r).get("TextBinding") or ""))
    col = nom   # colonne nom / nationalité / âge (bannière moyenne : le nom est un niveau plus bas)
    while col is not None and not {"column-direction-normal", "align-items-start"} <= set(t.elem(col).get("m_Classes") or []):
        col = t.parent.get(col)
    s, vis = ni.visible_model()
    if fa is None or not col or vis is None:
        return ["bouton Actions ou colonne du nom introuvable : Actions non déplacé"]
    mode = "settings.AdaptiveScalingLevelIndex"
    haut = t.parent[fa]
    autres = ni.new_visible(t, s, vis, haut, t.children(haut).index(fa), NOM_ACTIONS_AUTRES,
                            ni.make_binding(s.sd(vis)["Binding"], 4, [mode], 0))   # Medium / Small : > 0
    t.sd(autres)["name_UxmlAttributeFlags"] = 1
    move(t, fa, autres)
    large = ni.new_visible(t, s, vis, col, None, NOM_ACTIONS_LARGE, ni.equal_binding(s.sd(vis)["Binding"], mode, 0),
                           ["row-direction-normal", "margin-top-global-gap-regular"])
    t.sd(large)["name_UxmlAttributeFlags"] = 1
    c = t.clone(fa, large)
    t.sd(c)["name"] = ""
    return ["bouton Actions sous nationalité / âge (mode Large)"]


def nations_courtes_large(t):
    """mode Large seulement : nationalités en 3 lettres (ESP, FRA) dans l'en-tête, la place manque (bouton Actions
    sous l'âge) ; Medium / Small : en toutes lettres comme avant"""
    if named(t, NOM_NATIONS_LARGE):
        return []
    import notes_installations as ni
    row = named(t, NOM_NATIONALITES)
    s, vis = ni.visible_model()
    p = src_tree("PersonPersonalBlock")
    court = p and first(p, lambda r: p.name(r) == "SecondaryNationalitiesList")
    if not row or vis is None or court is None:
        return ["nationalités ou liste courte introuvables : nationalités en 3 lettres non posées"]
    row, mode = row[0], "settings.AdaptiveScalingLevelIndex"
    haut = t.parent[row]
    i = t.children(haut).index(row)
    autres = ni.new_visible(t, s, vis, haut, i, NOM_NATIONS_AUTRES,
                            ni.make_binding(s.sd(vis)["Binding"], 4, [mode], 0))   # Medium / Small : > 0
    move(t, row, autres)
    large = ni.new_visible(t, s, vis, haut, i + 1, NOM_NATIONS_LARGE, ni.equal_binding(s.sd(vis)["Binding"], mode, 0))
    for v in (autres, large):
        t.sd(v)["name_UxmlAttributeFlags"] = 1
    c = t.clone(row, large)
    t.sd(c)["name"] = ""
    for r in t.walk(c):
        sd = t.sd(r)
        for m in sd.get("Mappings") or []:
            if m["from"] == "primarytext":
                m["to"]["m_path"] = "nation.threelettername"
        if typ(t, r).endswith("StreamedObjectList"):
            sd["RowTemplate"] = dict(p.sd(court)["RowTemplate"])
            sd["RowParamName"] = p.sd(court)["RowParamName"]
    return ["nationalités en 3 lettres (mode Large)"]


def rapport_lettre_large(t):
    """mode Large seulement : rapport de supervision réduit à la lettre (icône gradinginfo.Grade) ; la phrase
    (gradinginfo.GradeString) reste en Medium / Small — passée ensuite en libellé court elle aussi (rapport_diminutif,
    2026-11-07)"""
    if named(t, NOM_RAPPORT_COURT_LARGE):
        return []
    import notes_installations as ni
    s, vis = ni.visible_model()
    mode = "settings.AdaptiveScalingLevelIndex"
    deja = named(t, NOM_PHRASE_RAPPORT)   # v1 déjà posée (lettre seule) : on ajoute le libellé court à côté
    if deja:
        autres = deja[0]
        phrase = next(iter(t.children(autres)), None)
    else:
        phrase = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "data_display-cell-standard-regular"
                       and "gradinginfo.GradeString" in str(t.elem(r)) + str(t.sd(r)))
        if phrase is None:   # repli : la cellule texte voisine de l'icône de la note
            bloc = first(t, lambda r: t.name(r) == "data_display-cell-non-cell-icon-and-string-regular")
            phrase = bloc and next((k for k in t.children(bloc)
                                    if t.elem(k).get("m_TemplateAlias") == "data_display-cell-standard-regular"), None)
    if phrase is None or vis is None:
        return ["phrase du rapport de supervision introuvable : laissée"]
    if not deja:
        haut = t.parent[phrase]
        autres = ni.new_visible(t, s, vis, haut, t.children(haut).index(phrase), NOM_PHRASE_RAPPORT,
                                ni.make_binding(s.sd(vis)["Binding"], 4, [mode], 0))   # Medium / Small : > 0
        t.sd(autres)["name_UxmlAttributeFlags"] = 1
        move(t, phrase, autres)
    # v2 (2026-11-06, le joueur) : en Large, le libellé court de FM (gradinginfo.ShortGradeString) au lieu de rien
    haut = t.parent[autres]
    large = ni.new_visible(t, s, vis, haut, t.children(haut).index(autres) + 1, NOM_RAPPORT_COURT_LARGE,
                           ni.equal_binding(s.sd(vis)["Binding"], mode, 0))
    t.sd(large)["name_UxmlAttributeFlags"] = 1
    c = t.clone(phrase, large)

    def court(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "m_path" and v == "gradinginfo.GradeString":
                    x[k] = "gradinginfo.ShortGradeString"
                else:
                    court(v)
        elif isinstance(x, list):
            for v in x:
                court(v)
    for r in t.closure(c):
        court(t.refs[r])
    if "ShortGradeString" not in str([t.refs[r] for r in t.closure(c)]):
        t.remove(large)
        return ["texte de la phrase du rapport introuvable : libellé court non posé (lettre seule en Large)"]
    return ["rapport de supervision : lettre + libellé court en mode Large"]


def colonne_nom(t):
    """colonne nom / poste / nationalité / âge de la bannière (1er ancêtre column + align-items-start du nom)"""
    col = first(t, lambda r: "person.Name" in str(t.sd(r).get("TextBinding") or ""))
    # v3 : la carte a les mêmes classes -> on la saute (sinon le polygone tombait dans la carte, sous le texte)
    while col is not None and (t.name(col) == NOM_CARTE or not {"column-direction-normal", "align-items-start"}
                               <= set(t.elem(col).get("m_Classes") or [])):
        col = t.parent.get(col)
    return col


def carte_identite(t):
    """2026-11-05 (le joueur) : le bloc à droite de la photo devient une carte (fond léger, bord, coins ronds) :
    nom + n°, poste, nationalité + âge, puis la taille (case « Taille » d'Infos recopiée de la fiche d'origine) ; le
    bouton Actions du mode Large reste sous la carte. Medium : polygone de la fiche juste après la carte"""
    if named(t, NOM_CARTE):
        # carte déjà là : polygone d'une ancienne version remplacé (l'en-tête ne repart pas de l'original)
        if not POLYGONE_ENTETE or named(t, NOM_POLYGONE_ENTETE):
            return []
        for r in [r for r in list(t.parent) if (t.name(r) or "").startswith("UIPickerPolygoneEntete-v")]:
            t.remove(r)
        col = colonne_nom(t)
        from attributs_tout_cocher import ouvrir
        o = ouvrir("PlayerAttributesLargeBlock", depart_original=True)
        return polygone_entete(t, col, o and o[3]) if col is not None else []
    col = colonne_nom(t)
    if col is None:
        return ["colonne du nom introuvable : carte identité non posée"]
    msgs = []
    carte = plain(t, col, 0, ["column-direction-normal", "align-items-start"])
    t.elem(carte)["m_RuleIndex"] = -1
    t.sd(carte)["name"], t.sd(carte)["name_UxmlAttributeFlags"] = NOM_CARTE, 1
    for k in list(t.children(col)):
        if k != carte and t.name(k) != NOM_ACTIONS_LARGE:
            move(t, k, carte)
    v, h = CARTE_MARGE
    t.styles.style(t, carte, {"background-color": CARTE_FOND,
                              **{f"border-{c}-width": 1 for c in ("top", "bottom", "left", "right")},
                              **{f"border-{c}-color": CARTE_BORD for c in ("top", "bottom", "left", "right")},
                              **{f"border-{c}-radius": CARTE_RAYON for c in ("top-left", "top-right", "bottom-left",
                                                                             "bottom-right")},
                              "padding-top": v, "padding-bottom": v, "padding-left": h, "padding-right": h,
                              "flex-shrink": 0})
    # taille : « Taille 192 cm » sur une ligne (case d'Infos de la fiche d'origine, texte traduit par FM)
    from attributs_tout_cocher import ouvrir
    o = ouvrir("PlayerAttributesLargeBlock", depart_original=True)
    src = o and o[3]
    hauteur = src and first(src, lambda r: src.name(r) == "PersonHeightTextFrame")
    if hauteur is not None:
        c = t.clone(hauteur, carte, src=src)
        t.styles.copy_from(src.styles, t, c)
        copy_usings(t, src, hauteur)
        t.sd(c)["name"] = ""
        t.elem(c)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-top-global-gap-small"]
        kids = t.children(c)
        if kids:
            t.elem(kids[0])["m_Classes"] = ["global-text-secondary", "body-sm", "margin-right-global-gap-small"]
        msgs.append("carte identité à droite de la photo (nom, n°, poste, nationalité, âge, taille)")
    else:
        msgs.append("carte identité à droite de la photo (taille introuvable dans la fiche d'origine)")
    if POLYGONE_ENTETE:
        msgs += polygone_entete(t, col, src)
    return msgs


CLASSES_TAILLE = ["row-direction-normal", "align-items-center", "margin-top-global-gap-small"]


def defaire_carte(t):
    """carte retirée : son contenu revient dans la colonne du nom à sa place, la ligne « Taille » ajoutée part"""
    carte = first(t, lambda r: t.name(r) == NOM_CARTE)
    if carte is None:
        return []
    col = t.parent[carte]
    i = t.children(col).index(carte)
    kids = []
    for k in list(t.children(carte)):   # ligne « Taille » et vieux polygone (v2, tombé dans la carte) retirés
        if t.elem(k).get("m_Classes") == CLASSES_TAILLE or (t.name(k) or "").startswith("UIPickerPolygoneEntete-v"):
            t.remove(k)
        else:
            kids.append(k)
    for j, k in enumerate(kids):
        move(t, k, col, i + j)
    t.remove(carte)
    return ["carte identité retirée (contenu remis à sa place)"]


def carte_ou_polygone(t):
    """carte d'identité (si CARTE_IDENTITE, polygone compris) ; sinon carte défaite et polygone seul"""
    if CARTE_IDENTITE:
        return carte_identite(t)
    msgs = defaire_carte(t)
    if not POLYGONE_ENTETE:
        vieux = [r for r in t.walk() if (t.name(r) or "").startswith("UIPickerPolygoneEntete-v")]
        for r in vieux:
            t.remove(r)
        return msgs + (["polygone de l'en-tête retiré (mode FM Guru)"] if vieux else [])
    if not named(t, NOM_POLYGONE_ENTETE):
        # t.walk() (pas t.parent : il garde les éléments retirés avec la carte)
        for r in [r for r in t.walk() if (t.name(r) or "").startswith("UIPickerPolygoneEntete-v")]:
            t.remove(r)
        col = colonne_nom(t)
        from attributs_tout_cocher import ouvrir
        o = ouvrir("PlayerAttributesLargeBlock", depart_original=True)
        msgs += polygone_entete(t, col, o and o[3]) if col is not None else ["colonne du nom introuvable : polygone non posé"]
    return msgs


def polygone_entete(t, col, src):
    """Medium seulement (settings.AdaptiveScalingLevelIndex == 1) : polygone de la fiche d'origine après la carte,
    zone fixe POLYGONE_ENTETE_TAILLE, réglé comme la vue Guru (étiquettes 10 px, anneaux) ; « player » = person"""
    import notes_installations as ni
    import fiche_fmguru as guru
    chart = src and first(src, lambda r: typ(src, r).endswith("FMSpiderChart"))
    rm_model = first(t, lambda r: typ(t, r).endswith("BindingRemapper"))
    s, vis = ni.visible_model()
    if None in (chart, rm_model, vis):
        return ["polygone de l'en-tête : éléments introuvables (le jeu a changé ?), ignoré"]
    haut = t.parent[col]
    box = ni.new_visible(t, s, vis, haut, t.children(haut).index(col) + 1, NOM_POLYGONE_ENTETE,
                         ni.equal_binding(s.sd(vis)["Binding"], "settings.AdaptiveScalingLevelIndex", 1),
                         ["column-direction-normal", "align-items-center", "justify-content-center"])
    t.sd(box)["name_UxmlAttributeFlags"] = 1
    w, h = POLYGONE_ENTETE_TAILLE
    t.styles.style(t, box, {"width": w, "min-width": w, "height": h, "flex-shrink": 0, "margin-left": 16})
    rm = t.clone(rm_model, box)
    for k in list(t.children(rm)):
        t.remove(k)
    t.sd(rm)["name"] = ""
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": "player", "to": {"m_path": "person"},
                             "type": {"id": 1145176065}}]
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = ["flex-grow-class", "align-self-stretch"], -1
    poly = t.clone(chart, rm, src=src)
    t.styles.copy_from(src.styles, t, poly)
    copy_usings(t, src, chart)
    sd = t.sd(poly)
    sd["SpiderChartRadiusPercentage"] = POLYGONE_ENTETE_RAYON
    sd["NumberOfInnerRings"] = guru.ANNEAUX_POLYGONE
    sd["LabelsTemplate"]["m_AssetGUID"] = guru.GUID_ETIQUETTES
    # v2 (le joueur : « mal placé ») : le polygone gardait la hauteur de la fiche (~260 px) dans une zone de 130 :
    # centre en bas de l'en-tête, moitié coupée -> taille de la zone imposée
    t.elem(poly)["m_Classes"] = [k for k in t.elem(poly)["m_Classes"]
                                 if k not in ("justify-content-end", "flex-grow-class", "align-self-stretch")]
    t.styles.style(t, poly, {"width": w, "min-width": w, "max-width": w, "height": h, "min-height": h,
                             "max-height": h, "flex-grow": 0, "flex-shrink": 0})
    t.styles.style(t, rm, {"width": w, "height": h, "flex-grow": 0, "flex-shrink": 0})
    t.elem(rm)["m_Classes"] = []
    return ["polygone dans l'en-tête, après la carte (mode Medium)"]


def jobs():
    # un seul passage par bannière : toutes ses retouches à la suite
    fns = [fn for ok, fn in ((DEUXIEME_NATIONALITE, second_nationality), (BANDEAU_POUR_CONTRE, banner_pros_cons),
                             (ACTIONS_SOUS_L_AGE, actions_large),
                             (DEUXIEME_NATIONALITE and NATIONS_COURTES_LARGE, nations_courtes_large),
                             (CARTE_IDENTITE or POLYGONE_ENTETE, carte_ou_polygone)) if ok]
    lst = [(b, lambda t: [m for fn in fns for m in fn(t)]) for b in BANNIERES] if fns else []
    if RAPPORT_LETTRE_LARGE:
        lst.append((MODELE_RAPPORT, rapport_lettre_large))
    if DEUXIEME_NATIONALITE:
        lst += [(cellule, nation_cell(cellule, alias)) for alias, (cellule, _) in CELLULES_NATION.items()]
    # 2026-11-05 : vue « grande tuile » au choix (option entete_vue) ; après les bannières (recopiées dedans)
    import entete_tuile
    lst.append((entete_tuile.MODELE, entete_tuile.job))
    # 2026-11-07 : étoiles Niveau / Potentiel sous la note du rapport (joueur hors club, vue tuile)
    lst.append((entete_tuile.MODELE_RAPPORT, entete_tuile.etoiles_rapport))
    # 2026-11-07 (le joueur : « partout juste les diminutifs ») : libellé court au lieu de la phrase, tous les modes,
    # en-tête / carte de la tuile + tuile « Rapport de supervision » + blocs de rapport (rapport_diminutif)
    import rapport_diminutif
    lst += rapport_diminutif.jobs(rapport_diminutif.MODELES)
    return lst


def cmd_etat():
    for model in BANNIERES:
        _, _, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable")
            continue
        t = Tree(tt)
        have = [n for n in (NOM_NATIONALITES, NOM_BANDEAU_PC, NOM_ACTIONS_LARGE) if named(t, n)]
        print(f"{model} : " + (", ".join(have) if have else "rien"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        appliquer()
    elif op == "retirer":
        lancer.retirer_par_restauration(MARKER)   # ajouts retirés en remettant les modèles d'origine
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            appliquer()
        else:
            print("en-tête de la fiche : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
